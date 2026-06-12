# Dépôt de fondations — Allia

> **Une seule vérité.** Ce dépôt est le domicile canonique des *règles* d'Allia. Tout endroit qui les affiche (un Projet Claude, un wiki, une présentation, un PDF) en est un *consommateur*, jamais un double éditable. On n'édite jamais une règle ailleurs qu'ici.

Ce dépôt porte les **règles** qui font tourner et gouvernent l'entreprise augmentée. Les **données** (missions, temps, imputations, livrables) vivent dans M365. Les deux ne se mélangent jamais.

## Par où entrer

- **Tu découvres Allia ?** Lis `doctrine/doctrine.md` (le pourquoi et les règles), puis `backlog/plan.md` (le chantier).
- **Tu es Claude Code ?** Lis d'abord `CLAUDE.md` : il dit où résoudre la doctrine, les contrats et la table des crans, et rappelle la règle ferme — *on résout le canon à l'exécution, on ne copie pas.*
- **Tu veux changer quelque chose ?** Tu ne modifies rien directement : tu ouvres un **candidat** (voir « Comment on change quelque chose »).

## Les trois documents socle

| Document | Dit | Chemin |
|---|---|---|
| **Doctrine** | Le pourquoi et les règles : rôles, principes, crans, boucle de promotion | `doctrine/doctrine.md` |
| **Plan de construction** | Le chantier : comment bâtir le SI augmenté, étape par étape | `backlog/plan.md` |
| **Organisation & délégations** | Qui répond de quoi : périmètres et règles de délégation | `contrats/socle/organisation.md` |

Les trois sont des **contrats socle** : ils appartiennent au gardien et n'évoluent que par la boucle de promotion.

## Comment on change quelque chose (la boucle de promotion)

1. **Proposer** — préparer un candidat via Claude (jamais en éditant le dépôt à la main) ; un aperçu fidèle est généré.
2. **Vérifier** — l'agent-gardien contrôle la conformité aux contrats et calcule le rayon d'impact ; il rejette ce qui casse.
3. **Décider** — le gardien approuve la version précise (l'approbation est attachée à l'empreinte, pas au résumé).
4. **Promouvoir** — le pointeur canonique avance (merge) : seule écriture autorisée dans le dépôt.
5. **Propager** — les consommateurs résolvent la nouvelle version à l'exécution (pull).
6. **Revenir en arrière** — repointer, en une seule action. Toujours possible, parce qu'on n'a jamais copié.

## La chaîne d'autorité : le guide → Claude → M365

Les décisions vivent dans **le guide** (ce dépôt) ; **Claude** les résout et les exécute ; **M365** applique — données comme droits. Modifier une décision — y compris une délégation et les droits qui en découlent — c'est modifier le guide, sous la porte de promotion du gardien. M365 suit alors en conséquence, par réconciliation au moindre privilège. **Aucun droit ni aucune règle ne se modifie hors de cette chaîne**, et le déploiement reste sous le contrôle du gardien.

## Le substrat

| Nature | Domicile |
|---|---|
| Données (les faits) | M365 |
| Règles (les versions du SI) | Ce dépôt (Git) |
| Journal d'approbation | Historique Git (qui a approuvé quoi, quand) |

## Structure du dépôt

```
/
  README.md                    ce fichier
  CLAUDE.md                    contexte de résolution pour Claude Code
  architecture.md              document de référence — décrit, ne gouverne pas
  .mcp.json                    branchement Claude Code au serveur MCP Graph (scope project, aucun secret)
  doctrine/
    doctrine.md                contrat socle racine
  contrats/
    socle/
      modele-donnees.md        mapping des faits vers M365
      table-des-crans.yaml     type d'action → cran (machine-readable)
      anonymisation.md         champs, seuil, déclencheur (RGPD / AI Act)
      organisation.md          périmètres & délégations
      design-system.md
      identites-et-secrets.md  modèle des identités appelantes (humains / workloads)
      memoire-organisation.md  synthèse hebdomadaire candidate (batch nocturne)
      rgpd-ecoute-teams.md     écoute Teams — cadre RGPD
      parc-collaborateur.md    politique de poste de travail
    local/
      <perimetre>/...          contrats locaux, un par animateur
  skills/
    <skill>/SKILL.md           skills versionnés, activables
  agents/
    <agent>/profil.yaml        profil = composition de skills + crans
  backlog/
    plan.md                    plan de construction (couche prose)
    chantiers/*.yaml           tâches agent-consommables
  outils/
    mcp-graph/                 serveur MCP Graph — code du connecteur
  .github/
    pull_request_template.md
    CODEOWNERS                 le gardien sur doctrine/ et contrats/socle/
    workflows/conformite.yml   l'agent-gardien (contrôle de conformité en CI)
    workflows/build-mcp-graph.yml  preuve image, sans push
```

## Statut & rôles

L'ensemble des contrats socle est **promu** (fait foi). Quatre rôles, et eux seuls, interviennent : **gardien du temple** (garant de la cohérence, promeut), **animateur de périmètre** (propose sur son périmètre), **agent** (exécute selon les crans), **utilisateur** (se sert du système). Aujourd'hui, l'organisation repose sur un gardien unique.

---
*Une seule vérité, propagée par contrats (pull) et gouvernée par les quatre rôles. On référence, on ne copie pas.*
