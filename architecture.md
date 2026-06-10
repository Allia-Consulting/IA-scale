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
   *Pourquoi* : l'infrastructure doit **tourner sans lui** (événementiel, disponible, sans dépendance à une machine personnelle). **Hébergement cible : Azure.** **État : déployé** (10 juin 2026 — chapeau `T-0002b` promue ; service `ca-allia-mcp-graph` sur Container Apps, voir Partie C).

4 bis. **MCP en SERVICE HTTP distant sur Container Apps (min 1 réplica) ; zéro secret côté Graph (identité managée), un secret serveur côté entrée (Easy Auth).** *(Décision du 8 juin 2026 — modèle d'hébergement précisé le 9 juin 2026, d'après la doc Microsoft « Host/Secure MCP servers on Azure Container Apps ».)*
   *Pourquoi* : le connecteur devient un **service HTTP distant** (et non plus un serveur stdio lancé localement), pour qu'à terme ~10 collaborateurs l'utilisent **sans dépendre du poste du fondateur** (exigence B.4).

   **Modèle d'hébergement.**
   - **Standalone container app** ; transport MCP **streamable HTTP** (endpoint **`/mcp`**) ; TLS assuré par l'ingress Container Apps ; SDK Python MCP en mode **stateless** (`stateless_http=True`).
   - **Endpoint de santé séparé** : **`/healthz`**, distinct de `/mcp` (les sondes font des **GET** simples ; `/mcp` attend du **JSON-RPC POST**).
   - **Scaling : min 1 réplica** (usage interactif réactif). *(Ceci **corrige** la cible d'échelle antérieure — un service interactif doit répondre **sans démarrage à froid** ; **App Service** reste le repli si une contrainte l'impose.)*
   - **Réseau** : public **+ restrictions** (IP restrictions / CORS au besoin) ; durcissement VNet / internal-only **repoussé en Phase 2/3**.

   **La double frontière de secret — deux régimes distincts, à ne jamais confondre :**
   - **Sortie vers Graph** (le service écrit dans M365) : **ZÉRO SECRET**, via l'identité managée **user-assigned `id-allia-mcp-graph`** (`DefaultAzureCredential`). **Inchangé** depuis le 8 juin — le connecteur Graph ne reprend **aucun** secret applicatif. Conséquences code (sous-tâche `T-0002b-1`, non exécutée ici) : `server.py` passe de `ClientSecretCredential` à **`DefaultAzureCredential`** ; **`GRAPH_CLIENT_SECRET` supprimée** ; **Key Vault optionnel** pour ce service.
   - **Entrée du service** (qui a le droit d'appeler `/mcp`) : **UN secret serveur**, porté par une app registration **« serveur »** via la **built-in auth Entra ID (« Easy Auth »)** de Container Apps. Tout appel porte un **bearer token OAuth 2.0**, sinon **401**. C'est **un** secret serveur **unique** (runbook humain), **pas** un secret par utilisateur, et **sans rapport avec le flux Graph**. *(Réalisé le 10 juin 2026 — runbook `T-0002b-4`, Easy Auth actif en Return401 ; état dans la Partie C.)*
   - **Identités appelantes** : les **humains** s'authentifient via **leur identité Entra** (client public **PKCE**, accès gouverné par le groupe **`grp-mcp-graph-users`** — *assignment required* sur l'enterprise app du service) ; les **workloads** via **identité managée** ; les **instruments du gardien** via **son identité Entra**. *(Décision du 10 juin 2026, stop doctrine ; la règle qui fait foi : `contrats/socle/identites-et-secrets.md`. L'app cliente **à secret** de `T-0002b-5` est en **extinction** — `T-0010`.)*

   > ⚠️ **« Zéro secret » borné, pas annulé.** Le « zéro secret » du 8 juin concernait la **sortie Graph** (identité managée) — il **reste vrai**. La frontière d'**entrée** Easy Auth introduit, elle, **un** secret serveur : frontière **nouvelle**, distincte du flux Graph. Formulation de référence : *« zéro secret côté Graph (identité managée) ; un secret serveur côté entrée Easy Auth, distinct du flux Graph »*.

   **Deux écarts décision ↔ exécution constatés le 9 juin 2026 (tracés) :**
   - **Séquence d'octroi pour une IDENTITÉ MANAGÉE** ≠ celle d'une app registration. Ce n'est pas le simple `POST /sites/{id}/permissions` : il faut **(1)** un **app role assignment** Entra `Sites.Selected` au **service principal de l'identité**, **puis (2)** le `POST /sites/{id}/permissions` avec le **`clientId` de l'identité** dans `application.id`. Les deux ont été réalisés le 9 juin (`T-0002a-bis`, **`promu`** — runbook exécuté le 9 juin 2026).
   - **Choix user-assigned (et non system-assigned)**, tranché le 9 juin. *Pourquoi* : identité **découplée du cycle de vie du conteneur** (elle survit aux redéploiements) et **droits octroyables AVANT déploiement** (on prépare l'octroi sans attendre que l'app existe).

   *Conséquence chantier* : `T-0002b` devient une **tâche-chapeau** redécoupée en sous-tâches **`T-0002b-1..5`** (code HTTP · image · déploiement · auth serveur · auth client) — voir `backlog/chantiers/`. *(Rappel d'en-tête : ce document **décrit**, il ne **gouverne pas** ; les crans et la nature « runbook humain » font foi dans `table-des-crans.yaml` et `CLAUDE.md`.)*

5. **Calcul pur vs travail de jugement** — deux natures d'exécution à ne pas confondre :
   - **calcul pur** : fonction **déterministe** (ex. un P&L) — entrées → sortie reproductible, pas de jugement ;
   - **travail de jugement** : **agent Claude guidé par un skill versionné** (ex. un kick-off) — résout le canon, applique un skill, produit un dérivé.
   *Pourquoi* : on n'engage un agent que là où il y a du jugement ; le déterministe reste une fonction, plus simple à éprouver et à tracer.

6. **Le parc de postes se gouverne en trois couches : ABM → Intune → Entra ; on canonise la POLITIQUE, pas l'exécution.** *(Décision du 8 juin 2026.)*
   *Pourquoi* : un poste de collaborateur s'inscrit dans une chaîne — **Apple Business Manager (ABM)** rattache le matériel à la firme et le pousse vers la gestion ; **Intune** applique le profil de poste (apps déployées, posture de sécurité, conformité) ; **Entra** porte les **groupes d'enrôlement** qui lient l'appareil à la politique. La **politique** (profil par fonction, apps, posture, groupes) est **canonisée** dans `contrats/socle/parc-collaborateur.md` (candidat) ; la **configuration effective** ABM/Intune est un **runbook humain**. La réconciliation automatique *politique → Intune* est un chantier **Phase 3/4** (backlog), pas construit aujourd'hui. Cette couche est l'application aux **appareils** de la chaîne d'autorité `guide → Claude → M365` (doctrine §8, ligne candidate v1.4) : on change la politique dans le guide, M365/Intune suit — jamais l'inverse.

7. **La mémoire d'organisation s'écrit par batch nocturne, en proposition — l'écriture continue est abandonnée.** *(Décision du 8 juin 2026.)*
   *Pourquoi* : un **batch Cowork nocturne** (jeudi → vendredi) écoute les conversations Claude + Teams de la semaine et produit **une** synthèse **candidate** ; la validation est **ligne à ligne le vendredi** (non-validé = oublié). C'est « le dérivé n'est jamais le saisi » appliqué à la mémoire : la synthèse atterrit en **zone de proposition** (liste « Zone-de-proposition », champ d'origine **« mémoire hebdo »** — `modele-donnees.md` §2 bis/§3), **simulée en local** sous `zone-proposition/memoire/` en attendant `T-0002b`. Le contrat qui régit ce mécanisme est `contrats/socle/memoire-organisation.md` (candidat), à renvoi normatif vers `anonymisation.md`. *Pourquoi pas l'écriture continue* : une mémoire qui se réécrit en continu n'est ni relisible ni gouvernable à la promotion ; un rendez-vous hebdomadaire candidat l'est. *(Décision du 10 juin 2026 — stop doctrine : le batch tourne en **Cowork local** sur le poste du gardien, sous l'**identité Entra du gardien** — zéro secret, `identites-et-secrets.md` §2 cas 3. **Écart à B.4 assumé et borné** : limité à la mémoire d'organisation, réversible à la fédération du rôle gardien — voir `T-0005`.)*

---

## Partie C — Inventaire du SI

> **État au 10 juin 2026 — se périme, vérifier les sources.** Légende : **FAIT** / **PARTIEL** / **À FAIRE** / *à confirmer par le gardien* (état non constatable depuis le dépôt). Chaque ligne indique **où vérifier la vérité**.

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
| Identité managée **user-assigned `id-allia-mcp-graph`** (principal Entra distinct) | **FAIT** — créée le 9 juin (user-assigned : découplée du cycle de vie du conteneur, droits octroyables avant déploiement — B.4 bis) | portail Azure / Entra |
| Ré-octroi `write` au principal de l'identité managée | **FAIT** — runbook `T-0002a-bis` réalisé le 9 juin : **(1)** app role assignment `Sites.Selected` au service principal de l'identité, **(2)** `POST /sites/{id}/permissions` avec le `clientId` de l'identité | Graph (app role assignment + `POST /sites/{id}/permissions`) |
| Registre de conteneurs **ACR `acralliamcpgraph`** (Basic, francecentral, rg-ia-scale) | **FAIT** — runbook `T-0002b-2` exécuté le 10 juin 2026 ; **admin user désactivé**, jetons d'audience ARM (`authentication-as-arm`) **activés** (prérequis du pull par identité managée, `T-0002b-3`) | portail Azure / `az acr show` |
| Image **`allia-mcp-graph:0.1.0`** (linux/amd64) poussée dans l'ACR | **FAIT** — buildée côté ACR (`az acr build --platform linux/amd64`) et poussée le 10 juin 2026 ; digest `sha256:34167f9e…` | `az acr repository show-tags` |
| Hébergement (Azure **Container Apps**, **min 1 réplica**) | **FAIT** — runbook `T-0002b-3` exécuté le 10 juin 2026 : environnement **`cae-ia-scale`** + container app **`ca-allia-mcp-graph`** (francecentral, rg-ia-scale), **min 1 / max 1 réplica**, identité user-assigned `id-allia-mcp-graph` attachée, pull ACR par identité managée (AcrPull) ; **restriction IP transitoire** « allow-gardien » (fenêtre pré-Easy-Auth, à lever fin `T-0002b-4`) | portail Azure / `az containerapp show` |
| Service MCP **HTTP distant** (`/mcp` streamable + `/healthz`, stateless) | **FAIT** — les **cinq sous-tâches `T-0002b-1..5` promues** (10 juin 2026) ; FQDN `ca-allia-mcp-graph.delightfulocean-1bf3f3c5.francecentral.azurecontainerapps.io` ; entrée Easy Auth **prouvée dans les deux sens** (sans token → 401 ; bearer du principe appelant → 200, handshake MCP) ; **restriction IP transitoire « allow-gardien » LEVÉE le 10 juin** (contre-preuve : 401 sans token depuis une IP quelconque — la porte du canon est la seule porte) | portail Azure + `az containerapp auth show` |
| App registration **« serveur »** Easy Auth (built-in auth Entra) + secret serveur | **FAIT** — runbook `T-0002b-4` exécuté le 10 juin 2026 : app **`allia-mcp-graph-server-auth`** (mono-tenant), clientId `0028a5ff-925a-4700-b703-2f2d0ce728fc`, app role **`MCP.Invoke`** posé (octroi = `T-0002b-5` ; validation code = `T-0009`), Easy Auth actif en **Return401** ; **secret serveur unique hors dépôt, expire juin 2028**. Preuve 401 OK ; preuve token = `T-0002b-5`. Secret serveur = **dette tracée** (`identites-et-secrets.md` §4) ; cible : suppression ou identité managée fédérée, **à instruire avant juin 2028** | portail Entra / `az containerapp auth show` |
| App registration **« client »** (principe appelant unique) + tokens | **FAIT** — runbook `T-0002b-5` exécuté le 10 juin 2026 : app **`allia-mcp-graph-client`** (mono-tenant), clientId `77aa6010-e3a8-4404-8c34-5f352e0c589a`, rôle **`MCP.Invoke`** octroyé + consentement admin accordé ; **secret client hors dépôt, expire juin 2028** ; tokens en client credentials (curl pur). Secret client = **dette tracée** (`identites-et-secrets.md` §4) ; cible : **extinction** (`T-0010` — client public PKCE, suppression du secret après preuve) | portail Entra |
| Branchement **Claude Code par identité de personne** (`.mcp.json`, scope project) | **À FAIRE** — `T-0010` (part agent : `.mcp.json` + README ; part runbook : scope délégué `access_as_user`, client public, *assignment required* + groupe `grp-mcp-graph-users`) | `.mcp.json` + portail Entra |

> La partie **runbook humain** de l'app M365/Entra (app registration, `Sites.Selected`, consentement admin, secret, octroi du rôle `write` sur le site) est **réalisée** — chantier **`T-0002a`** (`promu`) — et le **ré-octroi `write` à l'identité managée** est réalisé le 9 juin — **`T-0002a-bis`** (`promu`, runbook exécuté le 9 juin 2026). Le **service MCP HTTP distant** est **réalisé** (chapeau `T-0002b` **promue** le 10 juin 2026, cinq sous-tâches prouvées) : `T-0002b` avait été redécoupée en **`T-0002b-1`** (code stdio→HTTP streamable, `/healthz`, bascule `DefaultAzureCredential`, suppression `GRAPH_CLIENT_SECRET` — agent), **`T-0002b-2`** (image : Dockerfile = agent ; ACR = runbook), **`T-0002b-3`** (déploiement Container App min 1 réplica, attache identité managée — runbook), **`T-0002b-4`** (app reg « serveur » Easy Auth + secret — runbook), **`T-0002b-5`** (app reg « client » + tokens — runbook). À noter : **`T-0002b` reste DÉCOUPLÉ de `T-0003`** — il écrit en **Zone-de-proposition**, pas dans `Ressources-RH`/`CVs` ; `T-0003` reste prérequis de la lecture RH réelle. Garde-fous : `CLAUDE.md` / `backlog/plan.md` §2.

### Couche M365
| Composant | État | Source de vérité |
|---|---|---|
| Site SharePoint AlliaConsuling | **FAIT** — site et listes existants au tenant | `contrats/socle/modele-donnees.md` §2 bis + tenant M365 |
| Listes du modèle de données (Missions, Temps, …) | **PARTIEL** — listes **existantes au tenant** (lecture) **FAIT** ; **écriture des dérivés outillée** via la Zone-de-proposition (`T-0002b` fait) — le connecteur n'écrit **jamais** dans les sources (garde-fou structurel) | `modele-donnees.md` §2 bis / §4 + tenant |
| Zone de proposition | **FAIT** (de bout en bout) — Liste « Zone-de-proposition » créée le 10 juin 2026 (colonne « Origine » = champ d'origine, id Graph `2590d442-6e7d-4802-b271-451212ea10d4`) et **écriture réelle prouvée le même jour** (`create_list_item` → `created_id: 1`, item de preuve « test-gardien », écriture signée par l'**application** via identité managée) ; les **nouveaux dérivés** s'écrivent dans la liste réelle — les synthèses « mémoire hebdo » basculeront avec `T-0005` | `modele-donnees.md` §2 bis / §3 + tenant |
| Audit / journalisation sur `Ressources-RH` et `CVs` | **À FAIRE** (à activer avant tout accès agent — `T-0003`, runbook) | `modele-donnees.md` §2 bis + tenant |
| Écrans de saisie (SharePoint puis Power Apps) | **À FAIRE** (décision Partie B.1 ; non construits) | tenant M365 |
| Mémoire d'organisation — synthèse hebdo candidate (champ d'origine « mémoire hebdo ») | **PARTIEL** — **simulée en local** (`zone-proposition/memoire/`) ; l'infrastructure d'écriture est **prête** (chapeau `T-0002b` promue, liste réelle prouvée) ; la bascule des synthèses et le batch Cowork nocturne = **À FAIRE** (`T-0005`) | `contrats/socle/memoire-organisation.md` (candidat) + `modele-donnees.md` §2 bis/§3 |

> **Écart constaté le 10 juin 2026 (non corrigé)** : le site porte une liste **« Ressource-Profil »** (singulier) là où le canon dit **« Ressources-Profil »** (`modele-donnees.md` §2 bis). Micro-ajustement à arbitrer par le gardien (renommer la liste au tenant, ou aligner le canon).

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
| Serveur MCP Graph (`list_items`, `create_list_item`) | **FAIT** — **déployé, sécurisé, prouvé** (chapeau `T-0002b` promue le 10 juin 2026) : lecture Missions et écriture Zone-de-proposition vérifiées de bout en bout ; défense en profondeur (validation du claim `roles`) = `T-0009` (différé, phase 2) | `outils/mcp-graph/` + `T-0002b` / `T-0009` |
| Agent métier « kick-off » | **À FAIRE** — **conçu, non construit** | `backlog/plan.md` §6 (T-1.2) |

---

*Document de référence vivant. Il décrit ; il ne gouverne pas. La vérité des règles vit dans le canon (`doctrine/`, `contrats/socle/`), celle de l'état réel vit dans les sources indiquées ci-dessus. Mettre à jour la Partie C au fil des déploiements.*
