---
# Cadrage de mission — Skill

> **id** : `cadrage-mission`
> **Version** : 1.1 — *promu*. **Nature** : skill.
> **Changelog** : v1.1 — promu, 2 juillet 2026 : corps aligné post-promotion (§9 statut candidat → promu). v1.0 — promu, 2 juillet 2026 : promotion par le gardien (procédure allégée), chantier `T-0021`. v1.0 — candidat, 2 juillet 2026 : création (chantier `T-0021`, première marche de la tranche verticale métier, plan §6 T-1.1). Décrit le skill qui, d'une PROPOSITION GAGNÉE, produit un BRIEF DE MISSION-REGRESSION-TEST structuré, validé par l'utilisateur (« le brief suffit »), écrit en Zone-de-proposition via `create_list_item` ; la création réelle de l'espace de mission (cran auto) s'appuie sur l'outillage du chantier `T-0024`.
> **Domicile** : `skills/cadrage-mission/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `contrats/socle/modele-donnees.md` (§2 / §2 bis / §3 — entités Mission, Imputation, Compte ; Bibliothèques Propositions et Livrables ; Zone-de-proposition Title/Origine/Contenu), `contrats/socle/design-system.md` (templates consommés par référence), `contrats/socle/table-des-crans.yaml` (`creer_espace_mission` = **auto** ; `ecrire_fait_derive_zone_proposition` = **auto** ; `notifier_equipe` = **notifié** ; `merger_sur_main` / promotion = **gardien**), `contrats/socle/anonymisation.md` (§1 — réutilisation interne nominative), `backlog/chantiers/T-0021.yaml`, `backlog/chantiers/T-0024.yaml` (outillage de création d'espace), `CLAUDE.md`.

## 1. Objet

D'une **proposition gagnée**, produire un **BRIEF DE MISSION-REGRESSION-TEST structuré**, le faire valider par l'utilisateur (porte explicite **« le brief suffit »**), l'écrire en **Zone-de-proposition** (le dérivé n'est jamais le saisi), puis préparer la mise en place : **spécification de l'espace de mission** (création réelle = cran auto, outillage `T-0024`), **imputations proposées** et **templates adaptés** consommant le design system **par référence** — jamais par copie.

> **Thèse que ce skill matérialise (plan §6).** Une amélioration promue de ce skill profite à TOUTES les missions futures, parce que chaque mission le résout depuis le canon au moment de l'exécution. On référence, on ne copie pas.

## 2. Entrées

| Donnée | Source | Usage |
|---|---|---|
| Proposition gagnée | Bibliothèque « Propositions » (modele-donnees §2 bis) ou document fourni par l'utilisateur | matière du brief : contexte, périmètre vendu, jalons, budget |
| Précisions utilisateur | échange conversationnel (l'associé qui affecte — scénario du document de bienvenue) | lever les ambiguïtés ; le skill NE devine PAS |
| Compte / Client | Liste « Comptes » | rattachement de la mission |
| Design system | `contrats/socle/design-system.md` (pull) | templates adaptés, par référence |
| Matière capitalisée | Bibliothèque « Capitalisation » | réutilisation INTERNE nominative (cran auto, anonymisation.md §1 — pas de porte en interne) |

## 3. Sortie : le brief de mission (structure figée)

Le brief est un dérivé riche, auto-portant, écrit en Zone-de-proposition :

~~~
create_list_item(fields = {
  "Title":   "BRIEF-<code mission>",          # ex. BRIEF-M-2026-014
  "Origine": "cadrage-mission",
  "Contenu": <brief structuré, sections figées ci-dessous>,
})
~~~

**Sections figées du Contenu :**
1. **Identité** — code mission proposé, client (id Compte), associé/gestionnaire, dates cibles.
2. **Périmètre & objectifs** — ce qui est vendu, ce qui ne l'est pas (bornes explicites).
3. **Jalons** — étapes datées, livrables attendus à chaque jalon.
4. **Équipe proposée** — grades et volumes (proposition ; le staffing décidé reste humain).
5. **Imputations proposées** — rattachements Temps → Mission (dérivés ; promotion tracée vers la Liste « Imputations » = porte humaine).
6. **Templates adaptés** — liste des livrables types, chacun POINTANT vers le design system et la matière capitalisée (référence, jamais copie).
7. **Espace de mission à créer** — nom, structure (bibliothèques/listes), conforme à modele-donnees ; création = cran auto via outillage `T-0024`.

## 4. Déroulé et portes

1. **Lire** la proposition gagnée et les référentiels (auto — lecture).
2. **Dialoguer** avec l'utilisateur pour préciser le brief (le skill questionne, ne suppose pas).
3. **Porte utilisateur — « le brief suffit »** : validation explicite de l'utilisateur ; SANS elle, rien ne s'exécute (ni écriture, ni espace, ni notification).
4. **Écrire** le brief en Zone-de-proposition (auto — `ecrire_fait_derive_zone_proposition`).
5. **Créer l'espace de mission** (auto — `creer_espace_mission`, outillage `T-0024` ; tant que l'outillage n'est pas livré, la création passe par le gardien avec réserve tracée).
6. **Notifier l'équipe** (notifié — `notifier_equipe`).
7. **Promotion tracée** des faits (fiche Mission, imputations) de la zone vers les sources : porte humaine, HORS de ce skill.

## 5. Crans (résolus via `table-des-crans.yaml`)

| Action | Cran | Fondement |
|---|---|---|
| Lire proposition / référentiels | **auto** | lecture réversible, interne, locale |
| Écrire le brief en Zone-de-proposition | **auto** | `ecrire_fait_derive_zone_proposition` — le dérivé n'est jamais le saisi |
| Créer l'espace de mission | **auto** | `creer_espace_mission` (outillage `T-0024`) |
| Notifier l'équipe | **notifié** | `notifier_equipe` — visible, engage l'image interne |
| Promouvoir brief/imputations vers les sources | **validé — humain** | promotion tracée (modele-donnees §3) |
| Sortie vers le client | **HORS PÉRIMÈTRE** | c'est le skill `kick-off` (`T-0022`) — `envoyer_livrable_client` = validé |

## 6. Garde-fous inscrits dans ce skill

- **Jamais d'écriture directe dans une source** (Missions, Imputations, Temps) : tout naît en Zone-de-proposition ; la promotion est une étape humaine tracée.
- **Porte « le brief suffit »** : aucune action à effet de bord avant la validation explicite de l'utilisateur.
- **Templates par référence** : le brief pointe vers `design-system.md` et « Capitalisation » ; il n'en copie jamais le contenu.
- **Réutilisation interne nominative** (`reutiliser_matiere_interne` = auto) ; aucune sortie de firme dans ce skill, donc pas de porte d'anonymisation ici — elle joue au kick-off si matière d'un client tiers.
- **Le staffing proposé n'est pas le staffing décidé** : l'affectation reste humaine.
- **Collision = fail** : si un BRIEF-<code mission> existe déjà en zone, ne pas écraser — signaler (reprise humaine).

## 7. Ce que ce skill ne fait pas

- Il ne génère ni la proposition ni le support de kick-off (skill `kick-off`, `T-0022`).
- Il n'envoie rien au client et ne publie rien (crans validé / porte anonymisation — hors périmètre).
- Il n'écrit aucune imputation en source et ne promeut rien.
- Il ne décide ni du staffing ni du budget.
- Il ne modifie aucun droit d'accès (chaîne organisation.md §5, hors agent).

## 8. Prérequis avant mise en service

1. **`T-0024`** : outillage de création d'espace de mission (cible figée côté serveur, zéro secret) et câblage réel des Listes « Missions » / « Imputations » au tenant (modele-donnees §2 bis — partiellement câblé).
2. **Promotion de ce skill** par le gardien (procédure allégée).
3. **Épreuve réelle** (SOLDÉ de `T-0021`) : une affaire — réelle ou de démonstration explicitement étiquetée — déroule le skill de bout en bout, crans respectés.

## 9. Évolution

Ce skill est **promu** (procédure allégée, portée locale — `doctrine.md` §5). Son évolution suit la boucle (`doctrine.md` §7) : candidat → avis d'impact → promotion gardien (procédure allégée), montée de version en en-tête, corps byte-identique à la promotion. Retour arrière = repointage.
