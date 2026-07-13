# Génération de la newsletter hebdomadaire interne — Skill

> **id** : `newsletter-hebdo`
> **Version** : 1.0 — *candidat*. **Nature** : skill.
> **Changelog** : v1.0 — candidat, 13 juillet 2026 : création. Chantier `T-0011` (épreuve de fédération de la promotion). Décrit le skill qui **OUTILLE** le rituel canonisé par `contrats/local/communication/newsletter.md` v1.1 : il agrège les rubriques (§3) depuis leurs sources, rédige le **BROUILLON** de la newsletter dans la voix Allia, et le dépose en **Zone-de-proposition** via `create_list_item` (cran *auto* — état « rodage », newsletter.md §6). Il **ne réécrit pas** le rituel : toute règle de fond est un **pointeur** vers le contrat (on référence, on ne copie pas). La publication dans Teams est **hors périmètre** (connecteur non construit, newsletter.md §7) ; le passage rodage→croisière est une **décision du gardien**. Promotion par le **gardien** (procédure allégée) — aucune délégation retenue à ce stade (PR #198 fermée sans merge).
> **Domicile** : `skills/newsletter-hebdo/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `contrats/local/communication/newsletter.md` (v1.1 — **LE contrat outillé**, rituel §0–§7 : cadence §1, régime §2, rubriques §3, ordre du vendredi §4, domicile §5, crans §6, dépendances §7), `contrats/socle/memoire-organisation.md` (§3 — source **VALIDÉE** de la rubrique « leçon apprise » et porte de validation), `contrats/socle/modele-donnees.md` (Liste « Missions » ; Zone-de-proposition §3), `contrats/socle/anonymisation.md` (§1 — réserve de sortie externe), `contrats/socle/table-des-crans.yaml` (`ecrire_fait_derive_zone_proposition` = **auto** ; `notifier_equipe` = **notifié**), `contrats/socle/organisation.md` (§2 — périmètre *Communication & marque*), `doctrine/doctrine.md` (§5 contrat local, §6 crans, §9 nominatif interne), `CLAUDE.md`.

## 1. Objet

Outiller le **rituel de la newsletter hebdomadaire interne** canonisé par `newsletter.md` : **agréger** les rubriques (§3) depuis leurs sources, **rédiger** le brouillon dans la voix Allia, et le **déposer en Zone-de-proposition** pour relecture. Le skill **exécute** le rituel, il ne le **définit** pas : la cadence (**chaque vendredi**, §1), le régime interne nominatif (§2), les rubriques et leurs sources (§3), l'**ordre du vendredi** (§4), le domicile de publication (§5) et les crans (§6) **font foi dans le contrat** — ce skill y **renvoie**, il ne les recopie pas.

> **Bornes dures (reprises de `newsletter.md`, non négociables).**
> - L'agent **PRÉPARE** un brouillon en **Zone-de-proposition** (état « rodage », §6) ; il **ne publie jamais** dans Teams — la publication dépend du connecteur non construit (§7) et reste une porte (geste **humain** aujourd'hui ; cible « croisière » = cran *notifié*, sur décision du gardien).
> - L'écriture de l'agent va en **Zone-de-proposition UNIQUEMENT** (via `create_list_item`) ; **jamais dans une liste source** — le dérivé n'est jamais le saisi (`CLAUDE.md`).
> - La rubrique « leçon apprise » se pioche dans la **mémoire d'organisation validée** uniquement — **jamais dans le verbatim brut, jamais avant la validation** (ordre du vendredi, `newsletter.md` §4).

## 2. Entrées (lecture seule)

Les rubriques et leurs sources **font foi au §3 du contrat** ; ce skill les lit, il ne les redéfinit pas :

| Rubrique (`newsletter.md` §3) | Source | Accès |
|---|---|---|
| Dossiers gagnés | Liste « Missions » (M365, `modele-donnees.md`) | `list_items` (lecture — *auto*) |
| Évolution du SI Allia | historique Git des **PR mergées de la semaine** | lecture du dépôt (*auto*) |
| Leçon apprise de la semaine | mémoire d'organisation **validée** du vendredi (`memoire-organisation.md` §3) | lecture du **validé** uniquement |
| Recrutements & arrivées | pipeline candidat / onboarding | **manuel au départ** (capacité non construite, §3) |

> **Garde-fou d'entrée — l'ordre du vendredi (`newsletter.md` §4).** Ne générer la newsletter qu'**APRÈS** la validation de la mémoire d'organisation (ligne à ligne, porte du gardien). La leçon apprise ne sort que du **validé** — **jamais avant la validation**, **jamais dans le verbatim brut**. La porte de la mémoire précède **toujours** la porte de la newsletter.

## 3. Sortie (générée à la volée — aucun binaire versionné)

Un **brouillon** de newsletter, écrit en **Zone-de-proposition** (le brouillon y vit jusqu'à relecture — état « rodage », §6) :

~~~
create_list_item(fields = {
  "Title":   "NEWSLETTER-<AAAA-Sxx>",
  "Origine": "newsletter-hebdo",
  "Contenu": "<brouillon dans la voix Allia : rubriques renseignées (§3) ; leçon apprise
              issue du VALIDÉ ; mention : brouillon INTERNE — relecture puis publication
              humaine (connecteur Teams non construit, newsletter.md §7)>",
})
~~~

Écriture en **Zone-de-proposition UNIQUEMENT** — le skill n'écrit **jamais dans une liste source** (le journal est un dérivé réversible, `table-des-crans.yaml` : `ecrire_fait_derive_zone_proposition` = *auto*).

## 4. Déroulé et portes (rituel `newsletter.md` §4 / §6)

1. *(préalable, hors skill)* **Validation de la mémoire d'organisation** par le gardien (§4 ; `memoire-organisation.md` §3) — le non-validé est oublié.
2. **Lire** les sources des rubriques (§2) — *auto*.
3. **Rédiger** le brouillon dans la voix Allia — la leçon apprise **depuis le validé uniquement**.
4. **Déposer** le brouillon en **Zone-de-proposition** via `create_list_item` — *auto* (« rodage »).
5. **Relecture** par le gardien / l'animateur, puis **publication à la main** dans le canal Teams « vie interne » (§5) — **hors périmètre de l'agent** tant que le connecteur Teams en écriture (§7) n'existe pas.
6. **Cible « croisière » (§6)** : lorsque le connecteur Teams en écriture existera et que le rituel sera **prouvé fiable**, génération + publication au cran *notifié* — **décision du gardien**, tracée par une montée de version du **contrat** (pas de ce skill).

## 5. Crans (résolus via `table-des-crans.yaml`)

| Action | Cran | Fondement |
|---|---|---|
| Lire Missions / historique Git / mémoire **validée** | **auto** | lecture réversible, interne, locale |
| Déposer le brouillon en **Zone-de-proposition** (`create_list_item`) | **auto** | `ecrire_fait_derive_zone_proposition` — le dérivé n'est jamais le saisi |
| **Publier** dans Teams | **hors périmètre agent** (rodage) → cible *notifié* en croisière | connecteur non construit (§7) ; `notifier_equipe` (§6), décision gardien |
| **Reprendre** un fragment vers l'externe | **validé + porte anonymisation** | `anonymisation.md` §1 — constitue un **autre artefact** (§2) |

## 6. Garde-fous inscrits dans ce skill

- **Zone-de-proposition UNIQUEMENT** : l'agent écrit le brouillon en zone via `create_list_item` ; **jamais dans une liste source**.
- **Ne publie jamais** dans Teams : le skill s'arrête au brouillon en zone ; la publication est humaine (connecteur §7 non construit), *notifié* en cible croisière.
- **Leçon apprise du validé seul** : **jamais dans le verbatim brut, jamais avant la validation** (ordre du vendredi, §4).
- **Rituel non réécrit** : toute règle de fond (cadence, rubriques, régime, ordre, crans) est un **pointeur** vers `newsletter.md` — on référence, on ne copie pas.
- **Interne et nominatif** (§2, `doctrine.md` §9) ; **réserve de sortie externe** : toute reprise vers l'externe déclenche la porte d'`anonymisation.md` §1 (autre artefact, cran *validé*).
- **Cadence inconditionnelle du vendredi** (§1) : l'agent produit le brouillon quand on le lui demande ; il ne juge pas de l'opportunité de paraître.

## 7. Ce que ce skill ne fait pas

- Il **ne publie pas** dans Teams (connecteur en écriture non construit, `newsletter.md` §7).
- Il **ne valide pas** la mémoire d'organisation (porte du gardien, §4 ; `memoire-organisation.md` §3).
- Il **n'écrit dans aucune source** — le brouillon vit en **Zone-de-proposition**.
- Il **ne sort jamais** une leçon apprise non validée.
- Il **ne reprend rien vers l'externe** (ce serait un autre artefact — `anonymisation.md` §1).
- Il **ne décide pas** du passage rodage→croisière (décision du gardien, §6).
- Il **ne prend aucun engagement** juridique ou financier.

## 8. Prérequis avant mise en service

1. **Contrat `newsletter.md` promu** — *levé : v1.1 promu le 6 juillet 2026*.
2. **Connecteur Teams en écriture** (`newsletter.md` §7) — **NON construit** : il borne la seule **PUBLICATION** (cible croisière) ; le **rodage** (brouillon en Zone-de-proposition) **n'en dépend pas** et est faisable dès la promotion.
3. **Promotion de ce skill** par le gardien (procédure allégée) — prérequis (PR en **draft**, `T-0011`).
4. **Épreuve réelle** (SOLDÉ de `T-0011`) : un brouillon de newsletter généré en **Zone-de-proposition** sur une semaine réelle, **ordre du vendredi** respecté, leçon apprise issue du **validé**.

## 9. Évolution

Ce skill est **candidat**. Sa promotion suit la boucle (`doctrine.md` §7) : candidat → avis d'impact → **promotion par le gardien** (procédure allégée, portée locale — `doctrine.md` §5), montée de version en en-tête, corps byte-identique à la promotion. La délégation de ce périmètre à un animateur n'a pas été retenue à ce stade (PR #198 fermée sans merge) : la promotion reste au gardien. Retour arrière = repointage.
