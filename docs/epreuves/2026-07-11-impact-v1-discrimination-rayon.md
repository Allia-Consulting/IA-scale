# Épreuve T-0020-c (marche 1) — avis d'impact v1, discrimination du rayon

Journalisation rétroactive (2026-07-11) d'une épreuve advenue le 2026-07-10. Fait nouveau ;
aucune requalification d'un soldé, aucune réécriture d'entrée existante.

But : prouver sur le réel que l'avis d'impact déterministe v1 de l'agent-gardien
(`outils/agent-gardien/impact.py` + workflow `conformite.yml`) discrimine le rayon d'un
changement — un contrat socle largement consommé doit ressortir en RISQUE large, une feuille
locale en RISQUE faible.

- **PR #185** (`[ÉPREUVE — NE PAS MERGER]`, fermée sans merge — aucun code sur `main`) : l'avis
  d'impact v1, en production, a classé `contrats/socle/table-des-crans.yaml` (socle) en rayon
  **large** (≈82 consommateurs réels via le graphe inverse) et le chantier `T-0029` (feuille
  locale) en rayon **faible**. VERDICT `pass` : la discrimination du rayon est prouvée.
- Ce que l'épreuve prouve réellement : **une épreuve d'intégration du classificateur d'impact**,
  pas un cycle rouge-puis-vert de garde-fou. Elle a débloqué le solde de la marche 1
  (PR #186, merge `40c24a7`).

Journalisé comme fait nouveau.
