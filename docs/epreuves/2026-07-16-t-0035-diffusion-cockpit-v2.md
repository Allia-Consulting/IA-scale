# Épreuve T-0035 — diffusion de la Tour de contrôle v2 (bandeaux économiques en états vides, bascule hub)

Entrée d'épreuve du 2026-07-16 (session S36). Fait nouveau ; aucune requalification d'un soldé,
aucune réécriture d'entrée existante. **T-0035 reste `en_cours`** : le point 1 de l'ordre de bataille
S36 (diffusion) est soldé au sens gardien — éprouvé sur le réel — mais la lecture économique réelle
(point 2) et les gestes d'écriture guidée (points 3 à 5) restent à construire.

But : mettre la Tour de contrôle v2 sous les yeux des collaborateurs — les trois bandeaux
économiques restants construits en **états vides honnêtes** (câblage des calculs = point 2), dans
l'ordre figé de `tour-de-controle.md` v2.1 §3, et la page devenue **point d'entrée unique** du site.

## Code

**PR #222** (solution SPFx `1.2.0.0` → **`1.3.0.0`**) : couche de découverte pure `gabarits.ts` +
modèles `bandeaux-economiques.ts`, composants React `BandeauStaffing` / `BandeauRentabilite` /
`BandeauFactures` / `BandeauFraicheur`, intégration dans `TourDeControle.tsx` (ordre figé §3, 3 KPI
d'organisation conservés en bande compacte sous les cinq bandeaux), câblage cross-site sous
l'identité de l'utilisateur (`...ByServerRelativePath`) dans `listes-reelles.ts`, 3 propriétés de
coordonnées gabarits au property pane (vides par défaut = découverte non câblée). **heft : 50 tests
verts** (27 existants + 23 nouveaux), build ship sans erreur. Classée **faible risque, verdict
`pass`, non déléguée** : **auto-approuvée et mergée par `app/agent-gardien` le 2026-07-16T13:47:06Z**
(merge `f5d91ecc`) — **première promotion auto-approuvée d'une évolution du cockpit**.

## Mise en service (gestes gardien du 2026-07-16)

`.sppkg` **1.3.0.0** téléversé et déployé à l'**App Catalog**
(`https://alliaconsuling.sharepoint.com/sites/appcatalog`), en remplacement de la `1.2.0.0`.

## Épreuve sur le réel (vérification navigateur, `SitePages/Tour-de-contrôle.aspx`)

Les cinq bandeaux s'affichent dans l'**ordre figé §3** de `tour-de-controle.md` v2.1 :

1. **Staffing** — sélecteur d'année (année courante ±2), douze barres mensuelles, effectif et
   pourcentage en « · » (aucun gabarit actif lu → jamais un 0 % inventé), distinction
   réalisé / prévisionnel. Lecture seule.
2. **Pipe commercial** — inchangé, repositionné.
3. **Recrutement** — inchangé, repositionné (agrégats par étape, RGPD).
4. **Rentabilité & résultats** — tableau douze mois × (Budget | Réalisé) + Total, lignes CA total
   et EBITDA en « · », mention discrète « référentiel à audience restreinte » sur la ligne EBITDA
   (référentiel de coûts non accessible à l'utilisateur — état légitime). Lecture seule.
5. **Factures à émettre** — état vide honnête (échéanciers non ouverts au point 1). Lecture seule,
   aucun bouton « Émise » (le statut s'écrit dans le classeur de saisie, hors cockpit — v2.1).

- **Bande de fraîcheur** commune : « lu le 16/07/2026 à 15:56 ».
- **3 KPI d'organisation** en bande compacte sous les cinq bandeaux (décision gardien-copilote : le
  contrat fige l'ordre des bandeaux, il n'abroge pas les KPI).

Aucun zéro inventé, aucun vert, aucune pastille d'état ; lecture seule sur l'économique. Conforme à
`tour-de-controle.md` v2.1 (§3 hiérarchie, §4 modèle distribué, §5 SPFx).

## Bascule en page d'accueil (point d'entrée unique, §3)

Le geste UI « Promouvoir comme page d'accueil » du gardien **n'a pas persisté** le paramètre :
`GET _api/web/rootfolder` montrait `WelcomePage = SitePages/Home.aspx` inchangé. Posé par
**MERGE REST sur `_api/web/rootfolder`** sous l'identité du gardien (**HTTP 204**), vérifié après
coup : `WelcomePage = SitePages/Tour-de-contrôle.aspx`, et la racine du site atterrit désormais sur
la Tour de contrôle. Geste **réversible en une action** (re-MERGE vers `Home.aspx`).

## Reste à faire (points suivants de l'ordre de bataille — NON ouverts ici)

- **Point 2** — câblage réel des bandeaux économiques (staffing, rentabilité, factures), après
  T-0033 (souche/gabarits propres) et solde de T-0031 (chaîne économique vivante). Les 3 propriétés
  de coordonnées gabarits du property pane seront posées par le gardien à ce moment-là.
- **Point 3** — gestes CRM (écriture guidée, cascade « Gagnée »).
- **Point 4** — gestes recrutement (ajout candidat, changement d'étape, cascade « Acceptée »).
- **Point 5** — facturation (le statut « émise » reste écrit dans le classeur de saisie, hors cockpit).

Journalisé comme fait nouveau.
