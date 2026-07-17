# Épreuve T-0035 (reprise n°4) — régénération d'un gabarit existant rendue MACHINE (banc rouge→vert)

Entrée d'épreuve du 2026-07-17 (soir). Fait nouveau ; aucune requalification d'un soldé, aucune
réécriture d'entrée existante. **T-0035 reste `en_cours`.** La reprise n°3 (ouvrabilité à froid,
serveur 0.14.0) a corrigé la FABRICATION d'un gabarit **neuf** ; l'épreuve tenant du soir a révélé
le point de rupture **suivant** : la **régénération d'un gabarit EXISTANT** n'est pas machine. Entrée
**jumelée** au journal `T-0033` (la correction touche `workbook_archiver_gabarit`, famille des
primitives Workbook `T-0031`/fabrication `T-0033`). Historique immuable — cette entrée s'ajoute.

## 1. Garde-fou SHA (vert)

- `git fetch origin` ; `origin/main` = `59ff08e524eb356494e69cb7f14f377f486d9672` (merge PR #235,
  reprise n°3 — gabarit ouvrable à froid). Branche `t-0035/reconciliation-skill` depuis ce point.

## 2. Faits observés — l'épreuve tenant du soir (17/07/2026) : régénération IMPOSSIBLE

Après le déploiement 0.14.0, la ré-instanciation d'un gabarit **neuf** passe (preuve froide verte).
Mais **régénérer un gabarit qui existe déjà** (le cas normal de la boucle §5.6 : une saisie change,
il faut refaire le gabarit) **échoue** :

- `workbook_instancier_gabarit` est **fail-closed** (`@microsoft.graph.conflictBehavior=fail`) : sur
  un gabarit en place, il rend `FileExistsError` (409). **C'est correct — à conserver.**
- `workbook_archiver_gabarit` (avant cette reprise) ne faisait que **COPIER** (`POST /copy`) le
  gabarit courant vers « 00 - Old » : l'**original restait à la racine** « 06 - Gabarit ERP », le nom
  `gabarit-<code>.xlsx` **n'était jamais libéré**.
- Conséquence : la séquence de régénération (archiver → ré-instancier) **butait sur une collision non
  levable** — l'orchestration de réconciliation **n'était de toute façon pas implémentée** dans le skill.

**État tenant laissé par l'épreuve du soir (fait à connaître, réversible).** L'agent d'épreuve a
archivé **deux gabarits** — `gabarit-1-20260717T13xxxxZ.xlsx` et `gabarit-2-20260717T13xxxxZ.xlsx`
(horodatage compact `…T13xxxxZ`) — dans « 00 - Old ». Comme l'archivage **copiait**, ces deux fichiers
sont des **copies** : les originaux `gabarit-1.xlsx` / `gabarit-2.xlsx` (missions Siteflow / Datalab,
instanciés le matin, épreuve T-0033 verte) **sont toujours actifs à la racine**. Aucune perte, aucun
écrasement : « 00 - Old » porte simplement deux copies horodatées surnuméraires — **état réversible**
(le gardien peut les retirer, ou les garder comme versions).

## 3. Deux voies évaluées — voie B (rigoureuse) retenue

- **Voie A — élargir le serveur** (primitive composite « régénérer » ou primitive de suppression/
  déplacement générique) : **REJETÉE**. Elle viole la décision S34 (primitives BÊTES, logique métier
  dans le skill) et ouvre une **surface dangereuse** (suppression/déplacement de fichier générique).
- **Voie B — orchestration dans le skill + correction MINIMALE et BORNÉE de l'archivage** : **RETENUE**.
  La logique de réconciliation vit dans le skill `consolidation-pilotage` ; la seule correction serveur
  est le passage de `workbook_archiver_gabarit` de la **copie** au **DÉPLACEMENT** — opération bornée
  sur une cible figée, pas une primitive générique (cf. §4).

## 4. Correction — le nœud tranché : archivage = DÉPLACEMENT (serveur 0.14.0 → 0.15.0)

**Constat de lecture du code** (`outils/mcp-graph/server.py`) : `workbook_archiver_gabarit` faisait un
`POST /drives/{…}/items/{item}/copy` — une **copie asynchrone** (202 + `Location`). Le nom n'était donc
**jamais libéré**, la collision persistait. La correction minimale et conforme :

- `workbook_archiver_gabarit` fait désormais un **DÉPLACEMENT** : `PATCH /drives/{…}/items/{item}` avec
  un nouveau `parentReference` (« 00 - Old » figé) et un **nom horodaté**. Le *move* au sein d'un même
  drive est **SYNCHRONE** (`200` avec l'item déplacé) — plus de `202`/poll, plus de faux-vert
  « 202 ≠ preuve ». **Au retour, le nom `gabarit-<code>.xlsx` est libéré.**
- **Toujours BORNÉ, jamais générique** : source résolue côté serveur (`_resoudre_item_gabarit`,
  `gabarit-<code_mission>.xlsx` de « 06 - Gabarit ERP »), destination figée (« 00 - Old ») ; l'appelant
  ne fournit que `code_mission` (assaini avant tout réseau). L'écriture reste **bornée par construction**
  (test `(21)` inchangé et vert). **Le fail-closed de `workbook_instancier_gabarit` n'est PAS touché.**
- **Réversible sans perte** : la version précédente est **conservée intacte** dans « 00 - Old ». Le
  rétablissement inverse (« 00 - Old » → racine) reste un **geste gardien** : aucune primitive n'expose
  le déplacement inverse (pas de surface générique).

## 5. Orchestration de la régénération (skill `consolidation-pilotage` v1.2 → v1.3)

La régénération d'un gabarit existant est désormais **machine**, portée par le skill (§5) :

1. lire la **saisie** (source) + transformer matriciel → long ;
2. lire l'**état courant** du gabarit (`workbook_lire_table` ×3) — absent → instanciation pure ;
3. **réconcilier en mémoire** (jamais de suppression : report des lignes disparues + anomalie ; jamais
   de rétrogradation d'un `validé` ; report des champs propres au gabarit type `LienFacture`) ;
4. **archiver (DÉPLACEMENT)** → « 00 - Old » : nom libéré, version conservée ;
5. **ré-instancier** (`workbook_instancier_gabarit`) : fail-closed satisfait (nom libre), sa **preuve
   FROIDE §8** atteste l'ouvrabilité ; échec après archivage → **anomalie §6, STOP** (état réversible) ;
6. **repeupler** les 3 tables (`workbook_ajouter_lignes`, un appel par table) ;
7. **contrôle post-écriture** + rapport de passage (dont le nom de l'archive « 00 - Old »).

**Idempotent** (contenu du gabarit actif identique au rejeu ; les archives s'accumulent = versionnage),
**réversible** (« 00 - Old »), **journalisé**. Mécanisme aligné sur `modele-donnees.md` §5.6.

## 6. Vérification (banc) — rouge puis vert

Aucun accès tenant côté agent (garde-fou : ne pas toucher au tenant ; pas de Graph réel en test).
Au banc, avec `httpx` mocké :

- **archivage = déplacement (nominal)** : l'archivage exécute **un `PATCH`** vers l'item avec
  `parentReference.id` = dossier « 00 - Old » figé + nom horodaté, rend `deplace=True` / `dossier=00 - Old`,
  et **aucun `POST /copy`** — le mock lève d'ailleurs sur tout `POST /copy` (garde-fou de test) ;
- **rouge → vert** : ce même test, exécuté contre l'ancien corps (`/copy`), échouait (aucun `PATCH`,
  un `POST /copy` interdit) ; il passe contre le corps corrigé ;
- **code invalide → refus avant réseau** : `code_mission` d'évasion → `ValueError` avant toute ouverture
  de client httpx ;
- **gabarit absent → `FileNotFoundError` sans `PATCH`** : on ne déplace pas ce qui n'existe pas ;
- **bornage inchangé** : `workbook_archiver_gabarit` n'expose toujours **aucune** cible libre (test `(21)`) ;
- **fail-closed instancier inchangé** : collision `FileExistsError`, preuve interne rouge, preuve froide
  403/corps → rollback — tous verts et **non modifiés** ;
- **heft : 73 tests verts** (`pytest`), +3 par rapport à la reprise n°3 (les 3 tests d'archivage-déplacement).
- **evals skills verts** : `consolidation-pilotage` 10/10 invariants (golden : régénération réconciliée,
  archivage = déplacement synchrone, cran, séquence de réconciliation — les ancres « fusion incrémentale »
  et « 202 n'est pas une preuve », périmées, remplacées).

## 7. Reste (mise en service gardien, hors périmètre agent)

- **Build + déploiement** de l'image serveur **0.15.0** (runbook gardien ; l'agent ne déploie pas).
- **Promotion** du skill `consolidation-pilotage` v1.3 (procédure allégée, gardien).
- **Épreuve tenant** — après déploiement, régénérer un gabarit **existant** (ex. `gabarit-1.xlsx`) :
  archiver-déplacer (le nom se libère, l'archive part dans « 00 - Old »), ré-instancier (preuve froide
  verte, plus de collision), repeupler depuis la saisie, relire count + invariants. Puis lecture
  **froide en Graph délégué** (cockpit) `200` sur les tables régénérées.
- **Ménage optionnel** — retirer de « 00 - Old » les deux copies surnuméraires laissées par l'épreuve
  du soir (§2), si le gardien le souhaite (facultatif, sans effet sur les gabarits actifs).
- L'agent n'a **rien mergé, rien déployé, rien touché au tenant**.
