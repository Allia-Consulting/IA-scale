# Modèle de données — Allia Consulting

> **Version** : 1.0 — *candidat*. **Statut** : contrat socle — fait foi.
> **Domicile** : `contrats/socle/modele-donnees.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§2 et §8), `contrats/socle/organisation.md`.
> C'est **la couture M365** : les agents résolvent ce contrat pour savoir où lire et écrire les faits. Si M365 change, seule l'implémentation derrière ce contrat change ; les consommateurs ne bougent pas.

## 0. Objet

Dire où vit chaque **fait** dans M365, et garantir que tout fait **dérivé** passe par une **zone de proposition** avant promotion. Les *règles* vivent dans le dépôt ; les *données* vivent ici, dans M365.

## 1. Principes

- **Source vs dérivé.** Un fait saisi est la source ; un fait calculé par un agent est un dérivé, écrit en zone de proposition, promu de façon tracée. Le dérivé n'est jamais le saisi.
- **Une seule vérité, un seul domicile** par entité.
- **Accès via MCP M365** ; l'identité des personnes est référencée par identifiant Entra (voir `organisation.md`).

## 2. Les entités (les faits)

| Entité | Description | Domicile M365 *(à câbler au bloc 6)* | Identifiant stable | Nature |
|---|---|---|---|---|
| Mission | une affaire | site / liste « Missions » | code mission | source |
| Temps | temps passé | liste « Temps » | id saisie | source |
| Imputation | rattachement temps → mission | liste « Imputations » | id | source / dérivé |
| Livrable | document produit | bibliothèque de la mission | id document | source |
| Frais | frais de mission | liste « Frais » | id | source |
| Compte / Client | référentiel des clients | liste « Comptes » | id compte | source |

## 3. La zone de proposition

Un espace **distinct de la source** (liste, bibliothèque ou dossier dédié) où les agents écrivent les faits dérivés — marge calculée, imputation proposée, template anonymisé. La promotion déplace le fait vers la source, de façon tracée. **On n'écrit jamais un dérivé directement dans la source.**

## 4. Décisions du gardien à confirmer (au bloc 6)

Les domiciles concrets (noms réels de sites, listes, bibliothèques) seront **câblés quand on connectera M365** (bloc 6). Aujourd'hui, le modèle est *logique* ; les emplacements réels restent « à confirmer ». Le moment venu, je pourrai explorer ta structure SharePoint pour pré-remplir cette table — avec ton accord.
