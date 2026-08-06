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
import re

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


# --------------------------------------------------------------------------------------------
# allouer_code_mission — allocateur CodeMission ATOMIQUE (T-0038)
# Écriture SOURCE bornée par construction : cible FIGÉE (Liste « CRM », GRAPH_CRM_LIST_ID),
# colonne CodeMission UNIQUEMENT, préconditions fail-closed (Etape=Gagnée ET CodeMission vide),
# allocation max+1 avec If-Match/ETag + post-vérification anti-course bornées.
# --------------------------------------------------------------------------------------------

class _FauxClientCRM:
    """Client httpx factice pour allouer_code_mission.

    Route par forme d'URL :
      - GET .../items            → SCAN de la liste : renvoie la prochaine réponse de `scan_responses`
                                    (liste de valeurs CodeMission), la dernière étant répétée si épuisée ;
      - GET .../items/{id}       → l'opportunité cible : @odata.etag + fields {Etape, CodeMission} ;
      - PATCH .../items/{id}/fields → statut consommé dans l'ordre de `patch_statuses` (défaut 200).
    Enregistre chaque appel dans `self.appels` [(méthode, url, corps|params)] et les en-têtes dans
    `self.entetes_appels` [(méthode, url, headers)] (pour vérifier l'If-Match du PATCH)."""

    def __init__(
        self, etape="Gagnée", code_mission="", etag='W/"etag-1"',
        scan_responses=None, patch_statuses=None, item_status=200,
    ):
        self._etape = etape
        self._code_mission = code_mission
        self._etag = etag
        self._scans = list(scan_responses) if scan_responses is not None else [[]]
        self._patch_statuses = list(patch_statuses) if patch_statuses is not None else [200]
        self._item_status = item_status
        self._scan_i = 0
        self._patch_i = 0
        self.appels = []
        self.entetes_appels = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get(self, url, headers=None, params=None):
        self.appels.append(("GET", url, params))
        self.entetes_appels.append(("GET", url, headers or {}))
        if url.endswith("/items"):
            codes = self._scans[self._scan_i] if self._scan_i < len(self._scans) else self._scans[-1]
            self._scan_i += 1
            return _RepWb(200, {"value": [{"fields": {"CodeMission": c}} for c in codes]})
        if self._item_status != 200:
            return _RepWb(self._item_status, {})
        return _RepWb(
            200,
            {"@odata.etag": self._etag, "fields": {"Etape": self._etape, "CodeMission": self._code_mission}},
        )

    def patch(self, url, headers=None, json=None):
        self.appels.append(("PATCH", url, json))
        self.entetes_appels.append(("PATCH", url, headers or {}))
        st = self._patch_statuses[self._patch_i] if self._patch_i < len(self._patch_statuses) else self._patch_statuses[-1]
        self._patch_i += 1
        return _RepWb(st, {})


@pytest.fixture
def _config_crm_factice(monkeypatch):
    """Config CRM valide + acquisition de jeton neutralisée, pour exercer le corps réseau (mocké)
    de l'allocateur — `_entetes()` acquerrait sinon un jeton Azure (indisponible hors tenant).
    Aucun secret : en-tête factice."""
    monkeypatch.setattr(server, "_config_crm", lambda: {"site_id": "SITE-1", "crm_list_id": "CRM-1"})
    monkeypatch.setattr(server, "_entetes", lambda: {"Authorization": "Bearer faketoken"})


def _patchs(client):
    return [c for (m, _u, c) in client.appels if m == "PATCH"]


def test_allouer_code_mission_precondition_non_gagnee_refuse(_sans_porte, _config_crm_factice, monkeypatch):
    """(34) Opportunité pas à l'étape « Gagnée » → ValueError, et AUCUNE écriture (zéro PATCH)."""
    client = _FauxClientCRM(etape="Proposition", code_mission="")
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_code_mission)
    with pytest.raises(ValueError):
        fn(None, opportunite_id="O-042")
    assert not _patchs(client), "aucune écriture si l'étape n'est pas « Gagnée » (fail-closed)."


def test_allouer_code_mission_code_deja_pose_refuse(_sans_porte, _config_crm_factice, monkeypatch):
    """(35) CodeMission déjà renseigné → ValueError (jamais de réattribution), et AUCUNE écriture."""
    client = _FauxClientCRM(etape="Gagnée", code_mission="7")
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_code_mission)
    with pytest.raises(ValueError):
        fn(None, opportunite_id="O-042")
    assert not _patchs(client), "aucune réattribution si CodeMission est déjà posé (fail-closed)."


def test_allouer_code_mission_patch_porte_if_match_et_max_plus_un(_sans_porte, _config_crm_factice, monkeypatch):
    """(36) NOMINAL : le PATCH cible « .../items/{id}/fields », porte l'If-Match = ETag lu, et
    n'écrit QUE CodeMission = max(existants) + 1 ; retour tentatives=1."""
    client = _FauxClientCRM(
        etape="Gagnée", code_mission="", etag='W/"etag-42"',
        scan_responses=[[7], [7, 8]], patch_statuses=[200],
    )
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_code_mission)

    res = fn(None, opportunite_id="O-042")

    assert res == {"opportunite_id": "O-042", "code_mission": 8, "tentatives": 1}
    patchs_entetes = [(u, h) for (m, u, h) in client.entetes_appels if m == "PATCH"]
    assert len(patchs_entetes) == 1
    url_patch, entetes = patchs_entetes[0]
    assert url_patch.endswith("/items/O-042/fields")
    assert entetes.get("If-Match") == 'W/"etag-42"', "le PATCH doit porter l'If-Match avec l'ETag lu."
    assert _patchs(client)[0] == {"CodeMission": 8}, "le PATCH n'écrit QUE la colonne CodeMission."


def test_allouer_code_mission_conflit_412_puis_succes(_sans_porte, _config_crm_factice, monkeypatch):
    """(37) 412 au PATCH (ETag périmé) → relecture + recalcul + succès à la 2e tentative."""
    client = _FauxClientCRM(
        etape="Gagnée", code_mission="",
        scan_responses=[[3], [3], [3, 4]], patch_statuses=[412, 200],
    )
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_code_mission)

    res = fn(None, opportunite_id="O-042")

    assert res["code_mission"] == 4 and res["tentatives"] == 2
    assert len(_patchs(client)) == 2, "un PATCH refusé (412) puis un PATCH accepté."


def test_allouer_code_mission_trois_conflits_echec_explicite(_sans_porte, _config_crm_factice, monkeypatch):
    """(38) Trois 412 consécutifs → échec EXPLICITE (RuntimeError), après 3 tentatives bornées."""
    client = _FauxClientCRM(
        etape="Gagnée", code_mission="",
        scan_responses=[[1]], patch_statuses=[412, 412, 412],
    )
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_code_mission)
    with pytest.raises(RuntimeError):
        fn(None, opportunite_id="O-042")
    assert len(_patchs(client)) == 3, "exactement 3 tentatives de PATCH, puis échec (borné)."


def test_allouer_code_mission_course_reallocation(_sans_porte, _config_crm_factice, monkeypatch):
    """(39) Course simulée : le PATCH réussit mais le re-scan voit le code EN DOUBLE → réallocation
    de CET item (nouveau max+1), succès à la 2e tentative."""
    client = _FauxClientCRM(
        etape="Gagnée", code_mission="",
        # it.1 : before=[5] → code 6 ; PATCH 200 ; after=[5,6,6] (doublon) → réallouer
        # it.2 : before=[5,6] → code 7 ; PATCH 200 ; after=[5,6,7] (propre) → succès
        scan_responses=[[5], [5, 6, 6], [5, 6], [5, 6, 7]], patch_statuses=[200, 200],
    )
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_code_mission)

    res = fn(None, opportunite_id="O-042")

    assert res["code_mission"] == 7 and res["tentatives"] == 2
    assert len(_patchs(client)) == 2, "réécriture de l'item courant après détection de la course."


def test_allouer_code_mission_config_crm_absente_leve_configmanquante(_sans_porte, monkeypatch):
    """(40) GRAPH_CRM_LIST_ID (ou GRAPH_SITE_ID) absente → ConfigManquante, AVANT toute ouverture
    de client httpx (fail-closed : la config précède le réseau)."""
    monkeypatch.delenv("GRAPH_CRM_LIST_ID", raising=False)
    monkeypatch.delenv("GRAPH_SITE_ID", raising=False)

    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré une config CRM absente.")

    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.allouer_code_mission)
    with pytest.raises(server.ConfigManquante):
        fn(None, opportunite_id="O-042")


@pytest.mark.parametrize("mauvais", ["", "   ", None])
def test_allouer_code_mission_opportunite_id_vide_refuse(_sans_porte, monkeypatch, mauvais):
    """(41) opportunite_id vide / blanc / None → ValueError, AVANT toute ouverture de client httpx."""
    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré un opportunite_id vide.")

    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.allouer_code_mission)
    with pytest.raises(ValueError):
        fn(None, opportunite_id=mauvais)


# --------------------------------------------------------------------------------------------
# allouer_num_facture — allocateur NumFacture ATOMIQUE (T-0030), registre « Factures »
# Écriture SOURCE bornée par construction : cible FIGÉE (Liste « Factures », GRAPH_FACTURES_LIST_ID,
# même site que « CRM »), IDEMPOTENCE par clé (CodeMission, EtiquetteLocale), allocation
# F-AAAA-NNNN = max de l'année + 1 (0001 si aucun) à l'ÉMISSION, post-vérification anti-course
# bornée (tie-break déterministe par item_id), jamais de recyclage ni de suppression. Cran validé.
# --------------------------------------------------------------------------------------------

class _FauxClientFactures:
    """Client httpx factice pour allouer_num_facture (registre « Factures »).

    Piloté par `scans` : une liste d'ÉTATS successifs du registre ; chaque état est une liste
    d'items {"id": ..., "fields": {...}}. Le dernier état est répété si la séquence est épuisée.
      - GET .../items          → SCAN : renvoie l'état courant puis avance le compteur ;
      - GET .../items/{id}      → relecture d'un item (etag + fields) SANS avancer le compteur ;
      - POST .../items          → CRÉATION : enregistre les fields dans `self.posts`, renvoie
                                   {"id": post_id} avec le statut `post_status` (201 nominal) ;
      - PATCH .../items/{id}/fields → statut consommé dans l'ordre de `patch_statuses` (défaut 200).
    Enregistre chaque appel dans `self.appels` [(méthode, url, corps|params)]."""

    def __init__(self, scans, post_id="NEW-1", post_status=201, patch_statuses=None,
                 item_etag='W/"f-1"'):
        self._scans = [list(s) for s in scans]
        self._post_id = post_id
        self._post_status = post_status
        self._patch_statuses = list(patch_statuses) if patch_statuses is not None else [200]
        self._item_etag = item_etag
        self._scan_i = 0
        self._patch_i = 0
        self.appels = []
        self.entetes_appels = []
        self.posts = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def _etat(self):
        return self._scans[self._scan_i] if self._scan_i < len(self._scans) else self._scans[-1]

    def get(self, url, headers=None, params=None):
        self.appels.append(("GET", url, params))
        self.entetes_appels.append(("GET", url, headers or {}))
        if url.endswith("/items"):
            etat = self._etat()
            self._scan_i += 1
            return _RepWb(200, {"value": [{"id": it["id"], "fields": it["fields"]} for it in etat]})
        # GET item par id (relecture d'ETag au renumérotage) — n'avance PAS le compteur de scan.
        item_id = url.rsplit("/items/", 1)[-1]
        for it in self._etat():
            if str(it["id"]) == str(item_id):
                return _RepWb(200, {"@odata.etag": self._item_etag, "fields": it["fields"]})
        return _RepWb(404, {})

    def post(self, url, headers=None, json=None):
        self.appels.append(("POST", url, json))
        self.entetes_appels.append(("POST", url, headers or {}))
        champs = (json or {}).get("fields")
        self.posts.append(champs)
        return _RepWb(self._post_status, {"id": self._post_id, "fields": champs})

    def patch(self, url, headers=None, json=None):
        self.appels.append(("PATCH", url, json))
        self.entetes_appels.append(("PATCH", url, headers or {}))
        st = self._patch_statuses[self._patch_i] if self._patch_i < len(self._patch_statuses) else self._patch_statuses[-1]
        self._patch_i += 1
        return _RepWb(st, {})


_CLE_GESTE = "geste-001"   # clé de geste de `_entrees_ok()` — le geste « nominal » des tests
_AUTO = object()           # sentinelle : CleEmission dérivée de l'item_id


def _item_fact(item_id, title, code_mission, etiquette, statut="émise", cle_emission=_AUTO,
               date_emission=None):
    """Fabrique un item de registre {"id", "fields"} pour piloter _FauxClientFactures.

    `CleEmission` est par défaut DÉRIVÉE de l'item_id (« geste-<id> ») : deux items simulés ne
    partagent donc JAMAIS la clé de geste par accident — sans quoi l'idempotence de geste ferait
    court-circuiter les tests de séquence. Passer `cle_emission=None` simule la COLONNE ABSENTE du
    registre, le cas que la garde anti-faux-vert doit attraper. `date_emission` n'est posée que pour
    exercer le contrôle d'ORDRE (§2 bis (e)) : les seeds réels n'en portent pas."""
    cle = f"geste-{item_id}" if cle_emission is _AUTO else cle_emission
    champs = {"Title": title, "CodeMission": code_mission, "EtiquetteLocale": etiquette, "Statut": statut}
    if cle is not None:
        champs["CleEmission"] = cle
    if date_emission is not None:
        champs["DateEmission"] = date_emission
    return {"id": item_id, "fields": champs}


def _item_mien(item_id, title, code_mission="5", etiquette="2026-07-siteflow", **kw):
    """L'item tel qu'il EXISTE APRÈS notre POST : il porte NOTRE clé de geste (`_entrees_ok`)."""
    kw.setdefault("cle_emission", _CLE_GESTE)
    return _item_fact(item_id, title, code_mission, etiquette, **kw)


class _FauxDatetime:
    """Fige l'horloge du serveur à 2026-07-28 (année → NNNN, DateEmission déterministe)."""

    @staticmethod
    def now(tz=None):
        import datetime as _dt
        return _dt.datetime(2026, 7, 28, 9, 30, 0, tzinfo=_dt.timezone.utc)


@pytest.fixture
def _factures_2026(monkeypatch):
    """Config « Factures » valide + jeton neutralisé + horloge figée à 2026, pour exercer le corps
    réseau (mocké) de l'allocateur. Aucun secret ; aucune variable d'environnement réelle requise."""
    monkeypatch.setattr(server, "_config_factures", lambda: {"site_id": "SITE-1", "factures_list_id": "FACT-1"})
    monkeypatch.setattr(server, "_entetes", lambda: {"Authorization": "Bearer faketoken"})
    monkeypatch.setattr(server, "datetime", _FauxDatetime)


def _posts(client):
    return [c for (m, _u, c) in client.appels if m == "POST"]


def _entrees_ok():
    return dict(code_mission=5, etiquette_locale="2026-07-siteflow", mois_ca="2026-07-01",
                montant_ht=12000, echeance="2026-08-31", cle_emission=_CLE_GESTE)


def test_allouer_num_facture_rejeu_du_meme_geste_rend_le_meme_numero(_sans_porte, _factures_2026, monkeypatch):
    """(42) IDEMPOTENCE DE GESTE (v1.33 §2 bis (d)) : la MÊME `cle_emission` déjà au registre → on
    REND son NumFacture existant, SANS aucun POST. C'est le REJEU (double clic, retry réseau,
    réponse perdue) : aucun numéro n'est brûlé par un incident technique."""
    registre = [_item_fact("42", "F-2026-003", "5", "2026-07-siteflow", cle_emission=_CLE_GESTE)]
    client = _FauxClientFactures(scans=[registre])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    res = fn(None, **_entrees_ok())

    assert res == {"num_facture": "F-2026-003", "item_id": "42", "idempotent": True, "tentatives": 0}
    assert not _posts(client), "clé de GESTE déjà au registre → aucune création (rejeu)."


def test_allouer_num_facture_meme_prestation_cles_de_geste_differentes_deux_numeros_neufs(
    _sans_porte, _factures_2026, monkeypatch
):
    """(42 bis) LA RÈGLE MÉTIER, arbitrage gardien du 06/08/2026 (v1.33 §2 bis (a)) : deux émissions
    de la MÊME prestation (même CodeMission, même EtiquetteLocale) sous des `cle_emission`
    DIFFÉRENTES reçoivent DEUX numéros DISTINCTS et CROISSANTS — avoir, refacturation, réécriture.
    C'est le cas que l'ancienne idempotence par prestation rendait IMPOSSIBLE (elle rendait
    silencieusement l'ancien numéro) : ce test encode l'arbitrage, il ne doit jamais disparaître."""
    seed = _item_fact("40", "F-2026-0003", "5", "2026-07-siteflow", cle_emission="geste-000")
    fn = _sous_jacente(server.allouer_num_facture)

    # 1re émission : geste-001 → numéro NEUF (le seed n'est PAS rendu, malgré la prestation identique).
    apres_1 = [seed, _item_mien("NEW-1", "F-2026-0004")]
    client_1 = _FauxClientFactures(scans=[[seed], apres_1], post_id="NEW-1")
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client_1)
    res_1 = fn(None, **_entrees_ok())

    # 2de émission : MÊME prestation, geste-002 → encore un numéro NEUF.
    entrees_2 = {**_entrees_ok(), "cle_emission": "geste-002"}
    apres_2 = apres_1 + [_item_mien("NEW-2", "F-2026-0005", cle_emission="geste-002")]
    client_2 = _FauxClientFactures(scans=[apres_1, apres_2], post_id="NEW-2")
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client_2)
    res_2 = fn(None, **entrees_2)

    assert res_1["num_facture"] == "F-2026-0004" and res_1["idempotent"] is False
    assert res_2["num_facture"] == "F-2026-0005" and res_2["idempotent"] is False
    assert res_1["num_facture"] != res_2["num_facture"], "une émission = un numéro NEUF (§2 bis (a))."
    assert _posts(client_1) and _posts(client_2), "chaque geste CRÉE : aucun numéro n'est réutilisé."
    assert _posts(client_1)[0]["fields"]["CleEmission"] == _CLE_GESTE
    assert _posts(client_2)[0]["fields"]["CleEmission"] == "geste-002"


def test_allouer_num_facture_premiere_de_l_annee_est_0001(_sans_porte, _factures_2026, monkeypatch):
    """(43) Registre vide pour l'année → premier numéro = F-2026-0001, créé avec Statut « émise »."""
    client = _FauxClientFactures(
        scans=[[], [_item_mien("NEW-1", "F-2026-0001")]],
    )
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    res = fn(None, **_entrees_ok())

    assert res["num_facture"] == "F-2026-0001"
    assert res["idempotent"] is False and res["item_id"] == "NEW-1"
    champs = _posts(client)[0]["fields"]
    assert champs["Title"] == "F-2026-0001"
    assert champs["Statut"] == "émise", "l'allocation pose Statut « émise » côté serveur."
    assert champs["DateEmission"] == "2026-07-28", "DateEmission = date du jour, posée côté serveur."
    assert champs["CodeMission"] == "5" and champs["EtiquetteLocale"] == "2026-07-siteflow"
    assert champs["CleEmission"] == _CLE_GESTE, "la clé de GESTE est écrite au registre (§2 bis (d))."
    assert "anomalie_ordre" not in res, "retour NOMINAL : aucune anomalie d'ordre signalée."


def test_allouer_num_facture_max_plus_un_de_l_annee(_sans_porte, _factures_2026, monkeypatch):
    """(44) NNNN = max des NNNN de l'ANNÉE + 1 : un an antérieur est ignoré ; 001/003 → 004."""
    avant = [
        _item_fact("1", "F-2025-0009", "9", "2025-vieux"),   # autre année → ignorée du max
        _item_fact("2", "F-2026-0001", "1", "a"),
        _item_fact("3", "F-2026-0003", "2", "b"),
    ]
    apres = avant + [_item_mien("NEW-1", "F-2026-0004")]
    client = _FauxClientFactures(scans=[avant, apres])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    res = fn(None, **_entrees_ok())

    assert res["num_facture"] == "F-2026-0004", "max de 2026 = 3 → 4 (l'item 2025 est ignoré)."
    assert _posts(client)[0]["fields"]["Title"] == "F-2026-0004"


def test_allouer_num_facture_cible_figee_liste_factures(_sans_porte, _factures_2026, monkeypatch):
    """(45) L'écriture (POST) ne vise QUE le registre « Factures » figé (FACT-1), jamais ailleurs."""
    client = _FauxClientFactures(scans=[[], [_item_mien("NEW-1", "F-2026-0001")]])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    fn(None, **_entrees_ok())

    urls_post = [u for (m, u, _c) in client.appels if m == "POST"]
    assert urls_post and all("/lists/FACT-1/items" in u for u in urls_post), \
        "le POST vise la Liste « Factures » figée (GRAPH_FACTURES_LIST_ID), et elle seule."


@pytest.mark.parametrize("champ,valeur", [
    ("code_mission", 0), ("code_mission", -3), ("code_mission", "abc"),
    ("etiquette_locale", ""), ("etiquette_locale", "   "),
    ("mois_ca", ""), ("echeance", ""),
    ("montant_ht", 0), ("montant_ht", -5), ("montant_ht", "pasunnombre"),
    # v1.33 §2 bis (d) : la clé de GESTE est OBLIGATOIRE — son absence est un refus, jamais une
    # dégradation silencieuse (sans elle, un rejeu brûlerait un second numéro).
    ("cle_emission", ""), ("cle_emission", "   "), ("cle_emission", None), ("cle_emission", 42),
    ("cle_emission", "x" * 201),
])
def test_allouer_num_facture_preconditions_refusees_avant_reseau(_sans_porte, champ, valeur, monkeypatch):
    """(46) Précondition non tenue → ValueError, AVANT toute ouverture de client httpx (fail-closed)."""
    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré une précondition non tenue.")

    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.allouer_num_facture)
    entrees = _entrees_ok()
    entrees[champ] = valeur
    with pytest.raises(ValueError):
        fn(None, **entrees)


def test_allouer_num_facture_config_absente_leve_configmanquante(_sans_porte, monkeypatch):
    """(47) GRAPH_FACTURES_LIST_ID (ou GRAPH_SITE_ID) absente → ConfigManquante, AVANT tout réseau."""
    monkeypatch.delenv("GRAPH_FACTURES_LIST_ID", raising=False)
    monkeypatch.delenv("GRAPH_SITE_ID", raising=False)

    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré une config « Factures » absente.")

    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.allouer_num_facture)
    with pytest.raises(server.ConfigManquante):
        fn(None, **_entrees_ok())


def test_allouer_num_facture_course_sur_numero_renumerote_le_perdant(_sans_porte, _factures_2026, monkeypatch):
    """(48) COURSE sur NNNN : mon item (id « NEW-9 », le plus grand) partage F-2026-0004 avec un
    item concurrent (id « 3 ») → tie-break déterministe : le petit id garde 0004, MON item est
    RENUMÉROTÉ en F-2026-0005 par PATCH If-Match, puis re-scan propre → succès."""
    avant = [_item_fact("2", "F-2026-0003", "2", "b")]
    # après création : mon NEW-9 a pris 0004, mais l'item 3 concurrent l'a aussi → doublon.
    apres_course = avant + [
        _item_fact("3", "F-2026-0004", "7", "concurrent"),
        _item_mien("NEW-9", "F-2026-0004"),
    ]
    # après renumérotage de NEW-9 → 0005 : plus de doublon.
    apres_propre = [
        _item_fact("2", "F-2026-0003", "2", "b"),
        _item_fact("3", "F-2026-0004", "7", "concurrent"),
        _item_mien("NEW-9", "F-2026-0005"),
    ]
    client = _FauxClientFactures(
        scans=[avant, apres_course, apres_propre],
        post_id="NEW-9", patch_statuses=[200],
    )
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    res = fn(None, **_entrees_ok())

    assert res["num_facture"] == "F-2026-0005", "mon item (grand id) est renuméroté au suivant."
    assert res["tentatives"] == 2
    patchs = [(u, c) for (m, u, c) in client.appels if m == "PATCH"]
    assert len(patchs) == 1 and patchs[0][0].endswith("/items/NEW-9/fields")
    assert patchs[0][1] == {"Title": "F-2026-0005"}, "le PATCH ne réécrit QUE le Title (renumérotage)."
    entetes_patch = [h for (m, _u, h) in client.entetes_appels if m == "PATCH"]
    assert entetes_patch[0].get("If-Match") == 'W/"f-1"', "le renumérotage porte l'If-Match (ETag lu)."


def test_allouer_num_facture_course_sur_numero_canonique_garde(_sans_porte, _factures_2026, monkeypatch):
    """(49) COURSE sur NNNN mais MON item (id « 1 », le plus petit) est CANONIQUE → il GARDE
    F-2026-0004 ; aucun renumérotage (aucun PATCH), succès direct."""
    avant = [_item_fact("2", "F-2026-0003", "2", "b")]
    apres_course = [
        _item_mien("1", "F-2026-0004"),  # mon item, plus petit id
        _item_fact("2", "F-2026-0003", "2", "b"),
        _item_fact("9", "F-2026-0004", "7", "concurrent"),        # concurrent, plus grand id
    ]
    client = _FauxClientFactures(scans=[avant, apres_course], post_id="1")
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    res = fn(None, **_entrees_ok())

    assert res["num_facture"] == "F-2026-0004" and res["tentatives"] == 1
    assert not [m for (m, _u, _c) in client.appels if m == "PATCH"], \
        "l'item canonique GARDE son numéro : aucun renumérotage."


def test_allouer_num_facture_doublon_cle_de_geste_perdant_fail_closed(_sans_porte, _factures_2026, monkeypatch):
    """(50) DOUBLON DE CLÉ DE GESTE créé concurremment (deux exécutions du MÊME geste) et mon item
    NON canonique → RuntimeError explicite, AUCUNE suppression (l'outil n'en a pas la primitive) :
    réconciliation gardien signalée. Note : un doublon de PRESTATION n'est plus une anomalie."""
    apres = [
        _item_mien("1", "F-2026-0004"),      # concurrent canonique (petit id), MÊME clé de geste
        _item_mien("NEW-9", "F-2026-0005"),  # le mien, même clé de geste, plus grand id
    ]
    client = _FauxClientFactures(scans=[[], apres], post_id="NEW-9")
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    with pytest.raises(RuntimeError):
        fn(None, **_entrees_ok())
    # Fail-closed : jamais de DELETE (l'outil ne supprime pas).
    assert not [m for (m, _u, _c) in client.appels if m == "DELETE"], \
        "aucune suppression : l'orphelin est signalé pour réconciliation gardien, jamais purgé."


def test_allouer_num_facture_colonne_cle_emission_absente_fail_closed(_sans_porte, _factures_2026, monkeypatch):
    """(50 bis) GARDE ANTI-FAUX-VERT (v1.33 §2 bis (d)) : SharePoint ignore SILENCIEUSEMENT un champ
    inconnu. Si l'élément relu ne porte pas la `CleEmission` écrite, la colonne est absente du
    registre et l'idempotence de geste est INOPÉRANTE — un rejeu allouerait un second numéro. On
    exige un RuntimeError EXPLICITE (élément existant nommé, runbook gardien), et AUCUNE
    suppression. Sans cette garde, la conformité au canon serait un faux-vert : c'est la classe de
    défaut d'`impact.py` sans PyYAML, qu'on ne rejoue pas."""
    # L'item relu N'A PAS de CleEmission (cle_emission=None) : colonne absente du registre.
    apres = [_item_fact("NEW-1", "F-2026-0001", "5", "2026-07-siteflow", cle_emission=None)]
    client = _FauxClientFactures(scans=[[], apres])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    with pytest.raises(RuntimeError) as exc:
        fn(None, **_entrees_ok())

    message = str(exc.value)
    assert "CleEmission" in message, "la cause est NOMMÉE : la colonne du registre."
    assert "F-2026-0001" in message and "NEW-1" in message, \
        "l'élément créé EXISTE et son numéro est dit — rien n'est caché au gardien."
    assert "RUNBOOK GARDIEN" in message.upper(), "le remède est nommé (créer la colonne)."
    assert not [m for (m, _u, _c) in client.appels if m == "DELETE"], \
        "aucune suppression : l'outil n'en a pas la primitive."


def test_allouer_num_facture_anomalie_ordre_signalee_sans_refus(_sans_porte, _factures_2026, monkeypatch):
    """(50 ter) CONTRÔLE D'ORDRE (v1.33 §2 bis (e)) : une facture de NNNN INFÉRIEUR portant une
    DateEmission POSTÉRIEURE à la nôtre viole l'ordre. Le canon exige un SIGNALEMENT — jamais un
    refus, jamais une correction, jamais la réécriture d'un numéro déjà alloué : la fonction rend
    donc NORMALEMENT son numéro, avec la clé `anomalie_ordre` en plus."""
    # Notre DateEmission est celle de l'horloge figée : 2026-07-28. L'item 0003 est POSTÉRIEUR (30/07).
    anterieur = _item_fact("1", "F-2026-0003", "2", "b", date_emission="2026-07-30T00:00:00Z")
    apres = [anterieur, _item_mien("NEW-1", "F-2026-0004", date_emission="2026-07-28")]
    client = _FauxClientFactures(scans=[[anterieur], apres])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    res = fn(None, **_entrees_ok())

    assert res["num_facture"] == "F-2026-0004", "le numéro est rendu NORMALEMENT (aucun refus)."
    assert res["idempotent"] is False
    anomalie = res.get("anomalie_ordre")
    assert anomalie, "la violation d'ordre est SIGNALÉE au retour."
    assert anomalie["numero_anterieur"] == "F-2026-0003" and anomalie["mon_numero"] == "F-2026-0004"
    assert not [m for (m, _u, c) in client.appels if m == "PATCH"], \
        "JAMAIS de réécriture d'un numéro pour « réparer » l'ordre (§2 bis (e))."


def test_allouer_num_facture_ordre_respecte_ne_signale_rien(_sans_porte, _factures_2026, monkeypatch):
    """(50 quater) CONTRE-CAS du contrôle d'ordre : dates croissantes avec NNNN → AUCUNE clé
    `anomalie_ordre` au retour. Un contrôle qui crie toujours ne vaut rien ; celui-ci se tait quand
    l'ordre est tenu. Une DateEmission NULLE (seed historique) est tolérée et ignorée."""
    anterieur = _item_fact("1", "F-2026-0003", "2", "b", date_emission="2026-07-20")
    seed_sans_date = _item_fact("2", "F-2026-002", "9", "seed")  # aucune DateEmission → ignoré
    apres = [anterieur, seed_sans_date, _item_mien("NEW-1", "F-2026-0004", date_emission="2026-07-28")]
    client = _FauxClientFactures(scans=[[anterieur, seed_sans_date], apres])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    res = fn(None, **_entrees_ok())

    assert res["num_facture"] == "F-2026-0004"
    assert "anomalie_ordre" not in res, "ordre tenu (et seed sans date toléré) → aucun signalement."


# --------------------------------------------------------------------------------------------
# Correctif 0.19.1 (T-0030) — scan du registre aveugle (incident du 31/07, épreuve post-0.19.0)
#   (1) _RE_NUM_FACTURE exigeait NNNN sur 4 chiffres EXACTS → les seeds réels du registre
#       (F-AAAA-NNN, numéros des PDF émis, sur 3 chiffres) étaient exclus du max → séquence
#       repartie à 0001 (doublon).
#   (2) CodeMission est une colonne SharePoint Number ; Graph la sérialise en double intégral
#       (1 → 1.0) ; _code_mission_en_entier faisait str(brut).isdigit() → "1.0" échouait → None
#       → la clé d'idempotence (CodeMission, EtiquetteLocale) ne matchait jamais, et la
#       post-vérification anti-course était aveugle pareil (écriture d'un doublon de clé).
# Arbitrages gardien du 31/07 : lecture permissive \d{3,4} (les seeds comptent dans la séquence),
# écriture inchangée en 4 chiffres (:04d), contrat modele-donnees §2 bis INCHANGÉ.
# --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("brut,attendu", [
    (1.0, 1),        # double intégral (sérialisation Graph d'une colonne Number) → 1
    ("1.0", 1),      # même chose en chaîne (selon le sérialiseur) → 1
    (1, 1),          # entier natif → 1 (chemin isdigit inchangé)
    ("1", 1),        # chaîne d'entier → 1 (chemin isdigit inchangé)
    (1.5, None),     # double NON entier → rejeté (aucune facture partielle de code)
    ("x", None),     # texte libre → rejeté
    (None, None),    # vide → rejeté
    (0.0, None),     # zéro (double intégral) → rejeté (code ≥ 1 exigé)
])
def test_code_mission_en_entier_tolere_le_double_graph(brut, attendu):
    """(51) _code_mission_en_entier tolère le double intégral servi par Graph pour une colonne
    Number (1.0, « 1.0»), reste RÉTROCOMPATIBLE sur les entiers/chaînes, et rejette toujours un
    double non entier, un texte libre, le vide et le zéro (correctif 0.19.1, cause racine 2)."""
    assert server._code_mission_en_entier(brut) == attendu


def test_allouer_num_facture_seed_de_meme_prestation_ne_court_circuite_plus(_sans_porte, _factures_2026, monkeypatch):
    """(52) RENVERSEMENT v1.33 : un seed de la MÊME prestation (CodeMission sérialisé en double
    Graph 1.0, NumFacture sur 3 chiffres) ne court-circuite PLUS l'allocation — la clé d'idempotence
    est le GESTE, pas la prestation. L'appel reçoit un numéro NEUF (max des NNN + 1 = 0002), le seed
    reste intact. Avant v1.33, ce même appel rendait « F-2026-001 » en silence, ce qui contredisait
    « une émission = un numéro » (§2 bis (a) et (c))."""
    seed = _item_fact("4", "F-2026-001", 1.0, "2026-05-siteflow", cle_emission="geste-seed")
    apres = [seed, _item_mien("NEW-1", "F-2026-0002", code_mission=1, etiquette="2026-05-siteflow",
                              cle_emission="geste-avoir")]
    client = _FauxClientFactures(scans=[[seed], apres])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    res = fn(None, code_mission=1, etiquette_locale="2026-05-siteflow",
             mois_ca="2026-05-01", montant_ht=15300, echeance="2026-06-01",
             cle_emission="geste-avoir")

    assert res["num_facture"] == "F-2026-0002" and res["idempotent"] is False
    assert _posts(client), "geste NOUVEAU sur une prestation déjà facturée → création (avoir)."
    assert server._code_mission_en_entier(1.0) == 1, "le double Graph reste toléré à la lecture."


def test_allouer_num_facture_sequence_compte_les_seeds_3_chiffres(_sans_porte, _factures_2026, monkeypatch):
    """(53) SÉQUENCE : trois seeds réels sur 3 chiffres (F-2026-001..003) comptent dans le max →
    la prochaine allocation est F-2026-0004 (avant 0.19.1 : seeds exclus → repartait à 0001)."""
    avant = [
        _item_fact("1", "F-2026-001", "1", "2026-05-siteflow"),
        _item_fact("2", "F-2026-002", "1", "2026-06-siteflow"),
        _item_fact("3", "F-2026-003", "1", "2026-07-siteflow"),
    ]
    apres = avant + [_item_mien("NEW-1", "F-2026-0004", etiquette="2026-07-datalab")]
    client = _FauxClientFactures(scans=[avant, apres])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    res = fn(None, code_mission=5, etiquette_locale="2026-07-datalab",
             mois_ca="2026-07-01", montant_ht=12000, echeance="2026-08-31",
             cle_emission=_CLE_GESTE)

    assert res["num_facture"] == "F-2026-0004", "max des NNN (3 chiffres) = 3 → 4."
    assert _posts(client)[0]["fields"]["Title"] == "F-2026-0004"


def test_allouer_num_facture_sequence_mixte_3_et_4_chiffres(_sans_porte, _factures_2026, monkeypatch):
    """(54) SÉQUENCE mixte : un seed 3 chiffres (F-2026-003) et un numéro 4 chiffres (F-2026-0005)
    dans la même année → max = 5 → prochaine allocation F-2026-0006 (lecture \\d{3,4} unifiée)."""
    avant = [
        _item_fact("1", "F-2026-003", "1", "2026-07-siteflow"),
        _item_fact("2", "F-2026-0005", "2", "2026-07-datalab"),
    ]
    apres = avant + [_item_mien("NEW-1", "F-2026-0006", code_mission="3", etiquette="2026-07-arabelle")]
    client = _FauxClientFactures(scans=[avant, apres])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.allouer_num_facture)

    res = fn(None, code_mission=3, etiquette_locale="2026-07-arabelle",
             mois_ca="2026-07-01", montant_ht=9000, echeance="2026-08-31",
             cle_emission=_CLE_GESTE)

    assert res["num_facture"] == "F-2026-0006", "max(3, 5) = 5 → 6."
    assert _posts(client)[0]["fields"]["Title"] == "F-2026-0006"


# --------------------------------------------------------------------------------------------
# ANTI-DIVERGENCE de projection du schéma (T-0030, correctif 0.19.2, épreuve 3g)
# TABLES_GABARIT est la PROJECTION machine de contrats/socle/modele-donnees.md §5.2 (v1.25) —
# le contrat FAIT FOI, l'ordre des en-têtes est figé. L'épreuve 3g a stoppé une dérivation AVANT
# tout effet de bord : TABLES_GABARIT.T_Echeancier n'avait que 7 colonnes (EtiquetteLocale
# manquante) alors que §5.2 v1.25 en a 8 — le trou de la chaîne #268 (contrat) → #272 (skill,
# « aucun code serveur »), la projection serveur n'ayant été portée par aucune des deux PRs.
# Ces listes littérales RECOPIENT le contrat : elles cassent la CI si la projection diverge à nouveau.
# --------------------------------------------------------------------------------------------

# Ordre EXACT des en-têtes, tel qu'il fait foi dans modele-donnees.md §5.2 (v1.25).
_ENTETES_CONTRAT_52 = {
    "T_Affectations": ("CodeMission", "Ressource", "Mois", "JoursPrevus"),
    "T_Imputations": ("CodeMission", "Ressource", "Mois", "JoursRealises", "StatutValidation"),
    "T_Echeancier": ("NumFacture", "CodeMission", "EtiquetteLocale", "MoisCA", "MontantHT", "Echeance", "Statut", "LienFacture"),
}


def test_tables_gabarit_projette_exactement_modele_donnees_52():
    """(55) TABLES_GABARIT est la projection FIDÈLE de §5.2 : mêmes tables, mêmes en-têtes DANS
    L'ORDRE. Casse la CI si la projection serveur diverge du contrat (rejeu de l'écart 3g)."""
    projete = {table: tuple(entetes) for (_feuille, table, entetes) in server.TABLES_GABARIT}
    assert projete == _ENTETES_CONTRAT_52


def test_t_echeancier_porte_etiquettelocale_en_position_contractuelle():
    """(56) NON-RÉGRESSION 0.19.2 ciblée : T_Echeancier porte bien EtiquetteLocale, en 3e position
    (après CodeMission, avant MoisCA) — clé de réconciliation avec la saisie (§5.2 / §5.6)."""
    echeancier = next(entetes for (_f, table, entetes) in server.TABLES_GABARIT if table == "T_Echeancier")
    assert "EtiquetteLocale" in echeancier, "EtiquetteLocale absente — régression de l'écart 3g."
    assert echeancier.index("EtiquetteLocale") == 2, "EtiquetteLocale doit suivre CodeMission (§5.2)."
    assert len(echeancier) == 8, "T_Echeancier v1.25 a 8 en-têtes."


# --------------------------------------------------------------------------------------------
# inscrire_cout_structure — inscription du coût de structure RÉEL (T-0032), table T_Structure
# Écriture SOURCE bornée par construction : cible FIGÉE (classeur referentiel-structure.xlsx via
# GRAPH_REF_STRUCTURE_*, table T_Structure, PosteCout figé « fonctionnement-reel »), fail-closed,
# idempotente par (Mois, fonctionnement-reel), sur validation d'une ligne candidate (proposition_id).
# Cran VALIDÉ (table-des-crans v1.15). Miroir gouverné de allouer_num_facture.
# --------------------------------------------------------------------------------------------

class _FauxClientStructure:
    """Client httpx factice pour inscrire_cout_structure (table Workbook T_Structure).

    Maintient l'état des lignes `self.rows` (chaque ligne = liste de valeurs, ordre des colonnes).
      - GET   .../columns → en-têtes physiques (self._columns) au format Workbook (statut columns_status) ;
      - GET   .../rows    → lignes courantes {"values": [[...]]} ;
      - POST  .../rows    → append ({"index": None, "values": [[...]]}) → grandit self.rows (statut post_status) ;
      - PATCH .../rows/itemAt(index=N) → REMPLACE self.rows[N] ({"values": [[...]]}, statut patch_status),
        chemin de `corriger_cout_structure` (0.21.0) : jamais un append, la table ne grandit pas.
    Enregistre chaque appel dans self.appels [(méthode, url, corps|params)]."""

    def __init__(self, rows=None, columns=None, columns_status=200, post_status=201, patch_status=200):
        self.rows = [list(r) for r in (rows or [])]
        self._columns = list(columns) if columns is not None else list(server.ENTETES_T_STRUCTURE)
        self._columns_status = columns_status
        self._post_status = post_status
        self._patch_status = patch_status
        self.appels = []
        self.entetes_appels = []

    def _stocker(self, ligne):
        """Transformation appliquée à une ligne AU STOCKAGE (identité ici ; le sous-type SÉRIAL la surcharge).
        Partagée par POST et PATCH : les deux chemins d'écriture stockent donc de la MÊME façon."""
        return list(ligne)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get(self, url, headers=None, params=None):
        self.appels.append(("GET", url, params))
        self.entetes_appels.append(("GET", url, headers or {}))
        if url.endswith("/columns"):
            if self._columns_status != 200:
                return _RepWb(self._columns_status, {})
            value = [
                {"name": nom, "values": [[nom]] + [[r[j] if j < len(r) else ""] for r in self.rows]}
                for j, nom in enumerate(self._columns)
            ]
            return _RepWb(200, {"value": value})
        if url.endswith("/rows"):
            return _RepWb(200, {"value": [{"values": [list(r)]} for r in self.rows]})
        return _RepWb(200, {})

    def post(self, url, headers=None, json=None):
        self.appels.append(("POST", url, json))
        self.entetes_appels.append(("POST", url, headers or {}))
        if url.endswith("/rows"):
            for ligne in (json or {}).get("values", []):
                self.rows.append(self._stocker(ligne))
        return _RepWb(self._post_status, {})

    def patch(self, url, headers=None, json=None):
        self.appels.append(("PATCH", url, json))
        self.entetes_appels.append(("PATCH", url, headers or {}))
        m = re.search(r"/rows/itemAt\(index=(\d+)\)$", url)
        if m:
            i = int(m.group(1))
            for ligne in (json or {}).get("values", []):
                self.rows[i] = self._stocker(ligne)  # REMPLACE en place — la table ne grandit jamais
        return _RepWb(self._patch_status, {})


@pytest.fixture
def _ref_structure_factice(monkeypatch):
    """Config réf. structure valide + jeton neutralisé, pour exercer le corps réseau (mocké) de
    l'inscription. Aucun secret ; aucune variable d'environnement réelle requise."""
    monkeypatch.setattr(
        server, "_config_ref_structure",
        lambda: {"drive_id": "DRIVE-REF", "item_id": "ITEM-REFSTRUCT"},
    )
    monkeypatch.setattr(server, "_entetes", lambda: {"Authorization": "Bearer faketoken"})


def _entrees_structure_ok():
    return dict(mois="2026-07-01", montant=66000, proposition_id="ZP-2026-07-structure")


# --- ANTI-DIVERGENCE de projection (leçon S45) : ENTETES_T_STRUCTURE recopie modele-donnees §5.3.
# Le contrat FAIT FOI (Mois, PosteCout, Montant, dans l'ordre). Ce littéral casse la CI si la
# projection serveur diverge du schéma T_Structure — rejeu de la classe de bug de l'écart 3g.
_ENTETES_CONTRAT_53 = ("Mois", "PosteCout", "Montant")


def test_entetes_t_structure_projette_exactement_modele_donnees_53():
    """(57) ANTI-DIVERGENCE : ENTETES_T_STRUCTURE == §5.3 (Mois, PosteCout, Montant), dans l'ordre.
    Casse la CI si la projection serveur diverge du contrat (leçon S45)."""
    assert server.ENTETES_T_STRUCTURE == _ENTETES_CONTRAT_53


def test_poste_cout_structure_reel_est_fige():
    """(58) Le PosteCout du réel est figé côté serveur = « fonctionnement-reel » (§5.3, une ligne/mois)."""
    assert server.POSTE_STRUCTURE_REEL == "fonctionnement-reel"


def test_inscrire_cout_structure_config_absente_leve_configmanquante(_sans_porte, monkeypatch):
    """(59) GRAPH_REF_STRUCTURE_* absentes → ConfigManquante, AVANT tout réseau (fail-closed, pas de fallback)."""
    monkeypatch.delenv("GRAPH_REF_STRUCTURE_DRIVE_ID", raising=False)
    monkeypatch.delenv("GRAPH_REF_STRUCTURE_ITEM_ID", raising=False)

    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré une config « réf. structure » absente.")

    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.inscrire_cout_structure)
    with pytest.raises(server.ConfigManquante):
        fn(None, **_entrees_structure_ok())


@pytest.mark.parametrize("champ,valeur", [
    ("mois", "2026-07-15"),      # pas le 1er du mois
    ("mois", "2026-13-01"),      # mois calendaire invalide
    ("mois", "juillet"),         # pas une date ISO
    ("mois", ""),                # vide
    ("montant", 0),              # pas > 0
    ("montant", -100),           # négatif
    ("montant", "pasunnombre"),  # pas un nombre
    ("proposition_id", ""),      # obligatoire (fil d'audit)
    ("proposition_id", "   "),
])
def test_inscrire_cout_structure_preconditions_refusees_avant_reseau(
    _sans_porte, _ref_structure_factice, champ, valeur, monkeypatch
):
    """(60) Précondition non tenue (mois pas au 1er / invalide, montant ≤ 0, proposition_id manquant)
    → ValueError, AVANT toute ouverture de client httpx (fail-closed, rien écrit)."""
    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré une précondition non tenue.")

    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.inscrire_cout_structure)
    entrees = _entrees_structure_ok()
    entrees[champ] = valeur
    with pytest.raises(ValueError):
        fn(None, **entrees)


def test_inscrire_cout_structure_doublon_mois_refuse_sans_ecriture(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(61) IDEMPOTENCE : une ligne (Mois, « fonctionnement-reel ») déjà présente pour ce mois →
    RuntimeError (REFUS explicite), et AUCUN POST (jamais d'écrasement, jamais de doublon)."""
    existant = [["2026-07-01", "fonctionnement-reel", 50000]]
    client = _FauxClientStructure(rows=existant)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.inscrire_cout_structure)
    with pytest.raises(RuntimeError):
        fn(None, **_entrees_structure_ok())
    assert not [c for (m, _u, c) in client.appels if m == "POST"], "aucune écriture si le mois est déjà inscrit."


def test_inscrire_cout_structure_schema_divergent_refuse(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(62) GARDE ANTI-DIVERGENCE à l'exécution : si T_Structure ne sert pas EXACTEMENT les en-têtes
    §5.3, l'écriture est refusée (RuntimeError) et AUCUN POST (fail-closed, pas d'écriture aveugle)."""
    client = _FauxClientStructure(columns=("Mois", "PosteCout"))  # « Montant » manquant → divergence
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.inscrire_cout_structure)
    with pytest.raises(RuntimeError):
        fn(None, **_entrees_structure_ok())
    assert not [c for (m, _u, c) in client.appels if m == "POST"], "schéma divergent → aucune écriture."


def test_inscrire_cout_structure_chemin_nominal_append_puis_relecture(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(63) CHEMIN NOMINAL : registre vide → validations → /columns → /rows (idempotence) → append
    d'UNE ligne (Mois, fonctionnement-reel, Montant, dans l'ordre §5.3) → relecture → retour tracé."""
    client = _FauxClientStructure(rows=[])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.inscrire_cout_structure)

    res = fn(None, mois="2026-07-01", montant=66000, proposition_id="ZP-2026-07-structure")

    posts = [c for (m, _u, c) in client.appels if m == "POST"]
    assert len(posts) == 1, "exactement un append."
    assert posts[0] == {"index": None, "values": [["2026-07-01", "fonctionnement-reel", 66000]]}, \
        "la ligne écrite porte les colonnes §5.3 dans l'ordre, PosteCout figé, montant intègre."
    assert res["mois"] == "2026-07-01"
    assert res["poste"] == "fonctionnement-reel"
    assert res["montant"] == 66000
    assert res["proposition_id"] == "ZP-2026-07-structure", "le fil d'audit (proposition_id) est tracé."
    assert res["ligne_relue"] == {"Mois": "2026-07-01", "PosteCout": "fonctionnement-reel", "Montant": 66000}


def test_inscrire_cout_structure_normalise_le_mois_au_premier(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(64) « 2026-07-01 » est écrit au 1er du mois (v1.26 : une ligne agrégée par mois) ; un montant
    intégral flottant (66000.0) est écrit sans « .0 »."""
    client = _FauxClientStructure(rows=[])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.inscrire_cout_structure)

    res = fn(None, mois="2026-07-01", montant=66000.0, proposition_id="ZP-1")

    assert res["mois"] == "2026-07-01" and res["montant"] == 66000
    assert client.rows == [["2026-07-01", "fonctionnement-reel", 66000]]


def test_inscrire_cout_structure_cible_figee_classeur_et_table(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(65) CIBLE FIGÉE : tous les appels visent le classeur (DRIVE-REF / ITEM-REFSTRUCT) et la table
    T_Structure, et RIEN d'autre — l'appelant n'a fourni aucun drive/item/table/poste."""
    client = _FauxClientStructure(rows=[])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.inscrire_cout_structure)

    fn(None, **_entrees_structure_ok())

    attendu = "/drives/DRIVE-REF/items/ITEM-REFSTRUCT/workbook/tables/T_Structure"
    assert client.appels, "au moins un appel réseau."
    for (m, u, _c) in client.appels:
        assert attendu in u, f"appel {m} hors de la cible figée : {u}"


def test_inscrire_cout_structure_ne_prend_aucune_cible_libre():
    """(66) Signature : inscrire_cout_structure n'expose AUCUN drive_id / item_id / table / poste —
    cible figée par construction ; l'appelant ne fournit que mois / montant / proposition_id."""
    params = _params(server.inscrire_cout_structure)
    assert params == {"mois", "montant", "proposition_id"}
    for interdit in ("drive_id", "item_id", "table", "poste", "poste_cout", "classeur"):
        assert interdit not in params


# --------------------------------------------------------------------------------------------
# Correctif 0.20.1 — le mois RELU n'est pas le mois ÉCRIT : l'API Workbook restitue un SÉRIAL Excel
# là où l'on a écrit « AAAA-MM-01 » (incident tenant du 01/08 : écriture OK, post-vérification en
# FAUX-ROUGE ; garde d'idempotence porteuse du même biais → risque de doublon). Un incident devient
# une régression CI (leçon S38). `_mois_en_iso` normalise sérial / ISO / date Excel, fail-closed.
# --------------------------------------------------------------------------------------------

def _iso_vers_serial_excel(iso: str) -> int:
    """Sérial Excel (jours depuis l'époque 1899-12-30 du serveur) d'une date ISO — comme le fait Excel."""
    d = server.datetime.strptime(iso, "%Y-%m-%d").replace(tzinfo=server.timezone.utc)
    return (d - server._EPOQUE_EXCEL).days


class _FauxClientStructureSerialExcel(_FauxClientStructure):
    """Comme `_FauxClientStructure`, mais RESTITUE la colonne `Mois` en SÉRIAL Excel — reproduit le
    01/08 : la valeur ISO « AAAA-MM-01 » écrite est reconvertie en sérial au stockage, si bien que la
    relecture (`/rows`) rend un NOMBRE, jamais la chaîne ISO écrite.

    La conversion vit dans `_stocker`, donc elle vaut pour les DEUX chemins d'écriture — l'append de
    `inscrire_cout_structure` ET le PATCH de `corriger_cout_structure` (0.21.0)."""

    def _stocker(self, ligne):
        l = list(ligne)
        l[0] = _iso_vers_serial_excel(str(l[0]))  # col 0 = Mois → sérial Excel
        return l


def test_inscrire_cout_structure_incident_0108_mois_serial_excel(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(67) INCIDENT 01/08, rejoué : la relecture Workbook rend le mois en SÉRIAL Excel. Le correctif
    0.20.1 fait que (a) la POST-VÉRIFICATION reconnaît la ligne (plus de faux-rouge) et (b) une SECONDE
    inscription du même mois est REFUSÉE par la garde d'idempotence (jamais de doublon)."""
    serial = _iso_vers_serial_excel("2026-07-01")
    assert serial == 46204, "sérial Excel de 2026-07-01 (époque 1899-12-30)."
    client = _FauxClientStructureSerialExcel(rows=[])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.inscrire_cout_structure)

    # (a) 1re inscription : écriture ISO, relecture SÉRIAL → la post-vérification RECONNAÎT la ligne.
    res = fn(None, mois="2026-07-01", montant=706.84, proposition_id="ZP-2026-07")
    assert res["mois"] == "2026-07-01" and res["montant"] == 706.84
    assert res["ligne_relue"] == {"Mois": 46204, "PosteCout": "fonctionnement-reel", "Montant": 706.84}, \
        "la ligne relue (sérial Excel) est reconnue comme celle du mois écrit — plus de faux-rouge."
    assert len([c for (m, _u, c) in client.appels if m == "POST"]) == 1

    # (b) 2de inscription du MÊME mois (le registre porte désormais le sérial) → REFUS, aucun 2e POST.
    with pytest.raises(RuntimeError):
        fn(None, mois="2026-07-01", montant=999, proposition_id="ZP-2026-07-bis")
    assert len([c for (m, _u, c) in client.appels if m == "POST"]) == 1, \
        "aucune 2de écriture : la garde d'idempotence reconnaît le sérial comme 2026-07-01."


@pytest.mark.parametrize("valeur,attendu", [
    (46204, "2026-07-01"),        # sérial entier
    (46204.0, "2026-07-01"),      # sérial flottant
    ("46204", "2026-07-01"),      # sérial en chaîne
    ("2026-07-01", "2026-07-01"), # ISO
    ("2026-07-01T00:00:00Z", "2026-07-01"),  # ISO + heure
    ("7/1/2026", "2026-07-01"),   # date Excel « m/j/aaaa »
])
def test_mois_en_iso_normalise_toutes_les_formes(valeur, attendu):
    """(68) `_mois_en_iso` rend « AAAA-MM-JJ » depuis un sérial Excel (entier/flottant/chaîne), une
    chaîne ISO (avec ou sans heure) ou une date Excel « m/j/aaaa »."""
    assert server._mois_en_iso(valeur) == attendu


@pytest.mark.parametrize("valeur", [None, "", "   ", "juillet", "abc", True, "2026-13-01", "13/40/2026"])
def test_mois_en_iso_inconvertible_leve_valueerror(valeur):
    """(69) FAIL-CLOSED : une valeur « Mois » inconvertible (vide, texte libre, booléen, date invalide)
    lève ValueError — jamais de devinette silencieuse (c'est le repli littéral buggé qui est supprimé)."""
    with pytest.raises(ValueError):
        server._mois_en_iso(valeur)


# --------------------------------------------------------------------------------------------
# corriger_cout_structure (0.21.0) — CORRECTION gouvernée d'un mois DÉJÀ inscrit dans T_Structure.
# Besoin STRUCTUREL (pièce tardive, avoir, oubli), pas un incident. Jumeau de inscrire_cout_structure :
# MÊME cible figée, MÊME `_mois_en_iso`, MÊME cran VALIDÉ (table-des-crans v1.16) — mais précondition
# INVERSE : la ligne du mois DOIT exister (sinon refus « rien à corriger », jamais de création
# déguisée). Écriture = PATCH itemAt de la ligne existante, JAMAIS un append : l'anti-doublon des
# deux primitives est préservé par construction.
# --------------------------------------------------------------------------------------------

def _entrees_correction_ok():
    return dict(mois="2026-07-01", montant=2860.67, proposition_id="ZP-2026-07-correction")


def _ligne_juillet(montant=706.84):
    """La ligne réellement inscrite sur le tenant le 01/08 (épreuve T-0032)."""
    return ["2026-07-01", "fonctionnement-reel", montant]


def test_corriger_cout_structure_chemin_nominal_patch_puis_relecture(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(70) CHEMIN NOMINAL : la ligne de 2026-07-01 existe à 706.84 → correction à 2860.67 → un PATCH
    itemAt(index=0) portant les colonnes §5.3 dans l'ordre, relecture à 2860.67, et TOUJOURS UNE SEULE
    ligne (jamais un append). L'ancien montant est rendu — la correction est auditable."""
    client = _FauxClientStructure(rows=[_ligne_juillet()])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.corriger_cout_structure)

    res = fn(None, **_entrees_correction_ok())

    patches = [(u, c) for (m, u, c) in client.appels if m == "PATCH"]
    assert len(patches) == 1, "exactement un PATCH."
    assert patches[0][0].endswith("/rows/itemAt(index=0)"), "la ligne EXISTANTE est adressée par index."
    assert patches[0][1] == {"values": [["2026-07-01", "fonctionnement-reel", 2860.67]]}, \
        "colonnes §5.3 dans l'ordre, PosteCout figé, NOUVEAU montant."
    assert not [c for (m, _u, c) in client.appels if m == "POST"], "une correction n'APPEND jamais."
    assert client.rows == [["2026-07-01", "fonctionnement-reel", 2860.67]], "une seule ligne, corrigée."
    assert res["mois"] == "2026-07-01" and res["poste"] == "fonctionnement-reel"
    assert res["ancien_montant"] == 706.84 and res["nouveau_montant"] == 2860.67
    assert res["proposition_id"] == "ZP-2026-07-correction", "le fil d'audit est tracé."
    assert res["ligne_relue"] == {"Mois": "2026-07-01", "PosteCout": "fonctionnement-reel", "Montant": 2860.67}


def test_corriger_cout_structure_mois_absent_refuse_sans_ecriture(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(71) SÉMANTIQUE INVERSE de l'idempotence : AUCUNE ligne pour ce mois → RuntimeError « rien à
    corriger », et AUCUNE écriture (ni PATCH ni POST) — jamais de création déguisée (c'est le rôle
    exclusif d'inscrire_cout_structure, qui porte la porte humaine de la 1re inscription)."""
    autres = [["2026-06-01", "fonctionnement-reel", 500]]   # un AUTRE mois, pas celui demandé
    client = _FauxClientStructure(rows=autres)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.corriger_cout_structure)

    with pytest.raises(RuntimeError, match="[Rr]ien à corriger"):
        fn(None, **_entrees_correction_ok())
    assert not [c for (m, _u, c) in client.appels if m in ("PATCH", "POST")], \
        "mois absent → zéro écriture."
    assert client.rows == autres, "la table est intacte."


def test_corriger_cout_structure_config_absente_leve_configmanquante(_sans_porte, monkeypatch):
    """(72) GRAPH_REF_STRUCTURE_* absentes → ConfigManquante, AVANT tout réseau (fail-closed, comme le jumeau)."""
    monkeypatch.delenv("GRAPH_REF_STRUCTURE_DRIVE_ID", raising=False)
    monkeypatch.delenv("GRAPH_REF_STRUCTURE_ITEM_ID", raising=False)

    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré une config « réf. structure » absente.")

    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.corriger_cout_structure)
    with pytest.raises(server.ConfigManquante):
        fn(None, **_entrees_correction_ok())


@pytest.mark.parametrize("champ,valeur", [
    ("mois", "2026-07-15"),      # pas le 1er du mois
    ("mois", "2026-13-01"),      # mois calendaire invalide
    ("mois", "juillet"),         # pas une date ISO
    ("mois", ""),                # vide
    ("montant", 0),              # pas > 0
    ("montant", -100),           # négatif
    ("montant", "pasunnombre"),  # pas un nombre
    ("proposition_id", ""),      # obligatoire (fil d'audit de la correction)
    ("proposition_id", "   "),
])
def test_corriger_cout_structure_preconditions_refusees_avant_reseau(
    _sans_porte, _ref_structure_factice, champ, valeur, monkeypatch
):
    """(73) Précondition non tenue (mois pas au 1er / invalide, NOUVEAU montant ≤ 0, proposition_id
    manquant) → ValueError AVANT toute ouverture de client httpx — mêmes gardes que le jumeau."""
    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré une précondition non tenue.")

    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.corriger_cout_structure)
    entrees = _entrees_correction_ok()
    entrees[champ] = valeur
    with pytest.raises(ValueError):
        fn(None, **entrees)


def test_corriger_cout_structure_schema_divergent_refuse(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(74) GARDE ANTI-DIVERGENCE à l'exécution : en-têtes servis ≠ §5.3 → RuntimeError et AUCUNE
    écriture — on ne PATCHe pas des cellules à l'aveugle dans le mauvais ordre."""
    client = _FauxClientStructure(rows=[_ligne_juillet()], columns=("Mois", "PosteCout"))
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.corriger_cout_structure)

    with pytest.raises(RuntimeError):
        fn(None, **_entrees_correction_ok())
    assert not [c for (m, _u, c) in client.appels if m in ("PATCH", "POST")], \
        "schéma divergent → aucune écriture."


def test_corriger_cout_structure_plusieurs_lignes_du_mois_refuse(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(75) UNICITÉ : si la source porte DEUX lignes du même mois (anomalie), on REFUSE — on ne devine
    pas laquelle corriger ; réconciliation gardien. Aucune écriture."""
    client = _FauxClientStructure(rows=[_ligne_juillet(), _ligne_juillet(999)])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.corriger_cout_structure)

    with pytest.raises(RuntimeError, match="[Aa]nomalie"):
        fn(None, **_entrees_correction_ok())
    assert not [c for (m, _u, c) in client.appels if m in ("PATCH", "POST")], "anomalie → aucune écriture."


def test_corriger_cout_structure_ne_touche_que_la_ligne_du_mois(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(76) CIBLAGE : parmi plusieurs lignes (autre mois, autre poste), seule celle du mois demandé ET
    du poste FIGÉ est corrigée — l'index PATCHé est bien le sien, les autres lignes sont intactes."""
    rows = [
        ["2026-06-01", "fonctionnement-reel", 500],   # autre mois
        ["2026-07-01", "autre-poste", 111],           # bon mois, MAUVAIS poste
        _ligne_juillet(),                             # la cible, en 3e position (index 2)
    ]
    client = _FauxClientStructure(rows=rows)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.corriger_cout_structure)

    fn(None, **_entrees_correction_ok())

    patches = [u for (m, u, _c) in client.appels if m == "PATCH"]
    assert len(patches) == 1 and patches[0].endswith("/rows/itemAt(index=2)")
    assert client.rows[0] == ["2026-06-01", "fonctionnement-reel", 500], "autre mois intact."
    assert client.rows[1] == ["2026-07-01", "autre-poste", 111], "autre poste intact."
    assert client.rows[2] == ["2026-07-01", "fonctionnement-reel", 2860.67], "seule la cible est corrigée."


def test_corriger_cout_structure_mois_serial_excel_reconnu(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(77) ACQUIS 0.20.1 RÉUTILISÉ : la source porte le mois en SÉRIAL Excel (46204 = 2026-07-01, la
    forme RÉELLE relue sur le tenant). La correction (a) RECONNAÎT la ligne, (b) la PATCHe, (c) passe
    sa post-vérification alors que la relecture rend, à nouveau, un sérial — aucun faux-rouge."""
    serial = _iso_vers_serial_excel("2026-07-01")
    assert serial == 46204, "sérial Excel de 2026-07-01 (époque 1899-12-30)."
    client = _FauxClientStructureSerialExcel(rows=[[46204, "fonctionnement-reel", 706.84]])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.corriger_cout_structure)

    res = fn(None, **_entrees_correction_ok())

    assert res["ancien_montant"] == 706.84 and res["nouveau_montant"] == 2860.67
    assert res["ligne_relue"] == {"Mois": 46204, "PosteCout": "fonctionnement-reel", "Montant": 2860.67}, \
        "la ligne relue (sérial) est reconnue comme celle du mois corrigé — pas de faux-rouge."
    assert client.rows == [[46204, "fonctionnement-reel", 2860.67]], "une seule ligne, au nouveau montant."


def test_corriger_cout_structure_honore_l_index_servi_par_graph(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(78) Quand Graph sert un champ `index` sur la ligne, c'est LUI qui adresse le PATCH (et non la
    position dans la réponse) — sinon on corrigerait la mauvaise ligne. À défaut d'`index`, la position
    fait foi (chemin exercé par tous les autres tests, dont le nominal)."""
    class _ClientIndexDecale(_FauxClientStructure):
        def get(self, url, headers=None, params=None):
            if url.endswith("/rows"):
                self.appels.append(("GET", url, params))
                # Graph annonce que cette unique ligne occupe l'index 7 de la table.
                return _RepWb(200, {"value": [{"index": 7, "values": [list(self.rows[0])]}]})
            return super().get(url, headers, params)

        def patch(self, url, headers=None, json=None):
            self.appels.append(("PATCH", url, json))
            for ligne in (json or {}).get("values", []):
                self.rows[0] = self._stocker(ligne)   # une seule ligne réelle, quel que soit l'index annoncé
            return _RepWb(self._patch_status, {})

    client = _ClientIndexDecale(rows=[_ligne_juillet()])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.corriger_cout_structure)

    fn(None, **_entrees_correction_ok())

    patches = [u for (m, u, _c) in client.appels if m == "PATCH"]
    assert len(patches) == 1 and patches[0].endswith("/rows/itemAt(index=7)"), \
        "l'index servi par Graph adresse le PATCH."


def test_corriger_cout_structure_cible_figee_classeur_et_table(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(79) CIBLE FIGÉE : tous les appels (GET comme PATCH) visent le classeur DRIVE-REF /
    ITEM-REFSTRUCT et la table T_Structure — l'appelant n'a fourni aucun drive/item/table/poste."""
    client = _FauxClientStructure(rows=[_ligne_juillet()])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.corriger_cout_structure)

    fn(None, **_entrees_correction_ok())

    attendu = "/drives/DRIVE-REF/items/ITEM-REFSTRUCT/workbook/tables/T_Structure"
    assert client.appels, "au moins un appel réseau."
    for (m, u, _c) in client.appels:
        assert attendu in u, f"appel {m} hors de la cible figée : {u}"


def test_corriger_cout_structure_ne_prend_aucune_cible_libre():
    """(80) Signature : corriger_cout_structure n'expose AUCUN drive_id / item_id / table / poste /
    index — cible figée par construction ; l'appelant ne fournit que mois / montant / proposition_id.
    L'index de la ligne est RÉSOLU côté serveur, jamais reçu (sinon on pourrait écraser n'importe quoi)."""
    params = _params(server.corriger_cout_structure)
    assert params == {"mois", "montant", "proposition_id"}
    for interdit in ("drive_id", "item_id", "table", "poste", "poste_cout", "classeur", "index", "ligne"):
        assert interdit not in params


def test_corriger_cout_structure_est_au_cran_valide():
    """(81) Le cran de corriger_cout_structure est VALIDÉ — jumeau d'inscrire_cout_structure : même
    donnée financière à audience restreinte, même porte humaine (table-des-crans v1.16)."""
    assert server.CRAN_PAR_OUTIL["corriger_cout_structure"] == "valide"
    assert server.CRAN_PAR_OUTIL["corriger_cout_structure"] == server.CRAN_PAR_OUTIL["inscrire_cout_structure"]


def test_inscrire_et_corriger_ont_des_preconditions_exclusives(
    _sans_porte, _ref_structure_factice, monkeypatch
):
    """(82) INVARIANT DE LA PAIRE : sur un même état de source, exactement UNE des deux primitives peut
    agir. Registre VIDE → inscrire passe, corriger refuse. Mois DÉJÀ inscrit → inscrire refuse, corriger
    passe. Aucun état où les deux écrivent : le doublon est impossible par construction."""
    inscrire = _sous_jacente(server.inscrire_cout_structure)
    corriger = _sous_jacente(server.corriger_cout_structure)

    # (a) registre VIDE : corriger REFUSE (rien à corriger), inscrire PASSE.
    vide = _FauxClientStructure(rows=[])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: vide)
    with pytest.raises(RuntimeError):
        corriger(None, **_entrees_correction_ok())
    assert vide.rows == [], "corriger n'a rien créé."
    inscrire(None, mois="2026-07-01", montant=706.84, proposition_id="ZP-2026-07")
    assert vide.rows == [["2026-07-01", "fonctionnement-reel", 706.84]]

    # (b) mois DÉJÀ inscrit (le registre ci-dessus) : inscrire REFUSE, corriger PASSE.
    with pytest.raises(RuntimeError):
        inscrire(None, mois="2026-07-01", montant=2860.67, proposition_id="ZP-bis")
    corriger(None, **_entrees_correction_ok())
    assert vide.rows == [["2026-07-01", "fonctionnement-reel", 2860.67]], \
        "une seule ligne du mois, au montant corrigé — jamais deux."

# --------------------------------------------------------------------------------------------
# _lever_erreur_graph — REMONTÉE DU CORPS D'ERREUR GRAPH (T-0045, serveur 0.22.0)
# Le manque le plus coûteux du 01/08/2026 : `raise_for_status()` AVALE le corps de la réponse. Un
# 404 ne disait pas s'il s'agissait d'un itemNotFound (classeur) ou d'un NOM DE TABLE inconnu ; un
# 403 ne disait pas s'il s'agissait d'une absence d'octroi Sites.Selected ou d'une limite d'API. Le
# corps portait la réponse, le code la jetait. Ces tests prouvent qu'il ne la jette plus.
# --------------------------------------------------------------------------------------------

class _RepCorps:
    """Réponse httpx factice à corps PILOTABLE : JSON exploitable, JSON sans enveloppe, ou brut.

    `json_data=_ILLISIBLE` fait lever `.json()` (corps non JSON, comme une page HTML d'erreur) ;
    `.text` porte alors le corps brut. `lu` note si `.json()` a été touché — sert à prouver qu'un
    statut de SUCCÈS ne lit JAMAIS le corps (aucun changement de comportement de succès).
    """

    _ILLISIBLE = object()

    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text
        self.headers = {}
        self.lu = False

    def json(self):
        self.lu = True
        if self._json is _RepCorps._ILLISIBLE:
            raise ValueError("corps non JSON (simulation)")
        return self._json if self._json is not None else {}


def _corps_graph(code, message):
    """Enveloppe d'erreur Graph canonique : {"error": {"code": ..., "message": ...}}."""
    return {"error": {"code": code, "message": message}}


def test_lever_erreur_graph_corps_json_remonte_code_et_message():
    """(83) Corps JSON Graph exploitable → `error.code` ET `error.message` remontés dans le message,
    avec le CONTEXTE d'appel, et posés en ATTRIBUTS lisibles programmatiquement. C'est exactement ce
    que `raise_for_status()` avalait le 01/08 : le 404 disait « nom de table inconnu », pas le code."""
    rep = _RepCorps(404, _corps_graph("ItemNotFound", "The resource could not be found."))
    with pytest.raises(server.ErreurGraph) as capture:
        server._lever_erreur_graph(rep, "lecture de la table « SAISIE_Realise_2026 »")

    exc = capture.value
    assert exc.statut == 404
    assert exc.code == "ItemNotFound"
    assert exc.message_graph == "The resource could not be found."
    assert exc.contexte == "lecture de la table « SAISIE_Realise_2026 »"
    texte = str(exc)
    assert "404" in texte
    assert "ItemNotFound" in texte, "le code Graph doit figurer dans le message (il était avalé)."
    assert "The resource could not be found." in texte
    assert "SAISIE_Realise_2026" in texte, "le contexte d'appel rend le statut interprétable."


def test_lever_erreur_graph_403_absence_d_octroi_est_lisible():
    """(83 bis) REJEU du second fait du 01/08 : le 403 venait d'une ABSENCE D'OCTROI (Sites.Selected),
    pas d'une limite de l'API Workbook. Avec le corps remonté, `accessDenied` est lisible d'emblée."""
    rep = _RepCorps(403, _corps_graph("accessDenied", "Access denied. Check credentials and try again."))
    with pytest.raises(server.ErreurGraph) as capture:
        server._lever_erreur_graph(rep, "lecture des lignes de la table de saisie")
    assert capture.value.code == "accessDenied"
    assert capture.value.statut == 403


def test_lever_erreur_graph_corps_non_json_rend_extrait_brut_borne():
    """(84) Corps NON JSON (page HTML d'erreur de passerelle, p. ex.) → les **200 premiers caractères**
    du corps BRUT, et pas davantage : un message d'erreur ne doit jamais devenir un dump."""
    brut = "<html><body>" + ("X" * 500) + "</body></html>"
    rep = _RepCorps(502, _RepCorps._ILLISIBLE, text=brut)
    with pytest.raises(server.ErreurGraph) as capture:
        server._lever_erreur_graph(rep, "création de la table")

    exc = capture.value
    assert exc.statut == 502
    assert exc.code == "" and exc.message_graph == ""
    assert exc.corps_brut == brut[:200]
    assert len(exc.corps_brut) == 200, "l'extrait brut est BORNÉ à 200 caractères."
    assert brut[:50] in str(exc)
    assert "X" * 300 not in str(exc), "le corps complet ne doit jamais partir dans le message."


def test_lever_erreur_graph_corps_json_sans_enveloppe_error_retombe_sur_le_brut():
    """(85) JSON valide mais SANS enveloppe `{"error": …}` (cas non canonique) → repli sur l'extrait
    brut : on ne prétend jamais avoir un code Graph qu'on n'a pas lu."""
    rep = _RepCorps(500, {"quelquechose": "d'autre"}, text='{"quelquechose": "d\'autre"}')
    with pytest.raises(server.ErreurGraph) as capture:
        server._lever_erreur_graph(rep, "append de lignes")
    assert capture.value.code == ""
    assert "quelquechose" in capture.value.corps_brut


def test_lever_erreur_graph_succes_ne_leve_rien_et_ne_lit_pas_le_corps():
    """(86) NON-RÉGRESSION centrale : un statut de SUCCÈS ne lève rien **et ne touche pas au corps**.
    Le comportement de succès des primitives est INCHANGÉ — l'ajout est strictement additif."""
    for statut in (200, 201, 202, 204, 302, 399):
        rep = _RepCorps(statut, _corps_graph("neJamaisLire", "ne jamais lire"))
        assert server._lever_erreur_graph(rep, "peu importe") is None
        assert rep.lu is False, f"le corps ne doit pas être lu sur un succès (statut {statut})."


def test_erreur_graph_est_un_sous_type_de_httpstatuserror():
    """(87) COMPATIBILITÉ : `ErreurGraph` est un sous-type de `httpx.HTTPStatusError`. Tout
    consommateur (ou docstring) qui interceptait déjà `HTTPStatusError` continue de fonctionner — la
    remontée du corps n'introduit AUCUNE classe d'erreur nouvelle à attraper."""
    assert issubclass(server.ErreurGraph, server.httpx.HTTPStatusError)
    rep = _RepCorps(429, _corps_graph("activityLimitReached", "throttled"))
    with pytest.raises(server.httpx.HTTPStatusError):
        server._lever_erreur_graph(rep, "contexte")


# Fonctions PORTANT les appels Workbook (repérées dans server.py, pas devinées) : primitives exposées
# ET helpers qu'elles appellent. Aucune ne doit plus masquer une réponse Graph derrière raise_for_status.
_FONCTIONS_WORKBOOK = (
    "_resoudre_item_gabarit",
    "_resoudre_item_saisie",
    "_entetes_physiques_t_structure",
    "_lire_lignes_t_structure_indexees",
    "inscrire_cout_structure",
    "corriger_cout_structure",
    "workbook_lire_table",
    "lire_saisie_table",
    "workbook_ajouter_lignes",
    "workbook_maj_ligne",
    "workbook_archiver_gabarit",
    "workbook_instancier_gabarit",
)


def _fonctions_avec_raise_for_status() -> set:
    """Noms des fonctions de server.py contenant encore un `.raise_for_status()` (analyse AST)."""
    import ast
    source = open(inspect.getsourcefile(server), encoding="utf-8").read()
    trouvees = set()
    for noeud in ast.parse(source).body:
        if not isinstance(noeud, ast.FunctionDef):
            continue
        for interne in ast.walk(noeud):
            if isinstance(interne, ast.Attribute) and interne.attr == "raise_for_status":
                trouvees.add(noeud.name)
    return trouvees


def test_primitives_workbook_ne_masquent_plus_le_corps_graph():
    """(88) GARDE ANTI-RÉGRESSION : plus AUCUNE fonction Workbook n'appelle `raise_for_status()` —
    toutes passent par `_lever_erreur_graph`. Si quelqu'un rajoute un appel Graph masqué dans une
    primitive Workbook, la CI casse ici (et non à la prochaine épreuve tenant, comme le 01/08)."""
    masquantes = _fonctions_avec_raise_for_status() & set(_FONCTIONS_WORKBOOK)
    assert not masquantes, (
        f"ces fonctions Workbook avalent encore le corps d'erreur Graph : {sorted(masquantes)} — "
        "utiliser _lever_erreur_graph(reponse, contexte)."
    )


def test_lever_erreur_graph_est_bien_appele_par_les_primitives_workbook():
    """(88 bis) CONTRE-PREUVE de (88) : l'absence de `raise_for_status` ne suffirait pas (on aurait pu
    simplement SUPPRIMER la garde). Chaque fonction Workbook appelle bien `_lever_erreur_graph`."""
    import ast
    source = open(inspect.getsourcefile(server), encoding="utf-8").read()
    appelants = set()
    for noeud in ast.parse(source).body:
        if not isinstance(noeud, ast.FunctionDef):
            continue
        for interne in ast.walk(noeud):
            if isinstance(interne, ast.Call) and isinstance(interne.func, ast.Name) \
                    and interne.func.id == "_lever_erreur_graph":
                appelants.add(noeud.name)
    # `_metadonnees_item` est volontairement HORS liste : best effort, il ne lève jamais (cf. (105)).
    attendues = set(_FONCTIONS_WORKBOOK)
    assert attendues <= appelants, (
        f"garde absente (ni raise_for_status, ni _lever_erreur_graph) dans : {sorted(attendues - appelants)}"
    )


# --------------------------------------------------------------------------------------------
# Couche de SAISIE (T-0045, serveur 0.22.0) — lecture BORNÉE, aucune écriture par construction.
# Projection machine de modele-donnees.md §5.6 v1.28 (faits MESURÉS le 01/08/2026 sur
# `saisie-1-siteflow.xlsx`) : TROIS tables nommées, grille de 14 colonnes lue PAR POSITION, classeur
# résolu par la convention de nommage `^saisie-(\d+)-`. La primitive LIT ; elle n'interprète RIEN.
# --------------------------------------------------------------------------------------------

# --- ANTI-DIVERGENCE de projection (même discipline que §5.2 / §5.3) : ces littéraux RECOPIENT §5.6.
_TABLES_CONTRAT_56_MILLESIMEES = ("SAISIE_Prevu", "SAISIE_Realise")
_TABLE_CONTRAT_56_FACTURATION = "SAISIE_Facturation"


def test_tables_saisie_projettent_exactement_modele_donnees_56():
    """(89) ANTI-DIVERGENCE : la projection serveur des tables de saisie == §5.6 v1.28. Casse la CI si
    elle re-diverge du contrat (même classe de bug que l'écart 3g sur T_Echeancier)."""
    assert server.PREFIXES_TABLES_SAISIE_MILLESIMEES == _TABLES_CONTRAT_56_MILLESIMEES
    assert server.TABLE_SAISIE_FACTURATION == _TABLE_CONTRAT_56_FACTURATION


@pytest.mark.parametrize("nom", [
    "SAISIE_Prevu_2026",
    "SAISIE_Realise_2026",
    "SAISIE_Facturation",
    "SAISIE_Prevu_2027",       # le millésime est porté par le NOM : une année nouvelle = table nouvelle.
    "  SAISIE_Realise_2025  ",  # strippé
])
def test_valider_table_saisie_accepte_les_trois_tables_contractuelles(nom):
    """(90) Les TROIS tables de §5.6 sont acceptées (millésime variable pour les deux grilles)."""
    assert server._valider_table_saisie(nom) == nom.strip()


def test_valider_table_saisie_refuse_t_imputations_en_nommant_la_cause():
    """(91) REJEU EN RÉGRESSION DU FAIT DU 01/08/2026 : `T_Imputations` demandée sur une SAISIE est
    refusée, et le message NOMME la cause — T_Imputations est la table du GABARIT (§5.2), pas de la
    saisie. C'est l'origine du 404 opaque de l'épreuve ; il ne peut plus se reproduire en silence."""
    with pytest.raises(ValueError) as capture:
        server._valider_table_saisie("T_Imputations")
    message = str(capture.value)
    assert "T_Imputations" in message
    assert "GABARIT" in message, "le message doit dire que c'est la table du GABARIT."
    assert "saisie" in message.lower(), "et qu'elle n'est PAS de la saisie."
    assert "§5.2" in message and "§5.6" in message, "les deux sections doivent être citées."


@pytest.mark.parametrize("gabarit", ["T_Imputations", "T_Affectations", "T_Echeancier"])
def test_valider_table_saisie_refuse_toutes_les_tables_du_gabarit(gabarit):
    """(91 bis) Les TROIS tables du gabarit §5.2 sont refusées sur la saisie, pas seulement celle qui
    a mordu le 01/08 — la confusion de modèle est fermée en entier."""
    with pytest.raises(ValueError):
        server._valider_table_saisie(gabarit)


@pytest.mark.parametrize("mauvais", [
    "", "   ", None, 42,
    "SAISIE_Prevu",             # millésime manquant
    "SAISIE_Realise_26",        # millésime pas sur 4 chiffres
    "SAISIE_Facturation_2026",  # la facturation n'est PAS millésimée
    "saisie_prevu_2026",        # la casse du nom de TABLE n'est pas libre (seul le nom de FICHIER l'est)
    "Feuil1", "SAISIE_Autre_2026", "'; DROP TABLE",
])
def test_valider_table_saisie_refuse_tout_nom_hors_liste(mauvais):
    """(92) Aucun nom de table LIBRE : hors des trois tables contractuelles → ValueError."""
    with pytest.raises(ValueError):
        server._valider_table_saisie(mauvais)


@pytest.mark.parametrize("hors_bornes", ["SAISIE_Prevu_1999", "SAISIE_Realise_2101", "SAISIE_Prevu_0000"])
def test_valider_table_saisie_refuse_un_millesime_hors_bornes(hors_bornes):
    """(93) Millésime borné [2020..2100] — mêmes bornes que l'année d'un nom d'espace de mission."""
    with pytest.raises(ValueError):
        server._valider_table_saisie(hors_bornes)


# Grille RÉELLE telle que MESURÉE le 01/08/2026 (schéma §5.6 : 14 colonnes
# [Ressource, Janvier … Décembre (12 positions), TOTAL]) — reproduite AVEC ses vides.
_GRILLE_REALISE_14 = [
    # (a) ligne d'ENTÊTE TECHNIQUE « Nb. jours ouvres max » : un plafond de calendrier, PAS une
    #     ressource. §5.6 l'écarte à la DÉRIVATION — jamais à la LECTURE.
    ["Nb. jours ouvres max", 22, 20, 22, 21, 20, 22, 23, 21, 22, 22, 20, 22, 257],
    # (b) une ressource : JUILLET en position 7 (22 j) et AOÛT en position 8 (10 j) — les dix autres
    #     mois sont des cellules VIDES, jamais des colonnes absentes. C'est CE fait qui explique
    #     l'écart de 22 j de l'épreuve 3g : les jours manquants étaient juillet, à sa POSITION.
    ["adrien.raque@allia-consulting.com", "", "", "", "", "", "", 22, 10, "", "", "", "", 32],
    # (c) LIGNE FANTÔME de la zone de saisie pré-dimensionnée : TOTAL = 0. §5.6 l'écarte à la
    #     DÉRIVATION (même famille que le prédicat « vierge » de T-0035) — jamais à la LECTURE.
    ["", "", "", "", "", "", "", "", "", "", "", "", "", 0],
]


class _FauxClientSaisie:
    """Client httpx factice pour `lire_saisie_table` (drive de SAISIE, LECTURE SEULE).

    Routes :
      - GET  .../items/{folder}/children            → enfants du dossier de saisie figé (`enfants`) ;
      - GET  .../workbook/tables/{table}/rows       → lignes de la grille (statut `rows_status`) ;
      - GET  .../drives/{d}/items/{i}?$select=…     → métadonnées eTag/cTag (statut `meta_status`).
    POST et PATCH sont des ÉCHECS DE TEST : il n'existe AUCUN chemin d'écriture vers le drive de
    saisie — c'est le pendant serveur de l'invariant §5.6, et le mock le prouve structurellement.
    """

    def __init__(self, enfants=None, rows=None, rows_status=200, rows_corps=None,
                 meta_status=200, pages=None):
        self._enfants = enfants if enfants is not None else [
            {"id": "ITEM-SAISIE-1", "name": "saisie-1-siteflow.xlsx"},
        ]
        self._rows = _GRILLE_REALISE_14 if rows is None else rows
        self._rows_status = rows_status
        self._rows_corps = rows_corps
        self._meta_status = meta_status
        self._pages = pages or []   # pages SUPPLÉMENTAIRES de children (@odata.nextLink)
        self.appels = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get(self, url, headers=None, params=None):
        self.appels.append(("GET", url, params))
        if url.endswith("/children") or url.startswith("nextlink://"):
            if url.startswith("nextlink://"):
                page = self._pages[int(url.rsplit("/", 1)[-1])]
                return _RepCorps(200, page)
            corps = {"value": list(self._enfants)}
            if self._pages:
                corps["@odata.nextLink"] = "nextlink://page/0"
            return _RepCorps(200, corps)
        if url.endswith("/rows"):
            if self._rows_status != 200:
                return _RepCorps(self._rows_status, self._rows_corps, text="")
            return _RepCorps(200, {"value": [{"values": [list(r)]} for r in self._rows]})
        # métadonnées de l'item (eTag / cTag)
        if self._meta_status != 200:
            return _RepCorps(self._meta_status, _corps_graph("accessDenied", "no"))
        return _RepCorps(200, {
            "id": "ITEM-SAISIE-1",
            "name": "saisie-1-siteflow.xlsx",
            "eTag": '"{ETAG-SAISIE-1},7"',
            "cTag": '"c:{CTAG-SAISIE-1},2"',
            "lastModifiedDateTime": "2026-08-01T09:12:33Z",
        })

    def post(self, url, headers=None, json=None, content=None, params=None):
        raise AssertionError(
            "AUCUNE écriture ne doit exister sur le drive de SAISIE (POST tenté sur %s) — "
            "l'invariant §5.6 « la machine n'écrit jamais la saisie » est structurel." % url
        )

    def patch(self, url, headers=None, json=None):
        raise AssertionError(
            "AUCUNE écriture ne doit exister sur le drive de SAISIE (PATCH tenté sur %s)." % url
        )

    def put(self, url, headers=None, json=None, content=None, params=None):
        raise AssertionError(
            "AUCUNE écriture ne doit exister sur le drive de SAISIE (PUT tenté sur %s)." % url
        )

    def delete(self, url, headers=None):
        raise AssertionError("AUCUNE suppression ne doit exister sur le drive de SAISIE.")


@pytest.fixture
def _saisie_factice(monkeypatch):
    """Config « couche de saisie » valide + jeton neutralisé. Aucun secret, aucune env réelle."""
    monkeypatch.setattr(
        server, "_config_saisie",
        lambda: {"drive_id": "DRIVE-SAISIE", "folder_id": "FOLDER-SAISIE"},
    )
    monkeypatch.setattr(server, "_entetes", lambda: {"Authorization": "Bearer faketoken"})


def test_lire_saisie_table_ne_prend_aucune_cible_libre():
    """(94) SIGNATURE : `lire_saisie_table` n'expose AUCUN drive_id / item_id / chemin / dossier — la
    cible est BORNÉE au drive de saisie figé côté serveur. L'appelant ne fournit que code_mission et
    table. C'est le CONTRASTE voulu avec `workbook_lire_table` (lecture non bornée, cible libre)."""
    params = _params(server.lire_saisie_table)
    assert params == {"code_mission", "table"}
    for interdit in ("drive_id", "item_id", "folder_id", "drive", "item", "chemin", "path", "url"):
        assert interdit not in params, f"{interdit} ne doit jamais être exposé (cible bornée)."


def test_lire_saisie_table_est_au_cran_auto():
    """(95) Cran AUTO : lecture seule, réversible, interne — comme les autres lectures. Le journal
    d'observabilité doit le porter (un outil hors CRAN_PAR_OUTIL journaliserait « inconnu »)."""
    assert server.CRAN_PAR_OUTIL["lire_saisie_table"] == "auto"
    assert server.CRAN_PAR_OUTIL["lire_saisie_table"] == server.CRAN_PAR_OUTIL["workbook_lire_table"]


def test_lire_saisie_table_nominal_rend_les_positions_et_PRESERVE_les_vides(
    _sans_porte, _saisie_factice, monkeypatch
):
    """(96) NOMINAL — LA FIDÉLITÉ MÊME. La grille des 14 colonnes est rendue TELLE QUELLE :
       - les cellules VIDES SORTENT vides, à leur POSITION (l'index porte le mois, §5.6) ;
       - la ligne d'entête technique « Nb. jours ouvres max » est TOUJOURS LÀ ;
       - la ligne FANTÔME (TOTAL = 0) est TOUJOURS LÀ.
    La primitive ne DÉRIVE RIEN : pas de filtrage, pas de somme, pas de mapping mois — la règle de
    dérivation §5.6 appartient au consommateur. Lire ≠ interpréter."""
    client = _FauxClientSaisie()
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.lire_saisie_table)

    resultat = fn(None, code_mission="1", table="SAISIE_Realise_2026")

    # (a) IDENTITÉ STRICTE avec ce que Graph a servi — aucune transformation.
    assert resultat["lignes"] == _GRILLE_REALISE_14
    assert resultat["count"] == 3, "les 3 lignes servies sortent : aucune n'est filtrée à la LECTURE."
    # (b) 14 colonnes par ligne : [Ressource, 12 mois, TOTAL].
    for ligne in resultat["lignes"]:
        assert len(ligne) == 14, "schéma §5.6 : 1 + 12 + 1 colonnes, jamais compacté."
    # (c) les VIDES sont préservés à leur position, et JUILLET est bien en position 7.
    ressource = resultat["lignes"][1]
    assert ressource[7] == 22, "juillet = position 7 (l'index de colonne porte le mois)."
    assert ressource[8] == 10, "août = position 8."
    assert ressource[1] == "" and ressource[12] == "", "un mois sans imputation reste une cellule VIDE."
    assert ressource[13] == 32, "la colonne TOTAL est la 14e."
    # (d) les lignes que la DÉRIVATION écartera sont présentes ICI (elle, pas nous).
    assert resultat["lignes"][0][0] == "Nb. jours ouvres max"
    assert resultat["lignes"][2][13] == 0, "la ligne fantôme (TOTAL=0) n'est pas filtrée à la lecture."
    # (e) traçabilité de la cible résolue côté serveur.
    assert resultat["code_mission"] == "1"
    assert resultat["nom_classeur"] == "saisie-1-siteflow.xlsx"
    assert resultat["item_id"] == "ITEM-SAISIE-1"
    assert resultat["table"] == "SAISIE_Realise_2026"
    # (f) AUCUNE écriture : le mock lèverait sur POST/PATCH/PUT/DELETE ; seuls des GET ont eu lieu.
    assert all(methode == "GET" for (methode, _u, _p) in client.appels), (
        "lire_saisie_table ne doit émettre que des GET — aucune écriture sur la saisie."
    )


def test_lire_saisie_table_expose_les_etag_de_l_item(_sans_porte, _saisie_factice, monkeypatch):
    """(97) ETag/cTag EXPOSÉS (0.22.0) : plus besoin d'une sonde REST navigateur à côté du connecteur
    pour savoir si le classeur a bougé. Additif : rien n'est retiré du retour."""
    client = _FauxClientSaisie()
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.lire_saisie_table)

    resultat = fn(None, code_mission="1", table="SAISIE_Prevu_2026")

    meta = resultat["metadonnees_item"]
    assert meta["eTag"] == '"{ETAG-SAISIE-1},7"'
    assert meta["cTag"] == '"c:{CTAG-SAISIE-1},2"'
    assert meta["name"] == "saisie-1-siteflow.xlsx"
    assert meta["lastModifiedDateTime"] == "2026-08-01T09:12:33Z"


def test_lire_saisie_table_metadonnees_illisibles_ne_cassent_pas_la_lecture(
    _sans_porte, _saisie_factice, monkeypatch
):
    """(98) Les métadonnées sont ACCESSOIRES : un 403 sur elles ne doit PAS faire échouer une lecture
    de lignes RÉUSSIE (ce serait une régression pour les consommateurs). Elles sortent vides."""
    client = _FauxClientSaisie(meta_status=403)
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.lire_saisie_table)

    resultat = fn(None, code_mission="1", table="SAISIE_Realise_2026")

    assert resultat["lignes"] == _GRILLE_REALISE_14, "le CONTENU fait foi (§5.6) — il est rendu."
    assert resultat["metadonnees_item"] == {
        "eTag": "", "cTag": "", "name": "", "lastModifiedDateTime": "",
    }


def test_lire_saisie_table_refuse_t_imputations_AVANT_reseau(_sans_porte, monkeypatch):
    """(99) RÉGRESSION DU 01/08, BOUT EN BOUT : `T_Imputations` demandée à `lire_saisie_table` est
    refusée AVANT toute ouverture de client httpx — le refus nomme la cause, et Graph n'est même pas
    sollicité (plus de 404 opaque à diagnostiquer après coup)."""
    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré un nom de table hors §5.6.")

    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.lire_saisie_table)
    with pytest.raises(ValueError) as capture:
        fn(None, code_mission="1", table="T_Imputations")
    assert "GABARIT" in str(capture.value)


def test_lire_saisie_table_config_absente_leve_configmanquante(_sans_porte, monkeypatch):
    """(100) `GRAPH_SAISIE_DRIVE_ID` / `GRAPH_SAISIE_FOLDER_ID` absentes → `ConfigManquante`, AVANT
    tout réseau (fail-closed, aucun fallback, aucune cible par défaut). Fait mesuré le 01/08 :
    GRAPH_SAISIE_DRIVE_ID est ABSENTE du conteneur déployé — la pose est un geste runbook gardien."""
    monkeypatch.delenv("GRAPH_SAISIE_DRIVE_ID", raising=False)
    monkeypatch.delenv("GRAPH_SAISIE_FOLDER_ID", raising=False)

    class _ClientInterdit:
        def __init__(self, *a, **k):
            raise AssertionError("client httpx instancié malgré une config « saisie » absente.")

    monkeypatch.setattr(server.httpx, "Client", _ClientInterdit)
    fn = _sous_jacente(server.lire_saisie_table)
    with pytest.raises(server.ConfigManquante):
        fn(None, code_mission="1", table="SAISIE_Realise_2026")


@pytest.mark.parametrize("mauvais_code", ["", "   ", "a/b", "..", "1\x01", "M-2026-1", "1.0", "abc"])
def test_lire_saisie_table_code_mission_invalide_refuse(_sans_porte, _saisie_factice, mauvais_code, monkeypatch):
    """(101) `code_mission` vide / non numérique / portant un motif d'évasion → ValueError. §5.6 exige
    des CHIFFRES (`^saisie-(\\d+)-`) ; ce n'est jamais un chemin."""
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: _FauxClientSaisie())
    fn = _sous_jacente(server.lire_saisie_table)
    with pytest.raises(ValueError):
        fn(None, code_mission=mauvais_code, table="SAISIE_Realise_2026")


def test_lire_saisie_table_resout_par_convention_de_nommage_libelle_libre(
    _sans_porte, _saisie_factice, monkeypatch
):
    """(102) RÉSOLUTION PAR NOMMAGE §5.6 : le libellé après le code est LIBRE et la casse est LIBRE —
    le nom de fichier n'est donc PAS déductible du code. On liste le dossier figé et on apparie sur
    `^saisie-(\\d+)-`. Les SOUS-DOSSIERS et les codes voisins (11, 1bis) ne matchent pas."""
    client = _FauxClientSaisie(enfants=[
        {"id": "F1", "name": "00 - Template Mission"},          # sous-dossier — écarté par le motif
        {"id": "F2", "name": "01 - Missions cloturees"},         # sous-dossier — écarté
        {"id": "X1", "name": "saisie-11-datalab.xlsx"},           # code VOISIN (11 ≠ 1) — écarté
        {"id": "X2", "name": "saisie-1bis-vieux.xlsx"},           # pas `\\d+-` après le code — écarté
        {"id": "X3", "name": "Saisie-1-SiteFlow ARABELLE.xlsx"},  # LA cible : casse et libellé libres
        {"id": "X4", "name": "saisie-1-notes.docx"},              # pas un .xlsx — écarté
    ])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.lire_saisie_table)

    resultat = fn(None, code_mission="1", table="SAISIE_Facturation")

    assert resultat["item_id"] == "X3"
    assert resultat["nom_classeur"] == "Saisie-1-SiteFlow ARABELLE.xlsx"


def test_lire_saisie_table_aucun_classeur_leve_filenotfound_sans_lire_de_table(
    _sans_porte, _saisie_factice, monkeypatch
):
    """(103) Aucun classeur pour ce code → `FileNotFoundError`, et AUCUNE lecture de table n'est
    tentée : on ne lit rien qui n'existe pas."""
    client = _FauxClientSaisie(enfants=[{"id": "X", "name": "saisie-9-autre.xlsx"}])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.lire_saisie_table)

    with pytest.raises(FileNotFoundError):
        fn(None, code_mission="1", table="SAISIE_Realise_2026")
    assert not any(u.endswith("/rows") for (_m, u, _p) in client.appels), (
        "aucune table ne doit être lue si le classeur de la mission n'existe pas."
    )


def test_lire_saisie_table_deux_classeurs_pour_un_code_refuse(_sans_porte, _saisie_factice, monkeypatch):
    """(104) AMBIGUÏTÉ = REFUS : deux classeurs portant le même code → `RuntimeError`. On ne devine
    jamais laquelle des deux sources est la bonne (même discipline que l'unicité exigée par
    `corriger_cout_structure`) — anomalie signalée, réconciliation gardien."""
    client = _FauxClientSaisie(enfants=[
        {"id": "A", "name": "saisie-1-siteflow.xlsx"},
        {"id": "B", "name": "saisie-1-siteflow-copie.xlsx"},
    ])
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.lire_saisie_table)

    with pytest.raises(RuntimeError) as capture:
        fn(None, code_mission="1", table="SAISIE_Realise_2026")
    assert "2 classeurs" in str(capture.value)
    assert not any(u.endswith("/rows") for (_m, u, _p) in client.appels)


def test_lire_saisie_table_suit_la_pagination_du_dossier(_sans_porte, _saisie_factice, monkeypatch):
    """(105) Le dossier de saisie peut être paginé (`@odata.nextLink`) : le classeur cible doit être
    trouvé même s'il n'est pas sur la 1re page — sinon une mission « disparaîtrait » silencieusement."""
    client = _FauxClientSaisie(
        enfants=[{"id": "Z", "name": "saisie-7-autre.xlsx"}],
        pages=[{"value": [{"id": "ITEM-SAISIE-1", "name": "saisie-1-siteflow.xlsx"}]}],
    )
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.lire_saisie_table)

    resultat = fn(None, code_mission="1", table="SAISIE_Realise_2026")
    assert resultat["item_id"] == "ITEM-SAISIE-1"


def test_lire_saisie_table_remonte_le_corps_d_erreur_graph(_sans_porte, _saisie_factice, monkeypatch):
    """(106) BOUT EN BOUT : un échec Graph sur la lecture de la table remonte le `code` et le
    `message` du CORPS — plus jamais un statut nu. C'est précisément ce qui manquait le 01/08."""
    client = _FauxClientSaisie(
        rows_status=404,
        rows_corps=_corps_graph("ItemNotFound", "Table 'SAISIE_Realise_2026' not found."),
    )
    monkeypatch.setattr(server.httpx, "Client", lambda *a, **k: client)
    fn = _sous_jacente(server.lire_saisie_table)

    with pytest.raises(server.ErreurGraph) as capture:
        fn(None, code_mission="1", table="SAISIE_Realise_2026")
    exc = capture.value
    assert exc.statut == 404 and exc.code == "ItemNotFound"
    assert "SAISIE_Realise_2026" in str(exc) and "saisie-1-siteflow.xlsx" in str(exc), (
        "le contexte doit nommer la table ET le classeur visés."
    )


def test_lire_saisie_table_aucun_chemin_d_ecriture_vers_le_drive_de_saisie():
    """(107) INVARIANT STRUCTUREL §5.6 : `GRAPH_SAISIE_DRIVE_ID` n'est lu que par `_config_saisie`, et
    aucune fonction d'ÉCRITURE ne consomme cette config. Le seul consommateur est la LECTURE."""
    import ast
    source = open(inspect.getsourcefile(server), encoding="utf-8").read()
    consommateurs = set()
    for noeud in ast.parse(source).body:
        if not isinstance(noeud, ast.FunctionDef):
            continue
        for interne in ast.walk(noeud):
            if isinstance(interne, ast.Call) and isinstance(interne.func, ast.Name) \
                    and interne.func.id == "_config_saisie":
                consommateurs.add(noeud.name)
    assert consommateurs == {"lire_saisie_table", "_resoudre_item_saisie"}, (
        f"la config de saisie ne doit être consommée que par la LECTURE — trouvé {sorted(consommateurs)}."
    )


def test_workbook_lire_table_retour_reste_additif():
    """(108) NON-RÉGRESSION de `workbook_lire_table` : sa signature est INCHANGÉE (lecture non bornée,
    drive_id + item_id) et son retour ne perd rien — `metadonnees_item` s'AJOUTE à table/lignes/count."""
    params = _params(server.workbook_lire_table)
    assert {"drive_id", "item_id", "table"} == params, "signature publique inchangée."
    source = inspect.getsource(_sous_jacente(server.workbook_lire_table))
    for cle in ('"table"', '"lignes"', '"count"', '"metadonnees_item"'):
        assert cle in source, f"la clé {cle} doit figurer au retour (ajout strictement additif)."


def test_compte_des_outils_decores_est_dix_neuf():
    """(109) Le compte annoncé par la docstring du module est VÉRIFIÉ, plus seulement déclaré : 19
    outils décorés en 0.22.0 (18 en 0.21.0 + `lire_saisie_table`). Le chapeau disait « DIX-SEPT »
    alors que 18 étaient exposés — un compte déclaré à la main se périme ; celui-ci casse la CI."""
    import ast
    source = open(inspect.getsourcefile(server), encoding="utf-8").read()
    arbre = ast.parse(source)
    outils = []
    for noeud in arbre.body:
        if not isinstance(noeud, ast.FunctionDef):
            continue
        for deco in noeud.decorator_list:
            cible = deco.func if isinstance(deco, ast.Call) else deco
            if isinstance(cible, ast.Attribute) and cible.attr == "tool":
                outils.append(noeud.name)
    assert len(outils) == 19, f"19 outils attendus, {len(outils)} décorés : {outils}"
    assert "lire_saisie_table" in outils
    assert "DIX-NEUF opérations" in (ast.get_docstring(arbre) or ""), (
        "le chapeau du module doit annoncer le compte réel."
    )
