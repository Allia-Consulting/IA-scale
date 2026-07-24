---
name: revue-de-pipe
description: >
  Revue hebdomadaire de santé du pipe commercial (Liste « CRM »). Produit un score de santé du
  pipe justifié ligne à ligne, une priorisation pondérée des opportunités, des drapeaux de risque
  et d'hygiène, la forme du pipe par étape (avec pipe pondéré cohérent avec le cockpit), et un plan
  d'action de 3 actions maximum pour la semaine. Déclencheurs : « revue de pipe », « santé du
  pipe », « où en est le pipe commercial », « quelles opportunités prioriser cette semaine »,
  « fais le point sur les opportunités CRM ». Lecture seule ; aucune écriture source.
argument-hint: "[pondérations ajustées | semaine cible] (optionnel)"
---

# Revue de pipe commercial — Skill

> **id** : `revue-de-pipe`
> **Version** : 1.0 — *candidat*. **Nature** : skill.
> **Changelog** : v1.0 — candidat, 24 juillet 2026 (T-0035/1d, pillage `sales/pipeline-review` Apache-2.0) : création. Revue hebdomadaire de santé du pipe commercial (Liste « CRM ») : score de santé justifié ligne à ligne, priorisation pondérée (échéance / montant / étape, pondérations explicites et ajustables), drapeaux de risque et d'hygiène, forme du pipe par étape avec pipe pondéré cohérent avec le cockpit (Qualification 15 %, Proposition 60 %), plan d'action de 3 actions maximum. Gabarit `anthropics/knowledge-work-plugins → sales/pipeline-review` (Apache-2.0) **adapté** au substrat Allia — jamais adopté tel quel (voir §12). Lecture seule ; aucune écriture source ; les dérivés éventuels passent par la Zone-de-proposition.
> **Domicile** : `skills/revue-de-pipe/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `contrats/socle/modele-donnees.md` (§2 / §2 bis — entité Opportunité, schéma RÉEL de la Liste « CRM » ; règle d'écriture : dérivés via Zone-de-proposition uniquement, exception `CodeMission` réservée au serveur), `contrats/socle/tour-de-controle.md` (§3 — bandeau « Pipe commercial », pondérations figées), `contrats/socle/table-des-crans.yaml` (`list_items` = lecture auto ; `ecrire_fait_derive_zone_proposition` = auto), `contrats/socle/anonymisation.md` (§1 — usage interne nominatif), `docs/veille/2026-07-20--assets-accelerateurs.md` (provenance du pillage), `CLAUDE.md`.

## 1. Objet

D'une lecture de la **Liste « CRM »**, produire une **revue de pipe commercial** hebdomadaire, **sobre et justifiée** : un **score de santé du pipe** dont chaque note est adossée aux lignes qui la causent (jamais un score décoratif), une **priorisation pondérée** des opportunités actives, des **drapeaux de risque et d'hygiène**, la **forme du pipe par étape** (montants € HT, pipe pondéré cohérent avec le cockpit) et un **plan d'action de 3 actions maximum** pour la semaine — à trancher par le gardien.

> **Thèse.** La revue **lit et éclaire** ; elle ne corrige rien. Toute correction est soit un **geste humain au cockpit**, soit un **dérivé en Zone-de-proposition** promu ensuite — jamais une écriture directe de l'agent dans la source CRM.

## 2. Entrées

| Donnée | Source | Usage |
|---|---|---|
| Opportunités | **Liste « CRM »**, lue via `list_items(list_id = "CRM")` (lecture seule, cran auto) | matière de la revue |
| Comptes (facultatif) | Liste « Comptes » via `list_items` | rattachement lisible (`Compte` = lookup) |
| Pondérations | valeurs par défaut (§4), **ajustables à la demande du gardien** en argument | scoring et priorisation |
| Semaine cible | argument facultatif (défaut : semaine courante) | horizon du plan d'action |

**Schéma RÉEL de la Liste « CRM » consommé** (colonnes de `modele-donnees.md` §2 bis — ne JAMAIS référencer une colonne absente) : `Title` (id stable `O-NNN`), `NomOpportunite`, `Compte` (lookup), `Etape` (Qualification / Proposition / Gagnée / Perdue), `Montant` (€ HT), `Echeance` (date), `Responsable`, `CodeMission` (entier, renseigné à « Gagnée »). Métadonnée native `lastModifiedDateTime` de l'élément SharePoint = signal **indicatif** de fraîcheur (jamais autoritaire : le contenu fait foi, pas l'horodatage — `modele-donnees.md` §5.6).

**Dimensions du gabarit `sales/pipeline-review` SANS colonne au schéma Allia → ABANDONNÉES (on n'invente pas de donnée)** : « last activity / next step » dédiée, « nombre de contacts / multi-threading », « stage age » (aucune date d'entrée d'étape au schéma). Elles ne sont **pas** scorées ; leur absence est signalée comme telle si le gardien la questionne, jamais comblée par une valeur inventée.

## 3. Score de santé du pipe (dimensions notées — schéma-supportées uniquement)

Chaque dimension est notée **de 0 à 100** et **justifiée par les lignes qui la causent** (numéro d'opportunité). Le score global est la moyenne pondérée des dimensions retenues ; **aucune note sans justification**.

| Dimension | Ce qu'elle mesure (colonnes réelles) | Poids défaut |
|---|---|---|
| **Complétude / hygiène** | proportion d'opportunités actives sans trou : `Title` (`O-NNN`) présent, `Montant` renseigné, `Echeance` renseignée, `Compte` rattaché, `Responsable` présent | 0,30 |
| **Cohérence d'étape** | `Etape` ∈ {Qualification, Proposition, Gagnée, Perdue} ; **Gagnée ⇒ `CodeMission` renseigné** (couture fermée) ; pas de Gagnée/Perdue laissée dans le pipe actif | 0,30 |
| **Échéances** | part des opportunités actives dont l'`Echeance` n'est **pas dépassée** (échéance passée sur une opportunité non close = risque) | 0,25 |
| **Fraîcheur** *(indicative)* | ancienneté du `lastModifiedDateTime` natif ; signal **faible**, sauté si la lecture ne l'expose pas — **on n'invente pas de donnée** | 0,15 |

Les poids sont **explicites et ajustables** à la demande du gardien. Une dimension dont aucune donnée n'est disponible **SAUTE** (renormalisation des poids restants) plutôt que d'être notée à l'aveugle.

## 4. Priorisation pondérée des opportunités

Score de priorité par opportunité **active** (Qualification / Proposition), **transparent et ajustable** :

`priorité = w_montant · (Montant normalisé) + w_échéance · (proximité d'échéance) + w_étape · (poids d'étape)`

- **Pondérations par défaut** : `w_montant = 0,45`, `w_échéance = 0,35`, `w_étape = 0,20` — **ajustables à la demande du gardien**.
- **Poids d'étape** (cohérents avec le pipe pondéré du cockpit, §6) : Qualification 0,15 · Proposition 0,60.
- **Proximité d'échéance** : plus l'`Echeance` est proche (ou dépassée), plus la priorité monte.
- Sortie : opportunités **classées**, chacune avec la ou les lignes qui motivent son rang (jamais un rang décoratif).

## 5. Drapeaux de risque et d'hygiène

Signalés explicitement, un drapeau = une ou plusieurs opportunités nommées :

- **Étape figée / dormante** *(indicatif)* : opportunité active dont le `lastModifiedDateTime` est ancien — signal faible, à confirmer par le gardien (pas de date d'entrée d'étape au schéma).
- **Échéance dépassée** : `Echeance` < aujourd'hui sur une opportunité non close (Qualification / Proposition).
- **Donnée manquante (hygiène)** : `Title` vide (identifiant `O-NNN` non posé — défaut connu du geste cockpit « nouvelle opportunité »), `Montant` absent, `Echeance` absente, `Compte` non rattaché, `Responsable` absent.
- **Couture non fermée** : `Etape = Gagnée` sans `CodeMission` (la mission n'a pas été ouverte / le code n'a pas été alloué).
- **Scorie d'épreuve / de test** : opportunité manifestement non commerciale (libellé d'épreuve, compte de démonstration) — **flaguée comme telle et EXCLUE du pipe**, jamais comptée dans les montants.

## 6. Forme du pipe (par étape)

- **Répartition par `Etape`** : Qualification / Proposition / Gagnée / Perdue — nombre d'opportunités et **somme des `Montant` € HT** par étape.
- **Pipe pondéré** : `Σ (Montant × poids d'étape)` avec les **pondérations figées du cockpit** (`tour-de-controle.md` §3) : **Qualification 15 %**, **Proposition 60 %** ; Gagnée = réalisé (100 %), Perdue exclue (0 %). Le résultat doit être **cohérent avec le bandeau « Pipe commercial »** du cockpit.
- Absence de donnée affichée « · », **jamais un zéro inventé** (sobriété du design system).

## 7. Plan d'action hebdomadaire

- **3 actions maximum**, concrètes, chacune rattachée à une opportunité ou à un drapeau du §5.
- Cadence **hebdomadaire** (une revue par semaine).
- Les actions sont **proposées** — elles sont **tranchées par le gardien** ; le skill n'en exécute aucune.

## 8. Déroulé et portes

1. **Lire** la Liste « CRM » via `list_items(list_id = "CRM")` (et « Comptes » si besoin de libellés) — cran **auto**, lecture seule.
2. **Écarter** les scories d'épreuve / test (les flaguer au §5, ne pas les compter).
3. **Noter** les dimensions de santé (§3), **prioriser** (§4), **lever les drapeaux** (§5), **dresser la forme du pipe** (§6) — chaque note et chaque rang justifiés par leurs lignes.
4. **Livrer** la revue au gardien (score, priorités, drapeaux, forme, plan de 3 actions max). C'est le livrable ; **aucune écriture** n'accompagne la revue.
5. **Si** une correction dérivée est utile (ex. proposition d'étape / montant recalculé) : l'écrire en **Zone-de-proposition** via `create_list_item` (cran auto), promotion tracée ultérieure — **jamais** dans la source CRM.

## 9. Crans (résolus via `table-des-crans.yaml`)

| Action | Cran | Fondement |
|---|---|---|
| Lire la Liste « CRM » / « Comptes » | **auto** | `list_items` — lecture réversible, interne, locale |
| Produire et livrer la revue | **auto** | analyse en session, aucun effet de bord |
| Écrire un dérivé (proposition de correction) | **auto** | `ecrire_fait_derive_zone_proposition` — Zone-de-proposition uniquement |
| Corriger une opportunité dans la source CRM | **HORS PÉRIMÈTRE** | geste humain au cockpit, ou promotion tracée ; l'exception `CodeMission` est réservée au serveur (`allouer_code_mission`, `modele-donnees.md` §2 bis) |

## 10. Garde-fous inscrits dans ce skill

- **ZÉRO écriture pendant la revue** : la revue est une **lecture** ; elle ne modifie aucune opportunité. Toute correction est un **geste humain au cockpit** ou un **dérivé en Zone-de-proposition** (`create_list_item`) — **jamais** une écriture directe dans la source CRM.
- **On n'invente pas de donnée** : une dimension sans colonne au schéma RÉEL de la Liste « CRM » est **abandonnée**, pas comblée ; une note sans ligne justificative n'est pas posée.
- **Cohérence cockpit** : le pipe pondéré reprend les pondérations figées de `tour-de-controle.md` §3 (Qualification 15 %, Proposition 60 %).
- **Voix Allia sobre** : pas de score décoratif ; chaque note et chaque priorité citent les opportunités qui les causent.
- **Aucune donnée personnelle** : la Liste « CRM » n'en porte pas (`modele-donnees.md` §2 bis) ; la revue reste un usage **interne nominatif** (pas de porte d'anonymisation ici — `anonymisation.md` §1).

## 11. Ce que ce skill ne fait pas

- Il ne **modifie** aucune opportunité (étape, montant, échéance) dans la source CRM.
- Il ne **crée** ni n'ouvre de mission (c'est `cadrage-mission` / `allouer_code_mission`).
- Il n'**envoie** rien au client et ne publie rien.
- Il ne **supprime** aucune scorie d'épreuve (il la **flague** ; la purge est un geste gardien — la suppression définitive est proscrite à l'agent).
- Il n'**invente** aucune dimension absente du schéma réel.

## 12. Provenance et licence

Gabarit **pillé** : `anthropics/knowledge-work-plugins` → `sales/pipeline-review` (licence **Apache-2.0**). **Adapté** au substrat Allia (SharePoint / Liste « CRM », outils MCP Graph, crans, voix sobre), jamais adopté tel quel : les dimensions sans colonne au schéma réel ont été **retirées** (§2), et les écritures du gabarit d'origine sont remplacées par la règle Allia « lecture seule + dérivés en Zone-de-proposition ». Provenance consignée dans `docs/veille/2026-07-20--assets-accelerateurs.md` (gisement de pillage n°1 du screening).

## 13. Évolution

Ce skill est **candidat**. Son évolution suit la boucle (`doctrine.md` §7) : candidat → avis d'impact → promotion gardien (procédure allégée), montée de version en en-tête, corps byte-identique à la promotion. Enregistré au **harnais d'évals** (`evals/skills/revue-de-pipe/golden.yaml`) comme les autres skills. Retour arrière = repointage.
