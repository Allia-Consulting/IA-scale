# Épreuve T-0031 — première consolidation réelle (session S35, 3 STOP avant écriture)

Entrée d'épreuve du 2026-07-14. Fait nouveau ; aucune requalification d'un soldé, aucune
réécriture d'entrée existante. **T-0031 reste `en_cours`** : l'épreuve ne s'est PAS soldée cette
session — trois arrêts successifs, aucun n'ayant écrit quoi que ce soit dans un gabarit.

But : prouver sur le réel la boucle de consolidation du skill `consolidation-pilotage` (saisie →
gabarit de mission) via les primitives Workbook du MCP Graph, sur les missions Siteflow (code 1) et
Datalab (code 2).

## Les trois STOP (garde-fous vivants, zéro écriture)

1. **403 sur les saisies via MCP — ARCHITECTURAL, conforme au SKILL §2.** La lecture des classeurs
   `saisie-*.xlsx` par `workbook_lire_table` renvoie `403 Forbidden` au niveau du drive/item (et non
   `404` : ce n'est pas un problème de nom de table). Les saisies vivent sur le site
   **Management-et-Gestion**, hors périmètre `Sites.Selected` de l'identité managée du serveur — **à
   dessein**. Le SKILL §2 prévoit précisément la lecture des saisies par **surface déléguée**
   (l'agent humain / le copilote), pas par l'identité managée du connecteur, réservée à l'écriture
   bornée des gabarits (Contrats-et-administratif). Le 403 confirme l'architecture, il ne la contredit
   pas.

2. **Souche canon `gabarit-pilotage-mission.xlsx` NON vierge.** La relecture des gabarits fraîchement
   instanciés a révélé, dans **chacune des 3 tables**, une ligne d'illustration héritée de la souche :
   `MIS-EXEMPLE` / `jane.doe@allia-consulting.com` / `F-EXEMPLE-001` (avec statuts **non accentués** :
   `a valider`, `a emettre`). `workbook_instancier_gabarit` l'avait fidèlement recopiée dans
   `gabarit-1` et `gabarit-2` (création pure — la primitive a fait exactement son travail). Écrire
   par-dessus aurait faussé tous les invariants (sommes et comptes de lignes) : STOP.

3. **Lignes de tableau VIDES résiduelles après retrait manuel.** Après retrait des lignes d'exemple
   par le gardien, la relecture renvoie `count:1` avec **cellules toutes vides** — et non `count:0`.
   Vider le *contenu* d'une ligne de tableau Excel n'est pas **supprimer la ligne** ; une table nommée
   conserve au moins une ligne de corps. Appendre par-dessus aurait produit `9/3/9` et `7/1/7` au lieu
   des `8/2/8` et `6/0/6` attendus : STOP. (Le vidage réel des lignes de corps est porté par T-0033.)

## Acquis consignés

- **Chaîne d'exécution validée de bout en bout.** Pré-autorisation Azure CLI sur le scope
  `access_as_user`, jeton **délégué** (validité 1 h), Claude Code invoque les **5 primitives** MCP
  (`workbook_lire_table` / `workbook_instancier_gabarit` / `workbook_ajouter_lignes` /
  `workbook_maj_ligne` / `workbook_archiver_gabarit`). Les garde-fous ont **stoppé correctement trois
  fois, AVANT toute écriture** : la porte tient sous conditions réelles.
- **Transformation des saisies validée par lecture déléguée** (chaque facture = jours × TJM) :
  - **Mission 1 — Siteflow, 148 j, TJM 900 €.** Prévu : mai 17, juin 22, juil 23, août 7, sep 22,
    oct 22, nov 21, déc 14. Réalisé : mai 17 + juin 22. Échéancier `F-2026-001`→`008` =
    **133 200 € HT** (001 et 002 émises, le reste à émettre).
  - **Mission 2 — Datalab, 120 j, TJM 700 €.** Prévu : juil 23, août 15, sep 22, oct 22, nov 21,
    déc 17. Aucun réalisé. Échéancier `F-2026-003`→`008` = **84 000 € HT**.

## Faits annexes

- **Anomalie `CodeMission=1` dans `saisie-2-Datalab`** détectée en séance ; corrigée par le gardien ;
  **correction vérifiée le 14/07 au soir par relecture déléguée** (`CodeMission=2` sur les deux
  onglets).
- **Doublons de `NumFacture`** `F-2026-003`→`008` **entre les deux missions** : transitoires, pré-T-0030
  (numérotation machine à venir) — signalés, jamais renumérotés par l'agent.
- **Statuts de saisie `a emmettre`** à normaliser en **`à émettre`** à la consolidation (accentuation).

## Leçon de gouvernance (arbitrage gardien du 14/07/2026)

Une épreuve qui exige des **retouches manuelles répétées** du gardien **NE PASSE PAS**. Règle retenue,
non négociable : **STOP au premier incident, reprise documentée** ; l'agent **livre des artefacts
finis** (par exemple des classeurs régénérés par script), **jamais des instructions d'édition cellule
par cellule**. C'est le fondement du chantier T-0033 (souche et gabarits régénérés par script, zéro
geste manuel du gardien hors merge).

Journalisé comme fait nouveau.
