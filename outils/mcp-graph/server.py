"""Serveur MCP — connecteur Microsoft Graph (lecture liste + écriture zone de proposition).

Allia · couture M365 (voir `contrats/socle/modele-donnees.md`). Chantier `backlog/chantiers/T-0002.yaml`.

Ce serveur expose DEUX opérations à un agent, via le Model Context Protocol :

    - list_items        : LIT les éléments d'une liste SharePoint (lecture seule).
    - create_list_item  : CRÉE un élément UNIQUEMENT dans la « Zone-de-proposition ».

Garde-fous inscrits dans le code (pas seulement en prose) :

    * « Le dérivé n'est jamais le saisi » (doctrine §2, modele-donnees.md §3) : l'écriture
      ne peut JAMAIS viser une source. La liste d'écriture est fixée côté serveur par la
      variable d'environnement GRAPH_PROPOSITION_LIST_ID ; `create_list_item` n'accepte
      AUCUN identifiant de liste de l'appelant. Il est donc structurellement impossible
      d'écrire ailleurs que dans la zone de proposition.
    * AUCUN secret en dur. Tous les identifiants (tenant, client, secret, site, liste) sont
      injectés à l'exécution par le gardien via l'environnement (voir README et .env.example).
    * Moindre privilège : le code attend un jeton applicatif obtenu par flux client_credentials
      sur une app registration disposant de `Sites.Selected` (application), à qui le gardien
      a accordé le rôle `write` sur le SEUL site AlliaConsuling. La création de l'app
      registration, le consentement admin et le stockage du secret sont le RUNBOOK du gardien
      (plan §2, garde-fous CLAUDE.md) — NON faits ici.

Ce fichier « dort » : il ne se connecte à rien tant que les variables d'environnement ne sont
pas renseignées et qu'un client MCP ne le lance pas. L'import et l'inspection ne déclenchent
aucun appel réseau (la configuration n'est lue qu'au moment d'un appel d'outil).
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from azure.identity import ClientSecretCredential
from mcp.server.fastmcp import FastMCP

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"  # flux application (client_credentials)

# Variables d'environnement attendues (injectées par le gardien à l'exécution — jamais ici).
ENV_TENANT_ID = "GRAPH_TENANT_ID"
ENV_CLIENT_ID = "GRAPH_CLIENT_ID"
ENV_CLIENT_SECRET = "GRAPH_CLIENT_SECRET"  # noqa: S105 — nom de variable, pas un secret
ENV_SITE_ID = "GRAPH_SITE_ID"
ENV_PROPOSITION_LIST_ID = "GRAPH_PROPOSITION_LIST_ID"

mcp = FastMCP("allia-graph-proposition")


class ConfigManquante(RuntimeError):
    """Levée quand une variable d'environnement requise est absente."""


def _config() -> dict[str, str]:
    """Lit la configuration depuis l'environnement. Échoue clairement si une variable manque.

    Appelée au moment de l'exécution d'un outil (jamais à l'import) : le serveur reste
    inerte tant que le gardien ne l'a pas branché.
    """
    valeurs = {
        "tenant_id": os.environ.get(ENV_TENANT_ID, ""),
        "client_id": os.environ.get(ENV_CLIENT_ID, ""),
        "client_secret": os.environ.get(ENV_CLIENT_SECRET, ""),
        "site_id": os.environ.get(ENV_SITE_ID, ""),
        "proposition_list_id": os.environ.get(ENV_PROPOSITION_LIST_ID, ""),
    }
    manquantes = [k for k, v in valeurs.items() if not v]
    if manquantes:
        noms_env = {
            "tenant_id": ENV_TENANT_ID,
            "client_id": ENV_CLIENT_ID,
            "client_secret": ENV_CLIENT_SECRET,
            "site_id": ENV_SITE_ID,
            "proposition_list_id": ENV_PROPOSITION_LIST_ID,
        }
        absentes = ", ".join(noms_env[k] for k in manquantes)
        raise ConfigManquante(
            "Configuration M365 incomplète. Variables d'environnement manquantes : "
            f"{absentes}. Voir outils/mcp-graph/README.md (aucun secret n'est stocké dans le dépôt)."
        )
    return valeurs


def _token(cfg: dict[str, str]) -> str:
    """Obtient un jeton applicatif (client_credentials). ClientSecretCredential met en cache."""
    credential = ClientSecretCredential(
        tenant_id=cfg["tenant_id"],
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
    )
    return credential.get_token(GRAPH_SCOPE).token


def _entetes(cfg: dict[str, str]) -> dict[str, str]:
    return {"Authorization": f"Bearer {_token(cfg)}", "Accept": "application/json"}


@mcp.tool()
def list_items(list_id: str, top: int = 50) -> dict[str, Any]:
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
    cfg = _config()
    url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{list_id}/items"
    params = {"$expand": "fields", "$top": str(max(1, min(top, 200)))}
    with httpx.Client(timeout=30) as client:
        reponse = client.get(url, headers=_entetes(cfg), params=params)
        reponse.raise_for_status()
        corps = reponse.json()
    items = corps.get("value", [])
    return {"items": items, "count": len(items)}


@mcp.tool()
def create_list_item(fields: dict[str, Any]) -> dict[str, Any]:
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
    if not isinstance(fields, dict) or not fields:
        raise ValueError("`fields` doit être un dictionnaire non vide des colonnes à écrire.")

    cfg = _config()
    # Cible d'écriture NON paramétrable par l'appelant : la zone de proposition, et elle seule.
    liste_ecriture = cfg["proposition_list_id"]
    url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{liste_ecriture}/items"
    with httpx.Client(timeout=30) as client:
        reponse = client.post(
            url,
            headers={**_entetes(cfg), "Content-Type": "application/json"},
            json={"fields": fields},
        )
        reponse.raise_for_status()
        corps = reponse.json()
    return {"created_id": corps.get("id"), "fields": corps.get("fields", {})}


if __name__ == "__main__":
    # Transport stdio par défaut (le client MCP — ex. Claude Code — lance ce processus).
    # Aucune connexion n'est tentée tant qu'un outil n'est pas appelé avec une config valide.
    mcp.run()
