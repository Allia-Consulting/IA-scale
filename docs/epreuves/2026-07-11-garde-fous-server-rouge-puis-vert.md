# Épreuve T-0020-e — garde-fous `server.py` (rouge-puis-vert)

Journalisation rétroactive (2026-07-11) d'une épreuve advenue le 2026-07-10. Fait nouveau ;
aucune requalification d'un soldé, aucune réécriture d'entrée existante.

But : prouver sur le réel que le check requis « Tests garde-fous server.py » bloque la
promotion quand un garde-fou fail-closed de `outils/mcp-graph/server.py` est neutralisé.

- **Rouge — PR #180** (fermée sans merge, aucun code sur `main`) : régression
  volontaire du garde-fou d'intégrité `sha256` (`if sha256_recu != sha256_attendu:` → `if False:`).
  Le check « Tests garde-fous server.py » est passé **completed / FAILURE** sur le head_sha exact
  `42a2078384b2eb5e7101a53589bafd3d8869d678` — le test `integrite_mismatch` attendait un `ValueError`
  que le garde-fou neutralisé ne levait plus (`DID NOT RAISE`). La porte `main-protection` a bloqué le
  merge ; PR fermée sans merge, branche supprimée.
- **Vert — PR #181** (mergée le 2026-07-10T10:25:25Z, merge `7f18b20c75115df8beac5f002d5222722fabfc2a`) :
  solde de la sous-tâche T-0020-e (`en_cours` → `solde`) une fois les garde-fous rétablis et éprouvés.
  La PR ne touchant pas `outils/mcp-graph/**`, le check est repassé en **skip vert** (diff-gated,
  correctif #175).

Journalisé comme fait nouveau.
