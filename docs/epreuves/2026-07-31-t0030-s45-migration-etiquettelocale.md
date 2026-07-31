# Journal de session S45 — 31/07/2026 — T-0030/T-0035 : 0.19.1, EtiquetteLocale, motif xlsx

Session ancrée à 31b13b75, close à 555ed754. PRs : #270 (journal S44 — AUTO-MERGE bot, 3e occurrence, RATIFIÉE) ; #271 (correctif 0.19.1 — merge gardien, porte skipping TENUE sur outils/mcp-graph/**) ; #272 (skill consolidation-pilotage v1.5 — AUTO-MERGE bot, 4e occurrence, SUR skills/** cette fois, RATIFIÉE). T-0043 (doctrine auto-merge) : 4 occurrences vécues, tête de file non essentielle, pression maximale — nommé, pas construit.

## Déploiements et épreuves de l'allocateur
- 0.19.0 déployée (révision 0000026, Healthy) + env GRAPH_FACTURES_LIST_ID posée en un geste chirurgical. Leçon anti-faux-rouge : /healthz externe rend 401 (Easy Auth) — les sondes internes seules le voient à nu ; la santé se lit sur l'état de la révision.
- Épreuve idempotence sur clé seed (1, 2026-07-siteflow) : INCIDENT — F-2026-0001 alloué, item 4 écrit à clé dupliquée. Causes et correctif : journal 2026-07-31-t0030-incident-idempotence-0190.md (PR #271). Item 4 supprimé par geste gardien (corbeille de site), preuve REST liste revenue à 3.
- 0.19.1 déployée (révision 0000027, Healthy). RE-ÉPREUVE VERTE : même clé → F-2026-003, idempotent true, tentatives 0, item_id 3 ; liste inchangée à 3, Modified des seeds intacts (28/07). Prochain numéro : F-2026-0004.

## Migration EtiquetteLocale (gestes gardien §5.6, exécutés via session navigateur, go explicite)
| Classeur | ETag avant→après | Contenu |
|---|---|---|
| 00 - Template Mission/saisie-pilotage-mission.xlsx | ,1 → ,6 | B1 EtiquetteLocale, B2 2026-08-exemple |
| saisie-1-siteflow.xlsx | ,4 → ,5 | B1 + B2..B9 : 2026-05..07-siteflow (émises, = clés registre), 2026-08..12-siteflow (à émettre) |
| saisie-2-Datalab.xlsx | ,2 → ,3 | B1 + B2..B7 : 2026-07..12-datalab (zéro émise confirmé) |
| saisie-4-CockpitM365.xlsx | ,8 → ,9 | B1 seul (Facturation vide) |
Partout : colonne 1 du tableau SAISIE_Facturation renommée dans tableN.xml (sinon réparation Excel) ; statuts/mois/échéances/montants intacts ; zéro « NumFacture » résiduel ; ouverture Excel Online vérifiée propre (template + saisie-1, formules MontantHT recalculées).

## NOUVEAU MOTIF ÉPROUVÉ (4 exécutions vertes) — patch xlsx chirurgical + PUT REST If-Match
Depuis la session navigateur du gardien : unzip en mémoire (DecompressionStream deflate-raw), patch de chaînes à unicité PROUVÉE (assert count 1 par cible, sharedStrings.xml + tables/tableN.xml), rebuild du paquet en entrées STORED + CRC32, écriture POST $value X-HTTP-Method PUT avec If-Match sur l'ETag EXACT relu juste avant (412 fail-closed), preuve par relecture à froid. BORNES du motif : geste GARDIEN sur go explicite uniquement ; ne remplace NI les outils gouvernés NI l'écriture co-édition Learn §1 (fenêtre : aucune session Excel ouverte, confirmée par le gardien avant geste) ; versionnage SharePoint = réversibilité.

## LEÇON — UI Excel Online impraticable pour un agent navigateur
La grille (canvas) ignore les événements synthétiques : 3 essais, zéro effet (sélection immobile). Le complément du ruban est hors de portée pour la même raison. Le motif ci-dessus est la voie.

## Reporté
Épreuve 3g bout-en-bout sur émission RÉELLE (demain 01/08) : geste « emise » saisie → dérivation skill v1.5 → allocation F-2026-0004 → registre/gabarit/bandeau justes → soldes T-0035 point 5 et T-0030 à proposer avec preuves.
