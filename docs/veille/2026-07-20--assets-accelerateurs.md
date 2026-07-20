# Veille exploratoire — assets accélérateurs pour IA-scale

Statut : **candidat** (non promu). Chemin canonique : `docs/veille/2026-07-20--assets-accelerateurs.md`, dépôt `Allia-Consulting/IA-scale`. Produite le 2026-07-20 par screening GitHub (API publique, ~30 requêtes, 18 dépôts lus en profondeur) + Microsoft Learn, ancrée au HEAD `c94b7cda` (post-S39 `cloture-solde-journaux` — les repères de session dataient de S38 : les recommandations touchant `impact.py`, T-0031 et le cockpit restent des pistes à re-vérifier sur l'état réel avant action). Portée : veille — aucune force normative ; toute canonisation d'extraits passe par la boucle de promotion (doctrine §7). La copie éventuelle dans le Projet claude.ai est un instantané consommateur : le canon prime.

Objectif : identifier ce que d'autres ont déjà construit sur nos surfaces (substrat Graph, crans, skills, evals, cockpit, conformité) pour piller, adopter ou écarter — et confirmer où IA-scale est réellement original.

---

## Constat d'ensemble

Le screening confirme deux choses. D'abord, **le noyau d'IA-scale n'existe nulle part ailleurs** : personne ne combine canon Git unique + contrats socle/local + promotion candidat→pointeur en pull + rollback en une action + quatre rôles. Les projets « AI company OS » (ClawCompany, claw-empire, auto-company, markus) font des équipes d'agents à rôles, pas une organisation gouvernée par contrats. Il n'y a donc **pas d'accélérateur tout fait pour le cœur gouvernance** — c'est une bonne et une mauvaise nouvelle : différenciation réelle, mais tout reste à notre charge.

Ensuite, **la périphérie est très bien servie** : substrat M365 via MCP, portes humaines/policy-as-code, evals, skills, SPFx. C'est là que le temps se gagne.

---

## Axe 1 — Substrat M365/Graph via MCP (vs `ca-allia-mcp-graph`)

**`Softeria/ms-365-mcp-server`** (★856, TypeScript, MIT, très actif — maj 17/07/2026). Le comparateur direct de notre serveur. 320 endpoints Graph générés depuis un `endpoints.json` déclaratif, dont **20 endpoints workbook** couvrant exactement notre surface T-0031/T-0033 : `add-excel-table-rows`, `update/delete-excel-table-row (itemAt)`, `get-excel-used-range`, `create-excel-table`, `graph-batch` ($batch). Trois idées à piller sans adopter le produit :
1. le **catalogue déclaratif d'endpoints avec presets** (`mail`, `excel`, `work`…) formant des allow-lists exactes de noms d'outils — élégant pour scaler notre serveur sans multiplier le code Python à la main ;
2. le **mode read-only** global comme garde-fou de cran ;
3. le format **TOON** (expérimental) pour les sorties tabulaires : 30-60 % de tokens en moins sur les listes — pertinent pour nos bandeaux cockpit qui liront des tables.

**`pnp/cli-microsoft365-mcp-server`** (★117, officiel communauté PnP) : wrapper MCP au-dessus de CLI for Microsoft 365. Utile comme outil d'administration ponctuel du tenant (App Catalog, SPO, Entra), pas comme substrat de production.

**Découverte stratégique : Microsoft Agent 365** (`agent365.svc.cloud.microsoft`). Microsoft expose désormais des **serveurs MCP first-party remote, par tenant** (Work IQ MCP : Mail, Calendar, SharePoint, OneDrive, Teams, Word, Copilot, Dataverse), gouvernés par **Entra Agent ID**. Le modèle d'identité recouvre presque terme à terme le nôtre : *sponsor* humain obligatoire ≈ gardien, *agent identity blueprint* ≈ profil d'agent versionné du référentiel, Conditional Access et sign-in/audit logs par agent, tokens portant contexte utilisateur+agent (nos deux voies d'auth). Licence : M365 E7 ou licence Agent 365 + Entra P1/M365 E3. Verdict : **à surveiller sérieusement, pas à adopter maintenant** — ça pourrait à terme remplacer une partie de `ca-allia-mcp-graph` et résoudre T-0034 (connecteur durable) nativement, mais c'est jeune, sous licence coûteuse, et notre voie 1 `scp=access_as_user` sans état fonctionne. À réévaluer à chaque trimestre.

Réf. Learn : `learn.microsoft.com/microsoft-agent-365/`, `learn.microsoft.com/entra/agent-id/what-is-microsoft-entra-agent-id`.

---

## Axe 2 — Crans, portes humaines, policy-as-code (vs autonomie graduée + `impact.py`)

C'est l'axe le plus riche du screening, et il parle directement à l'anomalie S38 (`impact.py` a auto-mergé un diff `server.py`).

**`makerchecker/MakerChecker`** (AGPL core + Apache SDK, actif). Le plus proche conceptuellement de nos crans : deny-by-default, rôles avec grants explicites par skill versionné (`place-order@1`, `riskTier: high`), journal signé cryptographiquement, et le principe fondateur *maker-checker* : **un agent ne peut structurellement pas approuver son propre travail**. Leur `npx @makerchecker/scan .` analyse un code d'agent et classe chaque action conséquente par risque. Enseignements à transposer dans `impact.py` : (a) la classification de risque se déclare **au niveau de l'action/du fichier, pas du diff** — un `server.py` déclaré `riskTier: high` ne peut jamais être classé faible par une heuristique de taille de diff ; (b) le fail est fermé par défaut, l'ouverture est l'exception explicite.

**`Lelu-ai/lelu`** (★47, MIT) : moteur d'autorisation avec quatre verdicts — `allow / deny / human_review / compute` — chaque décision journalisée, gating pondéré par confiance. Le verdict quaternaire est une modélisation plus fine que notre triptyque auto/notifié/validé : `compute` (recalculer avec plus de contexte avant de trancher) est une idée à retenir.

**`Clyra-AI/gait`** (Go, CLI) : policy-as-code au *tool boundary*, fail-closed, **preuves signées vérifiables hors ligne**, et surtout : transformation des incidents en **régressions CI déterministes** (`gait regress`). C'est exactement le pattern qu'il nous faut pour l'anomalie S38 : l'incident #236 devrait devenir un test de non-régression de `impact.py` exécuté en CI, pas seulement une règle en mémoire.

**`deconvolute-labs/deconvolute`** (Python ≥3.11, s'appuie sur MCP SDK) : firewall MCP **côté client** — valide les définitions d'outils contre une baseline cryptographique (anti rug-pull : un serveur MCP qui change silencieusement ses outils est détecté), allow-list d'outils, audit complet. Pertinent le jour où des collaborateurs consomment des MCP tiers depuis leurs Macs.

**`humanlayer/12-factor-agents`** : doctrine de référence (le repo humanlayer produit lui-même est déprécié). Facteur 3 « own your context window » et les facteurs sur le HITL sont une lecture courte et rentable pour affiner la doctrine §autonomie.

**Recommandation ferme issue de cet axe** (chantier post-S38 déjà identifié) : réécrire la porte de `impact.py` en deny-by-default avec table de risque **par chemin de fichier** (tout `outils/mcp-graph/**` = large, sans exception heuristique), et ajouter un test CI qui rejoue les diffs #235/#236/#237 et vérifie le verdict attendu.

---

## Axe 3 — Skills, plugins, doctrine Claude Code (vs nos skills candidats)

**`anthropics/skills`** (★163k) : dépôt officiel, format `SKILL.md`, et surtout l'existence d'un **standard ouvert : agentskills.io**. Nos skills (consolidation-pilotage v1.4, modele-donnees, table-des-crans) gagneraient à être conformes au standard — interop gratuite avec Claude Code, Cowork et les marketplaces, sans rien changer à notre boucle de promotion.

**`anthropics/knowledge-work-plugins`** (★23k) : **11 plugins métiers open source** (finance, sales, legal, marketing, product, support…) bundlant skills + connecteurs + slash commands + sub-agents. Le plugin **finance** (journal entries, reconciliation, variance, close management) et le plugin **sales** (pipeline review, call prep, forecast) recouvrent des pans entiers de notre carte de capabilities (branches financière, CRM, recrutement). C'est **le gisement de pillage n°1 du screening** : ces skills sont écrits par Anthropic, éprouvés, et adaptables à notre substrat SharePoint. À lire avant d'écrire les gestes guidés pipe (branche CRM, priorité 3) et les bandeaux staffing/rentabilité.

Annuaires utiles pour veille continue : `anthropics/claude-plugins-official`, `hesreallyhim/awesome-claude-code` (★50k), `VoltAgent/awesome-claude-code-subagents` (★23k), `microsoft/skills` (★2.8k, skills orientés SDK Microsoft/Azure — utile pour nos prompts Claude Code touchant Azure).

---

## Axe 4 — Evals & non-régression (vs chantier « évaluation & observabilité » du socle)

**`promptfoo/promptfoo`** (★23k, MIT, désormais adossé à OpenAI mais toujours open source) + **`promptfoo/promptfoo-action`** : LA brique standard pour la non-régression de prompts et skills en CI. Un `promptfooconfig.yaml` par skill promu, exécuté par l'Action sur chaque PR touchant `contrats/` ou les skills = la porte de non-régression que la carte socle promet (« evals, non-régression des prompts & skills ») sans rien construire. Adoption recommandée, périmètre initial modeste : le skill consolidation-pilotage et newsletter-hebdo.

Alternative à surveiller : `agentevals-dev/agentevals` (évals sur traces OpenTelemetry, framework-agnostic) — pertinent plus tard quand on tracera les agents en production via Log Analytics.

---

## Axe 5 — Conformité DPO (registre art. 30, AI Act)

**`verifywise-ai/verifywise`** (★321, source available, hébergeable on-prem) : plateforme de gouvernance IA couvrant EU AI Act, ISO 42001, NIST AI RMF, avec module LLM evals. Trop lourd pour un cabinet d'une personne aujourd'hui, mais **sa structure de données (inventaire des systèmes IA, classification de risque AI Act, assessments) est un excellent gabarit** pour compléter le §9 du registre art. 30 (bases légales T4/T5, rétention, localisation/DPA Anthropic). À piller comme référence de structure, pas à déployer. Les petits outils dédiés (aicomply, ki-register-agent-kit) sont trop immatures.

---

## Axe 6 — Cockpit SPFx + Workbook API (T-0035, branche financière)

**`pnp/sp-dev-fx-webparts`** (★2 255, très actif) : le corpus de référence de web parts SPFx avec appels Graph, React, Fluent UI. Avant de construire les bandeaux restants (staffing, rentabilité, factures), un passage dans les samples `react-graph-*` évite de réinventer les patterns AadHttpClient/consentement.

**Microsoft Learn — bonnes pratiques Excel API** (`learn.microsoft.com/graph/workbook-best-practice`), directement applicables à `server.py` 0.16.x et aux bandeaux :
- **Sessions** : créer une session persistante (`createSession`, `persistChanges: true`) et passer `workbook-session-id` sur chaque appel dès qu'il y a plus d'un ou deux appels au même classeur. Expiration ~5 min d'inactivité (404 → recréer). Notre arc de corrections S38 (403, anomalies silencieuses) plaide pour l'adopter dans `workbook_instancier_gabarit` v2 qui enchaîne les écritures.
- **Jamais de concurrence en écriture sur un même classeur** : strictement séquentiel, attendre le succès avant l'appel suivant. Les écritures concurrentes causent throttling, timeouts et conflits de merge — c'est un candidat d'explication pour de futures anomalies si le cockpit et le service écrivent en même temps.
- **Respecter `Retry-After`** sur les 429 ; limites Excel : 1 500 req/10 s par app par tenant.
- `$batch` Graph existe pour les lectures multiples (cockpit : un bandeau = un batch).

---

## Axe 7 — Comparateurs « AI company OS » (positionnement)

`Claw-Company/clawcompany` (38 rôles, mémoire 4 couches, philosophie « thin harness + fat skills »), `claw-empire`, `nicepkg/auto-company`, `markus-global/markus`. Tous orchestrent des équipes d'agents à rôles en local ; **aucun n'a de canon versionné, de contrats, de boucle de promotion ni de rollback**. Deux idées tout de même : la philosophie *thin harness + fat skills* (le harnais reste mince, l'intelligence vit dans les skills versionnés — nous y sommes déjà, ça valide l'architecture) et le **routage de modèle par criticité de tâche** (Opus pour le travail à enjeu, modèle léger pour le routinier — 30× moins cher) à considérer pour les agents de fond type newsletter.

---

## Recommandations hiérarchisées

1. **Immédiat, coût quasi nul** — Adopter les bonnes pratiques Workbook (sessions persistantes + séquentialité stricte + Retry-After) dans `server.py` lors du prochain passage sur la branche financière ; c'est de la robustesse gratuite avant la preuve à froid T-0031.
2. **Chantier anomalie S38** — Refondre la porte d'`impact.py` sur le modèle MakerChecker/Gait : deny-by-default, risque déclaré par chemin (`outils/mcp-graph/**` = large, toujours), incidents #235–#237 rejoués en test CI de non-régression.
3. **Avant la branche CRM et les bandeaux** — Lire et piller `anthropics/knowledge-work-plugins` (plugins finance et sales) : gisement de skills éprouvés directement transposables à nos capacités.
4. **Chantier evals** — Introduire promptfoo + promptfoo-action comme porte CI de non-régression sur les skills promus (démarrer avec consolidation-pilotage et newsletter-hebdo).
5. **Format** — Aligner nos `SKILL.md` sur le standard agentskills.io lors de la prochaine promotion des trois artefacts candidats (changement d'en-tête, pas de refonte).
6. **Veille trimestrielle** — Microsoft Agent 365 / Entra Agent ID (recouvre T-0034 et notre modèle d'identité d'agents ; licence dissuasive aujourd'hui, trajectoire à suivre) et le catalogue déclaratif d'endpoints de Softeria si notre serveur dépasse la dizaine d'outils.

## Ce que le screening n'a pas trouvé

Aucun projet ne fait : promotion candidat→pointeur en pull, contrats socle/local comme frontière de capacité, rollback une action, ni le rôle d'animateur de périmètre. Les recherches « agent governance gitops » ne renvoient que 9 dépôts, tous embryonnaires. L'originalité du socle IA-scale est confirmée — et sa charge de construction aussi : là, personne ne nous fera gagner du temps.
