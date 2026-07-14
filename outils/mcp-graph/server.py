"""Serveur MCP — connecteur Microsoft Graph (lecture liste + écriture zone de proposition).

Allia · couture M365 (voir `contrats/socle/modele-donnees.md`). Chantier `backlog/chantiers/T-0002b.yaml`
(sous-tâche `T-0002b-1` : transport stdio → HTTP streamable + identité managée).

Ce serveur expose QUATORZE opérations à un agent, via le Model Context Protocol (transport HTTP streamable) :

    - list_items                  : LIT les éléments d'une liste SharePoint (lecture seule).
    - create_list_item            : CRÉE un élément UNIQUEMENT dans la « Zone-de-proposition ».
    - televerser_brouillon_offre  : DÉPOSE un brouillon .docx UNIQUEMENT dans « 00 - Proposition en cours ».
    - reconcilier_groupe_perimetre : RÉCONCILIE l'appartenance d'un groupe de périmètre (delta idempotent), cible bornée par liste blanche.
    - reconcilier_groupe_parc      : RÉCONCILIE l'appartenance du groupe de PARC d'enrôlement (delta idempotent), cible bornée par liste blanche DÉDIÉE.
    - lire_annuaire               : LIT l'annuaire Entra (lecture seule) — résout un UPN en objectId et/ou liste les membres d'un groupe borné aux listes blanches.
    - creer_espace_mission        : CRÉE l'espace de mission (arbre de dossiers FIGÉ) UNIQUEMENT sous la racine « Missions ».
    - deposer_document_mission    : DÉPOSE un brouillon interne UNIQUEMENT dans un sous-dossier FIGÉ d'un espace de mission.
    - notifier_canal              : DÉPOSE une notification UNIQUEMENT dans la liste « Notifications » (relais vers Teams par flux M365).
    - workbook_lire_table         : LIT (lecture seule, NON bornée) les lignes d'une table nommée d'un classeur Excel (saisie / gabarit / réf. coûts).
    - workbook_ajouter_lignes     : AJOUTE des lignes à une table du GABARIT d'une mission — cible FIGÉE « 06 - Gabarit ERP » (écriture bornée par construction).
    - workbook_maj_ligne          : MET À JOUR une ligne par POSITION dans une table du GABARIT — cible FIGÉE « 06 - Gabarit ERP » (écriture bornée par construction).
    - workbook_archiver_gabarit   : ARCHIVE le gabarit courant d'une mission dans « 00 - Old » (copie horodatée) avant régénération.
    - workbook_instancier_gabarit : INSTANCIE le gabarit d'une mission par COPIE de la souche vierge canon — cible FIGÉE « 06 - Gabarit ERP », fail-closed (jamais d'écrasement).

(Compte des opérations = 14 outils réellement décorés ; un `grep` du décorateur d'outil retourne 15,
car il compte aussi la mention littérale dans la docstring de `_journal_appel`, qui n'est pas un outil.)

Transport & santé :

    * Transport MCP : HTTP STREAMABLE (endpoint `/mcp`, sous-chemin par défaut du SDK), serveur
      instancié STATELESS (`stateless_http=True`) — exigence Azure Container Apps (pas de session
      persistante côté serveur). Lancement : `mcp.run(transport="streamable-http")`.
    * Endpoint de santé SÉPARÉ `/healthz` : `GET` → `200 {"status": "ok"}`, liveness PUR (ne touche
      pas Graph, n'acquiert aucun jeton). Une sonde ne vise JAMAIS `/mcp` (qui attend du JSON-RPC POST).

Garde-fous inscrits dans le code (pas seulement en prose) :

    * « Le dérivé n'est jamais le saisi » (doctrine §2, modele-donnees.md §3) : l'écriture
      ne peut JAMAIS viser une source. La liste d'écriture est fixée côté serveur par la
      variable d'environnement GRAPH_PROPOSITION_LIST_ID ; `create_list_item` n'accepte
      AUCUN identifiant de liste de l'appelant. Il est donc structurellement impossible
      d'écrire ailleurs que dans la zone de proposition.
    * SORTIE Graph = ZÉRO SECRET. L'authentification vers Microsoft Graph passe par une
      IDENTITÉ MANAGÉE (managed identity), pas par un secret applicatif :
        - en PROD : ManagedIdentityCredential(client_id=...) — identité user-assigned, type
          SPÉCIFIQUE (et non DefaultAzureCredential nu) pour empêcher la chaîne de fallback de
          ramasser silencieusement une autre identité (moindre privilège strict) ;
        - en LOCAL : DefaultAzureCredential() — découvre `az login` / VS Code (l'identité
          managée n'existe pas hors d'Azure).
      Sélection pilotée par la variable AZURE_ENV (`local` | `prod` ; défaut sûr : `prod`).
      Aucun secret Graph n'est lu, stocké ni injecté. (La frontière d'ENTRÉE du service — qui a
      le droit d'appeler `/mcp` — est une AUTRE frontière, l'auth Easy Auth de l'hébergement,
      portée par `T-0002b-4`, HORS de ce code.)
    * Moindre privilège : le jeton est acquis sur le scope `https://graph.microsoft.com/.default`
      et aucun autre. Les droits effectifs sont déjà bornés en amont par l'octroi `Sites.Selected`
      + `write` sur le SEUL site AlliaConsuling (runbook du gardien `T-0002a-bis`, fait) — NON ici.

Ce fichier « dort » : il ne se connecte à rien tant que les variables d'environnement ne sont
pas renseignées et qu'un client MCP ne le lance pas. L'import et l'inspection ne déclenchent
aucun appel réseau (le credential et la configuration ne sont lus qu'au moment d'un appel d'outil).
"""

from __future__ import annotations

import base64
import functools
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from mcp.server.fastmcp import Context, FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"  # scope unique (moindre privilège)

# clientId PUBLIC de l'identité managée user-assigned « id-allia-mcp-graph » (créée le 9 juin 2026).
# Un clientId est un identifiant PUBLIC, PAS un secret. Sert de défaut si AZURE_CLIENT_ID est absente.
# (clientId, PAS le principalId.)
MANAGED_IDENTITY_CLIENT_ID = "f2a3c40a-a447-4295-90da-76d6b0898d61"

# Logger de traçabilité des appels entrants (identité appelante Easy Auth).
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")

# --- Journal structuré d'observabilité (T-0020-b) -------------------------------------------
# UNE ligne JSON par appel d'outil, émise sur stdout → journaux de la Container App
# (Log Analytics, table ContainerAppConsoleLogs) — consultable en KQL. AUCUNE donnée
# personnelle en clair : ni argument, ni identité, ni contenu — seulement le fait de l'appel.
# Champs : ts (UTC ISO), outil, cran, resultat (succes|refus|erreur), duree_ms, type_erreur.
# Classification : refus = PermissionError (porte d'identité _verifier_appelant, fail-closed) ;
# toute autre exception = erreur, avec sa classe (les gardes métier — collision, liste blanche,
# intégrité — restent distinguables par type_erreur à la relecture).
journal_mcp = logging.getLogger("journal_mcp")
_journal_handler = logging.StreamHandler()
_journal_handler.setFormatter(logging.Formatter("%(message)s"))
journal_mcp.addHandler(_journal_handler)
journal_mcp.propagate = False
journal_mcp.setLevel(logging.INFO)


# --- T-0027 : réduction du bruit de logs -----------------------------------------------------
# Cause mesurée sur Log Analytics (13/07/2026, 24 h) : 98,4 % des lignes console étaient les
# sondes /healthz relayées par uvicorn.access — le journal {"journal": "mcp-graph"} était noyé.
# 1) Filtre des sondes sur le logger d'accès uvicorn (le logger nommé existe avant le démarrage
#    d'uvicorn : addFilter ici s'applique à toutes ses lignes). Aucun autre accès n'est filtré.
class _FiltreSondesHealthz(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "/healthz" not in record.getMessage()

logging.getLogger("uvicorn.access").addFilter(_FiltreSondesHealthz())

# 2) Diagnostics HTTP du SDK azure-identity (dumps d'en-têtes à INFO) : relevés à WARNING.
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)
# --- fin T-0027 -------------------------------------------------------------------------------
# Cran par outil — résolu depuis contrats/socle/table-des-crans.yaml (v1.9) :
# lectures (list_items, lire_annuaire) = auto par nature (réversible, interne) ;
# ecrire_fait_derive_zone_proposition / televerser_brouillon_offre_zone_travail /
# creer_espace_mission / deposer_document_mission_zone_travail = auto ;
# notifier_equipe = notifie. Les réconciliateurs (T-0019/T-0008) exécutent une décision
# DÉJÀ PROMUE (organisation.md §5) : la porte « validé » vit à la promotion, en amont —
# le geste d'exécution idempotent et borné (liste blanche + AU) est journalisé « auto ».
CRAN_PAR_OUTIL = {
    "list_items": "auto",
    "create_list_item": "auto",
    "televerser_brouillon_offre": "auto",
    "creer_espace_mission": "auto",
    "deposer_document_mission": "auto",
    "reconcilier_groupe_perimetre": "auto",
    "reconcilier_groupe_parc": "auto",
    "lire_annuaire": "auto",
    "notifier_canal": "notifie",
    # Primitives Workbook/Tables (T-0031) : lecture non bornée = auto par nature ; écritures
    # bornées au domicile gabarit = auto (type d'action reconcilier_gabarit_pilotage, table v1.10).
    "workbook_lire_table": "auto",
    "workbook_ajouter_lignes": "auto",
    "workbook_maj_ligne": "auto",
    "workbook_archiver_gabarit": "auto",
}


def _journal_appel(outil: str):
    """Décorateur d'observabilité : une ligne JSON par appel, quel qu'en soit l'issue.

    Inséré entre @mcp.tool() et la fonction : functools.wraps préserve signature,
    annotations et docstring, donc le schéma MCP généré est inchangé (éprouvé, T-0020-b).
    Le journal n'altère JAMAIS le comportement : les exceptions sont re-levées telles quelles.
    """

    def decorateur(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            debut = time.monotonic()
            resultat = "succes"
            type_erreur = None
            try:
                return fn(*args, **kwargs)
            except PermissionError:
                resultat = "refus"
                raise
            except BaseException as exc:
                resultat = "erreur"
                type_erreur = type(exc).__name__
                raise
            finally:
                ligne = {
                    "journal": "mcp-graph",
                    "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                    "outil": outil,
                    "cran": CRAN_PAR_OUTIL.get(outil, "inconnu"),
                    "resultat": resultat,
                    "duree_ms": round((time.monotonic() - debut) * 1000),
                }
                if type_erreur:
                    ligne["type_erreur"] = type_erreur
                journal_mcp.info(json.dumps(ligne, ensure_ascii=False))

        return wrapper

    return decorateur
# --- fin journal structuré (T-0020-b) --------------------------------------------------------

# Variables d'environnement attendues (injectées à l'exécution — jamais ici, aucun secret).
ENV_AZURE_ENV = "AZURE_ENV"                # local | prod (défaut prod) — pilote le credential
ENV_AZURE_CLIENT_ID = "AZURE_CLIENT_ID"    # clientId de l'identité managée (défaut: MANAGED_IDENTITY_CLIENT_ID)
ENV_SITE_ID = "GRAPH_SITE_ID"
ENV_PROPOSITION_LIST_ID = "GRAPH_PROPOSITION_LIST_ID"
ENV_BROUILLON_DRIVE_ID = "GRAPH_BROUILLON_DRIVE_ID"      # bibliothèque Documents (cible figée du dépôt de brouillon)
ENV_BROUILLON_FOLDER_ID = "GRAPH_BROUILLON_FOLDER_ID"    # dossier « 00 - Proposition en cours » (seule cible de dépôt)
ENV_GROUPES_PERIMETRE_AUTORISES = "GRAPH_GROUPES_PERIMETRE_AUTORISES"  # CSV d'objectId des groupes de périmètre gérables (liste blanche figée côté serveur)
ENV_GROUPES_PARC_AUTORISES = "GRAPH_GROUPES_PARC_AUTORISES"  # CSV d'objectId des groupes de PARC gérables (liste blanche figée côté serveur, dédiée — séparée du périmètre)
ENV_MISSION_DRIVE_ID = "GRAPH_MISSION_DRIVE_ID"    # bibliothèque hôte de la racine « Missions » (cible figée de l'espace de mission)
ENV_MISSION_FOLDER_ID = "GRAPH_MISSION_FOLDER_ID"  # dossier racine « Missions » (seul parent des espaces de mission créés)
ENV_GABARIT_DRIVE_ID     = "GRAPH_GABARIT_DRIVE_ID"      # drive du site Contrats-admin hébergeant les gabarits
ENV_GABARIT_FOLDER_ID    = "GRAPH_GABARIT_FOLDER_ID"     # dossier « 06 - Gabarit ERP » (cible figée d'écriture gabarit)
ENV_GABARIT_OLD_FOLDER_ID= "GRAPH_GABARIT_OLD_FOLDER_ID" # dossier « 00 - Old » (archivage avant régénération)
# Souche UNIQUE : le gabarit vierge canon à la racine de « 06 - Gabarit ERP » (modele-donnees §5.2).
# Source FIGÉE de workbook_instancier_gabarit — jamais choisie par l'appelant.
GABARIT_VIERGE_NOM       = "gabarit-pilotage-mission.xlsx"
ENV_NOTIFICATIONS_LIST_ID = "GRAPH_NOTIFICATIONS_LIST_ID"  # liste « Notifications » (SEULE cible de notifier_canal — relais vers Teams par flux M365)

# Arbre FIGÉ d'un espace de mission (aucun choix de l'appelant) — convention « NN - Nom », dans cet ordre.
# Le support de kick-off se dépose dans « 01 - Pilotage » (décision gardien, amendement n°2 après test 0.8.0).
SOUS_DOSSIERS_MISSION = ("01 - Pilotage", "02 - Livrables")
# Whitelist d'extensions déposables dans un espace de mission (brouillons internes). Toute autre = refus.
EXTENSIONS_MISSION = (".docx", ".pptx", ".xlsx", ".pdf", ".md")

# stateless_http=True : pas de session persistante côté serveur (exigence Container Apps).
# host/port portés ICI (le SDK résolu n'accepte host/port NI via l'env FASTMCP_HOST, NI dans run() —
# run(host=,port=) lève TypeError ; seul le constructeur les accepte). Défaut sûr 0.0.0.0 : interface
# joignable par l'ingress/les sondes d'un conteneur (127.0.0.1 du SDK était le piège), surchargeable
# par FASTMCP_HOST / FASTMCP_PORT.
mcp = FastMCP(
    "allia-graph-proposition",
    stateless_http=True,
    host=os.environ.get("FASTMCP_HOST", "0.0.0.0"),
    port=int(os.environ.get("FASTMCP_PORT", "8000")),
)


class ConfigManquante(RuntimeError):
    """Levée quand une variable d'environnement requise est absente."""


@mcp.custom_route("/healthz", methods=["GET"])
async def healthz(request: Request) -> JSONResponse:
    """Endpoint de santé — liveness PUR.

    Séparé de `/mcp` (contrat §3). Ne touche pas Graph, n'acquiert aucun jeton :
    une sonde de l'hébergement (Container Apps) doit pouvoir l'appeler sans config M365.
    """
    return JSONResponse({"status": "ok"})


def _verifier_appelant(ctx: Context) -> None:
    """Valide le claim du token entrant et journalise l'identité appelante. FAIL-CLOSED.

    Appelée en tête de chaque outil exposé sur /mcp (validation in-tool, décision T-0009,
    22 juin 2026). Easy Auth authentifie le token (signature, expiry, tenant) mais ne vérifie
    PAS le claim roles — cette validation revient au code applicatif (doc Microsoft).

    Accès vérifié par sondage du SDK (mcp 1.28.0) : ctx.request_context.request est un objet
    Starlette Request portant .headers ; ctx est injecté automatiquement dans la signature du tool.

    Voie de lecture des claims (T-0015, 22 juin 2026) : Authorization: Bearer (le token présenté,
    porte le scp du flux délégué sans dépendre du token store) ; puis X-MS-TOKEN-AAD-ACCESS-TOKEN
    (JWT brut, si token store activé) ; puis fallback X-MS-CLIENT-PRINCIPAL.

    Politique FAIL-CLOSED : si la requête HTTP est absente (transport non-HTTP / hors requête),
    ou si aucun token n'est présent, ou si ni scp=access_as_user (humains) ni roles=MCP.Invoke
    (workloads) n'autorisent l'appel — l'accès est REFUSÉ.

    Raises:
        PermissionError: dans tous les cas de refus (porte qui ne peut pas vérifier = porte fermée).
    """
    # --- request Optional : None en stdio / hors-requête. FAIL-CLOSED. ---
    request = None
    try:
        request = ctx.request_context.request
    except (AttributeError, LookupError):
        request = None

    if request is None:
        logger.warning("accès refusé — aucune requête HTTP dans le contexte (transport non-HTTP ?)")
        raise PermissionError(
            "Accès refusé : aucune requête HTTP dans le contexte. La validation d'identité "
            "exige le transport streamable-http derrière Easy Auth."
        )

    # --- Journalisation de l'identité appelante (en-têtes posés par Easy Auth) ---
    principal_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID", "inconnu")
    principal_name = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME", "inconnu")
    principal_idp = request.headers.get("X-MS-CLIENT-PRINCIPAL-IDP", "inconnu")
    logger.info(
        "appel /mcp — principal_id=%s principal_name=%s idp=%s",
        principal_id, principal_name, principal_idp,
    )

    # --- Helper local : décode le payload d'un JWT (base64url), sans vérif de signature ---
    #     (Easy Auth a déjà validé signature/expiry/tenant en amont). ---
    def _claims_depuis_jwt(jwt: str) -> dict:
        parties = jwt.split(".")
        if len(parties) < 2:
            return {}
        segment = parties[1]
        segment += "=" * (-len(segment) % 4)
        return json.loads(base64.urlsafe_b64decode(segment).decode("utf-8"))

    claims: dict = {}

    # --- Voie 1 : Authorization: Bearer (token présenté par le client, transmis par Easy Auth ---
    #     en mode Return401). Porte scp pour le flux DÉLÉGUÉ humain SANS dépendre du token store ---
    #     (désactivé ici, donc X-MS-TOKEN-AAD-ACCESS-TOKEN est vide). Voie zéro-secret, sans état. ---
    en_tete_auth = request.headers.get("Authorization", "")
    if en_tete_auth[:7].lower() == "bearer ":
        try:
            claims = _claims_depuis_jwt(en_tete_auth[7:].strip())
        except Exception as exc:  # noqa: BLE001
            logger.warning("décodage Authorization Bearer impossible — %s", exc)

    # --- Voie 2 : X-MS-TOKEN-AAD-ACCESS-TOKEN (JWT brut posé par Easy Auth SI token store activé) ---
    if not claims:
        jwt_brut = request.headers.get("X-MS-TOKEN-AAD-ACCESS-TOKEN", "")
        if jwt_brut:
            try:
                claims = _claims_depuis_jwt(jwt_brut)
            except Exception as exc:  # noqa: BLE001
                logger.warning("décodage JWT brut impossible — %s", exc)

    # --- Fallback : X-MS-CLIENT-PRINCIPAL (base64 JSON, claims potentiellement mappés) ---
    if not claims:
        principal_b64 = request.headers.get("X-MS-CLIENT-PRINCIPAL", "")
        if principal_b64:
            try:
                decoded = json.loads(base64.b64decode(principal_b64).decode("utf-8"))
                # Format : {"claims": [{"typ": "...", "val": "..."}]} -> dict plat (multi-val = liste).
                for entry in decoded.get("claims", []):
                    typ = entry.get("typ", "")
                    val = entry.get("val", "")
                    if not typ:
                        continue
                    if typ in claims:
                        existant = claims[typ]
                        claims[typ] = existant if isinstance(existant, list) else [existant]
                        claims[typ].append(val)
                    else:
                        claims[typ] = val
            except Exception as exc:  # noqa: BLE001
                logger.warning("décodage X-MS-CLIENT-PRINCIPAL impossible — %s", exc)

    if not claims:
        logger.warning("accès refusé — principal_id=%s : aucun claim lisible", principal_id)
        raise PermissionError(
            "Accès refusé : aucun token exploitable dans les en-têtes Easy Auth."
        )

    # --- Humains : claim scp contenant access_as_user ---
    scp = claims.get("scp", "")
    scp_valeurs = scp.split() if isinstance(scp, str) else (scp if isinstance(scp, list) else [])
    if "access_as_user" in scp_valeurs:
        return

    # --- Workloads / transition : claim roles contenant MCP.Invoke ---
    # roles : liste (JWT standard) ou chaîne (mapping). Gérer aussi l'URI longue (cadrage T-0009).
    roles = claims.get("roles", [])
    if isinstance(roles, str):
        roles = [roles]
    roles_uri = claims.get("http://schemas.microsoft.com/ws/2008/06/identity/claims/role", [])
    if isinstance(roles_uri, str):
        roles_uri = [roles_uri]
    roles_effectifs = set(roles) | set(roles_uri)
    if "MCP.Invoke" in roles_effectifs:
        return

    logger.warning(
        "accès refusé — principal_id=%s scp=%r roles=%r",
        principal_id, scp, sorted(roles_effectifs),
    )
    raise PermissionError(
        "Accès refusé : le token ne porte ni scp=access_as_user ni roles=MCP.Invoke. "
        "Vérifiez l'octroi de l'app role MCP.Invoke à l'application cliente (T-0002b-5)."
    )


def _config() -> dict[str, str]:
    """Lit la configuration M365 depuis l'environnement. Échoue clairement si une variable manque.

    Appelée au moment de l'exécution d'un outil (jamais à l'import) : le serveur reste
    inerte tant qu'il n'est pas branché. Ne lit AUCUN secret (l'auth Graph = identité managée).
    """
    valeurs = {
        "site_id": os.environ.get(ENV_SITE_ID, ""),
        "proposition_list_id": os.environ.get(ENV_PROPOSITION_LIST_ID, ""),
        "brouillon_drive_id": os.environ.get(ENV_BROUILLON_DRIVE_ID, ""),
        "brouillon_folder_id": os.environ.get(ENV_BROUILLON_FOLDER_ID, ""),
    }
    manquantes = [k for k, v in valeurs.items() if not v]
    if manquantes:
        noms_env = {
            "site_id": ENV_SITE_ID,
            "proposition_list_id": ENV_PROPOSITION_LIST_ID,
            "brouillon_drive_id": ENV_BROUILLON_DRIVE_ID,
            "brouillon_folder_id": ENV_BROUILLON_FOLDER_ID,
        }
        absentes = ", ".join(noms_env[k] for k in manquantes)
        raise ConfigManquante(
            "Configuration M365 incomplète. Variables d'environnement manquantes : "
            f"{absentes}. Voir outils/mcp-graph/README.md (aucun secret n'est stocké dans le dépôt)."
        )
    return valeurs


def _config_mission() -> dict[str, str]:
    """Lit la configuration de la racine « Missions » (cible figée des espaces de mission).

    Config DÉDIÉE, séparée de `_config()` : les outils existants ne dépendent PAS de ces
    variables (aucune régression de leur contrat). Sur le modèle des listes blanches des
    réconciliateurs, les outils de mission lisent leur propre configuration et échouent
    clairement (ConfigManquante) si elle est absente. Aucun secret (identité managée).
    """
    valeurs = {
        "mission_drive_id": os.environ.get(ENV_MISSION_DRIVE_ID, ""),
        "mission_folder_id": os.environ.get(ENV_MISSION_FOLDER_ID, ""),
    }
    manquantes = [k for k, v in valeurs.items() if not v]
    if manquantes:
        noms_env = {
            "mission_drive_id": ENV_MISSION_DRIVE_ID,
            "mission_folder_id": ENV_MISSION_FOLDER_ID,
        }
        absentes = ", ".join(noms_env[k] for k in manquantes)
        raise ConfigManquante(
            "Configuration « Missions » incomplète. Variables d'environnement manquantes : "
            f"{absentes}. Racine « Missions » posée au runbook T-0024-c. Voir outils/mcp-graph/README.md."
        )
    return valeurs


def _config_gabarit() -> dict[str, str]:
    """Lit la configuration du domicile GABARIT (cible figée des écritures Workbook/Tables).

    Config DÉDIÉE, séparée de `_config()` et `_config_mission()` : les outils existants ne
    dépendent PAS de ces variables (aucune régression de leur contrat). Sur le modèle des
    listes blanches des réconciliateurs, les primitives gabarit lisent leur propre configuration
    et échouent clairement (ConfigManquante) si l'une manque. Aucun secret (identité managée).

    Trois cibles FIGÉES côté serveur (site Contrats-et-administratif) :
        - gabarit_drive_id     : drive hébergeant les gabarits ;
        - gabarit_folder_id    : dossier « 06 - Gabarit ERP » (seul parent des gabarits en écriture) ;
        - gabarit_old_folder_id: dossier « 00 - Old » (archivage horodaté avant régénération).
    """
    valeurs = {
        "gabarit_drive_id": os.environ.get(ENV_GABARIT_DRIVE_ID, ""),
        "gabarit_folder_id": os.environ.get(ENV_GABARIT_FOLDER_ID, ""),
        "gabarit_old_folder_id": os.environ.get(ENV_GABARIT_OLD_FOLDER_ID, ""),
    }
    manquantes = [k for k, v in valeurs.items() if not v]
    if manquantes:
        noms_env = {
            "gabarit_drive_id": ENV_GABARIT_DRIVE_ID,
            "gabarit_folder_id": ENV_GABARIT_FOLDER_ID,
            "gabarit_old_folder_id": ENV_GABARIT_OLD_FOLDER_ID,
        }
        absentes = ", ".join(noms_env[k] for k in manquantes)
        raise ConfigManquante(
            "Configuration « Gabarit » incomplète. Variables d'environnement manquantes : "
            f"{absentes}. Domicile GABARIT (06 - Gabarit ERP / 00 - Old) posé au runbook T-0031. "
            "Voir outils/mcp-graph/README.md."
        )
    return valeurs


def _assainir_code_mission(code_mission: str) -> str:
    """Assainit `code_mission` (fail-closed) et retourne le code strippé.

    Routine PARTAGÉE (décision S34) par `_resoudre_item_gabarit` et `workbook_instancier_gabarit` —
    donc par toutes les primitives gabarit : MÊME vocabulaire d'assainissement que le nom de fichier de
    `deposer_document_mission` (non vide, ni « / » « \\ » « .. », ni caractère de contrôle). La
    validation précède TOUT appel réseau (fail-closed) : la cible gabarit reste figée sous
    « 06 - Gabarit ERP », jamais un chemin libre.

    Raises:
        ValueError: code_mission vide ou contenant un motif interdit.
    """
    if not isinstance(code_mission, str) or not code_mission.strip():
        raise ValueError("`code_mission` doit être une chaîne non vide.")
    code = code_mission.strip()
    if any(motif in code for motif in ("/", "\\", "..")) or any(ord(c) < 32 for c in code):
        raise ValueError(
            "`code_mission` invalide : il ne doit contenir ni « / », ni « \\ », ni « .. », "
            "ni caractère de contrôle (la cible gabarit est figée sous « 06 - Gabarit ERP »)."
        )
    return code


def _resoudre_item_gabarit(client_http: httpx.Client, code_mission: str) -> str:
    """Résout l'item_id du gabarit d'une mission SOUS le domicile FIGÉ « 06 - Gabarit ERP ».

    Garde-fou structurel (décision S34) : l'appelant ne fournit JAMAIS d'item_id en écriture.
    Seul ce helper résout la cible, par CHEMIN sous le dossier gabarit figé côté serveur — l'écriture
    reste bornée par CONSTRUCTION : elle ne peut viser qu'un `gabarit-<CodeMission>.xlsx` de
    « 06 - Gabarit ERP », jamais un item_id libre.

    `code_mission` est assaini avec le MÊME vocabulaire que le nom de fichier de
    deposer_document_mission (non vide, pas de « / » « \\ » « .. », pas de caractère de contrôle) —
    la validation précède TOUT appel réseau (fail-closed).

    Raises:
        ValueError: code_mission vide ou contenant un motif interdit.
        FileNotFoundError: aucun gabarit pour ce code_mission dans « 06 - Gabarit ERP » (404).
        ConfigManquante: GRAPH_GABARIT_* absentes.
    """
    code = _assainir_code_mission(code_mission)
    cfg = _config_gabarit()
    drive_id = cfg["gabarit_drive_id"]
    folder_id = cfg["gabarit_folder_id"]
    nom = f"gabarit-{code}.xlsx"
    # Adressage par CHEMIN relatif au dossier gabarit figé (…/items/{folder_id}:/{nom}).
    url = f"{GRAPH_BASE}/drives/{drive_id}/items/{folder_id}:/{nom}"
    reponse = client_http.get(url, headers=_entetes())
    if reponse.status_code == 404:
        raise FileNotFoundError(
            f"aucun gabarit pour {code} dans « 06 - Gabarit ERP » (fichier attendu : {nom}). "
            "Génération initiale requise avant toute écriture."
        )
    reponse.raise_for_status()
    return reponse.json()["id"]


def _config_notifications() -> dict[str, str]:
    """Lit la configuration de la liste « Notifications » (cible figée de notifier_canal).

    Config DÉDIÉE, séparée de `_config()` : les outils existants ne dépendent PAS de cette
    variable (aucune régression de leur contrat). L'outil de notification lit sa propre
    configuration et échoue clairement (ConfigManquante) si elle est absente. Aucun secret
    (identité managée).
    """
    valeur = os.environ.get(ENV_NOTIFICATIONS_LIST_ID, "")
    if not valeur:
        raise ConfigManquante(
            "Configuration « Notifications » incomplète. Variable d'environnement manquante : "
            f"{ENV_NOTIFICATIONS_LIST_ID}. Liste créée et id posé au runbook T-0012. "
            "Voir outils/mcp-graph/README.md."
        )
    return {"notifications_list_id": valeur}


# Caractères interdits dans un composant de nom d'espace (invalides SharePoint / dangereux pour le
# path Graph). Le « : » est notamment interdit car il délimite l'adressage par chemin (…/items/{id}:/…).
_CARACTERES_INTERDITS_ESPACE = set('"*:<>?/\\|#%,')


def _composer_nom_espace(annee: str, client: str, nom_mission: str) -> str:
    """Valide (annee, client, nom_mission) et compose « AAAA - Client - Nom de la mission ».

    Composition CÔTÉ SERVEUR (garde-fou structurel, décision gardien 2 juillet 2026) : l'appelant
    ne fournit JAMAIS le nom d'espace final, seulement ses trois composantes. Helper PARTAGÉ par
    `creer_espace_mission` et `deposer_document_mission` — zéro dérive possible entre la création de
    l'espace et le dépôt d'un document (les deux composent le nom exactement de la même façon).

    Règles :
        - `annee` : exactement 4 chiffres, bornée [2020..2100] ;
        - `client` / `nom_mission` : après réduction des espaces (multiples → un seul) et strip des
          extrémités, 1..60 caractères ; refus des caractères " * : < > ? / \\ | # % , (et de tout
          caractère de contrôle), de la séquence « .. » et d'un point en tête ou en fin ; accents et
          espaces internes AUTORISÉS.

    Raises:
        ValueError: toute composante invalide (message explicite).
    """
    # --- annee : exactement 4 chiffres, bornée ---
    if not isinstance(annee, str) or len(annee) != 4 or not all(c in "0123456789" for c in annee):
        raise ValueError("`annee` doit être exactement 4 chiffres (ex. « 2026 »).")
    if not (2020 <= int(annee) <= 2100):
        raise ValueError("`annee` hors bornes : elle doit être comprise entre 2020 et 2100.")

    def _valider(valeur: str, etiquette: str) -> str:
        if not isinstance(valeur, str):
            raise ValueError(f"`{etiquette}` doit être une chaîne.")
        # Espaces multiples réduits à un seul + strip des extrémités (str.split sans argument).
        v = " ".join(valeur.split())
        if not v:
            raise ValueError(f"`{etiquette}` ne doit pas être vide.")
        if len(v) > 60:
            raise ValueError(f"`{etiquette}` invalide : 60 caractères maximum.")
        if any((c in _CARACTERES_INTERDITS_ESPACE) or (ord(c) < 32) for c in v):
            raise ValueError(
                f"`{etiquette}` invalide : il ne doit contenir aucun des caractères "
                '" * : < > ? / \\ | # % , ni de caractère de contrôle.'
            )
        if ".." in v:
            raise ValueError(f"`{etiquette}` invalide : la séquence « .. » est interdite.")
        if v.startswith(".") or v.endswith("."):
            raise ValueError(f"`{etiquette}` invalide : pas de point en tête ni en fin.")
        return v

    client_ok = _valider(client, "client")
    nom_ok = _valider(nom_mission, "nom_mission")
    return f"{annee} - {client_ok} - {nom_ok}"


def _credential():
    """Construit le credential de SORTIE Graph selon AZURE_ENV (jamais à l'import — au call-time).

    - prod (défaut sûr) : ManagedIdentityCredential(client_id=...) — identité managée user-assigned,
      type SPÉCIFIQUE pour éviter qu'une chaîne de fallback ramasse une autre identité.
    - local : DefaultAzureCredential() — découvre az login / VS Code (hors Azure).

    Aucun secret : zéro secret côté flux Graph.
    """
    env = (os.environ.get(ENV_AZURE_ENV, "") or "prod").strip().lower()
    if env == "local":
        return DefaultAzureCredential()
    # prod (et défaut si AZURE_ENV absente ou inattendue) : identité managée user-assigned.
    client_id = (os.environ.get(ENV_AZURE_CLIENT_ID, "") or MANAGED_IDENTITY_CLIENT_ID).strip()
    return ManagedIdentityCredential(client_id=client_id)


def _entetes() -> dict[str, str]:
    """En-têtes Graph avec un jeton frais (identité managée). Construit le credential au call-time."""
    token = _credential().get_token(GRAPH_SCOPE).token
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def _lire_membres_groupe(client: httpx.Client, group_id: str) -> set[str]:
    """Lit l'ensemble des objectId des membres d'un groupe (pagination @odata.nextLink).

    Lecture seule. Ne décide rien, n'écrit rien.
    """
    actuels: set[str] = set()
    url = f"{GRAPH_BASE}/groups/{group_id}/members"
    params = {"$select": "id", "$top": "999"}
    page = client.get(url, headers=_entetes(), params=params)
    page.raise_for_status()
    corps = page.json()
    for membre in corps.get("value", []):
        mid = membre.get("id")
        if mid:
            actuels.add(mid)
    suivant = corps.get("@odata.nextLink")
    while suivant:
        page = client.get(suivant, headers=_entetes())
        page.raise_for_status()
        corps = page.json()
        for membre in corps.get("value", []):
            mid = membre.get("id")
            if mid:
                actuels.add(mid)
        suivant = corps.get("@odata.nextLink")
    return actuels


@mcp.tool()
@_journal_appel("list_items")
def list_items(ctx: Context, list_id: str, top: int = 50) -> dict[str, Any]:
    """Lit (lecture seule) les éléments d'une liste SharePoint du site AlliaConsuling.

    GET /sites/{site-id}/lists/{list-id}/items?$expand=fields

    Args:
        list_id: identifiant (ou nom) de la liste à lire, sur le site configuré.
        top: nombre maximum d'éléments à retourner (pagination simple, défaut 50).

    Returns:
        Un dict {"items": [...], "count": n} où chaque item inclut ses `fields`.

    Note : opération de LECTURE. Elle ne modifie rien. Les listes RH/CVs sensibles
    (modele-donnees.md §2 bis) exigent une journalisation active (chantier T-0003) AVANT
    tout accès agent — contrôle côté tenant, hors de ce code.
    """
    _verifier_appelant(ctx)
    cfg = _config()
    url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{list_id}/items"
    params = {"$expand": "fields", "$top": str(max(1, min(top, 200)))}
    with httpx.Client(timeout=30) as client:
        reponse = client.get(url, headers=_entetes(), params=params)
        reponse.raise_for_status()
        corps = reponse.json()
    items = corps.get("value", [])
    return {"items": items, "count": len(items)}


@mcp.tool()
@_journal_appel("create_list_item")
def create_list_item(ctx: Context, fields: dict[str, Any]) -> dict[str, Any]:
    """Crée un élément UNIQUEMENT dans la liste « Zone-de-proposition ».

    POST /sites/{site-id}/lists/{PROPOSITION_LIST_ID}/items  body: {"fields": {...}}

    La liste cible est fixée par GRAPH_PROPOSITION_LIST_ID côté serveur. Cette fonction
    n'accepte AUCUN identifiant de liste de l'appelant : il est donc impossible d'écrire
    dans une source. C'est « le dérivé n'est jamais le saisi » appliqué dans le code
    (doctrine §2 ; modele-donnees.md §3).

    Args:
        fields: dictionnaire des colonnes à écrire (ex. {"Title": "...", "Statut": "..."}).

    Returns:
        Un dict {"created_id": "...", "fields": {...}} décrivant l'élément créé.
    """
    _verifier_appelant(ctx)
    if not isinstance(fields, dict) or not fields:
        raise ValueError("`fields` doit être un dictionnaire non vide des colonnes à écrire.")

    cfg = _config()
    # Cible d'écriture NON paramétrable par l'appelant : la zone de proposition, et elle seule.
    liste_ecriture = cfg["proposition_list_id"]
    url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{liste_ecriture}/items"
    with httpx.Client(timeout=30) as client:
        reponse = client.post(
            url,
            headers={**_entetes(), "Content-Type": "application/json"},
            json={"fields": fields},
        )
        reponse.raise_for_status()
        corps = reponse.json()
    return {"created_id": corps.get("id"), "fields": corps.get("fields", {})}


@mcp.tool()
@_journal_appel("televerser_brouillon_offre")
def televerser_brouillon_offre(
    ctx: Context, nom_fichier: str, contenu_base64: str, candidat_id: str
) -> dict[str, Any]:
    """Dépose un BROUILLON d'offre (.docx) dans « 00 - Proposition en cours », et nulle part ailleurs.

    PUT /drives/{BROUILLON_DRIVE_ID}/items/{BROUILLON_FOLDER_ID}:/{nom_fichier}:/content
        ?@microsoft.graph.conflictBehavior=fail

    Cible FIGÉE côté serveur par GRAPH_BROUILLON_DRIVE_ID + GRAPH_BROUILLON_FOLDER_ID : comme
    `create_list_item` fige sa liste, cette fonction n'accepte AUCUN identifiant de cible de
    l'appelant. Le dépôt vise UNIQUEMENT le dossier « 00 - Proposition en cours » (bibliothèque
    de travail interne) ; JAMAIS le niveau « 01 - Proposition d'embauche », domicile des offres
    SIGNÉES. `candidat_id` sert au nommage / à la traçabilité, PAS à choisir la cible.

    Garde-fous inscrits dans le code (table-des-crans.yaml : televerser_brouillon_offre_zone_travail,
    cran auto) :
        - .docx FORCÉ (toute autre extension est refusée) ;
        - nom de fichier ASSAINI : refus de « / », « \\ », « .. » et des caractères de contrôle
          (pas d'évasion hors du dossier figé) ;
        - COLLISION = FAIL : un brouillon de même nom n'est JAMAIS écrasé ; sa régénération est
          un geste humain de retrait (cohérent avec supprimer_definitivement — proscrit).

    Un BROUILLON n'est PAS une offre : l'émission de l'offre reste un acte HUMAIN
    (prendre_engagement_juridique_ou_financier — PROSCRIT à l'agent et à Claude).

    Args:
        nom_fichier: nom du fichier à déposer, doit se terminer par « .docx ».
        contenu_base64: contenu du .docx encodé en base64.
        candidat_id: identifiant du candidat (nommage / traçabilité, jamais la cible).

    Returns:
        Un dict {"item_id": "...", "nom": "...", "web_url": "..."} décrivant le fichier déposé.
    """
    _verifier_appelant(ctx)

    # --- Nom de fichier : .docx FORCÉ + assainissement (jamais d'évasion hors du dossier figé) ---
    if not isinstance(nom_fichier, str) or not nom_fichier.lower().endswith(".docx"):
        raise ValueError("`nom_fichier` doit être une chaîne se terminant par « .docx ».")
    if any(motif in nom_fichier for motif in ("/", "\\", "..")) or any(ord(c) < 32 for c in nom_fichier):
        raise ValueError(
            "`nom_fichier` invalide : il ne doit contenir ni « / », ni « \\ », ni « .. », "
            "ni caractère de contrôle (le dépôt est figé dans « 00 - Proposition en cours »)."
        )

    # --- Décodage du contenu base64 ---
    try:
        contenu = base64.b64decode(contenu_base64, validate=True)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"`contenu_base64` n'est pas un base64 valide : {exc}") from exc

    cfg = _config()
    # Cible d'écriture NON paramétrable par l'appelant : « 00 - Proposition en cours », et elle seule.
    drive_id = cfg["brouillon_drive_id"]
    folder_id = cfg["brouillon_folder_id"]
    url = f"{GRAPH_BASE}/drives/{drive_id}/items/{folder_id}:/{nom_fichier}:/content"
    params = {"@microsoft.graph.conflictBehavior": "fail"}  # jamais d'écrasement
    type_docx = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    with httpx.Client(timeout=30) as client:
        reponse = client.put(
            url,
            headers={**_entetes(), "Content-Type": type_docx},
            content=contenu,
            params=params,
        )
        # Collision : un brouillon de même nom existe déjà — NE PAS réessayer, NE PAS écraser.
        if reponse.status_code == 409:
            raise FileExistsError(
                f"Brouillon déjà existant pour « {nom_fichier} » (candidat {candidat_id}) : "
                "retrait humain requis (collision=fail). Aucun écrasement."
            )
        reponse.raise_for_status()
        corps = reponse.json()
    return {
        "item_id": corps.get("id"),
        "nom": corps.get("name"),
        "web_url": corps.get("webUrl"),
    }


@mcp.tool()
@_journal_appel("creer_espace_mission")
def creer_espace_mission(
    ctx: Context, annee: str, client: str, nom_mission: str
) -> dict[str, Any]:
    """Crée l'ESPACE DE MISSION (arbre de dossiers figé) sous la racine « Missions », et nulle part ailleurs.

    POST /drives/{MISSION_DRIVE_ID}/items/{MISSION_FOLDER_ID}/children
         body {"name": <nom_espace>, "folder": {}, "@microsoft.graph.conflictBehavior": "fail"}
    puis, sous le dossier de mission ainsi créé, un POST children par sous-dossier FIGÉ.

    Cible FIGÉE côté serveur par GRAPH_MISSION_DRIVE_ID + GRAPH_MISSION_FOLDER_ID : comme
    `create_list_item` fige sa liste et `televerser_brouillon_offre` son dossier, cette fonction
    n'accepte AUCUN identifiant de cible de l'appelant. Le NOM de l'espace est COMPOSÉ CÔTÉ SERVEUR
    (décision gardien 2 juillet 2026) : « AAAA - Client - Nom de la mission » (ex.
    « 2026 - Arabelle Solutions - Siteflow ») via `_composer_nom_espace` — l'appelant fournit les trois
    composantes, jamais le nom final ; la racine « Missions » reste la seule cible possible.

    Garde-fous inscrits dans le code (table-des-crans.yaml : creer_espace_mission, cran auto) :
        - `annee` / `client` / `nom_mission` VALIDÉS et le nom COMPOSÉ côté serveur (pas d'évasion :
          « / », « \\ », « .. », « : » et autres caractères SharePoint-invalides refusés) ;
        - arbre de sous-dossiers FIGÉ DANS LE CODE (SOUS_DOSSIERS_MISSION), jamais choisi par l'appelant ;
        - COLLISION = FAIL (`@microsoft.graph.conflictBehavior: fail`) sur CHAQUE création : un espace
          de mission de même nom n'est JAMAIS écrasé ni fusionné ; sa reprise est un geste humain.

    Un espace de mission est une zone de travail INTERNE ; sa création est réversible (cran auto).

    Args:
        annee: année de la mission (exactement 4 chiffres, [2020..2100]).
        client: nom du client (1..60 car., composante du nom d'espace ; jamais la cible).
        nom_mission: nom de la mission (1..60 car., composante du nom d'espace ; jamais la cible).

    Returns:
        dict {"nom_espace", "web_url", "sous_dossiers"} décrivant l'espace créé.

    Raises:
        ValueError: annee / client / nom_mission invalide.
        FileExistsError: un espace de même nom existe déjà (collision=fail, aucun écrasement).
        ConfigManquante: GRAPH_MISSION_DRIVE_ID / GRAPH_MISSION_FOLDER_ID absentes.
    """
    _verifier_appelant(ctx)

    nom_espace = _composer_nom_espace(annee, client, nom_mission)

    cfg = _config_mission()
    # Cible NON paramétrable par l'appelant : la racine « Missions », et elle seule.
    drive_id = cfg["mission_drive_id"]
    racine_id = cfg["mission_folder_id"]
    enfants_racine = f"{GRAPH_BASE}/drives/{drive_id}/items/{racine_id}/children"
    with httpx.Client(timeout=30) as client_http:
        # --- Dossier racine de la mission (collision = fail) ---
        reponse = client_http.post(
            enfants_racine,
            headers={**_entetes(), "Content-Type": "application/json"},
            json={"name": nom_espace, "folder": {}, "@microsoft.graph.conflictBehavior": "fail"},
        )
        if reponse.status_code == 409:
            raise FileExistsError(
                f"Espace de mission déjà existant pour « {nom_espace} » : reprise humaine requise "
                "(collision=fail). Aucun écrasement, aucune fusion."
            )
        reponse.raise_for_status()
        mission = reponse.json()
        mission_id = mission.get("id")
        web_url = mission.get("webUrl")

        # --- Sous-dossiers FIGÉS, sous le dossier de mission (collision = fail sur chacun) ---
        enfants_mission = f"{GRAPH_BASE}/drives/{drive_id}/items/{mission_id}/children"
        sous_dossiers_crees: list[str] = []
        for sous_dossier in SOUS_DOSSIERS_MISSION:
            sous = client_http.post(
                enfants_mission,
                headers={**_entetes(), "Content-Type": "application/json"},
                json={"name": sous_dossier, "folder": {}, "@microsoft.graph.conflictBehavior": "fail"},
            )
            if sous.status_code == 409:
                raise FileExistsError(
                    f"Sous-dossier « {sous_dossier} » déjà existant dans l'espace « {nom_espace} » : "
                    "reprise humaine requise (collision=fail). Aucun écrasement."
                )
            sous.raise_for_status()
            sous_dossiers_crees.append(sous_dossier)

    return {
        "nom_espace": nom_espace,
        "web_url": web_url,
        "sous_dossiers": sous_dossiers_crees,
    }


@mcp.tool()
@_journal_appel("deposer_document_mission")
def deposer_document_mission(
    ctx: Context, annee: str, client: str, nom_mission: str,
    sous_dossier: str, nom_fichier: str, contenu_base64: str, sha256_attendu: str
) -> dict[str, Any]:
    """Dépose un BROUILLON INTERNE dans un sous-dossier FIGÉ d'un espace de mission, et nulle part ailleurs.

    PUT /drives/{MISSION_DRIVE_ID}/items/{MISSION_FOLDER_ID}:/{nom_espace}/{sous_dossier}/{nom}:/content
        ?@microsoft.graph.conflictBehavior=fail

    Même racine FIGÉE côté serveur que `creer_espace_mission` (GRAPH_MISSION_DRIVE_ID +
    GRAPH_MISSION_FOLDER_ID) : l'appelant ne choisit JAMAIS la cible. Le nom d'espace est RECOMPOSÉ
    côté serveur par le MÊME helper que `creer_espace_mission` (`_composer_nom_espace`) — zéro dérive
    possible entre la création et le dépôt. Le dépôt vise UNIQUEMENT
    <racine Missions>/<nom_espace>/<sous_dossier>/<nom_fichier> ; jamais un espace exposé au client.

    Garde-fous inscrits dans le code (table-des-crans.yaml : deposer_document_mission_zone_travail,
    cran auto) :
        - `annee` / `client` / `nom_mission` VALIDÉS et nom d'espace COMPOSÉ côté serveur (comme
          creer_espace_mission) — pas d'évasion hors de la racine figée ;
        - `sous_dossier` restreint à la LISTE BLANCHE figée SOUS_DOSSIERS_MISSION (PermissionError sinon) ;
        - `nom_fichier` ASSAINI (refus de « / », « \\ », « .. », caractères de contrôle) et extension
          FORCÉE dans EXTENSIONS_MISSION (.docx .pptx .xlsx .pdf .md) — toute autre est refusée ;
        - COLLISION = FAIL (`@microsoft.graph.conflictBehavior: fail`) : un document de même nom n'est
          JAMAIS écrasé ; sa régénération est un geste humain de retrait.
        - INTÉGRITÉ FAIL-CLOSED (leçon épreuve T-0024-d) : l'appelant fournit `sha256_attendu` ; le
          serveur recalcule le sha256 du contenu DÉCODÉ et REFUSE (ValueError) avant tout appel Graph
          si l'empreinte diffère — un contenu corrompu en transit ne peut PAS être stocké silencieusement.

    Un brouillon interne n'est PAS un livrable client : l'envoi au client reste un acte HUMAIN
    (envoyer_livrable_client — cran validé, grade habilité ; jamais l'agent).

    Args:
        annee: année de la mission (exactement 4 chiffres, [2020..2100]).
        client: nom du client (composante du nom d'espace ; jamais la cible).
        nom_mission: nom de la mission (composante du nom d'espace ; jamais la cible).
        sous_dossier: sous-dossier de destination, dans SOUS_DOSSIERS_MISSION (liste blanche).
        nom_fichier: nom du fichier, extension dans EXTENSIONS_MISSION.
        contenu_base64: contenu du fichier encodé en base64.
        sha256_attendu: empreinte sha256 (64 hex minuscules) du contenu attendu — garde-fou d'intégrité.

    Returns:
        dict {"item_id", "web_url", "taille_octets", "sha256"} décrivant le document déposé
        (sha256 = empreinte du contenu réellement envoyé au PUT).

    Raises:
        ValueError: annee/client/nom_mission ou nom_fichier invalide, extension hors whitelist,
            base64 invalide, sha256_attendu mal formé, ou INTÉGRITÉ (sha256 reçu ≠ attendu).
        PermissionError: sous_dossier hors liste blanche.
        FileExistsError: un document de même nom existe déjà (collision=fail, aucun écrasement).
        ConfigManquante: GRAPH_MISSION_DRIVE_ID / GRAPH_MISSION_FOLDER_ID absentes.
    """
    _verifier_appelant(ctx)

    # Nom d'espace recomposé par le MÊME helper que creer_espace_mission (zéro dérive).
    nom_espace = _composer_nom_espace(annee, client, nom_mission)

    # --- sous_dossier : liste blanche figée (exactement l'un des sous-dossiers de mission) ---
    if sous_dossier not in SOUS_DOSSIERS_MISSION:
        raise PermissionError(
            f"Sous-dossier non autorisé : « {sous_dossier} ». Seuls "
            f"{', '.join(SOUS_DOSSIERS_MISSION)} sont des cibles de dépôt (liste blanche figée)."
        )

    # --- Nom de fichier : assainissement + extension whitelistée ---
    if not isinstance(nom_fichier, str) or not nom_fichier.strip():
        raise ValueError("`nom_fichier` doit être une chaîne non vide.")
    if any(motif in nom_fichier for motif in ("/", "\\", "..")) or any(ord(c) < 32 for c in nom_fichier):
        raise ValueError(
            "`nom_fichier` invalide : il ne doit contenir ni « / », ni « \\ », ni « .. », "
            "ni caractère de contrôle (le dépôt est figé sous la racine « Missions »)."
        )
    if not any(nom_fichier.lower().endswith(ext) for ext in EXTENSIONS_MISSION):
        raise ValueError(
            "`nom_fichier` invalide : extension hors whitelist. Extensions autorisées : "
            f"{', '.join(EXTENSIONS_MISSION)}."
        )

    # --- sha256_attendu : format strict (64 hex minuscules) ---
    if (not isinstance(sha256_attendu, str) or len(sha256_attendu) != 64
            or any(c not in "0123456789abcdef" for c in sha256_attendu)):
        raise ValueError(
            "`sha256_attendu` doit être une empreinte sha256 de 64 caractères hexadécimaux minuscules."
        )

    # --- Décodage du contenu base64 ---
    try:
        contenu = base64.b64decode(contenu_base64, validate=True)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"`contenu_base64` n'est pas un base64 valide : {exc}") from exc

    # --- INTÉGRITÉ FAIL-CLOSED : sha256 du contenu décodé == attendu, AVANT tout appel Graph ---
    sha256_recu = hashlib.sha256(contenu).hexdigest()
    if sha256_recu != sha256_attendu:
        raise ValueError(
            f"INTEGRITÉ : sha256 reçu {sha256_recu} ≠ attendu {sha256_attendu} — "
            "contenu corrompu en transit, RIEN n'a été écrit."
        )

    cfg = _config_mission()
    # Cible NON paramétrable par l'appelant : sous la racine « Missions » figée, et elle seule.
    drive_id = cfg["mission_drive_id"]
    racine_id = cfg["mission_folder_id"]
    chemin = f"{nom_espace}/{sous_dossier}/{nom_fichier}"
    url = f"{GRAPH_BASE}/drives/{drive_id}/items/{racine_id}:/{chemin}:/content"
    params = {"@microsoft.graph.conflictBehavior": "fail"}  # jamais d'écrasement
    with httpx.Client(timeout=30) as client_http:
        reponse = client_http.put(
            url,
            headers={**_entetes(), "Content-Type": "application/octet-stream"},
            content=contenu,
            params=params,
        )
        # Collision : un document de même nom existe déjà — NE PAS réessayer, NE PAS écraser.
        if reponse.status_code == 409:
            raise FileExistsError(
                f"Document déjà existant pour « {nom_fichier} » dans « {nom_espace}/{sous_dossier} » : "
                "retrait humain requis (collision=fail). Aucun écrasement."
            )
        reponse.raise_for_status()
        corps = reponse.json()
    return {
        "item_id": corps.get("id"),
        "web_url": corps.get("webUrl"),
        "taille_octets": len(contenu),
        "sha256": sha256_recu,
    }


@mcp.tool()
@_journal_appel("reconcilier_groupe_perimetre")
def reconcilier_groupe_perimetre(
    ctx: Context, group_id: str, membres_attendus: list[str]
) -> dict[str, Any]:
    """Réconcilie l'appartenance d'un GROUPE DE PÉRIMÈTRE Entra sur un état désiré (idempotent).

    Projette une DÉCISION DE DÉLÉGATION promue (organisation.md §3, §5 — « le guide ») sur le
    groupe Entra du périmètre, en n'appliquant QUE le delta. « Le dérivé n'est jamais le saisi » :
    l'état désiré (membres_attendus) dérive d'une décision promue, résolue EN AMONT par Claude Code
    à partir du canon ; cet outil ne DÉCIDE rien — il réconcilie l'état réel sur l'état désiré.

    Chaîne d'autorité (organisation.md §5) : le guide (Git) -> Claude (réconciliation au moindre
    privilège) -> M365 (appartenance au groupe ouvre l'accès). Attribuer = ajouter au groupe ;
    révoquer = retirer (retour arrière en une action).

    Garde-fous inscrits dans le code :
    - LISTE BLANCHE figée côté serveur (GRAPH_GROUPES_PERIMETRE_AUTORISES) : group_id hors liste
      => PermissionError, aucun appel d'écriture. Défense en profondeur EN PLUS de la borne
      Administrative Unit côté Entra (runbook T-0019-b) : le code ne peut toucher QUE des groupes
      de périmètre déclarés.
    - IDEMPOTENT : seul le delta est appliqué (POST $ref pour ajouter, DELETE $ref pour retirer) ;
      delta vide => aucun appel d'écriture.
    - membres_attendus = [] est autorisé et signifie « vider le groupe » (révocation totale,
      réversible) : geste légitime de la chaîne, jamais une suppression de données.

    Le pouvoir de gérer l'appartenance est conféré HORS code : rôle Entra Groups Administrator
    assigné au service principal de l'identité managée, SCOPÉ à une Administrative Unit ne contenant
    que les groupes de périmètre (runbook T-0019-b). Le scope Graph reste .default ; aucun secret.

    Args:
        group_id: objectId du groupe de périmètre à réconcilier (doit être dans la liste blanche).
        membres_attendus: liste d'objectId Entra (GUID) des membres attendus (état désiré).

    Returns:
        dict {"group_id", "ajoutes", "retires", "inchanges", "etat_final"} décrivant le delta.

    Raises:
        PermissionError: group_id hors liste blanche (cible non autorisée), ou appelant non validé.
        ValueError: membres_attendus mal formé.
        ConfigManquante: GRAPH_GROUPES_PERIMETRE_AUTORISES absente.
    """
    _verifier_appelant(ctx)

    # --- Liste blanche figée côté serveur (défense en profondeur) ---
    csv_autorises = os.environ.get(ENV_GROUPES_PERIMETRE_AUTORISES, "").strip()
    if not csv_autorises:
        raise ConfigManquante(
            "Configuration incomplète : variable d'environnement manquante "
            f"{ENV_GROUPES_PERIMETRE_AUTORISES}. Voir outils/mcp-graph/README.md."
        )
    autorises = {g.strip() for g in csv_autorises.split(",") if g.strip()}
    if group_id not in autorises:
        logger.warning("réconciliation refusée — group_id=%s hors liste blanche", group_id)
        raise PermissionError(
            "Cible non autorisée : ce group_id n'est pas un groupe de périmètre déclaré "
            f"({ENV_GROUPES_PERIMETRE_AUTORISES}). Aucune écriture effectuée."
        )

    # --- Validation de l'état désiré ---
    if not isinstance(membres_attendus, list) or any(
        (not isinstance(m, str)) or len(m.strip()) < 30 or " " in m.strip()
        for m in membres_attendus
    ):
        raise ValueError(
            "`membres_attendus` doit être une liste d'objectId Entra (GUID). "
            "Liste vide autorisée (= vider le groupe)."
        )
    attendus = {m.strip() for m in membres_attendus}

    # --- Lecture des membres actuels (pagination @odata.nextLink) ---
    actuels: set[str] = set()
    url = f"{GRAPH_BASE}/groups/{group_id}/members"
    params = {"$select": "id", "$top": "999"}
    with httpx.Client(timeout=30) as client:
        page = client.get(url, headers=_entetes(), params=params)
        page.raise_for_status()
        corps = page.json()
        for membre in corps.get("value", []):
            mid = membre.get("id")
            if mid:
                actuels.add(mid)
        suivant = corps.get("@odata.nextLink")
        while suivant:
            page = client.get(suivant, headers=_entetes())
            page.raise_for_status()
            corps = page.json()
            for membre in corps.get("value", []):
                mid = membre.get("id")
                if mid:
                    actuels.add(mid)
            suivant = corps.get("@odata.nextLink")

        a_ajouter = sorted(attendus - actuels)
        a_retirer = sorted(actuels - attendus)
        inchanges = sorted(attendus & actuels)

        # --- Application du delta SEUL (idempotent) ---
        for oid in a_ajouter:
            ajout = client.post(
                f"{GRAPH_BASE}/groups/{group_id}/members/$ref",
                headers={**_entetes(), "Content-Type": "application/json"},
                json={"@odata.id": f"{GRAPH_BASE}/directoryObjects/{oid}"},
            )
            ajout.raise_for_status()
            logger.info("réconciliation — group_id=%s AJOUT membre=%s", group_id, oid)
        for oid in a_retirer:
            retrait = client.delete(
                f"{GRAPH_BASE}/groups/{group_id}/members/{oid}/$ref",
                headers=_entetes(),
            )
            retrait.raise_for_status()
            logger.info("réconciliation — group_id=%s RETRAIT membre=%s", group_id, oid)

    return {
        "group_id": group_id,
        "ajoutes": a_ajouter,
        "retires": a_retirer,
        "inchanges": inchanges,
        "etat_final": sorted(attendus),
    }


@mcp.tool()
@_journal_appel("reconcilier_groupe_parc")
def reconcilier_groupe_parc(
    ctx: Context, group_id: str, membres_attendus: list[str]
) -> dict[str, Any]:
    """Réconcilie l'appartenance du GROUPE DE PARC d'enrôlement Entra sur un état désiré (idempotent).

    Miroir EXACT de `reconcilier_groupe_perimetre` (T-0019), appliqué au groupe d'enrôlement du
    PARC collaborateur (grp-parc-collaborateur). Projette une DÉCISION promue (organisation.md
    §3, §5 — « le guide ») sur le groupe Entra du parc, en n'appliquant QUE le delta. « Le dérivé
    n'est jamais le saisi » : l'état désiré (membres_attendus) dérive d'une décision promue, résolue
    EN AMONT par Claude Code à partir du canon ; cet outil ne DÉCIDE rien — il réconcilie l'état
    réel sur l'état désiré.

    Chaîne d'autorité (organisation.md §5) : le guide (Git) -> Claude (réconciliation au moindre
    privilège) -> M365 (appartenance au groupe ouvre l'enrôlement). Attribuer = ajouter au groupe ;
    révoquer = retirer (retour arrière en une action).

    SÉPARATION socle/périmètre (décision gardien 28/06) : la liste blanche du parc est DÉDIÉE
    (GRAPH_GROUPES_PARC_AUTORISES), strictement séparée de celle du périmètre — un group_id de
    périmètre n'est PAS gérable par cet outil, et réciproquement.

    Garde-fous inscrits dans le code :
    - LISTE BLANCHE DÉDIÉE figée côté serveur (GRAPH_GROUPES_PARC_AUTORISES) : group_id hors liste
      => PermissionError, aucun appel d'écriture. Défense en profondeur EN PLUS de la borne
      Administrative Unit côté Entra (au-groupes-socle, runbook gardien) : le code ne peut toucher
      QUE des groupes de parc déclarés.
    - IDEMPOTENT : seul le delta est appliqué (POST $ref pour ajouter, DELETE $ref pour retirer) ;
      delta vide => aucun appel d'écriture.
    - membres_attendus = [] est autorisé et signifie « vider le groupe » (révocation totale,
      réversible) : geste légitime de la chaîne, jamais une suppression de données.

    Le pouvoir de gérer l'appartenance est conféré HORS code : rôle Entra Groups Administrator
    assigné au service principal de l'identité managée, SCOPÉ à l'Administrative Unit au-groupes-socle
    (runbook gardien). Le scope Graph reste .default ; aucun secret.

    Args:
        group_id: objectId du groupe de parc à réconcilier (doit être dans la liste blanche dédiée).
        membres_attendus: liste d'objectId Entra (GUID) des membres attendus (état désiré).

    Returns:
        dict {"group_id", "ajoutes", "retires", "inchanges", "etat_final"} décrivant le delta.

    Raises:
        PermissionError: group_id hors liste blanche (cible non autorisée), ou appelant non validé.
        ValueError: membres_attendus mal formé.
        ConfigManquante: GRAPH_GROUPES_PARC_AUTORISES absente.
    """
    _verifier_appelant(ctx)

    # --- Liste blanche DÉDIÉE figée côté serveur (défense en profondeur) ---
    csv_autorises = os.environ.get(ENV_GROUPES_PARC_AUTORISES, "").strip()
    if not csv_autorises:
        raise ConfigManquante(
            "Configuration incomplète : variable d'environnement manquante "
            f"{ENV_GROUPES_PARC_AUTORISES}. Voir outils/mcp-graph/README.md."
        )
    autorises = {g.strip() for g in csv_autorises.split(",") if g.strip()}
    if group_id not in autorises:
        logger.warning("réconciliation parc refusée — group_id=%s hors liste blanche", group_id)
        raise PermissionError(
            "Cible non autorisée : ce group_id n'est pas un groupe de parc déclaré "
            f"({ENV_GROUPES_PARC_AUTORISES}). Aucune écriture effectuée."
        )

    # --- Validation de l'état désiré ---
    if not isinstance(membres_attendus, list) or any(
        (not isinstance(m, str)) or len(m.strip()) < 30 or " " in m.strip()
        for m in membres_attendus
    ):
        raise ValueError(
            "`membres_attendus` doit être une liste d'objectId Entra (GUID). "
            "Liste vide autorisée (= vider le groupe)."
        )
    attendus = {m.strip() for m in membres_attendus}

    # --- Lecture des membres actuels (pagination @odata.nextLink) ---
    actuels: set[str] = set()
    url = f"{GRAPH_BASE}/groups/{group_id}/members"
    params = {"$select": "id", "$top": "999"}
    with httpx.Client(timeout=30) as client:
        page = client.get(url, headers=_entetes(), params=params)
        page.raise_for_status()
        corps = page.json()
        for membre in corps.get("value", []):
            mid = membre.get("id")
            if mid:
                actuels.add(mid)
        suivant = corps.get("@odata.nextLink")
        while suivant:
            page = client.get(suivant, headers=_entetes())
            page.raise_for_status()
            corps = page.json()
            for membre in corps.get("value", []):
                mid = membre.get("id")
                if mid:
                    actuels.add(mid)
            suivant = corps.get("@odata.nextLink")

        a_ajouter = sorted(attendus - actuels)
        a_retirer = sorted(actuels - attendus)
        inchanges = sorted(attendus & actuels)

        # --- Application du delta SEUL (idempotent) ---
        for oid in a_ajouter:
            ajout = client.post(
                f"{GRAPH_BASE}/groups/{group_id}/members/$ref",
                headers={**_entetes(), "Content-Type": "application/json"},
                json={"@odata.id": f"{GRAPH_BASE}/directoryObjects/{oid}"},
            )
            ajout.raise_for_status()
            logger.info("réconciliation parc — group_id=%s AJOUT membre=%s", group_id, oid)
        for oid in a_retirer:
            retrait = client.delete(
                f"{GRAPH_BASE}/groups/{group_id}/members/{oid}/$ref",
                headers=_entetes(),
            )
            retrait.raise_for_status()
            logger.info("réconciliation parc — group_id=%s RETRAIT membre=%s", group_id, oid)

    return {
        "group_id": group_id,
        "ajoutes": a_ajouter,
        "retires": a_retirer,
        "inchanges": inchanges,
        "etat_final": sorted(attendus),
    }


def _groupes_lisibles() -> set[str]:
    """Union des listes blanches périmètre + parc (les seuls groupes que ce serveur connaît)."""
    perim = os.environ.get(ENV_GROUPES_PERIMETRE_AUTORISES, "").strip()
    parc = os.environ.get(ENV_GROUPES_PARC_AUTORISES, "").strip()
    lisibles: set[str] = set()
    for csv in (perim, parc):
        lisibles |= {g.strip() for g in csv.split(",") if g.strip()}
    return lisibles


@mcp.tool()
@_journal_appel("lire_annuaire")
def lire_annuaire(
    ctx: Context, upn: str = "", group_id: str = ""
) -> dict[str, Any]:
    """Lit l'annuaire Entra en LECTURE SEULE : résout un utilisateur par UPN et/ou liste les membres d'un groupe.

    Outil de RÉSOLUTION pour l'onboarding (T-0007) et l'épreuve : Claude Code résout les objectId
    et l'appartenance réelle AVANT tout appel mutant, au lieu de figer des GUID de mémoire (interdit
    par la doctrine §2) ou de subir l'absence de dry-run des réconciliateurs.

    LECTURE SEULE STRICTE : n'écrit jamais, ne réconcilie rien.

    Bornage (moindre privilège, cohérent avec les réconciliateurs) :
    - `upn` : résolu sur les utilisateurs du tenant (GET /users/{upn}).
    - `group_id` : DOIT être dans l'union des listes blanches périmètre ∪ parc, sinon PermissionError.

    Au moins l'un des deux paramètres doit être fourni.

    Args:
        upn: userPrincipalName (email) à résoudre en objectId. Optionnel.
        group_id: objectId d'un groupe autorisé dont lister les membres. Optionnel, borné liste blanche.

    Returns:
        dict avec, selon les paramètres :
          - "utilisateur": {"id", "displayName", "userPrincipalName"} si upn fourni et trouvé ;
          - "membres": [objectId, ...] si group_id fourni (et autorisé).

    Raises:
        PermissionError: group_id hors liste blanche, ou appelant non validé.
        ValueError: aucun paramètre fourni.
    """
    _verifier_appelant(ctx)

    if not upn and not group_id:
        raise ValueError("Fournir au moins `upn` (résolution utilisateur) ou `group_id` (membres).")

    resultat: dict[str, Any] = {}

    with httpx.Client(timeout=30) as client:
        if upn:
            url = f"{GRAPH_BASE}/users/{upn}"
            params = {"$select": "id,displayName,userPrincipalName"}
            reponse = client.get(url, headers=_entetes(), params=params)
            reponse.raise_for_status()
            corps = reponse.json()
            resultat["utilisateur"] = {
                "id": corps.get("id"),
                "displayName": corps.get("displayName"),
                "userPrincipalName": corps.get("userPrincipalName"),
            }

        if group_id:
            lisibles = _groupes_lisibles()
            if not lisibles:
                raise ConfigManquante(
                    "Aucune liste blanche configurée : "
                    f"{ENV_GROUPES_PERIMETRE_AUTORISES} et {ENV_GROUPES_PARC_AUTORISES} absentes."
                )
            if group_id not in lisibles:
                logger.warning("lecture refusée — group_id=%s hors liste blanche lecture", group_id)
                raise PermissionError(
                    "Cible non autorisée : ce group_id n'est ni un groupe de périmètre ni un "
                    "groupe de parc déclaré. Aucune lecture effectuée."
                )
            resultat["membres"] = sorted(_lire_membres_groupe(client, group_id))

    return resultat


@mcp.tool()
@_journal_appel("notifier_canal")
def notifier_canal(ctx: Context, titre: str, corps: str, reference: str = "") -> dict[str, Any]:
    """Dépose une notification d'équipe dans la liste « Notifications » (relais vers Teams).

    Type d'action `notifier_equipe` (table-des-crans : cran NOTIFIE) — l'agent agit, le
    gardien et l'équipe sont informés. Le message part dans le canal Teams « Allia
    Consulting — vie interne » via un flux M365 (déclencheur : élément créé dans cette
    liste), PAS par un appel Graph d'envoi de canal : Graph ne supporte l'envoi de message
    de canal qu'en permissions déléguées (app-only = migration uniquement, fait vérifié le
    05/07/2026). Le relais par liste conserve le zéro secret et n'ajoute AUCUNE permission
    Graph (Sites.Selected write couvre déjà le site).

    La liste cible est fixée par GRAPH_NOTIFICATIONS_LIST_ID côté serveur. Cette fonction
    n'accepte AUCUN identifiant de liste ni de canal de l'appelant : impossible de notifier
    ailleurs que dans le canal câblé par le gardien. Cet outil ne sait QUE notifier —
    il n'élargit aucun droit existant.

    Args:
        titre: objet court de la notification (1 à 255 caractères).
        corps: contenu du message (1 à 4000 caractères).
        reference: rattachement facultatif (ex. code mission, id de PR, id d'élément en
            Zone-de-proposition) — 255 caractères maximum.

    Returns:
        Un dict {"created_id": "...", "titre": "..."} décrivant la notification déposée.

    Raises:
        ValueError: titre/corps vides ou hors bornes.
        ConfigManquante: GRAPH_NOTIFICATIONS_LIST_ID absente.
    """
    _verifier_appelant(ctx)
    if not isinstance(titre, str) or not titre.strip():
        raise ValueError("`titre` doit être une chaîne non vide.")
    if not isinstance(corps, str) or not corps.strip():
        raise ValueError("`corps` doit être une chaîne non vide.")
    if not isinstance(reference, str):
        raise ValueError("`reference` doit être une chaîne (éventuellement vide).")
    titre = titre.strip()
    corps = corps.strip()
    reference = reference.strip()
    if len(titre) > 255:
        raise ValueError("`titre` dépasse 255 caractères (limite de la colonne Title).")
    if len(corps) > 4000:
        raise ValueError("`corps` dépasse 4000 caractères — raccourcir ou pointer une référence.")
    if len(reference) > 255:
        raise ValueError("`reference` dépasse 255 caractères.")

    cfg_notif = _config_notifications()
    cfg = _config()
    # Cible d'écriture NON paramétrable par l'appelant : la liste Notifications, et elle seule.
    url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{cfg_notif['notifications_list_id']}/items"
    champs: dict[str, Any] = {"Title": titre, "Corps": corps}
    if reference:
        champs["Reference"] = reference
    with httpx.Client(timeout=30) as client:
        reponse = client.post(
            url,
            headers={**_entetes(), "Content-Type": "application/json"},
            json={"fields": champs},
        )
        reponse.raise_for_status()
        corps_reponse = reponse.json()
    logger.info("notification déposée — id=%s titre=%s", corps_reponse.get("id"), titre)
    return {"created_id": corps_reponse.get("id"), "titre": titre}


@mcp.tool()
@_journal_appel("workbook_lire_table")
def workbook_lire_table(ctx: Context, drive_id: str, item_id: str, table: str) -> dict[str, Any]:
    """LIT (lecture seule) les lignes d'une table nommée d'un classeur Excel, via l'API Workbook.

    GET /drives/{drive_id}/items/{item_id}/workbook/tables/{table}/rows

    LECTURE NON BORNÉE (à la différence des primitives d'écriture) : `drive_id` et `item_id` sont
    fournis par l'appelant. Cette primitive peut donc lire aussi bien un classeur de SAISIE
    (Management/Gestion), un gabarit de pilotage (« 06 - Gabarit ERP ») que le référentiel de coûts —
    la cible n'est PAS bornée. La lecture ne modifie rien ; seules les écritures sont bornées au
    domicile gabarit figé côté serveur (workbook_ajouter_lignes / workbook_maj_ligne).

    Adressage Workbook par POSITION (Graph REST v1.0) : les lignes sont retournées dans l'ordre de la
    table ; `workbook_maj_ligne` cible ensuite par index (itemAt).

    Args:
        drive_id: drive hébergeant le classeur (lecture non bornée — libre).
        item_id: driveItem du classeur .xlsx à lire (lecture non bornée — libre).
        table: nom (ou id) de la table nommée dans le classeur.

    Returns:
        dict {"table", "lignes": [[...valeurs...], ...], "count"} — valeurs brutes ligne à ligne.
    """
    _verifier_appelant(ctx)
    url = f"{GRAPH_BASE}/drives/{drive_id}/items/{item_id}/workbook/tables/{table}/rows"
    with httpx.Client(timeout=30) as client_http:
        reponse = client_http.get(url, headers=_entetes())
        reponse.raise_for_status()
        corps = reponse.json()
    lignes = [row["values"][0] for row in corps.get("value", [])]
    return {"table": table, "lignes": lignes, "count": len(lignes)}


@mcp.tool()
@_journal_appel("workbook_ajouter_lignes")
def workbook_ajouter_lignes(
    ctx: Context, code_mission: str, table: str, lignes: list[list]
) -> dict[str, Any]:
    """AJOUTE des lignes à une table nommée du GABARIT d'une mission (écriture BORNÉE par construction).

    POST /drives/{GABARIT_DRIVE_ID}/items/{item}/workbook/tables/{table}/rows  (index:null = append)

    ÉCRITURE BORNÉE : l'appelant ne fournit AUCUN drive_id / item_id / folder_id. La cible est le
    `gabarit-<code_mission>.xlsx` du dossier FIGÉ « 06 - Gabarit ERP » (GRAPH_GABARIT_*), résolu côté
    serveur par `_resoudre_item_gabarit`. Il est structurellement impossible d'écrire ailleurs.

    Primitive BÊTE (décision S34) : elle ajoute des lignes, rien d'autre. La régénération complète
    d'un gabarit (cran auto « reconcilier_gabarit_pilotage ») est orchestrée par le SKILL consommateur
    à venir, PAS par un outil MCP composite.

    Args:
        code_mission: code de la mission (assaini côté serveur ; sélectionne gabarit-<code>.xlsx).
        table: nom (ou id) de la table nommée cible dans le gabarit.
        lignes: liste NON VIDE de lignes, chaque ligne étant une liste de valeurs de cellules.

    Returns:
        dict {"code_mission", "table", "ajoutees": n}.

    Raises:
        ValueError: code_mission invalide, ou `lignes` n'est pas une liste non vide de listes.
        FileNotFoundError: aucun gabarit pour ce code_mission dans « 06 - Gabarit ERP ».
        ConfigManquante: GRAPH_GABARIT_* absentes.
    """
    _verifier_appelant(ctx)
    if not isinstance(lignes, list) or not lignes or any(not isinstance(l, list) for l in lignes):
        raise ValueError(
            "`lignes` doit être une liste NON VIDE de listes (une liste de valeurs par ligne)."
        )
    cfg = _config_gabarit()
    drive_id = cfg["gabarit_drive_id"]
    with httpx.Client(timeout=30) as client_http:
        item_id = _resoudre_item_gabarit(client_http, code_mission)
        url = f"{GRAPH_BASE}/drives/{drive_id}/items/{item_id}/workbook/tables/{table}/rows"
        reponse = client_http.post(
            url,
            headers={**_entetes(), "Content-Type": "application/json"},
            json={"index": None, "values": lignes},
        )
        reponse.raise_for_status()
    return {"code_mission": code_mission.strip(), "table": table, "ajoutees": len(lignes)}


@mcp.tool()
@_journal_appel("workbook_maj_ligne")
def workbook_maj_ligne(
    ctx: Context, code_mission: str, table: str, index: int, valeurs: list
) -> dict[str, Any]:
    """MET À JOUR une ligne par POSITION dans une table du GABARIT d'une mission (écriture BORNÉE).

    PATCH /drives/{GABARIT_DRIVE_ID}/items/{item}/workbook/tables/{table}/rows/itemAt(index={index})

    ÉCRITURE BORNÉE : aucun drive_id / item_id / folder_id exposé — la cible est le
    `gabarit-<code_mission>.xlsx` de « 06 - Gabarit ERP », résolu côté serveur. Adressage par POSITION
    (Graph REST v1.0 : itemAt(index=...)), 0-based ; l'ordre est celui de workbook_lire_table.

    Args:
        code_mission: code de la mission (assaini côté serveur).
        table: nom (ou id) de la table nommée cible.
        index: index 0-based de la ligne à mettre à jour (>= 0).
        valeurs: liste NON VIDE des valeurs de cellules de la ligne.

    Returns:
        dict {"code_mission", "table", "index", "maj": True}.

    Raises:
        ValueError: code_mission invalide, index négatif/non entier, ou `valeurs` vide.
        FileNotFoundError: aucun gabarit pour ce code_mission dans « 06 - Gabarit ERP ».
        ConfigManquante: GRAPH_GABARIT_* absentes.
    """
    _verifier_appelant(ctx)
    # bool est un sous-type de int en Python : True/False sont refusés explicitement.
    if not isinstance(index, int) or isinstance(index, bool) or index < 0:
        raise ValueError("`index` doit être un entier >= 0 (adressage Workbook par position, 0-based).")
    if not isinstance(valeurs, list) or not valeurs:
        raise ValueError("`valeurs` doit être une liste non vide de valeurs de cellules.")
    cfg = _config_gabarit()
    drive_id = cfg["gabarit_drive_id"]
    with httpx.Client(timeout=30) as client_http:
        item_id = _resoudre_item_gabarit(client_http, code_mission)
        url = (
            f"{GRAPH_BASE}/drives/{drive_id}/items/{item_id}"
            f"/workbook/tables/{table}/rows/itemAt(index={index})"
        )
        reponse = client_http.patch(
            url,
            headers={**_entetes(), "Content-Type": "application/json"},
            json={"values": [valeurs]},
        )
        reponse.raise_for_status()
    return {"code_mission": code_mission.strip(), "table": table, "index": index, "maj": True}


@mcp.tool()
@_journal_appel("workbook_archiver_gabarit")
def workbook_archiver_gabarit(ctx: Context, code_mission: str) -> dict[str, Any]:
    """ARCHIVE le gabarit courant d'une mission dans « 00 - Old » avant régénération (copie horodatée).

    POST /drives/{GABARIT_DRIVE_ID}/items/{item}/copy → « 00 - Old » (GRAPH_GABARIT_OLD_FOLDER_ID)

    Écriture BORNÉE : source = `gabarit-<code_mission>.xlsx` de « 06 - Gabarit ERP » résolu côté
    serveur ; destination = dossier « 00 - Old » figé (GRAPH_GABARIT_OLD_FOLDER_ID). L'appelant ne
    choisit ni la source ni la destination. Réversible sans perte : la version précédente est conservée
    sous un nom horodaté avant toute régénération.

    NB : le cran auto « reconcilier_gabarit_pilotage » (régénération complète : archiver puis
    réécrire) est porté par le SKILL consommateur à venir, PAS par un outil MCP composite — cette
    primitive reste BÊTE (décision S34) : elle archive, rien d'autre.

    Graph /copy est ASYNCHRONE : la réponse est un 202 Accepted + en-tête Location (URL de suivi) ;
    cette primitive ne bloque PAS sur l'achèvement de la copie.

    Args:
        code_mission: code de la mission (assaini côté serveur ; sélectionne gabarit-<code>.xlsx).

    Returns:
        dict {"code_mission", "nom_archive", "accepted": bool, "emplacement": <Location|None>}.

    Raises:
        ValueError: code_mission invalide.
        FileNotFoundError: aucun gabarit pour ce code_mission dans « 06 - Gabarit ERP ».
        ConfigManquante: GRAPH_GABARIT_* absentes.
    """
    _verifier_appelant(ctx)
    cfg = _config_gabarit()
    drive_id = cfg["gabarit_drive_id"]
    old_folder_id = cfg["gabarit_old_folder_id"]
    horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")  # UTC compact
    with httpx.Client(timeout=30) as client_http:
        item_id = _resoudre_item_gabarit(client_http, code_mission)
        nom_archive = f"gabarit-{code_mission.strip()}-{horodatage}.xlsx"
        url = f"{GRAPH_BASE}/drives/{drive_id}/items/{item_id}/copy"
        reponse = client_http.post(
            url,
            headers={**_entetes(), "Content-Type": "application/json"},
            json={
                "parentReference": {"driveId": drive_id, "id": old_folder_id},
                "name": nom_archive,
            },
        )
        reponse.raise_for_status()
    return {
        "code_mission": code_mission.strip(),
        "nom_archive": nom_archive,
        "accepted": reponse.status_code == 202,
        "emplacement": reponse.headers.get("Location"),
    }


@mcp.tool()
@_journal_appel("workbook_instancier_gabarit")
def workbook_instancier_gabarit(ctx: Context, code_mission: str) -> dict[str, Any]:
    """INSTANCIE le gabarit d'une mission par COPIE de la souche vierge canon (écriture BORNÉE, fail-closed).

    POST /drives/{GABARIT_DRIVE_ID}/items/{item_vierge}/copy → « 06 - Gabarit ERP » (GRAPH_GABARIT_FOLDER_ID)

    Écriture BORNÉE par construction : source = `gabarit-pilotage-mission.xlsx` (souche vierge unique,
    GABARIT_VIERGE_NOM) à la racine de « 06 - Gabarit ERP » résolue côté serveur ; destination = le MÊME
    dossier, nom `gabarit-<code_mission>.xlsx`. L'appelant ne fournit AUCUN drive_id / item_id /
    folder_id — seulement `code_mission`, assaini par la MÊME routine (`_assainir_code_mission`) que les
    autres primitives gabarit. Il est structurellement impossible d'instancier ailleurs.

    CRÉATION PURE, FAIL-CLOSED : `@microsoft.graph.conflictBehavior=fail`. Si un `gabarit-<code>.xlsx`
    existe déjà, Graph refuse la copie (409) et cette primitive lève FileExistsError — l'instanciation
    ne détruit ni n'écrase JAMAIS un gabarit en place. Réversible par simple suppression de la copie.

    NB : l'instanciation SYSTÉMATIQUE d'un gabarit manquant (décision gardien 14/07/2026 : plus jamais
    un geste humain) est orchestrée par le SKILL consommateur `consolidation-pilotage`, PAS par un outil
    composite — cette primitive reste BÊTE : elle instancie, rien d'autre.

    Graph /copy est ASYNCHRONE : la réponse est un 202 Accepted + en-tête Location (URL de suivi) ;
    cette primitive ne bloque PAS sur l'achèvement de la copie (le skill poll le Location).

    Args:
        code_mission: code de la mission (assaini côté serveur ; compose gabarit-<code>.xlsx).

    Returns:
        dict {"code_mission", "nom_gabarit", "accepted": bool, "emplacement": <Location|None>}.

    Raises:
        ValueError: code_mission invalide.
        FileExistsError: un gabarit existe déjà pour ce code_mission (conflictBehavior=fail → 409).
        FileNotFoundError: souche vierge canon introuvable dans « 06 - Gabarit ERP ».
        ConfigManquante: GRAPH_GABARIT_* absentes.
    """
    _verifier_appelant(ctx)
    code = _assainir_code_mission(code_mission)
    cfg = _config_gabarit()
    drive_id = cfg["gabarit_drive_id"]
    folder_id = cfg["gabarit_folder_id"]
    nom_gabarit = f"gabarit-{code}.xlsx"
    with httpx.Client(timeout=30) as client_http:
        # Source = souche vierge canon, résolue par CHEMIN sous le dossier gabarit figé (jamais libre).
        url_source = f"{GRAPH_BASE}/drives/{drive_id}/items/{folder_id}:/{GABARIT_VIERGE_NOM}"
        reponse_source = client_http.get(url_source, headers=_entetes())
        if reponse_source.status_code == 404:
            raise FileNotFoundError(
                f"souche vierge canon introuvable dans « 06 - Gabarit ERP » "
                f"(fichier attendu : {GABARIT_VIERGE_NOM}). Souche unique à poser au runbook gardien."
            )
        reponse_source.raise_for_status()
        item_vierge = reponse_source.json()["id"]
        # Copie vers le MÊME dossier, nom gabarit-<code>.xlsx, FAIL-CLOSED (jamais d'écrasement).
        url = f"{GRAPH_BASE}/drives/{drive_id}/items/{item_vierge}/copy"
        reponse = client_http.post(
            url,
            headers={**_entetes(), "Content-Type": "application/json"},
            json={
                "parentReference": {"driveId": drive_id, "id": folder_id},
                "name": nom_gabarit,
                "@microsoft.graph.conflictBehavior": "fail",
            },
        )
        # Collision : un gabarit de même nom existe déjà — NE PAS réessayer, NE PAS écraser.
        if reponse.status_code == 409:
            raise FileExistsError(
                f"un gabarit existe déjà pour {code} dans « 06 - Gabarit ERP » ({nom_gabarit}) : "
                "instanciation refusée (collision=fail). Aucun écrasement, aucune fusion."
            )
        reponse.raise_for_status()
    return {
        "code_mission": code,
        "nom_gabarit": nom_gabarit,
        "accepted": reponse.status_code == 202,
        "emplacement": reponse.headers.get("Location"),
    }


if __name__ == "__main__":
    # Transport HTTP STREAMABLE (endpoint /mcp par défaut du SDK ; /healthz pour les sondes).
    # run() NU : ce SDK n'accepte pas host/port dans run() (TypeError) — ils sont portés par le
    # constructeur FastMCP(...) ci-dessus. Aucune connexion réseau tant qu'un outil n'est pas appelé.
    mcp.run(transport="streamable-http")
