# Parc collaborateur — politique de poste de travail — Allia Consulting

> **Version** : 1.0 — **CANDIDAT** (pas encore promu). **Statut** : contrat socle — *en attente de promotion par le gardien*.
> **Domicile** : `contrats/socle/parc-collaborateur.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§2, §8 — chaîne d'autorité étendue aux **appareils**, ligne candidate v1.4), `contrats/socle/organisation.md` (§2 capacité « parc & gestion de poste » ; §5 réconciliation au moindre privilège).
> **Rattachement** : capacité *Socle d'exploitation & gouvernance / parc & gestion de poste* ; chantiers `backlog/chantiers/T-0006.yaml` (config effective, runbook) et `backlog/chantiers/T-0008.yaml` (réconciliateur politique→Intune, Phase 3/4).
> **Frontière** : ce contrat **canonise la POLITIQUE**, pas l'exécution. La **configuration effective** (ABM/Intune/Entra) est un **runbook humain** ; aucun agent ne configure le tenant, la sécurité ou des droits (`table-des-crans.yaml` : proscrites ; garde-fous `CLAUDE.md`).

## 0. Objet

Dire **ce qu'est un poste de travail conforme chez Allia** : son **profil par fonction**, les **applications déployées**, la **posture de sécurité**, et les **groupes Entra d'enrôlement**. C'est la **décision** (« le guide ») dont la configuration ABM/Intune est la **projection** — jamais l'inverse (doctrine §8).

## 1. Principe — la politique est un dérivé promu, pas une config saisie

La configuration d'un poste est un **dérivé** d'une décision de parc promue ici, réconciliée dans M365/Intune, **jamais paramétrée à la main** (doctrine §2 et §8, ligne candidate « appareils »). On change la **politique** dans le guide, sous la porte du gardien ; ABM/Intune/Entra **suivent** par réconciliation au moindre privilège. C'est « le dérivé n'est jamais le saisi » appliqué à l'**appareil**.

## 2. Les trois couches — ABM → Intune → Entra

| Couche | Rôle | Ce que la politique décide ici | Exécution |
|---|---|---|---|
| **Apple Business Manager (ABM)** | Rattache le matériel à la firme, le pousse vers la gestion | quels matériels entrent dans le parc géré | **runbook humain** (tenant/ABM) |
| **Intune** | Applique le profil de poste (apps, posture, conformité) | profil par fonction, apps déployées, posture de sécurité | **runbook humain** ; réconciliation auto = Phase 3/4 |
| **Entra** | Porte les **groupes d'enrôlement** qui lient l'appareil à la politique | quels groupes d'enrôlement, par profil | **runbook humain** ; projection au moindre privilège (`organisation.md` §5) |

## 3. Profil de poste (par fonction)

La politique définit, **par fonction** (le détail concret est volatil — réalisation, doctrine §2), un profil de poste : modèle/type de matériel attendu, système géré, niveau d'accès de base. *(À renseigner par le gardien à la promotion — squelette candidat ; aucune valeur n'est figée tant que non promue.)*

## 4. Applications déployées

Liste des applications poussées par défaut (productivité, sécurité, métier) et de celles conditionnées à une fonction ou un périmètre. *(Squelette candidat — à compléter/valider par le gardien.)*

## 5. Posture de sécurité

Exigences minimales de conformité d'un poste : chiffrement du disque, verrouillage, mises à jour gérées, télémétrie de conformité, conditions d'accès conditionnel. *(Squelette candidat — paramètres exacts à valider par le gardien, idéalement avec un conseil sécurité.)*

## 6. Groupes Entra d'enrôlement

La politique nomme les **groupes Entra d'enrôlement** par profil. L'appartenance à un groupe **ouvre** la politique correspondante ; elle se **projette** depuis une décision promue, au **moindre privilège**, jamais saisie à la main (`organisation.md` §5). Les ressources sont liées aux **groupes**, jamais aux individus.

## 7. Frontière politique / exécution — ce qui est runbook, ce qui est chantier

- **Politique** (ce document) : canonisée ici, promue par le gardien. **C'est tout ce que ce contrat porte.**
- **Configuration effective** ABM/Intune/Entra : **runbook humain** (`T-0006`). Ni Claude ni un agent ne paramètrent le tenant, la sécurité ou des droits (proscrites).
- **Réconciliation automatique politique → Intune** : chantier **Phase 3/4** (`T-0008`), inscrit au backlog, **non construit** aujourd'hui — parallèle au réconciliateur de droits (`organisation.md` §5, plan §9 T-4.3).

## 8. Articulation avec l'onboarding

Le parc est l'une des **trois réconciliations** de la capacité chapeau **onboarding & intégration** (`organisation.md` §2) : pour une décision promue « X devient collaborateur du périmètre P », l'onboarding réconcilie le **matériel** (ce contrat), les **droits** (Entra/SSO) et la **connaissance** (Claude/Git). Déclencheur : passage **candidat → collaborateur** (création de l'identité Entra). Voir `backlog/chantiers/T-0007.yaml`.

## 9. Comment ce contrat évolue

Contrat socle **candidat** : il devient *fait foi* à sa **promotion** par le gardien (doctrine §7). Tout changement de politique (profil, apps, posture, groupes) est ensuite un candidat promu — jamais une édition directe de la config.

---

*Contrat socle candidat — il canonise la POLITIQUE de parc, pas son exécution. Il attend la promotion du gardien. La config ABM/Intune/Entra est un runbook humain ; la réconciliation auto est un chantier Phase 3/4.*
