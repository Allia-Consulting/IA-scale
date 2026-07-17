# Épreuve T-0033 (instanciation v2 API-native, tenant) — VERTE : `count:0 × 6`, chaîne 100 % service

Entrée d'épreuve du 2026-07-17 (session S37). Fait nouveau ; aucune requalification d'un soldé, aucune
réécriture d'entrée existante. **VERDICT : VERT.** L'instanciation v2 API-native (serveur 0.13.0) a
fabriqué les deux gabarits actifs entièrement par le service Excel et prouvé `count:0` de façon
indépendante sur les 6 tables. **T-0033 est soldé au sens gardien** (éprouvé sur le réel). Le risque
assumé — ouverture Workbook d'un classeur 0 octet — est **levé sur ce tenant**. Zéro geste manuel du
gardien cette session.

## 1. Garde-fou SHA (vert)

- `git fetch origin` ; `origin/main` = `bd5258e4ab3a4157842bb1f2a55455d3aff5da08` (merge PR #229).
- Branche d'épreuve pré-existante `t-0033/epreuve-instanciation-v2` (zéro commit propre au-dessus du
  merge), non recréée.

## 2. Contexte serveur et coordonnées (vérifiés, aucune écriture)

- **Serveur MCP allia-graph 0.13.0** déployé (révision `ca-allia-mcp-graph--0000020`, digest image
  `sha256:14069168ce68…`), branché au projet CLI IA-scale en **jeton délégué frais** ; sonde
  `initialize` 200 (vérifiée par le gardien avant la session).
- **Preuve de vie MCP (étape 0)** : les 5 primitives `workbook_*` visibles côté CLI
  (`workbook_instancier_gabarit`, `workbook_lire_table`, `workbook_ajouter_lignes`,
  `workbook_maj_ligne`, `workbook_archiver_gabarit`).
- **Coordonnées (journal 16/07 qui fait foi)** : drive « Documents partages » du site
  Contrats-et-administratif `b!44CicXj16kaqbdbelsTnPUundQ8Qe5JKmBk7kAxljRO8Hx-KrTj1QJbs4Mp6eHK7` ;
  « 06 - Gabarit ERP » `01BWFCBZHUYHKQWWD2IZDLEAVEXO4PVCFS`, relu **vide** au soir du 16/07 ; 4 archives
  en « 00 - Old ». Le garde-fou de collision **est la primitive elle-même**
  (`@microsoft.graph.conflictBehavior=fail`) : un `FileExistsError` aurait signalé un état inattendu → STOP.

## 3. INCIDENT PRÉALABLE — deux essais avortés à l'étape 0 (preuve de vie MCP), zéro effet tenant

Avant cette session verte, **deux tentatives** de lancer l'épreuve se sont arrêtées **à l'étape 0** : les
primitives `allia-graph` n'apparaissaient pas dans la session. Conformément à la règle (STOP si les outils
ne sont pas visibles rapidement), les deux essais ont été **arrêtés sans rien tenter d'autre**.

**Cause établie APRÈS isolation** : les deux sessions tournaient dans **Claude Desktop**, qui ne charge
**PAS** la configuration MCP locale projet du CLI (`.claude.json`, projet IA-scale). Le jeton délégué et
le serveur étaient **hors de cause** — la sonde `initialize` répondait 200. **Zéro effet tenant** dans les
deux cas (aucune primitive appelée, que l'absence d'outils).

**Leçon durable** : le branchement `claude mcp add` au niveau projet ne vaut que pour une session `claude`
**lancée au Terminal depuis le dossier du dépôt** ; Claude Desktop est un autre client, avec sa propre
config, aveugle au serveur ajouté au projet CLI.

## 4. Étape 1 — instanciation v2 ×2 (les seules écritures de l'épreuve)

`workbook_instancier_gabarit` (fabrication 100 % service : PUT vide fail-closed → session Workbook →
feuilles → en-têtes §5.2 par PATCH range → `tables/add` hasHeaders → renommage `T_*` → preuve interne
`/rows` count:0 ×3 → closeSession). Écriture bornée au dossier figé côté serveur ; l'appelant ne fournit
que `code_mission`. **Retours bruts** :

```
workbook_instancier_gabarit(code_mission="1")   # Siteflow
→ {"code_mission":"1","nom_gabarit":"gabarit-1.xlsx",
   "item_id":"01BWFCBZFLKYKV5TRV4JGJYMFBDGAZUTQA",
   "tables":{"T_Affectations":0,"T_Imputations":0,"T_Echeancier":0}}

workbook_instancier_gabarit(code_mission="2")   # Datalab
→ {"code_mission":"2","nom_gabarit":"gabarit-2.xlsx",
   "item_id":"01BWFCBZATQHKNZ6BWHRBJF6E52CL2OBF4",
   "tables":{"T_Affectations":0,"T_Imputations":0,"T_Echeancier":0}}
```

Aucun `FileExistsError` (noms `gabarit-1/2` libres, état tenant conforme). Aucune erreur d'ouverture du
classeur (400/501 sur session, feuilles ou `tables/add`) : le **classeur 0 octet a bien été ouvert et
meublé par le service Excel** — le risque assumé de la reprise v2 est levé. **Preuve interne** `count:0 ×3`
portée par chacun des deux retours.

## 5. Étape 2 — preuve INDÉPENDANTE `count:0 × 6` (lecture seule)

`workbook_lire_table` (lecture non bornée, `drive_id`/`item_id` fournis) sur les 3 tables de chacun des
deux gabarits fraîchement instanciés :

| # | gabarit | item_id | table | count |
|---|---|---|---|---|
| 1 | gabarit-1 (Siteflow) | `01BWFCBZFLKYKV5TRV4JGJYMFBDGAZUTQA` | T_Affectations | **0** |
| 2 | gabarit-1 (Siteflow) | `01BWFCBZFLKYKV5TRV4JGJYMFBDGAZUTQA` | T_Imputations  | **0** |
| 3 | gabarit-1 (Siteflow) | `01BWFCBZFLKYKV5TRV4JGJYMFBDGAZUTQA` | T_Echeancier   | **0** |
| 4 | gabarit-2 (Datalab)  | `01BWFCBZATQHKNZ6BWHRBJF6E52CL2OBF4` | T_Affectations | **0** |
| 5 | gabarit-2 (Datalab)  | `01BWFCBZATQHKNZ6BWHRBJF6E52CL2OBF4` | T_Imputations  | **0** |
| 6 | gabarit-2 (Datalab)  | `01BWFCBZATQHKNZ6BWHRBJF6E52CL2OBF4` | T_Echeancier   | **0** |

Chaque appel a renvoyé `{"lignes":[],"count":0}`. **6/6 verts.** À la différence des gabarits openpyxl de
S35 (illisibles, 501) et des tables « ligne de corps vide » (`count:1`, STOP n°3 S35), ces tables sont
**vides ET valides au sens de l'API Workbook** parce que **fabriquées par le service** (`tables/add`).

## 6. Conclusion

Les **critères d'acceptation de T-0033 sont satisfaits sur le réel** :

- `workbook_lire_table` renvoie `count:0` sur les **6 tables** des deux gabarits ré-instanciés (§5) ;
- **chaîne service-authored de bout en bout** : aucun binaire produit hors service Excel n'entre dans la
  fabrication ; chaque instanciation porte sa **preuve interne** `count:0 ×3` (§4) ;
- **zéro geste manuel du gardien** : la génération et la ré-instanciation sont machine ; le seul geste
  gardien attendu est le merge de la PR.

Le **risque assumé** (ouverture Workbook d'un classeur 0 octet) est **levé** sur ce tenant : le service a
ouvert et meublé la base vide. Le fallback pré-décidé v2B (`base-vierge-service.xlsx` + bascule `/copy`)
**n'a pas eu à être mobilisé**. Ce solde **débloque le solde de T-0031** (consolidation réelle).

**Purge post-épreuve (geste gardien)** : `claude mcp remove allia-graph` (retire le branchement délégué du
projet CLI une fois l'épreuve close).
