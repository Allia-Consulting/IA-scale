# Épreuve T-0039 — gestes recrutement du cockpit (ajout, étape en ligne, cascade « Acceptée »)

> **Date** : 26 juillet 2026 (clôture, session S43 ; volet A joué le 24/07, session S42). **Chantier** : `T-0039`.
> **Nature** : épreuve réelle sur le tenant, en deux volets (A : gestes de liste ; B : cascade « Acceptée »).
> **Résultat** : **VERTE** — les trois gestes du bandeau recrutement sont prouvés sur le réel. La cascade
> « Acceptée » exécute, sur confirmation, exactement **deux écritures de listes** + un **rappel** d'affectation
> (contrat `tour-de-controle.md` **v2.2**), avec annulation à zéro écriture et minimisation RGPD prouvées.
> Rejeu volontairement **limité à un candidat** (arrêt d'usage prononcé par le gardien, cf. §Arrêt d'usage).

## Ancrages (lecture seule, avant tout effet de bord)

| Ancrage | Valeur relue |
|---|---|
| HEAD du dépôt (`git rev-parse HEAD`) | `ed85f7c6215d32f7246d08e029652e7cc0400638` (conforme) |
| Contrat de cible | `tour-de-controle.md` **v2.2** — PR #262 (mergée par le gardien), main `db46cb46` |
| Code cockpit du volet B | **1.5.1.0** — PR #263 (7 fichiers, 137 tests verts, preuve anti-paquet-vide) |
| Version déployée au tenant (App Catalog) | `AppCatalogVersion 1.5.1.0`, `deployed: true` — page Tour-de-contrôle vivante (bundle chargé, 5 bandeaux) |

## Volet A — gestes de liste (24/07, S42, cockpit 1.5.0.0) : **VERT**

Cinq preuves relues sur le réel (SharePoint REST, identité utilisateur, aucune élévation) :

1. **Ajout de candidat** — création `C-008` (item `Id 11`), `Title` alloué automatiquement au motif `C-NNN`
   (`max(^C-(\d+)$) + 1`) ; `Etape` posée à `E1`. Le défaut « Title vide » du geste CRM n'est **pas** reproduit.
2. **Changement d'étape en ligne** — `E1 → E2 → Proposition` par MERGE REST successifs sur la ligne candidat.
3. **Garde anti-« Acceptée » directe** — la bascule vers « Acceptée » ne s'écrit **jamais** en direct : elle
   ouvre la cascade (annonce + confirmation). Vérifié : aucune écriture d'étape « Acceptée » hors cascade.
4. **Annonce exhaustive** — le dialogue liste l'intégralité des écritures avant exécution, avec le rappel de
   **minimisation RGPD** (Email/Téléphone du candidat **non repris** dans la fiche Ressources-Profil).
5. **Annulation = zéro écriture** — fermer le dialogue avant confirmation ne produit aucune écriture.

### Incidents S42 consignés (n'ont pas bloqué le volet A)

1. **`.sppkg` déployé sans assets** — un paquet dont `ClientSideAssets` était **vide** a été déployé
   (symptôme `503` puis `404` sur le bundle). **Cause** : le build n'avait jamais été exécuté avant le
   packaging, et **aucun contrôle anti-paquet-vide** n'existait. **Correctif** : contrôle anti-paquet-vide
   ajouté au runbook (`unzip -l …/*.sppkg | grep ClientSideAssets` doit lister le bundle `.js`, horodatage
   du `.sppkg` = celui du build).
2. **Runbook `gulp` erroné fourni de mémoire** — le rig réel est **heft** (`heft test --clean --production &&
   heft package-solution --production`), pas `gulp`. Corrigé **sur lecture du réel** (leçon : `CLAUDE.md` —
   on résout depuis le dépôt, jamais de mémoire).
3. **Friction de branchement MCP ×3** — scope MCP par répertoire, `add`-sans-`remove`, spécificités `zsh`.
   Renforce la candidature **T-0034** (connecteur MCP durable).
4. **`403` identité managée sur `ManagementetGestion`** — l'identité managée du serveur n'a pas de vue sur ce
   site : `Sites.Selected` **strict**. Comportement **attendu**, **pas un défaut** (le moindre privilège joue).

## Défaut de SPÉCIFICATION du volet B (constaté le 24/07) — STOP consigné, non réparé en douce

L'écriture (3) initialement prévue visait une table **`T_Affectations` au format long** (`modele-donnees.md`
§5.2), qui est le schéma des **gabarits** (dérivés ERP). Or le **classeur de saisie réel** est **matriciel**
(onglets `Instructions` / `Prevu` / `Realise` / `Facturation`, **mois en colonnes**) : `T_Affectations` n'y
existe pas. Le **fail-closed du pré-vol a fonctionné exactement comme spécifié** — **2 refus**, messages
précis, **zéro écriture**. L'écart a été **consigné et remonté au gardien**, jamais contourné.

## Arbitrage gardien du 26/07 (Option A)

La cascade « Acceptée » est **réduite à deux écritures** (`Candidats.Etape` + fiche `Ressources-Profil`) et
affiche un **rappel** d'affectation : l'affectation initiale reste un **geste humain** dans le classeur de
saisie (`modele-donnees.md` §5.6), le cockpit ne l'écrit pas. Traduction :

- **Contrat** `tour-de-controle.md` **v2.2** — PR #262, **mergée par le gardien**, main `db46cb46`.
- **Cockpit** **1.5.1.0** — PR #263 : 7 fichiers, retrait de l'écriture (3) Graph Workbook et de son pré-vol,
  `rappelAffectation` (résolution du nom en **lecture seule**, fail-open), **137 tests verts**, preuve
  anti-paquet-vide.

### Incident S43 — PR #263 auto-mergée sans porte humaine

La **PR #263 a été auto-mergée par `agent-gardien[bot]`** (`RISQUE: faible`, `VERDICT: pass`, `DELEGUE: non`)
— le verrou #197 (« pas d'auto-merge d'un faible-risque sous périmètre délégué ») a été **appliqué à la
lettre**, mais il **ne couvre pas** ce cas. **Cause** : le préfixe `outils/tour-de-controle-spfx/` **n'est
pas déclaré sensible** dans `impact.py` — un **artefact déployable en production** (le `.sppkg`) peut donc
passer **sans gardien**. Le contenu avait été **contre-vérifié conforme avant le merge**, et le gardien a
**ratifié a posteriori** ; l'épreuve n'est pas invalidée. Le manque est **nommé au backlog** (T-0043).

## Pré-requis du volet B (26/07, gestes du gardien)

- **Purge de `C-008`** (clic gardien) — liste ramenée à **7 candidats**, vérifié en REST.
- **Initialisation humaine de `saisie-4-CockpitM365.xlsx`** — `CodeMission 4` (numérique), Ressource
  `yousra.boukiaou@allia-consulting.com` (UPN **vérifié** via recherche People), `Prevu` Juillet = **5 j**,
  **zéro trace d'exemples** ; **vérifié par lecture du XML** du classeur.

## Volet B — cascade « Acceptée » (26/07, cockpit 1.5.1.0) : **VERT sur `C-005`**

**Baselines relues avant tout effet de bord :**

| Baseline | Valeur |
|---|---|
| `C-005` | étape « Proposition », `Modified 2026-07-26T13:04:09Z` |
| Liste `Ressources-Profil` | **0 fiche** |
| `saisie-4-CockpitM365.xlsx` | ETag `{4A817C3E-7B1B-456F-94BA-690FACAB4CD8},8` |

**Dialogue conforme v2.2** — **2 écritures annoncées** + **rappel** nommant le **nom réel**
`saisie-4-CockpitM365.xlsx` (résolution **lecture seule** du classeur, pas d'écriture).

**Épreuve d'annulation (avant confirmation) — zéro écriture**, 3 preuves REST :
- l'étape de `C-005` reste « Proposition » ;
- `Ressources-Profil` reste à **0 fiche** ;
- l'**ETag** de `saisie-4` **inchangé**.

**Confirmation à `2026-07-26T13:10:15Z` — deux écritures + rappel :**
1. `C-005` → **Acceptée**.
2. Fiche `Ressources-Profil` **`Id 1`** : `Prenom = Yousra`, `Nom = Boukiaou`, `IdentifiantEntra = UPN`,
   `Grade = Consultant` (repris du candidat), `Disponibilité = 27/07/2026`.
3. **Minimisation RGPD prouvée** : **ni** l'email gmail **ni** le téléphone du candidat ne figurent dans la
   fiche.
4. **ETag de `saisie-4` inchangé** = **zéro écriture Workbook** (l'affectation n'est **pas** écrite — c'est
   le rappel qui joue).

## Arrêt d'usage (arbitrage gardien 26/07)

Le rejeu prévu sur `C-001` / `C-003` a été **arrêté par le gardien** : « la cascade n'est pas une feature
pertinente pour notre cible ». Les fiches `Ressources-Profil` de `C-001` / `C-003` **ne sont pas créées** :
**reliquat assumé**, matière d'usage — **pas de construction**. **Conséquence pour le point 2c** : aucun skill
RH du pillage ne sera construit sans **demande d'usage explicite**.

## Note de méthode (Cowork)

La construction assistée du classeur corrigé **en navigateur** a été **bloquée par le classifieur de
sécurité** ; repli sur le **geste humain Excel Online** — conforme à la doctrine (`modele-donnees.md` §5.6 :
la saisie est un geste humain).

## Manques nommés au backlog (nommage seul, aucune construction)

Quatre manques surfacés par l'épreuve, **nommés non ouverts** (statut `à_faire`) :

1. **T-0040** — chaîne d'ouverture de mission incomplète : la cascade « Gagnée » ne crée **ni** gabarit **ni**
   classeur de saisie (le gabarit a un outil, la saisie non).
2. **T-0041** — octroi `Sites.Selected` **lecture** sur `ManagementetGestion` à l'identité managée : décision
   gardien + runbook Graph.
3. **T-0042** — initialisation du classeur de saisie à l'ouverture de mission (template → valeurs mission) :
   aujourd'hui geste humain non outillé.
4. **T-0043** — déclarer `outils/tour-de-controle-spfx/` dans les chemins sensibles d'`impact.py` (suite de
   l'incident auto-merge PR #263).

## Conclusion

`T-0039` est **prouvé sur le réel** dans son périmètre v2.2 : les trois gestes du bandeau recrutement
fonctionnent sous l'identité de l'utilisateur ; la cascade « Acceptée » exécute **deux écritures de listes**
et **rappelle** l'affectation sans jamais l'écrire ; l'annulation est à **zéro écriture** et la **minimisation
RGPD** est prouvée. Le défaut de spécification du volet B a été **traité par arbitrage** (contrat v2.2), non
contourné. Le rejeu est **volontairement borné à `C-005`** (arrêt d'usage gardien). Quatre manques sont
**nommés** au backlog ; l'incident d'auto-merge (PR #263) est **consigné** et adressé par T-0043.
