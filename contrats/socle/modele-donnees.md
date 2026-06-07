# Modèle de données — Allia Consulting

> **Version** : 1.2 — *candidat*. **Statut** : contrat socle — fait foi.
> **Domicile** : `contrats/socle/modele-donnees.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§2 et §8), `contrats/socle/organisation.md`.
> **Changelog** : v1.2 — §2 bis : distinction explicite nom d'affichage (« Allia Consulting ») vs identifiant d'URL (« alliaconsuling », conservé). Aucun domicile ni câblage modifié.
> v1.1 — câblage M365 réel (site AlliaConsuling : §2 bis) ; domiciles « à confirmer » → **partiellement câblé — session 7 juin 2026 ; écriture Graph = T-0002** ; ajout de l'entité **CVs** (donnée personnelle, RGPD). Les **emplacements** sont renseignés ; l'**écriture** via Graph Lists API reste à outiller (connecteur Graph MCP en écriture — `backlog/chantiers/T-0002.yaml`).
> C'est **la couture M365** : les agents résolvent ce contrat pour savoir où lire et écrire les faits. Si M365 change, seule l'implémentation derrière ce contrat change ; les consommateurs ne bougent pas.

## 0. Objet

Dire où vit chaque **fait** dans M365, et garantir que tout fait **dérivé** passe par une **zone de proposition** avant promotion. Les *règles* vivent dans le dépôt ; les *données* vivent ici, dans M365.

## 1. Principes

- **Source vs dérivé.** Un fait saisi est la source ; un fait calculé par un agent est un dérivé, écrit en zone de proposition, promu de façon tracée. Le dérivé n'est jamais le saisi.
- **Une seule vérité, un seul domicile** par entité.
- **Accès via MCP M365** ; l'identité des personnes est référencée par identifiant Entra (voir `organisation.md`).

## 2. Les entités (les faits)

| Entité | Description | Domicile M365 *(partiellement câblé — session 7 juin 2026 ; écriture Graph = T-0002)* | Identifiant stable | Nature |
|---|---|---|---|---|
| Mission | une affaire | Liste « Missions » | code mission | source |
| Temps | temps passé | Liste « Temps » | id saisie | source |
| Imputation | rattachement temps → mission | Liste « Imputations » | id | source / dérivé |
| Livrable | document produit | Bibliothèque « Livrables » | id document | source |
| Frais | frais de mission | Liste « Frais » | id | source |
| Compte / Client | référentiel des clients | Liste « Comptes » | id compte | source |
| CVs | CV d'une ressource | Bibliothèque « CVs » | nom du fichier | source · **données personnelles (RGPD)** |

## 2 bis. Domiciles M365 réels (partiellement câblé — session 7 juin 2026 ; écriture Graph = T-0002)

**Site SharePoint**
- Nom d'affichage : *Allia Consulting*
- Identifiant d'URL (figé à la création, conservé tel quel) : `https://alliaconsuling.sharepoint.com/sites/AlliaConsuling`

> L'identifiant d'URL « alliaconsuling » (sans « t ») est volontairement conservé : il résout correctement et un identifiant technique n'a pas vocation à être renommé. Le nom lisible du site est « Allia Consulting ». Ne pas confondre les deux ni « corriger » l'URL.

Tous les emplacements ci-dessous vivent sous ce site. Les agents les résolvent via MCP M365 ; aucune copie n'est faite dans le dépôt (les *données* vivent ici, les *règles* dans Git).

| Ressource M365 | Chemin | Accès agent | Notes |
|---|---|---|---|
| Liste « Missions » | site AlliaConsuling / Liste Missions | lecture/écriture selon cran | source des affaires |
| Liste « Temps » | site AlliaConsuling / Liste Temps | lecture/écriture selon cran | — |
| Liste « Imputations » | site AlliaConsuling / Liste Imputations | lecture/écriture selon cran | rattachement temps → mission |
| Liste « Frais » | site AlliaConsuling / Liste Frais | lecture/écriture selon cran | — |
| Liste « Comptes » | site AlliaConsuling / Liste Comptes | lecture/écriture selon cran | référentiel clients |
| Liste « Ressources-Profil » | site AlliaConsuling / Liste Ressources-Profil | **lecture** | profil de ressource (compétences, séniorité) |
| Liste « Ressources-RH » | site AlliaConsuling / Liste Ressources-RH | **accès restreint** | ⚠️ **journalisation à activer** — données RH sensibles |
| Liste « Zone-de-proposition » | site AlliaConsuling / Liste Zone-de-proposition | **écriture (dérivés)** | domicile concret de la zone de proposition (§3). **Écriture via Graph Lists API — nécessite le connecteur Graph MCP en écriture (voir `T-0002`).** En attendant : zone de proposition **simulée en local** (`zone-proposition/`). |
| Bibliothèque « Livrables » | site AlliaConsuling / Bibliothèque Livrables | lecture/écriture selon cran | documents produits |
| Bibliothèque « Propositions » | site AlliaConsuling / Bibliothèque Propositions | lecture/écriture selon cran | propositions commerciales |
| Bibliothèque « Capitalisation » | site AlliaConsuling / Bibliothèque Capitalisation | lecture/écriture selon cran | matière capitalisée (canon — porte anonymisation à la réutilisation inter-client) |
| Bibliothèque « CVs » | site AlliaConsuling / Bibliothèque CVs | **lecture** | ⚠️ **données personnelles (RGPD) — journalisation à activer** |

> **Garde-fous (runbook humain — hors agent).** Activer la **journalisation** sur `Ressources-RH` et `CVs` avant tout accès agent ; les droits M365 ne se règlent jamais à la main par un agent mais par réconciliation au moindre privilège d'une décision promue (`organisation.md` §5). La présence d'un domicile dans cette table ne vaut pas ouverture d'accès.

## 3. La zone de proposition

Un espace **distinct de la source** où les agents écrivent les faits dérivés — marge calculée, imputation proposée, template anonymisé. Domicile concret câblé : **Liste « Zone-de-proposition »** (§2 bis). La promotion déplace le fait vers la source, de façon tracée. **On n'écrit jamais un dérivé directement dans la source.**

## 4. État du câblage

Les domiciles concrets (site, listes, bibliothèques) sont **partiellement câblé — session 7 juin 2026 ; écriture Graph = T-0002** (voir §2 bis). Les **emplacements** sont renseignés (lecture documentée) ; l'**écriture** dans les listes — notamment `Zone-de-proposition` — requiert un connecteur **Graph MCP en écriture**, identifié comme chantier `T-0002`. En attendant, la zone de proposition est **simulée en local** (`zone-proposition/`).

Restent à confirmer par le gardien (runbook humain, hors agent) : l'activation de la **journalisation** sur `Ressources-RH` et `CVs`, et la projection des **droits d'accès** au moindre privilège (`organisation.md` §5). Aucun droit ne se règle à la main par un agent.
