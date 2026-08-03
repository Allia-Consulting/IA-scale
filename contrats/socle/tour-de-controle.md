# Tour de contrôle — point d'entrée unique du SI — Allia Consulting

> **Version** : 2.3 — *candidat*. **Statut** : contrat socle — fait foi.
> **Domicile** : `contrats/socle/tour-de-controle.md`. **Autorité de promotion** : gardien du temple.
> **Changelog** :
> v2.3 — candidat, 3 août 2026 (point d'étape de conception, arbitrages gardien du 03/08 au soir) : refonte du §3 par l'USAGE. (1) Bandeau titre : « X chose(s) appelle(nt) à ton action aujourd'hui » (bulle « X action(s) ») — une action = facture à éditer sous la responsabilité de l'utilisateur ou étape CRM à échéance ; déclencheur = échéance ATTEINTE OU DÉPASSÉE ; les décisions recrutement n'y comptent pas. (2) Staffing : bouton « Détails » → page dédiée en lecture (ressources + taux de staffing réel, même surface de calcul que les barres) ; code couleur Rouge/Orange/Vert par ressource = appréciation LIBRE du gardien, persistée en colonne CodeCouleur de Ressources-Profil (édition humaine guidée, extension bornée du périmètre « listes » du §1). (3) Pipe : « comptes actifs » en info-bulle ; « Détails » → fenêtre dédiée des opportunités ouvertes ; la table quitte la première page ; « nouvelle opportunité » y demeure et permet la CRÉATION d'un compte. (4) Recrutement : E1/E2/E3/Décisions sur une ligne ; NomCandidat affiché (jamais l'id C-NNNN) ; collecte IdentiteEntra + Disponibilite ; le code mission SORT du formulaire (l'affectation naît du dépôt du classeur de saisie — v2.2 déjà aligné) ; Acceptée/Refusée quittent la liste visible, « Détails » → toutes les candidatures. (5) Rentabilité : affichage borné à l'ANNÉE EN COURS + bouton « Année N+1 » ; colonne Budget lue dans budget-entreprise.xlsx (table T_Budget, ManagementetGestion, saisie gardien) ; Réalisé inchangé = projection des fiches missions consolidées (gabarits actifs + référentiel de coûts). (6) Factures à émettre : mois à venir seulement ; NOM de la mission affiché ; geste « Éditer » = ÉMETTRE, cascade déterministe (annonce + confirmation) : statut « émise » sous l'identité du cliqueur, allocation allouer_num_facture (cran validé — la confirmation du gardien au clic EST la porte), génération du Word au format Allia depuis le modèle promu (remplissage OOXML côté client, upload sous identité utilisateur), dépôt au dossier d'enregistrement des factures, LienFacture renseigné — ABROGATION CONSCIENTE ET BORNÉE du « aucune création de facture depuis le cockpit » (v2.1), pour la SEULE cascade d'émission ; tout le reste de l'économique demeure lecture seule, édité dans la saisie. (7) Le bandeau « indicateurs d'organisation » est SUPPRIMÉ (aucun usage). Chantiers d'exécution : T-0047 à T-0052. Domicile de l'écriture « émise » (saisie sous identité déléguée vs registre re-dérivé) : tranché à l'ouverture de T-0052.
> v2.2 — promu via boucle de promotion, 26 juillet 2026 (arbitrage gardien S43, épreuve T-0039 volet B) : la cascade « Acceptée » (§3 bandeau 3) n'écrit plus l'affectation initiale — écritures réduites à (1) Candidats.Etape et (2) fiche Ressources-Profil, plus un rappel d'affectation nommant le classeur de saisie. Alignement avec la doctrine v2.1 : l'économique s'édite dans la SAISIE, hors cockpit ; « agir » ne porte que sur les listes. Motif : classeur de saisie matriciel (§5.6), T_Affectations n'existe que dans les gabarits ; fail-closed du pré-vol vérifié le 24/07 (2 refus, zéro écriture).
> v2.1 — promu via boucle de promotion, 14 juillet 2026 (lecture du réel, session S34 ; aligné sur `modele-donnees.md` v1.18) : **rectification du modèle économique**. Il n'y a **pas de classeur consolidé** — le cockpit lit les **gabarits de pilotage actifs** (dérivés ERP par mission, régénérés par agent depuis la couche saisie) et le **référentiel de coûts** à audience restreinte, en direct. §4 refondu. Les bandeaux économiques (staffing, rentabilité, factures à émettre) passent en **lecture seule** : l'édition économique humaine (affectations, validation d'imputations, statut « émise ») se fait dans le **classeur de saisie** de la mission (`modele-donnees.md` §5.6), **hors cockpit**. Le régime « voir → creuser → agir » demeure, mais « agir » ne porte plus que sur les **listes** (CRM, recrutement) ; l'économique est en lecture. §1, §3 (bandeaux 1/4/5), §5 alignés.
> v2.0 — promu via boucle de promotion, 14 juillet 2026 : refonte par arbitrage gardien (conception fonctionnelle des 13–14 juillet, session S33). Le cockpit passe de « consommateur en lecture seule » à **point d'entrée unique du SI** : voir, creuser, agir — éditions humaines guidées et cascades déterministes confirmées. Nouvelle hiérarchie figée en six bandeaux (staffing, pipe commercial, recrutement, rentabilité, factures à émettre). Introduction du modèle économique distribué (fichiers de pilotage par mission consolidés par agent). Le principe v1.0 « jamais un double éditable » est abrogé pour les gestes humains ; il demeure pour les agents (Zone-de-proposition, crans). La maquette v1 reste historique et non normative.
> v1.0 — promu via boucle de promotion, 19 juin 2026 : création. Fige le parti-pris d'expérience utilisateur du cockpit (« Tour de contrôle »), l'orientation technique SPFx, et le régime « socle animé » (consommé par toute la firme, animé par un animateur désigné, promu par le gardien — sur le modèle du design system, doctrine §5). Répond au chantier nommé en doctrine §10 (« le cockpit du collaborateur reste à concevoir »). Chantier de construction : backlog/chantiers/T-0014.yaml. Maquette de référence : contrats/socle/maquettes/tour-de-controle-cockpit-v1.html (non normative).
> **Adossé à** : doctrine/doctrine.md (§3 rôles, §5 socle vs local, §6 crans), contrats/socle/organisation.md, contrats/socle/design-system.md, contrats/socle/modele-donnees.md, contrats/socle/table-des-crans.yaml.

## 0. Objet

La Tour de contrôle est **le point d'entrée unique des collaborateurs dans le SI** : listes,
classeurs de pilotage et documents s'atteignent depuis elle, jamais par navigation directe
dans les listes brutes. Elle est la page d'accueil du site AlliaConsuling.

## 1. Principe directeur

**L'utilisateur ne navigue pas dans des listes — il voit, il creuse, il agit depuis une
seule surface.**

- **Voir** : le cockpit lit les listes M365, les **gabarits de pilotage actifs** et le **référentiel de coûts** (pull) — il n'y a pas de classeur consolidé.
- **Creuser** : un compteur ouvre son détail dans le cockpit ; l'exploration ne déclenche
  jamais une écriture.
- **Agir** : deux régimes distincts, jamais confondus.
  1. **Édition humaine guidée (listes seulement)** : l'utilisateur écrit dans les **listes**
     sources (CRM — y compris la création d'un compte au fil du geste « nouvelle opportunité » —,
     recrutement, et la seule colonne `CodeCouleur` de Ressources-Profil) depuis le cockpit,
     sous sa propre identité Entra, avec ses droits et le journal de versions SharePoint. Le
     cockpit remplace la grille brute par un
     geste contraint ; il n'élève aucun droit. **L'économique (jours, imputations, échéancier)
     ne s'édite PAS dans le cockpit** : il vit dans le classeur de saisie (`modele-donnees.md`
     §5.6) ; les bandeaux économiques du cockpit sont en lecture seule. **Une seule exception,
     bornée** : la cascade d'émission de facture (§3, bandeau 5) — un geste humain confirmé qui
     écrit le statut « émise » sous l'identité du cliqueur et porte la porte du cran validé
     d'`allouer_num_facture`.
  2. **Cascade déterministe** : un geste humain peut déclencher une écriture multiple
     portée par du code promu (exemples figés en §3). Toute cascade **s'annonce avant
     d'exécuter** (liste exhaustive des écritures) et **n'exécute que sur confirmation
     explicite**.
- Le **génératif** (synthèses, briefs, brouillons) reste du ressort des agents et atterrit
  en Zone-de-proposition, sous les crans. Le cockpit peut le surfacer ; il ne s'y
  substitue pas.

## 2. Régime : un contrat SOCLE, mais ANIMÉ

Inchangé sur le fond (modèle du design system, doctrine §5) : consommé par toute la firme,
animé par un animateur désigné qui propose des candidats, promu par le gardien seul —
le rayon d'impact est la firme entière.

## 3. Parti-pris d'expérience (figé, v2)

- **Point d'entrée unique** : le cockpit est la page d'accueil du site ; la navigation
  latérale vers les listes brutes sort de l'usage courant (les listes restent accessibles
  aux gestes d'administration). Les documents s'atteignent en contexte de ligne
  (opportunité → sa proposition ; candidat → son CV et ses synthèses ; facture → son PDF
  dans le dépôt Teams).
- **Modèle voir → creuser → agir**, avec la séparation stricte du §1.
- **Bandeau titre** : « X chose(s) appelle(nt) à ton action aujourd'hui », bulle « X action(s) ».
  Une **action** est exactement : une facture à éditer sous la responsabilité de l'utilisateur, ou
  une étape CRM à faire avancer à échéance. Déclencheur : **échéance atteinte ou dépassée**
  (facture du mois dès l'entrée dans le mois ; opportunité dès `Echeance` ≤ aujourd'hui ;
  responsabilité portée par `CRM.Responsable`, factures via la couture `CodeMission`). Les
  décisions recrutement n'y comptent pas (elles vivent au bandeau 3).
- **Hiérarchie des bandeaux (ordre figé, priorité décroissante)** :
  1. **Staffing** — % de staffing mensuel des salariés (hors sous-traitance), douze mois,
     sélecteur d'année, pourcentage lisible dans la barre, effectif actif au sommet de chaque
     barre, distinction réalisé / prévisionnel. **Lecture seule** sur l'économique. Bouton
     **« Détails »** (haut droite) → page dédiée en **lecture** : chaque ressource et son taux de
     staffing réel (même surface de calcul que les barres). À côté de chaque nom, un menu
     déroulant **Rouge / Orange / Vert** : appréciation **libre du gardien** (aucune règle de
     calcul), persistée dans la colonne `CodeCouleur` de Ressources-Profil, écrite sous l'identité
     de l'utilisateur (§1).
  2. **Pipe commercial** — compteurs : propositions en cours, montant proposé, **pipe pondéré**
     (pondérations figées : Proposition 60 %, Qualification 15 %) ; « comptes actifs » en
     **info-bulle** du bandeau. La table des opportunités ne vit plus sur la première page :
     bouton **« Détails »** → fenêtre dédiée des opportunités ouvertes (Qualification +
     Proposition), éditable (étape, montant). Gestes depuis la première page : **nouvelle
     opportunité** (le sélecteur de compte permet de **créer un compte** — statut initial
     Prospect, à confirmer au premier usage réel) ; passage en Gagnée → cascade proposant la
     création de la mission et de son espace.
  3. **Recrutement** — compteurs E1, E2, E3 et Décisions (candidats en étape Proposition) **sur
     une seule ligne**. La liste visible affiche **NomCandidat** (l'id `C-NNNN` reste la clé
     interne, jamais montrée) et exclut les étapes **Acceptée / Refusée** ; bouton **« Détails »**
     → page de **toutes** les candidatures. Gestes : ajouter un candidat (créé en E1 ; le
     formulaire collecte `IdentiteEntra` et `Disponibilite`, **jamais de code mission** — on
     recrute sans mission, l'affectation naît du dépôt du classeur de saisie dans l'espace de la
     mission) ; changement d'étape en ligne ; passage en Acceptée → cascade « fiche
     Ressources-Profil + rappel d'affectation » (v2.2), sur confirmation.
  4. **Rentabilité et résultats** — tableau **de l'année en cours** : douze mois × (Budget |
     Réalisé) + colonne Total ; lignes CA total et EBITDA ; bouton **« Année N+1 »** (haut
     droite) basculant sur le budget de l'année à venir. **Budget** : lu dans
     `budget-entreprise.xlsx` (table `T_Budget`, ManagementetGestion, saisie gardien — jamais
     écrite par la machine), filtré sur l'année affichée. **Réalisé** : projection des fiches
     missions consolidées — gabarits actifs + référentiel de coûts, lus à la volée (§4).
     L'absence de donnée s'affiche « · », jamais zéro inventé.
  5. **Factures à émettre** — échéanciers des **gabarits actifs** filtrés au statut « à émettre »
     et au **mois à venir** ; chaque ligne porte le **nom de la mission** (couture `CodeMission` →
     opportunité), jamais un code nu, et pointe vers le PDF dans le dépôt Teams. Geste
     **« Éditer » = ÉMETTRE** : cascade déterministe (annonce préalable de la liste exhaustive des
     écritures + confirmation explicite) — (1) statut « émise » (+ `EtiquetteLocale`) écrit sous
     l'**identité du cliqueur**, jamais machine ; (2) `allouer_num_facture` (cran **validé** — la
     confirmation du gardien au clic EST la porte) ; (3) génération du document Word au format
     factures Allia depuis le **modèle promu** (remplissage OOXML côté client, upload sous
     identité utilisateur), numéro `F-AAAA-NNNN` posé, déposé au dossier d'enregistrement des
     factures ; (4) `LienFacture` renseigné au registre. Chronologie légale sans trou inchangée ;
     STOP au premier incident. C'est la **seule** création de document de facture depuis le
     cockpit ; le reste de l'économique demeure en lecture (§1).
- **Règle « liste visible ↔ page détails »** : la première page ne montre que l'actionnable ;
  chaque bandeau qui masque (opportunités, candidatures, ressources) offre un « Détails » qui
  montre TOUT, en lecture ou en geste contraint — jamais une grille brute.
- **Honnêteté des données** : jamais de chiffre inventé ; le cockpit affiche la
  fraîcheur de sa dernière lecture des gabarits et signale tout gabarit en anomalie
  (« lu le J à H — 1 gabarit en anomalie : M-XXX »).
- **Sobriété** : style sobre du design system, pas d'ornement d'état.

## 4. Modèle économique distribué

- **Trois couches** (`modele-donnees.md` §5) : une **saisie** humaine par mission (source),
  un **gabarit ERP par mission** `gabarit-<CodeMission>.xlsx` (dérivé, régénéré par agent
  depuis la saisie ; tables nommées T_Affectations, T_Imputations, T_Echeancier), et un
  **référentiel de coûts** à audience restreinte. **Il n'y a pas de classeur consolidé.**
- **Les coûts ne descendent jamais dans les fichiers mission.** T_Ressources (coûts
  jour) et T_Structure (coûts de fonctionnement) vivent uniquement dans le **référentiel
  de coûts, à audience restreinte**.
- **Les gabarits sont des dérivés régénérables, produits par agent** depuis la couche
  saisie (boucle lun-ven 5h/13h, `modele-donnees.md` §5.6). Une saisie ou un gabarit au
  schéma cassé est **signalé, jamais silencieusement ignoré**.
- **Le cockpit lit les gabarits actifs et le référentiel de coûts en direct** — il n'y a
  pas de consolidé, et le cockpit ne réécrit pas les gabarits (dérivés agent).
- **Une seule vérité par champ** : Ressources-Profil porte identité, grade,
  disponibilité ; le référentiel de coûts porte coûts et dates contractuelles. Aucun champ
  ne vit à deux endroits.
- **L'édition économique humaine se fait dans la saisie, hors cockpit.** La saisie et la
  validation mensuelle des imputations sont des gestes du responsable de mission **dans le
  classeur de saisie** (`modele-donnees.md` §5.6), sous son identité ; le cockpit est en
  lecture seule sur l'économique. Le mail de rappel de fin de mois est une capacité d'agent
  à venir, contractualisée séparément (cran défini à ce moment-là).
- Le schéma détaillé du gabarit et les conventions de dépôt relèvent de
  `contrats/socle/modele-donnees.md` (PR distincte).

## 5. Orientation technique : SPFx

- **Modèle retenu inchangé** : web part SharePoint Framework (React/Fluent UI) hébergée
  sur la page d'accueil du site AlliaConsuling — SSO automatique, lecture native des
  listes, pas de coût d'exploitation supplémentaire.
- **Écritures** : la web part écrit dans les **listes** (CRM, Comptes, recrutement,
  Ressources-Profil `CodeCouleur`) sous l'identité de l'utilisateur connecté
  (REST SharePoint / Graph délégué). Le cockpit **n'écrit pas
  l'économique** (jours, imputations, statut d'échéancier) : cette édition a lieu dans le
  classeur de saisie de la mission (`modele-donnees.md` §5.6), hors cockpit. Aucune
  élévation de droits, aucun compte de service. Exception bornée du §1 : la cascade
  d'émission (§3, bandeau 5) — écritures sous identité du cliqueur + porte du cran validé
  d'`allouer_num_facture` ; la génération du Word se fait côté client (OOXML) et s'upload sous
  identité utilisateur, jamais par compte de service.
- **Conséquences assumées inchangées** : chaîne de build dédiée (Node, TypeScript,
  toolchain SPFx) ; déploiement du `.sppkg` via l'App Catalog du tenant = geste de
  configuration tenant, **runbook humain** (gardien), jamais un agent. Le code de la web
  part est agent-éditable (cran auto en branche).
- **Frontière** : ce contrat porte la POLITIQUE d'expérience. La construction effective
  (code, build, déploiement) est le chantier T-0014 et ses suites.

## 6. Crans

- **Éditer le code de la web part en branche** : cran **auto** (réversible, interne).
- **Promouvoir une évolution du cockpit** : cran **validé**, porte du gardien — rayon
  d'impact firme entière (doctrine §6).
- **Déployer le `.sppkg`** : **runbook humain** (table-des-crans.yaml).
- **Éditions humaines directes depuis le cockpit** : gestes de l'utilisateur sous ses
  propres droits — hors du régime des crans, qui gouverne les agents. Le cockpit
  n'élève ni n'abaisse aucun droit.
- **Cascades déterministes** : code promu, annonce préalable et confirmation explicite
  obligatoires (§1). Une cascade qui écrirait sans confirmation est un défaut.
- **Actions d'agent déclenchées depuis le cockpit** : portent le cran de l'action
  sous-jacente (un dérivé écrit en Zone-de-proposition reste auto ; un envoi externe
  reste validé).

## 7. Ce que ce contrat ne fait pas

- Il ne décrit pas l'implémentation (composants, schéma technique) — c'est T-0014 et
  ses suites.
- Il ne définit pas le schéma détaillé du gabarit de pilotage ni ses conventions de
  dépôt — c'est `modele-donnees.md` (PR distincte).
- Il ne contractualise pas l'envoi de mail par agent (rappel mensuel) — chantier dédié.
- Il ne nomme pas d'animateur : la délégation du périmètre est un acte distinct,
  inscrit dans organisation.md quand elle sera réelle.

## 8. Évolution

Contrat socle promu — il fait foi (doctrine §7). Toute évolution du parti-pris ou de
l'orientation passe par la boucle de promotion.
