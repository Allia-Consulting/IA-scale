# Épreuve S39 (T-0035 point 2 — cockpit câblé Graph Workbook) — VERTE : régénération + lecture froide + rejeu cockpit

Entrée d'épreuve du 2026-07-19 (session S39). Fait nouveau ; aucune requalification d'un soldé
au-delà de ce qui est prouvé ici, aucune réécriture d'entrée existante. **VERDICT : VERT.** Le
câblage économique du cockpit (bandeaux Staffing / Rentabilité / Factures à émettre) lit désormais
des gabarits réels via l'API Graph Workbook et affiche des agrégats justes — après un rejeu d'abord
**ROUGE** dont la cause racine a été rectifiée (voir §3.a).

## 1. Chronologie (faits)

1. **Déploiement image serveur 0.16.0** (geste gardien) — Container App `ca-allia-mcp-graph`,
   **révision ACA `--0000023`, état Healthy**. Contient le prédicat « vierge » recalibré + le
   rollback vérifié de `workbook_instancier_gabarit` (T-0035 reprise n°5).
2. **Épreuve de régénération** (agent, matin du 19/07), séquence normative du skill
   `consolidation-pilotage` v1.4, deux missions dans l'ordre :
   - **M1 — gabarit-1 / Siteflow (code 1)** : (1) `workbook_archiver_gabarit(1)` → DÉPLACEMENT du
     gabarit-1.xlsx **défectueux** (item `01BWFCBZHMHXN46WR2EFDJQFBLFKT7NXNP`) vers « 00 - Old »
     sous `gabarit-1-20260719T112151Z.xlsx` (`deplace:true`, nom libéré) ; (2)
     `workbook_instancier_gabarit(1)` → nouveau `gabarit-1.xlsx` (item
     `01BWFCBZHH7KJ2MPLVIJAK6LIV76UPMHEL`), preuve froide vierge 3 × `lignes_vides:1` (ligne
     d'insertion Excel tolérée) ; (3) `workbook_ajouter_lignes` ×3 → 8 / 2 / 8 ; (4) contrôle
     post-écriture (relecture 3 tables) → **148 j / 133 200 €**.
   - **M2 — gabarit-2 / Datalab (code 2)** : archivage du gabarit-2 intact (item
     `01BWFCBZATQHKNZ6BWHRBJF6E52CL2OBF4`) → `gabarit-2-20260719T112706Z.xlsx` ; ré-instanciation
     (item `01BWFCBZHFTVTA2XI7HJDK5AOTY4VAHZVB`, 3 × `lignes_vides:1`) ; repeuplement 6 / (0 sauté,
     aucun réalisé) / 6 ; contrôle → **120 j / 84 000 €**.
   - **Fin d'épreuve : 19/07 à 13:28 locale (11:28 UTC).** Zéro retouche manuelle, rollback non
     mobilisé (aucune preuve froide rouge).
3. **Refroidissement** ~10-15 min (binaires laissés au repos, aucune session Workbook chaude).
4. **Lecture froide différée** (session ultérieure, juge du solde) : lecture des **6 tables** des
   deux gabarits **à froid** (Graph délégué, `/columns` **sans** session Workbook — le chemin exact
   du cockpit), en-têtes **§5.2 conformes**, agrégats **148 j / 133 200 €** (M1) et
   **120 j / 84 000 €** (M2). **6/6 VERT** — les binaires au repos sont bien ouvrables à froid.
5. **Rejeu cockpit — ROUGE** : les **8 appels** `/workbook/tables/…/columns` (3 tables × 2 gabarits
   + 2 classeurs du référentiel) rendent **403 « Could not obtain a WAC access token »**, alors que
   la résolution `/sites` (200), `/drives` (200) et le listing du dossier (200) passent. Jeton
   délégué SPFx.
6. **Diagnostic** : l'échec est **l'échange WAC sur la forme d'adressage PAR CHEMIN**
   (`/drives/{id}/root:{chemin}:/workbook/…`). Contre-épreuve décisive : **même jeton, même
   fichier**, l'adressage **par item id** (`/drives/{id}/items/{id}/workbook/…`) → **200**. Les
   binaires 0.16.0 sont **hors de cause** (lus à froid côté serveur ET par item id côté page).
7. **Correctifs** (deux PR, porte gardien) :
   - **PR #238** — `package-solution.json` : ajout du scope délégué **`Files.ReadWrite.All`**
     (requis **même en lecture** par l'API Workbook), bump 1.4.2.0 → 1.4.3.0.
   - **PR #239** — `workbook-graph.ts` : **adressage par item id** (étape de résolution d'id par
     chemin ajoutée à la chaîne site→drive, puis lecture `items/{id}/workbook/…`) + filtre de la
     ligne d'insertion vide ; bump 1.4.3.0 → **1.4.4.0 déployée**.
8. **Rejeu cockpit — VERT, 19/07 à 16:28** : les **8 appels Workbook** passent **200** ; les
   bandeaux **Staffing / Rentabilité / Factures à émettre** affichent des valeurs **justes sur
   données réelles**.

## 2. Les trois preuves du solde (point 2)

| Preuve | Résultat |
|---|---|
| Régénération réconciliée M1 + M2 (séquence skill, contrôle post-écriture) | **VERT** — 148 j / 133 200 € ; 120 j / 84 000 € ; fin 19/07 13:28 locale |
| Lecture froide différée (binaires au repos, Graph délégué sans session) | **VERT** — 6/6 tables, en-têtes §5.2, mêmes agrégats |
| Rejeu cockpit sur le réel | **VERT** — 19/07 16:28, 8 appels Workbook 200, bandeaux justes |

## 3. Quatre consignations

### 3.a — RECTIFICATION du diagnostic S38 (403 Workbook)

Le diagnostic S38 attribuant les 403 à des **« binaires xlsx non normalisés / non ouvrables à
froid »** est **rectifié**. La cause mesurée en S39 est **l'échec WAC de l'adressage Workbook PAR
CHEMIN** (`root:{chemin}:`), **non** un défaut de binaire : à jeton égal et fichier égal,
l'adressage **par item id** rend 200 là où la forme chemin rend 403. Les binaires de fabrication
service (0.14.0+) sont **ouvrables à froid** — la lecture froide différée de cette épreuve (6/6) le
prouve indépendamment.

### 3.b — LEÇON DURABLE : contrat d'accès de l'API Graph Workbook

- **Adressage par ITEM ID obligatoire** pour tout appel `/workbook/…` : la forme chemin
  `root:{chemin}:/workbook/…` échoue à l'échange WAC. Le **chemin ne sert qu'à résoudre l'id**
  (`GET /drives/{driveId}/root:{chemin}` → métadonnées → `id`).
- **Scope délégué `Files.ReadWrite` requis MÊME EN LECTURE** : il n'existe **aucune** variante
  lecture seule pour `/workbook` ; sur un drive de site, la variante `.All` s'impose
  (`Files.ReadWrite.All`).
- **`Workbook-Session-Id` optionnel** : la **lecture sans session** est documentée et fonctionne
  (c'est le chemin du cockpit).
- **Références** : Microsoft Learn `table: List columns` / `table: List rows` ; Q&A Microsoft
  **1190965 / 1191649**.

### 3.c — CHANTIER À OUVRIR (non traité ici) : bug d'honnêteté du cockpit

À l'état actuel du module `workbook-graph.ts`, un **403 sur un gabarit ACTIF** est rendu en **état
vide SANS anomalie affichée** (branche `403/404 → 'restreint'`, silencieuse). C'est **contraire au
contrat** « une donnée manquante est *signalée*, jamais silencieusement remplacée par un zéro » :
le 403-légitime-silencieux ne doit valoir **que** pour le **référentiel de coûts restreint**, pas
pour un gabarit de mission actif dont l'illisibilité est une **anomalie**. À instruire dans un
chantier dédié (distinguer, côté cockpit, le 403 attendu du référentiel du 403 anormal d'un gabarit
actif). **Non traité dans cette clôture.**

### 3.d — GOUVERNANCE : auto-merge sur des surfaces de sécurité

Observation à instruire : l'**agent-gardien a auto-mergé** les PR **#236 (S38)**, **#238** et
**#239** ; or **#238 modifiait `webApiPermissionRequests`** — une **surface de sécurité** (octroi
de scope délégué tenant-wide sur le principal d'extensibilité partagé). La **porte humaine a en
revanche été correctement tenue** sur **#240** (promotion de contrats socle + skill). **Chantier
classifieur à instruire** (non traité ici) : les **surfaces de sécurité** — `outils/mcp-graph/server.py`,
`webApiPermissionRequests`, workflows CI — doivent relever d'une **porte humaine systématique**,
jamais de l'auto-approbation faible-risque.

## 4. Conclusion

Le **point 2 de T-0035** (cockpit câblé Graph Workbook, lecture économique sur données réelles) est
**prouvé sur le réel** par les trois preuves du §2. T-0033 est **requalifié** (fabrication service
0.16.0 déployée, souches instanciées et éprouvées à froid). Restent, hors de cette clôture : les
points 3-5 de T-0035 (gestes d'écriture guidée), le chantier d'honnêteté du cockpit (§3.c) et le
chantier classifieur de gouvernance (§3.d).
