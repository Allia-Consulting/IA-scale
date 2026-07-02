---
# Kick-off de mission — Skill

> **id** : `kick-off`
> **Version** : 1.0 — *promu*. **Nature** : skill.
> **Changelog** : v1.0 — promu, 2 juillet 2026 : promotion par le gardien (procédure allégée), chantier `T-0022`. v1.0 — candidat, 2 juillet 2026 : création (chantier `T-0022`, deuxième marche de la tranche verticale métier, plan §6 T-1.2). Décrit le skill qui, du BRIEF VALIDÉ (produit par `cadrage-mission`), génère la PROPOSITION et le SUPPORT DE KICK-OFF en consommant le design system par référence, journalise en Zone-de-proposition, notifie l'équipe (notifié) ; l'ENVOI au client reste une porte humaine (validé).
> **Domicile** : `skills/kick-off/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `skills/cadrage-mission/SKILL.md` (v1.1 promu — produit le brief d'entrée), `contrats/socle/design-system.md` (tokens, composants, voix §7 — consommé par référence), `contrats/socle/anonymisation.md` (§1 — matière d'un client tiers dans un livrable client = porte automatique), `contrats/socle/table-des-crans.yaml` (`ecrire_fait_derive_zone_proposition` = **auto** ; `notifier_equipe` = **notifié** ; `envoyer_livrable_client` = **validé**, grade habilité — organisation.md §4 bis ; `reutiliser_matiere_interne` = **auto**), `contrats/socle/modele-donnees.md` (§2 bis — Bibliothèques Propositions/Livrables/Capitalisation ; §3 — Zone-de-proposition), `backlog/chantiers/T-0022.yaml`, `backlog/chantiers/T-0024.yaml` (outillage de dépôt à cible figée), `CLAUDE.md`.

## 1. Objet

Du **brief validé** (« le brief suffit », skill `cadrage-mission`), produire la **proposition** et le **support de kick-off** de la mission — générés **à l'exécution** depuis le design system **résolu au moment de la génération** (versions à portée : une mission en cours reste sur sa version, un livrable ne change pas d'apparence en plein milieu) — puis **notifier l'équipe**. L'**envoi au client n'appartient pas à l'agent** : c'est une porte humaine.

## 2. Entrées

| Donnée | Source | Usage |
|---|---|---|
| Brief validé | Zone-de-proposition, `Title = BRIEF-<code mission>`, `Origine = cadrage-mission` | matière unique du kick-off : périmètre, jalons, équipe, templates |
| Design system | `contrats/socle/design-system.md` (pull, version résolue à la génération) | tokens, composants, voix & ton (§7) |
| Matière capitalisée | Bibliothèque « Capitalisation » | réutilisation INTERNE nominative (auto) ; si matière d'un CLIENT TIERS destinée au livrable client → porte anonymisation |
| Compte / Client | Liste « Comptes » | adressage de la proposition |

> **Garde-fou d'entrée — brief requis.** Ne générer QUE si un `BRIEF-<code mission>` validé existe en Zone-de-proposition. Sans brief : refus explicite et renvoi vers `cadrage-mission`. Le kick-off ne cadre pas ; il exécute un cadrage validé.

## 3. Sorties (générées à la volée — aucun binaire versionné)

1. **La proposition** — document remis au client (structure : contexte, périmètre, approche, jalons, équipe, conditions), au design system.
2. **Le support de kick-off** — présentation de lancement (objectifs, jalons, rôles, gouvernance de mission, premiers pas), au design system.
3. **Le journal** en Zone-de-proposition :

~~~
create_list_item(fields = {
  "Title":   "KICKOFF-<code mission>-<AAAAMMJJ>",
  "Origine": "kick-off",
  "Contenu": "<résumé : mission, documents générés (noms + emplacements internes),
              version du design system résolue, mention : brouillons internes — envoi client
              = porte humaine (grade habilité), anonymisation appliquée si matière tiers>",
})
~~~

Les binaires générés sont des **brouillons internes** : ils vivent en zone de travail interne (dépôt via outillage à **cible figée côté serveur**, extension `T-0024`, sur le modèle de `televerser_brouillon_offre` — collision = fail, jamais d'écrasement). **Jamais** déposés dans un espace exposé au client par l'agent.

## 4. Déroulé et portes

1. **Lire** le brief validé + référentiels (auto).
2. **Générer** proposition et support depuis le design system résolu (auto — production interne réversible).
3. **Porte anonymisation (automatique, orthogonale)** : toute matière d'un **client tiers** insérée dans un document destiné au client est anonymisée AVANT insertion (anonymisation.md §1) ; les données du client destinataire restent nominatives.
4. **Déposer** les brouillons en zone de travail interne (auto — cible figée, `T-0024`) et **journaliser** en Zone-de-proposition (auto).
5. **Notifier l'équipe** (notifié) — message de nomination/lancement, avec la proposition et le support (scénario du document de bienvenue).
6. **Envoi au client** : **validé** — porte tenue par un grade habilité (organisation.md §4 bis). L'agent prépare ; l'humain envoie.

## 5. Crans (résolus via `table-des-crans.yaml`)

| Action | Cran | Fondement |
|---|---|---|
| Lire brief / référentiels | **auto** | lecture réversible, interne, locale |
| Générer les documents (brouillons internes) | **auto** | réversible, interne, local |
| Déposer en zone de travail + journaliser | **auto** | cible figée côté serveur ; `ecrire_fait_derive_zone_proposition` |
| Notifier l'équipe | **notifié** | `notifier_equipe` — l'exemple canonique de la table |
| Envoyer la proposition / le support au client | **validé — grade habilité** | `envoyer_livrable_client` : action d'agent qui engage la firme |
| Insérer de la matière d'un client tiers | **porte anonymisation** | automatique, orthogonale au cran (anonymisation.md §1) |

## 6. Garde-fous inscrits dans ce skill

- **Brief requis** : pas de kick-off sans `BRIEF-<code mission>` validé — refus explicite sinon.
- **Design system par référence** : version résolue à la génération, consignée au journal ; jamais de copie éditable.
- **Aucun envoi client par l'agent** : le skill s'arrête aux brouillons internes + notification ; l'envoi est humain (grade habilité).
- **Porte anonymisation** sur la matière d'un client tiers ; le nominatif du client destinataire est préservé.
- **Collision = fail** : un document existant du même nom exige un retrait humain — jamais d'écrasement.
- **Versions à portée** : la mission reste sur la version du design system résolue à son lancement, sauf migration explicite.

## 7. Ce que ce skill ne fait pas

- Il ne cadre pas la mission (skill `cadrage-mission`, `T-0021`).
- Il n'envoie rien au client, ne publie rien, ne signe rien.
- Il ne crée pas l'espace de mission (cadrage + outillage `T-0024`).
- Il n'écrit rien dans une source ; le journal vit en Zone-de-proposition.
- Il ne prend aucun engagement juridique ou financier (PROSCRIT).

## 8. Prérequis avant mise en service

1. **`cadrage-mission` promu** — *levé : v1.1 promu le 2 juillet 2026*.
2. **`T-0024`** : outillage de dépôt interne à cible figée (extension du connecteur, modèle `televerser_brouillon_offre`).
3. **Promotion de ce skill** par le gardien (procédure allégée).
4. **Épreuve réelle** (SOLDÉ de `T-0022`) : proposition + support générés sur une affaire — réelle ou de démonstration explicitement étiquetée — crans et porte d'anonymisation respectés.

## 9. Évolution

Ce skill est un **candidat** (v1.0). Sa promotion suit la boucle (`doctrine.md` §7) : candidat → avis d'impact → promotion gardien (procédure allégée), montée de version en en-tête, corps byte-identique à la promotion. Retour arrière = repointage.
