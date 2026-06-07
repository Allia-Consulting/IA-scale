# Serveur MCP — connecteur Microsoft Graph (Allia)

> **Statut** : code de candidat — **ne se connecte à rien** tant que le gardien ne l'a pas configuré ni branché.
> **Rattachement** : chantier `backlog/chantiers/T-0002b.yaml` · couture M365 `contrats/socle/modele-donnees.md` (§2 bis, §3, §4).
> **Périmètre de ce livrable** : le code + ce README. Rien d'autre (voir « Hors de ce livrable »).

## Ce que c'est

Un petit serveur [Model Context Protocol](https://modelcontextprotocol.io) qui donne à un agent **deux** opérations sur Microsoft Graph, et deux seulement :

| Outil | Verbe | Effet |
|---|---|---|
| `list_items(list_id, top=50)` | **lecture** | `GET /sites/{site}/lists/{list}/items?$expand=fields` — lit les éléments d'une liste SharePoint du site AlliaConsuling. |
| `create_list_item(fields)` | **écriture** | `POST /sites/{site}/lists/{PROPOSITION}/items` — crée un élément **uniquement** dans la liste « Zone-de-proposition ». |

## Le garde-fou structurel : on n'écrit que dans la zone de proposition

« Le dérivé n'est jamais le saisi » (doctrine §2 ; `modele-donnees.md` §3). Ce principe est **inscrit dans le code**, pas seulement ici :

- la liste d'écriture est **fixée côté serveur** par `GRAPH_PROPOSITION_LIST_ID` ;
- `create_list_item` **n'accepte aucun identifiant de liste** de l'appelant.

Il est donc *structurellement* impossible d'écrire dans une source : l'écriture ne peut viser que la zone de proposition. `list_items` (lecture) reste libre de viser n'importe quelle liste du site, selon le cran applicable.

## Configuration (par le gardien, à l'exécution — aucun secret dans le dépôt)

Le serveur lit sa configuration **dans l'environnement**, au moment d'un appel d'outil (jamais à l'import). Variables attendues (voir `.env.example` ; copier en `.env`, qui est ignoré par git) :

| Variable | Rôle |
|---|---|
| `GRAPH_TENANT_ID` | Tenant Entra ID de la firme. |
| `GRAPH_CLIENT_ID` | App registration au moindre privilège (`Sites.Selected`). |
| `GRAPH_CLIENT_SECRET` | Secret client de l'app registration. **Injecté à l'exécution, jamais commité.** |
| `GRAPH_SITE_ID` | Identifiant Graph du site AlliaConsuling (`host,siteGuid,webGuid`). |
| `GRAPH_PROPOSITION_LIST_ID` | Identifiant de la liste « Zone-de-proposition » — **seule cible d'écriture**. |

Aucune de ces valeurs n'est fournie dans le dépôt. Le code échoue avec un message clair (`ConfigManquante`) si une variable manque — il ne devine ni ne stocke rien.

## Modèle d'autorisation : `Sites.Selected` (moindre privilège)

Le code attend un **jeton applicatif** (flux `client_credentials`, scope `https://graph.microsoft.com/.default`) porté par une app registration ayant la permission **application `Sites.Selected`**, à qui le gardien a accordé le rôle **`write` sur le seul site AlliaConsuling** :

```http
POST https://graph.microsoft.com/v1.0/sites/{GRAPH_SITE_ID}/permissions
{ "roles": ["write"], "grantedToIdentities": [ { "application": { "id": "<CLIENT_ID>", "displayName": "<APP>" } } ] }
```

Ainsi l'app ne peut toucher qu'un site, et ce serveur n'y écrit qu'une liste. La création de l'app registration, le consentement admin, l'octroi du rôle et le stockage du secret sont le **runbook du gardien** — **non faits ici** (plan §2 ; garde-fous `CLAUDE.md`).

## Installation et exécution (quand le gardien décide de le brancher)

```bash
cd outils/mcp-graph
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
# renseigner .env à partir de .env.example, puis :
python server.py            # transport stdio — lancé par le client MCP
```

Branchement à un client MCP (ex. Claude Code) : déclarer un serveur stdio dont la commande est `python /chemin/outils/mcp-graph/server.py`, en lui passant l'environnement ci-dessus. Tant que ce n'est pas fait, **le serveur dort**.

## Hors de ce livrable (signalé, non fait)

- **Mise à jour de `modele-donnees.md`** avec les endpoints/identifiants réels : viendra **après** le déploiement (étape ultérieure de T-0002b), pas ici.
- **App registration, consentement, octroi `write`, secret** : runbook du gardien.
- **Journalisation M365** sur `Ressources-RH` / `CVs` (chantier `T-0003`) : prérequis à tout accès agent sur ces données, côté tenant.
- **Aucune connexion réelle ni déploiement** n'a été effectué : ce code est inerte jusqu'à configuration.
