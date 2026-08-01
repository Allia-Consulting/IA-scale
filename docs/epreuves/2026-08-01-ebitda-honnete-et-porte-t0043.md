# Épreuve EBITDA honnête + porte SPFx tenue — 01/08/2026 — bandeau 4 (Rentabilité) & solde T-0043

Rattachement : correctif honnêteté du bandeau 4 (Rentabilité/EBITDA) du cockpit `tour-de-controle-spfx` (contrat `tour-de-controle.md` §3 bandeau 4) ; et **solde de T-0043** par épreuve réelle de la porte de conformité sur un artefact SPFx. Deux faits distincts prouvés le même jour : (a) le cockpit ne fabrique plus de zéro de coût ; (b) une PR touchant `outils/tour-de-controle-spfx/` est bien **tenue en porte humaine**, plus jamais auto-mergée.

## 1. Cause mesurée (01/08, matin)

Sur la page réelle du tenant, la ligne **EBITDA** affichait un résultat **égal au CA à l'euro près**. Cause racine mesurée dans `bandeaux-economiques.ts` : `coutsMois` comptait la part de coût d'une ressource `couts.get(ressource) ?? 0` — soit **un coût inventé à 0** dès qu'une ressource portant des jours n'avait pas de `CoutJour` au référentiel. L'EBITDA ainsi affiché n'était pas un résultat, c'était le CA déguisé — contraire au contrat socle §3 bandeau 4 (« L'absence de donnée s'affiche « · », jamais zéro inventé »).

Terrain qui a fait surgir le défaut :
- les référentiels de coûts `'07 - Coût de Structure'` et `'08 - Coût Masse salariale & Indep'` (T-0032) sont **semi-vides depuis le 14/07/2026** (posés vides, non encore alimentés) ;
- la clé `Ressource` d'Abdelhak n'était **pas appariée** au référentiel — mesurée au gabarit-2 : la ressource porte `abdelhak.chmaimi@gmail.com`, absente de la table des coûts.

Sans le correctif, les jours d'Abdelhak entraient dans l'EBITDA avec un coût 0 : un résultat gonflé, silencieusement faux.

## 2. Correctif (PR #277)

PR **#277** — head `1fd97bf4`, mergée par le gardien en `c3ecaaa0`. Un seul fichier de logique modifié (`bandeaux-economiques.ts`) :

- détecteur `coutJourManquantMois` par **mois × régime** (budget|réalisé) : s'il existe au moins une ressource avec jours > 0 sur le mois **absente** de la Map (`!couts.has(ressource)`), la cellule EBITDA de ce régime vaut le placeholder « · » et **n'entre pas dans le Total** ;
- le **CA n'est pas affecté** (calcul strictement inchangé) ;
- constante exportée `MENTION_COUTJOUR_MANQUANT = 'CoutJour manquant au référentiel'`, posée sur la ligne EBITDA dès qu'au moins une cellule est masquée pour cette cause ;
- **0 déclaré ≠ absent** : une ressource présente avec `CoutJour = 0` est une donnée valide (le test porte sur `couts.has`, pas sur la valeur) ; `T_Structure` vide = 0 assumé, ne masque rien ;
- référentiel inaccessible → comportement existant `MENTION_REFERENTIEL_RESTREINT` inchangé.

Preuve de non-régression : **140 tests verts (+3)** (`heft test --clean` ; `bandeaux-economiques` 27 dont 3 cas neufs — masquage+mention+Total hors mois masqué ; toutes ressources appariées dont une à CoutJour 0 ; référentiel restreint intact). Bump `package-solution.json` `1.5.1.0 → 1.5.2.0`.

## 3. Porte T-0043 TENUE en épreuve réelle sur #277

C'est la **condition de solde de T-0043** (« la prochaine PR sous `skills/` ou `outils/tour-de-controle-spfx/` doit être TENUE en porte humaine, auto-approbation « skipping », preuve à journaliser »). Prouvé sur #277 :

- **Avis d'impact = RISQUE `large`** (chemin sensible `outils/tour-de-controle-spfx/` déclaré dans `PREFIXES_SENSIBLES_LARGE`, correctif S45) — 0 consommateur, `DELEGUE: non` ;
- **Auto-approbation `skipped`** : `agent-gardien[bot]` n'a **pas** auto-mergé (contrairement à l'incident fondateur #263) — `state=OPEN`, `mergedAt=null`, `autoMerge=null` tant que la porte n'était pas franchie ;
- **merge par geste gardien explicite** (`c3ecaaa0`), après lecture.

Le trou de chemin de #263 est refermé et **éprouvé vivant** : un artefact SPFx déployable ne passe plus sans gardien.

## 4. Déploiement 1.5.2.0 et constat en deux temps sur la page réelle

Déploiement `1.5.2.0` à l'App Catalog — **geste gardien** (mise en production d'un artefact déployable). Constat sur la page réelle du cockpit, en deux temps :

1. **Avant correction du référentiel (A8)** — les mois où Abdelhak porte des jours s'affichent **« · » + mention** `CoutJour manquant au référentiel` sur la ligne EBITDA. **Honnêteté prouvée** : le cockpit refuse d'inventer un résultat plutôt que d'afficher un EBITDA = CA.
2. **Après saisie gardien** dans `referentiel-ressources` (ETag `,2 → ,5`) — `CoutJour` Yousra **418,35**, Guillaume **575,23**, cellule **A8 = `abdelhak.chmaimi@gmail.com`** (clé enfin appariée). La **mention disparaît**, l'EBITDA se calcule : **budget sept 18 616 €, oct 21 963 €, Total 150 500 €**.

**Contre-preuve arithmétique** : CA budget **216 500 €** − EBITDA budget **150 500 €** = **66 000 €** = **120 j × 550 €/j** (charge budget de la mission 2). L'écart CA→EBITDA correspond exactement au coût des jours désormais tarifés — le résultat est vrai, pas fabriqué.

## 5. Restes nommés (non construits ce jour)

- **T_Structure vide** — les coûts de structure ne sont pas encore alimentés (0 assumé, ne masque rien) ; alimentation = volet de T-0032.
- **EBITDA réalisé** — suspendu à **T-0045** (lecteur machine fidèle des saisies : `T_Imputations` fidèle est la condition du Réalisé, cf. journal 3g du 01/08).
- **Volet ingestion des factures fournisseur de T-0032** — à instruire (agent Cowork, ligne candidate en Zone-de-proposition, cran de validation) ; le volet référentiel + EBITDA cockpit est, lui, éprouvé ce jour.
- **RUNBOOK DE DÉPLOIEMENT `.sppkg` ABSENT DU CANON** — constaté ce jour : la mise en production de l'artefact SPFx (App Catalog) est un geste gardien répété, sans runbook consigné au canon. Nommé au `backlog/plan.md` (§14), non construit.
