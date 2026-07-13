# Épreuve T-0027 — extinction du bruit /healthz (mesure avant/après sur le réel)

Entrée d'épreuve du 2026-07-13. Fait nouveau ; aucune requalification d'un soldé, aucune
réécriture d'entrée existante.

But : prouver sur le réel que la réduction du bruit de logs (PR #193) éteint les sondes /healthz
qui noyaient le journal structuré `{"journal": "mcp-graph"}`, sans altérer ni le journal ni le
comportement du connecteur.

## Cause mesurée à la source (avant correctif)

Log Analytics (espace `workspace-rgiascaleQW10`, table `ContainerAppConsoleLogs_CL`), fenêtre
24 h au 2026-07-13, révision `ca-allia-mcp-graph--0000015` (image 0.10.0) : **11 704 lignes
console**, dont **11 518 (98,4 %)** = sondes /healthz relayées par `uvicorn.access` (3 sondes
actives : Liveness 30 s, Readiness 10 s, Startup 10 s). S'y ajoutaient des dumps d'en-têtes
`azure-identity` à INFO.

Anti-faux-rouge vérifié AVANT correctif : le journal métier était **vivant mais noyé** — les
lignes `list_items` du 2026-07-13 ~17:42 ont été retrouvées dans le bruit. Le bruit masquait le
journal ; il ne l'avait pas éteint.

## Correctif

**PR #193** (mergée par `agent-gardien[bot]` à 2026-07-13T17:59:34Z — 3e preuve du circuit
d'auto-approbation du faible risque, après #189 et #190) : filtre `_FiltreSondesHealthz` posé sur
le logger `uvicorn.access` (rejette les lignes contenant /healthz, aucun autre accès filtré) +
loggers `azure.core.pipeline.policies.http_logging_policy` et `azure.identity` relevés à WARNING.
Le logger `journal_mcp` (handler dédié, `propagate=False`) reste STRICTEMENT intact. Test dédié
`test_filtre_healthz_ne_touche_pas_le_journal` ; suite **30/30 verte**.

## Mise en service

Image `allia-mcp-graph:0.10.1` (digest `sha256:d6331406ae62…`), build ACR 2026-07-13 18:02–18:03Z
depuis le canon au SHA `ef817513`. Révision `ca-allia-mcp-graph--0000016`,
**Healthy / RunningAtMaxScale**, à **100 % du trafic**. Révision `--0000015` (image 0.10.0)
conservée pour rollback en une action (repointer la révision précédente).

## Épreuve après bascule

Log Analytics, ~2026-07-13 18:15Z : sur `--0000016`, **healthz = 0** ligne (total 55 lignes console
depuis 18:03Z), et le journal émet toujours sur données réelles du tenant —
`{"journal": "mcp-graph", "ts": "2026-07-13T18:08:08.202+00:00", "outil": "list_items",
"cran": "auto", "resultat": "succes", "duree_ms": 3060}`.

Le bruit /healthz est éteint, le journal métier ressort intact. T-0027 soldé.

Journalisé comme fait nouveau.
