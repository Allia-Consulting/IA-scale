# Épreuve T-0033 (jumelée) — `workbook_archiver_gabarit` : copie → DÉPLACEMENT (serveur 0.15.0)

Entrée d'épreuve du 2026-07-17 (soir). Fait nouveau ; aucune requalification d'un soldé, aucune
réécriture d'entrée existante. Entrée **jumelée** à `docs/epreuves/2026-07-17-t-0035-reprise-4-reconciliation-skill.md`
(récit complet et vérification de banc là-bas) : elle est dupliquée ici parce que la correction touche
une **primitive de la famille fabrication/archivage** dont `T-0033` porte l'histoire. Historique
immuable — cette entrée s'ajoute, elle n'efface rien.

## Contexte

`T-0033` a rendu la **fabrication** d'un gabarit neuf ouvrable à froid (serveur 0.13.0 → 0.14.0, preuve
FROIDE §8, PR #235). Restait le cas **régénération d'un gabarit existant** : l'épreuve tenant du soir a
montré qu'elle **butait sur une collision non levable** — `workbook_instancier_gabarit` est fail-closed
sur un gabarit en place (correct, **inchangé**), et `workbook_archiver_gabarit` ne faisait que **COPIER**
(l'original restait à la racine, le nom `gabarit-<code>.xlsx` **jamais libéré**).

## Correction (serveur 0.14.0 → 0.15.0)

`workbook_archiver_gabarit` passe de la **copie asynchrone** (`POST /copy`, 202 + `Location`) au
**DÉPLACEMENT synchrone** (`PATCH` de l'item : `parentReference` « 00 - Old » figé + nom horodaté,
`200`). Le nom source est **libéré au retour** → la ré-instanciation fail-closed se satisfait **sans
collision ni écrasement, sans affaiblissement**. La primitive **reste BÊTE et BORNÉE** (décision S34) :
source/destination résolues côté serveur, l'appelant ne fournit que `code_mission` ; ce **n'est pas** une
surface de déplacement/suppression générique. **Réversible** (version conservée dans « 00 - Old » ;
rétablissement inverse = geste gardien). L'orchestration de régénération (archiver → ré-instancier →
repeupler) vit dans le **skill** `consolidation-pilotage`, pas dans le serveur.

## État tenant laissé par l'épreuve du soir (fait, réversible)

L'agent d'épreuve a archivé **deux gabarits** — `gabarit-1-20260717T13xxxxZ.xlsx` et
`gabarit-2-20260717T13xxxxZ.xlsx` — dans « 00 - Old ». Comme l'archivage **copiait** à ce moment, ce sont
des **copies** : les originaux `gabarit-1.xlsx` / `gabarit-2.xlsx` (Siteflow / Datalab) **restent actifs
à la racine** « 06 - Gabarit ERP ». Aucune perte, aucun écrasement — deux copies surnuméraires
horodatées, **état réversible** (ménage optionnel côté gardien).

## Vérification & reste

- **Banc rouge→vert, 73 tests `pytest` verts** (+3 tests d'archivage-déplacement), fail-closed d'instanciation
  et bornage **inchangés et verts** ; evals `consolidation-pilotage` 10/10 (détails dans l'entrée T-0035 jumelée).
- **Reste gardien** : build+déploiement 0.15.0, promotion du skill v1.3, épreuve tenant (régénérer un
  gabarit **existant**), puis lecture froide en Graph délégué. **Requalification éventuelle du solde
  « au sens gardien » de `T-0033`** (fondé sur des preuves de fabrication) : appartient au gardien.
- L'agent n'a **rien mergé, rien déployé, rien touché au tenant**.
