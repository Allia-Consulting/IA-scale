# Mémoire d'organisation — Allia Consulting

> **Version** : 1.4 — *promu*. **Statut** : contrat socle **interne, nominatif** — fait foi.
> **Changelog** : v1.4 — promu via boucle de promotion, 30 juin 2026 : **changement de domicile d'exécution et de déclenchement.** Le mécanisme s'exécute désormais dans une **session claude.ai de l'espace Allia** (rendez-vous hebdomadaire le **vendredi**), et non plus en **batch Cowork nocturne**. Raison (confrontation au réel, T-0005) : l'écoute des **conversations Claude** de l'espace n'est accessible qu'en **session claude.ai** (recherche d'historique de chat, utilisateur courant) ; **Cowork et Claude Code n'exposent pas** cet historique. La note « Cowork local » (v1.2, 10 juin) est corrigée. §1, §2 et §6 actualisés ; **§3 (validation du vendredi), §4 (nominatif) et §5 (RGPD/anonymisation) inchangés**. v1.3 — alignement minimal, 12 juin 2026 : §5 — le déclenchement de la porte d'anonymisation renvoie au nouveau critère (**communication grand public** — `anonymisation.md` §1, révisé le 12 juin 2026) au lieu de « publication, livrable rendu hors firme ». Rien d'autre. v1.2 — promu via boucle de promotion, 12 juin 2026 ; §2 : justification périmée « en attendant T-0002b » remplacée (chapeau T-0002b promue le 10 juin 2026) — les synthèses « mémoire hebdo » restent simulées en local sous `zone-proposition/memoire/` jusqu'à T-0005. Aucun autre changement de fond. v1.1 — candidat, 9 juin 2026 : ajout du **renvoi normatif vers `contrats/socle/rgpd-ecoute-teams.md`** (cadre RGPD de l'écoute Teams/Claude) en en-tête et au §5. Régime **nominatif §4 confirmé, non modifié** ; aucun autre changement de fond. v1.0 — candidat (mécanisme initial).
> **Domicile** : `contrats/socle/memoire-organisation.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§2 « le dérivé n'est jamais le saisi », §7 boucle de promotion), `contrats/socle/modele-donnees.md` (§2 bis/§3 — zone de proposition, champ d'origine « mémoire hebdo »).
> **Renvoi normatif** : `contrats/socle/anonymisation.md` — ce contrat est **interne et nominatif** ; toute **sortie externe** d'un fragment de mémoire **déclenche la porte d'anonymisation** (anonymisation.md §1). Voir §5. **`contrats/socle/rgpd-ecoute-teams.md`** — **cadre RGPD de conformité de l'écoute** Teams/Claude (finalité, base légale, minimisation/rétention, transparence, droits des personnes) ; prérequis normatif de l'écoute réelle.
> **Rattachement** : capacité *Connaissance, contenu & IP* ; chantier `backlog/chantiers/T-0005.yaml` (mécanisme) ; cran de promotion `promouvoir_contrat_socle` (gardien).

## 0. Objet

Donner à Allia une **mémoire d'organisation** : ce que la firme a appris, décidé, répété au fil des semaines — distinct des *données* (M365) et des *règles* (le canon). Cette mémoire est un **dérivé** : elle n'est jamais saisie comme une source, elle est **proposée** puis **validée**, ligne à ligne, par le gardien.

Ce contrat dit **comment** cette mémoire se produit, **où** elle vit transitoirement, **comment** elle se valide, et **quand** elle reste nominative ou doit être anonymisée.

## 1. Mécanisme — un rendez-vous hebdomadaire en session claude.ai, une synthèse candidate

- **Cadence.** Un **rendez-vous hebdomadaire, le vendredi**, dans une **session claude.ai de l'espace Allia** (sous l'identité du gardien), écoute les **conversations Claude + Teams de la semaine** et produit **UNE synthèse candidate** pour la semaine. La production précède immédiatement la validation du vendredi (§3).
- **Écriture continue : abandonnée.** On ne tient pas une mémoire qui se réécrit en permanence (ni relisible, ni gouvernable à la promotion). On tient **un rendez-vous hebdomadaire** : une synthèse, candidate, examinée d'un bloc.
- **Le dérivé n'est jamais le saisi.** La synthèse atterrit en **zone de proposition**, jamais dans une source. Sa promotion (validation) est une étape **tracée** (doctrine §2).
- **Où s'exécute le mécanisme.** En **session claude.ai de l'espace Allia**, seule surface où l'**écoute des conversations Claude** (recherche d'historique de chat, utilisateur courant) est disponible — **Cowork et Claude Code n'exposent pas** cet historique. Le périmètre et le cadre de cette écoute sont fixés par `rgpd-ecoute-teams.md` (annexe 1 §3 : Claude = espace Allia, utilisateur courant ; Teams = canaux et missions, **hors 1-à-1**).

## 2. Domicile transitoire — zone de proposition, champ d'origine « mémoire hebdo »

- **Cible réelle** : liste **« Zone-de-proposition »** du site AlliaConsuling, avec un **champ d'origine = « mémoire hebdo »** qui distingue ces synthèses des autres faits dérivés (`modele-donnees.md` §2 bis/§3).
- Le connecteur Graph MCP en écriture est **déployé et prouvé** (chapeau `T-0002b` promue le 10 juin 2026). La **cible** des synthèses « mémoire hebdo » est la **liste réelle** via `create_list_item` (appelé depuis la session claude.ai, §1) ; la simulation locale `zone-proposition/memoire/` est **abandonnée** à la mise en service du mécanisme (`T-0005`).
- **Aucune copie** de la mémoire ailleurs : une seule vérité, un seul domicile (doctrine §2).

## 3. Validation — ligne à ligne, le vendredi ; non-validé = oublié

- Le **vendredi**, le gardien (ou un rôle désigné) **valide ligne à ligne** la synthèse candidate.
- **Ce qui n'est pas validé est oublié** : pas de rétention par défaut, pas d'accumulation silencieuse. La mémoire de la firme est ce que la firme a **explicitement retenu**.
- La validation est l'**acte de promotion** de cette mémoire (doctrine §7) : elle déplace les lignes retenues du candidat vers la mémoire promue, de façon tracée.

## 4. Nature — interne et nominative

- Cette mémoire est **interne** à la firme et **nominative** : elle nomme les personnes, les missions, les clients comme la matière interne le fait. C'est l'**avantage qui compose** (apprentissage inter-missions, doctrine §9) ; l'anonymisation **ne s'applique pas** à l'usage interne.
- Elle référence les personnes comme le fait `organisation.md` (par identité Entra le cas échéant) ; elle ne **duplique aucun dossier RH** (ceux-ci vivent dans M365).

## 5. Renvoi normatif à l'anonymisation — à la sortie externe

Conformément à `anonymisation.md` §1 (déclencheur, révisé le 12 juin 2026), toute **communication grand public** d'un fragment de cette mémoire **déclenche la porte d'anonymisation AVANT l'usage** (cran `anonymisation`, orthogonal au cran de l'action). Le critère décisif est celui d'`anonymisation.md` §1. La **réutilisation interne** (d'une mission/équipe à l'autre) reste **nominative** et ne déclenche rien.

**Cadre RGPD de l'écoute.** L'**écoute** elle-même (entrée du mécanisme §1 : conversations Teams/Claude) est un traitement de données personnelles gouverné par `contrats/socle/rgpd-ecoute-teams.md` (cadre de conformité : finalité limitée aux apprentissages **collectifs**, base légale d'intérêt légitime, minimisation/rétention — suppression du brut et du non-validé, transparence préalable, droits des personnes). Ce cadre est un **prérequis normatif de l'écoute réelle**. Le régime **nominatif** du §4 (ci-dessus) est **confirmé** par ce cadre, pas modifié.

## 6. Crans et gouvernance

- **Produire la synthèse candidate** (rendez-vous hebdo en session claude.ai, écriture en zone de proposition) : cran **auto** — réversible, interne, dérivé (`table-des-crans.yaml` : `ecrire_fait_derive_zone_proposition`).
- **Promouvoir une ligne de mémoire** (validation du vendredi) : **porte humaine** du gardien — c'est une promotion.
- **Sortir un fragment hors firme** : cran **validé** + **porte d'anonymisation** (§5).
- L'agent **ne promeut jamais** et **n'écrit jamais** une ligne de mémoire comme une source.

## 7. Comment ce contrat évolue

Contrat socle **promu** — il fait foi (doctrine §7). Toute évolution ultérieure (cadence, champs, seuils de rétention) est elle-même un candidat, promu par le gardien. `CLAUDE.md` renvoie à ce contrat (« résous aussi `memoire-organisation.md` ») ; le renvoi se résout pleinement.

---

*Contrat socle promu — interne et nominatif. Il fait foi et évolue par la boucle de promotion. La mémoire qu'il régit est un dérivé : proposée, validée, jamais saisie.*
