# Modèle de données — Allia Consulting

> **Version** : 1.7 — *promu*. **Statut** : contrat socle — fait foi.
> **Domicile** : `contrats/socle/modele-donnees.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§2 et §8), `contrats/socle/organisation.md`.
> **Changelog** : v1.7 — état de câblage de la zone de proposition, 10 juin 2026 (runbook `T-0002b-3`) : la liste « Zone-de-proposition » **existe désormais au tenant** (créée le 10 juin 2026 par le gardien, colonne texte « Origine » = champ d'origine, §2 bis/§3) ; la zone n'est plus « simulée en local » *faute de liste* — la simulation locale (`zone-proposition/`) reste le domicile **transitoire** des dérivés tant que l'**écriture réelle** via le connecteur n'est pas prouvée (fin de la chapeau `T-0002b` : entrée Easy Auth `T-0002b-4`, principe appelant `T-0002b-5`). **Aucun changement de règle, aucun changement de domicile.** v1.6 — promu via boucle de promotion, 8 juin 2026 (session doctrine) : §2 bis — ajout du **champ d'origine « mémoire hebdo »** sur la liste « Zone-de-proposition », qui marque les éléments produits par le batch nocturne de **mémoire d'organisation** (synthèse hebdomadaire candidate) et les distingue des autres faits dérivés ; en attendant T-0002b, ces éléments sont simulés en local sous `zone-proposition/memoire/`. Renvoi normatif vers le contrat socle (candidat) `contrats/socle/memoire-organisation.md`. Aucun autre domicile ni câblage modifié. v1.5 — repointage des renvois après le découpage (PR #23) du chantier d'écriture Graph en **T-0002a** (runbook Entra, promu) et **T-0002b** (déploiement / écriture réelle), 7 juin 2026 : toutes les mentions du chantier d'écriture (§2, §2 bis, §3, §4 et changelog v1.1) pointent désormais vers **T-0002b**. Aucun domicile ni câblage modifié. v1.4 — alignement sur le déclencheur d'anonymisation corrigé (`anonymisation.md` v1.3), 7 juin 2026 : la note de la bibliothèque « Capitalisation » (§2 bis) ne dit plus « porte anonymisation à la réutilisation inter-client » ; le canon interne reste **nominatif**, la porte joue à la **sortie externe**. Aucun domicile ni câblage modifié. v1.3 — promu via boucle de promotion (contenu inchangé ; état « partiellement câblé » du §2 bis/§4 inchangé). v1.2 — §2 bis : distinction explicite nom d'affichage (« Allia Consulting ») vs identifiant d'URL (« alliaconsuling », conservé). Aucun domicile ni câblage modifié.
> v1.1 — câblage M365 réel (site AlliaConsuling : §2 bis) ; domiciles « à confirmer » → **partiellement câblé — session 7 juin 2026 ; écriture Graph = T-0002b** ; ajout de l'entité **CVs** (donnée personnelle, RGPD). Les **emplacements** sont renseignés ; l'**écriture** via Graph Lists API reste à outiller (connecteur Graph MCP en écriture — `backlog/chantiers/T-0002b.yaml`).
> C'est **la couture M365** : les agents résolvent ce contrat pour savoir où lire et écrire les faits. Si M365 change, seule l'implémentation derrière ce contrat change ; les consommateurs ne bougent pas.

## 0. Objet

Dire où vit chaque **fait** dans M365, et garantir que tout fait **dérivé** passe par une **zone de proposition** avant promotion. Les *règles* vivent dans le dépôt ; les *données* vivent ici, dans M365.

## 1. Principes

- **Source vs dérivé.** Un fait saisi est la source ; un fait calculé par un agent est un dérivé, écrit en zone de proposition, promu de façon tracée. Le dérivé n'est jamais le saisi.
- **Une seule vérité, un seul domicile** par entité.
- **Accès via MCP M365** ; l'identité des personnes est référencée par identifiant Entra (voir `organisation.md`).

## 2. Les entités (les faits)

| Entité | Description | Domicile M365 *(partiellement câblé — session 7 juin 2026 ; écriture Graph = T-0002b)* | Identifiant stable | Nature |
|---|---|---|---|---|
| Mission | une affaire | Liste « Missions » | code mission | source |
| Temps | temps passé | Liste « Temps » | id saisie | source |
| Imputation | rattachement temps → mission | Liste « Imputations » | id | source / dérivé |
| Livrable | document produit | Bibliothèque « Livrables » | id document | source |
| Frais | frais de mission | Liste « Frais » | id | source |
| Compte / Client | référentiel des clients | Liste « Comptes » | id compte | source |
| CVs | CV d'une ressource | Bibliothèque « CVs » | nom du fichier | source · **données personnelles (RGPD)** |

## 2 bis. Domiciles M365 réels (partiellement câblé — session 7 juin 2026 ; écriture Graph = T-0002b)

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
| Liste « Zone-de-proposition » | site AlliaConsuling / Liste Zone-de-proposition | **écriture (dérivés)** | domicile concret de la zone de proposition (§3). **Liste créée au tenant le 10 juin 2026** (runbook `T-0002b-3` ; colonne texte « Origine » posée). Porte un **champ d'origine** qui qualifie chaque dérivé ; valeur **« mémoire hebdo »** = synthèse produite par le batch nocturne de **mémoire d'organisation** (contrat socle candidat `contrats/socle/memoire-organisation.md`), à valider ligne à ligne le vendredi. **Écriture via Graph Lists API — connecteur Graph MCP déployé ; l'écriture réelle reste conditionnée à la fin de la chapeau `T-0002b` (b-4/b-5).** En attendant : les dérivés restent **simulés en local** (`zone-proposition/` ; les synthèses « mémoire hebdo » sous `zone-proposition/memoire/`). |
| Bibliothèque « Livrables » | site AlliaConsuling / Bibliothèque Livrables | lecture/écriture selon cran | documents produits |
| Bibliothèque « Propositions » | site AlliaConsuling / Bibliothèque Propositions | lecture/écriture selon cran | propositions commerciales |
| Bibliothèque « Capitalisation » | site AlliaConsuling / Bibliothèque Capitalisation | lecture/écriture selon cran | matière capitalisée (canon interne — reste nominative ; la porte d'anonymisation joue à la **sortie externe** : publication / livrable hors firme, voir `anonymisation.md` §1) |
| Bibliothèque « CVs » | site AlliaConsuling / Bibliothèque CVs | **lecture** | ⚠️ **données personnelles (RGPD) — journalisation à activer** |

> **Garde-fous (runbook humain — hors agent).** Activer la **journalisation** sur `Ressources-RH` et `CVs` avant tout accès agent ; les droits M365 ne se règlent jamais à la main par un agent mais par réconciliation au moindre privilège d'une décision promue (`organisation.md` §5). La présence d'un domicile dans cette table ne vaut pas ouverture d'accès.

## 3. La zone de proposition

Un espace **distinct de la source** où les agents écrivent les faits dérivés — marge calculée, imputation proposée, template anonymisé. Domicile concret câblé : **Liste « Zone-de-proposition »** (§2 bis). La promotion déplace le fait vers la source, de façon tracée. **On n'écrit jamais un dérivé directement dans la source.**

Un **champ d'origine** qualifie la provenance de chaque dérivé. La valeur **« mémoire hebdo »** est réservée aux synthèses hebdomadaires candidates produites par le batch de **mémoire d'organisation** (`contrats/socle/memoire-organisation.md`, candidat) : domicile transitoire de cette mémoire en attendant T-0002b, validées ligne à ligne le vendredi (non-validé = oublié). La Liste « Zone-de-proposition » **existe au tenant depuis le 10 juin 2026** (champ d'origine posé — colonne « Origine ») ; les dérivés restent **simulés en local** tant que la chapeau `T-0002b` n'est pas soldée (écriture réelle via le connecteur — b-4/b-5) ; les synthèses « mémoire hebdo » vivent sous `zone-proposition/memoire/` d'ici là.

## 4. État du câblage

Les domiciles concrets (site, listes, bibliothèques) sont **partiellement câblé — sessions des 7 et 10 juin 2026 ; écriture Graph = T-0002b** (voir §2 bis). Les **emplacements** sont renseignés (lecture documentée) et la Liste « Zone-de-proposition » **existe au tenant** (créée le 10 juin 2026, runbook `T-0002b-3`). Le connecteur **Graph MCP en écriture** est **déployé** (`T-0002b-1..3` promus) ; l'**écriture réelle** dans les listes reste conditionnée à la fin de la chapeau `T-0002b` (entrée Easy Auth `T-0002b-4`, principe appelant `T-0002b-5`). En attendant, les dérivés restent **simulés en local** (`zone-proposition/`).

Restent à confirmer par le gardien (runbook humain, hors agent) : l'activation de la **journalisation** sur `Ressources-RH` et `CVs`, et la projection des **droits d'accès** au moindre privilège (`organisation.md` §5). Aucun droit ne se règle à la main par un agent.
