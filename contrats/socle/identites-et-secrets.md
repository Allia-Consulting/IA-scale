# Identités et secrets — Allia Consulting

> **Version** : 1.1 — **CANDIDAT** (pas encore promu). **Statut** : contrat socle — *en attente de promotion par le gardien*.
> **Changelog** : v1.1 — candidat, 10 juin 2026 : **extinction de la première dette** du registre §4 (secret client supprimé après preuve `T-0010`). v1.0 — candidat, 10 juin 2026 (session stop-doctrine) : principe **zéro secret applicatif**, modèle des **identités appelantes** (humains / workloads / instruments du gardien), registre des **dettes** de secrets avec échéances.
> **Domicile** : `contrats/socle/identites-et-secrets.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§2 « le dérivé n'est jamais le saisi » — appliqué aux droits, §8 chaîne d'autorité, §9 principe zéro secret), `contrats/socle/organisation.md` (§5 — les droits sont la projection d'une décision promue), `architecture.md` (B.4 bis — double frontière de secret, document de référence, ne fait pas foi).
> **Rattachement** : capacité *Socle d'exploitation / Orchestration des agents* ; chantiers `backlog/chantiers/T-0010.yaml` (branchement des postes), `T-0009.yaml` (validation applicative) ; cran de promotion `promouvoir_contrat_socle` (gardien).

## 0. Objet

Dire **QUI** peut appeler un service du SI et **AVEC QUOI** il s'authentifie. Ce contrat ne décrit pas une politique de gestion des secrets : il vise à **éliminer la classe « secret applicatif » plutôt qu'à la gérer**. Un secret qu'on n'a pas créé n'a pas besoin d'être stocké, distribué, tourné, ni révoqué.

## 1. Principe : ZÉRO SECRET APPLICATIF

**Aucun service du SI ne détient, ne distribue ni n'exige de secret applicatif.** Les humains s'authentifient par leur **identité Entra** ; les workloads par **identité managée** (ou fédération d'identité) ; les instruments du gardien par **l'identité Entra du gardien**.

Tout secret subsistant est une **DETTE** : il est inscrit au **registre** (§4) avec une **échéance** et une **cible d'extinction**. Un secret sans inscription au registre est une violation de ce contrat, pas une exception.

## 2. Modèle des identités appelantes

Trois cas, et eux seuls :

| Appelant | Identité | Flux d'authentification | Secret |
|---|---|---|---|
| **Humain** (poste de collaborateur) | identité **Entra de la personne** | **authorization code + PKCE** sur un client **PUBLIC** (aucun secret). L'accès est **gouverné par Entra** : « **assignment required** » sur l'enterprise app du service + appartenance à un **groupe Entra dédié** (ex. `grp-mcp-graph-users`) | **aucun** |
| **Workload hébergé dans Azure** | **identité managée** (directe, ou **fédérée** sur une app registration via Federated Identity Credential) | jeton émis par la plateforme Azure | **aucun** (zéro rotation) |
| **Instrument du gardien sur son poste** (ex. batch mémoire `T-0005`) | identité **Entra DU GARDIEN** | session interactive (`az login` / navigateur) | **aucun** |

**Renvoi normatif — cas « humain »** : l'appartenance au groupe Entra dédié est la **projection d'une décision promue** (`contrats/socle/organisation.md` §5) — c'est le **même mécanisme** que les droits M365, appliqué aux services du SI. On ne « donne » pas un accès à la main : on promeut une décision, Entra suit.

**Cas « instrument du gardien »** : la dépendance au poste du gardien est **assumée parce qu'elle est une dépendance au RÔLE** (décision du 10 juin 2026) — l'instrument exécute un acte de gouvernance que seul le gardien porte. Elle est bornée à ces instruments et réversible si le rôle se fédère.

## 3. Ce que le modèle interdit

- **Distribuer un secret par poste ou par personne.** Si un humain doit s'authentifier, c'est avec **son** identité Entra — jamais avec un secret partagé ou copié sur sa machine.
- **Créer un secret applicatif pour un nouveau service** sans l'inscrire **immédiatement** au registre (§4), avec une échéance et une cible d'extinction.
- **Tout flux qui authentifie « l'outil » plutôt que l'identité** (humaine ou workload) qui l'emploie. Un outil n'est pas un principal : c'est la personne ou le workload derrière lui qui répond de l'appel.

## 4. Registre des dettes

Les secrets qui existent encore, avec leur trajectoire d'extinction. Ce registre est la **seule** liste faisant foi ; il se met à jour par la boucle de promotion, comme le reste du contrat.

| Secret (dette) | Porteur | Créé le | Expire | Cible d'extinction | Chantier |
|---|---|---|---|---|---|
| Secret **client** (`mcp-client-secret`) | app registration `allia-mcp-graph-client` | 10 juin 2026 | — | **ÉTEINTE le 10 juin 2026** — supprimée après preuve `T-0010` (plus aucun consommateur : les humains passent par leur identité Entra, les workloads futurs par identité managée) | `T-0010` |
| Secret **serveur** Easy Auth (`easyauth-server-secret`) | app registration `allia-mcp-graph-server-auth` (porté par la container app via `microsoft-provider-authentication-secret`) | 10 juin 2026 | **juin 2028** | **suppression ou remplacement par identité managée fédérée** — la doc Microsoft documente Easy Auth **sans secret** pour la validation bearer pure ; MI-FIC documenté App Service, **à confirmer Container Apps**. À instruire en **runbook AVANT juin 2028** | à ouvrir (runbook) |

> Seule dette restante : le secret **serveur** (échéance **juin 2028**) — viser l'**extinction** à ce rendez-vous, pas la rotation.

## 5. Évolution de ce contrat

Ce document est un **contrat socle candidat** : il fait foi après promotion par le gardien, et n'évolue que par la **boucle de promotion** (`doctrine.md` §7) — proposition (PR), avis d'impact, décision du gardien attachée à l'empreinte exacte, promotion, retour arrière par repointage. Toute extinction ou création de secret se trace **ici**, dans le registre §4, dans la même PR que le geste qui la décide.
