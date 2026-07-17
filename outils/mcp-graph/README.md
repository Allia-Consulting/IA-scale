# Serveur MCP — connecteur Microsoft Graph (Allia)

> **Statut** : code de candidat — **ne se connecte à rien** tant qu'il n'est ni configuré ni branché.
> **Rattachement** : chantier `backlog/chantiers/T-0002b.yaml` (sous-tâche `T-0002b-1` : transport stdio → HTTP streamable + identité managée) · couture M365 `contrats/socle/modele-donnees.md` (§2 bis, §3, §4).
> **Périmètre de ce livrable** : le code + ce README + `.env.example`. Rien d'autre (voir « Hors de ce livrable »).

## Ce que c'est

Un serveur [Model Context Protocol](https://modelcontextprotocol.io), exposé en **HTTP streamable**, qui donne à un agent **quatorze** opérations sur Microsoft Graph, et quatorze seulement :

| Outil | Verbe | Effet |
|---|---|---|
| `list_items(list_id, top=50)` | **lecture** | `GET /sites/{site}/lists/{list}/items?$expand=fields` — lit les éléments d'une liste SharePoint du site AlliaConsuling. |
| `create_list_item(fields)` | **écriture** | `POST /sites/{site}/lists/{PROPOSITION}/items` — crée un élément **uniquement** dans la liste « Zone-de-proposition ». |
| `televerser_brouillon_offre(nom_fichier, contenu_base64, candidat_id)` | **écriture fichier** | `PUT .../drives/{BROUILLON_DRIVE}/.../{nom}.docx:/content` — dépose un **brouillon .docx** dans le dossier **« 00 - Proposition en cours » FIGÉ**, jamais ailleurs ; collision = **fail**. **Code en PR B (`T-0017-a`).** |
| `reconcilier_groupe_perimetre(group_id, membres_attendus)` | **gestion d'appartenance** | `GET/POST/DELETE .../groups/{id}/members` — **réconcilie** l'appartenance d'un groupe de périmètre sur un **état désiré** (delta idempotent : ajoute/retire le seul delta) ; cible bornée par **liste blanche figée** + **AU** (`T-0019-a`). |
| `reconcilier_groupe_parc(group_id, membres_attendus)` | **gestion d'appartenance** | `GET/POST/DELETE .../groups/{id}/members` — **réconcilie** l'appartenance du groupe de **parc** d'enrôlement (`grp-parc-collaborateur`) sur un **état désiré** (delta idempotent) ; cible bornée par **liste blanche DÉDIÉE** `GRAPH_GROUPES_PARC_AUTORISES` + **AU** `au-groupes-socle` (`T-0008`). |
| `lire_annuaire(upn="", group_id="")` | **lecture** | `GET /users/{upn}` et/ou `GET /groups/{id}/members` — **résout** un UPN en objectId et/ou **liste** les membres d'un groupe ; **lecture seule stricte**, `group_id` borné à l'**union** des listes blanches périmètre ∪ parc (`T-0007`). |
| `creer_espace_mission(annee, client, nom_mission)` | **écriture dossier** | `POST .../drives/{MISSION_DRIVE}/items/{MISSION_FOLDER}/children` — crée l'**espace de mission** (dossier au nom **composé côté serveur** `AAAA - Client - Nom de la mission` + arbre **FIGÉ** `01 - Pilotage / 02 - Livrables`) **uniquement** sous la racine **« Missions » FIGÉE**, jamais ailleurs ; collision = **fail** (`T-0024-a`). |
| `deposer_document_mission(annee, client, nom_mission, sous_dossier, nom_fichier, contenu_base64, sha256_attendu)` | **écriture fichier** | `PUT .../drives/{MISSION_DRIVE}/items/{MISSION_FOLDER}:/{nom_espace}/{sous_dossier}/{nom}:/content` — dépose un **brouillon interne** dans un sous-dossier **whitelisté** d'un espace de mission (nom d'espace **recomposé côté serveur**) ; extension dans `{.docx .pptx .xlsx .pdf .md}` ; collision = **fail** ; **intégrité fail-closed** (`sha256_attendu` recalculé côté serveur, mismatch = refus avant écriture) (`T-0024-a`). |
| `notifier_canal(titre, corps, reference="")` | **écriture** | `POST /sites/{site}/lists/{NOTIFICATIONS}/items` — dépose une **notification d'équipe** **uniquement** dans la liste « Notifications » **FIGÉE** ; le canal Teams « Allia Consulting — vie interne » est atteint par **flux M365** (élément créé → Post as Flow bot) — Graph n'offre PAS d'envoi de canal en app-only ; cran **notifie** (`T-0012`). |
| `workbook_lire_table(drive_id, item_id, table)` | **lecture** | `GET .../items/{item}/workbook/tables/{table}/rows` — lit les lignes d'une table nommée d'un classeur Excel ; **lecture NON bornée** (saisie / gabarit / référentiel de coûts), ne modifie rien (`T-0031`). |
| `workbook_ajouter_lignes(code_mission, table, lignes)` | **écriture** | `POST .../workbook/tables/{table}/rows` — ajoute des lignes à une table du **gabarit** d'une mission ; cible **FIGÉE** « 06 - Gabarit ERP » résolue côté serveur (`T-0031`). |
| `workbook_maj_ligne(code_mission, table, index, valeurs)` | **écriture** | `PATCH .../rows/itemAt(index=…)` — met à jour une ligne par **position** dans une table du gabarit ; cible **FIGÉE** côté serveur (`T-0031`). |
| `workbook_archiver_gabarit(code_mission)` | **écriture fichier** | `POST .../items/{item}/copy` → « 00 - Old » — archive (copie horodatée) le gabarit courant d'une mission avant régénération ; source et destination **FIGÉES** côté serveur (`T-0031`). |
| `workbook_instancier_gabarit(code_mission)` | **écriture fichier** | **v2 API-native** — fabrique `gabarit-<CodeMission>.xlsx` **par le service Excel** (PUT contenu vide fail-closed, puis `tables/add` sur les en-têtes §5.2) dans « 06 - Gabarit ERP » **FIGÉE** ; **plus aucune souche binaire** ; **ré-émission service** (« Ouvrir + Enregistrer » machine) + **preuve FROIDE sans session** `count:0 ×3` (le chemin du cockpit — ouvrabilité à froid, `T-0035`), **rollback borné**, collision = **fail** (`T-0031` / `T-0033` / `T-0035`). |

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

## Le garde-fou structurel (ter) : le réconciliateur ne gère que des groupes de périmètre déclarés

`reconcilier_groupe_perimetre` projette une **décision de délégation déjà promue** (`organisation.md` §3, §5) sur le groupe Entra du périmètre. « Le dérivé n'est jamais le saisi » : l'**état désiré** (`membres_attendus`) est résolu **en amont** par Claude Code à partir du canon promu ; l'outil ne **décide** rien — il réconcilie l'état réel sur l'état désiré. La chaîne d'autorité reste **le guide (Git) → Claude (réconciliation au moindre privilège) → M365** (`organisation.md` §5).

Deux bornes **indépendantes** encadrent ce pouvoir, en défense en profondeur :

- **Liste blanche figée côté serveur** (`GRAPH_GROUPES_PERIMETRE_AUTORISES`, CSV d'objectId) : un `group_id` hors liste lève `PermissionError` **avant tout appel d'écriture**. Même esprit que la liste/dossier figés des autres outils — le code ne peut toucher **que** des groupes de périmètre explicitement déclarés.
- **Administrative Unit côté Entra** (runbook `T-0019-b`) : le rôle Groups Administrator du service principal de l'identité managée est **scopé à une AU** ne contenant que les groupes de périmètre. Le scope Graph reste `.default` ; **aucun secret**.

L'opération est **idempotente** : seul le **delta** est appliqué (`POST $ref` pour ajouter, `DELETE $ref` pour retirer) ; un delta vide ne touche rien. `membres_attendus = []` est **autorisé** et signifie « vider le groupe » (révocation totale, **réversible** — jamais une suppression de données). Chaque retrait est **journalisé** par objectId (traçabilité par personne). Le pouvoir réel d'écriture sur l'appartenance est conféré **hors code**, au runbook humain `T-0019-b` ; le présent code reste **inerte** tant que la variable et l'AU ne sont pas posées.

## Le garde-fou structurel (quater) : socle et périmètre sont strictement séparés

`reconcilier_groupe_parc` est le **miroir exact** de `reconcilier_groupe_perimetre` (même structure idempotente, mêmes bornes en défense en profondeur), appliqué au **groupe de parc d'enrôlement** `grp-parc-collaborateur`. La différence tient à une **séparation stricte socle/périmètre** (décision gardien du 28/06) :

- **Liste blanche DÉDIÉE** : `GRAPH_GROUPES_PARC_AUTORISES` est une variable **séparée** de `GRAPH_GROUPES_PERIMETRE_AUTORISES`. Un `group_id` de périmètre n'est **pas** gérable par cet outil, et réciproquement — chaque outil ne touche que **sa** classe de groupes déclarés.
- **AU dédiée** : le rôle Groups Administrator du service principal de l'identité managée est **scopé à l'Administrative Unit `au-groupes-socle`** (qui ne contient que ce groupe), runbook gardien. Le scope Graph reste `.default` ; **aucun secret**.

Même contrat que le réconciliateur de périmètre pour le reste : `membres_attendus = []` vide le groupe (révocation totale, **réversible**), chaque mutation est **journalisée** par objectId, et le code reste **inerte** tant que la variable et l'AU ne sont pas posées. **Portée v1 minimale** (décision gardien 28/06) : seule l'**appartenance du groupe d'enrôlement** est réconciliée ; la projection complète des politiques (profils de configuration / conformité) vers Intune est un **incrément ultérieur différé**.

## Lecture d'annuaire bornée : résoudre avant de muter (`lire_annuaire`)

`lire_annuaire` est un outil de **LECTURE SEULE STRICTE** : il n'écrit **jamais**, ne réconcilie rien. Il existe pour que Claude Code **résolve** l'état réel de l'annuaire **avant** tout appel mutant — au lieu de figer des GUID **de mémoire** (interdit par la doctrine §2) ou de subir l'**absence de dry-run** des réconciliateurs. C'est le préalable de résolution d'identifiants requis par l'onboarding `T-0007` et son épreuve.

Deux résolutions, au moins une obligatoire :

- **`upn`** : résout un `userPrincipalName` (email) en `objectId` — `GET /users/{upn}` (`$select=id,displayName,userPrincipalName`). Retourne `{"utilisateur": {...}}`.
- **`group_id`** : liste les **objectId des membres** d'un groupe (pagination `@odata.nextLink`, via le helper partagé `_lire_membres_groupe`). Retourne `{"membres": [...]}`.

**Bornage (moindre privilège, cohérent avec les réconciliateurs)** : `group_id` doit appartenir à l'**union** des listes blanches périmètre ∪ parc (`GRAPH_GROUPES_PERIMETRE_AUTORISES` ∪ `GRAPH_GROUPES_PARC_AUTORISES`) — un `group_id` hors de cette union lève `PermissionError` **sans aucune lecture**. Aucune liste blanche configurée = outil fermé (`ConfigManquante`). La résolution d'`upn` porte sur les utilisateurs du tenant. **Aucune nouvelle variable d'environnement** : l'outil réutilise les deux listes blanches existantes.

**Prérequis (runbook gardien, DÉJÀ posé le 28/06)** : le rôle Entra **`Directory Readers`** est assigné à l'identité managée `id-allia-mcp-graph` (lecture d'annuaire — utilisateurs et appartenance de groupes). Le scope Graph reste `.default` ; **aucun secret**.

## Le garde-fou structurel (quinquies) : l'espace de mission ne se crée que sous la racine « Missions »

`creer_espace_mission` et `deposer_document_mission` suivent le **même** principe que `create_list_item` et `televerser_brouillon_offre` : la cible n'est **jamais** choisie par l'appelant, elle est **figée côté serveur** par deux variables d'environnement — `GRAPH_MISSION_DRIVE_ID` (la bibliothèque hôte) et `GRAPH_MISSION_FOLDER_ID` (le dossier racine « Missions »). Ces deux outils sont **dédiés** : ils lisent leur propre configuration (`_config_mission()`), les outils existants n'en dépendent pas.

**Le nom d'espace est COMPOSÉ côté serveur** (décision gardien du 2 juillet 2026, garde-fou structurel) : l'appelant fournit `(annee, client, nom_mission)`, jamais le nom final. Le helper **partagé** `_composer_nom_espace(annee, client, nom_mission)` valide les composantes et compose **`AAAA - Client - Nom de la mission`** (ex. **« 2026 - Arabelle Solutions - Siteflow »**). Les **deux** outils passent par ce même helper : **zéro dérive** possible entre la création de l'espace et le dépôt d'un document.

- **`creer_espace_mission(annee, client, nom_mission)`** crée, **uniquement** sous la racine « Missions », le dossier `<nom_espace>` composé puis l'**arbre FIGÉ dans le code** (`SOUS_DOSSIERS_MISSION` = `01 - Pilotage`, `02 - Livrables` — le support de kick-off se dépose dans `01 - Pilotage`) — l'appelant ne choisit ni la cible ni l'arborescence ni le nom final. Validation : `annee` = 4 chiffres bornée `[2020..2100]` ; `client` / `nom_mission` = 1..60 caractères (accents et espaces internes autorisés, espaces multiples réduits), refus des caractères `" * : < > ? / \ | # % ,`, de la séquence `..` et d'un point en tête/fin. **Collision = fail** sur chaque création : un espace de même nom n'est **jamais** écrasé ni fusionné.
- **`deposer_document_mission(annee, client, nom_mission, sous_dossier, nom_fichier, contenu_base64, sha256_attendu)`** dépose un **brouillon interne** dans `<racine>/<nom_espace>/<sous_dossier>/<nom>`, le `<nom_espace>` étant **recomposé** par le même helper. Le `sous_dossier` est restreint à la **liste blanche figée** `SOUS_DOSSIERS_MISSION` (`PermissionError` sinon) ; le `nom_fichier` est **assaini** et son extension **forcée** dans `EXTENSIONS_MISSION` (`.docx`, `.pptx`, `.xlsx`, `.pdf`, `.md`) ; **collision = fail** (jamais d'écrasement). Le dépôt ne vise **jamais** un espace exposé au client — l'envoi au client reste un acte **humain** (`envoyer_livrable_client`, cran validé, grade habilité).
  - **Intégrité fail-closed (leçon épreuve `T-0024-d`).** L'appelant fournit `sha256_attendu` (64 hex minuscules) ; après décodage base64, le serveur **recalcule** `sha256(contenu)` et **refuse** (`ValueError` « INTEGRITÉ : sha256 reçu X ≠ attendu Y ») **avant tout appel Graph** si l'empreinte diffère. Un contenu **corrompu en transit** (le cas réel de l'épreuve : 17307 o reçus ≠ 16758 o émis) ne peut donc plus être **stocké silencieusement**. Le retour inclut `sha256` = empreinte du contenu réellement envoyé au `PUT`.

Cran des deux actions : **auto** — espace/brouillon internes, réversibles, locaux (`table-des-crans.yaml` : `creer_espace_mission` ; `deposer_document_mission_zone_travail`, ajouté en `T-0024-b`). La **mise en service** (création de la racine « Missions », résolution des ids, pose des variables sur le service, octroi `write` prouvé) est un **runbook humain** — `T-0024-c`. Le code reste **inerte** tant que les deux variables ne sont pas posées.

## Le garde-fou structurel (sexies) : la notification ne part que par la liste « Notifications »

`notifier_canal(titre, corps, reference="")` dépose une notification d'équipe dans la liste
SharePoint « Notifications » — cible FIGÉE côté serveur (`GRAPH_NOTIFICATIONS_LIST_ID`), jamais
choisie par l'appelant. Le message atteint le canal Teams « Allia Consulting — vie interne » par
un flux M365 (déclencheur : élément créé dans la liste, publication en tant que Flow bot) : Graph
ne supporte PAS l'envoi de message de canal en app-only (permissions déléguées uniquement ;
app-only = migration — fait vérifié le 05/07/2026). Ce relais conserve le zéro secret et n'ajoute
AUCUNE permission Graph. Type d'action `notifier_equipe`, cran `notifie` (table-des-crans) :
l'agent agit, l'équipe est informée. Latence du déclencheur : de l'ordre de la minute (polling
standard M365) — acceptable pour une notification d'équipe. Évolution nommée si l'interactivité
(mentions, cartes, réponses) devient un besoin : bot Azure (identité managée), seule voie d'envoi
direct supportée — coût aujourd'hui disproportionné pour une notification sortante.

## Le garde-fou structurel (septies) : les primitives Workbook n'écrivent qu'au domicile gabarit

Les cinq primitives **Workbook/Tables** (`T-0031`) portent le modèle économique distribué (`modele-donnees.md` §5) : un **classeur Excel à tables nommées** par mission (`gabarit-<CodeMission>.xlsx`), distinct des listes SharePoint. Elles séparent nettement **lecture** et **écriture** :

- **Lecture NON bornée** — `workbook_lire_table(drive_id, item_id, table)` accepte `drive_id` + `item_id` de l'appelant : elle peut lire une **saisie** (Management et Gestion), un **gabarit** (« 06 - Gabarit ERP ») ou le **référentiel de coûts** (audience restreinte). Elle ne modifie rien ; adressage par **position** (l'ordre des lignes est celui de la table).
- **Écriture BORNÉE par construction** — `workbook_ajouter_lignes`, `workbook_maj_ligne`, `workbook_archiver_gabarit` et `workbook_instancier_gabarit` n'exposent **aucun** `drive_id` / `item_id` / `folder_id`. La cible est toujours le `gabarit-<code_mission>.xlsx` du dossier **FIGÉ** « 06 - Gabarit ERP » (`GRAPH_GABARIT_DRIVE_ID` + `GRAPH_GABARIT_FOLDER_ID`), résolu côté serveur ; `code_mission` est **assaini** par la même routine que le nom de fichier de `deposer_document_mission`. Écrire ailleurs est *structurellement* impossible. Chaque primitive reste **bête** : elle fait une chose ; l'orchestration systématique (régénération complète, instanciation d'un gabarit manquant) est portée par le **skill** `consolidation-pilotage`, pas par un outil composite.

**`workbook_instancier_gabarit` — v2 « fabrication service » (API-native, `T-0033`).** L'instanciation ne **copie plus aucune souche binaire** (leçon `T-0033` : un binaire openpyxl à tables sans ligne de corps est renormalisé par SharePoint et finit illisible — `501` sur l'API Workbook). Le gabarit est désormais **fabriqué de bout en bout par le service Excel** :

1. **Création service-authored, FAIL-CLOSED** — `PUT` d'un contenu **vide (0 octet)** sous le dossier figé, `@microsoft.graph.conflictBehavior=fail` (collision → `FileExistsError`, jamais d'écrasement) ;
2. **Session Workbook** `persistChanges: true` (l'id de session accompagne tous les appels suivants) ;
3. **Feuilles** — la 1re feuille est renommée « Affectations », « Imputations » et « Echeancier » sont ajoutées ;
4. **Par table** — écriture des en-têtes §5.2 (`PATCH range`), création de la table (`tables/add` `hasHeaders`, avec **retry borné** sur `504`), renommage `T_Affectations` / `T_Imputations` / `T_Echeancier` ;
5. **Preuve EN SESSION (sanity chaude)** — chaque table est relue (`/rows`, session chaude) et **doit** porter **0 ligne de corps** (`count:0 ×3`) ; **nécessaire mais non suffisant** (cf. étape 8) ;
6. **closeSession** de la session de fabrication (best effort) ;
7. **Ré-émission par le service (« Ouvrir + Enregistrer » machine)** — 2e session **FROIDE** + réécriture **inerte** des en-têtes de la 1re table (mêmes valeurs) → le service **re-sérialise un binaire canonique**. Un classeur amorcé depuis `0` octet est lisible en session **chaude** mais son binaire **au repos** n'est pas canonique : l'API Workbook refuse son ouverture **FROIDE** ultérieure (`403` sur `/workbook/tables` — épreuve `T-0035` du 17/07, cockpit en Graph délégué) ;
8. **Preuve FROIDE, SANS session (le chemin EXACT du cockpit)** — chaque table est relue par `/columns` **sans** `workbook-session-id` (comme `workbook-graph.ts` de la tour de contrôle) et **doit** s'ouvrir à froid (`200`), porter ses en-têtes §5.2 et **0 ligne de corps**. C'est **cette** preuve, et non l'étape 5, qui atteste l'ouvrabilité dont le cockpit a besoin ; un échec froid (`403`/`404`/`500`) déclenche le rollback — **plus jamais de faux-vert**.

**Rollback borné** : toute erreur survenant **après** la création (étape 1) supprime (best effort → corbeille) le **seul** item créé par l'appel courant — jamais un autre. Le schéma des 3 tables **dérive de** `modele-donnees.md` §5.2, qui **fait foi** (le binaire `gabarit-pilotage-mission.xlsx` est retiré du rôle de souche, conservé au canon comme trace historique). Retour : `{code_mission, nom_gabarit, item_id, tables: {T_Affectations: 0, T_Imputations: 0, T_Echeancier: 0}}` — les comptes attestés **à froid** (étape 8).

Cran des écritures gabarit : **auto** (`table-des-crans.yaml` : `reconcilier_gabarit_pilotage` / `instancier_gabarit_pilotage`) — interne, local, réversible. La **mise en service** (domicile « 06 - Gabarit ERP » / « 00 - Old », pose des variables) est un **runbook gardien** (`T-0031`) ; le **build + déploiement** de la v2 (image serveur **0.13.0**, `T-0033`) puis de la reprise **ouvrabilité à froid** (image serveur **0.14.0**, `T-0035` — ré-émission + preuve froide) et l'**épreuve tenant** (instancier ×2 → lecture **FROIDE en Graph délégué** `count:0 ×6`) restent des gestes gardien après merge.

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
| `GRAPH_GROUPES_PERIMETRE_AUTORISES` | **Liste blanche** (CSV d'objectId **publics**) des groupes de périmètre que `reconcilier_groupe_perimetre` peut gérer — défense en profondeur **en plus** de la borne AU (`T-0019-b`). Renseignée au runbook B ; absente = outil fermé (`ConfigManquante`). **Pas un secret.** |
| `GRAPH_GROUPES_PARC_AUTORISES` | **Liste blanche DÉDIÉE** (CSV d'objectId **publics**) des groupes de **parc** que `reconcilier_groupe_parc` peut gérer — séparée du périmètre, défense en profondeur **en plus** de la borne AU `au-groupes-socle` (`T-0008`). Renseignée au runbook gardien ; absente = outil fermé (`ConfigManquante`). **Pas un secret.** |
| `GRAPH_MISSION_DRIVE_ID` | Identifiant de la bibliothèque (drive) hôte de la racine **« Missions »** — **cible figée** de `creer_espace_mission` / `deposer_document_mission`. Identifiant **public**. Posé au runbook `T-0024-c` ; absent = outils mission fermés (`ConfigManquante`). **Pas un secret.** |
| `GRAPH_MISSION_FOLDER_ID` | Identifiant du dossier racine **« Missions »** — **seul parent** des espaces de mission créés, jamais choisi par l'appelant. Identifiant **public**. Posé au runbook `T-0024-c` ; absent = outils mission fermés (`ConfigManquante`). **Pas un secret.** |

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
