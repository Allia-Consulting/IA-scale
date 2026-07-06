# Plan de construction du SI augmenté — Allia

> Statut : promu — contrat socle · fait foi.
> Changelog : v0.6 → **candidat**, 6 juillet 2026 (toilettage canon d'hygiène) : §4 — convention de vocabulaire clarifiée : `promu` réservé à la boucle de promotion des **contrats** ; cycle de vie d'un **chantier** = `à_faire → en_cours → soldé` (l'étape « mergé, pas encore éprouvé » se lit dans `execution:`, non dans un statut `promu`). Fiches historiques Phase 0/1 non réécrites. Aucune autre section modifiée. v0.5 → promu, 5 juillet 2026 : §9 T-4.1 — incise nommant la brique CRM (Cœur de métier / Développement commercial : entités Compte / Opportunité, pipeline commercial Liste « CRM » et lien opportunité → mission, chantier T-0026), symétrique de l'incise recrutement v0.3. Aucune autre section modifiée. v0.4 → promu, 5 juillet 2026 (toilettage d'entrée en Phase 2) : §12 — hypothèse 1 révisée (Phase 2 engagée sans ingénieur dédié, leviers de saturation nommés) ; hypothèse 6 close (réalisée — matière portée par doctrine §10 bis et organisation.md §3/§4.1). Aucune autre section modifiée. v0.3 → promu, 16 juin 2026 : §9 T-4.1 — incise nommant la capacité Talent & RH / Recrutement comme cible de phase 4 (outil vue candidat T-0013, exécutant le cadre RGPD recrutement promu). Mention légère, aucun autre changement de fond. v0.2 → promu : passage par la boucle de promotion (session fondation 7 juin 2026). *(v0.2 : alignement sur la feuille de route et les grades de la présentation « Talents & recrutement ».)*
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
- **État réel (vérifié 28 juin 2026, ruleset `main-protection` id 17366850, enforcement actif)** : PR obligatoire, suppression et force-push bloqués. Le **statut CI agent-gardien est CONSULTATIF en v0** (aucune règle `required_status_checks` dans le ruleset), par décision du gardien — à rendre requis quand l'agent-gardien mûrit (Phase 2).

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
- **Critère de sortie** : une PR à faible risque et conforme passe sans toi ; toute régression d'un skill est bloquée par la CI.

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
