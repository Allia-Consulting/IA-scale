# Architecture du SI augmenté — Allia (document de référence)

> **Nature** : document de référence **vivant**. Il **décrit** la topologie technique et l'état du SI ; il ne **gouverne pas**.
> **Ce n'est PAS un contrat socle. Il ne fait pas foi.** En cas de **divergence** avec `doctrine/doctrine.md` ou un contrat socle (`contrats/socle/*`), **c'est le canon qui fait foi**, jamais ce document. Si une ligne d'ici contredit le canon, c'est cette ligne qui a tort — corrigez-la.
> **Domicile** : `/architecture.md` (racine du dépôt de fondations).
> **Ne duplique aucune règle.** Quand une règle est nécessaire, ce document **renvoie** au texte qui fait foi. Répartition : la doctrine dit *le pourquoi et les règles* ; `backlog/plan.md` dit *le chantier* ; `contrats/socle/organisation.md` dit *qui répond de quoi* ; **ce document dit la *topologie technique* et l'*état du SI***.
> **État** : photo datée du **8 juin 2026** (session doctrine — entrée en Phase 1). La Partie C **se périme** — vérifier les *sources de vérité* indiquées.

---

## Partie A — Topologie technique : comment les trois mondes s'emboîtent

Le SI repose sur trois mondes aux rôles distincts. La règle qui les sépare se résume ainsi : **Git gouverne, M365 affiche et stocke, Azure exécute.**

| Monde | Rôle | Contient |
|---|---|---|
| **Git** (dépôt de fondations) | **Gouverne** | le canon (règles : doctrine, contrats socle, skills, profils, backlog) **et** le code versionné (ex. `outils/mcp-graph/`) |
| **Azure** (Container Apps / agent) | **Exécute** | la logique métier : calcule, écrit dans M365. **Sous identité managée — ne détient aucun secret applicatif** (le jeton est injecté par Azure ; Partie B.4 bis) |
| **M365** (surfaces + données) | **Affiche et stocke** | les surfaces de saisie et les *faits* (missions, temps, livrables…) |

**Le flux nominal d'une action métier :**

1. une **surface M365** (écran de saisie) déclenche une **fonction Azure** (appel web) ;
2. la fonction **invoque l'agent / la logique** métier ;
3. la logique **écrit le résultat en zone de proposition**, jamais dans la source — *le dérivé n'est jamais le saisi* (règle : `doctrine.md` §2 ; domicile de la zone : `contrats/socle/modele-donnees.md` §3).

**La frontière, et pourquoi elle ne trahit pas la doctrine.** Les surfaces de saisie peuvent vivre dans M365 sans contredire « une seule vérité, un seul domicile » : elles ne **portent** aucune règle — elles **appliquent** des règles qui vivent dans Git et se résolvent à l'exécution (mécanisme de résolution : `CLAUDE.md` ; principe *pull, jamais push* : `doctrine.md` §2 et §8). Un écran M365 est un *consommateur* du canon, pas un double éditable.

> Les deux plans (gouverner une règle vs exécuter une affaire) et la règle d'or « le gardien n'est jamais dans la boucle d'exécution » sont définis en `doctrine.md` §4 — ce document ne les réénonce pas, il s'y conforme.

---

## Partie B — Décisions d'architecture et leur *pourquoi*

Les arbitrages tranchés, avec la raison (ce qui se perdrait si on l'oubliait). Renvoi au canon quand la règle correspondante y est inscrite.

1. **Les écrans de saisie vivent dans M365** (SharePoint d'abord, Power Apps ensuite), pas en HTML sur mesure.
   *Pourquoi* : on hérite des **droits Entra natifs** et il n'y a **aucune authentification à coder** ; c'est cohérent avec « M365 affiche/stocke, Git gouverne » (Partie A). Coder une auth maison reviendrait à recréer ce que M365 fournit déjà — et hors de la chaîne de droits gouvernée (`organisation.md` §5).

2. **L'agent métier ne passe jamais par le gardien.**
   *Pourquoi* : c'est la **règle d'or des deux plans** (`doctrine.md` §4) — le gardien gouverne les règles, pas les affaires. La validation d'une **sortie de firme** (livrable, publication) relève d'un **rôle métier habilité** (`doctrine.md` §6 ; grille concrète : `organisation.md` §4 bis), jamais du gardien en tant que gardien.

3. **L'anonymisation se déclenche à la SORTIE EXTERNE**, pas sur la réutilisation inter-client interne.
   *Pourquoi* : l'interne reste **nominatif** — c'est l'avantage qui compose (apprentissage inter-missions). Le déclencheur exact et le critère font foi dans `contrats/socle/anonymisation.md` §1 (et la version machine `contrats/socle/table-des-crans.yaml`).

4. **La logique d'écriture ne tourne PAS sur le poste du fondateur.**
   *Pourquoi* : l'infrastructure doit **tourner sans lui** (événementiel, disponible, sans dépendance à une machine personnelle). **Hébergement cible : Azure.** **État : décidé, non déployé** (le code du connecteur existe — `outils/mcp-graph/` ; son déploiement reste un runbook, `backlog/chantiers/T-0002b.yaml`).

4 bis. **Cible Azure précisée : Container Apps (scale-to-zero, événementiel), App Service en repli ; identité managée, pas de secret.** *(Décision du 8 juin 2026.)*
   *Pourquoi* : un service **événementiel** qui dort à zéro coût et se réveille à la demande colle au profil d'usage (écriture occasionnelle en zone de proposition) ; **Container Apps** offre ce scale-to-zero, **App Service** est le repli si une contrainte l'impose. Surtout, le service prend une **identité managée** (managed identity) : Azure injecte le jeton, **aucun secret n'est porté par l'application**. Conséquences, à exécuter dans `T-0002b` (code, à faire) et son runbook `T-0002a-bis` (octroi, à faire) :
   - `server.py` passe de `ClientSecretCredential` à **`DefaultAzureCredential`** ;
   - la variable **`GRAPH_CLIENT_SECRET` est supprimée** (plus aucun secret client à stocker ni injecter) ;
   - **Key Vault devient *optionnel*** pour ce service (il ne détient plus de secret applicatif à protéger).
   - **L'identité managée est un principal Entra DISTINCT** de l'app registration `allia-mcp-graph` de `T-0002a`. Le rôle `write` `Sites.Selected` accordé à l'ancienne app **ne se transfère pas** : il faut **ré-octroyer `write` au principal de l'identité managée** sur le seul site AlliaConsuling. C'est un **runbook humain** (`backlog/chantiers/T-0002a-bis.yaml`, à_faire) — jamais un agent ne configure une permission (garde-fous `CLAUDE.md` ; `table-des-crans.yaml` : proscrites).

5. **Calcul pur vs travail de jugement** — deux natures d'exécution à ne pas confondre :
   - **calcul pur** : fonction **déterministe** (ex. un P&L) — entrées → sortie reproductible, pas de jugement ;
   - **travail de jugement** : **agent Claude guidé par un skill versionné** (ex. un kick-off) — résout le canon, applique un skill, produit un dérivé.
   *Pourquoi* : on n'engage un agent que là où il y a du jugement ; le déterministe reste une fonction, plus simple à éprouver et à tracer.

6. **Le parc de postes se gouverne en trois couches : ABM → Intune → Entra ; on canonise la POLITIQUE, pas l'exécution.** *(Décision du 8 juin 2026.)*
   *Pourquoi* : un poste de collaborateur s'inscrit dans une chaîne — **Apple Business Manager (ABM)** rattache le matériel à la firme et le pousse vers la gestion ; **Intune** applique le profil de poste (apps déployées, posture de sécurité, conformité) ; **Entra** porte les **groupes d'enrôlement** qui lient l'appareil à la politique. La **politique** (profil par fonction, apps, posture, groupes) est **canonisée** dans `contrats/socle/parc-collaborateur.md` (candidat) ; la **configuration effective** ABM/Intune est un **runbook humain**. La réconciliation automatique *politique → Intune* est un chantier **Phase 3/4** (backlog), pas construit aujourd'hui. Cette couche est l'application aux **appareils** de la chaîne d'autorité `guide → Claude → M365` (doctrine §8, ligne candidate v1.4) : on change la politique dans le guide, M365/Intune suit — jamais l'inverse.

7. **La mémoire d'organisation s'écrit par batch nocturne, en proposition — l'écriture continue est abandonnée.** *(Décision du 8 juin 2026.)*
   *Pourquoi* : un **batch Cowork nocturne** (jeudi → vendredi) écoute les conversations Claude + Teams de la semaine et produit **une** synthèse **candidate** ; la validation est **ligne à ligne le vendredi** (non-validé = oublié). C'est « le dérivé n'est jamais le saisi » appliqué à la mémoire : la synthèse atterrit en **zone de proposition** (liste « Zone-de-proposition », champ d'origine **« mémoire hebdo »** — `modele-donnees.md` §2 bis/§3), **simulée en local** sous `zone-proposition/memoire/` en attendant `T-0002b`. Le contrat qui régit ce mécanisme est `contrats/socle/memoire-organisation.md` (candidat), à renvoi normatif vers `anonymisation.md`. *Pourquoi pas l'écriture continue* : une mémoire qui se réécrit en continu n'est ni relisible ni gouvernable à la promotion ; un rendez-vous hebdomadaire candidat l'est.

---

## Partie C — Inventaire du SI

> **État au 8 juin 2026 — se périme, vérifier les sources.** Légende : **FAIT** / **PARTIEL** / **À FAIRE** / *à confirmer par le gardien* (état non constatable depuis le dépôt). Chaque ligne indique **où vérifier la vérité**.

### Couche GitHub / canon
| Composant | État | Source de vérité |
|---|---|---|
| Dépôt de fondations (canon + code) | **FAIT** | le dépôt lui-même |
| Protection de branche (« Main-protection » sur `main`) | **FAIT** — règle active : PR obligatoire avant merge, suppression et force-push bloqués. Le **statut CI (agent-gardien) est délibérément CONSULTATIF** (non requis pour merger), par choix du gardien tant que l'agent-gardien est en v0. Qu'une PR puisse merger malgré une CI rouge est donc la conséquence **voulue** d'un statut consultatif, **pas** une absence de protection. | GitHub → Settings → Branches |
| `CODEOWNERS` (gardien sur le socle) | **Fichier correct, dormant.** Le handle `@Alliaconsulting` est un **compte réel**, membre de l'org `Allia-Consulting`, avec accès **Write** au dépôt (donc Code Owner valide). La **revue Code Owners n'est pas activée** dans la protection de branche, par **choix du gardien** tant qu'il est seul (un solo ne peut approuver ses propres PR). **S'activera à la première délégation.** | `.github/CODEOWNERS` + GitHub |
| Agent-gardien CI (avis d'impact, ne merge jamais) | **FAIT** | `.github/workflows/conformite.yml` |
| Secret `ANTHROPIC_API_KEY` (clé de l'agent-gardien CI) | **FAIT** (confirmé indirectement : les avis d'impact ont été produits sur les PR récentes) | GitHub → Settings → Secrets |
| Connecteur GitHub / résolution Claude Code (pull du canon à l'exécution) | **FAIT** | `CLAUDE.md` |

### Couche Azure / Entra
| Composant | État | Source de vérité |
|---|---|---|
| App registration `allia-mcp-graph` | **FAIT** — créée dans Entra | portail Entra |
| Permission application `Sites.Selected` | **FAIT** — accordée, consentement admin donné | portail Entra |
| Secret client (de l'app registration) | **FAIT** — créé et stocké hors dépôt par le gardien. ⚠️ **Devient inutile** avec l'identité managée (Partie B.4 bis) : `GRAPH_CLIENT_SECRET` supprimé, Key Vault optionnel. | Entra / coffre de secrets |
| Octroi du rôle `write` sur le site AlliaConsuling (app registration) | **FAIT** — accordé via Graph, confirmé | Graph `POST /sites/{id}/permissions` |
| Identité managée du service (principal Entra distinct) | **À FAIRE** (Partie B.4 bis — créée avec l'hébergement Container Apps) | portail Azure / Entra |
| Ré-octroi du rôle `write` au principal de l'identité managée | **À FAIRE** — **runbook humain** `T-0002a-bis` (`à_faire`) : l'identité managée est un **principal distinct**, l'octroi de `T-0002a` ne se transfère pas | Graph `POST /sites/{id}/permissions` |
| Hébergement de la fonction (Azure **Container Apps**, scale-to-zero ; App Service en repli) | **À FAIRE** (décidé, non déployé — Partie B.4 / B.4 bis) | portail Azure |

> La partie **runbook humain** de l'app M365/Entra (app registration, `Sites.Selected`, consentement admin, secret, octroi du rôle `write` sur le site) est **réalisée** — chantier **`T-0002a`** (`promu`). Reste à faire : le **code MCP est écrit mais non déployé** (`outils/mcp-graph/`), l'**hébergement Azure** — désormais **Container Apps**, scale-to-zero, sous **identité managée** (B.4 bis) — et, conséquence de l'identité managée, le **ré-octroi `write`** au nouveau principal : chantiers **`T-0002b`** (déploiement + bascule du code vers `DefaultAzureCredential`, `à_faire`) et **`T-0002a-bis`** (runbook d'octroi, `à_faire`). À noter : **`T-0002b` est désormais DÉCOUPLÉ de `T-0003`** — il écrit en **Zone-de-proposition**, pas dans `Ressources-RH`/`CVs` ; `T-0003` reste prérequis de la lecture RH réelle, plus de `T-0002b`. Garde-fous : `CLAUDE.md` / `backlog/plan.md` §2.

### Couche M365
| Composant | État | Source de vérité |
|---|---|---|
| Site SharePoint AlliaConsuling | **FAIT** — site et listes existants au tenant | `contrats/socle/modele-donnees.md` §2 bis + tenant M365 |
| Listes du modèle de données (Missions, Temps, …) | **PARTIEL** — listes **existantes au tenant** (lecture) **FAIT** ; **écriture** via Graph = `T-0002b` (à faire) | `modele-donnees.md` §2 bis / §4 + tenant |
| Zone de proposition | **PARTIEL** — **réelle** (Liste « Zone-de-proposition ») **À FAIRE** (`T-0002b`) ; **simulée en local** (`zone-proposition/`) **FAIT** | `modele-donnees.md` §3 / §4 |
| Audit / journalisation sur `Ressources-RH` et `CVs` | **À FAIRE** (à activer avant tout accès agent — `T-0003`, runbook) | `modele-donnees.md` §2 bis + tenant |
| Écrans de saisie (SharePoint puis Power Apps) | **À FAIRE** (décision Partie B.1 ; non construits) | tenant M365 |
| Mémoire d'organisation — synthèse hebdo candidate (champ d'origine « mémoire hebdo ») | **PARTIEL** — **simulée en local** (`zone-proposition/memoire/`) ; cible réelle (Liste « Zone-de-proposition ») **À FAIRE** (`T-0002b`) ; batch Cowork nocturne **À FAIRE** | `contrats/socle/memoire-organisation.md` (candidat) + `modele-donnees.md` §2 bis/§3 |

### Couche parc / poste de travail (ABM · Intune · Entra)
| Composant | État | Source de vérité |
|---|---|---|
| Politique de parc (profil de poste, apps, posture sécurité, groupes Entra d'enrôlement) | **PARTIEL** — **politique canonisée** (candidat) ; rien de déployé | `contrats/socle/parc-collaborateur.md` (candidat) |
| Enrôlement ABM (rattachement matériel → firme) | **À FAIRE** — **runbook humain** (config tenant/ABM, proscrite à l'agent) | portail Apple Business Manager + tenant |
| Profils & conformité Intune (apps, posture) | **À FAIRE** — **runbook humain** | portail Intune |
| Groupes Entra d'enrôlement | **À FAIRE** — **runbook humain** ; projection au moindre privilège (cf. `organisation.md` §5) | portail Entra |
| Réconciliateur automatique *politique → Intune* | **À FAIRE** — chantier **Phase 3/4** (backlog), non construit | `backlog/chantiers/` |

### Couche agents / skills
| Composant | État | Source de vérité |
|---|---|---|
| Skill `compte-rendu-reunion` | **FAIT** — promu (v1.1) | `skills/compte-rendu-reunion/SKILL.md` |
| Skill `releve-de-decisions` | **FAIT** — promu (v1.1) | `skills/releve-de-decisions/SKILL.md` |
| Profil `agent-redaction` (compose les deux skills) | **FAIT** (présent ; en-tête candidat v1.0) | `agents/agent-redaction/profil.yaml` |
| Serveur MCP Graph (`list_items`, `create_list_item`) | **PARTIEL** — **codé, non déployé** (code dormant) | `outils/mcp-graph/` + `T-0002b` |
| Agent métier « kick-off » | **À FAIRE** — **conçu, non construit** | `backlog/plan.md` §6 (T-1.2) |

---

*Document de référence vivant. Il décrit ; il ne gouverne pas. La vérité des règles vit dans le canon (`doctrine/`, `contrats/socle/`), celle de l'état réel vit dans les sources indiquées ci-dessus. Mettre à jour la Partie C au fil des déploiements.*
