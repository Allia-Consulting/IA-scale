"""Serveur MCP — connecteur Microsoft Graph (lecture liste + écriture zone de proposition).

Allia · couture M365 (voir `contrats/socle/modele-donnees.md`). Chantier `backlog/chantiers/T-0002b.yaml`
(sous-tâche `T-0002b-1` : transport stdio → HTTP streamable + identité managée).

Ce serveur expose DEUX opérations à un agent, via le Model Context Protocol (transport HTTP streamable) :

    - list_items        : LIT les éléments d'une liste SharePoint (lecture seule).
    - create_list_item  : CRÉE un élément UNIQUEMENT dans la « Zone-de-proposition ».

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

    Voie de lecture des claims : X-MS-TOKEN-AAD-ACCESS-TOKEN (JWT brut — pas de mapping de claims,
    indépendant du token store, recommandation cadrage T-0009), fallback X-MS-CLIENT-PRINCIPAL.

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

    # --- Diagnostic (présence uniquement, JAMAIS le contenu) : quel canal porte le token ? ---
    logger.info(
        "headers présents — Authorization=%s X-MS-TOKEN-AAD-ACCESS-TOKEN=%s X-MS-CLIENT-PRINCIPAL=%s",
        bool(request.headers.get("Authorization")),
        bool(request.headers.get("X-MS-TOKEN-AAD-ACCESS-TOKEN")),
        bool(request.headers.get("X-MS-CLIENT-PRINCIPAL")),
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
    }
    manquantes = [k for k, v in valeurs.items() if not v]
    if manquantes:
        noms_env = {
            "site_id": ENV_SITE_ID,
            "proposition_list_id": ENV_PROPOSITION_LIST_ID,
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


if __name__ == "__main__":
    # Transport HTTP STREAMABLE (endpoint /mcp par défaut du SDK ; /healthz pour les sondes).
    # run() NU : ce SDK n'accepte pas host/port dans run() (TypeError) — ils sont portés par le
    # constructeur FastMCP(...) ci-dessus. Aucune connexion réseau tant qu'un outil n'est pas appelé.
    mcp.run(transport="streamable-http")
