# Synthèse d'entretien — Skill

> **id** : `synthese-entretien`
> **Version** : 1.3 — *candidat*. **Nature** : skill.
> **Changelog** : v1.3 — candidat, 18 juin 2026 : §9 (exemple de sortie) — valeur du champ « Étape » alignée sur l'énumération (`entretien 1` → **E1**) ; clôt la non-conformité skill↔exemple relevée par l'agent-gardien (les mentions « entretien 2 » en prose, l.125/129/132, restent inchangées). v1.2 — promu via boucle de promotion, 18 juin 2026 : valeurs d'étape (§2 métadonnée, §4 bis format de sortie) basculées **E1 / E2 / E3** sur le substrat M365. v1.1 — promu via boucle de promotion, 18 juin 2026 : alignement des valeurs d'étape sur `recrutement-pipeline.md` / `modele-donnees.md` v1.13 — §2 (métadonnée « étape ») et §4 bis (ligne Étape du format de sortie) : valeurs = E1 / E2 / E3 (**drop « sourcing » et « proposition »** — les synthèses naissent aux étapes d'entretien). v1.0 — candidat, 17 juin 2026 : création. Sous-tâche `T-0013-c` de la chapeau `T-0013` (outil vue candidat & suivi d'entretiens). Produit une synthèse d'entretien structurée candidate, écrite en zone de proposition, exécutant la checklist en dur du cadre RGPD recrutement (`rgpd-recrutement-candidats.md` §4). Rubrique « recommandation » explicitement **non décisionnelle** (la décision de recrutement reste humaine — cadre §1).
> **Domicile** : `skills/synthese-entretien/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `contrats/socle/rgpd-recrutement-candidats.md` (§1 décision humaine, §3 minimisation, §4 checklist synthèse, §5 durées, §7 droit d'accès), `contrats/socle/modele-donnees.md` (entité « Synthèse d'entretien », liste « Candidats-Synthèses » ; §3 zone de proposition), `contrats/socle/anonymisation.md`, `contrats/socle/design-system.md`, `contrats/socle/table-des-crans.yaml`, `doctrine/doctrine.md` (§2, §6, §7), `CLAUDE.md`.

## 1. Objet

Transformer les **notes d'un entretien de recrutement** en une **synthèse structurée, fidèle et bornée** : un document court qui apprécie l'**adéquation au poste** du candidat, dégage les **points à creuser**, et porte une **recommandation non décisionnelle**. La synthèse est un fait **dérivé** (§6) ; elle sert l'instruction d'une candidature et, le cas échéant, le vivier — elle ne décide jamais à la place de l'humain (cadre §1).

> **Régime strict (cadre §4).** Une synthèse est une **appréciation** : c'est une donnée personnelle **accessible au candidat** au titre du droit d'accès (cadre §7). Sa rédaction est donc disciplinée par une **checklist en dur** (§4 ci-dessous). Les **notes brutes** d'entretien sont **éphémères** : ce skill produit la synthèse, il ne conserve jamais le verbatim.

## 2. Entrées

- **Matière** : notes prises pendant l'entretien (ou transcript).
- **Métadonnées** :
  - `candidat` — identifiant candidat (cf. `modele-donnees.md`, entité Candidat) ;
  - `poste` — poste visé ;
  - `étape` — E1 / E2 / E3 (cf. colonne étape ; les synthèses naissent aux étapes d'entretien) ;
  - `date` — date de l'entretien ;
  - `interviewer` — qui a mené l'entretien.

> **Règle de fidélité.** Si une métadonnée manque, la **marquer « à confirmer »** ; **ne jamais l'inventer**. Une appréciation non étayée par la matière n'a pas sa place dans la synthèse (§4, §8).

## 3. Procédure

1. **Lire** intégralement la matière.
2. **Rattacher** au candidat, au poste et à l'étape.
3. **Apprécier l'adéquation au poste** — compétences observées, séniorité, motivation, **uniquement** au regard du poste.
4. **Dégager les points à creuser** — questions ouvertes, zones à valider lors d'un prochain échange ou pour une future opportunité.
5. **Formuler une recommandation NON DÉCISIONNELLE** — une orientation (avancer / verser au vivier / ne pas retenir) **étayée** par les points précédents. C'est une **aide à la décision humaine**, jamais une décision : la décision de recrutement reste humaine (cadre §1).
6. **Passer la checklist §4** : retirer tout ce qui ne doit jamais y figurer.
7. **Rédiger** au format §4 bis, dans la voix Allia (sobre, factuel).

## 4. Checklist en dur — ce que la synthèse couvre / ne couvre jamais (cadre §4, figée)

**Elle couvre** : l'adéquation au poste — compétences observées, séniorité, motivation, points à creuser pour une future opportunité.

**Elle ne contient JAMAIS** :
- données sensibles (santé, origine, opinions, religion, orientation, situation familiale) ;
- éléments de vie privée sans lien avec le poste ;
- jugements de personnalité non étayés professionnellement ;
- toute appréciation qu'on ne voudrait pas relire au candidat exerçant son droit d'accès (cadre §7).

> Cette checklist **fait foi** (figée par `rgpd-recrutement-candidats.md` §4). En cas de doute sur un élément, **ne pas l'inclure**.

## 4 bis. Format de sortie

~~~
# Synthèse d'entretien — <candidat>, <poste>

Candidat : <id candidat | à confirmer>
Poste : <poste | à confirmer>
Étape : <E1 / E2 / E3 | à confirmer>
Date : <date | à confirmer>
Interviewer : <nom | à confirmer>

## Adéquation au poste
- Compétences observées : <…>
- Séniorité : <…>
- Motivation : <…>

## Points à creuser
- <question ouverte / zone à valider>

## Recommandation (non décisionnelle — aide à la décision humaine)
<Orientation étayée : avancer / verser au vivier / ne pas retenir. La décision
reste humaine ; cette ligne ne la remplace pas.>
~~~

**Ton** : voix Allia (sobre, factuel, sans jugement non étayé). Tout rendu visuel suit `contrats/socle/design-system.md` (on consomme, on ne recopie pas).

## 5. Crans (résolus via `table-des-crans.yaml`)

| Action | Cran | Note |
|---|---|---|
| **Produire la synthèse** (écrite en zone de proposition) | **auto** | réversible, interne, dérivé — l'agent agit seul |
| **Promouvoir une synthèse** vers la liste « Candidats-Synthèses » | **porte humaine** | promotion tracée — jamais l'agent (doctrine §7) |
| **Réutiliser / sortie grand public** | **porte anonymisation** | déclenchée par règle — voir §7 et `anonymisation.md` §1 |

## 6. Zone de proposition

La synthèse est un **dérivé** : elle s'écrit dans la **zone de proposition** (`modele-donnees.md` §3), jamais directement dans la liste « Candidats-Synthèses ». Elle ne rejoint son domicile candidat qu'à **validation** (promotion tracée). Le dérivé n'est jamais le saisi. Les **notes brutes** ne sont jamais écrites comme une entité : elles sont éphémères (cadre §4). Tant qu'elle n'est pas promue, la synthèse reste un candidat.

## 7. Anonymisation

Par défaut, une synthèse **reste nominative** : tant qu'elle circule **à l'intérieur de la firme** (instruction, vivier, destinataires en charge du poste), **pas d'anonymisation** (cadre §3, §8). La porte se déclenche (déclencheur d'`anonymisation.md` §1) à la **communication grand public** (ex. statistique de recrutement publiée, témoignage) : appliquer `anonymisation.md` (§1→§4) **avant** usage. La réutilisation interne ne déclenche rien.

## 8. Critères de qualité (Definition of Done)

- [ ] La synthèse apprécie l'**adéquation au poste** (compétences, séniorité, motivation), et rien hors poste.
- [ ] La **recommandation** est présente, **étayée**, et explicitement **non décisionnelle** (la décision reste humaine).
- [ ] **Checklist §4 respectée** : aucune donnée sensible, aucun élément de vie privée hors poste, aucun jugement non étayé.
- [ ] **Test du droit d'accès** : rien dans la synthèse qu'on ne voudrait pas relire au candidat l'exerçant (cadre §7).
- [ ] **Aucune information inventée** : fidélité stricte à la matière ; tout manque est « à confirmer ».
- [ ] **Notes brutes non conservées** : seule la synthèse subsiste.
- [ ] Écrite en **zone de proposition** ; non promue par l'agent.
- [ ] **Format respecté** ; rendu visuel conforme au design system.

## 9. Exemple minimal

**Entrée (notes brutes)**

~~~
Entretien 1 candidat C-014, poste Consultant. 12/06, interviewer Léa.
5 ans d'XP conseil, à l'aise sur le cadrage. Motivé par l'IA agentique.
À creuser : exposition au pilotage de mission. Plutôt favorable.
~~~

**Sortie (synthèse)**

~~~
# Synthèse d'entretien — C-014, Consultant

Candidat : C-014
Poste : Consultant
Étape : E1
Date : 12/06 (année à confirmer)
Interviewer : Léa

## Adéquation au poste
- Compétences observées : à l'aise sur le cadrage ; 5 ans d'expérience en conseil.
- Séniorité : cohérente avec le grade visé (à confirmer en entretien 2).
- Motivation : forte, orientée IA agentique.

## Points à creuser
- Exposition réelle au pilotage de mission (à valider en entretien 2).

## Recommandation (non décisionnelle — aide à la décision humaine)
Profil favorable à un passage en entretien 2. Orientation à confirmer par
l'interviewer ; cette synthèse ne décide pas.
~~~

## 10. Évolution

Ce skill est un **candidat** (procédure allégée, portée locale, `doctrine.md` §5). Sa promotion suit la boucle (`doctrine.md` §7) avec montée de version. Retour arrière = repointage.
