# Purge des données de recrutement — Skill

> **id** : `purge-recrutement`
> **Version** : 1.0 — *candidat*. **Nature** : skill.
> **Changelog** : v1.0 — candidat, 19 juin 2026 : création. Sous-tâche `T-0013-d` de la chapeau `T-0013` (outil vue candidat & suivi d'entretiens). Décrit le mécanisme de purge gouvernée des données de recrutement échues, au moindre privilège, appliquant la règle de rétention promue (`rgpd-recrutement-candidats.md` §5, v1.4). Le code d'exécution et le runbook du privilège sont des livrables distincts, construits après promotion de ce skill.
> **Domicile** : `skills/purge-recrutement/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `contrats/socle/rgpd-recrutement-candidats.md` (§5 durées, §7 opposition), `contrats/socle/modele-donnees.md` (entité Candidat, colonne native « Créé le », liste « Candidats »), `contrats/socle/table-des-crans.yaml` (exception gouvernée `supprimer_definitivement_des_donnees`, v1.7), `doctrine/doctrine.md` (§2, §6), `CLAUDE.md`.

## 1. Objet

Purger automatiquement les fiches candidat dont la durée de rétention au vivier est échue — **refusé depuis plus de 2 ans à compter de la date d'inscription** (colonne native « Créé le ») — en appliquant la règle de rétention **déjà promue** au canon (`rgpd-recrutement-candidats.md` §5). Ce skill est un **mécanisme gouverné au moindre privilège** : il ne sait que purger selon cette règle, il ne supprime jamais librement.

> **Distinction fondamentale.** Ce mécanisme **applique une décision promue** — il ne la prend pas. La durée de 2 ans est inscrite au canon (`rgpd-recrutement-candidats.md` §5) et à la `table-des-crans.yaml` (exception gouvernée, v1.7) ; le mécanisme en est l'exécutant tracé, sur le modèle de la réconciliation de droits (`organisation.md` §5). Toute modification de la durée passe par la boucle de promotion, jamais par ce code.

## 2. Règle de purge (promue — ne pas modifier ici)

La règle est inscrite dans `rgpd-recrutement-candidats.md` §5 et fait foi :

- **Cible** : fiches de la liste « Candidats » dont `Etape = Refusée` ET `Créé le < aujourd'hui − 2 ans`.
- **Horloge** : la colonne **native `Créé le`** (date d'inscription de la fiche) — fixe, non glissante. Ni un recontact, ni une consultation, ni un échange ne la prolongent.
- **Sauf opposition** : une fiche portant un marqueur d'opposition active (`OppositionVivier = true`) est **exclue de la purge** — l'opposition du candidat (cadre §7) est un garde-fou incontournable.
- **Nouvelle candidature** : une nouvelle candidature ultérieure ouvre une **fiche neuve** avec sa propre horloge. On ne prolonge jamais une fiche existante.
- **Action** : suppression définitive de la fiche et de la synthèse d'entretien rattachée (liste « Candidats-Synthèses »), ou anonymisation irréversible — au choix du gardien au moment de la mise en service (les deux sont conformes ; la suppression est plus simple).

## 3. Procédure d'exécution

1. **Lire** la liste « Candidats » via `list_items` (MCP Graph) : récupérer toutes les fiches dont `Etape = Refusée`.
2. **Filtrer** : conserver uniquement celles dont `Créé le < aujourd'hui − 730 jours` (2 ans).
3. **Exclure** : retirer les fiches dont `OppositionVivier = true` (opposition active du candidat).
4. **Journaliser** : pour chaque fiche à purger, écrire une entrée de traçabilité en **Zone-de-proposition** (`create_list_item`) avant toute suppression — `Title` = `PURGE-<id candidat>-<date>`, `Origine` = `purge-recrutement`, `Contenu` = résumé de la fiche (id, étape, date d'inscription, motif de purge). Ce log est le **journal de l'action** ; il ne contient pas de données personnelles superflues.
5. **Supprimer** (ou anonymiser) : via le **privilège dédié du mécanisme** (identité managée distincte à moindre privilège, posée par runbook humain — §5). Ce skill **ne supprime jamais avec le connecteur MCP Graph général** (`id-allia-mcp-graph`) : ce connecteur est en écriture `Zone-de-proposition` uniquement (garde-fou structurel, `server.py`). La suppression Graph est une **opération distincte**, sous une identité dédiée.
6. **Signaler** : produire un rapport de purge en Zone-de-proposition (`create_list_item`, `Origine = purge-recrutement-rapport`) : nombre de fiches traitées, ids purgés, date d'exécution, synthèses rattachées supprimées.

## 4. Crans (résolus via `table-des-crans.yaml`)

| Action | Cran | Fondement |
|---|---|---|
| **Lire** la liste « Candidats » (filtre Refusée) | **auto** | lecture réversible, interne, local |
| **Journaliser** en Zone-de-proposition | **auto** | dérivé réversible, interne — `ecrire_fait_derive_zone_proposition` |
| **Supprimer** les fiches échues | **exception gouvernée** | `table-des-crans.yaml` v1.7 — purge des données de recrutement échues, mécanisme gouverné au moindre privilège appliquant la durée promue (rgpd §5) ; hors de cette exception, `supprimer_definitivement_des_donnees` reste proscrit |
| **Mise en place du privilège** du mécanisme (identité/droits) | **runbook humain — proscrit à l'agent** | `table-des-crans.yaml` : `modifier_droits_permissions_ou_protection_de_branche` |

## 5. Garde-fous inscrits dans ce skill

- **Jamais de suppression libre** : le mécanisme ne supprime que les fiches correspondant **exactement** à la règle promue (Refusée + Créé le > 2 ans + pas d'opposition). Toute déviation est une non-conformité.
- **Opposition inviolable** : `OppositionVivier = true` exclut définitivement la fiche de la purge, quelle que soit la date. Le droit d'opposition du candidat (cadre §7) prime.
- **Journal avant suppression** : l'entrée de traçabilité en Zone-de-proposition précède toute suppression — si le journal échoue, la suppression n'a pas lieu.
- **Identité dédiée au moindre privilège** : la suppression Graph n'est jamais exécutée avec une identité ayant d'autres droits. L'identité du mécanisme de purge est distincte de `id-allia-mcp-graph` ; sa création et ses droits sont un runbook humain (§5 ci-dessous).
- **Pas d'accès aux synthèses-sources** : le mécanisme ne lit que ce dont il a besoin — liste « Candidats » (filtre Refusée + date). Les synthèses d'entretien rattachées sont supprimées par cascade (lookup Synthèse→Candidat) ou par une requête ciblée sur l'id candidat — jamais par lecture en masse de « Candidats-Synthèses ».
- **Rapport systématique** : chaque exécution se clôt par un rapport en Zone-de-proposition, qu'il y ait eu des purges ou non (rapport « 0 fiche éligible » compris).

## 6. Prérequis avant mise en service (runbooks humains — hors de ce skill)

Ce skill **ne peut pas être mis en service** tant que les prérequis suivants ne sont pas posés par le gardien :

1. **Colonne `OppositionVivier`** : ajouter la colonne booléenne `OppositionVivier` à la liste « Candidats » (nom interne ASCII, puis libellé renommé), défaut `false`. Runbook humain — modification de schéma M365.
2. **Identité managée dédiée à la purge** : créer une identité managée distincte de `id-allia-mcp-graph`, avec le seul droit de **suppression** (`DELETE /items/{id}`) sur la liste « Candidats » du site AlliaConsuling — `Sites.Selected` limité, octroi minimal. Runbook humain.
3. **Promotion de ce skill** : ce candidat doit être promu par le gardien avant toute exécution.
4. **Journalisation active** sur la liste « Candidats » (T-0003) — prérequis déjà posé pour tout accès agent aux données candidat.

## 7. Ce que ce skill ne fait pas

- Il **ne collecte pas** de données candidat au-delà du filtre de purge.
- Il **ne modifie pas** une fiche existante (pas de mise à jour d'étape, pas d'ajout de colonne).
- Il **ne décide pas** de la durée de rétention — elle est inscrite au canon.
- Il **ne purge pas** les fiches en cours d'instruction (étape ≠ Refusée), les fiches Acceptées, ni les fiches dont l'opposition est active.
- Il **ne communique pas** à l'extérieur de la firme — la sortie est le journal en Zone-de-proposition, interne.

## 8. Critères de qualité (Definition of Done)

- [ ] La règle de filtre est exacte : `Etape = Refusée` ET `Créé le < aujourd'hui − 730 jours` ET `OppositionVivier ≠ true`.
- [ ] Le journal de traçabilité est écrit en Zone-de-proposition **avant** toute suppression.
- [ ] L'opposition active exclut la fiche sans exception.
- [ ] La suppression est exécutée sous une **identité dédiée au moindre privilège**, distincte de `id-allia-mcp-graph`.
- [ ] Un rapport de fin d'exécution est produit en Zone-de-proposition, même si aucune fiche n'est éligible.
- [ ] Aucune donnée personnelle superflue n'est lue, stockée ou transmise au-delà du besoin de la purge.

## 9. Évolution

Ce skill est un **candidat** (procédure allégée, portée locale, `doctrine.md` §5). Sa promotion suit la boucle (`doctrine.md` §7) avec montée de version. Retour arrière = repointage. Les runbooks de mise en service (§6) sont des livrables distincts, séquencés après promotion.
