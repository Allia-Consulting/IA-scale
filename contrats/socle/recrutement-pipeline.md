# Pipeline de recrutement — processus & rôles par étape — Allia Consulting

> **Version** : 1.1 — *promu*. **Statut** : contrat socle — fait foi.
> **Changelog** : v1.1 — promu via boucle de promotion, 18 juin 2026 : alignement sur la règle de rétention promue (`rgpd-recrutement-candidats.md` §5) et le schéma corrigé du modèle de données (v1.13). §1 : étapes = entretien 1 / 2 / 3 / proposition / accepté / refusé (**drop « sourcing » et « vivier »**) ; note ajoutée « refusé → vivier automatique (2 ans depuis l'inscription, sauf opposition) » ; footer durées « 3 mois / 2 ans … §2 et §5 » → « durée unique 2 ans à compter de l'inscription … §5 ». §3 : « dernier interviewer » matérialisé par la colonne **Owner d'action** (`ResponsableAction`) du modèle de données. v1.0 — candidat, 17 juin 2026 : création. Sous-tâche `T-0013-b` de la chapeau `T-0013`. Canonise le **processus** du pipeline de recrutement : étapes, rôle qui tient chaque étape, notion de **dernier interviewer** (ancrage de la sous-capacité 1b : proposition relue et envoyée par lui). Ce contrat dit le **processus** ; le **droit** (RGPD) vit dans `rgpd-recrutement-candidats.md`, les **données** dans `modele-donnees.md`. La **surface (écran réel)** est explicitement **reportée** à la couche surface (doctrine §10) — non construite ici.
> **Domicile** : `contrats/socle/recrutement-pipeline.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `contrats/socle/rgpd-recrutement-candidats.md` (§1 décision humaine, §3 destinataires, §4 synthèses), `contrats/socle/organisation.md` (§4 bis grille d'habilitation, §5 droits réconciliés), `contrats/socle/modele-donnees.md` (entités Candidat / Synthèse d'entretien, colonne étape), `skills/synthese-entretien/SKILL.md` (production des synthèses), `doctrine/doctrine.md` (§2, §6).
> **Frontière** : ce contrat canonise le **processus** (étapes, rôles, dernier interviewer). Il ne porte **ni la surface** (écran de saisie/vue — couche surface, reportée), **ni le droit RGPD** (cadre dédié), **ni les durées/purge** (cadre §5 + `T-0013-d`).

## 0. Objet

Dire **comment une candidature progresse** chez Allia : les **étapes** du pipeline, **quel rôle tient chaque étape**, et qui porte la **proposition** au candidat. C'est le **processus** dont l'outil (vue candidat, `T-0013`) et la surface (à venir) seront la réalisation. Le **régime des données** candidat (base légale, durées, droits) vit dans `rgpd-recrutement-candidats.md` ; ce contrat n'en est que le pendant **processus**.

## 1. Les étapes du pipeline

Les étapes sont celles de la colonne **étape** de l'entité Candidat (`modele-donnees.md`) :

| Étape | Ce qui s'y passe | Phase RGPD |
|---|---|---|
| entretien 1 | premier entretien ; synthèse produite | instruction |
| entretien 2 | deuxième entretien ; synthèse produite | instruction |
| entretien 3 | troisième entretien ; synthèse produite | instruction |
| proposition | proposition formulée au candidat | instruction |
| accepté | candidat retenu → bascule onboarding (`T-0007`) | fin d'instruction |
| refusé | candidat non retenu → fin de l'instruction | fin d'instruction |

> **refusé → vivier automatique** (2 ans depuis l'inscription, sauf opposition) — `rgpd-recrutement-candidats.md` §5 : le vivier n'est **plus une étape**, c'est le **devenir par défaut d'un refusé** (sauf opposition). La phase RGPD et la **durée unique** (2 ans à compter de l'inscription) font foi dans `rgpd-recrutement-candidats.md` §5 ; ce tableau ne fait que les **rattacher** aux étapes.

## 2. Qui tient chaque étape

La **décision de recrutement reste humaine** — aucune décision automatisée à effet juridique (`rgpd-recrutement-candidats.md` §1). Les **destinataires** des données d'un candidat sont **les seules personnes en charge du recrutement du poste** (cadre §3).

- **Tenue d'une étape** : une étape est tenue par un collaborateur en charge du poste (sourcing, conduite d'entretien, formulation de proposition). Aujourd'hui, firme solo : le gardien-fondateur tient toutes les étapes au titre de son **rôle métier** (associé), jamais au titre de gardien (`organisation.md` §3 bis).
- **Articulation avec la grille d'habilitation** : la **proposition** au candidat est une sortie engageant la firme. Quand elle est **envoyée par un agent**, la porte du cran *validé* est tenue par un **grade habilité** (`organisation.md` §4 bis) ; **envoyée par un humain**, elle est libre (les crans gouvernent les agents, pas les humains — `doctrine.md` §6).

## 3. Le dernier interviewer — porteur de la proposition

**Décision de processus.** La **proposition** est relue et portée par le **dernier interviewer** — la personne qui a mené le dernier entretien du candidat.

- C'est l'ancrage de la sous-capacité **1b** (proposition générée par agent, **relue et envoyée par le dernier interviewer**) : la génération est un dérivé d'agent (zone de proposition, cran auto), mais la **relecture et l'envoi** relèvent de l'humain qui a tenu le dernier entretien.
- L'entité Candidat porte donc, fonctionnellement, la trace du **dernier interviewer** (qui a tenu la dernière étape d'entretien) — point de rattachement de la proposition. Sa **matérialisation** dans le modèle de données est la colonne **Owner d'action** (`ResponsableAction`, `modele-donnees.md` §2 bis) : au stade **proposition**, l'owner d'action **est** le dernier interviewer. Ce contrat fixe la **règle** ; l'outil `T-0013` la réalise.

## 4. Les synthèses dans le pipeline

À chaque étape d'entretien, une **synthèse** est produite par le skill `synthese-entretien` : dérivé écrit en **zone de proposition**, jamais promu par l'agent, soumis à la checklist en dur (`rgpd-recrutement-candidats.md` §4). Elle ne rejoint le domicile candidat (liste « Candidats-Synthèses ») qu'à **validation** (`modele-donnees.md` §2 bis ; `synthese-entretien` §6).

## 5. La surface — reportée, non construite ici

La **vue** concrète (écran de suivi du pipeline) suppose une **surface utilisateur**, qui n'existe pas encore : les écrans de saisie M365 sont à construire (décision d'architecture B.1) et le cockpit utilisateur est un chantier reporté (`doctrine.md` §10). Ce contrat **canonise le processus** que cette surface réalisera le jour venu ; il **n'invente aucune surface**. Tant qu'elle n'existe pas, le suivi se fait sur les listes M365 (`modele-donnees.md`) et la production des synthèses par le skill.

## 6. Droits d'accès — runbook humain, au moindre privilège

Les **destinataires** (personnes en charge du poste, cadre §3) accèdent aux données candidat par **projection d'une décision promue** sur des **groupes Entra**, au moindre privilège, jamais par attribution individuelle (`organisation.md` §5). La **mise en place effective** de ces droits (groupe d'accès recrutement, octrois) est un **runbook humain** du gardien — ni Claude ni un agent ne configurent de droits (`table-des-crans.yaml` : proscrites). Ce contrat pose la **règle** (qui doit accéder) ; l'**exécution** des droits est hors agent.

## 7. Crans et gouvernance

- **Produire une synthèse d'étape** : cran **auto** (dérivé, zone de proposition — `synthese-entretien` §5).
- **Faire progresser un candidat d'une étape à l'autre** : acte **humain** de processus (décision de recrutement humaine, §2) — hors crans quand c'est un humain ; un agent qui proposerait une transition écrit un dérivé (auto), jamais une décision.
- **Envoyer la proposition** : par un **humain** = libre ; par un **agent** = **validé**, porte tenue par un grade habilité (§2 ; `organisation.md` §4 bis).
- **Promouvoir ce contrat** : `promouvoir_contrat_socle` = **validé**, porte humaine du gardien.

## 8. Comment ce contrat évolue

Contrat socle — il fait foi (`doctrine.md` §7) et n'évolue que par la **boucle de promotion** : candidat, avis d'impact, décision du gardien attachée à l'empreinte, promotion, retour arrière par repointage.

---

*Contrat socle candidat — processus du pipeline de recrutement (étapes, rôles, dernier interviewer). Pendant « processus » du cadre RGPD recrutement (qui porte le droit) et du modèle de données (qui porte les faits). La surface est reportée à la couche surface. Il attend la promotion du gardien.*
