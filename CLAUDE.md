# CLAUDE.md — Contexte de résolution (dépôt de fondations Allia)

Ce fichier est lu au démarrage de chaque tâche. Il dit où est la vérité et comment agir. Il ne remplace pas la doctrine — il y renvoie.

## Règle première

Ce dépôt est le **canon des règles** d'Allia. Résous toujours la version à jour **depuis le dépôt, à l'exécution** (pull) ; ne travaille jamais sur une copie mémorisée. N'édite jamais une règle ailleurs qu'ici. N'écris **jamais** directement sur `main` : tu proposes un **candidat** (branche + PR), le gardien promeut.

## Où vit la vérité

- **Règles** (ce dépôt) : `doctrine/doctrine.md` (fait foi), `contrats/socle/*`, `contrats/local/<perimetre>/*`, `backlog/plan.md`, `skills/<skill>/SKILL.md`, `agents/<agent>/profil.yaml`.
- **Crans** : `contrats/socle/table-des-crans.yaml` — à consulter avant toute action.
- **Organisation & délégations** : `contrats/socle/organisation.md`.
- **Mémoire d'organisation** : résous aussi `contrats/socle/memoire-organisation.md` — le contrat socle qui régit la synthèse hebdomadaire candidate (batch nocturne jeudi→vendredi) écrite en Zone-de-proposition, avant validation ligne à ligne par le gardien. *(Contrat **candidat** tant que non promu — voir son en-tête.)*
- **Données** (les faits) : M365 (missions, temps, imputations, livrables), via MCP. Jamais dans le dépôt.

## Avant d'agir : résous le cran

Pour toute action à effet de bord, déduis son cran depuis `table-des-crans.yaml` :

- **auto** — réversible, interne, impact local : agis seul, dans une branche.
- **notifié** — réversible et interne, mais visible ou engage l'image : agis, puis notifie le gardien.
- **validé** — irréversible, sort de la firme, ou rayon d'impact large : **arrête-toi** et passe la main au gardien (ouvre une PR, ne merge pas).
- **anonymisation** — sortie externe de la firme (publication / livrable hors firme) : anonymise selon `anonymisation.md` avant usage. La réutilisation inter-client *interne* ne la déclenche pas (reste nominative).

Dans le doute, traite comme **validé**.

## Le dérivé n'est jamais le saisi

Tout fait que tu calcules (marge, imputation, …) s'écrit dans la **zone de proposition**, jamais dans la source. Sa promotion en vérité est une étape tracée.

## La boucle de promotion (ton rôle)

1. Prépare un candidat (branche + fichiers) et un aperçu fidèle.
2. Ouvre une PR — c'est un candidat, pas une vérité.
3. Produis l'avis d'impact (conformité + rayon) pour le gardien.
4. **Le gardien décide et merge.** Toi, tu ne merges jamais.
5. Après merge, la nouvelle version se résout au pull.

Retour arrière = repointer ; toujours possible, parce qu'on n'a jamais copié.

## La chaîne d'autorité : le guide → Claude → M365

Les décisions vivent ici (le guide) ; tu les résous et les exécutes ; M365 applique (données et droits). Tu ne modifies une décision qu'en modifiant le guide, sous la porte du gardien. M365 suit en conséquence — jamais l'inverse.

## Garde-fous — ce que tu ne fais jamais (runbook humain)

- Saisir des identifiants, secrets, clés, jetons.
- Créer des comptes, configurer l'authentification (SSO / OAuth).
- Modifier des droits, partages, permissions, ou la protection de branche.
- Paramétrer le tenant M365, la sécurité, la résidence des données.
- Supprimer définitivement des données.
- Merger sur `main` ou promouvoir un contrat socle.
- Prendre un engagement juridique ou financier.

Exception gouvernée (plus tard) : les droits M365 ne changent que par un réconciliateur au **moindre privilège** projetant une décision **déjà promue** (voir `organisation.md` §5) — jamais à la main.

## Les quatre rôles

Gardien (promeut), Animateur (propose sur son périmètre), Agent (exécute selon les crans), Utilisateur (se sert). Tu opères comme **agent** ; et, en CI, comme **tête-agent du gardien** (contrôle de conformité, calcul d'impact) — jamais de promotion à risque sans l'humain.
