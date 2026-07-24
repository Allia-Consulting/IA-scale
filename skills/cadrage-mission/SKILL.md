---
# Cadrage de mission — Skill

> **id** : `cadrage-mission`
> **Version** : 1.4 — *candidat*. **Nature** : skill.
> **Changelog** : v1.4 — candidat, 24 juillet 2026 (T-0038, lever le geste gardien de la couture) : §4 — l'agent **appelle** `allouer_code_mission(opportunite_id)` (cran **notifié**, outil MCP `T-0038`) qui alloue atomiquement le `CodeMission` (max+1) ET le **réécrit sur l'opportunité gagnée** — l'ancienne étape « réécrire `CodeMission` = PROMOTION gardien » est **supprimée** (le geste gardien est levé), puis `creer_espace_mission` (cran auto) crée l'espace à 4 segments **en bout de skill** : plus **aucun** geste gardien dans la chaîne. §5 — le cran de la réécriture passe de **gardien — promotion** à **notifié — `allouer_code_mission`**. L'**allocateur atomique**, jusqu'ici imputé à `T-0024`, est **livré par `T-0038`**. Garde-fous INCHANGÉS (écriture agent des dérivés = Zone-de-proposition uniquement ; l'écriture source `CodeMission` est bornée par construction, cible figée + colonne unique + préconditions fail-closed ; porte « le brief suffit »). v1.3 — candidat, 24 juillet 2026 (T-0035, couture « opportunité Gagnée → ouverture de mission ») : §2 — ajout de l'entrée **Opportunité Gagnée** (Liste « CRM », Etape=Gagnée) comme matière du brief (nom de mission = `NomOpportunite`, client = `NomCompte` lisible, montant, échéance ; couture par `CodeMission` entier). §4 — l'étape « Créer l'espace » explicite l'appel à 4 segments (`code_mission` = max(existants)+1, capacité PR #250) et une étape distincte pose la **réécriture de `CodeMission` sur l'opportunité gagnée (Liste « CRM ») = PROMOTION, cran GARDIEN — hors écriture agent** ; §5 — cran ajouté. Garde-fous INCHANGÉS (écriture agent = Zone-de-proposition uniquement ; porte « le brief suffit » ; allocateur atomique = `T-0024`, geste gardien tracé d'ici là). v1.2 — candidat, 23 juillet 2026 (T-0035, unification du « code mission » numérique) : §3/§4 — l'exemple de code devient un **entier** (`BRIEF-14`), « code mission proposé » → « code mission **alloué** (entier, `modele-donnees.md` §2 bis) », et l'étape 5 précise l'appel réel `creer_espace_mission(annee, client, nom_mission, code_mission)` (nom d'espace à 4 segments, capacité PR #250). Aucun changement de cran ni de garde-fou. v1.1 — promu, 2 juillet 2026 : corps aligné post-promotion (§9 statut candidat → promu). v1.0 — promu, 2 juillet 2026 : promotion par le gardien (procédure allégée), chantier `T-0021`. v1.0 — candidat, 2 juillet 2026 : création (chantier `T-0021`, première marche de la tranche verticale métier, plan §6 T-1.1). Décrit le skill qui, d'une PROPOSITION GAGNÉE, produit un BRIEF DE MISSION structuré, validé par l'utilisateur (« le brief suffit »), écrit en Zone-de-proposition via `create_list_item` ; la création réelle de l'espace de mission (cran auto) s'appuie sur l'outillage du chantier `T-0024`.
> **Domicile** : `skills/cadrage-mission/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `contrats/socle/modele-donnees.md` (§2 / §2 bis / §3 — entités Mission, Imputation, Compte ; Bibliothèques Propositions et Livrables ; Zone-de-proposition Title/Origine/Contenu), `contrats/socle/design-system.md` (templates consommés par référence), `contrats/socle/table-des-crans.yaml` (`allouer_code_mission` = **notifié** ; `creer_espace_mission` = **auto** ; `ecrire_fait_derive_zone_proposition` = **auto** ; `notifier_equipe` = **notifié** ; `merger_sur_main` / promotion = **gardien**), `contrats/socle/anonymisation.md` (§1 — réutilisation interne nominative), `backlog/chantiers/T-0021.yaml`, `backlog/chantiers/T-0024.yaml` (outillage de création d'espace), `backlog/chantiers/T-0038.yaml` (allocateur atomique du `CodeMission` + automatisation de la couture), `CLAUDE.md`.

## 1. Objet

D'une **proposition gagnée**, produire un **BRIEF DE MISSION structuré**, le faire valider par l'utilisateur (porte explicite **« le brief suffit »**), l'écrire en **Zone-de-proposition** (le dérivé n'est jamais le saisi), puis préparer la mise en place : **spécification de l'espace de mission** (création réelle = cran auto, outillage `T-0024`), **imputations proposées** et **templates adaptés** consommant le design system **par référence** — jamais par copie.

> **Thèse que ce skill matérialise (plan §6).** Une amélioration promue de ce skill profite à TOUTES les missions futures, parce que chaque mission le résout depuis le canon au moment de l'exécution. On référence, on ne copie pas.

## 2. Entrées

| Donnée | Source | Usage |
|---|---|---|
| Opportunité Gagnée | Liste « CRM » (Etape = Gagnée) — modele-donnees §2 bis | matière du brief et **couture opportunité → mission** : **nom de mission = `NomOpportunite`**, **client = `NomCompte`** (le nom LISIBLE, jamais le `Title`/code CPT-xxx), montant, échéance ; le lien est porté par **`CodeMission`** (entier) |
| Proposition gagnée | Bibliothèque « Propositions » (modele-donnees §2 bis) ou document fourni par l'utilisateur | matière du brief : contexte, périmètre vendu, jalons, budget |
| Précisions utilisateur | échange conversationnel (l'associé qui affecte — scénario du document de bienvenue) | lever les ambiguïtés ; le skill NE devine PAS |
| Compte / Client | Liste « Comptes » | rattachement de la mission |
| Design system | `contrats/socle/design-system.md` (pull) | templates adaptés, par référence |
| Matière capitalisée | Bibliothèque « Capitalisation » | réutilisation INTERNE nominative (cran auto, anonymisation.md §1 — pas de porte en interne) |

## 3. Sortie : le brief de mission (structure figée)

Le brief est un dérivé riche, auto-portant, écrit en Zone-de-proposition :

~~~
create_list_item(fields = {
  "Title":   "BRIEF-<code mission>",          # ex. BRIEF-14  (code mission = entier, §2 bis)
  "Origine": "cadrage-mission",
  "Contenu": <brief structuré, sections figées ci-dessous>,
})
~~~

**Sections figées du Contenu :**
1. **Identité** — code mission **alloué** (entier, cf. `modele-donnees.md` §2 bis), client (id Compte), associé/gestionnaire, dates cibles.
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
4. **Allouer le `CodeMission` et fermer la couture** (notifié — `allouer_code_mission(opportunite_id)`) : le serveur alloue **atomiquement** le code (`max(CodeMission existants) + 1`, entier ≥ 1) **et le réécrit sur l'opportunité gagnée** (Liste « CRM », colonne `CodeMission`), avec préconditions **fail-closed** (`Etape = Gagnée` ET `CodeMission` vide) et atomicité If-Match/ETag + post-vérification anti-course. C'est une écriture **source bornée par construction** (cible figée `GRAPH_CRM_LIST_ID`, colonne unique) — plus une promotion gardien : le **geste gardien tracé est LEVÉ** (`T-0038`). L'**allocateur atomique**, jusqu'ici imputé à `T-0024`, est **livré par `T-0038`**. Le code retourné adresse ensuite le brief (`BRIEF-<code>`), l'espace et les gabarits. L'allocation réserve le code **avant** tout usage (deux cadrages concurrents ne peuvent converger sur le même code).
5. **Écrire** le brief en Zone-de-proposition (auto — `ecrire_fait_derive_zone_proposition`), en portant le `CodeMission` alloué à l'étape 4 (`Title` = `BRIEF-<code>`).
6. **Créer l'espace de mission** (auto — `creer_espace_mission(annee = année d'ouverture, client = NomCompte du compte lié, nom_mission = NomOpportunite de l'opportunité gagnée, code_mission = <le code alloué à l'étape 4>)` : les quatre composantes ; le nom d'espace porte alors 4 segments « AAAA - Client - Nom - CodeMission » (capacité PR #250). **En bout de skill** — plus **aucun** geste gardien dans la chaîne.
7. **Notifier l'équipe** (notifié — `notifier_equipe`).
8. **Promotion tracée** des faits (fiche Mission, imputations) de la zone vers les sources : porte humaine, HORS de ce skill.

## 5. Crans (résolus via `table-des-crans.yaml`)

| Action | Cran | Fondement |
|---|---|---|
| Lire proposition / référentiels | **auto** | lecture réversible, interne, locale |
| Écrire le brief en Zone-de-proposition | **auto** | `ecrire_fait_derive_zone_proposition` — le dérivé n'est jamais le saisi |
| Créer l'espace de mission | **auto** | `creer_espace_mission` (outillage `T-0024`) |
| Notifier l'équipe | **notifié** | `notifier_equipe` — visible, engage l'image interne |
| Promouvoir brief/imputations vers les sources | **validé — humain** | promotion tracée (modele-donnees §3) |
| Allouer `CodeMission` + le réécrire sur l'opportunité (Liste « CRM ») | **notifié** | `allouer_code_mission` (`T-0038`) — écriture source **bornée par construction** (cible figée `GRAPH_CRM_LIST_ID`, colonne `CodeMission` unique, préconditions fail-closed, allocation atomique) ; l'agent agit, le gardien est informé. Le geste gardien de l'ancienne promotion est **levé** |
| Sortie vers le client | **HORS PÉRIMÈTRE** | c'est le skill `kick-off` (`T-0022`) — `envoyer_livrable_client` = validé |

## 6. Garde-fous inscrits dans ce skill

- **Jamais d'écriture directe et libre dans une source** (Missions, Imputations, Temps) : les faits dérivés naissent en Zone-de-proposition ; leur promotion est une étape humaine tracée.
- **Unique écriture source, BORNÉE PAR CONSTRUCTION** : la réécriture de `CodeMission` sur l'opportunité gagnée passe par `allouer_code_mission` (`T-0038`, cran notifié) — cible **figée** côté serveur (`GRAPH_CRM_LIST_ID`), **une seule colonne** (`CodeMission`), préconditions **fail-closed** (`Etape = Gagnée` ET `CodeMission` vide), allocation atomique et réversible. L'agent ne choisit ni la liste ni la colonne : ce n'est pas une écriture source libre mais un geste gouverné et tracé, sur le modèle des réconciliateurs (organisation.md §5). Le geste gardien de l'ancienne promotion manuelle est **levé**.
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
