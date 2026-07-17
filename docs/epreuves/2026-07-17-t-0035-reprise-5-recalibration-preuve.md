# Épreuve T-0035 (reprise n°5) — recalibrage de la preuve « vierge » + rollback vérifié

Entrée d'épreuve du 2026-07-17 (rouge → vert). Fait nouveau ; aucune requalification d'un soldé, aucune
réécriture d'entrée existante. **T-0035 reste `en_cours`.** La reprise n°4 (régénération machine d'un
gabarit existant) a été **éprouvée sur le tenant le soir du 17/07 et a échoué** : c'est le **rouge** de
cette entrée. Le diagnostic a d'abord accusé un binaire de fabrication non canonique et prescrit un
retour à une **souche binaire copiée** ; des **faits mesurés** ont invalidé cette piste. La correction
porte sur le **prédicat de preuve** et le **rollback** de `workbook_instancier_gabarit` — entrée
**jumelée** à `T-0033` (fabrication). Historique immuable — cette entrée s'ajoute, elle n'efface rien.

## 1. Garde-fou SHA (vert)

- `git fetch origin` ; `origin/main` = `0b5d6223eae0355eb256b673e5e5e1f159474b31` (merge PR #236, reprise
  n°4). Branche d'épreuve `t-0035/reprise-5-souche-binaire` depuis ce point.

## 2. Rouge — l'épreuve tenant du soir (régénération machine des 2 gabarits)

Régénération des gabarits des missions T-0031 (CodeMission 1 Siteflow, 2 Datalab) via le skill
`consolidation-pilotage` v1.3, serveur `0.15.0` (rév `--0000022`), jeton délégué. Deux défauts :

- **Défaut A — preuve FROIDE rouge.** `workbook_instancier_gabarit(1)`, après un archivage-déplacement
  réussi (`deplace:true`, archive `gabarit-1-20260717T135949Z.xlsx` en « 00 - Old »), a levé — verbatim :
  > `preuve FROIDE : la table T_Affectations porte 1 ligne(s) de corps (count:0 attendu à froid). Instanciation avortée — l'item créé est supprimé.`
- **Défaut B — le rollback a MENTI.** L'erreur annonçait l'item supprimé ; le listing de « 06 - Gabarit
  ERP » pris juste après montrait `gabarit-1.xlsx` **toujours présent**, item **nouveau**
  `01BWFCBZHMHXN46WR2EFDJQFBLFKT7NXNP`, **16878 o** — l'artefact avorté, non nettoyé.

## 3. Les trois faits mesurés (qui réorientent le cap)

1. **Binaire de fabrication service** (`gabarit-1.xlsx`) inspecté : tables `ref='A1:X2'` + `insertRow='1'`.
   La « ligne de corps » vue à froid est la **LIGNE D'INSERTION** standard d'une table Excel vide — pas
   un défaut de sérialisation.
2. **Binaire Excel authentique** (`test-table-vide.xlsx`, Microsoft Macintosh Excel, table créée sans
   données) : `ref='A1:D3'` — **deux** lignes de corps vides. Excel non plus ne produit pas de table
   « header-only » : la voie **souche copiée** (`/copy`) échouerait `count:0` **à l'identique**.
3. La **preuve froide de la reprise n°4** lisait déjà les colonnes **à froid sans `403`** (fabrication
   `0.14+` ouvrable à froid), et les gabarits **peuplés** relisent juste (`8/2/8`, `6/0/6`) : le
   **peuplement résorbe** la ligne d'insertion.

**Conséquence** : le binaire n'est pas en cause ; le **prédicat de preuve** (`count:0` strict) l'était.
La voie « souche binaire copiée » est **évaluée puis écartée**. Décision gardien : **fabrication service
conservée**.

## 4. Correctif (serveur 0.15.0 → 0.16.0)

- **A. Prédicat « vierge » recalibré** (preuves interne §5 `/rows` ET FROIDE §8 `/columns`) : une table
  fraîchement fabriquée est vierge si elle porte ses **en-têtes §5.2 exacts** et **aucune ligne de corps
  PLEINE** (portant une valeur) — les lignes **entièrement vides** (ligne d'insertion) sont **tolérées**.
  Le juge n'est **pas affaibli** : une ligne portant une valeur échoue toujours. Le retour porte
  `tables[*] = {lignes_vides: N}` (au lieu d'exiger `0`).
- **B. Rollback borné ET VÉRIFIÉ** : après le `DELETE`, l'item est **relu** (`GET` → `404` attendu) ; la
  suppression n'est annoncée **que prouvée**, sinon le statut est honnête (« rollback incomplet, item à
  retirer par le gardien »). Fin des annonces non vérifiées (défaut B).

Aucune souche binaire réintroduite ; `conflictBehavior=fail` et le bornage (cible figée côté serveur,
`code_mission` seul) **inchangés**.

## 5. Vert — la suite unitaire recalibrée

`python -m pytest tests/test_garde_fous.py -q` → **76 passed**. Cas saillants :

- **ligne d'insertion vide = PASS** (1 ou 2 lignes vides ; `lignes_vides` rapporté) — la régénération
  n'avorte plus à tort ;
- **ligne portant une valeur = FAIL**, à froid (§8) **et** en session (§5) — le juge tient ;
- **preuve froide `403` → rollback VÉRIFIÉ** (`DELETE` + `GET 404`, message « rollback vérifié ») ;
- **rollback INCOMPLET** (`GET 200`) → message « ROLLBACK INCOMPLET … gardien », **jamais** « vérifié » ;
- collision `fail` (409) → `FileExistsError`, aucun rollback ; retry `504` sur `tables/add` → PASS.

Reproduction du `403`/de la ligne d'insertion sur Graph réel non faisable au banc (pas de Graph réel,
tenant intact) : simulée fidèlement par le mock (`lignes_insertion`, `pollue_rows`/`pollue_columns`,
`verify_get_status`).

## 6. Canon aligné (candidats, entrées de changelog ajoutées — jamais réécrites)

- `contrats/socle/modele-donnees.md` **v1.22** (§5.6, prédicat vierge recalibré) ;
- `skills/consolidation-pilotage/SKILL.md` **v1.4** (§3/§5/§8) ;
- `contrats/socle/table-des-crans.yaml` **v1.12** (cran `instancier_gabarit_pilotage` **inchangé** ;
  description alignée sur la fabrication service) ;
- `outils/mcp-graph/README.md` (prédicat vierge, rollback vérifié, image serveur **0.16.0**).

## 7. État tenant (réversible — geste gardien) & reste à faire

- `gabarit-1.xlsx` **défectueux** en racine (item `01BWFCBZHMHXN46WR2EFDJQFBLFKT7NXNP`, 16878 o) à
  **remplacer** à la mise en service ; bonne version dans « 00 - Old » (`gabarit-1-20260717T135949Z.xlsx`,
  18977 o) ; `gabarit-2.xlsx` **intact**.
- **RIEN mergé/déployé, tenant intact.** Restent gestes **gardien** : build + déploiement **0.16.0** ;
  promotion des candidats (modele-donnees v1.22, skill v1.4, table-des-crans v1.12) ; **épreuve tenant**
  (régénérer un gabarit existant : archiver-déplacer → ré-instancier **vierge** froid → repeupler →
  relecture) ; nettoyage de l'artefact défectueux en racine.
