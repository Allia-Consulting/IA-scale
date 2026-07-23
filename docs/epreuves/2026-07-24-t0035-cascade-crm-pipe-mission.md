# Épreuve 2026-07-24 (T-0035 point 3 — boucle pipe commercial → mission) — VERTE : gestes CRM + bascule Gagnée proposante + couture opportunité → mission

Entrée d'épreuve du 2026-07-24. Fait nouveau ; aucune requalification d'un soldé au-delà de
ce qui est prouvé ici, aucune réécriture d'entrée existante. **VERDICT : VERT** pour le
**point 3** (gestes d'écriture guidée CRM), avec une **note d'honnêteté** sur la
matérialisation de l'espace de mission (§3, geste gardien tant que `T-0024` n'est pas livré).

## 1. Ce qui a été construit et mergé (PR #248–#254)

| PR | Surface | Objet |
|---|---|---|
| **#248** | cockpit SPFx | table d'opportunités éditable + formulaire « nouvelle opportunité » + édition en ligne étape/montant |
| **#249** | cockpit | bump solution 1.4.4.0 → **1.4.5.0** (mise en service des gestes pipe) |
| **#250** | serveur MCP Graph | `creer_espace_mission` (et `deposer_document_mission`) acceptent un **4e segment OPTIONNEL numérique** (code mission), rétro-compatible (défaut → 3 segments) ; **image 0.17.0** |
| **#251** | canon `modele-donnees.md` §2 bis | `CodeMission` = **ENTIER** (≥ 1, sans zéro de tête) + allocation `max(existants)+1` à l'ouverture, réécrit dans l'opportunité gagnée ; forme déjà câblée (`gabarit-<code>`, `saisie-<code>`) |
| **#252** | cockpit | bascule « **Gagnée** » = geste **PROPOSANT sur confirmation** (écrit l'étape, **pas** le code) ; bump → **1.4.6.0** |
| **#253** | cockpit | aperçu client = **`NomCompte` lisible** (défaut « CPT-001 » corrigé) ; bump → **1.4.7.0** |
| **#254** | canon `cadrage-mission` | entrée « **Opportunité Gagnée** » reconnue ; réécriture `CodeMission → CRM` documentée comme **geste GARDIEN** (promotion), hors écriture agent |

## 2. Mise en service (geste gardien)

- **SPFx `.sppkg` 1.4.7.0** déployé à l'**App Catalog** du tenant.
- **Image MCP Graph 0.17.0** déployée sur **Azure Container Apps** (`ca-allia-mcp-graph`),
  révision **Healthy**, **100 % du trafic**.

## 3. Épreuves sur le réel (chaque état relu, persisté)

### 3.a — Create / Edit (gestes guidés CRM, sous SSO)

Une opportunité de test (**item CRM id 3**) **créée** au cockpit (Qualification, **1000 €**,
compte **Arabelle**), puis **éditée en ligne** (Proposition, **2000 €**), puis **supprimée**
(corbeille). Les gestes **create** et **edit** sont prouvés au cockpit sous l'identité de
l'utilisateur (SSO SPHttpClient), chaque état relu persisté.

### 3.b — Bascule « Gagnée » proposante (confirmation, Annuler = aucune écriture)

La confirmation affiche le nom composé **« 2026 - Arabelle Solutions - Leader M365 »** (client
= `NomCompte` lisible, conforme #253). **Annuler → AUCUNE écriture** : l'opportunité **O-001**
reste **Qualification** à la source (état relu). Le geste écrit **seulement l'étape**, jamais le
code mission (conforme #252 et au canon §2 bis : le code est attribué à l'ouverture).

### 3.c — Cascade opportunité → espace de mission

Espace **« 2026 - Arabelle Solutions - Leader PowerBI - 2 »** créé sous
**« Documents partagés / General / 03 - Livrables de mission »**, arbre figé
**01 - Pilotage / 02 - Livrables**. Couture **cohérente avec O-002** (Étape = **Gagnée**,
**`CodeMission` = 2**) : le 4e segment du nom porte bien le code entier de l'opportunité gagnée.

> **NOTE D'HONNÊTETÉ.** Cet espace a été **matérialisé par un GESTE GARDIEN** (API SharePoint
> sous identité utilisateur), **non** par un appel de la brique `creer_espace_mission` : c'est le
> chemin **sanctionné par le canon tant que `T-0024` n'est pas livré** (allocateur atomique du
> code + automatisation de la création d'espace par l'agent). La **logique 4-segments** de la
> brique est, elle, **prouvée par la CI** (check « Tests garde-fous server.py » — miroir
> `_composer_nom_espace` / `apercuNomMission`, PR #250), pas par un appel live dans cette épreuve.

## 4. Garde-fous tenus

- **Agent → dérivés en Zone-de-proposition uniquement** ; les **sources** (CRM) sont écrites par
  l'humain (création/édition guidées sous SSO ; bascule Gagnée = écriture de l'étape par
  l'utilisateur). La **réécriture `CodeMission → CRM`** reste une **promotion, cran gardien**.
- **Porte humaine** tenue sur toute PR de **canon socle / surface sensible** : #250 (server.py),
  #251 et #254 (canon) ont vu l'**auto-approbation `skipped`** (RISQUE large).
- **Anti-faux-vert systématique** : sur chaque PR, `.diff` réel + check-runs sur le `head_sha`
  exact, conclusion sur `completed/success` seulement.

## 5. Restes nommés (non construits ici)

- **`T-0024`** — allocateur **atomique** du code mission (`max+1` sans course) **et**
  automatisation de la création d'espace par l'agent (`creer_espace_mission` en bout de
  `cadrage-mission`). D'ici là, allocation + matérialisation d'espace = **geste gardien tracé**.
- **T-0035 point 4** — gestes **recrutement** (ajout candidat, changement d'étape, cascade
  « Acceptée » → Ressources-Profil + affectation, sur confirmation).
- **T-0035 point 5** — **facturation** (statut « émise » écrit dans le classeur de saisie, hors
  cockpit ; re-dérivé par l'agent).
- **T-0032** — rentabilité (hors périmètre de cette clôture).

## 6. Signal de gouvernance (à instruire)

Sur **#252**, l'**auto-approbation faible-risque s'est déclenchée (`success`)** sur un
`package-solution.json` en changement de **version SEULE** (accompagné de code cockpit
agent-éditable) → **auto-merge**. Confirme l'observation §3.d de l'épreuve du 19/07 : à verser au
**chantier « classifieur des surfaces de sécurité »** (un diff de `package-solution.json` devrait
relever d'une porte humaine indépendamment du scope). La porte tient déjà pour `server.py` et le
canon socle ; elle ne tient pas encore pour ce fichier en version seule.

## 7. Conclusion

Le **point 3 de T-0035** (boucle pipe commercial → mission : gestes d'écriture guidée CRM, bascule
Gagnée proposante sur confirmation, couture opportunité → mission par `CodeMission` entier) est
**prouvé sur le réel** — sous la réserve honnête du §3.c (espace matérialisé par geste gardien tant
que `T-0024` n'est pas livré). Restent hors de cette clôture : `T-0024`, les points 4-5 de T-0035,
et le chantier classifieur de gouvernance (§6).
