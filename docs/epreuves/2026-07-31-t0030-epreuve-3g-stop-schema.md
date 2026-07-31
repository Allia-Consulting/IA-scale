# Épreuve 3g — 31/07/2026 — STOP à la frontière : TABLES_GABARIT diverge de modele-donnees §5.2 v1.25

Rattachement : T-0030 / T-0035 (point 5). Épreuve bout-en-bout de la dérivation (skill consolidation-pilotage v1.5) sur mission 2 (Datalab), **stoppée AVANT tout effet de bord** par un écart de schéma détecté à froid. STOP au premier écart respecté : aucune réparation en douce, la dérivation n'a rien écrit.

## 1. Où l'épreuve s'est arrêtée — la frontière étape 2 → 3 de la séquence §5

La séquence du skill (§5) est : 1 lire la saisie + transformer → 2 lire l'état courant du gabarit → 3 réconcilier en mémoire (dont **allocation** du NumFacture) → 4 archiver → 5 ré-instancier → 6 repeupler → 7 contrôle. L'épreuve s'est arrêtée **à la frontière 2 → 3**, à la lecture du schéma cible, **avant** toute réconciliation, toute allocation, tout archivage.

Preuves de non-effet (état tenant intact) :
- **zéro allocation** : aucun appel `allouer_num_facture`, registre « Factures » **toujours à 3** éléments (F-2026-001..003) ;
- **zéro archivage** : gabarit-2 en place, non déplacé vers « 00 - Old » ;
- **saisie-2 intacte** : ETag `,4` inchangé (aucune écriture — la saisie n'est de toute façon jamais écrite, §5.6).

## 2. L'écart : projection serveur 7 colonnes vs contrat 8 colonnes

`TABLES_GABARIT` (outils/mcp-graph/server.py) portait pour `T_Echeancier` **7 en-têtes** :
`NumFacture, CodeMission, MoisCA, MontantHT, Echeance, Statut, LienFacture`.

Le contrat `modele-donnees.md` §5.2 **v1.25** en fait foi avec **8** :
`NumFacture, CodeMission, EtiquetteLocale, MoisCA, MontantHT, Echeance, Statut, LienFacture`.

**`EtiquetteLocale` manquait** — précisément la clé de réconciliation `(CodeMission, EtiquetteLocale)` que la v1.5 du skill vient d'introduire. Dériver dans ce gabarit aurait produit un `T_Echeancier` sans la colonne d'appariement : la dérivation aurait été structurellement fausse.

## 3. La cause racine — le trou de la chaîne #268 → #272

- **PR #268** : le contrat (`modele-donnees.md` §5.2) gagne `EtiquetteLocale`.
- **PR #272** : le skill v1.5 s'aligne sur le contrat — mais explicitement « **aucun code serveur** ».
- La **projection serveur** (`TABLES_GABARIT`, qui matérialise §5.2 dans l'API Workbook) n'a été portée par **aucune** des deux PRs. Le contrat et le skill parlaient de 8 colonnes ; le serveur en fabriquait toujours 7. L'écart est resté invisible jusqu'à la première dérivation réelle qui l'a lu — l'épreuve 3g.

## 4. Constats annexes de l'épreuve (notés, non bloquants)

- **Placeholders pré-migration dans gabarit-2** (dérivation du 19/07) : `T_Echeancier` porte `F-2026-003..008` en `NumFacture`. `F-2026-003` coïncide de FORME avec un numéro réel du registre, mais c'est un **placeholder de l'ancienne convention** (avant que NumFacture ne soit vidé jusqu'à émission) — **pas un doublon légal**. Il sera **emporté par l'archivage** à la prochaine dérivation (régénération réconciliée §5) : rien à corriger à la main.
- **Ambiguïté de lecture `Réalisé 2026` de saisie-2** (« 22 22 ») : notée, **non bloquante** — `T_Imputations` est vide pour cette mission (aucune imputation à dériver). À lever à la re-épreuve si des réalisés apparaissent.

## 5. Correctif — 0.19.2

`TABLES_GABARIT.T_Echeancier` re-projeté sur §5.2 v1.25 (insertion d'`EtiquetteLocale` en 3e position, après `CodeMission`, avant `MoisCA`). `T_Affectations` et `T_Imputations` vérifiés conformes au contrat (4 et 5 en-têtes) — **inchangés**. Ajout d'un **test anti-divergence** : les en-têtes des 3 tables de `TABLES_GABARIT` sont comparés à la liste **littérale** de §5.2 (recopiée dans le test, référence au contrat en commentaire) — la CI casse si la projection diverge à nouveau. Suite complète : **127 tests verts**.

## 6. À suivre

**Re-épreuve 3g** après redéploiement de l'image **0.19.2** : reprendre la dérivation mission 2 depuis la même saisie-2, gabarit régénéré à 8 colonnes (placeholders pré-migration emportés par l'archivage), puis poursuivre vers l'émission réelle (allocation F-2026-0004) pour solder T-0035 point 5 et T-0030.
