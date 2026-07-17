# Consolidation du pilotage économique — saisie → gabarit de mission — Skill

> **id** : `consolidation-pilotage`
> **Version** : 1.3 — *candidat*. **Nature** : skill.
> **Changelog** : v1.3 — candidat, 17 juillet 2026 (T-0035 reprise n°4) : **orchestration de la RÉGÉNÉRATION d'un gabarit existant, rendue machine et éprouvable**. L'épreuve tenant du 17/07 (soir) a buté sur une **collision non levable** : `workbook_instancier_gabarit` est fail-closed sur un gabarit en place (correct, **inchangé**) et `workbook_archiver_gabarit` ne faisait que **COPIER** (l'original restait à la racine, le nom `gabarit-<code>.xlsx` n'était **jamais libéré**). Deux corrections **conformes S34** (primitives BÊTES, logique dans le skill) : (a) `workbook_archiver_gabarit` fait désormais un vrai **DÉPLACEMENT** vers « 00 - Old » (serveur **0.14.0 → 0.15.0**) — synchrone (`200`, plus de `202`/poll), borné (cible figée, jamais générique), réversible (version conservée) → **le nom est libéré** ; (b) le skill orchestre la régénération : *(lire saisie + gabarit courant → réconcilier en mémoire) → archiver (déplacement, nom libéré) → `workbook_instancier_gabarit` (fail-closed satisfait, plus de collision ; sa **preuve FROIDE §8** atteste l'ouvrabilité) → repeupler les 3 tables* — **idempotent** (contenu), **réversible** (« 00 - Old »), **journalisé**. La réconciliation par clé métier (jamais de suppression, jamais de rétrogradation de `validé`, report des champs propres au gabarit type `LienFacture`) est **préservée**, portée par la construction du jeu de données AVANT archivage. Le mécanisme passe de la fusion incrémentale en place (jamais éprouvée, condamnée par le déplacement) à la **régénération réconciliée** — alignée sur `modele-donnees.md` §5.6 (« archive courant → régénère → actualise »). §3, §5, §5 bis, §5 ter, §6, §7, §8, §10 alignés ; aucune entrée de changelog existante modifiée. v1.2 — candidat, 17 juillet 2026 (T-0035 reprise n°3) : l'instanciation exige désormais l'**ouvrabilité À FROID** du gabarit (serveur **0.14.0**) — la primitive **ré-émet** le classeur par le service puis prouve `count:0 ×3` **à froid** (lecture `/columns` **sans** session, le chemin du cockpit) ; la preuve chaude seule était un **faux-vert** (403 sur le cockpit délégué). §3 (preuve froide) et §6 (échec froid → rollback) alignés ; aucune entrée de changelog existante modifiée. v1.1 — candidat, 17 juillet 2026 (T-0033 reprise S37) : alignement du corps sur l'**instanciation v2 API-native** (`workbook_instancier_gabarit` fabrique le gabarit **par le service Excel** — création service-authored, tables par l'API Workbook, **appel synchrone**, **preuve interne count:0 ×3**, **plus de souche binaire**) — §3, §6, §8, §9, §10. `workbook_archiver_gabarit` **inchangé** (reste **asynchrone** : 202 à poller jusqu'à `completed`). > **Changelog** : v1.0 — candidat, 14 juillet 2026 : création. **Consommateur** des primitives Workbook/Tables du MCP Graph (`T-0031`) : il consolide les **classeurs de saisie humains** (site Management et Gestion) vers les **gabarits de pilotage par mission** (`gabarit-<CodeMission>.xlsx`, dossier « 06 - Gabarit ERP » du site Contrats et administratif), table par table, sous les crans auto `instancier_gabarit_pilotage` (gabarit manquant → instanciation systématique et machine) et `reconcilier_gabarit_pilotage`. Il **n'invente aucune tuyauterie** : il orchestre les cinq primitives bornées (`workbook_lire_table`, `workbook_instancier_gabarit`, `workbook_ajouter_lignes`, `workbook_maj_ligne`, `workbook_archiver_gabarit`) — la logique de clé métier vit **ici**, dans le skill, jamais dans le MCP (primitives BÊTES, décision S34). Écriture **bornée par construction** côté serveur : le skill ne manipule **jamais** de `drive_id`/`item_id` en écriture (il passe `code_mission`). Promotion par le **gardien** (procédure allégée). Première exécution **manuelle**, pilotée par le gardien.
> **Domicile** : `skills/consolidation-pilotage/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `contrats/socle/modele-donnees.md` (**§5** modèle économique distribué — §5.2 tables du gabarit `T_Affectations`/`T_Imputations`/`T_Echeancier`, §5.3 référentiel de coûts `T_Ressources`/`T_Structure`, §5.5 état du câblage, §5.6 couche de saisie + boucle agent), `contrats/socle/table-des-crans.yaml` (`reconcilier_gabarit_pilotage` = **auto**), `backlog/chantiers/T-0031.yaml` (les 4 primitives Workbook consommées ; **écriture bornée par construction**), `outils/mcp-graph/server.py` (docstrings et signatures des primitives), `doctrine/doctrine.md` (§2 source vs dérivé, §6 crans), `CLAUDE.md`.

## 1. Objet

Consolider les **classeurs de saisie humains** vers les **gabarits de pilotage par mission**, via les primitives **Workbook bornées** du MCP Graph. **Capacité** : Socle d'exploitation / la **boucle §5.6** du modèle de données (couche de saisie → gabarit ERP par mission → lecture directe par la tour de contrôle).

Le skill **exécute** la dérivation ; il ne définit ni les domiciles, ni les schémas de tables, ni le cran : ces règles **font foi** dans `modele-donnees.md` §5 et `table-des-crans.yaml` — ce skill y **renvoie**, il ne les recopie pas.

> **Bornes dures (non négociables).**
> - L'agent **dérive** un gabarit depuis la saisie ; **le dérivé n'est jamais le saisi** (`CLAUDE.md`). Il **écrit uniquement les gabarits** (cible figée par construction) et **lit** les saisies et le référentiel — il **n'écrit jamais** dans la saisie ni dans le référentiel de coûts.
> - L'écriture est **bornée par construction côté serveur** : le skill passe `code_mission` aux primitives d'écriture (`workbook_instancier_gabarit`, `workbook_ajouter_lignes`, `workbook_maj_ligne`, `workbook_archiver_gabarit`) et **ne manipule jamais de `drive_id`/`item_id` en écriture**. Il est structurellement impossible d'écrire ailleurs que dans `gabarit-<CodeMission>.xlsx` de « 06 - Gabarit ERP ».
> - **Jamais de suppression.** La fusion est **incrémentale** ; aucune ligne du gabarit n'est jamais effacée par l'agent (§5).

## 2. Entrées (lecture seule)

| Entrée | Domicile | Accès |
|---|---|---|
| Classeurs de saisie `saisie-<CodeMission>-<Libellé>.xlsx` | racine de la bibliothèque « Documents » du site **AlliaConsulting-ManagementetGestion** (`GRAPH_SAISIE_DRIVE_ID`) | outil de lecture M365 de l'agent (surface humaine, lecture souple) |
| Référentiel de coûts `T_Ressources` (§5.3) | site **AlliaConsulting-Contratsetadministratif**, « 08 - Coût Masse salariale & Indep » | `workbook_lire_table` (lecture non bornée) |
| État courant du gabarit `gabarit-<CodeMission>.xlsx` | « 06 - Gabarit ERP » (site Contrats et administratif) | `workbook_lire_table` (lecture non bornée) |

- **CodeMission extrait du NOM** du classeur de saisie par `^saisie-(\d+)-` ; le **libellé** qui suit est **libre**, **casse libre** (il n'entre pas dans la clé).
- **Onglets attendus de la saisie** : `consignes`, `Prévu <année>`, `Réalisé <année>`, `Facturation`.
- **Horodatage non fiable en co-édition.** Les métadonnées `lastModifiedDateTime` peuvent être **différées** quand un classeur Excel Online est en co-édition : **le contenu fait foi, pas l'horodatage**. Ne jamais décider d'ignorer une saisie sur le seul `lastModifiedDateTime`.

## 3. Cible — le gabarit de pilotage de la mission

`gabarit-<CodeMission>.xlsx` dans « 06 - Gabarit ERP » (site **AlliaConsulting-Contratsetadministratif**), tables nommées **`T_Affectations`** / **`T_Imputations`** / **`T_Echeancier`** (schéma figé, `modele-donnees.md` §5.2).

> **Si le gabarit d'une mission n'existe pas : l'agent l'INSTANCIE, puis poursuit la consolidation.** Il appelle `workbook_instancier_gabarit(code_mission)` — la primitive **FABRIQUE** le gabarit `gabarit-<CodeMission>.xlsx` **par le service Excel** (v2, serveur 0.13.0) : création d'un classeur **service-authored** (`PUT` contenu vide, `conflictBehavior=fail`, jamais d'écrasement) puis fabrication des **3 tables par l'API Workbook** (en-têtes §5.2). Cible **FIGÉE côté serveur**. **Preuve FROIDE count:0 ×3** portée par le retour (`{item_id, tables}`) : depuis la reprise n°3 (serveur **0.14.0**, `T-0035`), la primitive **ré-émet** le classeur par le service (« Ouvrir + Enregistrer » machine) puis prouve l'**ouvrabilité À FROID** (lecture `/columns` **sans** session, le chemin du cockpit) — le count:0 est vrai à froid, pas seulement en session chaude ; échec froid → rollback borné. Appel **SYNCHRONE** : aucun `Location` à poller pour l'instanciation. **Instanciation SYSTÉMATIQUE et machine** (décision gardien du 14/07/2026) : **plus jamais un geste humain**, aucune demande, aucune attente. **Un gabarit instancié dans le passage courant ne subit PAS d'archivage préalable** (§5 bis) : rien à archiver (création pure). **Si le gabarit EXISTE déjà**, on ne ré-instancie pas en place (le fail-closed refuse, à raison) : on le **régénère** par l'orchestration §5 (archiver-déplacer → ré-instancier → repeupler) — le déplacement libère le nom, la ré-instanciation retrouve son terrain vierge.

## 4. Transformation (matriciel → long)

La saisie est **matricielle** (grille ressource × mois) ; le gabarit est **long** (une ligne par cellule renseignée). La transformation :

- **`Prévu <année>` → `T_Affectations`** : une ligne par **(Ressource, Mois) dont la valeur > 0**, `Mois` normalisé au **1er du mois**. Colonnes longues : `CodeMission`, `Ressource`, `Mois`, `JoursPrevus`.
- **`Réalisé <année>` → `T_Imputations`** : idem, une ligne par **(Ressource, Mois) dont la valeur > 0**, avec `StatutValidation` initial **« à valider »**. Colonnes : `CodeMission`, `Ressource`, `Mois`, `JoursRealises`, `StatutValidation`.
- **`Facturation` → `T_Echeancier`** : une ligne par facture, `LienFacture` **vide** côté saisie (posé plus tard par le responsable). Colonnes : `NumFacture`, `CodeMission`, `MoisCA`, `MontantHT`, `Echeance`, `Statut`, `LienFacture`.

## 5. Régénération réconciliée, jamais de suppression

**RÉGÉNÉRATION RÉCONCILIÉE, JAMAIS DE SUPPRESSION.** Un gabarit existant se **régénère** — il ne se réécrit pas en place. Le mécanisme : *réconcilier en mémoire (saisie + état courant) → **archiver (DÉPLACEMENT, nom libéré)** → **ré-instancier** (fabrication service, preuve froide) → **repeupler***. La régénération traverse ainsi la **preuve FROIDE §8** de `workbook_instancier_gabarit` à **chaque** passage : le gabarit produit est **ouvrable à froid par construction** (le cockpit le lira), là où une écriture en place n'aurait jamais re-prouvé l'ouvrabilité. Ce mécanisme est aligné sur `modele-donnees.md` §5.6 (« archive courant → régénère → actualise »).

> **Pourquoi une régénération, et non une fusion en place ?** `workbook_instancier_gabarit` est fail-closed (jamais d'écrasement — à conserver) ; `workbook_archiver_gabarit` **déplace** désormais le gabarit courant (§5 bis) plutôt que de le copier. Le déplacement **libère le nom** — ce qui **rend la ré-instanciation possible** (plus de collision, la panne de l'épreuve tenant du 17/07) — mais retire du même geste la cible d'une écriture en place. La régénération complète est donc le seul mécanisme **réversible ET machine** disponible ; c'est aussi le plus sûr (openabilité re-prouvée à froid, aucun décalage d'index de `maj_ligne`).

### Séquence (idempotente, réversible, journalisée)

1. **Lire la saisie** (source) et **transformer** matriciel → long (§4) → jeu `saisie`.
2. **Lire l'état courant** du gabarit via `workbook_lire_table` (3 tables). Gabarit **absent** (`FileNotFoundError`) → **instanciation pure** (§3), **aucun archivage** (rien à archiver), jeu régénéré = `saisie`.
3. **Réconcilier en mémoire** → jeu `régénéré`, en appliquant les **clés métier** et les **invariants** ci-dessous ; **collecter les anomalies**. C'est ICI, **avant tout effet de bord**, que « jamais de suppression / jamais de rétrogradation de validé / report des champs propres au gabarit » sont honorés — le jeu régénéré n'efface ni ne rétrograde rien.
4. **Archiver (DÉPLACEMENT)** le gabarit courant → « 00 - Old » (`workbook_archiver_gabarit`) : **synchrone**, le nom `gabarit-<code>.xlsx` est **libéré**, la version précédente **conservée** intacte et horodatée (réversibilité). *(Sauté si gabarit absent — étape 2.)*
5. **Ré-instancier** le gabarit (`workbook_instancier_gabarit`) : le nom étant libre, le **fail-closed est satisfait** sans collision ni écrasement ; sa **preuve FROIDE §8** (lecture `/columns` sans session) **atteste l'ouvrabilité**. Échec (collision inattendue, ou **preuve froide rouge** → la primitive supprime elle-même l'item vide qu'elle vient de créer, rollback borné) → **anomalie §6**, STOP — **ne jamais réessayer en écrasant**.
6. **Repeupler** les 3 tables avec le jeu `régénéré` : `workbook_ajouter_lignes`, **un seul appel par table** (une liste de lignes).
7. **Contrôle post-écriture** (§5 ter) puis **rapport de passage**.

**Clés métier** (portées par le skill, jamais par le MCP) :
- `T_Affectations` / `T_Imputations` : **(CodeMission, Ressource, Mois)**.
- `T_Echeancier` : **(CodeMission, NumFacture)**.

**Invariants de réconciliation** (appliqués à l'étape 3, à la construction du jeu régénéré) :
- **Un mois repassé à 0 / vidé en saisie n'efface RIEN au gabarit** : la ligne présente dans l'état courant mais absente de la saisie est **reportée** (conservée) dans le jeu régénéré, et l'agent lève une **anomalie « correction de suppression à confirmer par le responsable »**. La suppression d'une donnée économique est une décision humaine, jamais une dérivation.
- **Ne JAMAIS rétrograder un `StatutValidation` « validé » vers « à valider ».** Une imputation `validé` de l'état courant est **reportée `validé`** si les jours n'ont pas changé (la saisie transformée porte « à valider » par défaut — le `validé` de l'état courant **prime**). Si les jours changent sur une ligne validée → **jours mis à jour + retour « à valider » + anomalie signalée** (le validé portait sur des jours qui ne sont plus ceux-là).
- **Champs propres au gabarit reportés** : un champ posé côté gabarit et **vide côté saisie** — typiquement `LienFacture` (posé plus tard par le responsable, §4) — est **reporté** depuis l'état courant vers le jeu régénéré. Régénérer ne doit **jamais perdre** un lien de facture déjà renseigné.

**Idempotence** : rejouer la réconciliation produit un gabarit actif au **contenu identique** (les archives de « 00 - Old » s'accumulent — c'est le versionnage voulu, `modele-donnees.md` §5.2). **Réversibilité** : la version précédente vit dans « 00 - Old » ; le **rétablissement** (« 00 - Old » → racine) est un **geste gardien** — aucune primitive n'expose le déplacement inverse. C'est cette réversibilité sans perte qui tient le cran à **auto**.

### 5 bis. Archivage = DÉPLACEMENT (réversibilité + libération du nom)

`workbook_archiver_gabarit(code_mission)` **DÉPLACE** (ne copie plus) le gabarit courant vers « 00 - Old » sous un nom horodaté, **AVANT la ré-instanciation**. Deux effets indissociables : la **réversibilité** (version précédente conservée intacte) **et** la **libération du nom** `gabarit-<code>.xlsx` de « 06 - Gabarit ERP », sans laquelle la ré-instanciation fail-closed (§3) buterait sur une **collision** (la panne exacte de l'épreuve tenant du 17/07, où l'archivage ne faisait que **copier**). **Exception** : si le gabarit n'existe pas (étape 2), aucun archivage — création pure (§3).

> **Le déplacement est SYNCHRONE** (Graph *move* au sein d'un même drive → `200` avec l'item déplacé) : au retour, le nom est **effectivement** libéré. Plus de `202`/`Location` à poller — l'ancien anti-faux-vert « un 202 n'est pas une preuve » **ne s'applique plus** (il visait la copie **asynchrone** `/copy`, abandonnée).

### 5 ter. Contrôle post-écriture (anti-faux-vert)

Après repeuplement, **relire les 3 tables** du gabarit via `workbook_lire_table` et vérifier :
- le **nombre de lignes attendu** (une ligne par entrée du jeu régénéré) ;
- **invariants** : Σ `MontantHT` de la mission = total de l'onglet `Facturation` ; Σ `JoursPrevus` = TOTAL de la grille de prévu.

Produire un **rapport de passage** : mission, lignes **écrites** par table, **anomalies** relevées, **nom de l'archive** déposée dans « 00 - Old » (trace de réversibilité). Un passage sans relecture de contrôle est un passage **non prouvé**.

## 6. Anomalies — à SIGNALER au gardien, JAMAIS à résoudre seul

- **Échec d'instanciation du gabarit** (conflit `conflictBehavior=fail` inattendu, droits insuffisants, échec de fabrication des tables, **preuve en session count:0 ×3 en défaut**, ou **preuve FROIDE en défaut** — classeur non ouvrable à froid par l'API Workbook, le cas du 403 cockpit `T-0035` — l'item créé est alors supprimé par le **rollback borné**) : signalé au gardien ; l'agent ne force pas et ne réessaie pas en écrasant.
- **Régénération avortée APRÈS archivage** (la ré-instanciation §5 étape 5 échoue une fois le gabarit déjà déplacé) : le gabarit courant est **en sécurité dans « 00 - Old »** sous son nom horodaté, mais la racine « 06 - Gabarit ERP » **n'a plus de gabarit actif** pour la mission. **Signaler au gardien** (nom de l'archive + code mission) pour **rétablissement** (« 00 - Old » → racine) ou relance ; **ne pas réessayer en écrasant**, ne pas tenter un déplacement inverse (aucune primitive ne l'expose). État **réversible**, jamais une perte.
- **Ressource absente de `T_Ressources`** du référentiel (§5.3, lecture seule via `workbook_lire_table`). **Convention d'identifiant** : adresse **mail Allia** pour un salarié, **mail du sous-traitant** pour un sous-traitant.
- **Doublon de `NumFacture` ENTRE missions** (état transitoire pré-T-0030) : détecté en lisant les `T_Echeancier` des gabarits actifs ; **signalement gardien, aucune renumérotation par l'agent**.
- **Toute régression de valeur** (mois vidé, jours d'une ligne validée modifiés) — cf. §5.

## 7. Crans (résolus via `table-des-crans.yaml`)

| Action | Cran | Fondement |
|---|---|---|
| Lire saisies / référentiel / gabarit | **auto** | lecture réversible, interne, locale |
| Instancier le gabarit d'une mission (`instancier_gabarit_pilotage`) | **auto** | création PURE fail-closed (`conflictBehavior=fail`, jamais d'écrasement), réversible par suppression ; interne ; local — journalisé |
| Régénérer un gabarit de mission (`reconcilier_gabarit_pilotage`) | **auto** | réversible : **archivage par DÉPLACEMENT** dans « 00 - Old » (nom libéré, version conservée) + **régénération réconciliée sans suppression** ; interne ; local — journalisé |

Les crans `instancier_gabarit_pilotage` et `reconcilier_gabarit_pilotage` **font foi dans `table-des-crans.yaml`** (tous deux auto, cible FIGÉE côté serveur ; instanciation en création pure `conflictBehavior=fail` ; régénération avec version précédente **déplacée** dans « 00 - Old » — nom libéré — avant ré-instanciation) — ce skill y **renvoie**. Chaque passage est **consigné au journal** (`_journal_appel` des primitives + rapport de passage §5 ter).

## 8. Garde-fous inscrits dans ce skill

- **Écriture bornée par construction** : le skill passe `code_mission` ; il **ne manipule jamais de `drive_id`/`item_id` en écriture**. Cible structurellement figée = `gabarit-<CodeMission>.xlsx` de « 06 - Gabarit ERP ».
- **Instanciation fail-closed** : gabarit manquant → `workbook_instancier_gabarit` (**fabrication service**, `PUT` contenu vide `conflictBehavior=fail`) ; jamais d'écrasement ; **aucune souche binaire**.
- **Jamais de suppression** : régénération réconciliée ; un mois repassé à 0 **n'efface RIEN** (la ligne est reportée dans le jeu régénéré) ; anomalie « correction de suppression à confirmer par le responsable ».
- **Jamais de rétrogradation de `validé`** vers « à valider » sans changement de jours (le `validé` de l'état courant est reporté dans le jeu régénéré).
- **Champs propres au gabarit reportés** (`LienFacture` renseigné, vide côté saisie) : régénérer ne perd jamais une donnée posée par le responsable.
- **Archive AVANT de ré-instancier** (`workbook_archiver_gabarit`) : **DÉPLACEMENT synchrone** vers « 00 - Old » (`200`) — le nom est libéré au retour (plus de `202`/poll : la copie asynchrone est abandonnée) ; c'est ce qui **satisfait le fail-closed** de la ré-instanciation sans l'affaiblir. L'**instanciation v2 est synchrone** et porte sa **preuve interne count:0 ×3** + **preuve froide**.
- **Régénération avortée après archivage → SIGNALER** (§6), jamais forcer, jamais de déplacement inverse par l'agent (état réversible via « 00 - Old », rétablissement gardien).
- **Relecture de contrôle** après repeuplement (anti-faux-vert) : compte de lignes + invariants de somme.
- **Anomalies signalées, jamais résolues seul** (§6) : échec d'instanciation, régénération avortée, ressource inconnue, doublon de `NumFacture`, régression de valeur.
- **Le contenu de la saisie fait foi, pas l'horodatage** (co-édition Excel Online).

## 9. Ce que ce skill ne fait pas

- Il **ne définit pas le schéma des tables** : `modele-donnees.md` §5.2 **fait foi**, projeté côté serveur (`TABLES_GABARIT`) ; l'instanciation est une **fabrication 100 % service, sans souche binaire**.
- Il **n'écrit pas** dans `T_Structure` ni `T_Ressources` (référentiel de coûts — `T-0032`, cran **validé**) : il les **lit** seulement.
- Il **ne publie pas** le cockpit / la tour de contrôle (chantier v3).
- Il **n'orchestre pas** sa propre planification lun-ven 05h/13h Paris (§5.6) : orchestration **ultérieure** — la **première exécution est manuelle, pilotée par le gardien**.
- Il **ne supprime rien** et **ne renumérote aucune facture**.
- Il **ne prend aucun engagement** juridique ou financier.

## 10. Prérequis avant mise en service

1. **Primitives Workbook `T-0031`** (`workbook_lire_table` / `workbook_ajouter_lignes` / `workbook_maj_ligne` / `workbook_archiver_gabarit`) déployées au tenant — *image 0.11.0, rév `--0000017`*. La v2 de `workbook_instancier_gabarit` (fabrication service) a été livrée en **image serveur 0.13.0** (PR #229), la reprise ouvrabilité à froid en **0.14.0** (PR #235). **Cette PR livre l'image serveur 0.15.0** : `workbook_archiver_gabarit` passe de la **copie** au **DÉPLACEMENT** (libération du nom) — **redéploiement gardien requis** avant la première régénération d'un gabarit existant. Solde de `T-0031` conditionné à la **première exécution réelle** d'une primitive (ce skill, sur un vrai gabarit).
2. **Gabarit canon** `gabarit-pilotage-mission.xlsx` — *promu (§5.5, PR #208)* ; depuis la v2, **trace historique retirée du rôle de souche** (`modele-donnees` v1.20).
3. ~~**Souche vierge canon en place** dans « 06 - Gabarit ERP » (runbook gardien)~~ — **caduc depuis la v2** : l'instanciation est une **fabrication service**, aucune souche à poser (le gabarit canon du point 2 reste une **trace historique**, retiré du rôle de souche, `modele-donnees` v1.20). L'agent instancie le gabarit de chaque mission **automatiquement** (`workbook_instancier_gabarit`, §3) ; l'instanciation n'est plus un geste gardien.
4. **Promotion de ce skill** par le gardien (procédure allégée).
5. **Épreuve réelle** : une régénération d'un vrai `gabarit-<CodeMission>.xlsx` **existant** depuis un vrai `saisie-<CodeMission>-….xlsx` sur le tenant — **archivage par déplacement prouvé** (nom libéré, version dans « 00 - Old »), **ré-instanciation sans collision** (preuve froide verte), repeuplement réconcilié sans suppression, relecture de contrôle verte, rapport de passage produit.

## 11. Évolution

Ce skill est **candidat**. Sa promotion suit la boucle (`doctrine.md` §7) : candidat → avis d'impact → **promotion par le gardien** (procédure allégée, portée locale), montée de version en en-tête, corps byte-identique à la promotion. Retour arrière = repointage. La réconciliation par clé métier restant **dans le skill** (primitives BÊTES), toute évolution de clé ou d'invariant se fait **ici**, pas dans le MCP.
