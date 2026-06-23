# Génération du brouillon d'offre de contrat de travail — Skill

> **id** : `generation-offre`
> **Version** : 1.1 — *promu*. **Nature** : skill.
> **Changelog** : v1.1 — promu, 23 juin 2026 : corps aligné post-promotion (§8 prérequis promotion marqué levé, §9 statut candidat → promu). v1.0 — promu, 23 juin 2026 : promotion par le gardien (prérequis T-0017-b et T-0003 levés). v1.0 — candidat, 23 juin 2026 : création. Sous-tâche `T-0016-b` de la chapeau `T-0016` (agent « brouillon d'offre de contrat de travail »). Décrit le skill qui produit un BROUILLON d'offre `.docx` à partir du gabarit canonique (`gabarit-offre.md` v1.2), le dépose dans « 00 - Proposition en cours » via `televerser_brouillon_offre` (connecteur étendu, `T-0017`), et journalise « brouillon généré » en Zone-de-proposition via `create_list_item` (double-écriture). La mise en service est subordonnée aux runbooks `T-0017-b` et `T-0003`.
> **Domicile** : `skills/generation-offre/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `contrats/local/talent-rh/gabarit-offre.md` (v1.2 — **LE document**, source de vérité), `contrats/socle/table-des-crans.yaml` (v1.8 : `televerser_brouillon_offre_zone_travail` = **auto** ; `ecrire_fait_derive_zone_proposition` = **auto** ; `prendre_engagement_juridique_ou_financier` = **PROSCRIT**), `contrats/socle/modele-donnees.md` (§2 bis / §2 ter — liste « Candidats », liste « Zone-de-proposition »), `contrats/socle/rgpd-recrutement-candidats.md` (§1 art. 22 — décision humaine ; §3 — régime nominatif interne), `backlog/chantiers/T-0017.yaml` (connecteur étendu — outil `televerser_brouillon_offre`), `contrats/socle/design-system.md`, `CLAUDE.md`.

## 1. Objet

Produire un **BROUILLON** `.docx` d'offre de contrat de travail à partir de la **fiche Candidat** et du **gabarit canonique** (résolu au pull), le **déposer dans « 00 - Proposition en cours »**, et **tracer « brouillon généré »** en Zone-de-proposition. Le skill épargne au gestionnaire la rédaction — rien de plus.

> **Borne dure (reprise du gabarit §0, non négociable).**
> - L'agent **PRÉPARE** un brouillon ; il **N'ÉMET JAMAIS** l'offre — émettre est un engagement juridique (`table-des-crans.yaml` : `prendre_engagement_juridique_ou_financier` — **PROSCRIT** à l'agent et à Claude).
> - La **décision de recrutement reste HUMAINE** (`rgpd-recrutement-candidats.md` §1, art. 22).
> - Le document est **imprimé, signé à la main et envoyé par le gestionnaire** de la proposition (dernier interviewer / personne en charge du poste). Le papier matérialise que l'offre est faite par un humain.
> - Le montant inséré est le **PLANCHER du grade**, marqué **« à valider / ajuster par le gestionnaire »** — jamais arrêté par l'agent.
> - Le brouillon va dans **« 00 - Proposition en cours » UNIQUEMENT** ; **jamais** au niveau « 01 - Proposition d'embauche » (offres **SIGNÉES**).

## 2. Entrées (lecture de la fiche Candidat)

Lecture via `list_items` sur la liste **« Candidats »** (noms internes réels — `modele-donnees.md` §2 ter) :

| Donnée | Colonne (nom interne) | Usage dans le brouillon |
|---|---|---|
| Identifiant candidat | `Title` (ex. `C-014`) | nommage du fichier + clé du journal |
| Nom du candidat | `NomCandidat` | `[Prénom NOM]` du gabarit |
| Grade visé | `Grade` | `[Grade]` + sélection du plancher (§5 gabarit) + ligne variable conditionnelle |
| Étape | `Etape` | **garde-fou métier** (voir ci-dessous) |
| Owner d'action | `ResponsableAction` | gestionnaire / dernier interviewer = destinataire du brouillon |

> **Garde-fou métier — `Etape == "Proposition"` requis.** Ne générer un brouillon **QUE** si la fiche est à l'étape `Proposition`. Pour toute autre valeur (`E1` / `E2` / `E3` / `Acceptée` / `Refusée`), **refuser explicitement** : un brouillon d'offre n'a de sens qu'au stade proposition. Le skill ne fait pas avancer l'étape — il la lit.

## 3. Génération du `.docx` (à la volée — aucun binaire versionné)

Le document est produit **à l'exécution** depuis le **gabarit markdown** (`gabarit-offre.md`), qui est la **SEULE vérité**. Aucun `.docx` n'est figé au dépôt : le rendu suit la **structure figée** du gabarit (en-tête « ALLIA CONSULTING » + SIRET/TVA, adressage, objet « Offre de CDI — [Grade] », tableau des conditions Syntec, validité 15 jours, paragraphe documents d'embauche, bloc signatures) et le **design system**. La génération du binaire s'appuie sur la **skill `docx` du poste**, consommée à l'exécution — ce SKILL.md décrit le **QUOI**, pas un binaire.

**Substitution des variables (gabarit §5), depuis la fiche :**

| Variable gabarit | Valeur |
|---|---|
| `[Grade]` | `Grade` de la fiche |
| `[Prénom NOM]` | depuis `NomCandidat` |
| `[Date d'émission]` | date du jour de génération |
| `[Date d'entrée en fonction]` | un **lundi** proposé, marqué **« à valider par le gestionnaire »** |
| `[Plancher du grade]` | repère gabarit §5, marqué **« à valider »** (Consultant Junior 42 · Consultant 48 · Consultant Senior 55 · Manager 65 · Senior Manager 75 · Directeur 90 · Associé 120 — en k€ bruts) |

> **Civilité — jamais inférée.** Le modèle Candidat ne porte **pas** la civilité. Insérer le placeholder explicite **« [Civilité — à compléter par le gestionnaire] »**. L'agent **n'infère JAMAIS** un genre depuis un nom.

> **Ligne de rémunération variable — conditionnelle.** Présente **UNIQUEMENT** si `Grade ∈ {Manager, Senior Manager, Directeur, Associé}`, et alors marquée **« à valider »**. **Absente** pour Consultant Junior / Consultant / Consultant Senior.

## 4. Double-écriture (ordre imposé : docx d'abord, journal ensuite)

**(1) Déposer le `.docx`** dans « 00 - Proposition en cours » :

~~~
televerser_brouillon_offre(
    nom_fichier   = "Offre-<Title>-<grade-slug>-<AAAAMMJJ>.docx",
    contenu_base64 = <docx généré, encodé base64>,
    candidat_id    = <Title>,
)
# → récupérer web_url du fichier déposé
~~~

La **cible est figée côté connecteur** (`T-0017`) — le skill ne la choisit pas. **Collision = fail** : si le connecteur lève `FileExistsError` (un brouillon de même nom existe déjà), **NE PAS réessayer**, **NE PAS écraser** — signaler au gestionnaire qu'un brouillon existe déjà (**retrait humain requis**).

**(2) Journaliser « brouillon généré »** en Zone-de-proposition (uniquement si (1) a réussi) :

~~~
create_list_item(fields = {
    "Title":   "BROUILLON-OFFRE-<Title>-<AAAAMMJJ>",
    "Origine": "generation-offre",
    "Contenu": "<résumé : candidat (Title + NomCandidat), grade, plancher proposé « à valider »,
                lien web_url du .docx déposé dans 00, mention : brouillon — non émis,
                décision humaine (rgpd §1 art. 22)>",
})
~~~

La **Zone-de-proposition est le JOURNAL** « brouillon généré » ; le **`.docx` vit dans 00**. **Si (1) échoue, NE PAS écrire le journal** — pas de trace d'un dépôt qui n'a pas eu lieu.

## 5. Crans (résolus via `table-des-crans.yaml` v1.8)

| Action | Cran | Fondement |
|---|---|---|
| **Lire** la fiche Candidat (`list_items`) | **auto** | lecture réversible, interne, local |
| **Téléverser** le brouillon dans 00 | **auto** | `televerser_brouillon_offre_zone_travail` — brouillon non émis, cible figée, collision=fail |
| **Journaliser** en Zone-de-proposition | **auto** | `ecrire_fait_derive_zone_proposition` — le dérivé n'est jamais le saisi |
| **ÉMETTRE** l'offre | **PROSCRIT — humain** | `prendre_engagement_juridique_ou_financier` ; décision humaine (art. 22) |

## 6. Garde-fous inscrits dans ce skill

- **Jamais d'émission** : le skill s'arrête au dépôt du brouillon + journal. L'émission est humaine.
- **Jamais de montant arrêté** : le plancher du grade est un repère **« à valider »**, jamais une cible.
- **Jamais d'inférence de civilité / de genre** : placeholder explicite à compléter par le gestionnaire.
- **`Etape == "Proposition"` requis** : refus explicite à tout autre stade.
- **Cible figée côté connecteur** : dépôt dans « 00 » uniquement, **jamais « 01 »** (offres signées).
- **Collision = fail** : aucun écrasement ; un brouillon existant exige un retrait humain.
- **Ordre de la double-écriture** : docx d'abord, journal ensuite ; si le docx échoue, pas de journal.
- **Régime nominatif interne** : données candidat nominatives, cohérent avec `rgpd-recrutement-candidats.md` §3 (interne, pas de sortie de firme — pas d'anonymisation).

## 7. Ce que ce skill ne fait pas

- Il **n'émet pas** l'offre et ne l'envoie **jamais** au candidat.
- Il **ne décide pas** du recrutement (décision humaine, art. 22).
- Il **ne fixe pas** le montant de rémunération (plancher « à valider »).
- Il **ne signe pas** le document.
- Il **ne fait pas avancer** l'étape de la fiche Candidat.
- Il **ne dépose jamais** au niveau « 01 - Proposition d'embauche ».

## 8. Prérequis avant mise en service (runbooks humains — hors de ce skill)

Ce skill **ne peut pas être mis en service** tant que les prérequis suivants ne sont pas posés :

1. **`T-0017-b`** (runbook humain) : pose des variables `GRAPH_BROUILLON_DRIVE_ID` / `GRAPH_BROUILLON_FOLDER_ID` du connecteur **et** vérification de l'**octroi write** sur la bibliothèque Documents. Sans elles, `televerser_brouillon_offre` échoue (`ConfigManquante`).
2. **`T-0003`** : journalisation active sur la liste « Candidats » — prérequis à tout accès agent réel aux données candidat.
3. **Promotion de ce skill** par le gardien (procédure allégée) — *levé : promu le 23 juin 2026*.

## 9. Évolution

Ce skill est **promu** (procédure allégée, portée locale — `doctrine.md` §5). Sa promotion suit la boucle (`doctrine.md` §7) avec montée de version. Retour arrière = repointage. Les runbooks de mise en service (§8) sont des livrables distincts, séquencés avant toute exécution réelle.
