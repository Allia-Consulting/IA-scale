# Onboarding & intégration — Skill
> **id** : `onboarding`
> **Version** : 1.0 — *candidat*. **Nature** : skill (capacité chapeau).
> **Changelog** : v1.0 — candidat, 28 juin 2026 : création. Chantier `backlog/chantiers/T-0007.yaml` (capacité chapeau onboarding & intégration). Orchestrateur des réconciliateurs EXISTANTS, sans nouveau code MCP : matériel via `reconcilier_groupe_parc` (`T-0008`, soldé), droits via `reconcilier_groupe_perimetre` (`T-0019`, soldé). Impose la contrainte d'ordonnancement RGPD (information « mémoire d'organisation » AVANT toute activation d'écoute — `rgpd-ecoute-teams.md` §5). Ne décide rien, ne promeut rien, n'écrit aucun droit hors de la chaîne le guide → Claude → M365.
> **Domicile** : `skills/onboarding/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `contrats/socle/organisation.md` (§2 capacité chapeau, §3 titulaires, §5 chaîne d'autorité des droits + groupes socle/périmètre), `contrats/socle/parc-collaborateur.md` (§6 groupe d'enrôlement `grp-parc-collaborateur`), `contrats/socle/rgpd-ecoute-teams.md` (§5 information préalable AVANT écoute), `contrats/socle/annexes/rgpd-ecoute-teams--annexe-3-gabarit-information.md` (gabarit d'information), `contrats/socle/identites-et-secrets.md` (§2 `grp-mcp-graph-users`), `contrats/socle/table-des-crans.yaml`, `doctrine/doctrine.md` (§2, §6, §7), `CLAUDE.md`.
## 1. Objet
Orchestrer, pour une **décision promue** « X devient collaborateur du périmètre P », les **trois réconciliations d'une même vérité** : **matériel** (parc), **droits** (Entra/SSO), **connaissance** (canon Git + mémoire d'organisation). C'est une capacité **chapeau** (`organisation.md` §2) : elle n'invente aucun pouvoir nouveau — elle **compose** des réconciliateurs au moindre privilège qui existent déjà, et impose l'**ordre RGPD** de l'intégration.
> **Ce skill ne décide rien.** L'état désiré dérive d'une décision **déjà promue** dans le canon (`organisation.md` §3). Le skill **résout** cet état désiré et **projette** le delta par les outils existants ; il ne crée pas de délégation, n'attribue aucun droit à la main, ne promeut jamais (doctrine §7). « Le dérivé n'est jamais le saisi » appliqué à l'intégration.
> **Déclencheur (figé).** Le passage **candidat → collaborateur**, matérialisé par la **création de l'identité Entra** de la personne. **PAS** l'entrée en liste de recrutement (découplage volontaire, `organisation.md` §2 et `T-0007`). La liste de recrutement reste un processus humain.
## 2. Entrées
- `personne` — objectId Entra (GUID) du nouveau collaborateur (identité **déjà créée** — préalable, runbook humain).
- `perimetre` — le périmètre P dont la personne devient collaboratrice (socle pour tous ; + animation si délégation promue).
- `decision_promue` — référence (chemin + SHA) de la version d'`organisation.md` qui porte la décision. La résolution lit le canon à ce SHA, jamais une copie.
> **Règle de fidélité.** Si une entrée manque ou ne se résout pas dans le canon promu, **s'arrêter** et le signaler. Ne jamais inventer un objectId, un groupe, ou une délégation non promue (doctrine §2).
## 3. Calcul de l'état désiré (résolu depuis le canon, jamais inventé)
Pour la personne et le périmètre, le skill calcule l'**état désiré** de chaque jambe en lisant `organisation.md` :
- **Socle (tout collaborateur)** — `organisation.md` §5 « ressources socle gouvernées par groupe » :
  - **parc / enrôlement** : la personne doit appartenir à `grp-parc-collaborateur` (jambe matériel, §4).
  - **licence M365** : la personne doit appartenir à `grp-collaborateurs-m365`. **Aucun réconciliateur MCP n'existe pour ce groupe** → **runbook humain** (§4, jambe licence). Le skill le **signale**, il ne le projette pas.
  - **accès SharePoint** : socle non cloisonné, ouvert par l'appartenance au socle collaborateur (`organisation.md` §5) — pas d'action par individu.
  - **`grp-mcp-graph-users`** : **non socle universel** (`organisation.md` §5, `identites-et-secrets.md` §2) — n'est ajouté **que** si la fonction de la personne requiert l'accès au service MCP. Par défaut : **non**.
- **Périmètre (si délégation promue)** — `organisation.md` §3/§5 : si la décision promue fait de X l'**animateur** de P, la personne doit appartenir au **groupe Entra du périmètre** (ex. `anim-communication`) — jambe droits, §4. Si X est seulement **collaborateur** (pas animateur), **aucun** groupe de périmètre n'est concerné.
> L'état désiré est une **liste d'objectId** par groupe (les membres attendus), pas une instruction par personne : les réconciliateurs réconcilient un **ensemble** (idempotent, delta seul). Le skill construit `membres_attendus` = état canonique du groupe, incluant la nouvelle personne.
## 4. Les trois jambes (+ licence) — comment chacune se projette
| Jambe | Moyen | Cran | Note |
|---|---|---|---|
| **Matériel (parc)** | `reconcilier_groupe_parc(grp-parc-collaborateur, membres_attendus)` | **auto** (réconciliation idempotente, interne, réversible) | Outil existant (`T-0008`, soldé). Liste blanche dédiée `GRAPH_GROUPES_PARC_AUTORISES`. L'enrôlement Intune suit l'appartenance au groupe (`parc-collaborateur.md` §6). |
| **Droits (périmètre)** | `reconcilier_groupe_perimetre(groupe-du-périmètre, membres_attendus)` — **seulement si animation déléguée et promue** | **auto** (réconciliation idempotente) ; la **délégation elle-même** est **validé** (déjà promue en amont) | Outil existant (`T-0019`, soldé). Liste blanche `GRAPH_GROUPES_PERIMETRE_AUTORISES` + AU `au-perimetres-droits`. Ressources liées au groupe, jamais aux individus. |
| **Connaissance** | Accès **canon** (org GitHub) + **mémoire d'organisation** | **runbook humain** (ni Claude ni agent ne posent un droit GitHub org — plan §2, `CLAUDE.md` garde-fous) | Pas un groupe Entra du tenant : le skill **prépare et signale** l'octroi (invitation org GitHub, accès Projet Claude/mémoire), il ne l'exécute pas. |
| **Licence M365 (socle)** | Appartenance à `grp-collaborateurs-m365` | **runbook humain** | Aucun réconciliateur MCP pour ce groupe à ce jour (décision : licence = ressource sensible, hors périmètre des outils actuels). Le skill **signale** l'écart à combler à la main. |
> **Moindre privilège préservé.** Le skill n'élargit **aucune** liste blanche ni aucun scope. Il appelle les outils **tels qu'ils sont bornés** ; une cible hors liste blanche lève `PermissionError` côté serveur (défense en profondeur, `server.py`). Le skill ne contourne jamais cette borne.
## 5. Contrainte d'ordonnancement RGPD (en dur)
`rgpd-ecoute-teams.md` §5 : l'**information préalable « mémoire d'organisation »** (gabarit = annexe 3) est délivrée **AVANT toute activation de l'écoute** Teams/Claude du collaborateur. C'est une **étape d'ordonnancement**, pas une case de fin de parcours.
Séquence imposée par le skill :
1. **Création identité Entra** (préalable, runbook) → déclencheur.
2. **Information « mémoire d'organisation »** délivrée à la personne (annexe 3) — **trace** de la remise.
3. **Réconciliations** matériel / droits / connaissance (§4).
4. **Activation de l'écoute** mémoire d'organisation pour cette personne (`T-0005`) — **interdite tant que l'étape 2 n'est pas tracée**.
> **Firme solo / petit effectif aujourd'hui** : peu ou pas d'écoute active, mais la contrainte est **armée** dès le premier collaborateur écouté (`rgpd-ecoute-teams.md` §5). Le skill **refuse** de signaler l'onboarding « complet » si l'étape 2 manque et qu'une écoute serait activable.
## 6. Procédure
1. **Vérifier le déclencheur** : l'identité Entra de la personne existe (sinon, s'arrêter — préalable runbook).
2. **Résoudre la décision promue** (`decision_promue` : chemin + SHA) dans `organisation.md` ; confirmer que X est bien collaborateur de P (et, le cas échéant, animateur).
3. **Calculer l'état désiré** de chaque groupe concerné (§3) : `membres_attendus` = état canonique incluant la personne.
4. **Délivrer l'information RGPD** (§5, étape 2) **avant** toute projection touchant l'écoute ; tracer la remise.
5. **Projeter le delta** :
   - matériel : `reconcilier_groupe_parc(...)` ;
   - droits : `reconcilier_groupe_perimetre(...)` **si** animation déléguée promue ;
   - connaissance + licence : **préparer et signaler** le runbook humain (ne pas exécuter).
6. **Vérifier l'idempotence** : un rejeu immédiat doit produire un **delta vide** sur les jambes projetées (preuve que l'état réel = état désiré).
7. **Restituer** un rapport d'onboarding (§7) : ce qui a été projeté, ce qui reste en runbook humain, l'état RGPD.
> L'agent **ne promeut jamais** la décision (elle est déjà promue), **ne crée jamais** d'identité ni de licence, **ne pose jamais** un droit GitHub org. Il **réconcilie** et **signale**.
## 7. Format de sortie (rapport d'onboarding)
~~~
# Onboarding — <personne (objectId)>, périmètre <P>
Décision promue : organisation.md @ <SHA>
Déclencheur : identité Entra créée (oui / NON → arrêt)
## RGPD — information mémoire d'organisation (préalable à l'écoute)
- Information annexe 3 remise : <oui (date/trace) / NON — écoute non activable>
## Jambes projetées (réconciliation idempotente)
- Matériel (parc, grp-parc-collaborateur) : ajoutés=<…> retirés=<…> inchangés=<…>
- Droits (périmètre <groupe>) : <projeté / sans objet (pas d'animation déléguée)>
## Jambes en runbook humain (signalées, NON exécutées par l'agent)
- Connaissance : invitation org GitHub + accès mémoire/Projet Claude — <à faire>
- Licence M365 (grp-collaborateurs-m365) : ajout au groupe — <à faire>
## Idempotence
- Rejeu : delta vide sur jambes projetées <oui / non>
~~~
**Ton** : voix Allia (sobre, factuel). Tout rendu visuel suit `design-system.md` (on consomme, on ne recopie pas).
## 8. Crans (résolus via `table-des-crans.yaml`)
| Action | Cran | Note |
|---|---|---|
| **Réconcilier parc / périmètre** (delta idempotent) | **auto** | réversible, interne — l'agent agit seul, dans la borne des listes blanches |
| **Délivrer l'information RGPD** (étape d'ordonnancement) | **auto** (trace) | préalable obligatoire à l'écoute (`rgpd-ecoute-teams.md` §5) |
| **Délégation / décision d'organisation** | **validé** | porte humaine — **déjà promue en amont** ; le skill ne la crée pas |
| **Octroi connaissance (GitHub org) / licence M365** | **runbook humain** | ni Claude ni agent (plan §2) ; le skill signale |
| **Activer l'écoute mémoire** d'un collaborateur | **subordonné** | interdit tant que l'information (§5) n'est pas tracée |
## 9. Zone de proposition
Le **rapport d'onboarding** est un **dérivé** : il s'écrit en zone de proposition (`modele-donnees.md` §3), il ne devient un fait promu qu'à validation tracée. Les réconciliations, elles, agissent directement sur l'appartenance aux groupes (cran auto, réversible par repointage) — ce n'est pas une écriture de source, mais la projection d'une décision déjà promue (chaîne `organisation.md` §5).
## 10. Critères de qualité (Definition of Done)
- [ ] Le **déclencheur** est l'identité Entra créée, **jamais** l'entrée en liste de recrutement.
- [ ] L'**état désiré** est **résolu depuis le canon promu** (chemin + SHA), aucun objectId ni groupe inventé.
- [ ] L'**information RGPD mémoire** (annexe 3) précède toute activation d'écoute (§5) ; l'absence de trace **bloque** l'activation.
- [ ] **Matériel** projeté par `reconcilier_groupe_parc` ; **droits** par `reconcilier_groupe_perimetre` **uniquement** si animation déléguée promue.
- [ ] **Connaissance** et **licence M365** **signalées** comme runbook humain, **non exécutées** par l'agent.
- [ ] **Idempotence** vérifiée : rejeu = delta vide sur les jambes projetées.
- [ ] **Aucune liste blanche ni aucun scope élargi** ; les bornes serveur restent intactes.
- [ ] L'agent **ne promeut pas**, **ne crée ni identité ni licence**, **ne pose aucun droit GitHub org**.
## 11. Évolution
Ce skill est un **candidat** (procédure allégée, portée locale, `doctrine.md` §5). Sa promotion suit la boucle (`doctrine.md` §7) avec montée de version. Retour arrière = repointage. **Incréments nommés** : un réconciliateur de **licence** (`grp-collaborateurs-m365`) le jour où la licence passe de runbook à projection gouvernée ; une jambe **connaissance** automatisée si l'accès org GitHub devient réconciliable au moindre privilège.
