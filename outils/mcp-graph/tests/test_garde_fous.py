"""Tests des GARDE-FOUS FAIL-CLOSED de server.py (T-0020-e, chapeau T-0020, plan §7 T-2.1).

Angle mort de la Phase 2 : le harnais d'evals (T-0020-a) ne teste que les SKILLS ; le CODE du
connecteur MCP n'était couvert par aucun test. Ces tests prouvent, en isolant CHAQUE garde-fou,
que les refus surviennent bien (exception attendue) — et, pour le garde-fou central d'intégrité
(leçon T-0024-d), que le refus intervient AVANT tout appel réseau.

Aucun appel réseau réel, aucun secret, aucune variable d'environnement requise : tous les
garde-fous testés s'exécutent avant `_config_mission()` et avant l'ouverture d'un client httpx.
"""

import asyncio
import base64
import hashlib
import inspect
import json
import logging

import pytest

import server


# --------------------------------------------------------------------------------------------
# Utilitaires de test
# --------------------------------------------------------------------------------------------

def _sous_jacente(obj):
    """Récupère la fonction sous-jacente d'un outil décoré @mcp.tool()/@_journal_appel.

    Selon la version du SDK mcp résolue, `server.deposer_document_mission` peut être :
    - un objet Tool portant l'attribut `.fn` (SDK officiel) ; on le prend ;
    - la fonction wrapper de `_journal_appel` (functools.wraps) portant `.__wrapped__` ; fallback ;
    - sinon l'objet lui-même (déjà appelable).
    Dans tous les cas, l'appel exécute les garde-fous de l'outil ; le décorateur de journal, s'il
    est traversé, re-lève les exceptions à l'identique (comportement inchangé, T-0020-b).
    """
    for attr in ("fn", "__wrapped__"):
        if hasattr(obj, attr):
            return getattr(obj, attr)
    return obj


def _jwt(payload: dict) -> str:
    """Fabrique un JWT NON signé factice « header.payload.signature ».

    `payload` est encodé en base64url SANS padding (comme un vrai JWT). Sert à exercer la voie 1
    de `_verifier_appelant` (en-tête « Authorization: Bearer <jwt> »). La signature n'est pas
    vérifiée par le code (Easy Auth valide signature/expiry/tenant EN AMONT — hors de ce code).
    """
    def b64url(donnees: bytes) -> str:
        return base64.urlsafe_b64encode(donnees).rstrip(b"=").decode("ascii")

    header = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode("utf-8"))
    corps = b64url(json.dumps(payload).encode("utf-8"))
    return f"{header}.{corps}.signature"


class FauxRequest:
    """Requête Starlette minimale : seule `.headers` (dict, avec `.get`) est utilisée par le code."""

    def __init__(self, headers: dict | None = None):
        self.headers = headers if headers is not None else {}


class FauxRequestContext:
    """Reproduit ctx.request_context.request (chemin d'attributs lu par _verifier_appelant)."""

    def __init__(self, request):
        self.request = request


class FauxCtx:
    """Reproduit ctx.request_context (le tool reçoit `ctx: Context` en 1er argument)."""

    def __init__(self, request):
        self.request_context = FauxRequestContext(request)


def _ctx_avec_headers(headers: dict) -> FauxCtx:
    return FauxCtx(FauxRequest(headers))


# --------------------------------------------------------------------------------------------
# _verifier_appelant — porte d'identité FAIL-CLOSED (T-0009 / T-0015)
# --------------------------------------------------------------------------------------------

def test_verifier_appelant_sans_requete_http_refuse():
    """(1) Aucune requête HTTP dans le contexte (transport non-HTTP / hors requête) → refus."""
    ctx = FauxCtx(request=None)
    with pytest.raises(PermissionError):
        server._verifier_appelant(ctx)


def test_verifier_appelant_sans_ctx_attribut_refuse():
    """(1 bis) ctx sans request_context du tout (AttributeError capté) → refus fail-closed."""
    class CtxVide:
        pass
    with pytest.raises(PermissionError):
        server._verifier_appelant(CtxVide())


def test_verifier_appelant_headers_vides_refuse():
    """(2) Requête présente mais aucun token dans les en-têtes → aucun claim lisible → refus."""
    ctx = _ctx_avec_headers({})
    with pytest.raises(PermissionError):
        server._verifier_appelant(ctx)


def test_verifier_appelant_scp_access_as_user_autorise():
    """(3) Bearer JWT avec scp=access_as_user (flux humain délégué) → autorisé (aucune exception)."""
    ctx = _ctx_avec_headers({"Authorization": "Bearer " + _jwt({"scp": "access_as_user"})})
    assert server._verifier_appelant(ctx) is None


def test_verifier_appelant_roles_mcp_invoke_autorise():
    """(4) Bearer JWT avec roles=["MCP.Invoke"] (workload) → autorisé (aucune exception)."""
    ctx = _ctx_avec_headers({"Authorization": "Bearer " + _jwt({"roles": ["MCP.Invoke"]})})
    assert server._verifier_appelant(ctx) is None


def test_verifier_appelant_claims_insuffisants_refuse():
    """(5) Bearer JWT avec scp autre + roles vides → ni access_as_user ni MCP.Invoke → refus."""
    ctx = _ctx_avec_headers(
        {"Authorization": "Bearer " + _jwt({"scp": "autrechose", "roles": []})}
    )
    with pytest.raises(PermissionError):
        server._verifier_appelant(ctx)


# --------------------------------------------------------------------------------------------
# _composer_nom_espace — validation + composition côté serveur (nom d'espace de mission)
# --------------------------------------------------------------------------------------------

def test_composer_nom_espace_nominal():
    """(6) Composantes valides → « AAAA - Client - Nom de la mission »."""
    assert server._composer_nom_espace("2026", "Siteflow", "Cadrage") == "2026 - Siteflow - Cadrage"


@pytest.mark.parametrize("annee", ["20260", "abcd", "1999", "2101", "202"])
def test_composer_nom_espace_annee_invalide(annee):
    """(7) annee non-4-chiffres OU hors bornes [2020..2100] → ValueError."""
    with pytest.raises(ValueError):
        server._composer_nom_espace(annee, "Siteflow", "Cadrage")


def test_composer_nom_espace_client_vide_refuse():
    """(8a) client vide (ou uniquement des espaces) → ValueError."""
    with pytest.raises(ValueError):
        server._composer_nom_espace("2026", "   ", "Cadrage")


def test_composer_nom_espace_nom_trop_long_refuse():
    """(8b) nom_mission de 61+ caractères → ValueError (max 60)."""
    with pytest.raises(ValueError):
        server._composer_nom_espace("2026", "Siteflow", "a" * 61)


@pytest.mark.parametrize("mauvais", ["a/b", "a\\b", "a..b", "a|b", "a:b", "a<b", "a\x01b"])
def test_composer_nom_espace_caracteres_interdits_refuse(mauvais):
    """(9) « / » « \\ » « .. » ou caractère interdit / de contrôle dans une composante → ValueError.

    NB : « \\x01 » (caractère de contrôle NON-espace) sonde bien la garde `ord(c) < 32` ; un « \\t »
    serait au contraire absorbé par la normalisation des espaces (`" ".join(v.split())`) et donc
    légitimement accepté — ce n'est pas un caractère interdit mais un espace.
    """
    with pytest.raises(ValueError):
        server._composer_nom_espace("2026", mauvais, "Cadrage")


def test_composer_nom_espace_accents_et_espaces_internes_autorises():
    """(10) Accents et espaces internes autorisés (réduction des espaces multiples)."""
    resultat = server._composer_nom_espace("2026", "Éléa Conseil", "Revue à mi-parcours")
    assert resultat == "2026 - Éléa Conseil - Revue à mi-parcours"


# --------------------------------------------------------------------------------------------
# deposer_document_mission — garde-fous en aval de la porte d'identité
# (on neutralise _verifier_appelant pour isoler CHAQUE garde-fou métier)
# --------------------------------------------------------------------------------------------

_ARGS_VALIDES = dict(
    annee="2026",
    client="Siteflow",
    nom_mission="Cadrage",
    sous_dossier="01 - Pilotage",
    nom_fichier="rapport.docx",
)


@pytest.fixture
def deposer(monkeypatch):
    """Fonction sous-jacente de deposer_document_mission, porte d'identité neutralisée."""
    monkeypatch.setattr(server, "_verifier_appelant", lambda ctx: None)
    return _sous_jacente(server.deposer_document_mission)


def test_deposer_sous_dossier_hors_liste_blanche_refuse(deposer):
    """(11) sous_dossier hors SOUS_DOSSIERS_MISSION → PermissionError (liste blanche figée)."""
    args = {**_ARGS_VALIDES, "sous_dossier": "99 - Interdit"}
    with pytest.raises(PermissionError):
        deposer(None, contenu_base64="AAAA", sha256_attendu="a" * 64, **args)


def test_deposer_nom_fichier_evasion_refuse(deposer):
    """(12) nom_fichier avec « .. » (ou « / » « \\ ») → ValueError (assainissement, pas d'évasion)."""
    args = {**_ARGS_VALIDES, "nom_fichier": "../evasion.docx"}
    with pytest.raises(ValueError):
        deposer(None, contenu_base64="AAAA", sha256_attendu="a" * 64, **args)


def test_deposer_extension_hors_whitelist_refuse(deposer):
    """(13) extension hors EXTENSIONS_MISSION (.exe) → ValueError."""
    args = {**_ARGS_VALIDES, "nom_fichier": "rapport.exe"}
    with pytest.raises(ValueError):
        deposer(None, contenu_base64="AAAA", sha256_attendu="a" * 64, **args)


def test_deposer_sha256_mal_forme_refuse(deposer):
    """(14) sha256_attendu ≠ 64 hex minuscules → ValueError (format strict)."""
    with pytest.raises(ValueError):
        deposer(None, contenu_base64="AAAA", sha256_attendu="xyz", **_ARGS_VALIDES)


def test_deposer_base64_invalide_refuse(deposer):
    """(15) contenu_base64 non décodable, sha256_attendu bien formé → ValueError (échec décodage)."""
    with pytest.raises(ValueError):
        deposer(None, contenu_base64="!!!pas du base64!!!", sha256_attendu="a" * 64, **_ARGS_VALIDES)


def test_deposer_integrite_mismatch_refuse_avant_reseau(deposer, monkeypatch):
    """(16) GARDE-FOU CENTRAL (T-0024-d) : sha256_attendu ≠ empreinte du contenu → ValueError,
    ET aucun appel réseau (httpx.Client jamais instancié : le refus précède le réseau)."""
    contenu = b"contenu connu de test"
    contenu_b64 = base64.b64encode(contenu).decode("ascii")
    faux_sha = hashlib.sha256(b"un AUTRE contenu").hexdigest()  # empreinte qui ne concorde pas

    class HttpxInterdit:
        def __init__(self, *a, **k):
            raise AssertionError(
                "Appel réseau tenté malgré un mismatch d'intégrité — le garde-fou fail-closed "
                "n'a PAS arrêté avant le réseau (régression T-0024-d)."
            )

    monkeypatch.setattr(server.httpx, "Client", HttpxInterdit)

    with pytest.raises(ValueError) as excinfo:
        deposer(None, contenu_base64=contenu_b64, sha256_attendu=faux_sha, **_ARGS_VALIDES)
    assert "INTEGRIT" in str(excinfo.value), "le refus doit être celui du garde-fou d'intégrité"


def test_deposer_integrite_concordante_laisse_passer(deposer, monkeypatch):
    """(17) CONTRE-PREUVE de (16) : sha256_attendu = VRAIE empreinte du contenu → le garde-fou
    d'intégrité LAISSE PASSER ; le code atteint _config_mission() et, sans config en CI, lève
    ConfigManquante — une exception AUTRE que le ValueError d'intégrité."""
    contenu = b"contenu connu de test"
    contenu_b64 = base64.b64encode(contenu).decode("ascii")
    vrai_sha = hashlib.sha256(contenu).hexdigest()  # empreinte qui concorde

    with pytest.raises(Exception) as excinfo:
        deposer(None, contenu_base64=contenu_b64, sha256_attendu=vrai_sha, **_ARGS_VALIDES)
    # Le garde-fou d'intégrité a été franchi : l'échec ne doit PAS être celui d'intégrité.
    assert "INTEGRIT" not in str(excinfo.value), (
        "l'intégrité concordante ne doit pas déclencher le refus d'intégrité"
    )
    # Concrètement, sans variables d'environnement M365, c'est _config_mission() qui refuse.
    assert isinstance(excinfo.value, server.ConfigManquante), (
        "après le garde-fou d'intégrité, le premier obstacle en CI est ConfigManquante "
        f"(obtenu : {type(excinfo.value).__name__})"
    )


# --------------------------------------------------------------------------------------------
# T-0027 — réduction du bruit de logs : le filtre /healthz ne touche pas le journal structuré
# --------------------------------------------------------------------------------------------

def _record(message: str) -> logging.LogRecord:
    """Fabrique un LogRecord dont getMessage() vaut `message` (comme une ligne uvicorn.access)."""
    return logging.LogRecord(
        name="uvicorn.access", level=logging.INFO, pathname=__file__, lineno=0,
        msg=message, args=(), exc_info=None,
    )


def test_filtre_healthz_ne_touche_pas_le_journal():
    """(18) T-0027 : le filtre des sondes rejette /healthz, laisse passer le reste, et n'est PAS
    posé sur le logger journal_mcp — le journal {"journal": "mcp-graph"} reste STRICTEMENT intact.
    """
    filtre = server._FiltreSondesHealthz()

    # (a) une sonde /healthz est rejetée (le bruit qui noyait le journal).
    assert filtre.filter(_record('127.0.0.1 - "GET /healthz HTTP/1.1" 200')) is False

    # (b) un vrai appel MCP passe — aucun accès utile n'est filtré.
    assert filtre.filter(_record('10.0.0.4 - "POST /mcp HTTP/1.1" 200')) is True

    # (c) le journal structuré ne porte PAS ce filtre (intégrité du journal T-0020-b) ;
    #     le filtre vit bien sur le logger d'accès uvicorn, et nulle part sur journal_mcp.
    assert not any(
        isinstance(f, server._FiltreSondesHealthz) for f in server.journal_mcp.filters
    ), "le filtre /healthz ne doit jamais être posé sur journal_mcp"
    assert any(
        isinstance(f, server._FiltreSondesHealthz)
        for f in logging.getLogger("uvicorn.access").filters
    ), "le filtre /healthz doit être posé sur uvicorn.access"


# --------------------------------------------------------------------------------------------
# T-0031 — primitives Workbook/Tables : écriture BORNÉE par construction, lecture NON bornée
# --------------------------------------------------------------------------------------------

class _ClientReseauInterdit:
    """Client httpx factice dont tout appel réseau échoue le test (prouve un refus AVANT réseau)."""

    def get(self, *a, **k):
        raise AssertionError("appel réseau tenté alors que le garde-fou aurait dû refuser avant.")

    post = get
    patch = get


def _params(outil) -> set:
    """Noms des paramètres de la fonction sous-jacente d'un outil (hors `ctx`)."""
    fn = _sous_jacente(outil)
    return set(inspect.signature(fn).parameters) - {"ctx"}


@pytest.mark.parametrize("mauvais", ["a/b", "a\\b", "a..b", "..", "code\x01", "   "])
def test_resoudre_item_gabarit_code_mission_evasion_refuse(mauvais):
    """(19) _resoudre_item_gabarit refuse un code_mission vide / « / » « \\ » « .. » / caractère de
    contrôle → ValueError, AVANT tout appel réseau (fail-closed : le client interdit reste intact)."""
    with pytest.raises(ValueError):
        server._resoudre_item_gabarit(_ClientReseauInterdit(), mauvais)


def test_resoudre_item_gabarit_code_valide_franchit_validation():
    """(20) CONTRE-PREUVE de (19) : un code_mission valide franchit l'assainissement ; sans config
    GRAPH_GABARIT_* en CI, l'obstacle suivant est ConfigManquante (PAS le ValueError d'assainissement)."""
    with pytest.raises(server.ConfigManquante):
        server._resoudre_item_gabarit(_ClientReseauInterdit(), "MISSION-2")


@pytest.mark.parametrize(
    "outil",
    [
        "workbook_ajouter_lignes",
        "workbook_maj_ligne",
        "workbook_archiver_gabarit",
        "workbook_instancier_gabarit",
    ],
)
def test_primitives_ecriture_gabarit_ne_prennent_aucune_cible_libre(outil):
    """(21) Les primitives d'ÉCRITURE gabarit n'exposent AUCUN drive_id / item_id / folder_id : la
    cible est FIGÉE côté serveur (domicile « 06 - Gabarit ERP ») — écriture bornée PAR CONSTRUCTION."""
    params = _params(getattr(server, outil))
    interdits = {"drive_id", "item_id", "folder_id", "drive", "item"}
    assert not (params & interdits), (
        f"{outil} ne doit exposer aucune cible libre ({params & interdits} présent) — "
        "l'écriture est bornée au domicile gabarit résolu côté serveur."
    )
    assert "code_mission" in params, f"{outil} borne sa cible par code_mission (assaini serveur)."


def test_workbook_lire_table_accepte_cible_libre():
    """(22) CONTRASTE avec (21) : la LECTURE est NON bornée — workbook_lire_table accepte bien
    drive_id + item_id (peut lire saisie / gabarit / réf. coûts) ; elle ne modifie rien."""
    params = _params(server.workbook_lire_table)
    assert {"drive_id", "item_id"} <= params, (
        "workbook_lire_table doit accepter drive_id + item_id (lecture non bornée)."
    )
    assert "code_mission" not in params, "la lecture n'est pas bornée au domicile gabarit."


@pytest.fixture
def _sans_porte(monkeypatch):
    """Neutralise la porte d'identité pour isoler les garde-fous métier des primitives d'écriture."""
    monkeypatch.setattr(server, "_verifier_appelant", lambda ctx: None)


@pytest.mark.parametrize("lignes", [[], "pas une liste", [1, 2], [["ok"], "pas une ligne"]])
def test_workbook_ajouter_lignes_payload_invalide_refuse(_sans_porte, lignes):
    """(23) workbook_ajouter_lignes exige une liste NON VIDE de listes → ValueError sinon
    (refus AVANT _config_gabarit / réseau)."""
    fn = _sous_jacente(server.workbook_ajouter_lignes)
    with pytest.raises(ValueError):
        fn(None, code_mission="MISSION-2", table="Saisie", lignes=lignes)


@pytest.mark.parametrize("index", [-1, True, 1.5, "0"])
def test_workbook_maj_ligne_index_invalide_refuse(_sans_porte, index):
    """(24) workbook_maj_ligne exige un index entier >= 0 (bool exclu) → ValueError sinon."""
    fn = _sous_jacente(server.workbook_maj_ligne)
    with pytest.raises(ValueError):
        fn(None, code_mission="MISSION-2", table="Saisie", index=index, valeurs=["x"])


def test_workbook_maj_ligne_valeurs_vides_refuse(_sans_porte):
    """(25) workbook_maj_ligne exige une liste de valeurs NON VIDE → ValueError."""
    fn = _sous_jacente(server.workbook_maj_ligne)
    with pytest.raises(ValueError):
        fn(None, code_mission="MISSION-2", table="Saisie", index=0, valeurs=[])


# --------------------------------------------------------------------------------------------
# workbook_instancier_gabarit — instanciation par COPIE de la souche vierge, cible figée fail-closed
# --------------------------------------------------------------------------------------------

class _FauxReponseCopie:
    """Réponse httpx minimale : status_code, .json(), .headers, raise_for_status() inerte < 400."""

    def __init__(self, status_code, json_data=None, headers=None):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.headers = headers if headers is not None else {}

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise AssertionError(
                f"raise_for_status ne devrait pas être atteint sur {self.status_code} "
                "(les cas 404/409 sont interceptés AVANT par un garde-fou explicite)."
            )


class _FauxClientCopie:
    """Client httpx factice : GET source (souche vierge) puis POST /copy au statut configuré.

    Capture le dernier POST (URL + corps JSON) pour prouver la cible FIGÉE (dossier gabarit résolu
    côté serveur) et `@microsoft.graph.conflictBehavior=fail`. `statut_source` permet de simuler une
    souche vierge absente (404).
    """

    dernier_post = None
    dernier_get = None

    def __init__(self, statut_copie=202, statut_source=200):
        self._statut_copie = statut_copie
        self._statut_source = statut_source

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get(self, url, headers=None):
        _FauxClientCopie.dernier_get = {"url": url}
        return _FauxReponseCopie(self._statut_source, {"id": "souche-vierge-item-id"})

    def post(self, url, headers=None, json=None):
        _FauxClientCopie.dernier_post = {"url": url, "json": json}
        entetes = {"Location": "https://graph.microsoft.com/monitor/xyz"} if self._statut_copie == 202 else {}
        return _FauxReponseCopie(self._statut_copie, {}, entetes)


@pytest.fixture
def _config_gabarit_factice(monkeypatch):
    """Fournit une config GABARIT valide et neutralise l'acquisition de jeton pour exercer le corps
    réseau (mocké) de l'instanciation — `_entetes()` acquerrait sinon un jeton Azure (indisponible
    hors tenant). Aucun secret : en-tête factice."""
    monkeypatch.setattr(
        server,
        "_config_gabarit",
        lambda: {"gabarit_drive_id": "DRIVE-CA", "gabarit_folder_id": "FOLDER-06", "gabarit_old_folder_id": "FOLDER-00"},
    )
    monkeypatch.setattr(server, "_entetes", lambda: {"Authorization": "Bearer faketoken"})


@pytest.mark.parametrize("mauvais", ["", "   ", "a/b", "a\\b", "a..b", "..", "code\x01"])
def test_workbook_instancier_gabarit_code_invalide_refuse(_sans_porte, mauvais):
    """(26) code_mission vide / « / » « \\ » « .. » / caractère de contrôle → ValueError, AVANT réseau
    (l'assainissement partagé `_assainir_code_mission` précède _config_gabarit et httpx)."""
    fn = _sous_jacente(server.workbook_instancier_gabarit)
    with pytest.raises(ValueError):
        fn(None, code_mission=mauvais)


def test_workbook_instancier_gabarit_nominal_cible_figee(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(27) Nominal : la copie vise la cible FIGÉE (dossier gabarit résolu côté serveur), le nom dérivé
    est `gabarit-<code>.xlsx`, `conflictBehavior=fail` est posé, la source est la souche vierge canon
    (résolue par chemin sous le dossier figé), et le 202+Location est remonté tel quel."""
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: _FauxClientCopie(statut_copie=202))
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    resultat = fn(None, code_mission="  MISSION-2  ")  # espaces → strip par l'assainissement

    assert resultat["code_mission"] == "MISSION-2"
    assert resultat["nom_gabarit"] == "gabarit-MISSION-2.xlsx"
    assert resultat["accepted"] is True
    assert resultat["emplacement"] == "https://graph.microsoft.com/monitor/xyz"
    # Source = souche vierge canon, résolue par CHEMIN sous le dossier gabarit figé.
    assert server.GABARIT_VIERGE_NOM in _FauxClientCopie.dernier_get["url"]
    assert "FOLDER-06" in _FauxClientCopie.dernier_get["url"]
    # Destination FIGÉE : même dossier gabarit + nom dérivé + jamais d'écrasement.
    corps = _FauxClientCopie.dernier_post["json"]
    assert corps["parentReference"]["id"] == "FOLDER-06"
    assert corps["parentReference"]["driveId"] == "DRIVE-CA"
    assert corps["name"] == "gabarit-MISSION-2.xlsx"
    assert corps["@microsoft.graph.conflictBehavior"] == "fail"


def test_workbook_instancier_gabarit_cible_existante_refuse(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(28) FAIL-CLOSED : la copie renvoie 409 (gabarit déjà existant) → FileExistsError, jamais
    d'écrasement (conflictBehavior=fail)."""
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: _FauxClientCopie(statut_copie=409))
    fn = _sous_jacente(server.workbook_instancier_gabarit)
    with pytest.raises(FileExistsError):
        fn(None, code_mission="MISSION-2")


def test_workbook_instancier_gabarit_souche_vierge_absente_refuse(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(29) Souche vierge canon absente (GET source → 404) → FileNotFoundError (jamais de copie muette)."""
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: _FauxClientCopie(statut_source=404))
    fn = _sous_jacente(server.workbook_instancier_gabarit)
    with pytest.raises(FileNotFoundError):
        fn(None, code_mission="MISSION-2")


# --------------------------------------------------------------------------------------------
# Découverte OAuth (RFC 9728 / RFC 8414) — routes PUBLIQUES de métadonnées.
# La découverte est OUVERTE par conception ; la porte /mcp reste FAIL-CLOSED (T-0015).
# Les handlers custom_route sont des coroutines qui n'utilisent pas la requête (métadonnées statiques).
# --------------------------------------------------------------------------------------------

def _run(coro):
    return asyncio.run(coro)


def test_oauth_protected_resource_public_sans_auth():
    """(30) /.well-known/oauth-protected-resource répond 200 SANS aucune auth ni en-tête."""
    rep = _run(server.oauth_protected_resource(FauxRequest({})))
    assert rep.status_code == 200


def test_oauth_protected_resource_json_rfc9728_exact():
    """(31) Le document RFC 9728 porte EXACTEMENT les 4 clés attendues et leurs valeurs."""
    rep = _run(server.oauth_protected_resource(FauxRequest({})))
    corps = json.loads(rep.body)
    assert set(corps.keys()) == {
        "resource",
        "authorization_servers",
        "scopes_supported",
        "bearer_methods_supported",
    }
    assert corps["resource"] == server._OAUTH_RESOURCE
    assert corps["resource"].endswith("/mcp")
    assert corps["authorization_servers"] == [server._OAUTH_TENANT_ISSUER]
    assert corps["scopes_supported"] == [server._OAUTH_SCOPE]
    assert corps["bearer_methods_supported"] == ["header"]


def test_oauth_authorization_server_redirige_vers_entra():
    """(32) /.well-known/oauth-authorization-server → 302 vers l'openid-configuration du tenant Entra."""
    rep = _run(server.oauth_authorization_server(FauxRequest({})))
    assert rep.status_code == 302
    assert rep.headers["location"] == f"{server._OAUTH_TENANT_ISSUER}/.well-known/openid-configuration"


def test_decouverte_ouverte_mais_mcp_reste_fail_closed():
    """(33) La découverte OAuth est OUVERTE, mais elle ne relâche PAS la porte /mcp : sans Bearer
    valide, _verifier_appelant refuse toujours (fail-closed, T-0015)."""
    # Découverte : ouverte, aucune auth requise.
    assert _run(server.oauth_protected_resource(FauxRequest({}))).status_code == 200
    # /mcp : toujours fermé sans token (en-têtes vides).
    with pytest.raises(PermissionError):
        server._verifier_appelant(_ctx_avec_headers({}))
