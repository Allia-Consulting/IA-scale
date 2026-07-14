# Tour de contrôle — point d'entrée unique du SI — Allia Consulting

> **Version** : 2.0 — *promu*. **Statut** : contrat socle — fait foi.
> **Domicile** : `contrats/socle/tour-de-controle.md`. **Autorité de promotion** : gardien du temple.
> **Changelog** :
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

- **Voir** : le cockpit lit les listes M365 et le classeur consolidé de pilotage (pull).
- **Creuser** : un compteur ouvre son détail dans le cockpit ; l'exploration ne déclenche
  jamais une écriture.
- **Agir** : deux régimes distincts, jamais confondus.
  1. **Édition humaine guidée** : l'utilisateur écrit dans les listes sources depuis le
     cockpit, sous sa propre identité Entra, avec ses droits et le journal de versions
     SharePoint. Le cockpit remplace la grille brute par un geste contraint ; il n'élève
     aucun droit.
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
- **Hiérarchie des bandeaux (ordre figé, priorité décroissante)** :
  1. **Staffing** — % de staffing mensuel des salariés (hors sous-traitance), douze mois,
     sélecteur d'année, pourcentage lisible dans la barre, effectif actif au sommet de
     chaque barre, distinction réalisé / prévisionnel. Geste : gérer les affectations.
  2. **Pipe commercial** — comptes actifs (Comptes, Statut = Client) ; propositions en
     cours (CRM, Étape = Proposition) ; montant proposé (somme des montants en étape
     Proposition) ; **pipe pondéré** (pondérations figées : Proposition 60 %,
     Qualification 15 %). Table des opportunités éditable (étape, montant). Gestes :
     nouvelle opportunité ; passage en Gagnée → cascade proposant la création de la
     mission et de son espace.
  3. **Recrutement** — compteurs E1, E2, E3 (Candidats.Etape) ; décisions en cours
     (candidats en étape Proposition). Gestes : ajouter un candidat (créé en E1) ;
     changement d'étape en ligne ; passage en Acceptée → cascade « fiche
     Ressources-Profil + affectation initiale », sur confirmation.
  4. **Rentabilité et résultats** — tableau douze mois × (Budget | Réalisé) + colonne
     Total ; lignes CA total et EBITDA ; source exclusive : classeur consolidé (§4).
     L'absence de donnée s'affiche « · », jamais zéro inventé.
  5. **Factures à émettre** — échéancier consolidé filtré au statut « à émettre » ;
     chaque ligne pointe vers le PDF de la facture dans le dépôt Teams. Geste unique :
     « Émise » (écrit le statut dans l'échéancier, la ligne sort de la vue). Aucune
     création de facture depuis le cockpit : les factures naissent de l'échéancier.
- **Honnêteté des données** : jamais de chiffre inventé ; le cockpit affiche la
  fraîcheur de la consolidation et signale tout fichier mission en anomalie
  (« consolidé le J à H — 1 fichier en anomalie : M-XXX »).
- **Sobriété** : style sobre du design system, pas d'ornement d'état.

## 4. Modèle économique distribué

- **Un gabarit promu** `gabarit-pilotage-mission.xlsx` (tables nommées : T_Affectations,
  T_Imputations, T_Echeancier) est instancié pour chaque mission dans l'espace de la
  mission, sous la responsabilité du responsable de mission.
- **Les coûts ne descendent jamais dans les fichiers mission.** T_Ressources (coûts
  jour) et T_Structure (coûts de fonctionnement) vivent uniquement dans le **classeur
  consolidé central, à audience restreinte**.
- **La consolidation est un dérivé régénérable, produit par agent** : énumération des
  missions actives, lecture des tables nommées de chaque fichier, reconstruction du
  consolidé. Un fichier au schéma cassé est **signalé, jamais silencieusement ignoré**.
- **Le cockpit ne lit que le consolidé** — jamais les fichiers mission en direct.
- **Une seule vérité par champ** : Ressources-Profil porte identité, grade,
  disponibilité ; le consolidé porte coûts et dates contractuelles. Aucun champ ne vit
  à deux endroits.
- La validation mensuelle des imputations est un geste du responsable de mission **dans
  le cockpit** ; le mail de rappel de fin de mois est une capacité d'agent à venir,
  contractualisée séparément (cran défini à ce moment-là).
- Le schéma détaillé du gabarit et les conventions de dépôt relèvent de
  `contrats/socle/modele-donnees.md` (PR distincte).

## 5. Orientation technique : SPFx

- **Modèle retenu inchangé** : web part SharePoint Framework (React/Fluent UI) hébergée
  sur la page d'accueil du site AlliaConsuling — SSO automatique, lecture native des
  listes, pas de coût d'exploitation supplémentaire.
- **Écritures** : la web part écrit dans les listes sous l'identité de l'utilisateur
  connecté (REST SharePoint / Graph délégué) ; le statut d'échéancier s'écrit dans le
  classeur consolidé via l'API Graph Excel (tables nommées). Aucune élévation de droits,
  aucun compte de service.
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
