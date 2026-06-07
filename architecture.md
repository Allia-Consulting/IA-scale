# Architecture du SI augmenté — Allia (document de référence)

> **Nature** : document de référence **vivant**. Il **décrit** la topologie technique et l'état du SI ; il ne **gouverne pas**.
> **Ce n'est PAS un contrat socle. Il ne fait pas foi.** En cas de **divergence** avec `doctrine/doctrine.md` ou un contrat socle (`contrats/socle/*`), **c'est le canon qui fait foi**, jamais ce document. Si une ligne d'ici contredit le canon, c'est cette ligne qui a tort — corrigez-la.
> **Domicile** : `/architecture.md` (racine du dépôt de fondations).
> **Ne duplique aucune règle.** Quand une règle est nécessaire, ce document **renvoie** au texte qui fait foi. Répartition : la doctrine dit *le pourquoi et les règles* ; `backlog/plan.md` dit *le chantier* ; `contrats/socle/organisation.md` dit *qui répond de quoi* ; **ce document dit la *topologie technique* et l'*état du SI***.
> **État** : photo datée du **7 juin 2026**. La Partie C **se périme** — vérifier les *sources de vérité* indiquées.

---

## Partie A — Topologie technique : comment les trois mondes s'emboîtent

Le SI repose sur trois mondes aux rôles distincts. La règle qui les sépare se résume ainsi : **Git gouverne, M365 affiche et stocke, Azure exécute.**

| Monde | Rôle | Contient |
|---|---|---|
| **Git** (dépôt de fondations) | **Gouverne** | le canon (règles : doctrine, contrats socle, skills, profils, backlog) **et** le code versionné (ex. `outils/mcp-graph/`) |
| **Azure** (fonctions / agent) | **Exécute** | la logique métier : calcule, détient les secrets, écrit dans M365 |
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
   *Pourquoi* : l'infrastructure doit **tourner sans lui** (événementiel, disponible, sans dépendance à une machine personnelle). **Hébergement cible : Azure.** **État : décidé, non déployé** (le code du connecteur existe — `outils/mcp-graph/` ; son déploiement reste un runbook, `backlog/chantiers/T-0002.yaml`).

5. **Calcul pur vs travail de jugement** — deux natures d'exécution à ne pas confondre :
   - **calcul pur** : fonction **déterministe** (ex. un P&L) — entrées → sortie reproductible, pas de jugement ;
   - **travail de jugement** : **agent Claude guidé par un skill versionné** (ex. un kick-off) — résout le canon, applique un skill, produit un dérivé.
   *Pourquoi* : on n'engage un agent que là où il y a du jugement ; le déterministe reste une fonction, plus simple à éprouver et à tracer.

---

## Partie C — Inventaire du SI

> **État au 7 juin 2026 — se périme, vérifier les sources.** Légende : **FAIT** / **PARTIEL** / **À FAIRE** / *à confirmer par le gardien* (état non constatable depuis le dépôt). Chaque ligne indique **où vérifier la vérité**.

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
| Secret client (de l'app registration) | **FAIT** — créé et stocké hors dépôt par le gardien | Entra / coffre de secrets |
| Octroi du rôle `write` sur le site AlliaConsuling | **FAIT** — accordé via Graph, confirmé | Graph `POST /sites/{id}/permissions` |
| Hébergement de la fonction (Azure, événementiel) | **À FAIRE** (décidé, non déployé — Partie B.4) | portail Azure |

> Tout ce bloc relève du **runbook humain** (création d'app, consentement, secret) — voir `backlog/chantiers/T-0002.yaml` (statut `à_faire`) et les garde-fous `CLAUDE.md` / `backlog/plan.md` §2.

### Couche M365
| Composant | État | Source de vérité |
|---|---|---|
| Site SharePoint AlliaConsuling | **FAIT** — site et listes existants au tenant | `contrats/socle/modele-donnees.md` §2 bis + tenant M365 |
| Listes du modèle de données (Missions, Temps, …) | **PARTIEL** — listes **existantes au tenant** (lecture) **FAIT** ; **écriture** via Graph = `T-0002` (à faire) | `modele-donnees.md` §2 bis / §4 + tenant |
| Zone de proposition | **PARTIEL** — **réelle** (Liste « Zone-de-proposition ») **À FAIRE** (`T-0002`) ; **simulée en local** (`zone-proposition/`) **FAIT** | `modele-donnees.md` §3 / §4 |
| Audit / journalisation sur `Ressources-RH` et `CVs` | **À FAIRE** (à activer avant tout accès agent — `T-0003`, runbook) | `modele-donnees.md` §2 bis + tenant |
| Écrans de saisie (SharePoint puis Power Apps) | **À FAIRE** (décision Partie B.1 ; non construits) | tenant M365 |

### Couche agents / skills
| Composant | État | Source de vérité |
|---|---|---|
| Skill `compte-rendu-reunion` | **FAIT** — promu (v1.1) | `skills/compte-rendu-reunion/SKILL.md` |
| Skill `releve-de-decisions` | **FAIT** — promu (v1.1) | `skills/releve-de-decisions/SKILL.md` |
| Profil `agent-redaction` (compose les deux skills) | **FAIT** (présent ; en-tête candidat v1.0) | `agents/agent-redaction/profil.yaml` |
| Serveur MCP Graph (`list_items`, `create_list_item`) | **PARTIEL** — **codé, non déployé** (code dormant) | `outils/mcp-graph/` + `T-0002` |
| Agent métier « kick-off » | **À FAIRE** — **conçu, non construit** | `backlog/plan.md` §6 (T-1.2) |

---

*Document de référence vivant. Il décrit ; il ne gouverne pas. La vérité des règles vit dans le canon (`doctrine/`, `contrats/socle/`), celle de l'état réel vit dans les sources indiquées ci-dessus. Mettre à jour la Partie C au fil des déploiements.*
