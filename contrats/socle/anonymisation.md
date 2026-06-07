# Anonymisation — Allia Consulting

> **Version** : 1.1 — *candidat*. **Statut** : contrat socle — fait foi.
> **Domicile** : `contrats/socle/anonymisation.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§6 et §9).
> **Changelog** : v1.1 — déclencheur décidé par le gardien (§1) : trois cas (inter-client, entrée au canon partagé, publication externe) ; critère décisif = « changement de destinataire ».
> ⚠️ **Exigence de conformité (RGPD, AI Act, NDA).** Ce document est un candidat *exécutable* ; ses paramètres juridiques doivent être validés par le gardien, idéalement avec un conseil. Je ne suis pas juriste.

## 0. Objet

Rendre l'anonymisation **exécutable**, pas une intention : dire **quand** elle se déclenche, sur **quels champs**, à **quel seuil**, et **comment**. C'est la porte automatique du cran « anonymisation » (doctrine §6).

## 1. Déclencheur — quand

Déclenche l'anonymisation, sans humain, dans trois cas : (a) réutilisation de matière d'un client pour un autre client ; (b) entrée dans le canon partagé (template, benchmark, skill, exemple) ; (c) toute publication externe à l'organisation (livrable client, publication, site).

Ne déclenche pas : réutilisation chez le même client / dans la même mission ; matière purement interne n'ayant jamais touché de donnée client.

Critère décisif : « la matière change-t-elle de destinataire » (autre client, canon, extérieur), et non « interne vs externe ».

## 2. Champs à traiter — quoi

**Identifiants directs (retirés ou remplacés systématiquement)** : nom du client et entités liées ; noms de personnes ; emails, téléphones ; adresses ; logos et identité visuelle ; codes de projet ou de contrat ; identifiants de systèmes internes, URLs, tenants ; signatures et mentions NDA.

**Quasi-identifiants (généralisés)** : secteur précis → secteur large ; montants exacts → ordres de grandeur ou fourchettes ; effectifs exacts → tranches ; dates précises → période ; et toute **combinaison** qui pointerait vers un acteur unique.

## 3. Seuil — jusqu'où

Règle d'or : **aucune combinaison des attributs conservés ne doit permettre de ré-identifier** le client, une personne ou l'affaire (principe de type *k-anonymat* : jamais de singularité). On retire tous les identifiants directs et on généralise les quasi-identifiants jusqu'à ce qu'il reste **un ensemble plausible d'acteurs, jamais un seul**. On vise une **anonymisation** (irréversible), pas une simple pseudonymisation — qui, elle, reste une donnée personnelle au sens du RGPD.

## 4. Comment — la transformation

Retrait, remplacement par des marqueurs neutres (« Client A », « secteur industriel »), ou généralisation. Si une table de correspondance (réel → anonyme) existe, elle reste dans la **zone de proposition**, jamais dans l'artefact promu. La transformation est **tracée** : qui, quand, quoi.

## 5. Conformité

- **RGPD** : une donnée vraiment anonyme sort du champ ; une donnée seulement pseudonymisée y reste — d'où l'exigence d'irréversibilité pour le canon partagé.
- **AI Act** : matière de contexte ou d'apprentissage conforme.
- **NDA** : respecter les clauses propres à chaque mission.
- En cas de doute : **ne pas promouvoir.**

## 6. Articulation avec les crans

Porte **automatique** (déclenchée par règle), orthogonale aux crans. Elle est un **préalable**, pas un substitut : l'artefact anonymisé qui rejoint le canon passe quand même par la promotion du gardien (cran *validé*).

## 7. Décisions du gardien

- **Déclencheur : décidé (v1.1).** Les trois cas et le critère « changement de destinataire » sont arrêtés en §1.

Restent à confirmer :

1. La liste exacte des champs (à compléter selon vos missions types).
2. Le paramètre de seuil (niveau de généralisation acceptable).
3. La validation juridique (RGPD / AI Act / NDA), idéalement avec un conseil.
