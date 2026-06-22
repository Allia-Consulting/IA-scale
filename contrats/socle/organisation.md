# Organisation & délégations — Allia Consulting

> **Version** : 1.7 — *promu*. Troisième contrat socle, aux côtés de `/doctrine/doctrine.md` et `/backlog/plan.md`.
> **Statut** : Contrat socle — fait foi.
> **Domicile** : Dépôt de fondations (Git), `/contrats/socle/organisation.md`.
> **Autorité de promotion** : Gardien du temple.
> **Portée** : Toute l'organisation Allia.
> **Changelog** : v1.7 — promu via boucle de promotion, 22 juin 2026. **Deux périmètres nommés dans la table des titulaires (§3), tous deux NON DÉLÉGUÉS** (tenus par le gardien, possiblement délégables) : « Talent & RH » (recrutement, formation, évaluation annuelle, politique RH — déjà capacité de la carte §2) et « Onboarding & intégration » (capacité chapeau orchestrant matériel/droits/connaissance, §2). Aucune délégation, aucun nom inventé (règle §3 respectée), aucun droit ni groupe Entra touché. Réagencement d'arborescence hors socle : contrats/local/recrutement/ → contrats/local/talent-rh/ (le périmètre RH héberge le gabarit d'offre). Aucune autre section modifiée. v1.6 — promu via boucle de promotion, 19 juin 2026. **Nouveau périmètre socle-animé (§2, §3)** : « Expérience utilisateur / Tour de contrôle » rattaché à la capacité « adoption multi-utilisateurs (RBAC) » ; premier cas formalisé de contrat socle ANIMÉ (consommé par toute la firme, animé par un animateur désigné, promu par le gardien — modèle du design system, doctrine §5). Politique figée dans contrats/socle/tour-de-controle.md (promu v1.0) ; construction = T-0014. Ligne « à déléguer » ajoutée à la table des titulaires (aucun nom futur inventé). Aucune autre section modifiée. v1.5 — promu via boucle de promotion, 15 juin 2026. **Groupes socle (§5)** : introduction de la distinction *groupes de périmètre* (projection d'une délégation) vs *groupes socle* (projection du statut de collaborateur) ; canonisation de `grp-collaborateurs-m365` (licence M365 = ressource socle gouvernée par groupe) et de l'**accès SharePoint comme socle collaborateur non cloisonné** (adossé doctrine §9) ; renvois à `grp-parc-collaborateur` (`parc-collaborateur.md` §6) et `grp-mcp-graph-users` (`identites-et-secrets.md` §2), chaque groupe socle gouvernant une seule nature de ressource (moindre privilège). Phrase de clôture du §5 actualisée (première délégation et premiers groupes socle réels — modèle partiellement actif). Aucune autre section modifiée. v1.4 — promu via boucle de promotion, 15 juin 2026. PREMIÈRE DÉLÉGATION RÉELLE (§3) : Sarah Shaiek passe de candidate à collaboratrice et devient animatrice du périmètre « Communication & marque ». La table des titulaires passe d'un état gardien-unique à un état à deux. §10 (hypothèse 3) aligné en conséquence. Aucune autre section modifiée. v1.3 — promu via boucle de promotion, 12 juin 2026. **D3 REQUALIFIÉE (décision du gardien, 12 juin 2026)** : la grille d'habilitation du §4 bis (grades habilités + délégation, **contenu inchangé**) ne conditionne **plus l'envoi humain** d'un livrable — tout collaborateur envoie **librement** son livrable à son client, responsable de son acte (les crans gouvernent les agents, pas les humains — doctrine §6). La grille définit désormais **qui tient la porte du cran *validé*** pour (i) les **actions d'AGENT engageant la firme vis-à-vis d'un client** (envoi de livrable par un agent) et (ii) la **communication grand public**. Aligne doctrine v1.6, anonymisation.md v1.4, table-des-crans.yaml v1.5. v1.2 — promu via boucle de promotion, 8 juin 2026 (session doctrine). **D4 (carte des capacités, §2)** : ajout de deux capacités au domicile canonique de la carte (la grille des périmètres) — **« onboarding & intégration »** (capacité chapeau orchestrant les trois réconciliations d'une décision « X devient collaborateur du périmètre P » : matériel, droits, connaissance) sous *Capacités habilitantes*, et **« parc & gestion de poste »** (profil de poste, apps déployées, posture sécurité, groupes Entra d'enrôlement ; politique canonisée, exécution = runbook) sous *Socle d'exploitation & gouvernance*. v1.1 — promu via boucle de promotion, 7 juin 2026. **D1 (cohérence, §7)** : la règle d'anonymisation gouverne la **sortie externe**, non la réutilisation inter-client interne (aligne `anonymisation.md` v1.3). **D2 (décision d'organisation nouvelle, §3 bis)** : introduction du rôle **associé** comme rôle métier distinct du gardien, les deux tenus par le fondateur. **D3 (décision d'organisation nouvelle, §4 bis)** : grille d'habilitation des portes de sortie de firme (grade habilité + délégation, cumulatifs). v1.0 — candidat (état initial).

La doctrine définit *les règles et les rôles* (en abstrait). Le plan définit *le chantier*. Ce document définit **qui répond de quoi** : il lie les rôles abstraits de la doctrine à des périmètres concrets et à leurs titulaires, et il gouverne la délégation. C'est la « réalisation » de la gouvernance, rendue canonique et gouvernable — ce que la doctrine laisse délibérément de côté pour rester stable (principe « capacités stables, réalisation volatile »).

---

## 0. Objet et frontière

Ce document **dit** : la carte des périmètres, qui tient quel rôle sur quel périmètre, et ce qu'une délégation accorde.

Ce document **ne dit pas** : la définition des rôles (→ doctrine §3), ni les dossiers RH des personnes (→ M365). Il référence, il ne duplique pas.

## 1. Trois vérités distinctes : identité, décision, droits

Chacune vit à un seul endroit ; aucune n'est copiée.

- **L'identité** (qui est la personne : compte, profil, grade) → M365 / Entra. *Source.*
- **La décision de délégation** (qui anime quel périmètre) → ce contrat, dans le dépôt (« le guide »). *Source.*
- **Les droits d'accès** (ce à quoi la personne accède) → *dérivés* de la décision, réconciliés dans M365, jamais saisis à la main (voir §5).

Ce contrat nomme « le titulaire du rôle R sur le périmètre P » par un identifiant Entra ; il ne duplique aucun dossier RH.

## 2. La carte des périmètres (dérivée de la carte des capacités)

Un périmètre est une capacité, ou un groupe cohérent de capacités, dont un animateur peut répondre. Grille de départ, alignée sur la carte des capacités :

- **Pilotage** — stratégie & offre · performance & gouvernance.
- **Cœur de métier** — développement commercial · delivery · relation client · connaissance, contenu & IP (dont **communication & marque**).
- **Capacités habilitantes** — talent & RH · **onboarding & intégration** · gestion financière · ressources & capacité · corporate & conformité.
- **Socle d'exploitation & gouvernance** — orchestration des agents · référentiel & cycle de vie des agents · **parc & gestion de poste** · évaluation & observabilité · adoption multi-utilisateurs (RBAC).

> **Deux capacités ajoutées (v1.2, session doctrine du 8 juin 2026).**
> - **Onboarding & intégration** (*Capacités habilitantes*) — capacité **chapeau** qui orchestre, pour une même décision promue « X devient collaborateur du périmètre P », les **trois réconciliations** d'une même vérité : **matériel** (parc — ABM/Intune), **droits** (Entra/SSO, via le réconciliateur de `§5`), **connaissance** (Claude/Git — accès au canon et à la mémoire d'organisation). Déclencheur : le passage **candidat → collaborateur** (création de l'identité Entra). La liste de recrutement reste un **processus humain**, volontairement non couplé (cf. `backlog/chantiers/`).
> - **Parc & gestion de poste** (*Socle d'exploitation & gouvernance*) — la **politique** de poste (profil par fonction, applications déployées, posture de sécurité, groupes Entra d'enrôlement) est **canonisée** ici et dans `contrats/socle/parc-collaborateur.md` (candidat) ; la **configuration effective** Intune/ABM est un **runbook humain**, et la réconciliation automatique politique→Intune est un chantier de Phase 3/4 (backlog). Voir l'extension de la chaîne d'autorité aux **appareils** (doctrine §8, candidat v1.4).

Le gardien décide de la granularité : on délègue rarement une capacité isolée, plus souvent un domaine cohérent.

## 3. Les titulaires aujourd'hui (état réel)

Par défaut, **le gardien (fondateur) tient le rôle de gardien et anime tous les périmètres non délégués**. Une première délégation est désormais active : la **communication & marque** est déléguée à Sarah Shaiek. La firme passe ainsi d'un état gardien-unique à un état à deux.

| Périmètre | Animateur (titulaire) | Statut |
|---|---|---|
| Tous les périmètres non délégués | Le gardien (fondateur) | non délégué |
| Communication & marque | Sarah Shaiek (sarah.shaiek@allia-consulting.com) | délégué — 15 juin 2026 |
| Talent & RH (recrutement, formation, évaluation, politique RH) | Le gardien (fondateur) | non délégué — possiblement délégable |
| Onboarding & intégration (orchestration matériel · droits · connaissance) | Le gardien (fondateur) | non délégué — possiblement délégable |
| Expérience utilisateur / Tour de contrôle | — | à déléguer (socle animé — tour-de-controle.md) |
| … | — | à déléguer |

*Aucun nom de collaborateur **futur** n'est inventé : la règle « on n'invente pas de délégations à venir » demeure. L'état réel comporte désormais une délégation nommée (communication & marque → Sarah Shaiek) ; les lignes futures restent en attente jusqu'à une délégation réelle.*

## 3 bis. Gardien et associé : deux rôles, une même personne aujourd'hui

*Décision d'organisation (nouvelle).* Au-delà des quatre rôles de la doctrine, la firme reconnaît le rôle **associé** comme rôle **métier** — celui qui pratique le conseil et peut être responsable d'une mission — **distinct** du rôle de **gardien**, qui gouverne les règles (skills, doctrine, design, délégations, infrastructure).

Aujourd'hui, le **fondateur porte les deux rôles simultanément** : gardien *et* associé. Ils ne se confondent pas, parce qu'ils n'opèrent pas sur le même plan (doctrine §4) :

- **comme gardien**, il promeut des règles (plan doctrine) — jamais dans une affaire ;
- **comme associé**, il pratique le métier (plan d'exécution) et peut **tenir une porte de sortie de firme** (livrable client, publication) au titre de cette responsabilité métier.

La distinction porte sur le **rôle au titre duquel on agit**, pas sur la personne. C'est ce qui rend légitime qu'il valide lui-même une sortie client : il agit alors **comme associé**, jamais en tant que gardien (doctrine §6, règle d'or §4).

## 4. Ce qu'une délégation accorde — et n'accorde pas

Déléguer l'animation d'un périmètre P à une personne Y :

- **accorde** : proposer des candidats sur les **contrats locaux** de P (procédure allégée, doctrine §5 et §7) ; faire évoluer le périmètre ;
- **n'accorde pas** : promouvoir (le gardien promeut) ; toucher au socle ; animer hors de P.

Une délégation est elle-même un **acte de promotion** sur ce contrat (gardien seul). La **révocation** est un repointage — une seule action, comme tout retour arrière.

À l'échelle 50-200 (fédération de la promotion, doctrine §10), le gardien pourra déléguer en plus le **droit de promotion local** par domaine ; c'est ici qu'il sera enregistré, le gardien conservant le socle.

## 4 bis. Habilitation des portes de sortie de firme

*Décision d'organisation — **requalifiée le 12 juin 2026** (décision du gardien).* **Les crans gouvernent les agents, pas les humains** (doctrine §6). Un **collaborateur envoie librement son livrable à son client** : aucune validation tierce, aucun grade requis, aucune délégation requise — il est lui-même **responsable de son acte**. La grille ci-dessous **ne conditionne plus l'envoi humain** d'un livrable.

**Ce que la grille définit désormais : QUI TIENT LA PORTE du cran *validé*** pour :

1. les **actions d'AGENT engageant la firme vis-à-vis d'un client** — l'envoi d'un livrable par un agent : la porte humaine est une **supervision de la machine**, pas un contrôle de la personne ;
2. la **communication grand public** (site, publication, institutionnel) — qui reste au régime cran *validé* + porte d'anonymisation (`anonymisation.md` §1).

C'est **ici** que cette habilitation se **concrétise** — cohérent avec « capacités stables, réalisation volatile » : les grades relèvent de la réalisation et vivent hors de la doctrine.

**Tenir une de ces portes exige deux conditions CUMULATIVES** (contenu de la grille inchangé) :

1. un **grade habilité** — **manager, senior manager, directeur, ou associé** ;
2. la **responsabilité déléguée** sur la mission ou le périmètre concerné.

**Grades NON habilités** : consultant junior, consultant, consultant senior.

**Le grade est nécessaire mais non suffisant.** Pour ces deux cas, un grade habilité ne peut tenir la porte que des **missions ou périmètres dont il a la responsabilité déléguée** : le grade est un **plancher de capacité** ; la **délégation** rattache à l'affaire. Aucun des deux ne suffit seul.

**Où vit cette grille.** La doctrine définit la règle abstraite (« rôle métier habilité ») ; **`organisation.md` porte la grille concrète**. Un changement de grille de grades se fait **ici**, **jamais** dans la doctrine.

## 5. Droits d'accès — décision dans le guide, droits réconciliés dans M365

Les droits ne se saisissent pas à la main : ils sont le **dérivé** d'une décision de délégation promue. La décision est la *source* (ce contrat, dans le dépôt — « le guide ») ; les droits M365 en sont la *projection*, réconciliée, jamais éditée directement. C'est « le dérivé n'est jamais le saisi » appliqué aux accès.

**Chaîne d'autorité — le guide → Claude → M365 :**

1. **Identité (SSO)** — une seule identité par personne, fournie par Entra, pour accéder au guide (GitHub), à Claude et à M365. Pas de second annuaire.
2. **Décision (le guide, Git)** — ce contrat nomme, par périmètre, le titulaire par son identifiant Entra. La décision n'entre en vigueur que **promue** par le gardien (porte humaine, cran *validé* — modifier des droits est à large rayon d'impact et sensible).
3. **Réconciliation (Claude)** — un réconciliateur, au **moindre privilège**, lit le canon et fait correspondre l'appartenance au **groupe Entra du périmètre** (ex. `anim-communication`), en idempotent (il n'applique que le delta). Les ressources SharePoint / Teams sont liées au groupe, jamais aux individus.
4. **Application (M365)** — l'appartenance au groupe ouvre l'accès. Attribuer = ajouter au groupe ; révoquer = retirer. Le « retour arrière en une action » s'étend ainsi aux accès.

**Inscrit en dur (non négociable, dès qu'il y a délégation) :**

- la porte humaine reste à la **promotion** du contrat — c'est la décision du gardien qui autorise ;
- le réconciliateur est au **moindre privilège** : une app registration qui ne sait gérer *que* ces groupes, rien d'autre ; tout changement tracé ;
- le **déploiement et la mise en production restent sous le contrôle du gardien** : il modifie le guide (le canon), et Claude puis M365 suivent en conséquence. Aucun droit ne change hors de cette chaîne.

**Runbook humain (ni Claude ni agent) :** créer l'app registration, donner le consentement admin, stocker le secret. Ni Claude ni un agent ne configurent de permissions ni ne saisissent de secret (plan §2).

**Ressources socle gouvernées par groupe.** La réconciliation ci-dessus vaut pour les **groupes de périmètre** — projection d'une **délégation** (ex. `anim-communication`, lié à l'animation d'un périmètre). À côté d'eux existent des **groupes socle** : ils ne projettent aucune délégation ni périmètre, mais le simple **statut de collaborateur**. Tout collaborateur y appartient du seul fait d'être collaborateur ; la ressource gouvernée s'ouvre par cette appartenance, jamais par une attribution individuelle.

Chaque groupe socle gouverne **une seule nature de ressource** — au moindre privilège, jamais un groupe fourre-tout :

- **`grp-collaborateurs-m365`** — la **licence M365 Business Premium**. La licence est une ressource socle, attribuée *par groupe* (Assigned), non personne par personne : appartenir au groupe ouvre la licence.
- **`grp-parc-collaborateur`** — l'**enrôlement du poste** (profil, apps, posture, conformité). Canonisé dans `parc-collaborateur.md` §6 ; nommé ici pour mémoire, sa politique fait foi là-bas.
- **`grp-mcp-graph-users`** — l'**accès au service MCP Graph**. Décrit dans `identites-et-secrets.md` §2 (cas « humain ») ; nommé ici pour mémoire. *Note : il n'est pas socle pour tout collaborateur aujourd'hui — il gouverne l'accès d'un service, pas un droit universel ; il figure dans cette liste comme groupe gouvernant une nature de ressource, au même titre que les autres, et non comme acquis d'office.*

**Accès SharePoint — socle, non cloisonné.** Tous les collaborateurs accèdent au **site unique AlliaConsuling**, sans cloisonnement par périmètre : le périmètre d'animation **n'isole pas les données**. C'est cohérent avec la doctrine §9 (les données vivent dans M365, sans isolation par mission) et avec « l'avantage qui compose » (l'apprentissage inter-missions suppose une matière partagée). L'accès socle au site relève de l'appartenance au socle collaborateur, non d'une délégation.

La première délégation réelle (communication & marque → Sarah Shaiek, §3) et les premiers **groupes socle** (licence, parc) existent désormais : le modèle n'est plus seulement *conçu*, il est **partiellement actif**. Les attributions ont été posées par **runbook humain** (onboarding) ; la **réconciliation automatique** au moindre privilège reste à construire (réconciliateur de droits, plan §9 T-4.3 ; réconciliateur de parc, `T-0008`). La porte humaine demeure à la **promotion** du contrat.

## 6. Cycle de vie d'une délégation — exemple « Communication & marque »

1. **Candidat** : préparer (via Claude) une modification de ce contrat affectant Communication à Y.
2. **Conformité** : l'agent-gardien vérifie que rien ne casse et calcule le rayon d'impact.
3. **Promotion** : le gardien approuve ; Y devient animateur de Communication.
4. **Effet** : Y peut proposer sur `/contrats/local/communication/*` (piliers éditoriaux, voix de marque, templates) ; il ne promeut pas.
5. **Réconciliation** : les droits se projettent sur le groupe Entra du périmètre (réconciliateur au moindre privilège — ou à la main lors des toutes premières délégations).
6. **Communication (option)** : annonce à l'équipe (cran *notifié*).
7. **Révocation** : repointer en une action.

## 7. Confidentialité

Ce contrat est interne à la firme et référence les personnes par identifiant ; aucun dossier RH n'y est dupliqué. Les identités et leurs détails restent dans M365, sous contrôle d'accès. La règle d'anonymisation (contrat socle dédié) gouverne la **sortie externe de la firme** (publication, livrable rendu hors firme), non la réutilisation inter-client interne ; elle ne s'applique pas ici, qui relève de la donnée d'organisation interne — mais l'accès y est restreint au strict nécessaire.

## 8. Articulation avec les grades

Un **animateur** est typiquement un Manager ou un Associé qui pilote un savoir-faire ; tout collaborateur est **utilisateur** ; le **gardien** est au niveau firme. Le grade est un détail RH (M365 / documents talents) ; ce contrat enregistre la tenue d'un rôle sur un périmètre, pas le grade.

## 9. Comment ce document évolue

Contrat socle : chaque délégation, révocation ou redécoupage de périmètre est un candidat promu par le gardien (doctrine §7). Il se gouverne comme il prêche.

## 10. Hypothèses prises (à corriger par le gardien)

1. Les périmètres dérivent de la carte des capacités ; la granularité est au choix du gardien.
2. Identités / RH dans M365 (référencées par identifiant), délégations dans Git. Séparation recommandée dès maintenant.
3. Aujourd'hui : le gardien tient les périmètres **non délégués** ; une première délégation est active (communication & marque → Sarah Shaiek) ; aucun nom **futur** inventé.
4. Les droits sont un dérivé réconcilié de la décision promue (groupes Entra), jamais saisis ; la porte humaine reste à la promotion, le réconciliateur au moindre privilège. La mise en place du privilège (app registration, secret) reste un runbook humain.

> Pour corriger : ouvre un candidat, ne modifie pas ce fichier directement.
