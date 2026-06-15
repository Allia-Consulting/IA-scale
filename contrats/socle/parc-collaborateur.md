# Parc collaborateur — politique de poste de travail — Allia Consulting

> **Version** : 1.1 — *candidat*. **Statut** : contrat socle — fait foi.
> **Changelog** :
> - v1.1 (enrichissement candidat) — 15 juin 2026 : §4 — ajout de la politique de sauvegarde des données utilisateur (OneDrive Folder Backup / KFM) : redirection silencieuse et verrouillée des dossiers Bureau et Documents vers OneDrive ; blocage de la synchronisation de comptes OneDrive personnels sur le poste géré. Décision du gardien du 15 juin 2026. Contenu antérieur inchangé.
> - v1.1 (enrichissement candidat) — 13 juin 2026 : §5 précisé sur la posture d'accès conditionnel (security defaults, mode Rapport seul avant bascule, pas d'exclusion de plateforme, compte break-glass comme préalable à la bascule) ; §5 alignement macOS min. Décisions du gardien du 13 juin 2026 lors du runbook T-0006. Contenu antérieur inchangé.
> - v1.1 — candidat, 12 juin 2026 : renseignement des §3–§6 (décisions du gardien, 12 juin 2026) — canal d'acquisition rattaché à l'ABM, profil unique "collaborateur", apps socle, posture de sécurité, groupes d'enrôlement. Le contrat cesse d'être un squelette ; prérequis normatif de T-0006 satisfait à sa promotion.
> - 12 juin 2026 — promu via boucle de promotion ; contenu inchangé hors en-tête/statut. Les §3–§5 restent des squelettes à renseigner par candidats ultérieurs avant exécution de T-0006.
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

- **Canal d'acquisition** : tout matériel du parc est acheté via le canal Apple rattaché à l'**ABM de la firme** (numéro d'organisation / numéro client Apple déclaré dans Apple Business Manager). Conséquence : l'appareil est inscrit automatiquement dans ABM dès la commande — la commande **déclenche** la chaîne ABM → Intune → déploiement du poste (profil, apps, posture), sans geste manuel sur l'appareil. Un matériel acheté hors de ce canal n'entre pas au parc géré (hors politique). L'acte d'achat reste un engagement financier : geste exclusif du gardien (`table-des-crans.yaml` : proscrites) ; l'interfaçage effectif du canal dans ABM relève du runbook T-0006.
- Un profil **unique** : « collaborateur », appliqué à tous les postes de la firme, gardien compris (un seul standard de poste). Le grade est un détail RH (M365), orthogonal au profil (`organisation.md` §8) ; les instruments propres au gardien relèvent de son runbook humain, hors profil Intune.
- **Matériel de référence** : MacBook Pro 14" (puce Apple M5), 24 Go de mémoire unifiée, 1 To de stockage.
- **Plancher contractuel** (évite une re-promotion à chaque refresh Apple) : puce Apple Silicon en cours de commercialisation, ≥ 24 Go, ≥ 1 To, macOS géré.
- **Système géré** : macOS, enrôlé zéro-touch ABM → Intune.

## 4. Applications déployées

- **Socle** (poussé par défaut via Intune) : suite Microsoft 365 (Word, Excel, PowerPoint, Outlook, Teams, OneDrive) ; Claude desktop ; Claude Code CLI (l'authentification OAuth des serveurs MCP `.mcp.json` projet se fait au CLI — fait durci T-0010) ; Google Chrome (navigateur géré) ; git et gh (la connexion Git vise le dépôt commun de la firme — org GitHub Allia-Consulting ; le geste d'authentification `gh auth login` reste celui de la personne, sous son identité).
- **Company Portal** : implicite à l'enrôlement Intune.
- **Apps conditionnées à une fonction ou un périmètre** : aucune à ce stade ; s'ajoutent par candidats ultérieurs.

### Sauvegarde des données utilisateur (OneDrive)

- Les dossiers **Bureau** et **Documents** de chaque poste sont redirigés vers OneDrive (fonction *Folder Backup* / *Known Folder Move*), en mode **silencieux** (sans interaction utilisateur) et **verrouillé** (l'utilisateur ne peut pas désactiver la sauvegarde).
- **Finalité** : continuité des données. En cas de perte ou de remplacement du poste, le collaborateur retrouve ses fichiers Bureau et Documents en se reconnectant à OneDrive avec son identité Entra sur un poste réenrôlé. La reconstruction du **poste** (profil, apps, posture) relève de l'enrôlement Intune ; la restauration des **fichiers** relève de OneDrive. Les deux canaux sont distincts et complémentaires.
- **Périmètre** : Bureau et Documents uniquement (le dossier Téléchargements n'est pas couvert).
- **Nature** : synchronisation miroir, non archive — la suppression d'un fichier local le supprime aussi dans OneDrive.
- Le poste géré ne synchronise **que** les données de la firme : la synchronisation de comptes OneDrive **personnels** est bloquée.
- **Prérequis techniques** (exécution = runbook humain T-0006, jamais un agent) : client OneDrive « standalone » (le client Mac App Store n'est pas supporté pour *Folder Backup*) ; *Full Disk Access* accordé à OneDrive ; profil de configuration « Background Services » autorisant le daemon OneDrive (requis depuis macOS 13).
- **Clés de configuration de référence** (renvoi runbook, non normatif sur la syntaxe) : `KFMSilentOptIn` (tenant firme), `KFMBlockOptOut`, `DisablePersonalSync`.

## 5. Posture de sécurité

- **FileVault obligatoire**, clé de récupération séquestrée dans Intune ;
- **verrouillage de session** à 5 minutes d'inactivité, mot de passe requis immédiatement ;
- **mises à jour macOS gérées par Intune**, fenêtre de conformité : 10 jours calendaires de retard maximum ;
- **accès conditionnel** : l'accès M365 est conditionné à l'état « appareil conforme » (Intune *compliant*) — c'est le verrou qui rend la posture opposable. La stratégie :
  - cible le **seul** groupe `grp-parc-collaborateur` (jamais « tous les utilisateurs »), **exclut le compte du gardien**, et vise **toutes les ressources** ;
  - est mise en service en **deux temps** : créée d'abord en **« Rapport seul »** (observation, aucun blocage), puis basculée en **« Activé »** **seulement après** preuve de bout en bout sur un poste de test enrôlé ;
  - **n'exclut aucune plateforme** (pas d'option « configuration sélectionnée ») ; conséquence assumée : en Rapport seul, un poste macOS peut recevoir une **invite de sélection de certificat** (nuisance d'expérience, sans blocage) ;
- **prérequis Entra à la bascule en « Activé »** :
  - les **security defaults** du tenant et l'accès conditionnel sont **mutuellement exclusifs** ; tant que les security defaults assurent le socle (MFA), ils **ne sont pas désactivés** ; leur désactivation n'est admise qu'au moment où un jeu de stratégies d'accès conditionnel de remplacement (au minimum **MFA pour tous** / **MFA administrateurs**) est prêt à prendre le relais **dans le même geste** — jamais avant ;
  - au moins un **compte break-glass** dédié (cloud-only, non nominatif, exclu de toute stratégie d'accès conditionnel, secret long en coffre) existe et est exclu de la stratégie **avant toute bascule en « Activé »** ; sa création est un **runbook humain** (geste exclusif du gardien) ;
- **version macOS minimale** : N-1 (la version courante ou la précédente ; au 13 juin 2026 : macOS 15 / Sequoia, courant grand public = macOS 26 / Tahoe).

## 6. Groupes Entra d'enrôlement

- **Convention de nommage** : `grp-parc-<profil>` (alignée sur le pattern existant `grp-mcp-graph-users`).
- **Groupe du profil unique** : `grp-parc-collaborateur` — créé en T-0006 (runbook humain), porteur de la politique d'enrôlement.
- L'appartenance au groupe est la **projection d'une décision promue** (`organisation.md` §5) ; ressources liées aux **groupes**, jamais aux individus.

## 7. Frontière politique / exécution — ce qui est runbook, ce qui est chantier

- **Politique** (ce document) : canonisée ici, promue par le gardien. **C'est tout ce que ce contrat porte.**
- **Configuration effective** ABM/Intune/Entra : **runbook humain** (`T-0006`). Ni Claude ni un agent ne paramètrent le tenant, la sécurité ou des droits (proscrites).
- **Réconciliation automatique politique → Intune** : chantier **Phase 3/4** (`T-0008`), inscrit au backlog, **non construit** aujourd'hui — parallèle au réconciliateur de droits (`organisation.md` §5, plan §9 T-4.3).

## 8. Articulation avec l'onboarding

Le parc est l'une des **trois réconciliations** de la capacité chapeau **onboarding & intégration** (`organisation.md` §2) : pour une décision promue « X devient collaborateur du périmètre P », l'onboarding réconcilie le **matériel** (ce contrat), les **droits** (Entra/SSO) et la **connaissance** (Claude/Git). Déclencheur : passage **candidat → collaborateur** (création de l'identité Entra). Voir `backlog/chantiers/T-0007.yaml`.

## 9. Comment ce contrat évolue

Contrat socle **promu** — il fait foi (doctrine §7). Tout changement de politique (profil, apps, posture, groupes) est un candidat promu — jamais une édition directe de la config.

---

*Contrat socle promu — il canonise la POLITIQUE de parc, pas son exécution. Il fait foi et évolue par la boucle de promotion. La config ABM/Intune/Entra est un runbook humain ; la réconciliation auto est un chantier Phase 3/4.*
