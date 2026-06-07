# Anonymisation — Allia Consulting

> **Version** : 1.3 — *promu*. **Statut** : contrat socle — fait foi.
> **Domicile** : `contrats/socle/anonymisation.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§6 et §9).
> **Changelog** : v1.3 — **CORRECTION du déclencheur** (§1, §5, §6, §7), 7 juin 2026 : l'anonymisation se déclenche à la **sortie externe de la firme** (publication externe, livrable rendu hors firme), et **non** sur la réutilisation inter-client **interne** — qui reste **nominative** (avantage qui compose, doctrine §9). Critère décisif : « la matière quitte-t-elle la firme ? ». (L'inter-client interne n'était pas censé déclencher l'anonymisation.) v1.2 — promu via boucle de promotion (contenu inchangé). v1.1 — déclencheur décidé par le gardien ; critère antérieur (corrigé en v1.3) = « changement de destinataire ».
> ⚠️ **Exigence de conformité (RGPD, AI Act, NDA).** Ce document est un candidat *exécutable* ; ses paramètres juridiques doivent être validés par le gardien, idéalement avec un conseil. Je ne suis pas juriste.

## 0. Objet

Rendre l'anonymisation **exécutable**, pas une intention : dire **quand** elle se déclenche, sur **quels champs**, à **quel seuil**, et **comment**. C'est la porte automatique du cran « anonymisation » (doctrine §6).

## 1. Déclencheur — quand

Déclenche l'anonymisation, sans humain, à la **sortie externe de la firme** :

- toute **publication externe** (site internet, marketing, publication) ;
- tout **livrable rendu hors de la firme** (livrable client).

**Ne déclenche pas** la **réutilisation inter-client interne** : une matière qui circule entre missions ou entre clients, *à l'intérieur de la firme*, reste **nominative**. C'est l'avantage qui compose — l'apprentissage inter-missions (doctrine §9).

**Critère décisif** : « la matière **quitte-t-elle la firme vers l'extérieur** ? » — et **non** « change-t-elle de client ? ».

**Exemple validé.** Un agent capitalise une mission et génère un insight destiné au **site** (sortie externe) → l'anonymisation est **appliquée**, et un message part au **responsable communication**, qui valide la publication (validation **métier**, hors GitHub). En revanche, la même matière réutilisée d'une mission à l'autre **à l'intérieur de la firme** reste **nominative** : aucune anonymisation.

## 2. Champs à traiter — quoi

**Identifiants directs (retirés ou remplacés systématiquement)** : nom du client et entités liées ; noms de personnes ; emails, téléphones ; adresses ; logos et identité visuelle ; codes de projet ou de contrat ; identifiants de systèmes internes, URLs, tenants ; signatures et mentions NDA.

**Quasi-identifiants (généralisés)** : secteur précis → secteur large ; montants exacts → ordres de grandeur ou fourchettes ; effectifs exacts → tranches ; dates précises → période ; et toute **combinaison** qui pointerait vers un acteur unique.

## 3. Seuil — jusqu'où

Règle d'or : **aucune combinaison des attributs conservés ne doit permettre de ré-identifier** le client, une personne ou l'affaire (principe de type *k-anonymat* : jamais de singularité). On retire tous les identifiants directs et on généralise les quasi-identifiants jusqu'à ce qu'il reste **un ensemble plausible d'acteurs, jamais un seul**. On vise une **anonymisation** (irréversible), pas une simple pseudonymisation — qui, elle, reste une donnée personnelle au sens du RGPD.

## 4. Comment — la transformation

Retrait, remplacement par des marqueurs neutres (« Client A », « secteur industriel »), ou généralisation. Si une table de correspondance (réel → anonyme) existe, elle reste dans la **zone de proposition**, jamais dans l'artefact promu. La transformation est **tracée** : qui, quand, quoi.

## 5. Conformité

- **RGPD** : une donnée vraiment anonyme sort du champ ; une donnée seulement pseudonymisée y reste — d'où l'exigence d'irréversibilité pour toute matière **publiée ou rendue hors de la firme**.
- **AI Act** : matière de contexte ou d'apprentissage conforme.
- **NDA** : respecter les clauses propres à chaque mission.
- En cas de doute : **ne pas promouvoir.**

## 6. Articulation avec les crans

Porte **automatique** (déclenchée par règle), orthogonale aux crans. Elle est un **préalable**, pas un substitut : l'artefact anonymisé qui **sort de la firme** (publication, livrable) passe quand même par la **porte humaine du cran *validé*** — tenue par un **rôle métier habilité** (doctrine §6).

## 7. Décisions du gardien

- **Déclencheur : décidé et corrigé (v1.3).** Le déclenchement est la **sortie externe de la firme** (publication externe, livrable hors firme) ; la réutilisation inter-client **interne** ne déclenche pas et reste nominative. Critère décisif arrêté en §1 : « la matière quitte-t-elle la firme vers l'extérieur ? ». *(Corrige le critère antérieur « changement de destinataire » de la v1.1.)*

Restent à confirmer :

1. La liste exacte des champs (à compléter selon vos missions types).
2. Le paramètre de seuil (niveau de généralisation acceptable).
3. La validation juridique (RGPD / AI Act / NDA), idéalement avec un conseil.
