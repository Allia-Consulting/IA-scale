# Serveur MCP — connecteur Microsoft Graph (Allia)

> **Statut** : code de candidat — **ne se connecte à rien** tant qu'il n'est ni configuré ni branché.
> **Rattachement** : chantier `backlog/chantiers/T-0002b.yaml` (sous-tâche `T-0002b-1` : transport stdio → HTTP streamable + identité managée) · couture M365 `contrats/socle/modele-donnees.md` (§2 bis, §3, §4).
> **Périmètre de ce livrable** : le code + ce README + `.env.example`. Rien d'autre (voir « Hors de ce livrable »).

## Ce que c'est

Un serveur [Model Context Protocol](https://modelcontextprotocol.io), exposé en **HTTP streamable**, qui donne à un agent **trois** opérations sur Microsoft Graph, et trois seulement :

| Outil | Verbe | Effet |
|---|---|---|
| `list_items(list_id, top=50)` | **lecture** | `GET /sites/{site}/lists/{list}/items?$expand=fields` — lit les éléments d'une liste SharePoint du site AlliaConsuling. |
| `create_list_item(fields)` | **écriture** | `POST /sites/{site}/lists/{PROPOSITION}/items` — crée un élément **uniquement** dans la liste « Zone-de-proposition ». |
| `televerser_brouillon_offre(nom_fichier, contenu_base64, candidat_id)` | **écriture fichier** | `PUT .../drives/{BROUILLON_DRIVE}/.../{nom}.docx:/content` — dépose un **brouillon .docx** dans le dossier **« 00 - Proposition en cours » FIGÉ**, jamais ailleurs ; collision = **fail**. **Code en PR B (`T-0017-a`).** |

## Transport HTTP streamable et endpoint de santé

- **Transport** : HTTP **streamable** — endpoint MCP `/mcp` (sous-chemin par défaut du SDK). Le serveur est instancié **stateless** (`FastMCP(..., stateless_http=True)`) : pas de session persistante côté serveur, exigence de l'hébergement Azure Container Apps (déploiement = chantier `T-0002b-3`).
- **Santé** : endpoint **séparé** `/healthz` — `GET` → `200 {"status": "ok"}`, **liveness pur** (ne touche pas Graph, n'acquiert aucun jeton). Les sondes de l'hébergement visent `/healthz`, **jamais** `/mcp` (qui attend du JSON-RPC POST).

## Le garde-fou structurel : on n'écrit que dans la zone de proposition

« Le dérivé n'est jamais le saisi » (doctrine §2 ; `modele-donnees.md` §3). Ce principe est **inscrit dans le code**, pas seulement ici :

- la liste d'écriture est **fixée côté serveur** par `GRAPH_PROPOSITION_LIST_ID` ;
- `create_list_item` **n'accepte aucun identifiant de liste** de l'appelant.

Il est donc *structurellement* impossible d'écrire dans une source : l'écriture ne peut viser que la zone de proposition. `list_items` (lecture) reste libre de viser n'importe quelle liste du site, selon le cran applicable.

## Le garde-fou structurel (bis) : le brouillon ne se dépose que dans « 00 - Proposition en cours »

`televerser_brouillon_offre` suit le **même** principe que `create_list_item` : la cible n'est **jamais** choisie par l'appelant, elle est **figée côté serveur** par deux variables d'environnement — `GRAPH_BROUILLON_DRIVE_ID` (la bibliothèque `Documents`) et `GRAPH_BROUILLON_FOLDER_ID` (le dossier « 00 - Proposition en cours »). L'outil :

- dépose **uniquement** dans « 00 - Proposition en cours » — **jamais** au niveau « 01 - Proposition d'embauche », domicile des offres **SIGNÉES** ;
- **force** l'extension `.docx` et **assainit** le nom de fichier (refus de `/`, `\`, `..`) ;
- **échoue** si un fichier de même nom existe déjà (**collision = fail**) : l'agent n'écrase jamais un brouillon ; la régénération est un geste humain de retrait (cohérent avec `supprimer_definitivement_des_donnees` — proscrit).

Cran de l'action : **auto** (`table-des-crans.yaml` : `televerser_brouillon_offre_zone_travail`) — brouillon non émis, réversible, interne, local. L'émission de l'offre reste **proscrite et humaine**. **Le code de cet outil arrive en PR B (chantier `T-0017-a`)** ; la présente PR fige l'architecture dans le canon.

## Authentification de SORTIE Graph : identité managée — ZÉRO secret

L'authentification vers Microsoft Graph passe par une **identité managée** (managed identity), **jamais** par un secret applicatif. Le credential est choisi à l'exécution selon `AZURE_ENV` :

- **`prod`** (défaut sûr) : `ManagedIdentityCredential(client_id=AZURE_CLIENT_ID)` — l'identité **user-assigned** `id-allia-mcp-graph`. Type **spécifique** (et non `DefaultAzureCredential` nu) : on évite qu'une chaîne de fallback ramasse silencieusement une autre identité (moindre privilège strict).
- **`local`** : `DefaultAzureCredential()` — découvre `az login` / VS Code (l'identité managée n'existe pas hors d'Azure).

Le jeton est acquis sur le scope `https://graph.microsoft.com/.default` et aucun autre. **Aucun secret Graph n'est lu, stocké ni injecté.** Les droits effectifs sont bornés en amont par l'octroi `Sites.Selected` + `write` sur le **seul** site AlliaConsuling, accordé à l'identité managée (runbook du gardien `T-0002a-bis`, fait) — **non fait ici**.

> **Deux frontières à ne pas confondre.** Ce qui précède concerne la **sortie** (le service appelle Graph) : zéro secret. **Qui a le droit d'appeler le service** (`/mcp`) est une **autre** frontière — l'authentification d'**entrée** (Easy Auth de l'hébergement), portée par le chantier `T-0002b-4`, **hors de ce code**. Ce connecteur Graph ne reprend, lui, **aucun** secret.

## Configuration (à l'exécution — aucun secret dans le dépôt)

Le serveur lit sa configuration **dans l'environnement**, au moment d'un appel d'outil (jamais à l'import). Variables attendues (voir `.env.example` ; copier en `.env`, ignoré par git) :

| Variable | Rôle |
|---|---|
| `AZURE_ENV` | `local` \| `prod` — pilote le choix du credential (défaut `prod` si absente). |
| `AZURE_CLIENT_ID` | clientId **public** de l'identité managée user-assigned `id-allia-mcp-graph` (lu en prod ; défaut intégré au code si absent). **Pas un secret.** |
| `GRAPH_SITE_ID` | Identifiant Graph du site AlliaConsuling (`host,siteGuid,webGuid`). |
| `GRAPH_PROPOSITION_LIST_ID` | Identifiant de la liste « Zone-de-proposition » — **seule cible d'écriture** de liste. |
| `GRAPH_BROUILLON_DRIVE_ID` | Identifiant de la bibliothèque `Documents` (drive) — **cible figée** du dépôt de brouillon (`televerser_brouillon_offre`). Consommée par le code de `T-0017-a` (PR B). |
| `GRAPH_BROUILLON_FOLDER_ID` | Identifiant du dossier « 00 - Proposition en cours » — **seule cible de dépôt** du brouillon, jamais le niveau « 01 ». Consommée par le code de `T-0017-a` (PR B). |

Le code échoue avec un message clair (`ConfigManquante`) si `GRAPH_SITE_ID` ou `GRAPH_PROPOSITION_LIST_ID` manque — il ne devine ni ne stocke rien. **Aucun secret n'apparaît dans cette liste** : l'auth Graph est portée par l'identité managée.

## Installation et exécution (quand le service est branché)

```bash
cd outils/mcp-graph
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
# renseigner .env à partir de .env.example, puis :
python server.py            # transport HTTP streamable (endpoint /mcp ; /healthz pour les sondes)
```

En local hors Azure, poser `AZURE_ENV=local` (le credential découvre `az login`). En production, l'hébergement (Container Apps, `T-0002b-3`) fournit l'identité managée et `AZURE_ENV=prod`. Tant que la configuration M365 n'est pas renseignée, **le serveur dort** (aucun appel réseau à l'import).

## Branchement d'un poste (Claude Code)

Le branchement d'un poste suit le **modèle des identités appelantes** (`contrats/socle/identites-et-secrets.md` §2, cas « humain ») : **identité Entra de la personne**, flux **authorization code + PKCE** sur un client **public** — **aucun secret** créé, distribué ni stocké sur le poste. Chantier : `backlog/chantiers/T-0010.yaml` (la part Entra — scope délégué, client public, groupe `grp-mcp-graph-users` — est un **runbook humain**, non couverte ici).

- **Configuration** : le fichier **`.mcp.json` à la racine du dépôt** (scope **project** de Claude Code) porte l'endpoint `/mcp` réel et la configuration OAuth (clientId public, métadonnées Entra, scope `access_as_user`). Il ne contient **aucun secret**.
- **Porte humaine** : au premier lancement, Claude Code **demande l'approbation** du serveur MCP du projet — rien ne se connecte sans ce geste explicite.
- **Flux** : à la connexion, Claude Code ouvre le **navigateur** sur la mire Entra ; la personne s'authentifie avec **son** compte ; l'accès n'est accordé que si elle appartient au groupe `grp-mcp-graph-users` (*assignment required* sur l'enterprise app du service).
- **Faits durcis** (prouvés le 10 juin 2026, trace `T-0010`) — à connaître pour le prochain poste :
  - `oauth.scopes` dans `.mcp.json` est une **CHAÎNE** (scopes multiples séparés par des espaces), jamais un tableau — config invalide = serveur **ignoré** (silencieusement par l'app desktop ; warning explicite au CLI : `/doctor` et bandeau `/mcp`).
  - L'authentification OAuth des serveurs `.mcp.json` projet se fait au **CLI** — l'app **desktop** ne les expose pas (son `/mcp` ouvre le catalogue de connecteurs claude.ai) ; la configuration est partagée entre les deux.
  - Côté Entra, les **redirect URIs** se saisissent en **minuscules strictes** (correspondance sensible à la casse, `AADSTS50011` sur une majuscule) — copier-coller plutôt que retaper.
  - L'accès s'obtient par **ajout au groupe Entra `grp-mcp-graph-users`** — c'est la **porte du gardien** (projection d'une décision promue, `organisation.md` §5), jamais une affectation individuelle.
  - Après **tout changement de membres** du groupe, **ré-authentifier** (`/mcp`) : l'affectation ne prend effet dans le jeton qu'à sa **prochaine émission** (prévoir 2-3 min de propagation d'annuaire). Un groupe **vide** ferme la porte à tout le monde — comportement attendu et constaté.
- **Plan B (même cible zéro-secret, confort moindre)** : si le flux OAuth natif bute contre Entra, un `headersHelper` exécutant `az account get-access-token --resource api://0028a5ff-925a-4700-b703-2f2d0ce728fc` sous l'identité Entra de la personne (`az login`) — voir la note de `T-0010`.

## Hors de ce livrable (signalé, non fait)

- **Conteneurisation** (Dockerfile, image, ACR) : chantier `T-0002b-2`. **Fait ACR Tasks durci** : le scanner de dépendances d'ACR Tasks n'accepte pas le flag `--platform` dans l'instruction `FROM` (« unable to understand line », build avorté avant exécution) ; la plateforme cible se passe à `az acr build --platform linux/amd64` (défaut déjà Linux/AMD64), **pas** dans le `FROM`. Ne pas réintroduire `FROM --platform=...` : cela recasserait le build côté ACR.
- **Déploiement Container App** (min 1 réplica, attache de l'identité managée, ingress) : chantier `T-0002b-3` (runbook).
- **Authentification d'ENTRÉE** (app registration « serveur » Easy Auth + secret serveur ; app registration « client ») : chantiers `T-0002b-4` / `T-0002b-5` (runbooks). C'est une frontière distincte du flux Graph.
- **Mise à jour de `modele-donnees.md`** avec les endpoints/identifiants réels : **après** le déploiement (étape ultérieure de `T-0002b`), pas ici.
- **Journalisation M365** sur `Ressources-RH` / `CVs` (chantier `T-0003`) : prérequis à tout accès agent sur ces données, côté tenant.
- **Aucune connexion réelle ni déploiement** n'a été effectué : ce code est inerte jusqu'à configuration.
