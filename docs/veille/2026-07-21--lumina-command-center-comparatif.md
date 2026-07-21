# Analyse d'écart — Lumina Partners « Command Center » vs IA-scale

Statut : **candidat** (non promu). Chemin canonique : `docs/veille/2026-07-21--lumina-command-center-comparatif.md`, dépôt `Allia-Consulting/IA-scale`. Produite le 2026-07-21 par lecture du dépôt partagé `smhkb08/lumina-authz-reference` (v2, commit `163f0c2c`, extrait assaini du Command Center de Lumina Partners FZ-LLC, partagé en lecture pour analyse d'écart). Portée : veille — aucune force normative. Le canon prime sur toute affirmation d'état d'IA-scale ci-dessous : les repères IA-scale utilisés (S38/S39, T-0031/T-0033/T-0035, chantier `impact.py`) sont des pistes à re-vérifier au HEAD réel avant action.

Sources lues : README v2, ARCHITECTURE.md, docs/AGENT_CAPABILITY_MATRIX.md (audit du 2026-07-12), docs/METHOD_GOVERNANCE.md v1.2, docs/agent-doctrine.md, docs/wf1-runbook.md v1.0, docs/ONBOARDING.md, src/authz/* (structure), src/lib/v2/run-employee.ts, run-employee-on-thread.ts (extraits), model-map.ts, contact-stage.ts, relationship-score.ts, employee-tools.ts (inventaire d'outils), lumina-dna.template.ts. Non lus en profondeur : prompts seed des 21 agents, workflows wf1b/c/d, design/, prisma.

---

## 1. Ce qu'est réellement le Command Center

Un **produit logiciel intégré** : application Next.js + Prisma/Supabase, connexion SSO Microsoft, dans laquelle vivent 21 « employés virtuels » (agents IA à identité duale codename + nom humain fictif), un moteur d'exécution unifié, des workflows métier, un CRM, et un fil d'approbation humaine (« le Fil »). La base de données est la source de vérité ; l'identité de la firme vit dans un module TypeScript unique (`lumina-dna.ts`) importé par tous les agents, l'UI, les seeds et les crons. Contexte : cabinet GCC (UAE), CEO + une directrice + un senior manager, tout au « Niveau 1 » (chaque étape validée par le CEO).

Le contraste architectural avec IA-scale est fondamental et conditionne toute la comparaison : **eux ont construit une application ; nous construisons une organisation gouvernée**. Leur vérité vit en base et en code applicatif ; la nôtre vit dans un canon Git propagé par contrats vers un substrat M365 existant. Ce ne sont pas deux niveaux d'avancement du même objet — ce sont deux paris différents sur ce qui tient à 200 collaborateurs.

---

## 2. Comparatif fonctionnalité par fonctionnalité

Légende maturité : ✅ construit et éprouvé sur le réel · 🟡 construit, partiellement éprouvé · 🔷 conçu, non construit · ⬜ absent. Les états Lumina reprennent leur propre audit conçu-vs-câblé (2026-07-12) ; les états IA-scale sont au mieux de ma connaissance de session (à re-vérifier au canon).

### 2.1 Socle de gouvernance à l'échelle

| Fonctionnalité | Lumina | IA-scale | Écart |
|---|---|---|---|
| Source de vérité unique | 🟡 DNA module typé + registre MethodAsset en base ; « défini une fois, ne peut pas dériver entre surfaces » | ✅ Canon Git unique, tout part du dépôt | Mécanismes équivalents en intention ; le nôtre est vérifiable (SHA, diff), le leur est une convention de code |
| Contrats de périmètre (socle/local, frontières de capacité) | ⬜ Rien d'équivalent — le couplage passe par les imports TypeScript | ✅ Contrats socle/local, délégation §4.1 | **Notre différenciateur confirmé** — rien chez eux ne borne un périmètre |
| Promotion candidat→canon | 🟡 `draft → validated` en base, acte humain exclusif (CEO + directrice), agent propose au Fil | ✅ PR + CI + journal d'approbation + merge tracé | Même philosophie (l'agent propose, l'humain promeut) ; notre implémentation porte diff, historique et CI, la leur est un changement d'état en base sans journal de gouvernance |
| Rollback | 🟡 Re-pointage manuel d'ids épinglés (aucune version supprimée, donc réversible) | ✅ Une action (revert Git) | Leur immutabilité des versions est réelle mais le retour arrière est un geste manuel multi-consommateurs |
| Propagation des améliorations | 🟡 Pull implicite (tous les consommateurs importent le même module/id) | ✅ Pull explicite par pointeurs à portée | Comparable en pratique à leur échelle ; le nôtre est conçu pour des périmètres délégués |
| Historique de gouvernance | ⬜ Volontairement absent du partage, et structurellement faible (états en base, seeds) | ✅ Journal immutable, changelogs, PRs | Notre avance nette |
| Rôles et délégation | 🟡 CEO super-utilisateur + grades ; pas de rôle « animateur de périmètre » | ✅ Quatre rôles opérationnels, délégation réelle (Sarah) | Leur modèle est une hiérarchie de grades ; le nôtre une gouvernance de périmètres |

**Verdict socle : IA-scale devant, nettement.** C'est cohérent avec la veille du 20/07 : personne, y compris Lumina, ne fait contrats + promotion pull + rollback une action. Leur gouvernance méthodologique (voir 2.5) est le point où ils s'en approchent le plus — en base, sans infrastructure de preuve.

### 2.2 Autorisation et crans

| Fonctionnalité | Lumina | IA-scale | Écart |
|---|---|---|---|
| Refus par défaut | ✅ Route non déclarée → 404 ; point d'application unique | 🟡 Principe posé (crans) ; `impact.py` a précisément fauté là (anomalie S38 : diff `server.py` auto-mergé) | **Leur avance la plus utile pour nous** |
| Table de politiques exhaustive | ✅ 158 routes classées SESSION/CEO/CRON/PUBLIC ; **test de couverture qui casse la CI si une route n'a pas d'entrée** | 🔷 Table des crans v1.12 candidate ; pas de test de bijection | « L'oubli casse la CI, pas la production » — exactement le correctif que demande l'anomalie S38 |
| Capacités par geste | ✅ 39 capacités `{minGrade, institutional}`, nommées par geste, jamais par route | 🔷 Crans par type d'action (auto/notifié/validé), conçus | Leur granularité est supérieure ; leur axe statut (externe masque tout l'institutionnel, prime sur le grade) est une idée propre |
| Filtrage de lignes (row-level) | ✅ `scope()` : isolation d'org, confidentialité vs grade, affectation (le go/no-go n'est décidable que par le Pilote grade ≥ director) | ⬜ Équivalent délégué aux permissions SharePoint/Graph | Pertinent pour nous seulement si une surface applicative multi-comptes émerge (cockpit v3+) |
| Révocation immédiate | ✅ Grade/statut rechargés de la base à chaque requête, jamais lus d'un jeton | 🟡 Nos tokens Entra portent `scp` ; révocation = cycle de vie Entra | Bonne pratique à garder en tête, pas urgente |
| Preuve par tests | ✅ Oracle indépendant × implémentation sur toute la matrice (39×6×2) | 🔷 Chantier evals (promptfoo) non ouvert | Leur discipline attendu-vs-obtenu est le modèle |
| Épreuve réelle | ⬜ **Réserve explicite du README : jamais validé en conditions réelles** (round-trip HTTP, multi-comptes) | — | Leur moteur est prouvé, leur câblage ne l'est pas — ils ont l'inverse de notre règle « soldé = éprouvé » |

**Verdict autorisation : Lumina devant sur le moteur, mais non éprouvé.** Le transposable ne se discute pas : la paire *table de politiques exhaustive + test de couverture CI* est la forme finie du chantier `impact.py` (déjà identifié en veille via MakerChecker/gait — ici on a une implémentation complète et testée à copier dans l'esprit).

### 2.3 Agents et runtime

| Fonctionnalité | Lumina | IA-scale | Écart |
|---|---|---|---|
| Référentiel d'agents versionné | ✅ 21 agents, 5 tiers, PromptVersion versionnée/réversible, prompts en seed | 🔷 Sur la carte socle (« profils & skills activables et versionnés ») | Leur avance — mais voir la ligne « théâtre » ci-dessous |
| Moteur d'exécution unifié | ✅ `runEmployeeOnThread` : contexte 7 couches, résumé à fenêtre glissante, Files API, directive anti-fabrication | ⬜ Nos agents = Claude (Code/claude.ai/MCP), pas de runtime propriétaire | Choix assumé chez nous (thin harness) ; leur couche 2 (profils de mission → frameworks épinglés du registre) est la partie intéressante |
| Routage de modèle par criticité | ✅ Registre central de modèles, zéro id en dur, tiers opus/sonnet/haiku, budgets de thinking, **coût USD calculé par run** | 🔷 Idée notée en veille (30× moins cher), rien de construit | À piller le jour des agents de fond (newsletter) ; le coût par run est la brique FinOps IA de notre carte |
| Hygiène de prompt caching | ✅ Horodatage sorti du préfixe système pour préserver le cache | ⬜ Non formalisé | Micro-pillage gratuit pour nos prompts serveur |
| Écart conçu/câblé | Leur audit : **5 ✅ · 10 🟡 · 6 🔷 sur 21** — le câblé se concentre sur un workflow + le standup | Nous traquons le même écart via « soldé = éprouvé » | **Point de lucidité clé : les « 21 agents » sont ~5 agents pleins autour d'un flux.** Leur matrice conçu-vs-câblé auditée est en soi une pratique à copier |
| Personas humaines fictives | ✅ Choix produit (Viktor Larssen, etc.), mécanisme identité duale propre | ⬜ Non souhaité | Choix de produit, pas de gouvernance — on n'adopte pas |
| Apprentissage des préférences | ✅ Cron `distill-styles` : Haiku analyse les corrections humaines (`editDiff`) → `StylePreference` par agent | ⬜ Rien | Boucle de capitalisation légère et élégante — candidate pour notre « confidentialité & apprentissage intermissions » |

### 2.4 Workflows métier — le cœur de l'intuition du gardien

| Fonctionnalité | Lumina | IA-scale | Écart |
|---|---|---|---|
| Qualification AO de bout en bout (WF1) | ✅ **Production-ready, éprouvé** : pre-scan 4 filtres déterministes → 6 agents séquentiels → grille 13 critères / 4 quadrants → **agrégation en code déterministe, pas en IA** (0 rouge + ≥8 verts = Go ; D2 rouge = No-Go auto) → décision CEO ; statuts avec boucle Reformulate ; runbook opérationnel ; 8 h manuelles → 15-45 min | ⬜ « Réponse à AO & proposition » sur la carte, rien de construit | **Leur avance réelle la plus nette.** C'est leur seul flux éprouvé de bout en bout — et il est excellent |
| Production de proposition (plan → rédaction → revue visuelle → checklist → pricing) | 🟡 Chaîne S3-S5 câblée (runs réels), revue visuelle bloquante déterministe, gates au Fil | ⬜ | Idem — gabarit directement transposable |
| Standup quotidien | 🟡 Cron 06:00, 3 agents (marché, pipeline, compliance), mail Resend | 🔷 T-0011 newsletter-hebdo (première exécution réelle en attente) | Comparable en nature ; eux tournent |
| Pipeline éditorial avec gate de publication | 🟡 Câblé, publication finale = stub (Publer) ; LinkedIn OAuth en place non appelée | 🔷 Branche communication déléguée à Sarah, newsletter en file | Match nul pratique : leur dernier kilomètre n'existe pas non plus |
| Cascade gagné → mission | ⬜ Non visible dans l'extrait | 🔷 Priorité 3 (CRM) | — |
| HITL systémique | ✅ « Le Fil » : toute proposition d'agent est signée et approuvée ; Niveau 1 = validation CEO partout | ✅ Crans + gestes réservés du gardien | Philosophies identiques ; leur Fil est une belle surface UX d'approbation unifiée, notre équivalent est distribué (PR, cockpit) |

**Verdict workflows : Lumina devant, et c'est le fond de l'intuition — validé, mais circonscrit.** Un seul flux est réellement éprouvé (WF1 + sa chaîne de production S3-S5). Le reste (contenu, RH, CRM agentifié, réputation, sécurité, savoir) est chez eux au même état que chez nous : conçu, non câblé. Leur propre audit le dit sans fard.

### 2.5 Gouvernance du capital méthodologique

Leur `MethodAsset` est l'objet le plus proche de notre boucle de promotion, et il contient trois idées que nous n'avons pas :

| Fonctionnalité | Lumina | IA-scale | Écart |
|---|---|---|---|
| Épinglage type lockfile | ✅ Toute référence par id immuable ; montée de version = nouvelle ligne (`parentAssetId`), jamais d'écrasement, jamais de hard delete, aucune référence « latest » | ✅ Équivalent par SHA/pointeurs à portée | Convergence remarquable — deux implémentations du même principe |
| Eval harness obligatoire | ✅ `pnpm eval` avant ET après tout re-pointage ; le moindre écart bloque | 🔷 Chantier promptfoo identifié, non ouvert | Confirme et durcit notre chantier : chez eux c'est **bloquant**, pas indicatif |
| **Filtre concurrent (garde NDA)** | ✅ `sourceEngagementId` conservé après promotion ; liste `competitorClientIds` posée manuellement par le CEO, jamais inférée ; symétrique ; point de câblage unique pour que tous les consommateurs héritent | ⬜ « Confidentialité & apprentissage intermissions » sur la carte, non spécifié | **Le pillage conceptuel n°1 de cette lecture.** Un asset anonymisé reste tracé à sa mission d'origine et exclu de tout contexte servant un concurrent — c'est la condition de la capitalisation intermissions en conseil, et nous ne l'avons pas formalisée |
| **Plafond de dette de décision** | ✅ Max 15 candidats en attente d'approbation ; au-delà, l'ingestion se met en pause — « on ne crée pas de dette de décision » | ⬜ Zone-de-proposition sans plafond | Discipline directement transposable au gardien mono-personne |
| Nommage canonique | ✅ Règles anti-doublons gravées (millésime hors du nom, correction ≠ montée de version) | 🟡 Implicite dans nos conventions | Hygiène à noter |
| Doctrine AI-native des frameworks publics | ✅ « Le savoir vit dans le modèle ; le registre est le mécanisme d'activation et de gouvernance » — fiche d'activation 4 lignes, pas d'inventaire du savoir | 🟡 Proche de notre philosophie skills | Formulation plus nette que la nôtre, à méditer pour nos SKILL.md |

### 2.6 CRM

| Fonctionnalité | Lumina | IA-scale | Écart |
|---|---|---|---|
| Stages de contact | ✅ **Dérivés, jamais saisis** : le stage est déduit de l'historique d'interactions (fonctions pures, zéro dépendance) ; override manuel possible, retour auto en le levant | 🔷 Gestes guidés pipe (priorité 3) | Leur réponse à « la maladie chronique de tout CRM : les stages pourrissent » — à adopter tel quel |
| Scoring relationnel | ✅ Dérivé : fraîcheur, dormance **pondérée par l'enjeu** (un sponsor de pursuit actif silencieux 30 j > un dormant 90 j), Mendelow influence×intérêt dérivé ; « l'absence de donnée est un inconnu, jamais un faible » | ⬜ | Doctrine saine, code lisible, transposable sur nos listes SharePoint |
| Anti-double-forecast | ✅ Refus délibéré d'une seconde grille de probabilité (la grille WF1 + pricing S5 font foi) — « deux forecasts contradictoires » explicitement proscrit | — | Principe « une seule vérité » appliqué au forecast — exactement notre langue |
| Graphe de réseau, actualités client | 🟡 `network-graph.ts`, `client-news` (outil agent) | ⬜ | Nice-to-have |
| CRM agentifié | 🔷 Iris (CRM Manager) : persona seedée, zéro run, zéro UI | 🔷 | **Match nul : leur CRM est de la lib + UI, pas un agent.** Le « CRM avancé » est réel côté logique métier, pas côté agentique |

### 2.7 Observabilité, coûts, conformité

| Fonctionnalité | Lumina | IA-scale | Écart |
|---|---|---|---|
| Coût par run agent | ✅ `calcCostUsd` + TokenUsage persistés | ⬜ (Log Analytics infra seulement) | Brique FinOps IA de notre carte, servie sur un plateau |
| Evals en CI | 🔷 Harness `pnpm eval` (méthodo) ; pas de CI visible dans l'extrait | 🔷 promptfoo identifié | Égalité de chantier |
| Conformité | GCC : PDPL UAE, bibliothèque juridique citée par article **dans le prompt de Sentinel** ; bibliothèque de clauses standard = « positions préférées = capital » | RGPD/AI Act, registre art. 30, DPO | Juridictions différentes ; **l'idée « bibliothèque de clauses = capital méthodologique versionné » est à reprendre** pour notre capacité Juridique & contrats (clauses IA) |
| Posture sécurité | Exclue du partage (démarche d'assainissement sérieuse et bien pensée) | Incident CLIENT_SECRET S38, règle presse-papiers | Leur discipline d'assainissement du partage (placeholders typés, exclusion par défaut) est en soi un modèle si nous partageons un jour |

---

## 3. Synthèse — qui est « plus avancé » sur l'IA company à l'échelle ?

**L'intuition du gardien est validée sur les blocs métiers, avec un périmètre précis : ils ont un (1) workflow de bout en bout réellement éprouvé — la qualification/production d'AO — et une logique CRM d'une maturité doctrinale supérieure à la nôtre.** WF1 est exactement ce que notre règle « soldé = éprouvé sur le réel » désigne, et ils l'ont atteint sur leur flux le plus critique. Leur moteur d'autorisation est aussi formellement supérieur à tout ce que nous avons (mais jamais confronté au réel, de leur propre aveu).

**En revanche, sur l'objectif « à l'échelle » proprement dit, nous restons devant, et la lecture le confirme plutôt qu'elle ne l'infirme.** Leur système est un monolithe applicatif dont la vérité vit en base, la promotion en conventions, l'historique nulle part ; pas de contrats de périmètre, pas de rôle d'animateur, pas de rollback en une action, et une gouvernance qui suppose un CEO au centre de chaque approbation (Niveau 1 partout — ce qui ne passe pas 1→200). Six de leurs vingt-et-un agents sont des personas sans exécution ; leur propre matrice d'audit — pratique admirable — le documente. Ils ont construit une très bonne *firme augmentée à trois personnes* ; l'architecture d'*organisation qui grandit sans se réécrire* est de notre côté.

Autrement dit : **ils sont en avance sur ce qui se voit (workflows, CRM, produit), nous sommes en avance sur ce qui tient (canon, contrats, promotion, preuve).** Les deux avances sont réelles ; elles ne sont pas sur le même étage.

## 4. Pillage recommandé, hiérarchisé

1. **Table de politiques + test de couverture CI → chantier `impact.py` / serveur MCP.** Chaque chemin (`outils/mcp-graph/**` = large, toujours) et chaque outil MCP déclaré dans une table exhaustive ; un test CI casse si un élément n'a pas d'entrée ; refus par défaut. C'est la forme finie du correctif anomalie S38, plus concrète que MakerChecker/gait car implémentée et testée dans un contexte cabinet.
2. **WF1 comme gabarit de notre branche AO** (quand son tour viendra dans l'ordre de bataille) : filtres absolus déterministes avant tout compute IA, grille de scoring dont l'**agrégation est du code, jamais de l'IA**, statuts avec boucle Reformulate, runbook. À transposer sur notre substrat (SharePoint + crans), pas à copier.
3. **Filtre concurrent NDA** : formaliser dans nos contrats la règle « tout actif promu conserve sa traçabilité de mission d'origine et est exclu de tout contexte servant un concurrent du client source ; la liste de concurrence est posée par le gardien, jamais inférée ». Condition de la capitalisation intermissions — à écrire avant d'avoir plusieurs clients, pas après.
4. **CRM : dérivation systématique** (« jamais saisi, toujours déduit », absence de donnée = inconnu, dormance pondérée par l'enjeu, une seule source de forecast) → à intégrer dès la conception des gestes guidés pipe (priorité 3). Les fonctions pures de `contact-stage.ts` sont quasi transposables telles quelles.
5. **Plafond de dette de décision** sur la Zone-de-proposition (leur défaut : 15 candidats en attente max, ingestion en pause au-delà) — protection directe du gardien mono-personne.
6. **Matrice conçu-vs-câblé auditée** comme artefact de gouvernance récurrent : notre équivalent serait un état ✅/🟡/🔷 par capacité de la carte, audité contre le canon à chaque clôture de sprint. Antidote structurel au faux-vert.
7. **Micro-pillages** : coût USD par run (FinOps IA), boucle editDiff→StylePreference (apprentissage léger des corrections humaines), horodatage hors préfixe de cache, bibliothèque de clauses standard comme actif versionné (branche juridique), zéro id de modèle en dur.

## 5. Ce qu'on n'adopte pas

Le monolithe applicatif comme surface unique (notre pari substrat + gouvernance est l'inverse, et leur Niveau 1 CEO-partout montre la limite d'échelle) ; les personas humaines fictives (choix de produit, coût de complexité identitaire sans gain de gouvernance) ; la promotion par état en base sans journal ni diff ; une seconde source de vérité identitaire en code applicatif (notre DNA, c'est le canon).
