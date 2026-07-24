# Épreuve T-0038 — cascade « Gagnée » → mission + espace SANS geste gardien

> **Date** : 24 juillet 2026. **Chantier** : `T-0038`. **Nature** : épreuve réelle sur le tenant.
> **Résultat** : **VERTE** — une bascule « Gagnée » produit `CodeMission` + espace de mission de bout en bout, par les seuls outils MCP Graph (crans **notifié** + **auto**), **sans aucun geste technique gardien** dans la chaîne. Solde de `T-0038` **proposé** (prononcé = geste gardien au merge).

## Ancrages (lecture seule, avant tout effet de bord)

| Ancrage | Valeur relue |
|---|---|
| HEAD du dépôt (`git rev-parse HEAD`) | `e485786cf24e68236bedc3d266bf436c8d3378cb` (attendu — conforme) |
| Image déployée (ACA `ca-allia-mcp-graph`) | `acralliamcpgraph.azurecr.io/allia-mcp-graph:0.18.0` |
| Digest de l'image | `sha256:4ac1f68b80a41cb078f65fdf52df38ad45b6d4fdb808970a232845dfd8108952` |
| Révision ACA | `ca-allia-mcp-graph--0000025` — `active: true`, `health: Healthy` |
| `SOUS_DOSSIERS_MISSION` (code déployé, `server.py:225`) | `("01 - Pilotage", "02 - Livrables")` — **2 dossiers** (le code fait foi) |

## Matière de l'épreuve (opportunité gagnée, Liste « CRM »)

- **Item Id 4** — `NomOpportunite` = « Épreuve T-0038 — cascade auto », `Etape = Gagnée`, `Montant = 1000`, `CompteLookupId = 1`, `CodeMission` **VIDE**, `Title` **vide**.
- Compte lié (`CompteLookupId = 1`, Liste « Comptes ») : `Title` = `CPT-001`, `NomCompte` = **« Arabelle Solutions »**.
- `CodeMission` existants au départ : `{2}` (item 2 / O-002 « Leader PowerBI »). **Code attendu : 3** (`max(2) + 1`).
- Préconditions fail-closed de l'allocateur **satisfaites** : `Etape = Gagnée` ∧ `CodeMission` vide.

## Déroulé (skill `cadrage-mission` v1.4 candidat — §4, entrée « Opportunité Gagnée »)

1. **Lire** l'opportunité gagnée (item 4) + référentiels (Comptes) — `list_items` (cran auto). Fait.
2. **Dialogue / porte « le brief suffit »** — décisions de **session** portées par le gardien (le prompt d'épreuve les prononce). Ce ne sont pas des gestes techniques : conforme.
3. **Allouer le `CodeMission` + fermer la couture** — `allouer_code_mission(opportunite_id="4")` (cran **notifié**, outil serveur à cible figée). Retour : `{"opportunite_id":"4","code_mission":3,"tentatives":1}`.
4. **Créer l'espace** — en bout de skill, `creer_espace_mission(annee="2026", client="Arabelle Solutions", nom_mission="Épreuve T-0038 — cascade auto", code_mission="3")` (cran **auto**). Retour : nom d'espace à 4 segments + arbre figé.

**Aucun geste gardien technique dans la chaîne** : l'ancienne étape « réécrire `CodeMission` = PROMOTION gardien » est **levée** par `T-0038` (l'allocateur atomique la porte, cran notifié). Les deux seuls effets de bord passent par des outils MCP Graph (cibles figées côté serveur) ; aucune écriture REST, UI ou `az` en écriture.

**Périmètre de l'épreuve.** Elle éprouve la **cascade que `T-0038` automatise** — les deux écritures gouvernées `allouer_code_mission` (notifié) + `creer_espace_mission` (auto), soit exactement le critère d'acceptation #1 « mission + espace SANS AUCUN GESTE GARDIEN ». Les étapes 5 (écrire le brief `BRIEF-3` en Zone-de-proposition, cran auto) et 7 (`notifier_equipe`, cran notifié) du skill n'ont **pas** été jouées : hors de la surface éprouvée ici (ni prouvée ni purgée par ce prompt), elles n'introduisent aucun geste gardien et ne conditionnent pas le critère. Le cran **notifié** de `allouer_code_mission` est matérialisé par le **journal d'observabilité** (`_journal_appel`), pas par un appel `notifier_canal` — l'outil reste « bête » (README §septies).

## Preuves relues sur le réel (anti-faux-vert)

### Preuve 1 — `CodeMission = 3` posé sur l'item 4, codes uniques
`list_items` CRM après coup :
- Item 4 : `CodeMission = "3"`, `Etape = Gagnée`, etag `…,3`, `Modified = 2026-07-24T09:46:42Z`.
- **`lastModifiedBy` = `application` `id-allia-mcp-graph`** (appId `f2a3c40a-a447-4295-90da-76d6b0898d61`), `AppEditorLookupId = 20` — l'écriture est le fait de **l'identité managée du serveur**, jamais d'un geste humain/manuel.
- Codes après épreuve : item 2 → `2`, item 4 → `3` → ensemble `{2, 3}` **unique** (aucune réattribution).

### Preuve 2 — l'espace existe au tenant, nom à 4 segments + arbre conforme
- Retour `creer_espace_mission` : `nom_espace` = **« 2026 - Arabelle Solutions - Épreuve T-0038 — cascade auto - 3 »** (4 segments) ; `sous_dossiers` = `["01 - Pilotage","02 - Livrables"]`.
- **Vérification indépendante en live** (listing Graph des enfants, hors index de recherche) :
  - Parent « 03 - Livrables de mission » (drive `b!tZYcCkb3…Ar_v`) → contient le dossier `2026 - Arabelle Solutions - Épreuve T-0038 — cascade auto - 3` (itemId `01OFZO2MT5N5ZW2SNM4RHINTFN6VJYGQ2F`).
  - Enfants de cet espace → exactement **`01 - Pilotage`** (itemId `01OFZO2MVFUGMBKVKPBZH26MEC37ZLOJ7S`) et **`02 - Livrables`** (itemId `01OFZO2MS6SRZNK2N2GZD3N4IYNO7M6TML`) — 2 dossiers, conforme à `SOUS_DOSSIERS_MISSION`.
  - `web_url` : `https://alliaconsuling.sharepoint.com/sites/AlliaConsuling/Documents%20partages/General/03%20-%20Livrables%20de%20mission/2026%20-%20Arabelle%20Solutions%20-%20%C3%89preuve%20T-0038%20%E2%80%94%20cascade%20auto%20-%203`
- *Note* : la recherche SharePoint **indexée** ne rendait pas encore l'espace (latence d'indexation, dossier créé ~1 min avant) — la vérification indépendante a donc été faite par **listing direct des enfants** (Graph children), non tributaire de l'index.

### Preuve 3 — cran notifié visible dans le journal d'observabilité
Journal `mcp-graph` (stdout du conteneur, révision `--0000025`, `az containerapp logs`) :
```json
{"journal": "mcp-graph", "ts": "2026-07-24T09:46:42.158+00:00", "outil": "allouer_code_mission", "cran": "notifie", "resultat": "succes", "duree_ms": 867}
{"journal": "mcp-graph", "ts": "2026-07-24T09:50:21.478+00:00", "outil": "creer_espace_mission", "cran": "auto", "resultat": "succes", "duree_ms": 888}
{"journal": "mcp-graph", "ts": "2026-07-24T09:50:39.072+00:00", "outil": "allouer_code_mission", "cran": "notifie", "resultat": "erreur", "duree_ms": 212, "type_erreur": "ValueError"}
```
La ligne d'allocation porte bien `"cran": "notifie"` — le gardien est informé par ce journal (matérialisation du cran, conforme à la docstring de l'outil).

### Preuve 4 — négatif : la seconde allocation ÉCHOUE (fail-closed)
`allouer_code_mission(opportunite_id="4")` rejoué après la pose → **erreur, zéro écriture** :
> `Précondition non tenue : l'opportunité « 4 » porte déjà un CodeMission (« 3 ») — jamais de réattribution (modele-donnees §2 bis). Aucun code réécrit (fail-closed).`

Journalisé `"resultat": "erreur"`, `"type_erreur": "ValueError"` (cf. Preuve 3, 3e ligne). Aucune réattribution, `CodeMission` reste `3`.

## Incident consigné (ne bloque pas l'épreuve)

- **`Title` vide sur l'item 4** : le geste cockpit « nouvelle opportunité » ne pose pas l'identifiant stable `Title` (canon : `O-NNN`) — l'item 4 a été créé sans `Title`. C'est un défaut du **geste de saisie CRM**, pas de la cascade T-0038. Renvoi à l'**hygiène CRM (point 1c)** : correctif = clic gardien hors épreuve (poser `Title = O-003`), ou correction du geste « nouvelle opportunité ».

## Purge d'hygiène (clics gardien, hors épreuve — Étape 5)

À la main du gardien, pour rendre le tenant à son état d'avant-épreuve :
1. Supprimer l'espace de mission `2026 - Arabelle Solutions - Épreuve T-0038 — cascade auto - 3` (drive « Documents partagés » → « General/03 - Livrables de mission », itemId `01OFZO2MT5N5ZW2SNM4RHINTFN6VJYGQ2F`) et ses 2 sous-dossiers.
2. Supprimer (ou remettre en jeu) l'item CRM Id 4 « Épreuve T-0038 — cascade auto ».
3. Au passage, traiter l'incident `Title` vide (point 1c) sur le geste « nouvelle opportunité ».

*(La suppression définitive de données est un geste gardien — CLAUDE.md, garde-fous ; l'agent ne l'exécute pas.)*

## Conclusion

Le critère d'acceptation #1 de `T-0038` est **prouvé sur le réel** : « une bascule Gagnée produit mission + espace SANS AUCUN GESTE GARDIEN ». L'allocation est **atomique** (If-Match/ETag, `tentatives: 1`) ; l'écriture ne vise **que** la colonne `CodeMission` de la Liste « CRM » figée ; les préconditions strictes (Gagnée ∧ vide) refusent tout rejeu (Preuve 4). Solde de `T-0038` **proposé** au gardien (prononcé au merge).
