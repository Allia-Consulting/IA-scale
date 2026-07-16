# Épreuve T-0033 (reprise tenant) — STOP n°1 de reprise à l'étape 0 : la souche déposée est illisible par l'API Workbook (501)

Entrée d'épreuve du 2026-07-16 (session S36), **reprise après le STOP n°1 consigné en PR #225 (mergée,
`220c9621`)**. Fait nouveau ; aucune requalification d'un soldé, aucune réécriture d'entrée existante.
**T-0033 reste `à_faire`** : la reprise ne s'est PAS soldée — arrêt à **l'étape 0 (preuve d'intégrité de
la souche)**, AVANT toute ré-instanciation. **Aucune écriture émise par la machine** cette session (que
des lectures) ; **tenant strictement inchangé** par rapport à l'état laissé par le copilote (§4). Zéro
geste manuel du gardien.

But visé : prouver l'intégrité de la souche propre déposée sur le tenant, ré-instancier les deux gabarits
actifs (Siteflow = code 1, Datalab = code 2), prouver `count:0 × 6`. **Non atteint** : la souche déposée
est **illisible** par l'API Workbook de Graph (501 sur les 3 tables), donc son intégrité **n'est pas
prouvée** — elle est même infirmée (§3). Ré-instancier depuis une souche cassée aurait propagé le défaut :
arrêt.

## 1. Garde-fou SHA (vert)

- `git fetch origin` ; `origin/main` = `220c9621fea3a125093ade4eef3d066a3c8f7195`.
- `220c9621` (merge PR #225) est **ancêtre de `origin/main`** (`ANCESTOR_OK`) — en fait il **EST** le tip.
- Branche de travail créée depuis `main` à jour : `feat/t0033-tenant-reprise`.

## 2. Gestes du copilote de gouvernance (surface déléguée, identité gardien — AUCUN geste manuel)

Repris du contexte de reprise et **re-vérifiés par relecture déléguée** (§4) :

- **Archivage** (3 × `MoveToUsingPath`, HTTP 200) vers « 00 - Old » :
  - `gabarit-1.xlsx` (22 592 o) → `gabarit-1-pollue-s35-archive-2026-07-16.xlsx`
  - `gabarit-2.xlsx` (22 551 o) → `gabarit-2-pollue-s35-archive-2026-07-16.xlsx`
  - `gabarit-pilotage-mission.xlsx` pollué (22 594 o) → `gabarit-pilotage-mission-pollue-s35-archive-2026-07-16.xlsx`
  - « 06 - Gabarit ERP » relu **vide** après déplacement. **Confirmé** : « 00 - Old » pèse désormais
    67 737 o = 22 592 + 22 551 + 22 594 (les 3 fichiers pollués), et les noms `gabarit-1/2` sont libres.
- **Dépôt** (`AddUsingPath`, HTTP 200) : souche propre du canon
  (`contrats/socle/gabarit-pilotage-mission.xlsx` à HEAD, **9 886 o**) déposée dans « 06 - Gabarit ERP ».
  - **POINT DE VIGILANCE (levé — défavorablement) :** SharePoint a réécrit le binaire à l'ingestion,
    **Length persistée 17 656 o** (≠ 9 886 o du canon). L'intégrité des tables était donc à prouver
    (étape 0). **Résultat : NON prouvée — infirmée** (§3).

État de « 06 - Gabarit ERP » avant la reprise (et après, cf. §4 — inchangé) :

| Fichier | Length (o) | item id |
|---|---|---|
| `gabarit-pilotage-mission.xlsx` (souche déposée) | 17 656 | `01BWFCBZCNPTXAWFWVAVFKJVRPDJDBM5PK` |
| `00 - Old` (dossier, 3 archives) | 67 737 | `01BWFCBZADO5QA7ZWTUBGZSBGWWCKQZH65` |

(drive « Documents partages » `b!44CicXj16kaqbdbelsTnPUundQ8Qe5JKmBk7kAxljRO8Hx-KrTj1QJbs4Mp6eHK7`,
« 06 - Gabarit ERP » `01BWFCBZHUYHKQWWD2IZDLEAVEXO4PVCFS`.)

## 3. Étape 0 — PREUVE D'INTÉGRITÉ : ÉCHEC (501 sur les 3 tables) → STOP n°1 de reprise

`workbook_lire_table` (allia-graph, identité managée) sur les 3 tables de la souche déposée
(item `01BWFCBZCNPTXAWFWVAVFKJVRPDJDBM5PK`) — **réponses brutes** :

```
workbook_lire_table(…, table=T_Affectations)
→ Error: Server error '501 Not Implemented' for url
  .../items/01BWFCBZCNPTXAWFWVAVFKJVRPDJDBM5PK/workbook/tables/T_Affectations/rows

workbook_lire_table(…, table=T_Imputations)
→ Error: Server error '501 Not Implemented' for url
  .../items/01BWFCBZCNPTXAWFWVAVFKJVRPDJDBM5PK/workbook/tables/T_Imputations/rows

workbook_lire_table(…, table=T_Echeancier)
→ Error: Server error '501 Not Implemented' for url
  .../items/01BWFCBZCNPTXAWFWVAVFKJVRPDJDBM5PK/workbook/tables/T_Echeancier/rows
```

Les **3 tables** renvoient **501 Not Implemented** : l'API Workbook n'ouvre PAS ce classeur. Ce n'est ni
un `count ≠ 0` ni une table manquante (404) — c'est **pire** : le classeur dont dépendent la
ré-instanciation ET la preuve `count:0` est **illisible**. Le critère « les 3 tables existent et count:0
chacune » est donc **non satisfait**. Conformément à la règle (STOP au premier incident, zéro retouche),
**arrêt AVANT toute ré-instanciation**. `workbook_instancier_gabarit` **n'a PAS été appelée** (instancier
depuis une souche cassée aurait fabriqué deux gabarits cassés).

*Contrôle de non-régression du MCP : ce n'est pas le serveur ni le jeton qui sont en cause — plus tôt
cette session, `workbook_lire_table` a lu sans erreur l'ancien `gabarit-1` (retour `count:1`). Le 501 est
spécifique à ce binaire.*

### Diagnostic (évidence locale sur le binaire canon 9 886 o)

Inspection **locale** (non mutante) de `contrats/socle/gabarit-pilotage-mission.xlsx` (HEAD) :

- **Chaînes en ligne, pas de table de chaînes partagées** : les cellules d'en-tête sont écrites en
  `t="inlineStr"` et le classeur **ne contient aucun `xl/sharedStrings.xml`** (trait openpyxl ;
  `xl/_rels/workbook.xml.rels` ne référence pas de `sharedStrings`).
- **Tables SANS corps de données** : chaque table est définie avec `ref` = **la seule ligne d'en-tête** :
  - `T_Affectations` : `ref="A1:D1" headerRowCount="1"`
  - `T_Imputations` : `ref="A1:E1" headerRowCount="1"`
  - `T_Echeancier` : `ref="A1:G1" headerRowCount="1"`
  C'est exactement la forme « en-têtes seuls, 0 ligne de corps » que T-0033 (1/2) a fabriquée pour
  obtenir `count:0`. Or une table nommée dont le `ref` ne couvre **que** l'en-tête (hauteur de corps
  nulle) est précisément ce que l'API Workbook refuse d'ouvrir. **Contraste** : les gabarits
  précédemment lisibles avaient un corps (`ref …:D2`, `count ≥ 1`, cf. STOP n°3 de S35).

**Hypothèse de tête (fortement étayée par la structure locale)** : le défaut vient de la **forme du
gabarit canon** — table « en-tête seul » (± chaînes en ligne) que l'API Workbook n'ouvre pas — et la
réécriture SharePoint (9 886 → 17 656 o) **ne l'a pas rendu ouvrable**. Autrement dit, la cible même de
T-0033 (une table qui lit `count:0`) et sa réalisation actuelle (table sans corps produite par openpyxl)
sont **en tension** avec l'API Workbook.

**Ce que cette session NE PEUT PAS trancher** : impossible d'isoler avec certitude « défaut du binaire
canon » (H2) de « corruption par la réécriture SharePoint » (H1), faute de chemin d'écriture Graph
délégué côté agent pour redéposer le binaire **9 886 o brut** (octet-fidèle) et le relire. C'est la
première tâche de la reprise. L'évidence locale (structure atypique du binaire canon, indépendante de la
réécriture) désigne néanmoins H2 comme cause principale.

## 4. État exact du tenant après l'arrêt — INCHANGÉ

Relecture de « 06 - Gabarit ERP » **après** l'arrêt (identique au début de reprise) :

```
00 - Old                        (folder, 67737 bytes)  01BWFCBZADO5QA7ZWTUBGZSBGWWCKQZH65   [3 archives pollués]
gabarit-pilotage-mission.xlsx   (file, 17656 bytes)    01BWFCBZCNPTXAWFWVAVFKJVRPDJDBM5PK   [souche déposée, ILLISIBLE 501]
```

Aucun `gabarit-1.xlsx` / `gabarit-2.xlsx` (ré-instanciation **non exécutée**). La machine n'a émis que
des lectures ; **rien n'a été créé, déplacé, supprimé ou écrit** cette session.

## 5. Reprise proposée

1. **Isoler H1/H2** (nécessite un chemin d'écriture Graph délégué — copilote de gouvernance ou connecteur
   M365 en écriture) : redéposer le binaire canon **9 886 o octet-fidèle** (sans réécriture SharePoint —
   p. ex. upload de session Graph, ou dépôt vérifié par hash) puis relire via `workbook_lire_table`.
   - Si toujours **501** → **H2 confirmé** : le gabarit canon (openpyxl, table « en-tête seul ») n'est
     pas ouvrable par l'API Workbook → corriger le **générateur T-0033 (1/2)**.
   - Si **count:0** → **H1 confirmé** : la réécriture SharePoint corrompt → figer une méthode de dépôt
     octet-fidèle.
2. **Corriger la souche pour qu'une table VIDE soit lisible `count:0` par l'API Workbook** (probable, si
   H2) : produire les tables via un moteur que Graph accepte — round-trip Excel/LibreOffice de
   normalisation, **ou** création des tables via l'API Workbook elle-même (`POST …/worksheets/{id}/tables`
   avec en-têtes) qui donne une table vide native lisible `count:0`. Re-promouvoir le binaire au canon
   (nouvelle boucle T-0033 1/2), avec une **épreuve de lecture Graph** ajoutée au golden (empêche qu'un
   binaire illisible reparte au canon).
3. **Rejouer la reprise tenant** : archiver la souche cassée déposée → « 00 - Old », déposer la souche
   corrigée, **re-prouver l'étape 0 (count:0 × 3 sur la souche)**, puis `instancier ×2` et `count:0 × 6`.

Note : les codes mission (Siteflow = 1, Datalab = 2, cf. journal S35 mergé) n'ont pas eu à être
reconfirmés en référentiel cette session — la ré-instanciation n'a pas été atteinte (STOP à l'étape 0).

## 6. Fait nouveau consigné — leçon durable

**« En-têtes seuls » (0 ligne de corps) obtenu par table openpyxl à `ref` d'en-tête seul rend le classeur
ILLISIBLE par l'API Workbook (501), alors qu'une ligne de corps vide donne `count:1` (STOP n°3 de S35).**
Le `count:0` visé doit donc être produit par une table **vide mais valide au sens de l'API Workbook**
(round-trip Excel ou création via l'API Graph), pas par une table amputée de son corps. Toute promotion
future de la souche doit être **gardée par une épreuve de lecture Graph** (`workbook_lire_table` →
`count:0`), pas seulement par une vérification openpyxl locale. Journalisé comme fait nouveau ; aucune
entrée existante réécrite.

## 7. Isolation H1/H2 (post-STOP, copilote) — 2026-07-16

Après le STOP de §3, le copilote de gouvernance (surface déléguée, REST SharePoint depuis Chrome) a mené
l'isolation H1 (réécriture SharePoint) / H2 (défaut du binaire canon) que l'agent ne pouvait pas trancher
faute de chemin d'écriture Graph délégué. **Aucun nouveau geste tenant demandé à l'agent** : les faits
ci-dessous sont **relus sur l'état persisté** et consignés ici (les sections §1–§6 ne sont pas réécrites).

**Test A — fidélité des octets à l'ingestion.** Le fichier déposé (17 656 o, `sha256[0:16] =
2ee570bdc051447a`) **diffère** du binaire canon (9 886 o, `sha256[0:16] = 48b875a192dd5a6c`). → SharePoint
**réécrit** le paquet openpyxl à l'ingestion (le dépôt n'est pas octet-fidèle pour ce binaire).

**Test B — innocence du chemin de dépôt.** Le `gabarit-1` archivé (**Excel-authored**, 22 592 o) a été
**redéposé par le MÊME chemin** (`AddUsingPath`) → ressort **22 592 o, strictement identique**, non
réécrit. Le fichier d'essai `_test-lecture-excel-authored.xlsx` a été **recyclé après test**.

**Verdict — H2 CONFIRMÉ.** Le chemin de dépôt et l'ingestion des fichiers **Excel canoniques** sont
**innocentés** (Test B) ; c'est le **binaire openpyxl** (tables **sans ligne de corps** + packaging non
canonique) qui **déclenche la normalisation SharePoint** et finit **501**. Contre-preuve directe de H1.
**Fait de fond** : **Excel lui-même ne produit pas de table à zéro ligne** — un `count:0` fiable doit être
**FABRIQUÉ PAR LE SERVICE** (API Workbook), **pas** par un binaire tiers déposé.

**État final du tenant (relu).** « 06 - Gabarit ERP » : **VIDE** (aucun gabarit actif — cohérent avec
l'honnêteté du cockpit, « aucun gabarit actif lu »). « 00 - Old » contient :

| Fichier archivé | Length (o) |
|---|---|
| `gabarit-1-pollue-s35-archive-2026-07-16.xlsx` | 22 592 |
| `gabarit-2-pollue-s35-archive-2026-07-16.xlsx` | 22 551 |
| `gabarit-pilotage-mission-pollue-s35-archive-2026-07-16.xlsx` | 22 594 |
| `gabarit-pilotage-mission-openpyxl-illisible-501-2026-07-16.xlsx` | 17 656 |

(La souche cassée déposée a donc été elle-même archivée sous un nom parlant ; le domicile actif est propre
et vide, prêt pour une instanciation saine.)

## 8. Décision d'architecture retenue (arbitrage copilote — porte gardien à la PR)

**Instanciation API-native.** Faire **évoluer le serveur MCP** (`outils/mcp-graph`) pour que la primitive
d'instanciation **v2** crée les **3 tables via l'API Workbook** (`tables/add` sur la plage d'en-têtes
§5.2, `hasHeaders=true`) sur une **base service-authored**, garantissant par construction des **tables à
0 ligne lisibles** (`count:0`). Le **binaire souche openpyxl cesse d'être le vecteur des tables** — il ne
porte plus (au mieux) que la mise en forme / les en-têtes, la structure de tables étant matérialisée par
le service Excel lui-même.

**À instruire en S37** (aucune écriture ce jour) :
- conception **lue du code réel** du serveur (`outils/mcp-graph/server.py` — signatures/docstrings des
  primitives Workbook), avant tout amendement ;
- amendement de la **fiche T-0033** (produit / critères d'acceptation : l'instanciation API-native
  remplace le « instancier par copie de souche » comme voie du `count:0`) ;
- retouche éventuelle de **`modele-donnees.md` §5.6** (rôle exact de la souche une fois les tables
  service-authored) ;
- **build + déploiement** de l'image serveur (runbook gardien) ;
- **golden gardé par une épreuve de LECTURE Graph** (`workbook_lire_table → count:0`) pour interdire tout
  retour d'un binaire illisible.

Journalisé comme fait nouveau ; aucune entrée existante réécrite.
