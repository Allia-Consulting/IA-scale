# Épreuve — première dérivation née du rituel des temps (mission 4)

> **Date** : 1er août 2026, ~18h49 UTC (S46). **Chantier** : `T-0046` (rituel des temps).
> **Verdict** : **VERTE**. **Anomalie** : aucune.
> **Nature** : première dérivation **née d'une déclaration du rituel** — ET non-régression du
> dérivateur `consolidation-pilotage` **v1.6** sur une **saisie fraîche** (mission jamais dérivée).

## 1. La chaîne à l'épreuve

| Maillon | Version éprouvée |
|---|---|
| Dépôt | `main` = `729e324` (merge PR #294) |
| Règle | `modele-donnees.md` **§5.6 v1.29** — *promu* (rituel des temps institué le 01/08) |
| Dérivateur | `skills/consolidation-pilotage/SKILL.md` **v1.6** — *promu* |
| Serveur MCP | image **0.22.0** (`lire_saisie_table` bornée, ETag exposés) |
| Source | `saisie-4-CockpitM365.xlsx`, eTag `{4A817C3E-…},15`, mtime `2026-08-01T18:28:30Z` |

Ce que cette épreuve démontre, et qu'aucune précédente ne démontrait : la §5.6 v1.29 décrit un
**geste humain récurrent** (déclarer son mois) ; l'épreuve prouve que **ce geste-là**, posé dans la
grille par un humain, traverse la chaîne jusqu'au gabarit **sans qu'un seul chiffre soit forgé**.
T-0045 avait prouvé le **lecteur** sur une saisie ancienne ; ici la saisie est **fraîche** et la
mission **jamais dérivée**.

## 2. La déclaration du rituel (bootstrap gardien)

Premier passage du rituel institué le jour même : le gardien déclare **POUR** Yousra — bootstrap
assumé, l'écran de déclaration n'existant pas (nommé, non construit). Déclaration : **5 jours,
mission 4, juillet 2026**, posée sur **sa ligne**, à la **position 7**, sous son identifiant §5.3
(`yousra.boukiaou@allia-consulting.com`).

## 3. Mesures — lecture (`lire_saisie_table`, app-only `role=read`)

### 3.1 `SAISIE_Realise_2026` — 21 lignes servies, 14 colonnes

| Ligne servie | Traitement | Motif |
|---|---|---|
| `Nb. jours ouvres max` (22,20,22,22,21,22,23,21,22,22,21,23) | **écartée** | entête technique — plafond de calendrier, pas une ressource (§4 bis) |
| `yousra.boukiaou@…` — position 7 = **5**, TOTAL **5** | **retenue** | seule ligne de sens |
| 19 lignes `TOTAL = 0` | **écartées** | lignes fantômes de la zone pré-dimensionnée (§4 bis) |

Les onze autres positions de la ligne retenue sont des **cellules VIDES** — ni comptées, ni
resserrées. C'est le point exact où l'épreuve 3g avait perdu 22 j : ici la position **tient**.

### 3.2 `SAISIE_Prevu_2026` — mesuré, aucun attendu fourni

Ligne Yousra : juillet 5 · août 21 · septembre 22 · octobre 22 · novembre 21 · décembre 18 —
**TOTAL 109**. Même entête technique et mêmes 19 lignes fantômes écartées.

### 3.3 `SAISIE_Facturation` — mesuré

Une seule ligne de sens : `2026-07-cockpitM365` · MoisCA `2026-07` · MontantHT **3 350** ·
Echeance **46235** · Statut **`a emettre`**.

**Sérial Excel normalisé** (piège consigné, épreuve `inscrire_cout_structure` 0.20.0 → 0.20.1) :
`46204` = **2026-07-01**, `46235` = **2026-08-01**. L'échéance tombe donc au 1er du mois suivant le
CA — même patron que la mission 1.

**Aucune ligne au statut `émise`** → **`allouer_num_facture` n'a PAS été appelé**. Le cran
**validé** de l'allocation (skill §7) n'a pas été sollicité par cette épreuve : elle est
intégralement restée en crans **auto**.

### 3.4 Contrôles §4 ter, à blanc, AVANT toute écriture

| Contrôle | Mesure | Verdict |
|---|---|---|
| Par ligne retenue — Σ douze positions == TOTAL (Réalisé) | 5 == 5 | **vert** |
| Par ligne retenue — Σ douze positions == TOTAL (Prévu) | 5+21+22+22+21+18 = 109 == 109 | **vert** |
| Miroir mission — Σ `JoursRealises` dérivés == Σ TOTAL retenus | 5 == 5 | **vert** |

### 3.5 Ressource au référentiel (§6)

`yousra.boukiaou@allia-consulting.com` est **présente** dans `T_Ressources` (salarié, CoutJour
`418,348623853211`). L'identifiant de la saisie est **caractère pour caractère** celui du
référentiel — la couture §5.3 tient. **Aucune anomalie « ressource inconnue »** ; le référentiel
n'a **pas** été écrit (lecture seule).

### 3.6 Baseline des gabarits, avant écriture

| Gabarit | eTag | mtime |
|---|---|---|
| `gabarit-1.xlsx` | `{AFCF6079-F554-44BA-80FB-CDEB2B826092},9` | `2026-08-01T17:15:48Z` |
| `gabarit-2.xlsx` | `{644CACC0-A8F6-4C0E-AB44-F9FE5DFEBA5B},8` | `2026-07-31T16:55:59Z` |
| `gabarit-4.xlsx` | `{7690D987-B43A-4318-9F5A-E58DC760BDF3},6` | `2026-07-26T11:36:15Z` |

`gabarit-4` **intégralement vierge** : les trois tables relues à `count: 0`. Le fait « instancié le
26/07, jamais peuplé » est donc **mesuré**, non supposé — rien à réconcilier, mais la séquence §5
reste la séquence (régénération, non instanciation pure).

## 4. Écriture — séquence §5 du skill v1.6 (crans auto, cible bornée gabarit-4)

1. **Archivage par DÉPLACEMENT** → `gabarit-4-20260801T184907Z.xlsx` dans « 00 - Old »,
   `deplace: true`. **Preuve que c'est bien un déplacement et non une copie** : l'archive porte
   l'`item_id` **de l'original** (`01BWFCBZEH3GIHMOVUDBBZ6WXFRXDWBPPT`) et la racine
   « 06 - Gabarit ERP » n'en garde aucune trace — le nom est libéré.
2. **Ré-instanciation** — `workbook_instancier_gabarit(4)` : fail-closed satisfait sans collision,
   **preuve FROIDE verte** sur les 3 tables (`lignes_vides: 1` chacune — la ligne d'insertion Excel,
   tolérée depuis la reprise n°5). Nouvel `item_id` `01BWFCBZHZLUJAAK6QVVCL456Y6PHJLGGF`.
3. **Repeuplement** — un seul appel par table : `T_Affectations` 6 · `T_Imputations` 1 ·
   `T_Echeancier` 1.

## 5. Preuves — relecture à froid du gabarit régénéré

`T_Imputations` — **1 ligne, et une seule** :

```
[4, "yousra.boukiaou@allia-consulting.com", 46204, 5, "à valider"]
```

`46204` = **2026-07-01**. `JoursRealises` **5**. `StatutValidation` « **à valider** » (§5.2 — les
lignes dérivées naissent à valider, aucune validation outillée en v1). **Aucun autre mois n'existe
dans la table** : les onze mois vides de la saisie sont **absents**, pas à zéro — aucun mois forgé.

`T_Affectations` — 6 lignes (46204→5, 46235→21, 46266→22, 46296→22, 46327→21, 46357→18).
`T_Echeancier` — 1 ligne : `["", 4, "2026-07-cockpitM365", 46204, 3350, 46235, "à émettre", ""]`,
`NumFacture` **vide** comme il se doit pour une ligne non émise.

### Contrôles §5 ter, après écriture

| Contrôle | Mesure | Verdict |
|---|---|---|
| Nombre de lignes == jeu régénéré | 6 / 1 / 1 | **vert** |
| Σ `JoursRealises` relus == Σ TOTAL retenus (miroir de §4 ter) | 5 == 5 | **vert** |
| Σ `JoursPrevus` == TOTAL grille de prévu | 109 == 109 | **vert** |
| Σ `MontantHT` == total onglet Facturation | 3 350 == 3 350 | **vert** |
| Toute ligne `émise` porte un `NumFacture` | aucune ligne émise — sans objet | **vert** |

### Non-régression et invariants

- `gabarit-1` : eTag `{AFCF6079-…},9` et mtime **INCHANGÉS**. `gabarit-2` : `{644CACC0-…},8`,
  mtime **INCHANGÉ**. L'écriture bornée n'a touché que la mission 4.
- `gabarit-4` porte un eTag **neuf** (`{00125DF9-…},9`) et un GUID différent : **attendu par
  construction** — une régénération produit un **fichier neuf**. Un ETag ne traverse pas une
  régénération (leçon T-0045) ; ce n'est **pas** un incident.
- **La saisie n'a pas bougé** : `saisie-4-CockpitM365.xlsx` relue après écriture porte le **même**
  eTag `{4A817C3E-…},15` et le même mtime `18:28:30Z`. L'invariant §5.6 « la machine n'écrit jamais
  la saisie » est tenu — et il l'est **au niveau du droit** (`Sites.Selected role=read`), pas
  seulement du code.

## 6. Rapport de passage

| | |
|---|---|
| Mission | **4** — CockpitM365 |
| `T_Affectations` | **6** lignes écrites |
| `T_Imputations` | **1** ligne écrite |
| `T_Echeancier` | **1** ligne écrite |
| Allocations `NumFacture` | **0** (aucune ligne émise) |
| Archive de réversibilité | `gabarit-4-20260801T184907Z.xlsx` (« 00 - Old ») |
| **Anomalies** | **aucune** |

## 7. Ce que cette épreuve ne prouve pas

- **La récurrence.** Un seul mois a été déclaré et dérivé. Le critère d'acceptation « un deuxième
  mois déclaré et dérivé par le même rituel » (même famille de preuve que le contrôle mensuel
  T-0032) reste **ouvert** — il se jouera à la clôture d'**août**. `T-0046` reste donc `à_faire`.
- **Le rituel comme geste d'équipe.** La déclaration a été faite **par le gardien pour** Yousra
  (bootstrap). Le rituel n'a pas encore été exercé par un collaborateur sur sa propre ligne.
- **L'écran de déclaration** et l'**orchestration** (rappel de clôture, contrôle de complétude,
  déclenchement) restent **NOMMÉS, non construits** — le déclenchement de cette dérivation a été un
  geste manuel du gardien, et c'est aujourd'hui cette manualité qui tient la porte du cran validé
  de l'allocation (skill §7).
- **La relecture cockpit** n'a pas été rejouée dans cette épreuve : le gabarit est prouvé **ouvrable
  à froid** (preuve froide de l'instanciation, chemin exact du cockpit), ce qui est la condition que
  l'épreuve T-0035 avait isolée — mais l'affichage lui-même n'a pas été observé ici.
