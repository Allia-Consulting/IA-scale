# outils/gabarit-pilotage

Générateur reproductible de la **souche** du gabarit de pilotage de mission,
`contrats/socle/gabarit-pilotage-mission.xlsx` (chantier **T-0033**).

Le **script est le livrable** — la souche canon n'est jamais éditée à la main. C'est la
leçon de gouvernance S35 (`docs/epreuves/2026-07-14-t-0031-consolidation-s35.md`) : l'agent
livre des artefacts finis, jamais des instructions d'édition cellule par cellule.

## Ce que le script garantit

Conforme à `contrats/socle/modele-donnees.md` **§5.2** (schéma normatif) :

- Trois tables nommées **T_Affectations**, **T_Imputations**, **T_Echeancier**, en-têtes
  repris **caractère pour caractère** (accents compris).
- **En-têtes seuls** : la plage (`ref`) de chaque table couvre exactement la ligne
  d'en-tête, **zéro ligne de corps**. Une table en-tête seul a une collection `rows` vide
  côté Graph → `workbook_lire_table` renvoie **count:0** (critère d'acceptation T-0031).
  C'est le remède au **STOP n°3** de S35 (vider une ligne à la main ≠ la supprimer :
  `count:1 ≠ 0`).
- **Aucune donnée d'illustration** : zéro `MIS-EXEMPLE`, `jane.doe`, `F-EXEMPLE`
  (la pollution assainie — **STOP n°2** de S35).
- **Statuts de référence accentués** portés par des listes de validation sur les colonnes
  de statut : « à valider » / « validé » (T_Imputations), « à émettre » / « émise » /
  « payée » (T_Echeancier).
- Mises en forme reprises de la souche existante (non polluées) : en-têtes blanc Arial gras
  sur fond `1F3864`, largeurs de colonnes, style de table `TableStyleLight1` sans bandes.

La feuille `Legende` est régénérée pour rester **conforme au canon** : nom d'instanciation
`gabarit-<CodeMission>.xlsx` (§5.2), instanciation machine (§5.6), absence de « consolidé
central » (le modèle v2 n'en a pas — les coûts vivent dans le référentiel à audience
restreinte, §5.3).

## Usage

```sh
pip install openpyxl --break-system-packages   # si absent

# Génère la souche au domicile canon PUIS l'auto-vérifie :
python3 outils/gabarit-pilotage/generer_souche.py

# Génère ailleurs :
python3 outils/gabarit-pilotage/generer_souche.py --sortie /chemin/souche.xlsx

# Vérifie seulement un fichier existant (aucune génération) :
python3 outils/gabarit-pilotage/generer_souche.py --verifier contrats/socle/gabarit-pilotage-mission.xlsx
```

## Auto-vérification (mode `--verifier`, exécuté aussi en fin de génération)

Rouvre le fichier produit et affirme programmatiquement, table par table :

- **(a)** les trois tables existent sous leurs noms exacts ;
- **(b)** la `ref` de chaque table = ligne d'en-tête seule (1 ligne) ;
- **(c)** aucune cellule non vide sous les en-têtes ;
- **(d)** les en-têtes correspondent caractère pour caractère à §5.2 (colonnes de table ET
  cellules) ;
- **(e)** les statuts accentués sont présents dans les listes de validation ;
- garde-fou anti-régression : aucune trace des données d'illustration polluantes ni des
  statuts non accentués (`a valider`, `a emettre`).

Toute assertion en échec → **code retour non nul** et message clair.

## Temps 2 (tenant — après merge, MCP délégué, hors de ce script)

Sur le site *Contrats et administratif*, racine `06 - Gabarit ERP` : archivage des
`gabarit-1.xlsx` / `gabarit-2.xlsx` pollués vers `00 - Old`
(`workbook_archiver_gabarit`), remplacement de la souche par le binaire promu, puis
ré-instanciation machine des deux gabarits (`workbook_instancier_gabarit`) et **preuve
`count:0` sur les 6 tables** (`workbook_lire_table`). Coordonnées tenant en variables
d'environnement (runbook gardien), jamais au canon.
