# Compte rendu de réunion — Skill

> **id** : `compte-rendu-reunion`
> **Version** : 1.2 — *promu*. **Nature** : skill.
> **Changelog** : v1.2 — alignement sur la **révision de la sortie de firme** (décision du gardien, 12 juin 2026 ; `anonymisation.md` v1.4, doctrine v1.6, `organisation.md` v1.3) : §5 — l'envoi au client par un **humain collaborateur** est **libre** (hors crans) ; l'envoi par l'**agent** reste **validé**, porte tenue par un **grade habilité** ; §7 — déclencheur aligné (**communication grand public** ; **matière d'un client tiers** avant insertion dans un livrable). La réutilisation interne nominative est inchangée. v1.1 — **CORRECTION du §7 (anonymisation)**, 7 juin 2026 : aligné sur `anonymisation.md` v1.3 — un CR réutilisé **en interne** (même pour un autre client) reste **nominatif** ; l'anonymisation ne se déclenche qu'à la **sortie externe de la firme**. v1.0 — promu via boucle de promotion (procédure allégée) ; exécution du chantier T-0004 (test de sortie A0.9). Artefact cité « v1.0 » par le dérivé `CR-test-A0.6`.
> **Domicile** : `skills/compte-rendu-reunion/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `doctrine/doctrine.md` (§6, §7), `contrats/socle/table-des-crans.yaml`, `contrats/socle/anonymisation.md`, `contrats/socle/design-system.md`, `contrats/socle/modele-donnees.md`, `CLAUDE.md`.

## 1. Objet

Transformer des **notes brutes** ou un **transcript** de réunion en un **compte rendu (CR) structuré, fidèle et exploitable** : un document court qui dit ce qui a été discuté, ce qui a été décidé, qui fait quoi et pour quand. Le CR est un fait **dérivé** (§6) ; il sert l'exécution d'une mission et ne se substitue jamais à la source.

## 2. Entrées

- **Matière** (au moins l'une) : notes brutes prises en séance, ou transcript (verbatim, sortie d'outil de transcription).
- **Métadonnées** :
  - `objet` — sujet de la réunion ;
  - `date` — date (et heure si utile) ;
  - `mission` / `client` — affaire rattachée (code mission, cf. `modele-donnees.md` §2) ;
  - `participants` — présents et excusés ;
  - `type de réunion` — cadrage, point d'avancement, comité de pilotage, atelier, etc.

> **Règle de fidélité.** Si une métadonnée manque, la **marquer « à confirmer »** dans le CR. **Ne jamais l'inventer** ni la déduire au-delà de ce que la matière permet (§8).

## 3. Procédure

1. **Lire** intégralement la matière (notes ou transcript).
2. **Identifier l'objet** de la réunion et le rattacher à la mission.
3. **Extraire les points discutés** — les sujets réellement abordés, sans commentaire ajouté.
4. **Isoler les décisions**, chacune avec un **statut** : `prise` ou `à confirmer`.
5. **Extraire les actions** — pour chacune : **responsable** et **échéance** (ou « à définir » si absent).
6. **Lister les points en suspens** — questions ouvertes, sujets reportés, dépendances.
7. **Rédiger** le CR au format §4, dans la voix Allia (sobre, factuel).

## 4. Format de sortie

```
# Compte rendu — <objet>

Date : <date | à confirmer>
Mission : <code mission / client | à confirmer>
Participants : <présents ; excusés | à confirmer>

## Résumé
<2 à 3 lignes : l'essentiel de la réunion et son issue.>

## Points discutés
- <point 1>
- <point 2>

## Décisions
| Décision | Statut |
|---|---|
| <décision> | prise / à confirmer |

## Actions
| Action | Responsable | Échéance |
|---|---|---|
| <action> | <personne> | <date / à définir> |

## Points en suspens
- <question ouverte ou sujet reporté>

## Prochaine étape
<la suite immédiate : prochaine réunion, jalon, livrable attendu.>
```

**Ton** : la **voix Allia** — sobre, factuel, sans emphase commerciale. **Toute version rendue ou visuelle** (HTML, PDF, page) suit `contrats/socle/design-system.md` (on consomme le design system, on ne le recopie pas).

## 5. Crans (résolus via `table-des-crans.yaml`)

| Action | Cran | Note |
|---|---|---|
| **Produire le CR** (écrit en zone de proposition) | **auto** | réversible, interne, local — l'agent agit seul |
| **Envoi du CR au client par un humain collaborateur** | **libre** | hors crans — les crans gouvernent les agents, pas les humains (`organisation.md` §4 bis) |
| **Envoi du CR au client par l'agent** | **validé** | porte tenue par un **grade habilité** (`organisation.md` §4 bis) |
| **Réutiliser** le CR pour un autre client / **entrée au canon** | **porte anonymisation** | déclenchée par règle — voir §7 et `anonymisation.md` §1 |

## 6. Zone de proposition

Le CR est un **dérivé** : il s'écrit dans la **zone de proposition** (`modele-donnees.md` §3), jamais dans la source. Le dérivé n'est jamais le saisi. Sa promotion en vérité (rattachement à la mission dans M365) est une **étape tracée** : qui, quand, quoi. Tant qu'il n'est pas promu, le CR reste un candidat.

## 7. Anonymisation

Par défaut, un CR **reste nominatif** : tant qu'il circule **à l'intérieur de la firme** — même mission, même client, **ou réutilisé pour une autre mission / un autre client en interne** — **pas d'anonymisation** (c'est l'avantage qui compose, `anonymisation.md` §1 — inchangé). La porte se déclenche (déclencheur d'`anonymisation.md` §1, révisé le 12 juin 2026) :

- à la **communication grand public** (site, publication, communication institutionnelle) ;
- sur la **matière issue d'un client tiers**, anonymisée **avant insertion** dans un livrable destiné à un client (exigence NDA) — les données du client destinataire restent **nominatives** : un CR rendu au client pour ses propres données n'est **pas** anonymisé.

Dans ces cas, appliquer `anonymisation.md` (§1 déclencheur, §2 champs, §3 seuil, §4 transformation) **avant** tout usage. L'anonymisation est un préalable, pas un substitut aux portes du cran *validé* (`doctrine.md` §6).

## 8. Critères de qualité (Definition of Done)

- [ ] Chaque **décision** porte un **statut** (`prise` / `à confirmer`).
- [ ] Chaque **action** porte un **responsable** et une **échéance** (ou « à définir »).
- [ ] **Aucune information inventée** : fidélité stricte aux notes ; tout manque est marqué « à confirmer ».
- [ ] **Aucun identifiant client** si le CR est destiné au **canon** ou à l'**externe** (anonymisation appliquée, §7).
- [ ] **Format respecté** (en-tête, résumé, points discutés, tableaux Décisions et Actions, points en suspens, prochaine étape).
- [ ] Écrit en **zone de proposition** ; non mergé, non promu par l'agent.

## 9. Exemple minimal

**Entrée (notes brutes)**
```
Réu projet Atlas 12/03. Présents : Léa, Marc, client (DSI). 
Validé le périmètre phase 1. Budget pas tranché, à voir avec achats.
Marc envoie le planning vendredi. Prochain point le 26/03.
```

**Sortie (CR)**
```
# Compte rendu — Cadrage phase 1, projet Atlas

Date : 12/03 (année à confirmer)
Mission : projet Atlas (code mission à confirmer)
Participants : Léa, Marc, DSI client ; excusés : à confirmer

## Résumé
Réunion de cadrage de la phase 1. Le périmètre est validé ; le budget reste
à trancher avec les achats. Un planning est attendu en fin de semaine.

## Points discutés
- Périmètre de la phase 1
- Budget de la phase 1

## Décisions
| Décision | Statut |
|---|---|
| Périmètre de la phase 1 validé | prise |
| Budget de la phase 1 | à confirmer |

## Actions
| Action | Responsable | Échéance |
|---|---|---|
| Envoyer le planning | Marc | vendredi |
| Trancher le budget avec les achats | à définir | à définir |

## Points en suspens
- Arbitrage budgétaire avec le service achats

## Prochaine étape
Prochain point le 26/03.
```

## 10. Évolution

Ce skill est **promu** (procédure allégée, contrat à portée locale, `doctrine.md` §5). Toute évolution future suit la boucle de promotion (`doctrine.md` §7) avec **montée de version** en en-tête. Retour arrière = repointage.
