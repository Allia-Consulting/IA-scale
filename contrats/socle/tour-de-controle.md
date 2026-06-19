# Tour de contrôle — cockpit utilisateur du SI — Allia Consulting

> **Version** : 1.0 — *promu*. **Statut** : contrat socle — fait foi.
> **Domicile** : `contrats/socle/tour-de-controle.md`. **Autorité de promotion** : gardien du temple.
> **Changelog** : v1.0 — promu via boucle de promotion, 19 juin 2026 : création. Fige le parti-pris d'expérience utilisateur du cockpit (« Tour de contrôle »), l'orientation technique SPFx, et le régime « socle animé » (consommé par toute la firme, animé par un animateur désigné, promu par le gardien — sur le modèle du design system, doctrine §5). Répond au chantier nommé en doctrine §10 (« le cockpit du collaborateur reste à concevoir »). Chantier de construction : backlog/chantiers/T-0014.yaml. Maquette de référence : contrats/socle/maquettes/tour-de-controle-cockpit-v1.html (non normative).
> **Adossé à** : doctrine/doctrine.md (§3 rôles, §5 socle vs local, §6 crans, §10 cockpit utilisateur), contrats/socle/organisation.md (§2 carte des périmètres — capacité « adoption multi-utilisateurs / RBAC » ; §5 droits réconciliés), contrats/socle/design-system.md (voix visuelle), contrats/socle/modele-donnees.md (listes consommées), contrats/socle/table-des-crans.yaml (crans des actions déclenchées).

## 0. Objet

Définir **l'expérience de l'utilisateur quotidien** face au SI : un cockpit — la « Tour de contrôle » — qui répond à « qu'est-ce qui me concerne, et que puis-je déclencher ? ». Ce contrat fige le **parti-pris UX** et l'**orientation technique** ; il ne décrit pas l'implémentation détaillée (→ chantier T-0014). Il répond au chantier que la doctrine §10 nomme explicitement comme « le vrai test de l'adoption ».

## 1. Principe directeur

**L'utilisateur ne navigue pas dans des listes — il voit ce qui le concerne, et déclenche ; le système réalise sous son contrôle.** Le cockpit est un **consommateur** des listes M365 (pull) — jamais un double éditable. Il montre l'état (lecture des listes) et porte des actions déléguées à l'agent (qui écrit en Zone-de-proposition, sous les crans).

## 2. Régime : un contrat SOCLE, mais ANIMÉ

La Tour de contrôle suit le modèle du **design system** (doctrine §5) :

- **Consommée par toute la firme** : tous les collaborateurs voient et utilisent le cockpit au quotidien (rôle utilisateur, doctrine §3).
- **Animée par un animateur désigné** : une seule personne fait vivre le cockpit — invente, ajoute, retire des cartes et des boutons pour l'ensemble des collaborateurs. Elle **propose** des candidats (procédure de contrat socle), exactement comme la communication anime le design system sans le promouvoir.
- **Promue par le gardien** : parce que le rayon d'impact est la firme entière, tout changement passe par le cran **validé** (doctrine §6). L'animateur ne met jamais en service ses propres changements de cockpit.

> C'est le **premier cas formalisé de « socle animé »** chez Allia : un contrat socle dont l'animation est déléguée à un animateur désigné, la promotion restant au gardien. Le périmètre est rattaché à la capacité « adoption multi-utilisateurs (RBAC) » de la carte (organisation.md §2).

## 3. Parti-pris d'expérience (figé)

- **Deux faces complémentaires** : une face « cockpit » (voir / s'orienter — qu'est-ce qui me concerne aujourd'hui ?) et une face « action » (déclencher — l'agent exécute). Le cockpit corrige le défaut « page blanche » d'une interface conversationnelle pure : il oriente l'utilisateur avant qu'il ne demande.
- **Modèle d'interaction : voir → creuser → agir.** Un compteur ouvre le détail (liste filtrée) DANS le cockpit ; l'action vers l'agent est un geste SÉPARÉ et délibéré — jamais déclenché par mégarde en explorant.
- **Premier rôle servi : le manager-gestionnaire** (pilotage). Validé en premier parce que c'est le rôle « voir pour décider » le plus exigeant. Les autres rôles (consultant, animateur) suivront.
- **Hiérarchie des zones du cockpit manager (ordre figé, priorité décroissante)** : 1. pipe commercial — 2. recrutement — 3. rentabilité & résultats — 4. activité des équipes. Chaque zone montre l'état ET porte une action déléguée à l'agent.
- **Honnêteté des données** : le cockpit n'affiche jamais de chiffre inventé. Une zone sans donnée réelle l'indique explicitement, plutôt que de simuler.

## 4. Orientation technique : SPFx

- **Modèle retenu : SharePoint Framework (SPFx)** — web part React/Fluent UI hébergée dans SharePoint, sur une page d'accueil du site AlliaConsuling. C'est le modèle recommandé par Microsoft pour une UI sur substrat M365 ; SSO automatique, hébergement dans SharePoint sans coût d'exploitation supplémentaire, lecture native des listes.
- **Conséquences assumées** : une chaîne de build dédiée (Node, TypeScript, toolchain SPFx) et un déploiement via l'App Catalog du tenant — geste de configuration tenant, donc **runbook humain** (gardien), jamais un agent. Le code de la web part est agent-éditable (cran auto en branche) ; le déploiement du `.sppkg` ne l'est pas.
- **Frontière** : ce contrat porte la POLITIQUE d'expérience. La construction effective (code, build, déploiement) est le chantier T-0014.

## 5. Crans

- **Éditer le code de la web part en branche** : cran **auto** (réversible, interne — éditer un fichier).
- **Promouvoir une évolution du cockpit** (nouvelle carte, bouton, zone) : cran **validé**, porte du gardien — rayon d'impact firme entière (doctrine §6).
- **Déployer le `.sppkg` dans l'App Catalog** : **runbook humain** (configuration tenant, proscrite à l'agent — table-des-crans.yaml).
- **Actions déclenchées par l'utilisateur depuis le cockpit** : portent le cran de l'action sous-jacente (un dérivé écrit en Zone-de-proposition reste auto ; un envoi externe reste validé). Le cockpit n'élève ni n'abaisse les crans.

## 6. Ce que ce contrat ne fait pas

- Il ne décrit pas l'implémentation (composants, schéma de données du cockpit) — c'est T-0014.
- Il ne nomme pas d'animateur : la délégation du périmètre est un acte distinct, inscrit dans organisation.md quand elle sera réelle (aucun nom futur inventé).
- Il ne se substitue pas aux listes : il les consomme.

## 7. Évolution

Contrat socle promu — il fait foi (doctrine §7). Toute évolution du parti-pris ou de l'orientation passe par la boucle de promotion. La doctrine §10 (« cockpit utilisateur à concevoir ») reste à actualiser par un candidat ultérieur dédié, pour refléter que ce chantier est désormais ouvert (hors périmètre de cette PR — la doctrine est socle et se modifie séparément).
