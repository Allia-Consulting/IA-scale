"""Serveur MCP — connecteur Microsoft Graph (lecture liste + écriture zone de proposition).

Allia · couture M365 (voir `contrats/socle/modele-donnees.md`). Chantier `backlog/chantiers/T-0002b.yaml`
(sous-tâche `T-0002b-1` : transport stdio → HTTP streamable + identité managée).

Ce serveur expose SIX opérations à un agent, via le Model Context Protocol (transport HTTP streamable) :

    - list_items                  : LIT les éléments d'une liste SharePoint (lecture seule).
    - create_list_item            : CRÉE un élément UNIQUEMENT dans la « Zone-de-proposition ».
    - televerser_brouillon_offre  : DÉPOSE un brouillon .docx UNIQUEMENT dans « 00 - Proposition en cours ».
    - reconcilier_groupe_perimetre : RÉCONCILIE l'appartenance d'un groupe de périmètre (delta idempotent), cible bornée par liste blanche.
    - reconcilier_groupe_parc      : RÉCONCILIE l'appartenance du groupe de PARC d'enrôlement (delta idempotent), cible bornée par liste blanche DÉDIÉE.
    - lire_annuaire               : LIT l'annuaire Entra (lecture seule) — résout un UPN en objectId et/ou liste les membres d'un groupe borné aux listes blanches.

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
import json
import logging
import os
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

# Variables d'environnement attendues (injectées à l'exécution — jamais ici, aucun secret).
ENV_AZURE_ENV = "AZURE_ENV"                # local | prod (défaut prod) — pilote le credential
ENV_AZURE_CLIENT_ID = "AZURE_CLIENT_ID"    # clientId de l'identité managée (défaut: MANAGED_IDENTITY_CLIENT_ID)
ENV_SITE_ID = "GRAPH_SITE_ID"
ENV_PROPOSITION_LIST_ID = "GRAPH_PROPOSITION_LIST_ID"
ENV_BROUILLON_DRIVE_ID = "GRAPH_BROUILLON_DRIVE_ID"      # bibliothèque Documents (cible figée du dépôt de brouillon)
ENV_BROUILLON_FOLDER_ID = "GRAPH_BROUILLON_FOLDER_ID"    # dossier « 00 - Proposition en cours » (seule cible de dépôt)
ENV_GROUPES_PERIMETRE_AUTORISES = "GRAPH_GROUPES_PERIMETRE_AUTORISES"  # CSV d'objectId des groupes de périmètre gérables (liste blanche figée côté serveur)
ENV_GROUPES_PARC_AUTORISES = "GRAPH_GROUPES_PARC_AUTORISES"  # CSV d'objectId des groupes de PARC gérables (liste blanche figée côté serveur, dédiée — séparée du périmètre)

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


if __name__ == "__main__":
    # Transport HTTP STREAMABLE (endpoint /mcp par défaut du SDK ; /healthz pour les sondes).
    # run() NU : ce SDK n'accepte pas host/port dans run() (TypeError) — ils sont portés par le
    # constructeur FastMCP(...) ci-dessus. Aucune connexion réseau tant qu'un outil n'est pas appelé.
    mcp.run(transport="streamable-http")
