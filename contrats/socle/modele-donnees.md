# Modèle de données — Allia Consulting

> **Version** : 1.20 — *promu*. **Statut** : contrat socle — fait foi.
> **Domicile** : `contrats/socle/modele-donnees.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§2 et §8), `contrats/socle/organisation.md`.
> **Changelog** : v1.20 — promu via boucle de promotion, 17 juillet 2026 (T-0033 reprise S37) : instanciation des gabarits par **fabrication service** (API Workbook, `workbook_instancier_gabarit` v2, **serveur 0.13.0**) — création du classeur par le service Excel (PUT contenu vide, `@microsoft.graph.conflictBehavior=fail`) puis `tables/add` sur les plages d'en-têtes §5.2, **preuve interne count:0 ×3** et **rollback borné** ; **retrait du rôle de souche** du binaire `gabarit-pilotage-mission.xlsx` (conservé au canon comme trace historique, plus consommé) ; **§5.2 = unique source de vérité du schéma des tables** ; §5.6 instanciation par fabrication service, plus par copie de souche. Éditions surgicales du corps uniquement ; aucune entrée de changelog existante modifiée.
> **Changelog** : v1.19 — promu via boucle de promotion, 14 juillet 2026 (session S34, consommation des primitives Workbook `T-0031`) : **consignation des domiciles réels du référentiel de coûts et de la couche de saisie**, vérifiés sur le tenant le 14/07/2026. **§5.5** — le référentiel de coûts vit sur le site **AlliaConsulting-Contratsetadministratif** : `referentiel-structure.xlsx` (table `T_Structure`) dans « 07 - Coût de Structure » et `referentiel-ressources.xlsx` (table `T_Ressources`) dans « 08 - Coût Masse salariale & Indep » ; coordonnées tenant (drive-id/item-id) en **variables d'environnement** posées par runbook gardien, jamais au canon ; **renvoi croisé** vers le skill consommateur `skills/consolidation-pilotage/`. **§5.6** — convention de nommage des classeurs de saisie `saisie-<CodeMission>-<Libellé>.xlsx` (code porté par le nom, libellé libre, casse libre) et note « métadonnées de modification différées en co-édition : le contenu fait foi, pas l'horodatage ». **§5.3** — la colonne `Ressource` de `T_Ressources` porte pour identifiant l'adresse **mail Allia** (salarié) ou l'adresse **mail du sous-traitant** (sous-traitant), décision gardien du 14/07/2026. **Instanciation systématique** : ajout de la primitive `workbook_instancier_gabarit` (serveur 0.12.0, `T-0031`) et du cran `instancier_gabarit_pilotage` (`table-des-crans.yaml` v1.11, auto, création pure fail-closed `@microsoft.graph.conflictBehavior=fail`) — l'instanciation du gabarit d'une mission devient **systématique et machine** (§5.6, décision gardien du 14/07/2026), plus jamais un geste humain ; le gabarit canon vierge reste la seule souche. Aucune entrée de changelog existante ni domicile modifié ; éditions surgicales du corps uniquement.
> **Changelog** : v1.18 — promu via boucle de promotion, 14 juillet 2026 (lecture du réel, session S34 ; adossé à `tour-de-controle.md` v2.1) : **rectification des domiciles réels du modèle économique (§5)**. Il n'y a **pas de classeur consolidé unique** — les mentions antérieures d'un `pilotage-consolide.xlsx` sont caduques. Le modèle réel a **trois couches** : (i) **saisie** humaine (source) dans des classeurs `saisie-…xlsx` sur le site **Management et Gestion** ; (ii) **gabarit ERP par mission** `gabarit-<CodeMission>.xlsx` (dérivé régénéré par agent) sur le site **Contrats et administratif**, dossier `06 - Gabarit ERP` (+ `00 - Old`, 1 mission = 1 gabarit actif) ; (iii) **référentiel de coûts** à audience restreinte (T_Ressources, T_Structure). La tour de contrôle lit les **gabarits actifs + le référentiel en direct**, sans artefact consolidé. §5.1 réécrit, §5.3 « consolidé » → **référentiel de coûts**, §5.4 « calcul à la volée », **§5.6 ajoutée** (couche saisie + boucle agent lun-ven 5h/13h Paris, détection par `lastModifiedDateTime`). L'édition économique humaine se fait dans la saisie, **hors cockpit** (lecture seule côté cockpit). Coordonnées tenant en **variables d'environnement** posées par runbook gardien — jamais au canon. v1.17 — promu via boucle de promotion, 14 juillet 2026 (conception S33, adossé à `tour-de-controle.md` v2.0) : **modèle économique distribué** (§5). Introduction d’un type d’objet nouveau au modèle — le **classeur Excel à tables nommées** — distinct des listes SharePoint : un **gabarit de pilotage par mission** (jours et CA, jamais les coûts) instancié dans l’espace de chaque mission, et un **classeur consolidé central à audience restreinte** (coûts ressources et structure) régénéré par agent. Couture Graph par **Workbook/Tables API** (et non Lists API). Corrige aussi une référence de section périmée dans `T-0013.yaml` (§5→§6 suite à `tour-de-controle.md` v2.0).
> **Changelog** : v1.16 — promu via boucle de promotion, 5 juillet 2026 (chantier `T-0026`) : **brique CRM — pipeline commercial** (§2, §2 bis, §2 ter, §3). Ajout de l'entité **Opportunité**, domicile **Liste « CRM »** (à créer, runbook `T-0026`) : étapes **Qualification / Proposition / Gagnée / Perdue**, montant, échéance, responsable ; lien **opportunité → mission** porté par `CodeMission` — couture par identifiant stable, renseigné à la bascule « Gagnée », où se branche la tranche cadrage-mission / kick-off. Schéma de colonnes posé sur la Liste « Comptes » existante (id compte, nom, secteur, statut Prospect / Client / Inactif) ; §2 ter étendu (Comptes, CRM) ; §3 — une opportunité **détectée par un agent** est un dérivé : elle naît en Zone-de-proposition et rejoint la Liste « CRM » à validation (promotion tracée) ; la saisie humaine directe reste une source. **Aucune entité Contact ni donnée personnelle** (décision gardien du 05/07/2026 : ce volet est hors périmètre). Écriture agent **inchangée** : Zone-de-proposition uniquement (garde-fou structurel §3/§4). Câblage tenant (colonnes Comptes, création de la Liste « CRM ») = runbook `T-0026`. Aucun domicile existant modifié. v1.15 — promu via boucle de promotion, 19 juin 2026 : §2 bis + §3 — ajout de la colonne **Contenu** (texte multiligne) à la liste « Zone-de-proposition », destinée à porter le corps d'un fait dérivé riche (ex. synthèse d'entretien au format auto-portant) que Title / Origine (mono-ligne) ne peuvent pas porter ; prérequis de l'écriture réelle des synthèses (preuve T-0013-c). Aucun autre domicile ni règle modifié. v1.14 — promu via boucle de promotion, 18 juin 2026 : bascule des **valeurs d'énumération** du schéma recrutement sur le substrat M365 — `Etape`/`EtapeSynthese` → **E1 / E2 / E3** (+ **Proposition / Acceptée / Refusée** pour `Etape`) ; `Source` réordonnée et recasée (**Cooptation / Chasseur / Candidature spontanée / LinkedIn**) ; `Grade` « **Consultant Senior** » (casse). §2 bis et §2 ter alignés. Aucun changement de domicile ni de règle. v1.13 — promu via boucle de promotion, 18 juin 2026 : **CORRECTION** du schéma des deux listes de recrutement (v1.12 promu), projetant la règle de rétention promue (`rgpd-recrutement-candidats.md` §5, v1.4). §2 bis + §2 ter, liste **Candidats** : **Poste visé → Grade visé** (échelle firme — Consultant Junior … Associé, choix sans ajout manuel) ; **Étape** = entretien 1 / 2 / 3 / proposition / accepté / refusé (**drop « sourcing » et « vivier »** — un refusé rejoint le vivier par la **règle** §5, pas par une valeur d'étape) ; **horloge de rétention = colonne native « Créé le »** (date d'inscription, 2 ans, `T-0013-d`) — **suppression des colonnes de date custom** `DateDernierContact` / `DateAboutissementInstruction` ; **`DernierInterviewer` → `ResponsableAction`** (Owner d'action, Personne ; au stade proposition = dernier interviewer, ancrage 1b). Liste **Candidats-Synthèses** : `EtapeSynthese` gagne **entretien 3** ; lookup Synthèse→Candidat et régime « dérivé né en Zone-de-proposition, rejoint à validation ; notes brutes éphémères » **inchangés**. Aucune autre section ni domicile modifié. v1.12 — schéma complet des deux listes de recrutement (couture M365, guide → M365 ; prérequis T-0013-a..d et recrutement-pipeline), promu via boucle de promotion, 18 juin 2026 : au §2 bis, fixation des **colonnes, types et noms internes (Graph)** des listes **Candidats** (Title, NomCandidat, PosteVise, Source, Email, Telephone, Etape, DateDernierContact, DateAboutissementInstruction, DernierInterviewer) et **Candidats-Synthèses** (Title, Candidat [lookup → Candidats], EtapeSynthese, DateEntretien, Interviewer, Synthese) ; valeurs d'étape figées ; nouvelle sous-section **§2 ter — Noms internes (couture Graph)** (mapping libellé ↔ nom interne ; principe « créer la colonne sous son nom interne propre puis renommer le libellé » pour éviter les encodages `_x00e9_` / tirets côté Graph). Lookup Synthèse→Candidat inchangé (canon v1.11) ; le dérivé **naît en Zone-de-proposition** et ne rejoint « Candidats-Synthèses » **qu'à validation** ; notes brutes éphémères, jamais une colonne. Régime données personnelles candidat + journalisation prérequis **inchangés**. Aucune autre section ni domicile modifié. v1.11 — entité Candidat & synthèses d'entretien (sous-tâche T-0013-a), 17 juin 2026 : ajout au §2 des entités **Candidat** (liste unique « Candidats », colonne étape sourcing→vivier, colonnes de dates pour la purge T-0013-d) et **Synthèse d'entretien** (liste dédiée « Candidats-Synthèses », rattachée au candidat) ; domiciles réels au §2 bis ; régime **données personnelles candidat** aligné sur Ressources-RH/CVs (journalisation d'audit prérequis runbook, cf. T-0003). Exécute le cadre RGPD recrutement promu (rgpd-recrutement-candidats.md + annexes 1 et 3). Aucun domicile existant modifié. v1.10 — balayage post-promotion, 12 juin 2026 : `memoire-organisation.md` est promu ; les deux mentions « candidat » (§2 bis, §3) sont retirées. Aucun changement de règle ni de domicile. v1.9 — alignement des mentions d'entrée sur le modèle des identités appelantes (post-T-0010), 12 juin 2026 : les §2 bis et §4 ne décrivent plus l'entrée comme « bearer du principe appelant unique `allia-mcp-graph-client` » mais selon `identites-et-secrets.md` §2 — humains : identité Entra (PKCE, client public `allia-mcp-graph-client`, groupe `grp-mcp-graph-users`) ; workloads : identité managée ; le secret client est supprimé (dette éteinte, `T-0010`). Aucun changement de règle ni de domicile. v1.8 — endpoints réels après déploiement (item prévu par la chapeau `T-0002b`), 10 juin 2026 : le connecteur **Graph MCP en écriture** est **déployé et prouvé** (chapeau `T-0002b` promue — cinq sous-tâches) ; endpoint MCP `https://ca-allia-mcp-graph.delightfulocean-1bf3f3c5.francecentral.azurecontainerapps.io/mcp` (entrée : **bearer OAuth 2.0** du principe appelant unique `allia-mcp-graph-client`, Easy Auth Return401 ; sortie Graph : identité managée, **zéro secret**) ; la Zone-de-proposition est **réelle** et l'**écriture y est outillée** (preuve `create_list_item` le 10 juin) — la simulation locale `zone-proposition/` cesse d'être le domicile transitoire des **nouveaux** dérivés (les synthèses « mémoire hebdo » basculeront avec `T-0005`). Mentions d'état §2 bis/§3/§4. **Aucun changement de règle ni de domicile logique.** v1.7 — état de câblage de la zone de proposition, 10 juin 2026 (runbook `T-0002b-3`) : la liste « Zone-de-proposition » **existe désormais au tenant** (créée le 10 juin 2026 par le gardien, colonne texte « Origine » = champ d'origine, §2 bis/§3) ; la zone n'est plus « simulée en local » *faute de liste* — la simulation locale (`zone-proposition/`) reste le domicile **transitoire** des dérivés tant que l'**écriture réelle** via le connecteur n'est pas prouvée (fin de la chapeau `T-0002b` : entrée Easy Auth `T-0002b-4`, principe appelant `T-0002b-5`). **Aucun changement de règle, aucun changement de domicile.** v1.6 — promu via boucle de promotion, 8 juin 2026 (session doctrine) : §2 bis — ajout du **champ d'origine « mémoire hebdo »** sur la liste « Zone-de-proposition », qui marque les éléments produits par le batch nocturne de **mémoire d'organisation** (synthèse hebdomadaire candidate) et les distingue des autres faits dérivés ; en attendant T-0002b, ces éléments sont simulés en local sous `zone-proposition/memoire/`. Renvoi normatif vers le contrat socle (candidat) `contrats/socle/memoire-organisation.md`. Aucun autre domicile ni câblage modifié. v1.5 — repointage des renvois après le découpage (PR #23) du chantier d'écriture Graph en **T-0002a** (runbook Entra, promu) et **T-0002b** (déploiement / écriture réelle), 7 juin 2026 : toutes les mentions du chantier d'écriture (§2, §2 bis, §3, §4 et changelog v1.1) pointent désormais vers **T-0002b**. Aucun domicile ni câblage modifié. v1.4 — alignement sur le déclencheur d'anonymisation corrigé (`anonymisation.md` v1.3), 7 juin 2026 : la note de la bibliothèque « Capitalisation » (§2 bis) ne dit plus « porte anonymisation à la réutilisation inter-client » ; le canon interne reste **nominatif**, la porte joue à la **sortie externe**. Aucun domicile ni câblage modifié. v1.3 — promu via boucle de promotion (contenu inchangé ; état « partiellement câblé » du §2 bis/§4 inchangé). v1.2 — §2 bis : distinction explicite nom d'affichage (« Allia Consulting ») vs identifiant d'URL (« alliaconsuling », conservé). Aucun domicile ni câblage modifié.
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
| Compte / Client | référentiel des comptes (prospects et clients) | Liste « Comptes » *(schéma complet : § 2 bis)* | id compte | source |
| Opportunité | une affaire en développement (pipeline commercial) | Liste « CRM » *(schéma complet : § 2 bis)* | id opportunité | source / dérivé |
| CVs | CV d'une ressource | Bibliothèque « CVs » | nom du fichier | source · **données personnelles (RGPD)** |
| Candidat | un candidat au recrutement | Liste « Candidats » *(schéma complet : § 2 bis)* | id candidat | source · **données personnelles (RGPD)** |
| Synthèse d'entretien | appréciation structurée d'un entretien | Liste « Candidats-Synthèses » (rattachée au candidat) *(schéma complet : § 2 bis)* | id synthèse | dérivé · **données personnelles (RGPD)** |

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
| Liste « Comptes » | site AlliaConsuling / Liste Comptes | lecture/écriture selon cran | référentiel des comptes (prospects et clients). Identifiant stable = **id compte** (`Title`, ex. `CPT-001`). **Colonnes** (libellé → nom interne / type) : Identifiant compte → `Title` (id stable) · Nom du compte → `NomCompte` (texte) · Secteur → `Secteur` (texte, optionnel) · Statut → `Statut` (choix **unique** : Prospect / Client / Inactif — pas de défaut, pas d'ajout manuel). Noms internes : voir **§2 ter**. Liste **existante au tenant** (vide) — colonnes à poser par runbook (`T-0026`). **Aucune donnée personnelle** : le référentiel porte des organisations, jamais des interlocuteurs (décision gardien du 05/07/2026). |
| Liste « CRM » | site AlliaConsuling / Liste CRM | lecture selon cran ; **écriture agent : dérivés via Zone-de-proposition uniquement** | pipeline commercial (entité **Opportunité**). Identifiant stable = **id opportunité** (`Title`, ex. `O-001`). **Colonnes** (libellé → nom interne / type) : Identifiant opportunité → `Title` (id stable) · Nom de l'opportunité → `NomOpportunite` (texte) · Compte → `Compte` (**lookup → Comptes** sur `Title` — **le rattachement**) · Étape → `Etape` (choix **unique** : Qualification / Proposition / Gagnée / Perdue — pas de défaut, pas d'ajout manuel) · Montant → `Montant` (nombre — € HT estimés) · Échéance → `Echeance` (date — signature attendue) · Responsable → `Responsable` (personne, unique — porteur du développement de l'affaire) · Code mission → `CodeMission` (texte — renseigné à la bascule « **Gagnée** » ; porte l'**identifiant stable de la Mission** ouverte par l'affaire gagnée : **LE lien opportunité → mission**, couture par identifiant — la tranche cadrage-mission / kick-off s'y branche, le brief portant le code mission). Noms internes : voir **§2 ter**. Une opportunité **saisie par un humain** est une **source** ; une opportunité **détectée par un agent** est un **dérivé** : elle **naît en Zone-de-proposition** et ne rejoint cette liste **qu'à validation** (promotion tracée, §3). **Aucune donnée personnelle** dans cette liste. Liste **à créer** par runbook (`T-0026`). |
| Liste « Ressources-Profil » | site AlliaConsuling / Liste Ressources-Profil | **lecture** | profil de ressource (compétences, séniorité) |
| Liste « Ressources-RH » | site AlliaConsuling / Liste Ressources-RH | **accès restreint** | ⚠️ **journalisation à activer** — données RH sensibles |
| Liste « Zone-de-proposition » | site AlliaConsuling / Liste Zone-de-proposition | **écriture (dérivés)** | domicile concret de la zone de proposition (§3). **Liste créée au tenant le 10 juin 2026** (runbook `T-0002b-3` ; colonne texte « Origine » posée). Porte un **champ d'origine** qui qualifie chaque dérivé ; valeur **« mémoire hebdo »** = synthèse produite par le batch nocturne de **mémoire d'organisation** (contrat socle `contrats/socle/memoire-organisation.md`), à valider ligne à ligne le vendredi. **Écriture via Graph Lists API — outillée et prouvée (10 juin 2026, chapeau `T-0002b` promue)** : endpoint MCP `https://ca-allia-mcp-graph.delightfulocean-1bf3f3c5.francecentral.azurecontainerapps.io/mcp` (entrée : bearer OAuth 2.0 selon le modèle des identités appelantes — humains : identité Entra PKCE via le client public `allia-mcp-graph-client`, accès gouverné par le groupe `grp-mcp-graph-users` ; workloads : identité managée — `identites-et-secrets.md` §2 ; Easy Auth Return401). Les **nouveaux dérivés** s'écrivent dans la liste réelle — la simulation locale (`zone-proposition/`) cesse d'être leur domicile transitoire ; les synthèses « mémoire hebdo » basculeront avec `T-0005` (sous `zone-proposition/memoire/` d'ici là). **Colonnes** (libellé → nom interne / type) : Titre → `Title` (texte) · Origine → `Origine` (texte ; provenance, ex. « mémoire hebdo », « synthese-entretien ») · **Contenu → `Contenu` (texte multiligne)** — porte le corps du dérivé riche (ex. synthèse structurée du skill `synthese-entretien`, format §4 bis) ; Title/Origine mono-ligne ne peuvent pas le porter. Création §2 ter : nom interne ASCII `Contenu`, puis libellé « Contenu ». |
| Bibliothèque « Livrables » | site AlliaConsuling / Bibliothèque Livrables | lecture/écriture selon cran | documents produits |
| Bibliothèque « Propositions » | site AlliaConsuling / Bibliothèque Propositions | lecture/écriture selon cran | propositions commerciales |
| Bibliothèque « Capitalisation » | site AlliaConsuling / Bibliothèque Capitalisation | lecture/écriture selon cran | matière capitalisée (canon interne — reste nominative ; la porte d'anonymisation joue à la **sortie externe** : publication / livrable hors firme, voir `anonymisation.md` §1) |
| Bibliothèque « CVs » | site AlliaConsuling / Bibliothèque CVs | **lecture** | ⚠️ **données personnelles (RGPD) — journalisation à activer** |
| Liste « Candidats » | site AlliaConsuling / Liste Candidats | **accès restreint** | ⚠️ **données personnelles candidat (RGPD)** — recrutement. Identifiant stable = **id candidat** (`Title`, ex. `C-014`). **Colonnes** (libellé → nom interne / type) : Identifiant candidat → `Title` (id stable) · Nom du candidat → `NomCandidat` (texte, donnée perso, pertinente au poste) · Grade visé → `Grade` (choix **unique** : Consultant Junior / Consultant / Consultant Senior / Manager / Senior Manager / Directeur / Associé — sans ajout manuel) · Source → `Source` (choix **unique** : Cooptation / Chasseur / Candidature spontanée / LinkedIn — sans ajout manuel) · Email → `Email` (texte, recontact vivier) · Téléphone → `Telephone` (texte, optionnel) · **Étape** → `Etape` (choix **unique** : E1 / E2 / E3 / Proposition / Acceptée / Refusée — pas de défaut, pas d'ajout manuel ; un refusé rejoint le vivier **par la règle** §5, jamais par une valeur d'étape) · Owner d'action → `ResponsableAction` (personne, unique — porteur de l'action ; au stade proposition = **dernier interviewer**, ancrage 1b / recrutement-pipeline §3) · **(Créé le)** → colonne **native** (date d'inscription = **horloge de rétention** : 2 ans, purge `T-0013-d`) — **pas de colonne de date custom**. Noms internes : voir **§2 ter**. Cadre `contrats/socle/rgpd-recrutement-candidats.md`. **Journalisation à activer** avant accès agent réel (cf. T-0003). |
| Liste « Candidats-Synthèses » | site AlliaConsuling / Liste Candidats-Synthèses | **écriture (dérivés via Zone-de-proposition)** | ⚠️ **données personnelles candidat (RGPD)**. Une synthèse d'entretien **par entretien**. Identifiant stable = **id synthèse** (`Title`, ex. `C-014-E1`). **Colonnes** (libellé → nom interne / type) : Identifiant synthèse → `Title` (id stable) · Candidat → `Candidat` (**lookup → Candidats** sur `Title` — **LE rattachement**, canon v1.11) · Étape → `EtapeSynthese` (choix : E1 / E2 / E3) · Date entretien → `DateEntretien` (date) · Interviewer → `Interviewer` (personne) · Synthèse → `Synthese` (texte multiligne — contenu **structuré** du skill, checklist §4 du cadre ; brut). Noms internes : voir **§2 ter**. Le dérivé **naît en Zone-de-proposition** (T-0013-c) et ne rejoint cette liste **qu'à validation** (promotion tracée) ; les **notes brutes** sont éphémères et ne sont **jamais une colonne** ni une entité (cadre §4). Synthèse **accessible au candidat** (droit d'accès, cadre §7). **Journalisation à activer** avant accès agent réel (cf. T-0003). |

> **Garde-fous (runbook humain — hors agent).** Activer la **journalisation** sur `Ressources-RH` et `CVs` avant tout accès agent ; les droits M365 ne se règlent jamais à la main par un agent mais par réconciliation au moindre privilège d'une décision promue (`organisation.md` §5). La présence d'un domicile dans cette table ne vaut pas ouverture d'accès.

## 2 ter. Noms internes (couture Graph)

Côté Graph (Lists API), chaque colonne porte **deux** noms : un **libellé** affiché (modifiable, accentué) et un **nom interne** (figé à la création, sert de clé dans les payloads `fields`). **Principe de création** : créer la colonne sous son **nom interne propre** (ASCII, sans accent ni tiret — ex. `Etape`), **puis** renommer le libellé affiché (« Étape »). Créer directement sous un libellé accentué fait dériver le nom interne en encodage Graph (`_x00e9_`, suffixes, tirets transformés) — pénible à câbler et instable. Le **mapping fait foi** ci-dessous : les agents écrivent sur le **nom interne**, jamais sur le libellé.

**Liste « Candidats »** (identifiant stable = `Title`)

| Libellé affiché | Nom interne | Type | Notes |
|---|---|---|---|
| Identifiant candidat | `Title` *(existant)* | — | id stable, ex. `C-014` |
| Nom du candidat | `NomCandidat` | Texte | donnée personnelle, pertinente au poste |
| Grade visé | `Grade` | Choix (unique) | Consultant Junior / Consultant / Consultant Senior / Manager / Senior Manager / Directeur / Associé — sans ajout manuel |
| Source | `Source` | Choix (unique) | Cooptation / Chasseur / Candidature spontanée / LinkedIn — sans ajout manuel |
| Email | `Email` | Texte | contact (recontact vivier) |
| Téléphone | `Telephone` | Texte | optionnel |
| Étape | `Etape` | Choix (unique) | E1 / E2 / E3 / Proposition / Acceptée / Refusée — pas de défaut, pas d'ajout manuel |
| Owner d'action | `ResponsableAction` | Personne (unique) | porteur de l'action ; au stade proposition = dernier interviewer (ancrage 1b / recrutement-pipeline §3) |
| *(Créé le)* | *(natif)* | Date (native) | date d'inscription = **horloge de rétention** (2 ans, `T-0013-d`) — pas de colonne de date custom |

**Liste « Candidats-Synthèses »** (identifiant stable = `Title` ; une synthèse par entretien)

| Libellé affiché | Nom interne | Type | Notes |
|---|---|---|---|
| Identifiant synthèse | `Title` *(existant)* | — | ex. `C-014-E1` |
| Candidat | `Candidat` | Lookup → Candidats (`Title`) | **le rattachement** (canon v1.11) |
| Étape | `EtapeSynthese` | Choix | E1 / E2 / E3 |
| Date entretien | `DateEntretien` | Date | |
| Interviewer | `Interviewer` | Personne | |
| Synthèse | `Synthese` | Texte multiligne | contenu structuré du skill (checklist §4 du cadre) — brut |

**Liste « Comptes »** (identifiant stable = `Title` ; liste existante — colonnes à poser, runbook `T-0026`)

| Libellé affiché | Nom interne | Type | Notes |
|---|---|---|---|
| Identifiant compte | `Title` *(existant)* | — | id stable, ex. `CPT-001` |
| Nom du compte | `NomCompte` | Texte | |
| Secteur | `Secteur` | Texte | optionnel |
| Statut | `Statut` | Choix (unique) | Prospect / Client / Inactif — pas de défaut, pas d'ajout manuel |

**Liste « CRM »** (identifiant stable = `Title` ; à créer, runbook `T-0026`)

| Libellé affiché | Nom interne | Type | Notes |
|---|---|---|---|
| Identifiant opportunité | `Title` *(existant)* | — | id stable, ex. `O-001` |
| Nom de l'opportunité | `NomOpportunite` | Texte | |
| Compte | `Compte` | Lookup → Comptes (`Title`) | **le rattachement** |
| Étape | `Etape` | Choix (unique) | Qualification / Proposition / Gagnée / Perdue — pas de défaut, pas d'ajout manuel |
| Montant | `Montant` | Nombre | € HT estimés |
| Échéance | `Echeance` | Date | signature attendue |
| Responsable | `Responsable` | Personne (unique) | porteur du développement de l'affaire |
| Code mission | `CodeMission` | Texte | renseigné à « Gagnée » — identifiant stable de la Mission ouverte (le lien opportunité → mission) |

## 3. La zone de proposition

Un espace **distinct de la source** où les agents écrivent les faits dérivés — marge calculée, imputation proposée, template anonymisé. Domicile concret câblé : **Liste « Zone-de-proposition »** (§2 bis). La promotion déplace le fait vers la source, de façon tracée. **On n'écrit jamais un dérivé directement dans la source.** La liste porte trois champs utiles : `Title` (libellé/identifiant), `Origine` (provenance) et `Contenu` (texte multiligne — le corps du dérivé, ex. synthèse d'entretien) : un dérivé riche vit entier dans la zone avant promotion ; la promotion mappe ensuite ses champs vers la liste cible.

Un **champ d'origine** qualifie la provenance de chaque dérivé. La valeur **« mémoire hebdo »** est réservée aux synthèses hebdomadaires candidates produites par le batch de **mémoire d'organisation** (`contrats/socle/memoire-organisation.md`) : domicile transitoire de cette mémoire en attendant T-0002b, validées ligne à ligne le vendredi (non-validé = oublié). La Liste « Zone-de-proposition » **existe au tenant depuis le 10 juin 2026** (champ d'origine posé — colonne « Origine ») et l'**écriture réelle y est outillée et prouvée** (chapeau `T-0002b` promue le 10 juin 2026) : les **nouveaux dérivés** s'écrivent dans la liste réelle via le connecteur ; les synthèses « mémoire hebdo » basculeront avec le batch (`T-0005`) et vivent sous `zone-proposition/memoire/` d'ici là.

Le **pipeline commercial** suit le même régime : une **opportunité détectée par un agent** (ex. repérée en atelier au fil d'un compte rendu) est un dérivé — elle naît en Zone-de-proposition (`Origine` = skill producteur) et sa promotion tracée la mappe vers la Liste « CRM » (§2 bis). La **saisie humaine directe** dans la Liste « CRM » reste une source ; un agent n'y écrit jamais.

## 4. État du câblage

Les domiciles concrets (site, listes, bibliothèques) sont **câblés — sessions des 7 et 10 juin 2026 ; écriture Graph faite (chapeau `T-0002b` promue)** (voir §2 bis). Le connecteur **Graph MCP en écriture** est **déployé, sécurisé et prouvé** (10 juin 2026) : endpoint MCP `https://ca-allia-mcp-graph.delightfulocean-1bf3f3c5.francecentral.azurecontainerapps.io/mcp` — entrée : **bearer OAuth 2.0** selon le modèle des identités appelantes (`identites-et-secrets.md` §2 — humains : identité Entra PKCE ; workloads : identité managée ; Easy Auth, sinon 401) ; sortie Graph : **identité managée, zéro secret**. L'écriture ne peut viser que la Liste « Zone-de-proposition » (garde-fou structurel, §3). Les **nouveaux dérivés** s'écrivent dans la liste réelle ; la simulation locale (`zone-proposition/`) ne subsiste que pour les synthèses « mémoire hebdo », qui basculeront avec `T-0005`.

Restent à confirmer par le gardien (runbook humain, hors agent) : l'activation de la **journalisation** sur `Ressources-RH` et `CVs`, et la projection des **droits d'accès** au moindre privilège (`organisation.md` §5). Aucun droit ne se règle à la main par un agent.

## 5. Modèle économique distribué (classeurs Excel)

Cette section décrit un **type d'objet distinct des listes** (§2–§2 ter) : des **classeurs
Excel à tables nommées**, coutés côté Graph par la **Workbook/Tables API** (et non la
Lists API). La règle « nom interne ASCII figé, libellé accentué » des colonnes de liste
ne s'y applique pas ; ce qui fait foi ici, ce sont les **noms de tables** et leurs
**en-têtes de colonnes**, figés à la création du gabarit.

### 5.1 Principe

- **Saisie humaine, dérivation par agent, lecture directe.** Chaque mission possède un
  classeur de **saisie** — la seule chose que l'humain édite (cf. §5.6). L'agent en dérive
  un **gabarit ERP** par mission ; la tour de contrôle lit les **gabarits actifs et le
  référentiel de coûts en direct** (`tour-de-controle.md` §4). **Il n'y a pas de classeur
  consolidé.**
- **Un gabarit, pas N formats.** Tous les gabarits sont dérivés d'un gabarit vierge unique
  promu au canon ; c'est la condition de la lecture agrégée.
- **Les coûts ne descendent jamais dans les fichiers mission.** Coûts jour des
  ressources et coûts de structure vivent **seulement** dans le **référentiel de coûts**,
  à audience restreinte (§5.3). Un responsable de mission ne voit pas le coût des ressources.
- **Une seule vérité par champ.** `Ressources-Profil` (liste) porte identité, grade,
  disponibilité ; le référentiel de coûts porte coûts et dates contractuelles. Aucun recouvrement.

### 5.2 Gabarit de pilotage par mission

- **Domicile canon** : le **présent contrat (§5.2) est l'unique source de vérité du schéma** des
  tables décrites ci-dessous. Le binaire `contrats/socle/gabarit-pilotage-mission.xlsx` est **retiré
  du rôle de souche d'instanciation** (conservé au canon comme trace historique, plus consommé par
  aucune primitive).
- **Instanciation** : un gabarit **par mission** — `gabarit-<CodeMission>.xlsx` — à la racine
  du dossier `06 - Gabarit ERP` de la bibliothèque « Documents » du site **Contrats et
  administratif** (`AlliaConsulting-Contratsetadministratif`). Règle : **1 mission = 1 gabarit**,
  un seul gabarit actif par mission à cette racine. Le gabarit précédent est archivé dans le
  sous-dossier `00 - Old` (versionnage visible ; ne garder à la racine que les gabarits actifs).
  Le modèle vierge de référence est `gabarit-pilotage-mission.xlsx` (même dossier). L'humain ne
  dépose JAMAIS le gabarit : il est initié, actualisé et archivé par l'agent (cf. §5.6).
  Coordonnées tenant (drive-id, folder-id de `06 - Gabarit ERP` et de `00 - Old`) : variables
  d'environnement `GRAPH_GABARIT_DRIVE_ID` / `GRAPH_GABARIT_FOLDER_ID` / `GRAPH_GABARIT_OLD_FOLDER_ID`,
  posées par runbook gardien — jamais en dur au canon.
- **Trois tables nommées** (en-têtes figés) :

`T_Affectations` — le prévisionnel de staffing et de charge.
| En-tête | Type | Notes |
|---|---|---|
| CodeMission | Texte | id stable de la mission |
| Ressource | Texte | identifiant Entra (couture `Ressources-Profil`) |
| Mois | Date (1er du mois) | granularité mensuelle |
| JoursPrevus | Nombre | budget de charge du mois |

`T_Imputations` — le réalisé déclaré.
| En-tête | Type | Notes |
|---|---|---|
| CodeMission | Texte | id stable |
| Ressource | Texte | identifiant Entra |
| Mois | Date (1er du mois) | |
| JoursRealises | Nombre | saisie du collaborateur |
| StatutValidation | Texte | `à valider` / `validé` — écrit par le responsable dans la saisie (§5.6), re-dérivé dans le gabarit par l'agent ; cockpit en lecture seule sur l'économique |

`T_Echeancier` — le plan de facturation de la mission.
| En-tête | Type | Notes |
|---|---|---|
| NumFacture | Texte | id stable de la facture |
| CodeMission | Texte | id stable |
| MoisCA | Date (1er du mois) | mois de rattachement du CA |
| MontantHT | Nombre | € |
| Echeance | Date | date d'échéance |
| Statut | Texte | `à émettre` / `émise` / `payée` |
| LienFacture | Texte | URL du PDF dans le dépôt Teams de la mission |

### 5.3 Référentiel de coûts (audience restreinte)

- **Domicile** : un **référentiel de coûts** dédié (classeur ou liste) dans un emplacement
  à **audience restreinte** (droits réglés par runbook humain — jamais par un agent ;
  `organisation.md` §5). Emplacement concret et périmètre d'accès : à câbler par le
  gardien, consigné en §5.5 quand réel (aucun chemin inventé ici). **Pas de classeur
  consolidé** : ce référentiel ne porte que les coûts, jamais l'agrégat des missions.
- **Nature** : **source à audience restreinte**. Les coûts jour des ressources et les
  coûts de structure y sont saisis/maintenus par un rôle habilité ; l'agent et la tour de
  contrôle les **lisent** (jamais un responsable de mission). Ces coûts ne descendent
  jamais dans les gabarits mission.
- **Deux tables propres au référentiel** (jamais dans les gabarits mission) :

`T_Ressources` — le référentiel de coûts.
| En-tête | Type | Notes |
|---|---|---|
| Ressource | Texte | identifiant : adresse **mail Allia** (salarié) ou adresse **mail du sous-traitant** (sous-traitant) — décision gardien du 14/07/2026 |
| Type | Texte | `salarié` / `sous-traitant` (le staffing du cockpit exclut les ST) |
| CoutJour | Nombre | € — donnée sensible, confinée au référentiel de coûts |
| DateEntree | Date | date contractuelle d'entrée |
| DateSortie | Date | vide si actif |

`T_Structure` — les coûts de fonctionnement Allia.
| En-tête | Type | Notes |
|---|---|---|
| Mois | Date (1er du mois) | |
| PosteCout | Texte | libellé du poste |
| Montant | Nombre | € |

### 5.4 Ce que la tour de contrôle calcule (à la volée)

La tour de contrôle calcule ces agrégats **à la volée** en lisant les gabarits actifs et le
référentiel de coûts (pas de classeur consolidé intermédiaire).

- **Staffing mensuel** (bandeau 1) : par salarié actif du mois (T_Ressources.Type =
  `salarié`, actif selon DateEntree/DateSortie), taux = JoursPrevus (réalisé =
  JoursRealises) ÷ jours ouvrés du mois ; barre = moyenne des taux ; sommet = effectif
  actif.
- **CA total** (bandeau 4) : par mois, budget = Σ (JoursPrevus × TJM) ; réalisé =
  Σ (JoursRealises × TJM). Le TJM par mission est porté par la brique Missions/CRM.
- **EBITDA** (bandeau 4) : CA − (jours × CoutJour) − T_Structure du mois.
- **Factures à émettre** (bandeau 5) : lignes T_Echeancier au statut `à émettre`.
- **Fraîcheur et anomalies** : la tour de contrôle horodate sa dernière lecture et liste les
  gabarits au schéma cassé (signalés, jamais ignorés silencieusement).

### 5.5 État du câblage

- Gabarit vierge `gabarit-pilotage-mission.xlsx` : **promu** au socle (PR #208).
- Extension MCP Graph **Workbook/Tables API** (lecture des saisies et du référentiel,
  écriture et archivage des gabarits par mission) : **à construire** (T-0031) — les outils
  Graph actuels ne couvrent que les listes. Microsoft Learn obligatoire avant ce code.
  Doc Graph REST v1.0 (Workbook/Tables).
- Agent de génération des gabarits + golden set : **à construire** (lit les saisies,
  régénère les gabarits, déclenche l'actualisation de la tour de contrôle).
- **Modèle : pas de classeur consolidé unique.** La tour de contrôle lit les **gabarits
  actifs + le référentiel de coûts en direct**. Les mentions antérieures d'un
  `pilotage-consolide.xlsx` sont caduques.
- Domiciles réels (drive-id/folder-id des trois couches — saisie, gabarit `06 - Gabarit ERP`
  + `00 - Old`, référentiel de coûts) : **variables d'environnement** posées par runbook
  gardien, jamais au canon. **Référentiel de coûts — domiciles réels** (vérifiés sur le tenant le 14/07/2026,
  site `AlliaConsulting-Contratsetadministratif`) : `T_Structure` dans « 07 - Coût de Structure »
  /`referentiel-structure.xlsx` et `T_Ressources` dans « 08 - Coût Masse salariale & Indep »
  /`referentiel-ressources.xlsx` ; coordonnées tenant (drive-id/item-id) en variables d'environnement
  (runbook gardien), jamais au canon. Sa **projection de droits** (audience restreinte) reste réglée
  par runbook humain (`organisation.md` §5). Le **skill consommateur** des primitives Workbook (T-0031)
  est `skills/consolidation-pilotage/`.

### 5.6 Couche de saisie et boucle d'actualisation (agent)

- **Saisie (surface équipe, source humaine).** Classeurs `saisie-...xlsx` à la racine de la
  bibliothèque « Documents » du site **Management et Gestion**
  (`AlliaConsulting-ManagementetGestion`). `00 - Template Mission` porte le template de saisie ;
  `01 - Missions cloturées` archive les missions terminées. **L'humain n'édite QUE la saisie**
  (y compris les gestes économiques — affectations, validation d'imputations, statut
  d'échéancier) ; il ne le fait PAS depuis le cockpit, en **lecture seule** sur l'économique
  (`tour-de-controle.md` §1, §4). Coordonnées tenant : `GRAPH_SAISIE_DRIVE_ID` /
  `GRAPH_SAISIE_FOLDER_ID` (runbook gardien). **Convention de nommage** :
  `saisie-<CodeMission>-<Libellé>.xlsx` — le CodeMission est porté par le nom (`^saisie-(\d+)-`), le
  libellé qui suit est libre, casse libre. **Métadonnées de modification différées en co-édition**
  (Excel Online) : le **contenu fait foi**, pas l'horodatage `lastModifiedDateTime`.
- **Trois domiciles distincts, trois audiences** : saisie (gestion opérationnelle), gabarit
  ERP (contrats/administratif) et référentiel de coûts (audience restreinte, §5.3) vivent sur
  des emplacements séparés. L'agent **écrit** uniquement les gabarits (cible figée par
  construction, cf. T-0031, sur le modèle de `deposer_document_mission`) et **lit** les saisies
  et le référentiel ; il n'écrit jamais les coûts.
- **Boucle agent** : lun→ven, 05h00 et 13h00 (heure de Paris). À chaque passage, l'agent lit les
  saisies ; pour toute saisie dont `lastModifiedDateTime` est postérieur au dernier passage, il
  (1) archive le gabarit courant de la mission dans `00 - Old`, (2) régénère le gabarit
  `gabarit-<CodeMission>.xlsx`, (3) déclenche l'actualisation de la tour de contrôle. **Si le gabarit d'une mission n'existe pas
  encore, l'agent l'instancie** (`workbook_instancier_gabarit`, cran `instancier_gabarit_pilotage`)
  par **FABRICATION SERVICE** (`workbook_instancier_gabarit` v2 : création du classeur par le service
  Excel + `tables/add` sur les plages d'en-têtes §5.2), avant de régénérer : l'instanciation est
  **SYSTÉMATIQUE et machine** (décision gardien du 14/07/2026), plus jamais un geste humain ; **il n'y a
  plus de souche binaire**.
- **Piège de ciblage** : le tenant est `alliaconsuling` (une seule « t ») mais les URL de sites
  portent `AlliaConsulting-...` (deux « t »). Vérifié sur le réel le 14/07/2026.
