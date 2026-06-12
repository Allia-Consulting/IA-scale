# Anonymisation — Allia Consulting

> **Version** : 1.4 — *promu*. **Statut** : contrat socle — fait foi.
> **Domicile** : `contrats/socle/anonymisation.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§6 et §9).
> **Changelog** : v1.4 — **RÉVISION du déclencheur** (décision du gardien, 12 juin 2026) : la porte se déclenche à la **COMMUNICATION GRAND PUBLIC**, non plus à toute sortie vers un client — la **relation firme-client est considérée comme la firme** ; un client n'est **jamais anonymisé pour lui-même**. **AJOUT d'un second déclencheur** : la **matière issue d'un client tiers** est anonymisée **avant insertion** dans un livrable client (exigence NDA). Critère décisif : « la matière **part-elle vers le grand public**, ou **contient-elle la matière d'un client tiers à destination d'un autre client** ? ». v1.3 — **CORRECTION du déclencheur** (§1, §5, §6, §7), 7 juin 2026 : l'anonymisation se déclenche à la **sortie externe de la firme** (publication externe, livrable rendu hors firme), et **non** sur la réutilisation inter-client **interne** — qui reste **nominative** (avantage qui compose, doctrine §9). Critère décisif : « la matière quitte-t-elle la firme ? ». (L'inter-client interne n'était pas censé déclencher l'anonymisation.) v1.2 — promu via boucle de promotion (contenu inchangé). v1.1 — déclencheur décidé par le gardien ; critère antérieur (corrigé en v1.3) = « changement de destinataire ».
> ⚠️ **Exigence de conformité (RGPD, AI Act, NDA).** Ce document est un candidat *exécutable* ; ses paramètres juridiques doivent être validés par le gardien, idéalement avec un conseil. Je ne suis pas juriste.

## 0. Objet

Rendre l'anonymisation **exécutable**, pas une intention : dire **quand** elle se déclenche, sur **quels champs**, à **quel seuil**, et **comment**. C'est la porte automatique du cran « anonymisation » (doctrine §6).

## 1. Déclencheur — quand

Déclenche l'anonymisation, sans humain :

- toute **communication grand public** : site internet, publication, communication institutionnelle — tout canal **non adressé à un client identifié dans une relation contractuelle** ;
- l'**insertion de matière issue d'un client tiers** dans un livrable destiné à un client : la matière du client tiers est anonymisée **AVANT insertion** (exigence NDA/RGPD — le NDA du client Y ne s'étend pas au client X).

**Ne déclenche pas** :

- le **livrable rendu au client pour ses propres données** : la **relation firme-client est considérée comme la firme** — un livrable destiné au client X n'est **jamais anonymisé pour les données de X lui-même** ;
- la **réutilisation inter-client interne** : une matière qui circule entre missions ou entre clients, *à l'intérieur de la firme*, reste **nominative**. C'est l'avantage qui compose — l'apprentissage inter-missions (doctrine §9). *(Inchangé.)*

**Critère décisif** : « la matière **part-elle vers le grand public**, ou **contient-elle la matière d'un client tiers à destination d'un autre client** ? »

**Exemple validé.** Un agent capitalise une mission et génère un insight destiné au **site** (communication grand public) → l'anonymisation est **appliquée**, et un message part au **responsable communication**, qui valide la publication (validation **métier**, hors GitHub). En revanche, la même matière réutilisée d'une mission à l'autre **à l'intérieur de la firme** reste **nominative** : aucune anonymisation.

**Exemple (matière d'un client tiers).** Un **benchmark issu de la mission du client Y** est inséré dans un **livrable destiné au client X** → la **matière Y est anonymisée** avant insertion ; les **données de X restent nominatives**.

## 2. Champs à traiter — quoi

**Identifiants directs (retirés ou remplacés systématiquement)** : nom du client et entités liées ; noms de personnes ; emails, téléphones ; adresses ; logos et identité visuelle ; codes de projet ou de contrat ; identifiants de systèmes internes, URLs, tenants ; signatures et mentions NDA.

**Quasi-identifiants (généralisés)** : secteur précis → secteur large ; montants exacts → ordres de grandeur ou fourchettes ; effectifs exacts → tranches ; dates précises → période ; et toute **combinaison** qui pointerait vers un acteur unique.

## 3. Seuil — jusqu'où

Règle d'or : **aucune combinaison des attributs conservés ne doit permettre de ré-identifier** le client, une personne ou l'affaire (principe de type *k-anonymat* : jamais de singularité). On retire tous les identifiants directs et on généralise les quasi-identifiants jusqu'à ce qu'il reste **un ensemble plausible d'acteurs, jamais un seul**. On vise une **anonymisation** (irréversible), pas une simple pseudonymisation — qui, elle, reste une donnée personnelle au sens du RGPD.

## 4. Comment — la transformation

Retrait, remplacement par des marqueurs neutres (« Client A », « secteur industriel »), ou généralisation. Si une table de correspondance (réel → anonyme) existe, elle reste dans la **zone de proposition**, jamais dans l'artefact promu. La transformation est **tracée** : qui, quand, quoi.

## 5. Conformité

- **RGPD** : une donnée vraiment anonyme sort du champ ; une donnée seulement pseudonymisée y reste — d'où l'exigence d'irréversibilité pour toute matière **communiquée au grand public** ou **issue d'un client tiers insérée dans un livrable client**.
- **AI Act** : matière de contexte ou d'apprentissage conforme.
- **NDA** : respecter les clauses propres à chaque mission. **Le NDA du client Y ne s'étend pas au client X** : toute matière issue d'un client tiers est anonymisée **avant insertion** dans un livrable destiné à un autre client (§1).
- En cas de doute : **ne pas promouvoir.**

## 6. Articulation avec les crans

Porte **automatique** (déclenchée par règle), orthogonale aux crans. Elle est un **préalable**, pas un substitut : la **communication grand public** passe quand même par la **porte humaine du cran *validé*** — tenue par un **grade habilité** (`organisation.md` §4 bis). Pour un **livrable client**, la porte du cran *validé* ne concerne que l'**envoi par un agent** (tenant de porte : grade habilité) ; l'envoi par un **humain collaborateur est libre** — les crans gouvernent les agents, pas les humains (doctrine §6).

## 7. Décisions du gardien

- **Déclencheur : RÉVISÉ (v1.4, décision du gardien, 12 juin 2026).** La porte se déclenche à la **communication grand public** (site internet, publication, communication institutionnelle — tout canal non adressé à un client identifié dans une relation contractuelle), non plus à toute sortie vers un client : la **relation firme-client est considérée comme la firme** — un client n'est **jamais anonymisé pour lui-même**. **Second déclencheur ajouté** : la **matière issue d'un client tiers** est anonymisée **avant insertion** dans un livrable client (exigence NDA). Critère décisif arrêté en §1.
- **Déclencheur : décidé et corrigé (v1.3).** Le déclenchement est la **sortie externe de la firme** (publication externe, livrable hors firme) ; la réutilisation inter-client **interne** ne déclenche pas et reste nominative. Critère décisif arrêté en §1 : « la matière quitte-t-elle la firme vers l'extérieur ? ». *(Corrige le critère antérieur « changement de destinataire » de la v1.1.)*

Restent à confirmer :

1. La liste exacte des champs (à compléter selon vos missions types).
2. Le paramètre de seuil (niveau de généralisation acceptable).
3. La validation juridique (RGPD / AI Act / NDA), idéalement avec un conseil.
