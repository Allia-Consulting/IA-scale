# Journal de session S44 — 28/07/2026 — registre Factures : création, seed, incidents et arbitrages

Rattachement : T-0030 (registre légal des factures), T-0035 (facturation, point 5). Complète le journal d'épreuve 2026-07-28-t0035-geste-emise.md (même session). Clôture S44 ancrée à 31b13b75 (merge PR #269).

## 1. Création du registre « Factures » (geste tenant, cran validé, go gardien)

Liste SharePoint « Factures » créée sur le site principal AlliaConsuling, via REST depuis la session navigateur du gardien (motif S44 : hors du champ du classifieur — ni donnée personnelle ni contenu de fichier —, sur go explicite du gardien, preuve REST après chaque pas).

- Guid : 439baf86-02bf-40a0-afb1-08004cdecc7e
- 8 colonnes aux noms internes exacts du contrat (modele-donnees.md v1.25 §2 bis) : Title (porte le NumFacture), CodeMission, EtiquetteLocale, MoisCA, MontantHT, Echeance, DateEmission, Statut.

## 2. Seed : reprise de l'existant légal (arbitrage gardien)

Trois éléments seed, F-2026-001 → F-2026-003 : ce sont les numéros des PDF RÉELS des factures déjà émises par la firme (mission 1, Siteflow) — pas des numéros de test. Arbitrage gardien : la séquence légale du registre part de l'existant réel, sans trou ni renumérotation.

| NumFacture | CodeMission | EtiquetteLocale | MoisCA | MontantHT | Echeance | DateEmission | Statut |
|---|---|---|---|---|---|---|---|
| F-2026-001 | 1 | 2026-05-siteflow | 2026-05 | 15300 | 2026-06-01 | (inconnue) | émise |
| F-2026-002 | 1 | 2026-06-siteflow | 2026-06 | 19800 | 2026-07-01 | (inconnue) | émise |
| F-2026-003 | 1 | 2026-07-siteflow | 2026-07 | 20700 | 2026-08-01 | 2026-07-28 | émise |

DateEmission renseignée pour la 003 seule (émise pour de vrai le 28/07, épreuve 3b) ; les dates réelles des 001/002 sont inconnues — geste gardien mineur si retrouvées (file non essentielle). Prochain numéro à allouer : F-2026-004.

Arbitrage gardien associé : mission 2 n'a RIEN émis (confirmé saisie-2 + gardien) — les NumFacture placeholders partagés entre saisies 1 et 2 sur les lignes « à émettre » ne constituent AUCUN doublon légal réel ; ils deviennent EtiquetteLocale à l'étape 3f.

Rappel du canon (déjà acté, PR #267/#268 — aucune re-proposition) : statut « émise » = geste humain dans la saisie, option (i) ; allocation du NumFacture À L'ÉMISSION, jamais à l'ingestion.

## 3. Incident : mcp 2.0.0 casse l'import (réparé au grand jour, PR #269)

CI rouge sur `import server` : mcp 2.0.0 (majeure, fin 07/2026) retire `mcp.server.fastmcp`. Correctif : borne `mcp>=1.2.0,<2.0.0` dans les dépendances du serveur, prouvée en venv neuf (114 tests verts). Relever la borne = migration explicite nommée en file d'attente, jamais en douce.

## 4. Deuxième auto-merge du bot agent-gardien (PR #267)

PR #267 (journal + amendement T-0035, périmètre docs/backlog) auto-mergée par le bot — 2e occurrence vécue après #263 (SPFx). Ratifiée par le gardien a posteriori. Conséquence : T-0043 (doctrine auto-merge) renforcé en tête de file non essentielle ; tant que T-0043 n'est pas traité, toute PR se contre-vérifie en SUPPOSANT l'auto-merge possible. La porte a en revanche TENU sur #269 (outils/mcp-graph/** chemin sensible, auto-approbation skipping, merge gardien).

## 5. État tenant en clôture S44

Candidats 7, Ressources-Profil 1, CRM 3, Missions 2, liste Factures 3. Saisie-1 ETag {10B1CBBC-02C5-46DB-99DB-0E00659A3143},4 (geste émise F4) ; gabarit-1 re-dérivé {23D559F1-3D06-471A-9681-6BC9771DB851},9 ; saisie-4 {4A817C3E-7B1B-456F-94BA-690FACAB4CD8},8 ; gabarit-4 vierge (première dérivation mission 4 à venir — la boucle n'est pas orchestrée, SKILL.md v1.4). Image déployée : 0.18.0 (le déploiement 0.19.0 + GRAPH_FACTURES_LIST_ID = étape suivante, 3d).
