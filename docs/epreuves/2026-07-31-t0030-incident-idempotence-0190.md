# Incident T-0030 — 31/07/2026 — allocateur NumFacture 0.19.0 : scan de registre aveugle (idempotence & séquence)

Rattachement : T-0030 (allocateur `allouer_num_facture`), T-0035 (facturation, point 5). Épreuve post-déploiement de l'image 0.19.0, SANS risque (registre « Factures » de test, clé connue). STOP au premier incident respecté : un seul appel, aucune réparation en douce, journalisation avant correctif.

## 1. Contexte de l'épreuve

Image déployée 0.19.0 (digest `sha256:58fc9116…`, révision `--0000026`), `GRAPH_FACTURES_LIST_ID` posée. Premier appel réel de `allouer_num_facture` avec une clé DÉJÀ présente au registre — `(CodeMission=1, EtiquetteLocale="2026-07-siteflow")`, correspondant au seed réel F-2026-003 — pour vérifier l'idempotence (une re-ingestion ne réalloue jamais).

## 2. Symptôme : JSON brut rendu

L'appel a rendu :

```json
{"num_facture": "F-2026-0001", "item_id": "4", "idempotent": false, "tentatives": 1}
```

Attendu : `{"num_facture": "F-2026-003", "item_id": "<id du seed>", "idempotent": true, "tentatives": 0}`.

## 3. État persisté, contre-vérifié au tenant

L'appel n'a pas seulement mal répondu : il a ÉCRIT. Un item 4 a été créé dans le registre « Factures », Title `F-2026-0001`, clé `(CodeMission=1, EtiquetteLocale="2026-07-siteflow")` DUPLIQUÉE avec le seed F-2026-003, `Statut = "émise"` et `DateEmission = 2026-07-31` posés côté serveur. Doublon légal de clé + numéro fantôme (0001) alors que la séquence réelle était à 003.

## 4. Les deux causes racines (lues au code)

1. **Séquence aveugle aux seeds.** `_RE_NUM_FACTURE = ^F-(\d{4})-(\d{4})$` exigeait NNNN sur EXACTEMENT 4 chiffres. Les seeds réels du registre sont les numéros des PDF déjà émis — F-2026-001..003, sur 3 chiffres. Ils ne matchaient pas le motif → `_num_facture_en_couple` rendait None → ils étaient exclus du calcul du max → `max(...) default=0` + 1 = **0001**, séquence repartie à zéro.

2. **Idempotence aveugle au double Graph.** `CodeMission` est une colonne SharePoint de type Number ; Graph la sérialise en DOUBLE (`1` rendu `1.0`). `_code_mission_en_entier` faisait `str(brut).strip().isdigit()` → `"1.0".isdigit()` est False → None. Résultat : le `code_mission` de CHAQUE descripteur du registre valait None, la clé `(code_mission, etiquette)` ne pouvait jamais égaler `(1, "2026-07-siteflow")` → l'idempotence ne matchait jamais, et la post-vérification anti-course (qui compare la même clé) était aveugle à l'identique → l'écriture du doublon n'a pas été rattrapée.

## 5. Pourquoi les 18 tests étaient verts — les angles morts

Aucun test existant n'exerçait ces deux formes réelles :

- Tous les mocks du registre passaient `CodeMission` en `int`/`str` d'entier (`"5"`, `"2"`) — jamais le double intégral (`1.0`) que Graph sert pour une colonne Number. Le chemin `isdigit` marchait donc toujours en test.
- Tous les Titles de seed des mocks étaient sur 4 chiffres (`F-2026-0001`, `F-2026-0003`) — jamais les 3 chiffres des factures réellement émises. La regex 4-exact n'a donc jamais rejeté un item censé compter.

Deux fidélités manquantes au réel (sérialisation Graph, forme des seeds), pas un défaut de logique de course : les 18 tests prouvaient la mécanique, pas les entrées du terrain.

## 6. Arbitrages gardien du 31/07

- **Item 4 supprimé par geste gardien** (hors de cette PR : l'outil n'a aucune primitive de suppression, proscrite).
- **Lecture permissive `\d{3,4}`** : les seeds réels sur 3 chiffres comptent dans la séquence ; **écriture inchangée sur 4 chiffres** (`:04d`).
- **Parse `CodeMission` tolérant au double Graph** (double intégral → entier ; `1.5` rejeté). Fonction partagée avec `allouer_code_mission` : élargissement rétrocompatible (chemin `isdigit` inchangé).
- **Contrat `modele-donnees.md` §2 bis INCHANGÉ** : le NumFacture fait toujours foi sous forme `F-AAAA-NNNN` ; seule la LECTURE de l'existant est assouplie.

## 7. Correctif 0.19.1 + re-épreuve à suivre

Correctif porté en 0.19.1 (cette PR) : regex de lecture `\d{3,4}`, `_code_mission_en_entier` tolérant le double intégral, docstrings adaptées, 11 tests de régression ajoutés (double Graph paramétré, idempotence seed 3 chiffres + CodeMission double, séquence seeds 3 chiffres → 0004, séquence mixte 3/4 chiffres → 0006). Suite complète verte. Reste, porte gardien : merger (chemin sensible `outils/mcp-graph/**`), déployer l'image 0.19.1, puis REJOUER l'épreuve d'idempotence sur la même clé (attendu : `idempotent: true`, aucun POST) une fois l'item 4 fantôme supprimé.
