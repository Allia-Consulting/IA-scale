# Plan de construction du SI augmenté — Allia

> Statut : promu — contrat socle · fait foi.
> Changelog : v0.11 → promu, 5 août 2026 (S49, solde de session — consignation de ce que l'usage du 05/08 a démenti ou découvert) : ajout du §18 — treize points nommés, non ouverts. Corrections **par renvoi** de deux constats antérieurs, les sections visées n'étant **pas réécrites** : §17.3.ii **démenti sur le réel** (l'opportunité « Cockpit M365 » était Gagnée et son `CodeMission` alloué depuis le 24/07 — un constat d'audit vieillit plus vite qu'un contrat) et **§13.3 intégralement soldé** le 24/07 (reste du §13 : le seul point 1). Découvertes consignées : la cause réelle de « Missions actives : 2 » (la Liste « Missions » n'était alimentée par aucun geste outillé — refermé par la PR #302), un **défaut de conception de la cascade qu'on vient de graver** (`creer_ligne_mission` DEVINE `DateDebut` faute de date de réalisation au CRM — correctif `DateDebutPrevue` à trancher **avant** de coder `T-0040`), un **critère d'acceptation faux** dans `T-0051` (zéros budgétés réels ≠ absent), la **3e occurrence** du défaut `Title` `O-NNN` (premier commit de `T-0049`), la dégradation **silencieuse** d'`impact.py` sans PyYAML, deux restes d'espaces documentaires (avant-vente `MES` — concept manquant du modèle ; 4e segment de « Siteflow »), l'**institution hebdomadaire de la revue de pipe** avec trois manques du skill v1.0 à graver en v1.1 (barème « Fraîcheur », dimension de concentration client, seuil de matérialité) et les décisions de pipe du jour. Normalisation de `backlog/chantiers/T-0039.yaml` dans la même PR (dernière fiche dont `cran:` portait une phrase → `cran: valide`, prose reportée en note sans perte, `statut` et `note_epreuve` non touchés) : 60 fiches sur 60 au vocabulaire contrôlé. **Consignation seule : aucun outil, aucun chantier ouvert, aucun statut modifié, aucune écriture tenant.** Sections et notes existantes non réécrites. Aucune autre section modifiée. v0.10 → promu, 2 août 2026 (S47, audit de fin de construction, session Cowork) : ajout du §17 — état des lieux d'audit au HEAD `0ac6d3a5` (cinq chaînes métier construites et éprouvées, aucune en récurrence : la fin de construction est un problème d'USAGE), ordre de bataille usage-first S48+, nommage des deux restes S46 (échéancier de facturation mission 4 = geste gardien ; cohérence CRM ↔ chaîne économique mission 4), consignation de la caducité de facto de T-0041 (octroi joué le 01/08, épreuve T-0045 1/2) et des étiquettes caduques (doctrine v1.11), classification « priorité non essentielle » confirmée (délégation, optimisation technique, sauvegarde, sécurité). Consignation seule : aucun outil, aucune écriture tenant, aucun statut de chantier modifié. Notes et sections existantes non réécrites. Aucune autre section modifiée. v0.9 → promu, 1er août 2026 (S46, consignation des arbitrages gardien métier du 01/08 au soir) : **§15.3 tranché** — le référentiel 550 €/j fait foi (la facturation 500 €/j du sous-traitant n'entre pas dans le coût, aucune correction du référentiel), hygiène connexe corrigée par le gardien le même soir (`Type` → `sous-traitant`, `DateEntree` de Guillaume → 2026-09-01) ; **§16.3 tranchée** — saisie RÉVISÉE (historique de versions SharePoint, éditeur unique = le gardien ; sources vivantes, la dernière version fait foi, §5.6 inchangée), tranchée par l'auteur et jamais par recoupement. Deux arbitrages connexes consignés à `backlog/chantiers/T-0045.yaml` (note S46) : `CoutJour` du gardien = 0 ASSUMÉ et clôture du point (a) de `note_solde`. **Consignation seule : aucun outil, aucun canon, aucune écriture tenant.** Notes et points existants non réécrits. Aucune autre section modifiée. v0.8 → promu, 1er août 2026 (S46, arbitrage gardien « merge vaut promotion ») : §4 — **complément** ajouté à la suite de la convention de vocabulaire du 6 juillet (celle-ci **non réécrite**) : pour un contrat ou un skill, `promu` = **mergé au canon par la porte humaine** (doctrine §7, note d'exécution v1.11) ; l'étiquette « candidat » ne désigne plus que l'état d'une PR ouverte ; le cycle des chantiers `à_faire → en_cours → soldé` est inchangé, son passage étant désormais sous porte humaine (`backlog/chantiers/` chemin sensible, PR #291). Fiches et changelogs historiques non réécrits. Aucune autre section modifiée. v0.7 → candidat, 24 juillet 2026 (1c, hygiène CRM nommée) : ajout du §13 — trois restes d'hygiène de la brique CRM (`T-0026`) surfacés par la cascade `T-0038` du 24/07, **nommés, non ouverts** (promotion tracée Zone → CRM ; correctif du `Title` posé par le geste cockpit « nouvelle opportunité » ; clics gardien d'hygiène tenant). Nommage seul : aucun outil, aucun canon, aucune écriture tenant. Aucune autre section modifiée. v0.6 → promu, 6 juillet 2026 (toilettage canon d'hygiène ; mergé PR #171 `7d16ccc`) : §4 — convention de vocabulaire clarifiée : `promu` réservé à la boucle de promotion des **contrats** ; cycle de vie d'un **chantier** = `à_faire → en_cours → soldé` (l'étape « mergé, pas encore éprouvé » se lit dans `execution:`, non dans un statut `promu`). Fiches historiques Phase 0/1 non réécrites. Aucune autre section modifiée. v0.5 → promu, 5 juillet 2026 : §9 T-4.1 — incise nommant la brique CRM (Cœur de métier / Développement commercial : entités Compte / Opportunité, pipeline commercial Liste « CRM » et lien opportunité → mission, chantier T-0026), symétrique de l'incise recrutement v0.3. Aucune autre section modifiée. v0.4 → promu, 5 juillet 2026 (toilettage d'entrée en Phase 2) : §12 — hypothèse 1 révisée (Phase 2 engagée sans ingénieur dédié, leviers de saturation nommés) ; hypothèse 6 close (réalisée — matière portée par doctrine §10 bis et organisation.md §3/§4.1). Aucune autre section modifiée. v0.3 → promu, 16 juin 2026 : §9 T-4.1 — incise nommant la capacité Talent & RH / Recrutement comme cible de phase 4 (outil vue candidat T-0013, exécutant le cadre RGPD recrutement promu). Mention légère, aucun autre changement de fond. v0.2 → promu : passage par la boucle de promotion (session fondation 7 juin 2026). *(v0.2 : alignement sur la feuille de route et les grades de la présentation « Talents & recrutement ».)*
> Domicile cible : `dépôt de fondations (GitHub)`, chemin `/backlog/plan.md`.
> Adossé à : `/doctrine/doctrine.md`. La doctrine dit *le pourquoi et les règles* ; ce plan dit *le comment et le chantier*. Les deux forment le canon socle que Claude Code résout à l'exécution.
> Ce document est écrit pour deux lecteurs : **toi** (le gardien, qui exécute l'amorçage) et **les agents** (qui consommeront ensuite les tâches qu'il référence). Il ne se modifie pas dans une copie : il évolue par la boucle de promotion (§11).

---

## 0. Mode d'emploi et principes de pilotage

### 0.1 La récursion à tenir en tête
Le système à bâtir *est lui-même* la machine qui gouverne les agents. On ne peut donc pas demander aux agents de se gouverner avec une machinerie qui n'existe pas encore. La construction se fait en deux temps :

- **Amorçage (Phase 0)** : *toi*, à la main, avec Claude Code comme binôme, sous ta validation systématique. Tu poses le squelette minimal qui rend les agents gouvernables.
- **Relais (Phases 1→4)** : à partir du moment où la machinerie minimale tient, les agents **proposent** (candidats / PR) et tu **promeus** (gardien). Ils construisent alors le reste — y compris l'amélioration de la machinerie elle-même, qui repasse par la même boucle.

### 0.2 La construction suit ses propres crans
On bâtit le système comme il est censé tourner. Chaque activité de ce plan porte un cran :
- créer/éditer un fichier dans une branche = **auto** (réversible, interne, local) ;
- promouvoir un contrat socle = **validé** (porte humaine = toi) ;
- toucher la configuration M365, la sécurité, les droits, un secret/credential = **runbook humain** (ni Claude ni un agent ne le font — voir §2).

### 0.3 Gradient de transfert de contrôle

| Phase | Qui propose | Qui valide / promeut | Cran dominant |
|---|---|---|---|
| 0 — Amorçage | Toi (+ Claude Code en binôme) | Toi, à chaque pas | manuel |
| 1 — Tranche verticale | Agents | Toi, sur tout | validé |
| 2 — Qualité | Agents | Toi sur le socle ; agent-gardien auto-approuve le faible risque | validé / auto par politique |
| 3 — Résolution | Agents + ingénierie | Toi sur le socle | validé |
| 4 — Généralisation | Agents + animateurs délégués | Toi (socle) ; animateurs (local, procédure allégée) | délégué |

### 0.4 Alignement avec la trajectoire et les grades de la firme

Le plan se cale sur la feuille de route de la présentation « Talents & recrutement » :
- **Fondation** (cap 50) — Phases 0 à 2 : amorçage, première tranche verticale, qualité. Gardien unique (toi).
- **Ouverture** (cap 100) — Phase 3 et début de Phase 4 : couche de résolution, premiers animateurs délégués.
- **Acquisition** (cap 200) — Phase 4 à pleine maturité : délégation large, fédération de la promotion.

Côté rôles : tout collaborateur entre comme **utilisateur**, quel que soit son grade ; un **animateur** est typiquement un Manager ou un Associé qui pilote un savoir-faire ; le **gardien** reste au niveau firme. Les grades (Consultant / Manager / Associé) relèvent de la réalisation volatile — ils vivent dans les documents talents, pas dans le backlog.

---

## 1. Principes de construction (mes convictions)

1. **Squelette d'abord, puis une seule tranche verticale.** On ne câble pas les 30 capacités d'un coup. On prouve que le cycle complet *pull → action → proposition → promotion → propagation* tourne sur **une** capacité réelle, avant de généraliser.
2. **Le plan est auto-hébergé.** Le backlog vit dans le dépôt, versionné, tâche par tâche. Les agents le pull ; il évolue par promotion. Pas de plan figé dans un document mort.
3. **Les contrats sont les coutures de l'évolution.** Un composant (M365, un skill, un modèle) peut changer parce qu'il est caché derrière un contrat stable que les consommateurs résolvent. Faire évoluer = changer l'implémentation derrière un contrat inchangé, via la boucle. C'est *ça*, « le faire vivre ».
4. **Pull réel là où c'est possible, refresh manuel assumé ailleurs.** Claude Code résout vraiment la doctrine depuis le dépôt à chaque tâche. La surface chat/utilisateur, elle, reste rafraîchie à la main en v1 — la couche de résolution automatique est un chantier nommé (Phase 3), pas un réglage.
5. **Le dérivé n'est jamais le saisi.** Tout fait calculé par un agent atterrit dans une *zone de proposition* avant promotion tracée. La source unique ne se corrompt jamais en silence.
6. **L'autonomie hausse l'exigence d'évaluation, elle ne la baisse pas.** Tant que les evals et l'observabilité ne tiennent pas (Phase 2), on garde l'humain dans la boucle au cran validé.
7. **L'architecture sert la culture du collectif.** « Pas de mon périmètre », le cross-selling qui compte pour tous, l'intelligence collective : le canon partagé (pull, jamais copie) en est la forme technique. C'est pourquoi on passe à l'échelle par le canon, jamais par l'augmentation individuelle de chacun.

---

## 2. Garde-fous — ce que ni les agents ni Claude ne font (→ runbook humain)

Ces actions restent les tiennes ; pour chacune, le plan produit un *runbook* précis que tu exécutes :
- saisir des identifiants, secrets, clés d'API, jetons ;
- créer des comptes, configurer l'authentification (OAuth/SSO) ;
- modifier des droits, partages ou permissions (M365, dépôt, dossiers) ;
- paramétrer le tenant M365, la sécurité ou la résidence des données ;
- supprimer définitivement des données ;
- prendre un engagement juridique ou financier ;
- promouvoir un contrat socle (porte humaine = toi).

**Exception gouvernée (dès qu'il y a délégation).** Les droits M365 changent uniquement via un *réconciliateur au moindre privilège* qui projette une décision **déjà promue** dans le guide (voir `organisation.md` §5) ; la mise en place du privilège lui-même (app registration, consentement admin, secret) reste ton runbook. Personne — ni toi à la main, ni Claude — n'édite un droit hors de cette chaîne `guide → Claude → M365`, et la mise en production reste sous le contrôle du gardien.

Limite assumée du planificateur : je ne connais que tes trois documents et cette conversation, et mon socle de connaissances s'arrête à janvier 2026. Les détails exacts de Claude Code, des Skills, de MCP et de l'API Microsoft Graph sont à revérifier sur la documentation officielle (`docs.claude.com`, doc Microsoft Graph). Ce plan est un échafaudage solide à versionner, pas un plan garanti.

---

## 3. Structure cible du dépôt de fondations

```
/                              dépôt de fondations (GitHub)
  README.md                    point d'entrée : comment lire, où est la vérité
  CLAUDE.md                    contexte de résolution pour Claude Code (pull doctrine au démarrage)
  /doctrine/
    doctrine.md                contrat socle racine (4 rôles, principes, crans, boucle)
  /contrats/
    /socle/
      modele-donnees.md        mapping des faits vers M365 (la couture M365)
      table-des-crans.yaml      machine-readable : type d'action → cran
      anonymisation.md          champs, seuil, déclencheur (RGPD / AI Act)
      organisation.md           qui anime quel périmètre · règles de délégation
      design-system.md
    /local/
      <perimetre>/...          contrats locaux, un par animateur (plus tard)
  /skills/
    <skill>/SKILL.md           skills versionnés, activables
  /agents/
    <agent>/profil.yaml        profil = composition de skills + cran par type d'action
  /backlog/
    plan.md                    CE plan (couche prose)
    chantiers/*.yaml           tâches agent-consommables
  /.github/
    pull_request_template.md   gabarit de candidat
    CODEOWNERS                 le gardien (toi) sur /doctrine et /contrats/socle
    workflows/conformite.yml   l'agent-gardien (contrôle de conformité en CI)
  /journal/                    journal d'approbation (historique Git + releases)
```

Le `journal d'approbation` exigé par la doctrine est porté par l'historique Git lui-même (qui a approuvé/mergé quel SHA, quand) ; on n'invente pas un second registre.

---

## 4. Format des tâches (le contrat entre le plan et les agents)

Chaque tâche du backlog est un fichier YAML que l'agent sait lire et exécuter. Schéma :

```yaml
id: T-0001
titre: "Rédiger le SKILL de cadrage de mission"
capacite: "Delivery / Cadrage & lancement"     # rattachement à la carte de capacités
phase: 1
type_action: "edition_contrat_local"           # sert à déduire le cran
cran: "validé"                                  # résolu via table-des-crans.yaml
produit:
  - "/skills/cadrage-mission/SKILL.md"
depend_de: ["T-0000"]                           # dépendances dures
contrats_concernes: ["/contrats/socle/design-system.md"]
criteres_acceptation:                           # Definition of Done, vérifiable
  - "Le skill produit un brief structuré à partir d'une proposition gagnée"
  - "Aucun contrat consommateur n'est cassé (vérifié par l'agent-gardien)"
rayon_impact: "local"                           # rempli/contrôlé par l'agent-gardien
statut: "à_faire"                               # à_faire | en_cours | soldé | abandonné (historique : candidat/promu — voir convention ci-dessous)
```

Cycle de vie d'un **chantier** : `à_faire → en_cours → soldé`. **SOLDÉ = construit/mergé au canon ET ÉPROUVÉ SUR LE RÉEL** (exécution réelle sur vraie donnée tenant).

> **Convention de vocabulaire (toilettage du 6 juillet 2026).** Le mot **promu** appartient en propre à la **boucle de promotion des contrats** (doctrine §7) : un *contrat* candidat devient *promu* quand le gardien le merge au canon. Pour un **chantier**, l'état terminal est **soldé** (mergé au canon *et* éprouvé sur le réel) ; l'étape intermédiaire « mergé, pas encore éprouvé » se lit dans l'`execution:` de la fiche, pas dans un statut `promu`. Les fiches **historiques** (Phase 0/1) portant `statut: promu` ou `candidat` ne sont **pas réécrites** — elles restent lisibles telles quelles ; la convention vaut pour les chantiers **à venir**.

> **Complément (arbitrage gardien du 1er août 2026, S46).** Pour un contrat ou un skill, **promu = mergé au canon par la porte humaine** (merge vaut promotion, doctrine §7 — note d'exécution). L'étiquette « candidat » ne désigne plus que l'état d'une **PR ouverte**. Les fiches et changelogs **historiques ne sont pas réécrits**. Le cycle des chantiers (`à_faire → en_cours → soldé`) est **inchangé** — et le passage d'un statut de chantier est désormais **sous porte humaine** (`backlog/chantiers/` chemin sensible de l'avis d'impact, PR #291).

Règle : un agent ne traite **que** des tâches dont les dépendances sont **satisfaites** (`soldé` pour un chantier, `promu` pour un contrat), et n'écrit jamais directement le pointeur canonique — il ouvre une PR.

---

## 5. Phase 0 — Amorçage (mené par TOI)

But unique de la phase : atteindre le **niveau agentique**, défini par le test de sortie A0.9. Chaque activité est faite par toi, Claude Code en binôme, et validée par toi avant la suivante.

### A0.1 — Initialiser le dépôt et l'arborescence
- **Produit** : la structure du §3, vide mais en place ; `README.md` qui pose « une seule vérité, on référence on ne copie pas ».
- **Cran** : auto (création de fichiers en branche).
- **Done** : l'arborescence existe sur `main`, protégée (cf. A0.4).

### A0.2 — Configurer la résolution Claude Code
- **Objectif** : que Claude Code, au démarrage d'une tâche, *résolve* la doctrine et les contrats depuis le dépôt (pull réel), et non une copie.
- **Produit** : `CLAUDE.md` décrivant où sont la doctrine, les contrats, la table des crans, et la règle « on n'édite jamais une règle hors du dépôt ».
- **Runbook humain** : authentification de Claude Code et accès au dépôt (clé/credential = toi).
- **Done** : depuis un poste, Claude Code ouvre le dépôt, cite la doctrine à jour, et refuse une action hors cran.

### A0.3 — Canoniser la doctrine et les contrats socle minimaux
- **Objectif** : transformer tes PDF en vérité versionnée et exploitable.
- **Produit** :
  - `/doctrine/doctrine.md` (reprise fidèle de la doctrine v1) ;
  - `/contrats/socle/table-des-crans.yaml` (machine-readable : `type_action → {réversible, sort_firme, rayon, cran, qui_décide}`) ;
  - `/contrats/socle/anonymisation.md` (champs, seuil, déclencheur — **décision métier : toi**) ;
  - `/contrats/socle/modele-donnees.md` (où vit chaque fait dans M365 — la couture M365) ;
  - `/contrats/socle/design-system.md` (au minimum un squelette).
- **Cran** : validé (contrats socle → promotion par toi).
- **Done** : un agent peut résoudre « quel cran pour l'action X ? » en lisant `table-des-crans.yaml`.

### A0.4 — Outiller la boucle de promotion (PR)
- **Objectif** : faire de la boucle §7 de la doctrine un workflow GitHub concret.
- **Produit** : `pull_request_template.md` (candidat = PR, rattaché à un SHA) ; `CODEOWNERS` plaçant le gardien sur `/doctrine` et `/contrats/socle` ; protection de branche imposant revue + statut CI vert avant merge.
- **Runbook humain** : réglages de protection de branche et droits dépôt (= toi).
- **Done** : aucune écriture sur `main` sans PR approuvée ; un revert ramène l'état précédent en une action.
- **État réel (vérifié 10 juillet 2026, ruleset `main-protection` id 17366850, enforcement actif)** : PR obligatoire, suppression et force-push bloqués. Le **statut CI est REQUIS et bloquant** : le ruleset impose 3 checks `required_status_checks` — `Avis d'impact`, `Harnais skills`, `Tests garde-fous server.py`. Un rouge sur l'un d'eux bloque le merge (éprouvé sur le réel le 10/07/2026 : PR d'épreuve #180 dégradant un garde-fou d'intégrité → `Tests garde-fous server.py` ET `Avis d'impact` rouges, merge refusé par main-protection, PR fermée sans merge). La CI consultative de la v0 est révolue.

### A0.5 — Premier squelette d'agent-gardien (contrôle de conformité v0)
- **Objectif** : la « tête-agent » du gardien, version minimale, qui s'exécute sur chaque PR.
- **Produit** : `.github/workflows/conformite.yml` lançant Claude Code en mode non-interactif (à vérifier sur la doc) qui, sur le diff d'une PR : (a) liste les consommateurs des fichiers modifiés (= rayon d'impact basique), (b) vérifie qu'aucun contrat consommateur n'est cassé, (c) poste un **avis d'impact** en commentaire, (d) marque le statut pass/échec.
- **Runbook humain** : la clé d'API utilisée par l'Action en CI (= toi ; secret de dépôt).
- **Done** : ouvrir une PR déclenche l'avis d'impact ; une PR qui casse un contrat est marquée en échec.
- **Honnêteté** : v0 reste fruste (impact par recherche de références textuelles). Le calcul d'impact fin est un objet de Phase 2.

### A0.6 — Premier profil d'agent + premier skill
- **Produit** : un `/agents/<agent>/profil.yaml` (composition de skills + cran par type d'action) et un `/skills/<skill>/SKILL.md` simple et réel (ex. : produire un compte rendu structuré).
- **Cran** : skill = contrat local (validé, procédure allégée) ; profil socle au départ (validé).
- **Done** : l'agent, lancé via Claude Code, charge son profil depuis le dépôt et exécute le skill.

### A0.7 — Connecter M365 et poser la zone de proposition
- **Objectif** : l'agent lit/écrit les *données* dans M365 via MCP, et écrit tout fait dérivé dans une zone de proposition séparée.
- **Produit** : conformément à `modele-donnees.md`, l'emplacement des faits (sites/Listes/dossiers) et une **zone de proposition** distincte de la source.
- **Runbook humain** : connexion MCP M365, création des emplacements, **droits et sécurité** (= toi).
- **Done** : l'agent lit un fait réel et écrit une proposition au bon endroit, sans toucher la source.

### A0.8 — Amorcer le backlog
- **Produit** : ce `plan.md` promu, plus 1 à 3 fichiers `chantiers/*.yaml` au format §4 (la première tranche verticale).
- **Cran** : validé (le backlog est du socle).
- **Done** : il existe une tâche `à_faire` dont toutes les dépendances sont `promu`.

### A0.9 — TEST DE SORTIE = niveau agentique atteint
**Critère unique, vérifiable, qui clôt la Phase 0 :**
> Un agent lit *une* tâche du backlog, l'exécute, ouvre une PR (candidat) ; l'agent-gardien poste l'avis d'impact ; tu promeus (merge) ; le changement se propage (le run suivant de l'agent pull la nouvelle version) ; et tu peux annuler en une action.

Quand ce cycle passe de bout en bout, la machinerie minimale tient : **les agents peuvent désormais construire le reste, tâche par tâche, sous ta promotion.**

---

## 6. Phase 1 — Tranche verticale « gain d'affaire »

On déroule de bout en bout le scénario de ton document de bienvenue, *par les agents* (ils proposent, tu valides tout).

- **T-1.1** Skill « cadrage de mission » : du brief gagné → espace de mission, imputations, templates adaptés (cran : actions internes réversibles = auto ; notification équipe = notifié).
- **T-1.2** Skill « kick-off » : génération de la proposition et du support, en consommant le design system (sortie firme/client = **validé**).
- **T-1.3** Agent « mission » composant ces skills, avec son `profil.yaml` et ses crans par action.
- **T-1.4** Branchement M365 : création réelle de l'espace SharePoint (auto), écriture des imputations en zone de proposition puis promotion tracée.
- **Critère de sortie** : un gain d'affaire réel déclenche, sous tes validations, la création de la mission ; chaque action a respecté son cran ; tout dérivé est passé par la zone de proposition.

> C'est ici que se vérifie ta vraie exigence : une amélioration d'un skill, une fois promue, profite à *toutes* les futures missions, parce qu'on référence et qu'on ne copie pas. L'IA passe à l'échelle par le canon partagé, pas par augmentation individuelle.

---

## 7. Phase 2 — Qualité : evals, observabilité, agent-gardien renforcé

La barrière qui rend l'autonomie tenable. **Pièce de génie logiciel — à porter avec soin ; un agent échafaude, mais la conception relève d'un humain.**

- **T-2.1** Evals par skill et par agent (jeux de cas, attendus, scoring) ; non-régression des prompts/skills en CI.
- **T-2.2** Calcul d'impact fin dans l'agent-gardien (qui consomme, combien d'artefacts, quelles missions en cours).
- **T-2.3** Observabilité en production : traçabilité des actions, métriques de qualité, journal d'audit consultable.
- **T-2.4** Auto-approbation du faible risque *contre politique* par l'agent-gardien ; le reste remonte à toi.
- **Critère de sortie** : une PR à faible risque et conforme passe sans toi ; toute régression d'un skill est bloquée par la CI. *(Atteint et éprouvé — **Phase 2 close le 13/07/2026** : chapeau `T-0020` soldé, ses cinq sous-items `-a..-e` soldés ; l'agent-gardien auto-merge le faible risque conforme (#189, #190, #193, #194, #195) et la CI bloque les régressions (épreuves rouges #154, #180) ; les 3 KPI d'organisation s'affichent sur le tenant — cockpit publié à `SitePages/Tour-de-contrôle.aspx`, épreuve `docs/epreuves/2026-07-13-t-0020-d-kpi-cockpit.md`.)*

---

## 8. Phase 3 — Couche de résolution automatique

Le chantier nommé (doctrine §8) : faire que les surfaces (Projets Claude, outils, cockpit) résolvent la doctrine depuis le dépôt à l'exécution, sans rafraîchissement manuel.

- **T-3.1** Mécanisme de résolution à portée : nouveaux usages → nouvelle version ; missions en cours → version figée sauf migration explicite (un livrable client ne change pas d'apparence en cours de route).
- **T-3.2** Suppression du refresh manuel des surfaces utilisateur.
- **Critère de sortie** : promouvoir un pointeur propage la nouvelle version aux consommateurs sans intervention manuelle, et la vérification confirme la résolution.

---

## 9. Phase 4 — Généralisation, animateurs, cockpit utilisateur

- **T-4.1** Étendre capacité par capacité selon la carte (chaque capacité = un contrat + des skills + un agent), les agents produisant les candidats ; côté Talent & RH, l'outil « vue candidat & suivi d'entretiens » (`T-0013`) exécutera le cadre RGPD recrutement déjà promu ; côté Développement commercial, la brique **CRM** (`T-0026`) instancie les entités Compte / Opportunité et le pipeline commercial (Liste « CRM ») dans `modele-donnees.md`, avec le lien opportunité → mission — une affaire gagnée ouvre une mission, où se branche la tranche verticale « gain d'affaire » (§6). Premières cibles concrètes, tirées des offres et de la promesse « consultant augmenté » : les quatre piliers (IT Strategy, Design Authority, Réduction des coûts, Transformation & Agilité) et les outils d'analyse prêts (cost analysis, SAM, CIO office, PPM, cartographie) — chacun devient un skill versionné, réutilisable d'une mission à l'autre.
- **T-4.2** Introduire les **animateurs** : RBAC, délégation de la promotion *locale* par domaine (procédure allégée), le gardien conservant le socle — c'est ta « fédération de la promotion » pour passer le cap des 50-200. C'est aussi la trajectoire promise au collaborateur : entré *utilisateur*, il peut se voir confier l'animation d'un périmètre (typiquement à partir du grade de Manager ou d'Associé).
- **T-4.3** Bâtir le **réconciliateur de droits** (`organisation.md` §5) : la décision de délégation promue dans le guide est projetée, au moindre privilège et en idempotent, sur les groupes Entra par périmètre ; SSO unique (guide / Claude / M365) ; porte humaine maintenue à la promotion ; app registration et secret posés par runbook. Aucun droit hors de la chaîne `guide → Claude → M365`.
- **T-4.4** Concevoir le **cockpit de l'utilisateur quotidien** (doctrine §10) : le vrai test d'adoption.
- **Critère de sortie** : un nouvel animateur fait évoluer son périmètre sans toucher au socle ; sa délégation, une fois promue, ouvre ses accès M365 par réconciliation sans qu'aucun droit n'ait été saisi à la main ; et un utilisateur non technique opère depuis le cockpit.

---

## 10. Faire vivre et transformer les composants

La question « et si M365, Claude ou GitHub changent ? » se règle par les coutures, pas par une réécriture :
- **Changer le stockage des données** (M365 → autre) : on ne réécrit pas les agents, on réécrit l'implémentation derrière `modele-donnees.md` ; les consommateurs résolvent le même contrat.
- **Changer une méthode** (un meilleur livrable) : nouvelle version d'un `SKILL.md`, promue ; tous les agents la pull.
- **Changer le moteur d'exécution** (Claude Code → autre) : tant que l'agent résout la doctrine et respecte les crans, le squelette ne bouge pas.
- **Changer une règle** (crans, design system) : candidat → avis d'impact → promotion ; rollback toujours possible.
- **Changer un droit d'accès** (attribuer / révoquer une délégation) : jamais à la main — on modifie la décision dans le guide (promotion par le gardien), un réconciliateur au moindre privilège la projette sur les groupes Entra ; la mise en production reste sous le contrôle du gardien, et le retour arrière (repointage) vaut aussi pour les accès.

Règle d'or : ce qui change souvent (outils, agents, contenu) s'accroche à ce qui ne change presque jamais (capacités, contrats, rôles). On ne fait jamais bouger une couture sans passer par la boucle.

---

## 11. Comment ce plan évolue (auto-hébergé)

Ce `plan.md` et les `chantiers/*.yaml` sont du **socle**. Toute évolution — réordonner, ajouter une tâche, redéfinir un critère — est un candidat : on prépare via Claude Code, l'agent-gardien évalue l'impact, tu promeus. Le plan devient ainsi une chose vivante gouvernée par sa propre doctrine, exactement comme le reste du SI.

---

## 12. Hypothèses prises (à corriger par le gardien)

1. Tu es seul gardien ; pas d'ingénieur dédié à ce stade. *(Révisée le 05/07/2026, à l'entrée en Phase 2 :)* la Phase 2 est engagée sans ingénieur dédié et la vélocité a tenu — harnais d'evals soldé (T-0020-a), porte de promotion outillée par la machine. En cas de saturation du gardien, les leviers sont la fédération de la promotion (registre `organisation.md` §4.1, première délégation active) et l'agent-gardien (T-0020-c) — pas un recrutement d'urgence.
2. Les agents agissent sur un dépôt GitHub **réel** (réversible, sous porte de PR) ; pour M365, droits et sécurité, ils ne produisent que des **runbooks** que tu exécutes.
3. Périmètre v1 = squelette + tranche verticale « gain d'affaire ». Le reste suit en Phase 4.
4. Couche de résolution automatique **différée** (Phase 3) ; pull réel côté Claude Code/MCP, refresh manuel des surfaces utilisateur en v1.
5. Le backlog agent-consommable dans le dépôt est le format de sortie retenu, avec ce document comme couche prose par-dessus.
6. *(Close le 05/07/2026 — réalisée, plus une hypothèse :)* l'articulation rôles / grades / trajectoire vit au §10 bis de la doctrine (promu) ; le « qui répond de quoi » — délégations et titulaires — vit au registre `contrats/socle/organisation.md` (§3, §4.1). La doctrine v1.8 renvoie au registre comme seule source de vérité des délégations.

> Pour corriger une hypothèse, ne modifie pas ce fichier directement : ouvre un candidat. Le plan se gouverne comme il prêche.

---

## 13. Restes d'hygiène CRM — nommés, non ouverts (exposés par l'usage du 24 juillet 2026)

Trois restes d'hygiène de la brique CRM (`T-0026`), surfacés par la cascade `T-0038` du 24/07. **Nommés ici, non encore ouverts** — aucun outil construit, aucun canon modifié, aucune écriture tenant :

1. **Promotion tracée Zone → CRM** — outiller la promotion des opportunités *dérivées* de la Zone-de-proposition vers la Liste « CRM » (réserve restante de `T-0026` ; aujourd'hui geste gardien).
2. **Correctif du geste cockpit « nouvelle opportunité »** — le geste ne pose pas l'identifiant stable `Title` (`O-NNN`, canon `modele-donnees.md`), défaut constaté le 24/07 sur les items 4 et 5 de la Liste « CRM » ; à corriger côté cockpit (chemin sensible → porte humaine à l'ouverture du chantier).
3. **Clics gardien d'hygiène tenant** (à exécuter, pas à outiller) — purger l'item CRM 4 + l'espace « 2026 - Arabelle Solutions - Épreuve T-0038 — cascade auto - 3 » (épreuve close) ; poser le `Title` sur l'item 5 (« Cockpit M365 ») ; supprimer la colonne `NomClient` orpheline. Rappel : la **suppression définitive de données est proscrite à l'agent** (runbook humain — doctrine §2 / `table-des-crans.yaml`).

## 14. Reste nommé — runbook de déploiement `.sppkg` au canon (exposé par l'épreuve du 1er août 2026)

**Runbook de déploiement `.sppkg` à consigner au canon** — **nommé ici, non ouvert**. La mise en production de l'artefact cockpit (paquet `.sppkg` à l'App Catalog SharePoint) est un **geste gardien répété** — encore joué à la main le 01/08/2026 pour l'image `1.5.2.0` (épreuve EBITDA honnête, `docs/epreuves/2026-08-01-ebitda-honnete-et-porte-t0043.md`) — mais **aucun runbook n'est consigné au canon** (contrairement aux runbooks M365 de §2). À écrire comme runbook humain (App Catalog, bump de version, contrôle post-déploiement), coordonnées tenant en variables d'environnement, jamais au canon. Aucun outil, aucun code : nommage seul.

## 15. Restes du contrôle mensuel de structure — nommés, non ouverts (exposés par l'épreuve du 1er août 2026)

Trois restes surfacés par la **clôture du volet 4a de `T-0032`** (journal `docs/epreuves/2026-08-01-t0032-couts-standards-controle-mensuel.md`). **Nommés ici, non encore ouverts** — aucun outil construit, aucun canon modifié, aucune écriture tenant :

1. **Orchestration du contrôle mensuel** — l'exécution du skill `controle-structure-mensuel` est **manuelle en v1**, pilotée en session. Restent à construire : le **rythme de déclenchement**, le **mail de synthèse** au gardien (avec hyperlien vers la ligne candidate en Zone-de-proposition) et le **rangement des pièces** contrôlées. C'est la condition de la **preuve de RÉCURRENCE** (contrôle d'août) qui maintient `T-0032` à `à_faire`.
2. **Convention de conversion de devise — la SOURCE du taux reste à arrêter au canon.** Le skill v1.1 exige déjà le **taux de référence BCE à la date de la pièce**, lu à une **source nommée** et tracé au rapport (devise, montant d'origine, taux, source, date du taux), et **interdit** tout taux inventé ou substitué. Ce qui manque est **quelle source fait foi** — constaté le 01/08 sur une pièce Anthropic de **15,03 USD**, laissée « à trancher » faute de taux lisible à la date (aucun taux inventé ; elle entrera par une correction gouvernée). À trancher, puis à graver au canon (`modele-donnees.md` §5.4).
3. **Écart de `CoutJour` du sous-traitant — arbitrage gardien** (à trancher, pas à outiller) : le référentiel `T_Ressources` porte **550 €/j** là où le sous-traitant **facture 500 €/j**. Laquelle des deux valeurs fait foi est une **décision**, pas un calcul ; la correction du référentiel est une **saisie source** (geste gardien, jamais l'agent). Écart **constaté et consigné** le 01/08, sans effet sur les mesures du jour. Hygiène connexe du même référentiel : la valeur de `Type` y est saisie **« Sous traitant »** là où le canon dit **`sous-traitant`** — à normaliser avant qu'un filtre strict ne la rencontre. **Tranché le 01/08/2026 au soir (S46)** : le référentiel **550 €/j fait foi** — la facturation à **500 €/j** du sous-traitant **n'entre pas dans le coût** ; **aucune correction du référentiel**. Hygiène connexe **corrigée par le gardien le même soir** (geste saisie source) : `Type` normalisé **`sous-traitant`**, `DateEntree` de Guillaume posée au **2026-09-01**.

## 16. Restes exposés par les épreuves T-0045 du 1er août 2026 — nommés, non ouverts

Trois restes surfacés par les **deux épreuves vertes d'accès et de lecture de la couche de saisie** (journal `docs/epreuves/2026-08-01-t0045-acces-et-lecture-saisie.md`). **Nommés ici, non encore ouverts** — aucun outil construit, aucun canon modifié, aucune écriture tenant :

1. **Trou de gouvernance de l'observabilité — `workbook_instancier_gabarit` absent de `CRAN_PAR_OUTIL`.** Le dictionnaire d'observabilité de `outils/mcp-graph/server.py` porte **18 des 19 outils** exposés ; le seul manquant est `workbook_instancier_gabarit`, dont chaque appel se journalise donc `"cran": "inconnu"` (`CRAN_PAR_OUTIL.get(outil, "inconnu")`) **depuis la 0.12.0** (commit `9b874dc`, 14/07/2026). Le cran **existe bien au canon** (`instancier_gabarit_pilotage`, `table-des-crans.yaml` v1.11, **auto**) : le trou n'est **pas** un cran manquant, c'est le **mapping serveur** qui ne le relie pas — un outil à effet de bord écrit depuis deux semaines des lignes de journal sans cran lisible. Reste à ajouter, avec une **garde générique** qui rende ce trou impossible à rouvrir (un test échouant si un outil exposé n'a pas d'entrée au dictionnaire, plutôt qu'un défaut silencieux `"inconnu"`) — c'est la classe de correctif, pas seulement le cas.
2. **Dette Workbook restante (image 0.23.0)** — **sessions persistantes** (`Workbook-Session-Id`, aujourd'hui jamais ouvertes : chaque appel paie une session implicite) et **`$batch`** (regroupement des appels Graph, recommandé par la documentation pour les écritures de lignes). Non bloquante : la chaîne est vivante sans elles. À instruire ensemble, à l'image suivante.
3. **Anomalie à instruire — divergence de relevé sur la même saisie** (nommée, **non résolue**) : le relevé du **14/07/2026** portait **juillet 23 j / août 7 j** là où la lecture positionnelle du **01/08/2026** rend **juillet 22 j / août 10 j** (`SAISIE_Prevu_2026`, mission 1, Σ mesurée le 01/08 = **148 j**). Deux hypothèses **non tranchées** : saisie humaine **révisée** entre les deux dates, ou relevé du 14/07 **imprécis** (il précédait la lecture par position). À instruire ; **jamais à trancher par recoupement** — la règle §5.6 interdit de forger ou déduire un mois. **Tranchée le 01/08/2026 au soir (S46)** : **saisie RÉVISÉE** — historique de versions SharePoint constaté (v2.0/v3.0 le 28/07, v4.0/v5.0 le 31/07, **éditeur unique = le gardien**) et confirmation du gardien : les saisies sont des **sources vivantes**, la **dernière version fait foi** (§5.6, **inchangée**), toute dérivation **recalcule depuis elle**. Tranchée **par l'auteur**, jamais par recoupement. Détail à `backlog/chantiers/T-0045.yaml`, note S46.

## 17. État des lieux d'audit S47 (02/08/2026) — finir la construction par l'USAGE

Consignation d'audit (nommage seul — aucun outil, aucune écriture tenant, aucun statut de chantier modifié) :

1. **Constat central.** Au HEAD `0ac6d3a5` (merge PR #295), les cinq chaînes métier sont construites et éprouvées sur le réel — CRM (T-0026/T-0035/T-0038), recrutement (T-0039), facturation (T-0030), chaîne économique saisie→dérivation→gabarit→cockpit (T-0031/T-0033/T-0045, rituel T-0046 institué et première dérivation verte), contrôle de structure (T-0032, volet 4a) — mais aucune n'est en RÉCURRENCE ni servie par un autre déclarant que le gardien en bootstrap. La fin de construction du SI est un problème d'USAGE, pas de briques.

2. **Ordre de bataille usage-first (S48+)** : (1) CRM en routine — hygiène du §13, cohérence mission 4 (point 3 ci-dessous), première revue de pipe réelle avec le skill `revue-de-pipe` (au canon, jamais exécuté) ; (2) clôture d'août (≈ 2 septembre) — déclaration d'un collaborateur SUR SA LIGNE, dérivation, contrôle mensuel : solde conjoint visé de `T-0032` et `T-0046`, avec la pièce Anthropic 15,03 USD et la SOURCE du taux BCE à graver (§5.4, reste §15.2) ; (3) chaîne d'ouverture de mission complète — `T-0042` puis `T-0040` ; (4) écran de déclaration des temps (évolution `tour-de-controle.md` §1/§4, écriture sous identité déléguée, jamais machine) puis orchestrations (rituel, contrôle mensuel, dérivation — chaque orchestration porte explicitement la porte du cran validé d'`allouer_num_facture`, skill consolidation-pilotage §7) ; (5) épreuve de sortie : une semaine où le SI est le point d'entrée unique.

3. **Deux restes S46 nommés, non ouverts** : (i) **échéancier de facturation de la mission 4 incomplet** — une seule ligne de 3 350 € HT pour 109 j prévus, d'où un EBITDA budget total écrasé ; compléter la saisie est un GESTE GARDIEN (saisie source, §5.6), pas un chantier ; (ii) **cohérence CRM ↔ chaîne économique** — la mission 4 vit économiquement (saisie, gabarit, cockpit) mais l'opportunité « Cockpit M365 » n'est jamais passée « Gagnée », aucun CodeMission n'est posé côté CRM et le cockpit affiche « Missions actives : 2 » ; gestes gardien guidés à l'ouverture du sujet CRM en routine.

4. **T-0041 caduc de facto.** L'octroi `Sites.Selected` `role=read` sur ManagementetGestion a été JOUÉ le 01/08/2026 (épreuve T-0045 1/2, `docs/epreuves/2026-08-01-t0045-acces-et-lecture-saisie.md`) ; il ne reste de la fiche que la consignation du runbook. Requalification à sa prochaine ouverture, sous porte humaine (`backlog/chantiers/` chemin sensible) — la fiche n'est pas touchée ici.

5. **Priorité non essentielle (arbitrage gardien du 02/08/2026)** : délégation ; optimisation technique — dont l'image 0.23.0 (sessions Workbook persistantes, `$batch`, entrée `workbook_instancier_gabarit` manquante à `CRAN_PAR_OUTIL` + test générique « tout outil exposé a une entrée », pourquoi périmé « par COPIE de la souche » dans `table-des-crans.yaml`) ; sauvegarde (`T-0029`) ; sécurité et hygiène de plateforme (`T-0025`, `T-0034`, `T-0036`, `T-0044`, break-glass, DPO §9) ; runbook `.sppkg` (§14) ; frais refacturés en saisie. Ne rien engager sans arbitrage explicite. Un manque exposé par un travail essentiel se NOMME au plan, il ne se construit pas.

6. **Étiquettes caduques constatées** (doctrine v1.11 — merge vaut promotion ; aucune PR de re-étiquetage, jamais) : `cadrage-mission` v1.4, `kick-off` v1.2, `newsletter-hebdo` v1.0, `onboarding` v1.0, `revue-de-pipe` v1.0 portent « candidat » en en-tête et se LISENT promus ; `T-0037` porte le statut historique « fait » (hors vocabulaire §4, non réécrit).

## 18. Restes et corrections exposés par la session du 5 août 2026 — nommés, non ouverts

Consignation de ce que l'usage du 05/08/2026 a **démenti** ou **découvert**. **Nommage seul** — aucun outil construit, aucun chantier ouvert, aucun statut modifié, aucune écriture tenant depuis cette section. Les §13 et §17 **ne sont pas réécrits** : ils sont corrigés **par renvoi depuis ici** (points 1 et 2).

1. **§17.3.ii est FAUX sur le réel, et l'était à sa rédaction.** Le constat « l'opportunité *Cockpit M365* n'est jamais passée Gagnée, aucun `CodeMission` n'est posé côté CRM » est **démenti** par le journal de versions de l'item 5 de la Liste « CRM » (`_api …/Versions`) : **Gagnée le 24/07/2026 à 10:05:40** (gardien), **`CodeMission` 4 alloué à 10:09:10** par `allouer_code_mission` (`T-0038`), **`Title` posé à 14:07:02**. Le CRM était **en règle depuis douze jours** quand l'audit du 02/08 l'a déclaré en défaut. §17.3.ii est donc corrigé ici, et non réécrit là-bas. **Leçon à inscrire : un constat d'audit vieillit plus vite qu'un contrat — mesurer avant de consigner.**

2. **§13.3 est INTÉGRALEMENT SOLDÉ, joué le 24/07/2026** (et non « à exécuter ») : item CRM 4 **en corbeille** (13:59:51 pour l'espace d'épreuve, 14:06:11 pour l'item), `Title` **`O-003`** posé sur l'item 5 à 14:07:02, colonne **`NomClient` absente** du CRM — elle vit sur la Liste « Missions », où elle est **légitime** (ce n'était donc pas une orpheline à supprimer). **Reste ouvert du §13 : le seul point 1** — promotion tracée Zone-de-proposition → CRM, **non outillée**. Le point 2 est traité au point 6 ci-dessous.

3. **La vraie cause de « Missions actives : 2 » — un trou de chaîne, ni CRM ni cockpit.** `outils/tour-de-controle-spfx/…/kpi-organisation.ts::compterMissionsActives` compte les lignes de la **Liste « Missions »** au statut « En cours ». Or cette liste **n'était alimentée par aucun geste outillé** : la mission 4 n'y avait **jamais eu de ligne**, alors qu'elle vivait au CRM *et* à l'économique. Le compteur disait vrai sur ce qu'il comptait. **Refermé au canon par la PR #302** (cascade d'ouverture de mission, `creer_ligne_mission`) et **rattrapé au tenant le 05/08** (ligne id 4, `Projet Cockpit M365`). **Leçon : lire le CODE du compteur avant d'accuser la donnée.**

4. **Défaut de conception DANS LA CASCADE QU'ON VIENT DE GRAVER — à trancher AVANT de coder `T-0040`.** `creer_ligne_mission` **dérive** `DateDebut` (1er du mois de la bascule) et `DateFin` (31/12 de l'année) **faute de les trouver au CRM** : le schéma de la Liste « CRM » **ne porte aucune date de réalisation**. L'heuristique ne tient que si **signature et démarrage tombent le même mois** — vrai des trois missions passées, **faux dès la première affaire réelle qui la traversera** : l'opportunité `MES` créée le 05/08 annonce un **démarrage au 01/09** pour une **signature attendue avant**. **Correctif d'architecte proposé** : une colonne **`DateDebutPrevue`** sur la Liste « CRM », **saisie humaine**, lue **telle quelle** par `creer_ligne_mission` au lieu d'être devinée. **Nommé ici** ; à porter à `modele-donnees.md` §2 bis et à la fiche `T-0040` **avant la première ligne de code**.

5. **`T-0051` porte un critère d'acceptation FAUX.** La fiche exige que « janvier à mars 2026 […] vides dans le classeur déposé […] s'affichent « · » ». Or la **mesure du 04/08 sous identité déléguée** dit **zéros budgétés RÉELS** (Graph renvoie `0`, pas une absence), et la convention « · » ne couvre que l'**ABSENT** (`modele-donnees.md` §5.7). Laissé en l'état, le chantier **livre un affichage faux**. **Correction = premier commit de `T-0051`** (la fiche n'est pas touchée ici).

6. **Défaut §13.2 — TROISIÈME occurrence, datée.** Le geste cockpit « nouvelle opportunité » **ne pose toujours pas** le `Title` `O-NNN` : item 6 (`MES`) créé le **05/08 à 21:41:20**, `Title` **vide sur ses trois versions** — après les items 4 et 5 du 24/07. Confirme que le correctif est bien le **premier commit de `T-0049`**, et non un chantier à part.

7. **Signal d'usage sur le geste de clôture d'opportunité** (matière, pas incident). Le 05/08 entre **21:42:07 et 21:42:40**, « Perdue » a été posé **sur la mauvaise ligne** puis corrigé (**33 s**), avant d'être posé sur la bonne à **21:42:42**. **État final correct, journal de versions intact.** La table du bandeau 2 rend un geste **irréversible-en-apparence** trop facile à jouer à côté : **matière pour la fenêtre Détails de `T-0049`**.

8. **`T-0039` normalisée** (partie A de la même PR que cette section) : dernière fiche dont `cran:` portait une **phrase**, portée à **`cran: valide`** par application de `tour-de-controle.md` §6 — **en vigueur à son exécution** du 26/07, donc pas une règle rétroactive. Le dépôt est **homogène** : **60 fiches sur 60** portent une valeur du vocabulaire contrôlé.

9. **Espace « 2026 - Arabelle Solutions - MES » — tranché : matière d'AVANT-VENTE, pas une mission** (arbitrage gardien du 05/08/2026). Une opportunité `MES` (**60 000 € HT**, étape **Qualification**, compte `CPT-001`) a été créée au CRM le 05/08 et porte désormais l'affaire. **Reste nommé, non joué** : l'espace vit dans `03 - Livrables de mission` alors qu'il **ne porte pas de mission** — il n'a d'ailleurs **ni `01 - Pilotage` ni `02 - Livrables`**. **Où domicilier la matière d'avant-vente ?** C'est un **concept manquant du modèle documentaire**, à trancher.

10. **Espace « 2026 - Arabelle Solutions - Siteflow » sans son 4e segment `- 1`** (convention `modele-donnees.md` §5.6). Renommage à **risque non nul** : **trois livrables réels** y sont référencés. **Nommé, non joué.**

11. **`impact.py` dégrade SILENCIEUSEMENT sans PyYAML — confirmé à l'usage le 05/08.** Sans dépendance, il rend un `VERDICT: pass` **d'allure normale calculé à vide** (`try/except ImportError: yaml = None`) ; **avec** venv jetable et `--changed`, il rend `RISQUE: large` **sur les mêmes fichiers**. Un faux vert de porte est plus dangereux qu'une porte absente. **Correctif candidat : échec bruyant** (refuser de rendre un verdict plutôt que d'en rendre un faux). **File non essentielle** (§17.5).

12. **Revue de pipe — INSTITUÉE HEBDOMADAIRE** depuis sa **première exécution réelle** du 05/08/2026 (score **69/100** ; pipe pondéré **recalculé à la main concordant** avec le cockpit). **Trois manques du skill `revue-de-pipe` v1.0 à graver en v1.1** : (i) **aucun barème pour la dimension « Fraîcheur »** — la note n'est pas reproductible ; barème posé en séance, à graver : **≤ 7 j = 100 · 8–14 j = 60 · 15–30 j = 30 · > 30 j = 0** ; (ii) **aucune dimension de CONCENTRATION CLIENT** alors que la colonne `Compte` la supporte **au schéma** — abandonnée à tort, et c'est **le risque dominant** : **100 % du pipe et 100 % du réalisé sur le seul compte `CPT-001`** ; (iii) **aucun seuil de matérialité** — sur **une seule opportunité active**, un score global ne veut rien dire et doit se refuser plutôt que s'afficher.

13. **Décisions de pipe du 05/08/2026 (gardien), consignées** : `O-001` « Remplacement SITEFLOW » → **Perdue** (échéance dépassée, affaire close) ; `O-003` « Cockpit M365 » → `Echeance` **24/07/2026**, **date mesurée de la bascule**, qui fait foi ; `O-004` « MES » → **créée**, **60 000 € HT**, étape **Qualification**, échéance de signature **01/09/2026**.
