# Relevé de décisions — Skill

> **id** : `releve-de-decisions`
> **Version** : 1.2 — *promu*. **Nature** : skill.
> **Changelog** : v1.2 — repointage du renvoi de câblage vers `T-0002b` après le découpage (PR #23) du chantier d'écriture Graph, 7 juin 2026 : le renvoi du §6 pointe désormais vers `T-0002b` (déploiement / écriture réelle). Aucun changement de comportement du skill. v1.1 — **CORRECTION du §7 (anonymisation)**, 7 juin 2026 : aligné sur `anonymisation.md` v1.3 — un relevé réutilisé **en interne** (même pour un autre client) reste **nominatif** ; l'anonymisation ne se déclenche qu'à la **sortie externe de la firme**. v1.0 — promu via boucle de promotion (procédure allégée) ; alignement sur le statut backlog (T-0001 `promu`, PR #11). Artefact référencé « v1.0 » par T-0001 et les dérivés.
> **Domicile** : `skills/releve-de-decisions/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `doctrine/doctrine.md` (§6, §7), `contrats/socle/table-des-crans.yaml`, `contrats/socle/anonymisation.md`, `contrats/socle/design-system.md`, `contrats/socle/modele-donnees.md`, `skills/compte-rendu-reunion/SKILL.md` (référence de format), `CLAUDE.md`.

## 1. Objet

Extraire, **depuis un compte rendu** (ou, à défaut, des notes/transcript), la **liste des décisions** prises en réunion, chacune assortie de son **statut** : `prise` ou `à confirmer`. Le relevé est un fait **dérivé** (§6) : un extrait structuré, fidèle, exploitable pour le suivi — il ne crée aucune décision, il les **isole** de la matière existante.

> **Relation au CR.** Ce skill consomme idéalement la section **« Décisions »** d'un compte rendu produit par `compte-rendu-reunion` (même voix, même format). Il peut aussi opérer directement sur des notes brutes, mais le CR reste l'entrée canonique.

## 2. Entrées

- **Matière** (au moins l'une) : un **compte rendu** (de préférence issu de `compte-rendu-reunion`), ou des notes brutes / un transcript.
- **Métadonnées** (reprises du CR si présentes) : `objet`, `date`, `mission` / `client`, `participants`.

> **Règle de fidélité.** Si une métadonnée manque, la **marquer « à confirmer »** ; **ne jamais inventer** une décision, un statut ou un porteur. Une décision absente de la matière n'existe pas (§8).

## 3. Procédure

1. **Lire** la matière (CR ou notes).
2. **Repérer les décisions** — les énoncés qui tranchent (« validé », « retenu », « acté », « reporté »). Ignorer les simples discussions sans arbitrage (→ relèvent des « points en suspens » du CR).
3. **Statuer** chaque décision :
   - `prise` — arbitrage explicite et non conditionnel dans la matière ;
   - `à confirmer` — décision annoncée mais conditionnelle, partielle, ou dépendante d'un tiers/d'une validation ultérieure.
4. **Rattacher** chaque décision, si la matière le permet : porteur/échéance de l'action associée, et **référence à la source** (section du CR, ligne de notes).
5. **Rédiger** le relevé au format §4, dans la voix Allia (sobre, factuel).

## 4. Format de sortie

```
# Relevé de décisions — <objet>

Date : <date | à confirmer>
Mission : <code mission / client | à confirmer>
Source : <CR « <objet> » du <date> | notes brutes>

## Décisions
| # | Décision | Statut | Source |
|---|---|---|---|
| 1 | <décision> | prise / à confirmer | <section CR / ligne notes> |

## À confirmer — détail
- <décision « à confirmer »> : <ce qui manque pour la rendre « prise » (validation, arbitrage, dépendance)>
```

**Statut** : exactement deux valeurs — `prise` ou `à confirmer`. **Ton** : voix Allia (sobre, factuel).

**Rendu visuel** (HTML/PDF/page) — suit `contrats/socle/design-system.md` (on consomme, on ne recopie pas). Convention de statut, alignée sur le composant **Pill** (§5.3 du design system) :
- `prise` → **Pill primaire** (ambre plein) ;
- `à confirmer` → **Pill secondaire** (ambre clair).

## 5. Crans (résolus via `table-des-crans.yaml`)

| Action | Cran | Note |
|---|---|---|
| **Produire le relevé** (écrit en zone de proposition) | **auto** | réversible, interne, local — l'agent agit seul |
| **Envoyer le relevé hors firme** (client, externe) | **validé** | sort de la firme — porte humaine du gardien |
| **Réutiliser** pour un autre client / **entrée au canon** | **porte anonymisation** | déclenchée par règle — voir §7 et `anonymisation.md` §1 |

## 6. Zone de proposition

Le relevé est un **dérivé** : il s'écrit dans la **zone de proposition** (`modele-donnees.md` §3), jamais dans la source ; sa promotion en vérité est une **étape tracée**. **État du câblage** : l'écriture M365 n'est pas encore outillée (`modele-donnees.md` §4 — *partiellement câblé* ; écriture Graph = `T-0002b`). En attendant, la zone de proposition est **simulée en local** (`zone-proposition/`).

## 7. Anonymisation

Par défaut, un relevé **reste nominatif** : tant qu'il circule **à l'intérieur de la firme** — même mission, même client, **ou réutilisé pour une autre mission / un autre client en interne** — **pas d'anonymisation** (c'est l'avantage qui compose, `anonymisation.md` §1). La porte se déclenche dès que la matière **quitte la firme vers l'extérieur** (critère décisif d'`anonymisation.md` §1) :

- le relevé **est publié hors de la firme** ;
- le relevé **est rendu hors de la firme** (livrable client).

Dans ces cas, appliquer `anonymisation.md` (§1→§4) **avant** usage. Attention particulière : un libellé de décision peut contenir un nom de client, un montant, une échéance datée — autant de quasi-identifiants à généraliser.

## 8. Critères de qualité (Definition of Done)

- [ ] Chaque décision porte un **statut** ∈ {`prise`, `à confirmer`} — **aucune autre valeur**.
- [ ] **Aucune décision inventée** : fidélité stricte à la matière ; un manque se marque « à confirmer », ne se comble pas.
- [ ] Chaque décision est **rattachée à sa source** (section du CR / ligne de notes).
- [ ] Les décisions « à confirmer » précisent **ce qui manque** pour les rendre « prises ».
- [ ] **Aucun identifiant client** si le relevé est destiné au **canon** ou à l'**externe** (anonymisation appliquée, §7).
- [ ] **Format respecté** (en-tête, tableau Décisions, détail « à confirmer »).
- [ ] Écrit en **zone de proposition** ; non mergé, non promu par l'agent.

## 9. Exemple minimal

**Entrée — extrait de CR (produit par `compte-rendu-reunion`)**
```
## Décisions
| Décision | Statut |
|---|---|
| Périmètre de la phase 1 validé | prise |
| Budget de la phase 1 | à confirmer |
```

**Sortie — relevé de décisions**
```
# Relevé de décisions — Cadrage phase 1, projet Atlas

Date : 12/03 (année à confirmer)
Mission : projet Atlas (code mission à confirmer)
Source : CR « Cadrage phase 1, projet Atlas » du 12/03

## Décisions
| # | Décision | Statut | Source |
|---|---|---|---|
| 1 | Périmètre de la phase 1 validé | prise | CR §Décisions |
| 2 | Budget de la phase 1 | à confirmer | CR §Décisions |

## À confirmer — détail
- Budget de la phase 1 : arbitrage à trancher avec le service achats (dépendance externe).
```

## 10. Évolution

Ce skill est **promu** (procédure allégée, portée locale, `doctrine.md` §5). Toute évolution future suit la boucle de promotion (`doctrine.md` §7) avec **montée de version** en en-tête. Retour arrière = repointage.
