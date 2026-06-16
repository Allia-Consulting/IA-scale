# Newsletter hebdomadaire — communication interne — Allia Consulting

> **Version** : 1.0 — *candidat*. **Statut** : contrat **local** (périmètre Communication & marque) — fait foi sur son périmètre.
> **Changelog** :
> - v1.0 — candidat, 16 juin 2026 : création du premier contrat local du dépôt. Canonise le rituel de communication interne hebdomadaire (« release note du cabinet ») : cadence inconditionnelle du vendredi, rubriques et sources, régime interne nominatif, ordre du vendredi, workflow agentique cible (rodage puis croisière au cran notifié). Skill de génération et connecteur Teams en écriture = chantiers reportés (§7).
> **Domicile** : `contrats/local/communication/newsletter.md`. **Propriété** : animateur du périmètre Communication & marque (Sarah Shaiek, délégation promue `organisation.md` v1.4 §3). **Autorité de promotion** : gardien du temple (procédure allégée — `doctrine.md` §5).
> **Adossé à** : `contrats/socle/organisation.md` v1.5 (§2 périmètre communication, §4 délégation, §5 réconciliation), `doctrine/doctrine.md` (§4 deux plans, §5 contrat local, §6 crans), `contrats/socle/memoire-organisation.md` (source de la rubrique « leçon apprise »), `contrats/socle/anonymisation.md` (§1 — réserve de sortie externe), `contrats/socle/table-des-crans.yaml` (cran *notifié*).
> **Rattachement** : périmètre *Cœur de métier / Connaissance, contenu & IP — communication & marque* ; chantiers reportés `skills/newsletter-hebdo/SKILL.md` (génération, non construit) et connecteur Teams en écriture (non construit, §7).
> **Frontière** : ce contrat canonise le **rituel** (cadence, rubriques, régime, ordre, cran cible). Son **exécution automatique** (agent génère et publie) dépend de briques non construites (§7) ; en attendant, la publication est assurée à la main par l'animateur ou le gardien (geste humain, hors crans).

## 0. Objet

Canoniser le **rituel de communication interne hebdomadaire** d'Allia : une « release note du cabinet » publiée chaque vendredi dans Teams, qui raconte la semaine de la firme. C'est le **premier contrat local** du dépôt ; il appartient au périmètre Communication & marque et se gouverne en procédure allégée (l'animateur propose, le gardien promeut).

## 1. Cadence — inconditionnelle, chaque vendredi

- Publication **chaque vendredi**, hebdomadaire.
- **Inconditionnelle** : la newsletter paraît quel que soit l'effectif de la firme, **gardien seul compris**. La firme se raconte sa semaine même à un. C'est une discipline rituelle, pas une fonction de la taille.

## 2. Régime — interne et nominatif

- Diffusion **interne uniquement** (collaborateurs de la firme).
- **Nominative** : elle nomme personnes, missions, clients comme le fait la matière interne — **pas d'anonymisation** (usage interne, avantage qui compose, `doctrine.md` §9).
- **Réserve en dur (sortie externe)** : toute reprise d'un fragment vers l'externe (site, LinkedIn, communication grand public) **déclenche la porte d'anonymisation** (`anonymisation.md` §1) et constituerait un **autre artefact**, soumis au cran *validé* + porte d'anonymisation. La présente newsletter, elle, reste interne et n'est jamais publiée telle quelle hors de la firme.

## 3. Rubriques et sources

Cinq rubriques, chacune avec sa source et son état de branchement :

| Rubrique | Source | État |
|---|---|---|
| Recrutements & arrivées | pipeline candidat / onboarding (sujet de conception en cours) | **manuel au départ** (capacité non construite) |
| Dossiers gagnés | Liste « Missions » (M365, `modele-donnees.md`) | branchable (lecture déjà outillée) |
| Évolution du SI Allia | historique Git des **promotions de la semaine** (PR mergées) | branchable (le dépôt est sa propre source) |
| Leçon apprise de la semaine | mémoire d'organisation **validée** du vendredi (`memoire-organisation.md`, `T-0005`) | **manuel au départ** (batch non construit) |

> L'« évolution du SI » se lit directement dans l'historique des promotions : chaque PR mergée de la semaine *est* un morceau d'évolution du SI, auto-documenté.

## 4. Ordre du vendredi — la mémoire d'abord

Chronologie stricte du vendredi, à ne jamais inverser :

1. **Validation de la mémoire d'organisation** (ligne à ligne, `memoire-organisation.md` §3) — le non-validé est oublié.
2. **Génération de la newsletter**, qui pioche la rubrique « leçon apprise » dans le **validé** uniquement — **jamais dans le verbatim brut, jamais avant la validation**.
3. **Publication** dans Teams.

La newsletter ne sort jamais une leçon apprise non validée. La porte de la mémoire (validation gardien) précède toujours la porte de la newsletter.

## 5. Domicile de publication

- Canal **Teams « Allia Consulting — vie interne »**, dans la conversation.
- La newsletter publiée **vit là** ; aucun double éditable ailleurs (une seule vérité, un seul domicile — `doctrine.md` §2).

## 6. Workflow et crans — rodage puis croisière

L'agent **ne publie jamais** une communication officielle sans être passé par l'épreuve. Deux états canonisés, du moins au plus autonome :

- **Rodage (agent assisté)** : l'agent **génère un brouillon** de newsletter en **zone de proposition** (cran *auto* — dérivé réversible, `table-des-crans.yaml`) ; le gardien (ou l'animateur) **relit**, ajuste, puis la publication a lieu. On éprouve plusieurs éditions avant de passer en croisière.
- **Croisière (agent autonome)** : une fois le rituel **prouvé fiable**, l'agent **génère et publie** dans Teams au cran **notifié** (l'agent agit, le gardien est informé) — cohérent avec `table-des-crans.yaml` (`notifier_equipe`, exemple « message de nomination à l'équipe »).

Le passage de rodage à croisière est une **décision du gardien**, prise au vu de l'épreuve (« prouvé par l'usage, pas supposé »), tracée par une montée de version de ce contrat.

> **Note transitoire.** Tant que le skill de génération et le connecteur Teams en écriture (§7) ne sont pas en service, **aucun agent ne peut générer ni publier** : la newsletter est rédigée et publiée **à la main** par l'animateur ou le gardien (geste humain, donc **libre**, hors crans — `doctrine.md` §6). Le présent contrat fixe la **cible agentique** pour quand l'infrastructure sera là ; le rituel, lui, démarre dès maintenant en manuel.

## 7. Dépendances et chantiers reportés

L'exécution **agentique** (états §6) suppose deux briques **non construites**, à inscrire au backlog le moment venu :

- **Skill `newsletter-hebdo`** — la procédure par laquelle l'agent agrège les rubriques (§3) depuis leurs sources et rédige le brouillon dans la voix Allia. Non construit.
- **Connecteur Teams en écriture** — le connecteur MCP Graph actuel (`outils/mcp-graph/`) lit les Listes SharePoint et écrit en Zone-de-proposition ; il **ne poste pas** de message Teams. Publier dans le canal suppose d'étendre le connecteur (ou d'en ajouter un) pour l'envoi de message Teams — chantier d'infrastructure (du même ordre que `T-0002b`). Non construit.

Tant que ces deux briques n'existent pas, voir la note transitoire (§6).

## 8. Évolution

Contrat **local** — il fait foi sur son périmètre et évolue par la **boucle de promotion en procédure allégée** (`doctrine.md` §5, §7) : l'**animateur propose**, le **gardien promeut**.

Aujourd'hui, l'animatrice (Sarah Shaiek) n'a pas encore de compte GitHub dans l'organisation : **le gardien porte la proposition** en attendant son branchement. À l'activation de son compte, la ligne dédiée du `.github/CODEOWNERS` (`/contrats/local/communication/ @animateur-communication @Alliaconsulting`, aujourd'hui en commentaire) sera activée, et Sarah proposera elle-même sur ce contrat.

---

*Premier contrat local du dépôt — périmètre Communication & marque. Il canonise le rituel de la newsletter hebdomadaire interne ; son exécution agentique attend les briques du §7. Il fait foi sur son périmètre et évolue par la boucle de promotion en procédure allégée, sous l'autorité du gardien.*
