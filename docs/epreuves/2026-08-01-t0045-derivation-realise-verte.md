# Épreuve VERTE — 01/08/2026 — T-0045 : dérivation du Réalisé par POSITION, mission 1 (skill v1.6, image 0.22.0)

Rattachement : `T-0045` (« Lecteur machine fidèle des classeurs de saisie »). **Troisième et dernière épreuve du chantier**, après les deux du matin (`2026-08-01-t0045-acces-et-lecture-saisie.md` : accès `Sites.Selected read`, puis lecture bornée `lire_saisie_table`). Celle-ci exerce le **dernier maillon** — le **dérivateur** : `SAISIE_Realise_2026` → `T_Imputations`, sur la mission 1, avec les contrôles de `skills/consolidation-pilotage/SKILL.md` **v1.6** §4 bis / §4 ter. **VERTE, aucun incident, aucune anomalie.** Le Réalisé est vivant : **39 j → 61 j**.

Chaîne au moment de l'épreuve : `main` = `cd9e314` (PR #289 mergée) · skill **v1.6** · image serveur **0.22.0**, révision **--0000032** · variables `GRAPH_SAISIE_DRIVE_ID` / `GRAPH_SAISIE_FOLDER_ID` posées · connecteur `allia-graph` sain.

## 1. Baselines relevées AVANT tout geste

| Objet | ETag | cTag | `lastModifiedDateTime` |
|---|---|---|---|
| `saisie-1-siteflow.xlsx` (item `013OHVIUF4ZOYRBRIC3NDJTWYOABSZUMKD`) | `"{10B1CBBC-02C5-46DB-99DB-0E00659A3143},8"` | `"c:{…},9"` | `2026-07-31T15:30:53Z` |
| `gabarit-1.xlsx` (item `01BWFCBZC2NPXFBN4ARRE2ZMZCKT2J7O6I`) | `"{50EE6B5A-80B7-498C-ACB3-2254F49FBBC8},9"` | `"c:{…},10"` | `2026-08-01T09:21:44Z` |

**`T_Imputations` de départ — 2 lignes / 39 j** : `2026-05-01` **17 j**, `2026-06-01` **22 j**, toutes deux « à valider ». **Juillet absent.** C'est exactement l'état hérité de l'épreuve 3g, le point de départ à corriger.

> **Fausse alerte écartée, à consigner.** La première recherche SharePoint (`gabarit`) n'a rendu **que** des archives de « 00 - Old », sans `gabarit-1.xlsx` actif — ce qui ressemblait au cas §6 « régénération avortée après archivage ». Une recherche ciblée a montré que le fichier **existait bien** à la racine : c'était un **artefact de pertinence de l'index**, pas un état du tenant. **Leçon** : un index de recherche n'est pas une mesure ; ne jamais déclarer un incident sur son silence.

## 2. Lecture — la grille sort avec ses positions

`lire_saisie_table(code_mission="1", table="SAISIE_Realise_2026")` rend **21 lignes × 14 colonnes**, positions intactes, **vides compris** :

- **1** ligne d'entête technique « Nb. jours ouvres max » ;
- **1** ligne de ressource : `adrien.raque@allia-consulting.com` ;
- **19** lignes de la zone pré-dimensionnée, entièrement vides, `TOTAL` = 0.

Vingt lignes à écarter pour une ligne de sens — et la primitive les rend **volontairement** : lire n'est pas interpréter, le filtrage appartient au consommateur (§4 bis).

## 3. Dérivation par POSITION et contrôles §4 ter

Ligne retenue, lue **par index** — jamais par en-tête relu, jamais par inférence :

| Position | Mois | Valeur |
|---|---|---|
| 5 | Mai | **17 j** |
| 6 | Juin | **22 j** |
| 7 | Juillet | **22 j** |
| 8 | Août | *(cellule VIDE)* |

| Contrôle | Mesure | Verdict |
|---|---|---|
| Σ des douze positions == `TOTAL` (par ligne) | **61 == 61** | ✔ |
| Σ `JoursRealises` dérivés == Σ des `TOTAL` retenus (miroir mission) | **61 == 61** | ✔ |
| Lignes écartées | 1 entête technique + 19 fantômes (`TOTAL` = 0) | ✔ |
| Anomalies | **aucune** | ✔ |

Contrôle miroir passé aussi sur le Prévu (`SAISIE_Prevu_2026`) : **Σ 148 == TOTAL 148**, huit positions renseignées (Mai 17, Juin 22, Juil. 22, Août 10, Sept. 22, Oct. 21, Nov. 20, Déc. 14).

**Réconciliation (§5)** : aucune ligne du gabarit courant absente de la saisie (rien à reporter, aucune anomalie « suppression à confirmer ») ; **aucun `StatutValidation` « validé »** au courant, donc rien à préserver ; **une seule nouveauté — Juillet 22**.

## 4. Écriture — régénération réconciliée

Séquence §5 exécutée dans l'ordre, sans écart :

1. **Archivage par déplacement** — `gabarit-1-20260801T171502Z.xlsx` déposé dans « 00 - Old », `deplace: true`, **nom libéré** (synchrone, aucun `202` à poller).
2. **Ré-instanciation** — nouvel item `01BWFCBZDZMDH26VHVXJCIB66N5MVYEYES` ; **preuve FROIDE verte**, les trois tables vierges (`lignes_vides: 1` chacune — la ligne d'insertion Excel tolérée depuis la reprise n°5).
3. **Repeuplement**, un appel par table : `T_Affectations` **8**, `T_Imputations` **3**, `T_Echeancier` **8**.

**Aucun cran « validé » sollicité** : les trois lignes émises portaient déjà leur `NumFacture` au gabarit courant — **reportées telles quelles**, sans réallocation ni appel à `allouer_num_facture` (invariant d'allocation §5). Les cinq lignes « à émettre » gardent un `NumFacture` vide.

## 5. Preuves — relecture À FROID après écriture

```
T_Imputations (3 lignes)
  1 | adrien.raque@allia-consulting.com | serial 46143 → 2026-05-01 | 17 j | à valider
  1 | adrien.raque@allia-consulting.com | serial 46174 → 2026-06-01 | 22 j | à valider
  1 | adrien.raque@allia-consulting.com | serial 46204 → 2026-07-01 | 22 j | à valider
  Σ JoursRealises = 61
```

| Preuve | Mesure | Verdict |
|---|---|---|
| Σ `JoursRealises` relus | **61** (attendu 61) | ✔ |
| Les trois mois portent leurs valeurs exactes | Mai 17 · Juin 22 · Juillet 22 | ✔ |
| Écart de 3g comblé | 39 → **61**, soit **+22 j = juillet** | ✔ |
| **Aucun mois forgé** | mois écrits ⊆ positions porteuses en saisie ; **Août, vide en saisie, ABSENT du gabarit** | ✔ |
| Non-régression `T_Affectations` | 8 lignes, **Σ 148 j** | ✔ |
| Non-régression `T_Echeancier` | 8 lignes, **Σ 133 200 € HT**, `F-2026-001/002/003` intacts | ✔ |

**ETag après écriture** : `"{AFCF6079-F554-44BA-80FB-CDEB2B826092},9"` · cTag `"c:{…},10"` · `lastModifiedDateTime` `2026-08-01T17:15:48Z`.

> **Nuance à retenir sur les ETag.** Une régénération produit un **fichier NEUF** (l'ancien part horodaté dans « 00 - Old ») : le GUID de l'ETag diffère **par construction**, et comparer les ETag de part et d'autre d'une régénération **n'a aucun sens**. Ce qui prouve le changement, c'est le **contenu relu à froid** et l'**archive conservée** — pas le delta d'ETag. Les ETag exposés en 0.22.0 servent à détecter un changement **entre deux lectures du même item**, pas à travers une régénération.

## 6. Ce que l'épreuve n'a PAS prouvé — dit explicitement

- **Le fail-closed sur écart n'a pas été exercé sur le tenant.** Le 3ᵉ critère d'acceptation (« aucun mois forgé ni déduit par recoupement ; anomalie signalée, jamais résolue seule ») est **inscrit** au skill §4 ter et **testé** au golden set (`controle-somme-21`, `jamais-mois-forge-22`, rouge-puis-vert en CI) — mais **aucun écart réel ne s'est présenté** aujourd'hui, tous les contrôles tombant justes. On ne fabrique pas un faux écart dans une source pour se prouver qu'on le détecte : le critère est tenu **par construction et par la CI**, non par un rouge réel. Arbitrage gardien assumé au solde.
- **`T_Ressources` n'a pas pu être relu.** Le référentiel de coûts est à **audience restreinte** (§5.3) et n'est atteignable ni par la recherche M365 ni par les coordonnées disponibles à l'agent — **conforme au modèle**, mais le contrôle §6 « ressource présente en saisie mais absente de `T_Ressources` » **n'a donc pas été clos**. Si `adrien.raque@allia-consulting.com` n'y porte pas de `CoutJour`, le cockpit **masquera** l'EBITDA de juillet plutôt que d'inventer un coût nul (acquis T-0043), et l'anomalie §6 sera à ouvrir. **À vérifier par le gardien.**

## 7. Effet attendu au cockpit — à CONSTATER par le gardien, non calculé ici

Le Réalisé étant vivant, sur **juillet** :

- **jours réalisés mission 1 : 0 → 22 j** (le mois n'existait pas côté réalisé) ;
- **CA de juillet inchangé** — `MoisCA 2026-07` = 19 800 € HT, `F-2026-003` émise : rien n'a bougé côté recette ;
- un **coût direct réalisé** apparaît donc sur juillet (22 j × `CoutJour`) là où il n'y en avait aucun → **l'EBITDA réalisé de juillet doit BAISSER**, et son taux de marge avec ;
- **coût de structure de juillet inchangé** (2 860,67 € inscrits le 01/08, T-0032) ;
- **cumul réalisé mission 1 : 39 → 61 j**.

Aucun de ces chiffres n'est calculé ici : la page fait foi, le gardien constate.

## 8. Élément nouveau sur l'anomalie du 14/07 — orientée, toujours PAS tranchée

Le Prévu relu ce jour donne **juillet 22 / août 10, TOTAL 148** — **identique** à la lecture du matin du 01/08, et le classeur de saisie porte `lastModifiedDateTime` **`2026-07-31T15:30:53Z`**, soit **postérieur au relevé du 14/07** (qui donnait juillet 23 / août 7, TOTAL 148 déjà identique).

Cela **oriente** vers « saisie révisée entre les deux dates » plutôt que « relevé du 14/07 imprécis. » **Ce n'est pas une preuve** : en co-édition, les métadonnées de modification sont **différées** et **le contenu fait foi, pas l'horodatage** (§5.6) — un horodatage établit qu'une modification a eu lieu *au moins* à cette date, jamais qu'il n'y en a pas eu d'autre. **L'anomalie reste OUVERTE et non tranchée**, à instruire ; elle ne se résout pas par recoupement.

## 9. Acquis durables de cette épreuve

1. **La chaîne économique est complète.** Prévu (`T_Affectations`), Réalisé (`T_Imputations`) et Échéancier (`T_Echeancier`) sont tous les trois dérivés de la saisie par la machine, sans geste humain sur le gabarit. Le Réalisé était le maillon manquant depuis l'épreuve 3g.
2. **La lecture par position tient sur le réel.** Vingt lignes de bruit (entête technique + zone pré-dimensionnée) pour une ligne de sens : le tri par `TOTAL` = 0 et par libellé d'entête fait exactement son travail, et le contrôle `Σ == TOTAL` le vérifie.
3. **Un index de recherche n'est pas une mesure** (§1) — ne jamais déclarer un incident sur le silence d'un index.
4. **Un ETag ne traverse pas une régénération** (§5) — le GUID change par construction ; la preuve est le contenu relu, pas le delta d'ETag.
