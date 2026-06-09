# Mémoire d'organisation — Allia Consulting

> **Version** : 1.0 — **CANDIDAT** (pas encore promu). **Statut** : contrat socle **interne, nominatif** — *en attente de promotion par le gardien*.
> **Domicile** : `contrats/socle/memoire-organisation.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§2 « le dérivé n'est jamais le saisi », §7 boucle de promotion), `contrats/socle/modele-donnees.md` (§2 bis/§3 — zone de proposition, champ d'origine « mémoire hebdo »).
> **Renvoi normatif** : `contrats/socle/anonymisation.md` — ce contrat est **interne et nominatif** ; toute **sortie externe** d'un fragment de mémoire **déclenche la porte d'anonymisation** (anonymisation.md §1). Voir §5.
> **Rattachement** : capacité *Connaissance, contenu & IP* ; chantier `backlog/chantiers/T-0005.yaml` (mécanisme) ; cran de promotion `promouvoir_contrat_socle` (gardien).

## 0. Objet

Donner à Allia une **mémoire d'organisation** : ce que la firme a appris, décidé, répété au fil des semaines — distinct des *données* (M365) et des *règles* (le canon). Cette mémoire est un **dérivé** : elle n'est jamais saisie comme une source, elle est **proposée** puis **validée**, ligne à ligne, par le gardien.

Ce contrat dit **comment** cette mémoire se produit, **où** elle vit transitoirement, **comment** elle se valide, et **quand** elle reste nominative ou doit être anonymisée.

## 1. Mécanisme — un batch nocturne hebdomadaire, une synthèse candidate

- **Cadence.** Un **batch Cowork nocturne**, du **jeudi au vendredi**, écoute les **conversations Claude + Teams de la semaine** et produit **UNE synthèse candidate** pour la semaine.
- **Écriture continue : abandonnée.** On ne tient pas une mémoire qui se réécrit en permanence (ni relisible, ni gouvernable à la promotion). On tient **un rendez-vous hebdomadaire** : une synthèse, candidate, examinée d'un bloc.
- **Le dérivé n'est jamais le saisi.** La synthèse atterrit en **zone de proposition**, jamais dans une source. Sa promotion (validation) est une étape **tracée** (doctrine §2).

## 2. Domicile transitoire — zone de proposition, champ d'origine « mémoire hebdo »

- **Cible réelle** : liste **« Zone-de-proposition »** du site AlliaConsuling, avec un **champ d'origine = « mémoire hebdo »** qui distingue ces synthèses des autres faits dérivés (`modele-donnees.md` §2 bis/§3).
- **En attendant `T-0002b`** (déploiement du connecteur Graph MCP en écriture) : la zone est **simulée en local**, sous **`zone-proposition/memoire/`**. Aucune écriture réelle dans M365 tant que T-0002b n'est pas déployé.
- **Aucune copie** de la mémoire ailleurs : une seule vérité, un seul domicile (doctrine §2).

## 3. Validation — ligne à ligne, le vendredi ; non-validé = oublié

- Le **vendredi**, le gardien (ou un rôle désigné) **valide ligne à ligne** la synthèse candidate.
- **Ce qui n'est pas validé est oublié** : pas de rétention par défaut, pas d'accumulation silencieuse. La mémoire de la firme est ce que la firme a **explicitement retenu**.
- La validation est l'**acte de promotion** de cette mémoire (doctrine §7) : elle déplace les lignes retenues du candidat vers la mémoire promue, de façon tracée.

## 4. Nature — interne et nominative

- Cette mémoire est **interne** à la firme et **nominative** : elle nomme les personnes, les missions, les clients comme la matière interne le fait. C'est l'**avantage qui compose** (apprentissage inter-missions, doctrine §9) ; l'anonymisation **ne s'applique pas** à l'usage interne.
- Elle référence les personnes comme le fait `organisation.md` (par identité Entra le cas échéant) ; elle ne **duplique aucun dossier RH** (ceux-ci vivent dans M365).

## 5. Renvoi normatif à l'anonymisation — à la sortie externe

Conformément à `anonymisation.md` §1 (déclencheur), **toute sortie externe de la firme** d'un fragment de cette mémoire — publication, livrable rendu hors firme — **déclenche la porte d'anonymisation AVANT l'usage** (cran `anonymisation`, orthogonal au cran de l'action). Le critère décisif reste « la matière **quitte-t-elle la firme** ? ». La **réutilisation interne** (d'une mission/équipe à l'autre) reste **nominative** et ne déclenche rien.

## 6. Crans et gouvernance

- **Produire la synthèse candidate** (batch nocturne, écriture en zone de proposition) : cran **auto** — réversible, interne, dérivé (`table-des-crans.yaml` : `ecrire_fait_derive_zone_proposition`).
- **Promouvoir une ligne de mémoire** (validation du vendredi) : **porte humaine** du gardien — c'est une promotion.
- **Sortir un fragment hors firme** : cran **validé** + **porte d'anonymisation** (§5).
- L'agent **ne promeut jamais** et **n'écrit jamais** une ligne de mémoire comme une source.

## 7. Comment ce contrat évolue

Contrat socle **candidat** : il devient *fait foi* à sa **promotion** par le gardien (doctrine §7). Toute évolution ultérieure (cadence, champs, seuils de rétention) est elle-même un candidat. `CLAUDE.md` renvoie à ce contrat (« résous aussi `memoire-organisation.md` ») ; le renvoi se résout pleinement une fois ce contrat promu.

---

*Contrat socle candidat — interne et nominatif. Il attend la promotion du gardien. La mémoire qu'il régit est un dérivé : proposée, validée, jamais saisie.*
