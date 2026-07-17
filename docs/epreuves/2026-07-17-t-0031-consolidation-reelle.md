# Épreuve T-0031 (première consolidation réelle saisie → gabarit) — VERTE : 30 lignes, invariants vérifiés

Entrée d'épreuve du 2026-07-17 (session S37). Fait nouveau ; aucune requalification d'un soldé, aucune
réécriture d'entrée existante. **VERDICT : VERT.** Première exécution **réelle** d'une primitive Workbook
d'écriture par l'usage : consolidation `saisie → gabarit` des missions 1 (Siteflow) et 2 (Datalab) via
`workbook_ajouter_lignes`, contrôle post-écriture §5 ter vert. **T-0031 est soldé au sens gardien**
(première exécution réelle prouvée, condition de solde de la fiche). Zéro geste manuel du gardien cette
session hors merge de la PR.

## 1. Garde-fou SHA (vert)

- `git fetch origin` ; `origin/main` = `d18341281a0db2c48402b0a0e7142035ed0537b3` (préfixe `d1834128`
  attendu). Conforme → poursuite.
- `git checkout main && git pull` (fast-forward `bd5258e..d183412`) puis branche d'épreuve
  `t-0031/epreuve-consolidation-reelle` créée à partir de `main`.

## 2. Contexte serveur et coordonnées (vérifiés)

- **Serveur MCP allia-graph 0.13.0** branché au projet CLI IA-scale en **jeton délégué frais**.
- **Preuve de vie MCP (étape 0)** : les 5 primitives `workbook_*` visibles côté CLI
  (`workbook_lire_table`, `workbook_ajouter_lignes`, `workbook_maj_ligne`,
  `workbook_archiver_gabarit`, `workbook_instancier_gabarit`).
- **Gabarits cibles** : instanciés **VIDES** ce jour (T-0033 soldé, `count:0 × 6` prouvé). Drive
  Contrats-et-administratif `b!44CicXj16kaqbdbelsTnPUundQ8Qe5JKmBk7kAxljRO8Hx-KrTj1QJbs4Mp6eHK7` ;
  gabarit-1.xlsx `01BWFCBZFLKYKV5TRV4JGJYMFBDGAZUTQA`, gabarit-2.xlsx `01BWFCBZATQHKNZ6BWHRBJF6E52CL2OBF4`.
- **Saisies (lecture déléguée, SKILL §2 — le MCP ne peut PAS lire les saisies, 403 architectural)** :
  drive Management-et-Gestion `b!RDlbCyP2okiouOcWTO8j4VMiGodDa-lGrhevWa_Fe7IZ5zSujeUVRLqhOfRJedGI` ;
  saisie-1-siteflow.xlsx `013OHVIUF4ZOYRBRIC3NDJTWYOABSZUMKD`,
  saisie-2-Datalab.xlsx `013OHVIUGCL3BA65GWWRG24PCZKMS3OLYT`. Coordonnées relues ce jour par le copilote
  de gouvernance ; contre-lecture agent via `read_resource` (outil M365). Saisies **inchangées depuis
  le 14/07**.

## 3. Étape 0 — préconditions (aucune écriture)

- **Garde anti-écrasement** : `workbook_lire_table` sur les **6 tables** des 2 gabarits →
  `count:0 × 6` (état conforme, personne n'a écrit entre-temps).
- **Décision « pas d'archivage préalable » (motivée)** : `workbook_archiver_gabarit` (§5 bis) protège
  un **contenu antérieur** avant écrasement. Les gabarits ayant été **instanciés vides et créés ce
  jour** (T-0033), il n'y a **rien à archiver** (création pure, exception explicite §5 bis / §3). Aucun
  archivage préalable exécuté — décision consignée.
- **Contre-lecture des saisies** (lecture déléguée) : `CodeMission=1` partout dans saisie-1,
  `CodeMission=2` partout dans saisie-2 (conforme) ; matrices **concordantes** avec les données de
  référence de l'étape 1 (aucune divergence).

## 4. Étape 2 — écriture (les seules écritures de l'épreuve)

`workbook_ajouter_lignes` (écriture BORNÉE par construction : l'appelant ne passe que `code_mission`,
jamais de `drive_id`/`item_id` ; cible = `gabarit-<code>.xlsx` de « 06 - Gabarit ERP » résolue côté
serveur). Transformation matriciel → long (SKILL §4 : valeurs > 0 uniquement, `Mois` au 1er du mois,
statuts normalisés accentués, `LienFacture` vide). **5 appels** (T_Imputations m2 sauté — aucun
réalisé). **Retours bruts** :

| # | code_mission | table | `ajoutees` |
|---|---|---|---|
| 1 | 1 (Siteflow) | T_Affectations | **8** |
| 2 | 1 (Siteflow) | T_Imputations  | **2** |
| 3 | 1 (Siteflow) | T_Echeancier   | **8** |
| 4 | 2 (Datalab)  | T_Affectations | **6** |
| 5 | 2 (Datalab)  | T_Echeancier   | **6** |

**Total écrit : 30 lignes** (18 pour m1, 12 pour m2). Aucune erreur ; aucune retentative.

## 5. Étape 3 — contrôle post-écriture §5 ter (anti-faux-vert), relecture des 6 tables

`workbook_lire_table` sur les 6 tables :

| gabarit | table | count relu | attendu |
|---|---|---|---|
| gabarit-1 (Siteflow) | T_Affectations | **8** | 8 ✓ |
| gabarit-1 (Siteflow) | T_Imputations  | **2** | 2 ✓ |
| gabarit-1 (Siteflow) | T_Echeancier   | **8** | 8 ✓ |
| gabarit-2 (Datalab)  | T_Affectations | **6** | 6 ✓ |
| gabarit-2 (Datalab)  | T_Imputations  | **0** | 0 ✓ |
| gabarit-2 (Datalab)  | T_Echeancier   | **6** | 6 ✓ |

**Invariants recalculés sur les valeurs RELUES** :

- Σ JoursPrevus : m1 = 17+22+23+7+22+22+21+14 = **148** ✓ ; m2 = 23+15+22+22+21+17 = **120** ✓.
- Σ MontantHT : m1 = **133 200 €** ✓ ; m2 = **84 000 €** ✓.
- Chaque MontantHT = JoursPrevus du même mois × TJM (900 m1 / 700 m2) : vérifié ligne à ligne.
- Réalisé : m1 = mai 17 + juin 22 (2 lignes, Σ 39) ✓ ; m2 = néant (0 ligne) ✓.

Observations de round-trip (non bloquantes) : les dates écrites `AAAA-MM-JJ` reviennent en **série
Excel** (46143 = 2026-05-01, …) — coercition native du service Excel, valeurs intactes ; `CodeMission`
revient en **entier** (Excel coerce la chaîne numérique) — la clé métier reste identifiable. Statuts
accentués (`émise`, `à émettre`, `à valider`) et `LienFacture` vide préservés à la relecture.

**6/6 verts.** Passage prouvé (relecture de contrôle effectuée).

## 6. ANOMALIES SIGNALÉES (au gardien — jamais résolues par l'agent)

Conformément au SKILL §6 (anomalies signalées, jamais résolues seul) :

1. **Doublons de `NumFacture` ENTRE les deux missions** : `F-2026-003` → `F-2026-008` apparaissent à la
   fois dans `T_Echeancier` de gabarit-1 (mission 1) et de gabarit-2 (mission 2). **État transitoire
   pré-T-0030** (SKILL §6). **Aucune renumérotation par l'agent** — signalement gardien.
2. **Statuts de saisie non accentués** : la saisie porte `Emise` / `a emmettre` (non accentués, faute
   de frappe incluse) ; **normalisés à la consolidation** en `émise` / `à émettre` (statuts normalisés
   accentués, SKILL §4), **conformément au journal S35**. Signalé pour trace, aucune action tenant
   requise.

## 7. Écart documentaire relevé (transparence)

Le modèle de texte de solde dicté dans l'ordre d'épreuve mentionnait « 28 lignes écrites ». Le compte
**réel et vérifié** (données de référence 8/2/8 + 6/0/6, retours `ajoutees`, relecture §5 ter) est de
**30 lignes**. Le présent journal et la fiche T-0031 consignent le compte réel **30**, par fidélité au
résultat prouvé.

## 8. Conclusion

La **condition de solde de T-0031** est satisfaite : première exécution **réelle** d'une primitive
Workbook d'écriture par l'usage (skill de consolidation écrivant deux vrais gabarits sur le tenant),
contrôle post-écriture §5 ter **vert** (8/2/8 et 6/0/6 ; Σ 133 200 € et 84 000 € ; 148 j et 120 j).
Écriture **bornée par construction** honorée (`code_mission` seul). Fusion incrémentale sans suppression
(gabarits vides → ajout pur).

**Purge post-épreuve (geste gardien)** : `claude mcp remove allia-graph` — l'épreuve économique est
close ; le branchement délégué est retiré du projet CLI.
