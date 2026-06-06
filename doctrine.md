# Doctrine de gouvernance de l'entreprise augmentée — Allia Consulting

> **Version** : 1.1 — *candidat*. Enrichie en lien avec la présentation « Talents & recrutement » (ajout du §10 bis). À promouvoir par le gardien du temple via la boucle de promotion (§7).
> **Statut** : Contrat socle — fait foi.
> **Domicile** : Dépôt de fondations (Git), chemin `/doctrine/doctrine.md`. **Ce fichier markdown est la version canonique.** Le PDF qui a circulé en est un *aperçu rendu* — un consommateur, jamais un double éditable.
> **Autorité de promotion** : Gardien du temple.
> **Portée** : Toute l'organisation Allia.
> **Adossé à** : `/backlog/plan.md` (plan de construction du SI augmenté). La doctrine dit *le pourquoi et les règles* ; le plan dit *le comment et le chantier*. Les deux forment le canon que Claude Code résout à l'exécution.

Ce document est lui-même un contrat socle. Il ne se modifie pas dans une copie : toute évolution suit la boucle de promotion décrite en §7. Le fichier présent est la seule source de vérité ; tout endroit qui l'affiche (un Projet Claude, un wiki, une présentation, un PDF) en est un consommateur, jamais un double éditable.

---

## 0. Comment lire ce document

Ce texte explique comment Allia décide, change et reste cohérente à mesure qu'elle grandit. Il est écrit pour être compris par quelqu'un qui découvre Allia : un nouveau collaborateur, un partenaire, un futur animateur d'un périmètre.

- La section 1 et le début de chaque partie disent **le pourquoi** (en prose).
- Les sections 3 à 9 sont **opérantes** : rôles, crans, boucle de promotion, contrats. Elles sont structurées pour être lues par un humain aujourd'hui et exploitées par un agent demain.
- La section 11 est un **glossaire** ; en cas de doute sur un mot, commencez par là.

## 1. Pourquoi cette doctrine existe

Allia est un cabinet de conseil nativement augmenté par l'IA. L'ambition n'est pas que quelques personnes soient plus productives, mais que l'organisation entière le soit — et qu'elle puisse passer de 1 à 200 collaborateurs sans se réécrire.

Cela n'est possible qu'à une condition : que les choses qui changent souvent (les outils, les agents, les offres, le style) reposent sur des choses qui ne changent presque jamais (les capacités de la firme et ses règles). La gouvernance est le mécanisme qui tient cette promesse. Elle répond à trois questions :

1. **Qui a le droit de changer quoi ?** — pour qu'une amélioration locale profite à tous sans que personne ne casse l'ensemble.
2. **Comment un changement se propage-t-il ?** — pour qu'une modification faite à un endroit se répercute partout, de façon traçable et réversible.
3. **Que peut faire un agent sans demander ?** — pour que la firme soit rapide là où c'est sûr, et prudente là où ça ne l'est pas.

Sans cette doctrine, l'augmentation par l'IA produit des outils brillants mais divergents, impossibles à gouverner à l'échelle. Avec elle, l'organisation devient un système cohérent qui compose de la valeur à chaque niveau.

## 2. Les principes fondateurs

Ces principes ne sont pas négociables. Tout le reste en découle.

- **Capacités stables, réalisation volatile.** Une capacité est ce que la firme doit savoir faire (piloter la marge, produire un livrable, gérer la connaissance). Un agent ou un outil est *comment* on le fait. Les capacités forment le squelette ; les agents s'y accrochent et peuvent changer sans déformer le squelette.
- **Une seule vérité, un seul domicile.** Chaque information n'existe qu'à un seul endroit faisant foi. Les **données** (missions, temps, imputations, livrables) vivent dans M365. Les **règles** (doctrine, contrats, templates, design system, table des crans) vivent dans le dépôt de fondations. Jamais deux copies de la même vérité.
- **Pull, jamais push.** Un consommateur ne reçoit pas une copie d'une règle : il référence la version canonique et la résout au moment où il en a besoin. Conséquence directe : promouvoir une nouvelle version, c'est déplacer un pointeur ; revenir en arrière, c'est le repointer. La propagation est instantanée et toujours réversible.
- **Tout passe par des contrats.** Chaque capacité expose un contrat : ce qu'elle publie, ce qu'elle consomme. Les changements se propagent par ces contrats, pas par des modifications faites à la main dans chaque outil.
- **Le dérivé n'est jamais le saisi.** Un fait calculé par un agent (une marge, une imputation) est écrit dans une zone de proposition. Sa promotion en vérité est une étape tracée. La source unique ne se corrompt jamais en silence. **Il en va de même des droits d'accès** : ils sont un dérivé d'une décision de délégation promue dans le dépôt, réconciliés dans M365, jamais saisis à la main.
- **L'autonomie est graduée, par type d'action.** « Les agents agissent » n'est pas une politique globale. Chaque type d'action porte un cran d'autonomie (§6).

## 3. Les quatre rôles

Quatre rôles, et eux seuls, interviennent dans le système. Ils se répartissent sur deux plans (§4).

**Gardien du temple.** Assure la cohérence de l'ensemble. C'est un Janus à deux têtes : une **tête humaine**, qui autorise la mise en service d'une nouvelle version d'un bout du SI ; une **tête agent**, qui vérifie en continu que le comportement des agents respecte les contrats, calcule l'impact d'un changement et filtre en amont ce qui ne mérite pas l'attention de l'humain. Le gardien gouverne les règles, pas les affaires : il n'intervient jamais dans le déroulé d'une mission.

**Animateur de périmètre.** Le *product manager* de son sujet (ex. : communication et marque). Il peut se voir déléguer la responsabilité d'un périmètre pour le faire évoluer. Il propose une nouvelle version (un candidat) ; il ne peut pas la mettre en production seul. C'est le gardien qui autorise.

**Agent.** Exécute les tâches selon les règles établies, sous le contrôle de la tête-agent du gardien. Il agit dans la limite du cran de chaque action (§6) et écrit les faits dérivés en zone de proposition.

**Utilisateur.** Un collaborateur d'Allia qui se sert du système au quotidien (saisir ses temps, chercher un template, dialoguer avec son assistant). C'est le rôle le plus nombreux ; l'adoption du système se gagne auprès de lui.

| Rôle | Plan | Peut | Ne peut pas |
|---|---|---|---|
| Gardien (humain) | Doctrine | Promouvoir une version, déléguer | Éditer à la place d'un animateur |
| Gardien (agent) | Doctrine + Exécution | Contrôler la conformité, calculer l'impact, rejeter, auto-approuver le faible risque | Promouvoir un changement à risque sans l'humain |
| Animateur | Doctrine | Proposer un candidat sur son périmètre | Mettre en production |
| Agent | Exécution | Agir selon le cran, proposer du dérivé | Écrire du dérivé comme du saisi ; agir au-delà de son cran |
| Utilisateur | Exécution | Utiliser le système, déclencher des actions | Modifier une règle |

## 4. Les deux plans

Le système se lit sur deux plans qu'il ne faut jamais confondre.

- **Plan doctrine** — on y édite et promeut les règles. Y opèrent l'animateur (propose) et le gardien (promeut).
- **Plan d'exécution** — on y fait tourner les missions et le quotidien. Y opèrent l'agent (exécute) et l'utilisateur (se sert).

**Règle d'or** : le gardien n'est jamais dans la boucle d'exécution d'une affaire. Il fixe les règles que l'exécution applique. C'est ce qui rend l'échelle tenable : on ne sollicite pas le gardien à chaque mission, seulement quand une règle change.

## 5. Les contrats : socle et local

Un contrat est la frontière d'une capacité : ce qu'elle publie (et que d'autres consomment) et ce qu'elle consomme. On distingue deux natures, parce qu'elles n'ont pas le même propriétaire.

**Contrat socle.** Partagé par toute la firme. Il appartient au tout, donc au gardien. Les animateurs peuvent proposer dessus, mais l'autorité de promotion reste au gardien. Exemples : le design system, le modèle de données, la règle d'anonymisation, la table des crans, le registre d'organisation et des délégations (`/contrats/socle/organisation.md`), et les quatre rôles eux-mêmes (ce document).

**Contrat local.** Propre à un seul périmètre. Édité par l'animateur de ce périmètre ; promu par le gardien, mais selon une procédure allégée. Exemples : les piliers éditoriaux, la voix de marque fine, les templates propres à une practice.

| | Contrat socle | Contrat local |
|---|---|---|
| Propriété | Le tout (gardien) | L'animateur du périmètre |
| Qui propose | Tout animateur concerné | L'animateur du périmètre |
| Qui promeut | Gardien | Gardien (procédure allégée) |
| Exemples | Design system, modèle de données, crans, rôles | Piliers éditoriaux, templates d'une practice |

**Pourquoi cette distinction.** Un animateur ne doit jamais faire bouger ce qui n'est pas le sien. Le design system est animé par la communication, mais consommé par toute la firme, y compris la gestion : il est donc socle, pas local. La frontière des périmètres s'arrête là où commence un contrat partagé.

## 6. Les crans d'autonomie

Chaque type d'action porte un cran. Le cran se déduit de trois questions :

> cran = f( l'action est-elle réversible ? · sort-elle de la firme ? · quel est son rayon d'impact ? )

| Cran | Conditions | Qui décide | Exemple |
|---|---|---|---|
| **auto** | réversible **et** interne **et** impact local | L'agent, seul | Créer l'espace SharePoint d'une mission |
| **notifié** | réversible et interne, mais engage l'image ou est largement visible | L'agent agit ; le gardien est informé | Envoyer le message de nomination à l'équipe |
| **validé** | irréversible **ou** sort de la firme **ou** rayon d'impact large | Porte humaine (gardien ou rôle désigné) avant l'action | Promouvoir un contrat socle ; envoyer un livrable au client |
| **anonymisation** (porte automatique) | réutilisation de matière inter-client | Déclenchée par règle, sans humain | Générer un template à partir du livrable d'un autre client |

Deux compléments indissociables :

- **Le rayon d'impact compte autant que la réversibilité.** Une action peut être interne et lourde de conséquences (modifier le design system touche toute l'organisation). Les changements à large impact passent par le cran *validé*, même internes. On les rend réversibles (pull + versionnement) pour garder une porte proportionnée plutôt que de tout verrouiller.
- **L'anonymisation est une règle exécutable, pas une intention.** « Anonymiser quand nécessaire » doit préciser quels champs, quel seuil et quel déclencheur. C'est une exigence de conformité (RGPD, AI Act), pas une bonne pratique.

## 7. La boucle de promotion

Comment une nouvelle version d'un bout du SI entre en service. C'est le cœur opérant de la doctrine.

1. **Proposition.** L'animateur prépare un candidat via une interface Claude — jamais en éditant le dépôt directement. L'agent dépose le candidat dans une zone temporaire et en génère un aperçu produit à partir de l'artefact candidat exact, rattaché à une version précise (empreinte).
2. **Contrôle de conformité (agent gardien).** Il vérifie que le candidat respecte les contrats de tous ses consommateurs ; calcule le rayon d'impact (qui consomme, combien d'artefacts, quelles missions en cours sont concernées) ; rejette d'office ce qui casse un contrat ; et produit un avis d'impact et de risque.
3. **Décision (gardien humain).** Il dialogue avec l'agent gardien, examine l'aperçu et l'avis, puis approuve la version précise. L'approbation est attachée à l'empreinte de l'artefact, jamais au résumé qui le présente.
4. **Promotion.** L'agent gardien déplace le pointeur canonique dans le dépôt (commit approuvé, journalisé). C'est la seule écriture autorisée dans le dépôt.
5. **Propagation (pull).** Les consommateurs référencent la version canonique et la résolvent à l'exécution. *Versions à portée* : les nouveaux usages prennent la nouvelle version ; les missions en cours restent sur leur version sauf migration explicite — un livrable client ne change pas d'apparence en plein milieu.
6. **Vérification.** L'agent gardien s'assure que les consommateurs résolvent bien la nouvelle version. (« Prendre en compte » ne signifie jamais distribuer une copie à chaque agent.)
7. **Communication (optionnelle).** L'agent gardien demande au gardien humain si une communication est nécessaire. Le cas échéant, ordre est donné à l'agent Communication de publier l'annonce (mail, Teams).
8. **Retour arrière.** Repointer vers la version précédente — en une seule action. Toujours possible, parce qu'on n'a jamais copié.

## 8. Le substrat — où vivent les choses

| Nature | Domicile | Exemples |
|---|---|---|
| Données (les faits) | M365 | Missions, temps, imputations, livrables, frais |
| Règles (les versions du SI) | Dépôt de fondations (Git) | Doctrine, contrats, design system, templates, crans |
| Journal d'approbation | Dépôt (Git) | Historique des promotions, qui a approuvé quoi, quand |

**Préalable technique à ne pas oublier.** La promesse « toute l'organisation s'adapte » suppose une couche de résolution qui fait que les agents et les surfaces (Projets Claude, outils) résolvent la doctrine depuis le dépôt à l'exécution. Tant qu'elle n'existe pas, les surfaces sont rafraîchies à la main depuis le dépôt, avec une règle ferme : on n'édite jamais la doctrine dans une surface, seulement dans le dépôt. Construire cette couche est un chantier en soi, préalable à l'automatisation complète de la propagation.

**La chaîne d'autorité va du guide vers M365, jamais l'inverse.** Le dépôt (« le guide ») porte les décisions ; Claude les résout et les exécute ; M365 applique (données comme droits). Modifier une décision — y compris une délégation et les droits qui en découlent — c'est modifier le guide, sous la porte de promotion du gardien (cran *validé*) ; M365 suit alors en conséquence. Le déploiement et la mise en production restent ainsi sous le contrôle du gardien, et aucun droit ni aucune règle ne se modifie hors de cette chaîne.

## 9. Confidentialité, conformité et qualité

- **Confidentialité.** Les données restent dans M365, sans isolation par mission. La protection passe par l'anonymisation déclenchée à la réutilisation inter-client (§6), exécutable et tracée.
- **Apprentissage inter-missions.** L'intelligence se compose entre missions (le véritable avantage qui compose), au prix d'une discipline d'anonymisation conforme RGPD, AI Act et NDA.
- **Qualité — non optionnelle.** Comme les agents agissent en autonomie, lisent à travers les missions et apprennent entre elles, la seule barrière restante est l'évaluation et les garde-fous. L'autonomie augmente l'exigence d'évaluation et d'observabilité ; elle ne la réduit pas. Le gardien-agent filtre le faible risque contre politique ; le reste remonte à l'humain.

## 10. Évolutions connues (nommées, non encore construites)

Pour que le lecteur sache ce qui est délibérément reporté :

- **Fédération de la promotion.** À 50-200 collaborateurs, un promoteur humain unique sature. On déléguera le droit de promotion par domaine, et l'agent gardien auto-approuvera le faible risque contre politique. Le gardien conserve le socle, délègue le reste.
- **Couche de résolution automatique** (§8) : à construire pour que la propagation soit instantanée sans intervention manuelle.
- **Plan de l'utilisateur quotidien.** Cette doctrine modélise en profondeur la gouvernance. Le quotidien du rôle Utilisateur — le cockpit du collaborateur — reste à concevoir. C'est le prochain chantier, et le vrai test de l'adoption.

## 10 bis. Articulation avec les grades et la trajectoire de la firme

*Section ajoutée en lien avec la présentation « Talents & recrutement ». Elle articule la doctrine à la réalité RH sans y importer le détail RH, qui est volatil (réalisation) et vit dans les documents talents, pas ici (principe « capacités stables, réalisation volatile »).*

- **Les quatre rôles sont orthogonaux aux grades.** Un grade (Consultant → Manager → Associé) dit l'expérience et la responsabilité dans la firme ; un rôle (utilisateur, animateur, agent, gardien) dit la place dans le système. Tout collaborateur entre comme **utilisateur**, quel que soit son grade. Avec la séniorité et la délégation, il peut devenir **animateur** d'un périmètre — typiquement un Manager ou un Associé qui « pilote la croissance d'un savoir-faire ». Le rôle de **gardien** est tenu au niveau firme (aujourd'hui : le fondateur).
- **La trajectoire de la firme cadence la fédération de la promotion** (§10) :
  - *Fondation* (cap 50) — gardien unique ; passage de l'amorçage manuel au niveau agentique.
  - *Ouverture* (cap 100) — début de la fédération : premiers animateurs délégués, promotion locale en procédure allégée.
  - *Acquisition* (cap 200) — délégation large ; le gardien conserve le socle, l'agent-gardien auto-approuve le faible risque contre politique.
- **La culture du collectif est le pendant humain de « on référence, on ne copie pas ».** « Pas de mon périmètre », le cross-selling qui compte pour tous, l'intelligence collective : ce sont les valeurs dont le canon partagé est la forme technique. Une amélioration promue profite à tous, exactement parce que personne n'en garde un double.

## 11. Glossaire

- **Capacité** — ce que la firme doit savoir faire, indépendamment de l'outil. Stable.
- **Skill / outil** — un moyen réutilisable de réaliser une partie d'une capacité.
- **Agent** — une composition de skills qui exécute des tâches selon les règles.
- **Contrat** — la frontière d'une capacité : ce qu'elle publie et consomme.
- **Contrat socle** — contrat partagé par toute la firme ; propriété du gardien.
- **Contrat local** — contrat propre à un périmètre ; propriété de son animateur.
- **Gardien du temple** — rôle garant de la cohérence ; Janus humain (promotion) + agent (conformité).
- **Animateur** — responsable d'un périmètre ; propose des versions, ne promeut pas.
- **Utilisateur** — collaborateur qui se sert du système au quotidien.
- **Cran** — niveau d'autonomie d'un type d'action : auto, notifié, validé (+ porte d'anonymisation).
- **Rayon d'impact** — l'ensemble des consommateurs et artefacts qu'un changement affecte.
- **Candidat** — une version proposée, pas encore promue.
- **Promotion** — la mise en service d'une version, par déplacement du pointeur canonique.
- **Pull** — un consommateur référence la version canonique et la résout à l'exécution (par opposition à *push*, qui distribuerait des copies).
- **Zone de proposition** — l'espace où un agent écrit un fait dérivé avant sa promotion tracée en vérité.
- **Plan doctrine / plan d'exécution** — où l'on édite les règles / où l'on fait tourner les missions.
- **Substrat** — M365 pour les données, le dépôt Git pour les règles.

---

*Fin de la doctrine de gouvernance v1.1 (candidat). Ce document est un contrat socle : il évolue par la boucle de promotion (§7), sous l'autorité du gardien du temple.*
