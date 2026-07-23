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


def test_composer_nom_espace_sans_code_reste_3_segments():
    """(11) code_mission par défaut (None) → nom 3 segments INCHANGÉ (non-régression explicite)."""
    attendu = "2026 - Siteflow - Cadrage"
    assert server._composer_nom_espace("2026", "Siteflow", "Cadrage") == attendu
    assert server._composer_nom_espace("2026", "Siteflow", "Cadrage", None) == attendu


def test_composer_nom_espace_avec_code_numerique_4_segments():
    """(12) code_mission numérique → 4e segment « - <code> » en fin de nom."""
    assert (
        server._composer_nom_espace("2026", "Arabelle Solutions", "Siteflow", "14")
        == "2026 - Arabelle Solutions - Siteflow - 14"
    )


@pytest.mark.parametrize("mauvais_code", ["14a", "M-2026-014", "", "  ", "1.4", "-14", "0x14"])
def test_composer_nom_espace_code_non_numerique_refuse(mauvais_code):
    """(13) code_mission fourni mais non exclusivement numérique → ValueError."""
    with pytest.raises(ValueError):
        server._composer_nom_espace("2026", "Siteflow", "Cadrage", mauvais_code)


def test_composer_nom_espace_creer_deposer_meme_nom():
    """(14) creer_espace_mission et deposer_document_mission partagent le MÊME helper : mêmes
    (annee, client, nom_mission, code_mission) ⇒ nom composé IDENTIQUE (zéro dérive, 3 ou 4 segments)."""
    args = ("2026", "Arabelle Solutions", "Siteflow")
    # 3 segments (sans code) : déterministe et identique des deux côtés.
    assert server._composer_nom_espace(*args) == server._composer_nom_espace(*args)
    # 4 segments (avec code) : identique des deux côtés, et conforme au format attendu.
    assert server._composer_nom_espace(*args, "14") == server._composer_nom_espace(*args, "14")
    assert server._composer_nom_espace(*args, "14") == "2026 - Arabelle Solutions - Siteflow - 14"


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
# workbook_archiver_gabarit — DÉPLACEMENT (move), PAS COPIE (T-0035 reprise n°4, serveur 0.15.0)
# Le déplacement LIBÈRE le nom `gabarit-<code>.xlsx` de « 06 - Gabarit ERP » → la ré-instanciation
# fail-closed du skill se satisfait sans collision. Cible FIGÉE côté serveur, réversible (00 - Old).
# --------------------------------------------------------------------------------------------

class _FauxClientArchiver:
    """Client httpx factice pour workbook_archiver_gabarit.

    `_resoudre_item_gabarit` fait un GET (résolution par chemin sous le dossier figé) ; l'archivage
    fait ensuite UN PATCH (déplacement). Un POST /copy est un ÉCHEC de test : l'archivage ne copie plus.
    """

    def __init__(self, gabarit_present=True):
        self._present = gabarit_present
        self.appels = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get(self, url, headers=None):
        self.appels.append(("GET", url, None))
        if not self._present:
            return _RepWb(404, {})  # aucun gabarit pour ce code → FileNotFoundError attendu
        return _RepWb(200, {"id": "ITEM-GABARIT"})

    def patch(self, url, headers=None, json=None):
        self.appels.append(("PATCH", url, json))
        return _RepWb(200, {"id": "ITEM-GABARIT"})

    def post(self, url, headers=None, json=None):
        self.appels.append(("POST", url, json))
        raise AssertionError(
            "workbook_archiver_gabarit ne doit PLUS appeler POST /copy : c'est un DÉPLACEMENT "
            "(PATCH parentReference), pas une copie — sinon le nom n'est jamais libéré."
        )


def test_workbook_archiver_gabarit_deplace_pas_copie(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(25 bis) NOMINAL : l'archivage DÉPLACE le gabarit courant vers « 00 - Old » par PATCH
    (parentReference = dossier « 00 - Old » figé + nom horodaté). AUCUN POST /copy. Retour synchrone
    `deplace=True` — plus de 202/Location à poller. Le nom source est libéré au retour."""
    client = _FauxClientArchiver()
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_archiver_gabarit)

    resultat = fn(None, code_mission="  MISSION-2  ")

    assert resultat["code_mission"] == "MISSION-2"
    assert resultat["deplace"] is True
    assert resultat["dossier"] == "00 - Old"
    assert resultat["item_id"] == "ITEM-GABARIT"
    # nom d'archive horodaté : gabarit-<code>-<UTC compact>.xlsx
    assert resultat["nom_archive"].startswith("gabarit-MISSION-2-") and resultat["nom_archive"].endswith(".xlsx")

    patchs = [(u, c) for (m, u, c) in client.appels if m == "PATCH"]
    assert len(patchs) == 1, "un seul PATCH (déplacement de l'unique gabarit courant)."
    url_patch, corps = patchs[0]
    assert f"/items/ITEM-GABARIT" in url_patch and "/copy" not in url_patch
    # destination FIGÉE côté serveur : dossier « 00 - Old » (jamais choisi par l'appelant).
    assert corps["parentReference"]["id"] == "FOLDER-00"
    assert corps["name"] == resultat["nom_archive"]
    # DÉPLACEMENT, pas copie : aucun POST (le mock lèverait sur POST /copy de toute façon).
    assert not any(m == "POST" for (m, _u, _c) in client.appels)


def test_workbook_archiver_gabarit_code_invalide_refuse_avant_reseau(_sans_porte, monkeypatch):
    """(25 ter) Un code_mission invalide refuse (ValueError) AVANT toute ouverture de client httpx :
    l'assainissement partagé précède le réseau (fail-closed, comme les autres primitives gabarit)."""
    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré un code_mission invalide.")
    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.workbook_archiver_gabarit)
    with pytest.raises(ValueError):
        fn(None, code_mission="../evasion")


def test_workbook_archiver_gabarit_absent_leve_filenotfound_sans_patch(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(25 quater) Aucun gabarit pour ce code (résolution 404) → FileNotFoundError, et AUCUN PATCH
    n'est tenté : on ne déplace rien qui n'existe pas (le déplacement reste borné à une cible réelle)."""
    client = _FauxClientArchiver(gabarit_present=False)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_archiver_gabarit)

    with pytest.raises(FileNotFoundError):
        fn(None, code_mission="MISSION-2")
    assert not any(m == "PATCH" for (m, _u, _c) in client.appels), (
        "aucun déplacement ne doit être tenté si le gabarit courant n'existe pas."
    )


# --------------------------------------------------------------------------------------------
# workbook_instancier_gabarit v2 — FABRICATION SERVICE (API-native), cible figée fail-closed.
# T-0035 reprise n°5 : le PRÉDICAT « vierge » est RECALIBRÉ (preuves interne §5 ET froide §8). Fait
# mesuré : une table Excel vide porte une LIGNE D'INSERTION standard (fabrication `ref=A1:X2` ; Excel
# authentique `ref=A1:D3`) — donc « vierge » = en-têtes §5.2 + AUCUNE ligne de corps PLEINE (les lignes
# entièrement vides sont TOLÉRÉES), et non un count:0 strict. La voie « souche binaire copiée » a été
# évaluée puis écartée (Excel écrit aussi des lignes vides). Le rollback est VÉRIFIÉ (DELETE puis GET →
# 404 ; un GET 200 = annonce honnête d'incomplet, jamais de suppression non prouvée — défaut B).
# --------------------------------------------------------------------------------------------

class _RepWb:
    """Réponse httpx factice : status_code, .json(), .headers ; raise_for_status() → HTTPStatusError ≥ 400."""

    def __init__(self, status_code, json_data=None, headers=None):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.headers = headers if headers is not None else {}

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise server.httpx.HTTPStatusError("statut Graph d'erreur", request=None, response=None)


# En-têtes attendus par table (miroir de server.TABLES_GABARIT), pour fabriquer une réponse /columns.
_ENTETES_PAR_TABLE = {table: entetes for (_feuille, table, entetes) in server.TABLES_GABARIT}


class _FauxClientWorkbook:
    """Client httpx factice simulant la séquence Workbook v2 complète (fabrication service).

    Route par (méthode, motif d'URL) et enregistre chaque appel dans `self.appels`
    [(méthode, url, corps)] — et, en parallèle, les en-têtes dans `self.entetes_appels`
    [(méthode, url, headers)] (permet d'assurer que la PREUVE FROIDE §8 lit SANS workbook-session-id).
    Paramètres de pilotage des branches :
      - statut_creation  : code du PUT de création (201 nominal ; 409 = collision fail-closed) ;
      - codes_tables_add : codes renvoyés par POST tables/add, consommés dans l'ordre (permet de
                           simuler un 504 puis un 201) ; défaut 201 quand la liste est épuisée ;
      - lignes_insertion : nb de lignes de corps ENTIÈREMENT VIDES que chaque table montre — miroir de
                           la LIGNE D'INSERTION Excel (défaut 1), en /rows (chaud) ET /columns (froid) ;
      - pollue_rows      : {nom_table: n} nb de lignes PLEINES (1re cellule non vide) en /rows —
                           table NON vierge vue par la PREUVE INTERNE §5 (chaude) ;
      - pollue_columns   : {nom_table: n} nb de lignes PLEINES en /columns — table NON vierge vue par la
                           PREUVE FROIDE §8 (le cas d'une pollution visible SEULEMENT à froid) ;
      - columns_status   : code HTTP de la PREUVE FROIDE §8 (/columns ; 200 nominal, 403 = non ouvrable
                           à froid — le cas du cockpit T-0035) ;
      - verify_get_status: GET de contrôle du rollback (404 = suppression PROUVÉE ; 200 = incomplet).
    """

    def __init__(
        self,
        statut_creation=201,
        codes_tables_add=None,
        lignes_insertion=1,
        pollue_rows=None,
        pollue_columns=None,
        columns_status=200,
        verify_get_status=404,
    ):
        self._statut_creation = statut_creation
        self._codes_tables_add = list(codes_tables_add) if codes_tables_add else []
        self._lignes_insertion = lignes_insertion
        self._pollue_rows = pollue_rows or {}
        self._pollue_columns = pollue_columns or {}
        self._columns_status = columns_status
        self._verify_get_status = verify_get_status
        self._table_seq = 0
        self._nb_sessions = 0
        self.appels = []
        self.entetes_appels = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def put(self, url, headers=None, content=None, params=None):
        self.appels.append(("PUT", url, {"params": params, "taille": len(content or b"")}))
        self.entetes_appels.append(("PUT", url, headers or {}))
        return _RepWb(self._statut_creation, {"id": "ITEM-CREE"})

    def post(self, url, headers=None, json=None):
        self.appels.append(("POST", url, json))
        self.entetes_appels.append(("POST", url, headers or {}))
        if url.endswith("/createSession"):
            self._nb_sessions += 1
            # id distinct par session : fabrication (§2) puis ré-émission (§7).
            return _RepWb(201, {"id": f"SESSION-{self._nb_sessions}"})
        if url.endswith("/worksheets/add"):
            return _RepWb(201, {"id": "{ws-added}", "name": (json or {}).get("name")})
        if url.endswith("/tables/add"):
            code = self._codes_tables_add.pop(0) if self._codes_tables_add else 201
            if code == 504:
                return _RepWb(504, {})
            self._table_seq += 1
            return _RepWb(201, {"id": f"TBL-{self._table_seq}"})
        if url.endswith("/closeSession"):
            return _RepWb(200, {})
        return _RepWb(200, {})

    def get(self, url, headers=None):
        self.appels.append(("GET", url, None))
        self.entetes_appels.append(("GET", url, headers or {}))
        if url.endswith("/worksheets"):
            return _RepWb(200, {"value": [{"id": "{00000000-0001-0000-0000-000000000000}", "name": "Feuil1"}]})
        if url.endswith("/rows"):
            # PREUVE INTERNE §5 : lignes de corps. `lignes_insertion` lignes VIDES (tolérées) + `pleines`
            # lignes portant une valeur (1re cellule non vide) → table non vierge si pleines > 0.
            nom_table = url.split("/tables/")[1].split("/rows")[0]
            pleines = self._pollue_rows.get(nom_table, 0)
            rows = [{"values": [["", "", "", ""]]} for _ in range(self._lignes_insertion)]
            rows += [{"values": [["x", "", "", ""]]} for _ in range(pleines)]
            return _RepWb(200, {"value": rows})
        if url.endswith("/columns"):
            # PREUVE FROIDE §8 : réponse au format /columns (une colonne par en-tête, en-tête + corps).
            if self._columns_status != 200:
                return _RepWb(self._columns_status, {})
            nom_table = url.split("/tables/")[1].split("/columns")[0]
            entetes = _ENTETES_PAR_TABLE.get(nom_table, ())
            pleines = self._pollue_columns.get(nom_table, 0)
            colonnes = []
            for j, e in enumerate(entetes):
                body = [[""] for _ in range(self._lignes_insertion)]  # lignes d'insertion (vides)
                # lignes pleines : seule la 1re colonne porte une valeur (suffit à « pleine »).
                body += [[("x" if j == 0 else "")] for _ in range(pleines)]
                colonnes.append({"name": e, "values": [[e]] + body})
            return _RepWb(200, {"value": colonnes})
        if "/workbook" not in url and url.endswith("ITEM-CREE"):
            # GET de contrôle du rollback (…/items/ITEM-CREE) — 404 = suppression prouvée, 200 = incomplet.
            return _RepWb(self._verify_get_status, {})
        return _RepWb(200, {})

    def patch(self, url, headers=None, json=None):
        self.appels.append(("PATCH", url, json))
        self.entetes_appels.append(("PATCH", url, headers or {}))
        return _RepWb(200, {})

    def delete(self, url, headers=None):
        self.appels.append(("DELETE", url, None))
        self.entetes_appels.append(("DELETE", url, headers or {}))
        return _RepWb(204, {})


@pytest.fixture
def _config_gabarit_factice(monkeypatch):
    """Config GABARIT valide + acquisition de jeton neutralisée, pour exercer le corps réseau (mocké)
    de l'instanciation — `_entetes()` acquerrait sinon un jeton Azure (indisponible hors tenant).
    Aucun secret : en-tête factice."""
    monkeypatch.setattr(
        server,
        "_config_gabarit",
        lambda: {"gabarit_drive_id": "DRIVE-CA", "gabarit_folder_id": "FOLDER-06", "gabarit_old_folder_id": "FOLDER-00"},
    )
    monkeypatch.setattr(server, "_entetes", lambda: {"Authorization": "Bearer faketoken"})


@pytest.fixture
def _sans_sleep(monkeypatch):
    """Neutralise le backoff (time.sleep) : le RETRY 504 ne doit pas attendre réellement en test."""
    monkeypatch.setattr(server.time, "sleep", lambda _s: None)


@pytest.mark.parametrize("mauvais", ["", "   ", "a/b", "a\\b", "a..b", "..", "code\x01"])
def test_workbook_instancier_gabarit_code_invalide_refuse(_sans_porte, mauvais):
    """(26) code_mission vide / « / » « \\ » « .. » / caractère de contrôle → ValueError, AVANT réseau
    (l'assainissement partagé `_assainir_code_mission` précède _config_gabarit et httpx)."""
    fn = _sous_jacente(server.workbook_instancier_gabarit)
    with pytest.raises(ValueError):
        fn(None, code_mission=mauvais)


def test_workbook_instancier_gabarit_code_invalide_aucun_appel_reseau(_sans_porte, monkeypatch):
    """(26 bis) Un code_mission invalide refuse AVANT toute ouverture de client httpx : le client
    interdit prouve qu'aucun appel réseau n'est tenté (l'assainissement précède le réseau)."""
    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError(
                "client httpx instancié malgré un code_mission invalide (refus attendu avant réseau)."
            )
    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.workbook_instancier_gabarit)
    with pytest.raises(ValueError):
        fn(None, code_mission="../evasion")


def test_workbook_instancier_gabarit_nominal_fabrication_service(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(27) NOMINAL v2 : PUT vide (fail-closed) → session → feuilles (rename + 2 add) → 3×(range +
    tables/add + rename T_*) → preuve EN SESSION vierge → closeSession → RÉ-ÉMISSION (2e session +
    range inerte) → PREUVE FROIDE vierge ×3 (/columns, sans session). Une table fraîche porte 1 ligne
    d'insertion VIDE : elle est VIERGE (tolérée). Retour : `lignes_vides` par table. Aucun rollback."""
    client = _FauxClientWorkbook()  # lignes_insertion=1 par défaut : la ligne d'insertion Excel
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    resultat = fn(None, code_mission="  MISSION-2  ")  # espaces → strip par l'assainissement

    assert resultat["code_mission"] == "MISSION-2"
    assert resultat["nom_gabarit"] == "gabarit-MISSION-2.xlsx"
    assert resultat["item_id"] == "ITEM-CREE"
    # PRÉDICAT RECALIBRÉ : le retour porte `lignes_vides` (la ligne d'insertion tolérée), pas un count:0.
    assert resultat["tables"] == {
        "T_Affectations": {"lignes_vides": 1},
        "T_Imputations": {"lignes_vides": 1},
        "T_Echeancier": {"lignes_vides": 1},
    }

    methodes = [(m, u) for (m, u, _c) in client.appels]
    # 1) création service-authored fail-closed : PUT vide (0 octet), conflictBehavior=fail, dossier figé.
    put_appel = next(a for a in client.appels if a[0] == "PUT")
    assert "FOLDER-06" in put_appel[1] and "gabarit-MISSION-2.xlsx" in put_appel[1]
    assert put_appel[2]["params"]["@microsoft.graph.conflictBehavior"] == "fail"
    assert put_appel[2]["taille"] == 0
    # 3+4) trois tables créées puis nommées T_* ; 5) preuve EN SESSION = 3 lectures /rows.
    assert sum(1 for (_m, u) in methodes if u.endswith("/tables/add")) == 3
    noms_tables = {c.get("name") for (m, u, c) in client.appels if m == "PATCH" and "/tables/" in u and c}
    assert {"T_Affectations", "T_Imputations", "T_Echeancier"} <= noms_tables
    assert sum(1 for (_m, u) in methodes if u.endswith("/rows")) == 3
    # 2+7) DEUX sessions : fabrication puis RÉ-ÉMISSION (« Ouvrir + Enregistrer » machine) ; 2 fermetures.
    assert sum(1 for (_m, u) in methodes if u.endswith("/createSession")) == 2
    assert sum(1 for (_m, u) in methodes if u.endswith("/closeSession")) == 2
    # 8) PREUVE FROIDE : 3 lectures /columns (le chemin du cockpit).
    assert sum(1 for (_m, u) in methodes if u.endswith("/columns")) == 3
    assert not any(m == "DELETE" for (m, _u) in methodes), "instanciation réussie → aucun rollback."


def test_workbook_instancier_gabarit_ligne_insertion_vide_est_vierge(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(27 bis) RECALIBRATION : une table portant UNIQUEMENT des lignes de corps entièrement VIDES
    (ligne d'insertion Excel) est VIERGE — l'instanciation aboutit. Fait mesuré : Excel matérialise une
    telle ligne dans toute table vide (fabrication `A1:X2`, Excel authentique `A1:D3`)."""
    client = _FauxClientWorkbook(lignes_insertion=2)  # deux lignes vides (cas Excel authentique)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    resultat = fn(None, code_mission="MISSION-2")
    assert resultat["tables"] == {
        "T_Affectations": {"lignes_vides": 2},
        "T_Imputations": {"lignes_vides": 2},
        "T_Echeancier": {"lignes_vides": 2},
    }
    assert not any(m == "DELETE" for (m, _u, _c) in client.appels), "table vierge → aucun rollback."


def test_workbook_instancier_gabarit_zero_ligne_est_vierge(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(27 ter) Une table SANS aucune ligne de corps (0 ligne) reste vierge (rétro-compatible avec le
    cas count:0 strict)."""
    client = _FauxClientWorkbook(lignes_insertion=0)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    resultat = fn(None, code_mission="MISSION-2")
    assert resultat["tables"]["T_Affectations"] == {"lignes_vides": 0}
    assert not any(m == "DELETE" for (m, _u, _c) in client.appels)


def test_workbook_instancier_gabarit_preuve_froide_est_sans_session(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(27 quater) La PREUVE FROIDE §8 reproduit le chemin EXACT du cockpit : les lectures /columns
    portent le jeton MAIS AUCUN `workbook-session-id` (lecture à froid). Contraste : la preuve EN
    SESSION §5 (/rows) porte bien, elle, un workbook-session-id."""
    client = _FauxClientWorkbook()
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    fn(None, code_mission="MISSION-2")

    lectures_columns = [(u, h) for (m, u, h) in client.entetes_appels if m == "GET" and u.endswith("/columns")]
    assert len(lectures_columns) == 3
    for _u, headers in lectures_columns:
        assert "workbook-session-id" not in headers, (
            "la preuve FROIDE doit lire SANS session (chemin du cockpit) ; un id de session la rendrait chaude."
        )
    lectures_rows = [(u, h) for (m, u, h) in client.entetes_appels if m == "GET" and u.endswith("/rows")]
    assert lectures_rows and all("workbook-session-id" in h for _u, h in lectures_rows)


def test_workbook_instancier_gabarit_ligne_pleine_froide_echoue_rollback_verifie(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(27 quinquies) RECALIBRATION — le juge n'est PAS affaibli : une table portant une ligne de corps
    PLEINE (une valeur) À FROID échoue, et l'item créé est supprimé PUIS le rollback est VÉRIFIÉ
    (GET → 404). Le message porte la preuve de la suppression, jamais une annonce non prouvée."""
    # pollution visible SEULEMENT à froid (/columns) → passe la preuve §5, échoue la preuve froide §8.
    client = _FauxClientWorkbook(pollue_columns={"T_Echeancier": 1}, verify_get_status=404)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    with pytest.raises(RuntimeError) as excinfo:
        fn(None, code_mission="MISSION-2")
    msg = str(excinfo.value)
    assert "FROIDE" in msg and "NON VIDE" in msg
    assert "rollback vérifié" in msg and "404" in msg, "la suppression doit être PROUVÉE, pas annoncée."

    suppressions = [u for (m, u, _c) in client.appels if m == "DELETE"]
    assert len(suppressions) == 1 and "ITEM-CREE" in suppressions[0]
    idx_delete = next(i for i, (m, _u, _c) in enumerate(client.appels) if m == "DELETE")
    gets_apres = [u for (m, u, _c) in client.appels[idx_delete + 1:] if m == "GET"]
    assert any(u.endswith("ITEM-CREE") for u in gets_apres), "un GET de contrôle doit suivre le DELETE."


def test_workbook_instancier_gabarit_ligne_pleine_interne_echoue_rollback_verifie(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(27 sexies) MÊME prédicat recalibré côté PREUVE INTERNE §5 (/rows) : une ligne PLEINE vue en
    session chaude fait échouer dès la preuve §5, en amont de la preuve froide, avec rollback vérifié."""
    client = _FauxClientWorkbook(pollue_rows={"T_Affectations": 1}, verify_get_status=404)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    with pytest.raises(RuntimeError) as excinfo:
        fn(None, code_mission="MISSION-2")
    msg = str(excinfo.value)
    assert "session" in msg and "NON VIDE" in msg
    assert "rollback vérifié" in msg
    suppressions = [u for (m, u, _c) in client.appels if m == "DELETE"]
    assert len(suppressions) == 1 and "ITEM-CREE" in suppressions[0]


def test_workbook_instancier_gabarit_preuve_froide_403_rollback_verifie(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(27 septies) PREUVE FROIDE anti-faux-vert : si /columns renvoie 403 (classeur non ouvrable à
    froid, le cas du cockpit T-0035), l'instanciation LÈVE et l'item est supprimé PUIS vérifié (GET → 404)."""
    client = _FauxClientWorkbook(columns_status=403, verify_get_status=404)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    with pytest.raises(RuntimeError) as excinfo:
        fn(None, code_mission="MISSION-2")
    msg = str(excinfo.value)
    assert "FROIDE" in msg and "rollback vérifié" in msg
    suppressions = [u for (m, u, _c) in client.appels if m == "DELETE"]
    assert len(suppressions) == 1 and "ITEM-CREE" in suppressions[0]


def test_workbook_instancier_gabarit_rollback_incomplet_annonce_honnete(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(27 octies — DÉFAUT B) Si, APRÈS le DELETE, l'item est TOUJOURS présent (GET → 200), l'échec est
    annoncé HONNÊTEMENT (« ROLLBACK INCOMPLET … à retirer par le gardien ») — JAMAIS une suppression
    prouvée. C'est la correction du rollback menteur de l'épreuve tenant du 17/07 (item réputé supprimé
    resté en racine, `01BWFCBZHMHXN46WR2EFDJQFBLFKT7NXNP`)."""
    client = _FauxClientWorkbook(columns_status=403, verify_get_status=200)  # 200 = item encore présent
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    with pytest.raises(RuntimeError) as excinfo:
        fn(None, code_mission="MISSION-2")
    msg = str(excinfo.value)
    assert "ROLLBACK INCOMPLET" in msg and "gardien" in msg
    assert "rollback vérifié" not in msg, "surtout PAS d'annonce de suppression prouvée quand elle ne l'est pas."
    assert any(m == "DELETE" for (m, _u, _c) in client.appels), "le DELETE est bien tenté (best effort)."


def test_workbook_instancier_gabarit_collision_refuse_sans_autre_appel(_sans_porte, _config_gabarit_factice, monkeypatch):
    """(28) FAIL-CLOSED (INCHANGÉ) : le PUT de création renvoie 409 (gabarit déjà présent) →
    FileExistsError, et AUCUN autre appel — pas de session, pas de rollback (rien n'a été créé)."""
    client = _FauxClientWorkbook(statut_creation=409)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    with pytest.raises(FileExistsError):
        fn(None, code_mission="MISSION-2")

    assert [m for (m, _u, _c) in client.appels] == ["PUT"], (
        "une collision doit s'arrêter au PUT : aucune session, aucune table, aucun rollback."
    )


def test_workbook_instancier_gabarit_retry_504_sur_tables_add(_sans_porte, _config_gabarit_factice, _sans_sleep, monkeypatch):
    """(29) RETRY borné : le 1er POST tables/add renvoie 504, le réessai renvoie 201 → l'instanciation
    aboutit (3 tables créées, preuve vierge, retour nominal), sans rollback."""
    client = _FauxClientWorkbook(codes_tables_add=[504, 201])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.workbook_instancier_gabarit)

    resultat = fn(None, code_mission="MISSION-2")

    assert resultat["tables"] == {
        "T_Affectations": {"lignes_vides": 1},
        "T_Imputations": {"lignes_vides": 1},
        "T_Echeancier": {"lignes_vides": 1},
    }
    # 4 POST tables/add au total : 2 pour la 1re table (504 + 201), 1 + 1 pour les deux autres.
    assert sum(1 for (m, u, _c) in client.appels if m == "POST" and u.endswith("/tables/add")) == 4
    assert not any(m == "DELETE" for (m, _u, _c) in client.appels), "un 504 rattrapé ne déclenche pas de rollback."


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
