# Épreuve T-0035 (reprise) — le câblage Graph n'émettait aucun appel

Entrée d'épreuve du 2026-07-17. Fait nouveau ; aucune requalification d'un soldé, aucune réécriture
d'entrée existante. **T-0035 reste `en_cours`** : le point 2 (câblage économique réel) est repris à
la suite d'une épreuve du réel **ÉCHOUÉE**. Historique immutable — cette entrée s'ajoute au journal,
elle n'efface rien.

## Faits observés — l'épreuve du réel (17/07/2026) a échoué

Contexte du tir : page cockpit publiée v2.0, solution `1.4.0.0` déployée à l'App Catalog, permission
Graph **Sites.Read.All** approuvée org-wide (API access), et **4 propriétés posées et vérifiées
byte-exactes dans `CanvasContent1`** (`gabaritsSiteUrl`, `gabaritsFolderPath`,
`referentielRessourcesPath`, `referentielStructurePath`) — page **publiée par API** après gel de
l'UI SharePoint.

Symptômes constatés au navigateur :

- **Fraîcheur vivante** : « lu le 17/07/2026 à 12:58 » — le composant se monte et rend.
- **« 8 gabarits en anomalie »** : `gabarit-1.xlsx` ×3, `gabarit-2.xlsx` ×3, référentiel
  `T_Ressources`, référentiel `T_Structure`.
- **Capture réseau exhaustive** : **AUCUNE** requête vers `graph.microsoft.com`, **AUCUNE** vers le
  site *Contrats et administratif*, **AUCUNE** acquisition de jeton. **L'échec précède tout HTTP.**
- **Console** : **rien**. L'anomalie n'exposait pas sa cause.

## Diagnostic — un échec MUET, et un câblage jamais testé

Lecture du chemin réel d'exécution (`TourDeControleWebPart.ts` → `ITourDeControleProps.ts` →
`TourDeControle.tsx` → `listes-reelles.ts` → `workbook-graph.ts`) et **reproduction empirique** au
banc (montage React réel + Graph mocké, seam `chargerCockpit`) :

1. **Le câblage, quand les props atteignent le composant, émet BIEN l'appel.** Le montage réel du
   composant avec des props câblées et un Graph mocké invoque `msGraphClientFactory.getClient('3')`
   **et** la lecture des tables (`workbook/tables/…/columns`), et charge des modèles non vides. Le
   passage de la fabrique au composant est par ailleurs **garanti par le typage** :
   `msGraphClientFactory` est un champ REQUIS de `ITourDeControleProps` — l'omettre casserait la
   compilation. La piste « factory non passée au composant » est donc exclue.

2. **La cause racine de l'ÉCHEC DE L'ÉPREUVE est l'absence totale de signal.** Tous les chemins de
   saut / d'échec de la lecture de contenu étaient **muets** :
   - `chargerGabarits` retournait la découverte seule **en silence** lorsque le client Graph était
     absent, et un `catch {}` autour de `getClient('3')` **avalait** l'erreur (« son échec avalé ») ;
   - `formaterFraicheur` n'affichait que la **source** de chaque anomalie, **jamais sa raison** ;
   - aucun `console.error` n'était émis.

   Résultat sur le réel : la lecture ne partait pas (aucun HTTP, aucun jeton), et le cockpit
   n'offrait **aucun moyen de savoir pourquoi** — ni anomalie explicite, ni console. Un échec en
   amont de tout HTTP (découverte non aboutie / fabrique ou jeton indisponible / client non résolu)
   restait rigoureusement indiagnosticable.

3. **Le trou des 81 tests verts** : tous étaient PURS (normalisations, parsing, calculs). **Aucun**
   n'exerçait le câblage ni le montage — l'épreuve du réel pouvait échouer sans qu'aucun test ne
   rougisse.

## Correction (PR de reprise, solution SPFx `1.4.0.0` → `1.4.1.0`)

- **Jamais d'échec muet** (`workbook-graph.ts`, `gabarits.ts`, `listes-reelles.ts`) : chaque
  `AnomalieGabarit` porte désormais un champ **`cause`** (message technique court : statut HTTP,
  message d'exception, drapeau de câblage), **affiché** dans la ligne d'anomalies du cockpit
  (`formaterFraicheur` → `source (cause)`).
- **`chargerGabarits` ne saute/n'échoue plus en silence** : fabrique Graph absente, `getClient('3')`
  en échec, découverte indisponible — chaque cas **surface une anomalie portant sa cause** et émet un
  **`console.error('[tour-de-controle]', …)`**. L'adaptateur Graph journalise chaque `GET` en échec
  avec son statut (un `status 0` = échec **avant** réponse HTTP : jeton refusé / réseau / client non
  résolu — exactement le symptôme du 17/07).
- **Test de câblage** (`cablage-graph.test.tsx`, comble le trou) : montage du VRAI composant React,
  props câblées, Graph mocké → **asserte que la lecture EST invoquée** (`getClient('3')` + `GET`
  workbook tables) et que les modèles ne sont pas vides ; un second cas asserte qu'un client Graph en
  échec **surface l'anomalie avec sa cause + `console.error`** (jamais muet). Ce test aurait rougi
  sur le défaut.

## Vérification (banc)

- **heft : 83 tests verts** (81 d'origine + 2 de câblage), aucune régression.
- **Build SPFx complet vert**, `.sppkg` **`1.4.1.0`** produit
  (`sharepoint/solution/tour-de-controle.sppkg`).
- **Rien déployé, tenant intact.** La permission Graph, l'App Catalog et la page ne sont pas touchés.

## Reste (mise en service gardien, hors périmètre agent)

L'épreuve du réel reste **à rejouer par le gardien** : déploiement du `.sppkg` `1.4.1.0` à l'App
Catalog, puis vérification navigateur. Le diagnostic est désormais **exploitable** — si la lecture ne
part toujours pas, le cockpit (ligne d'anomalies) **et** la console nommeront la cause exacte
(découverte non câblée / indisponible, fabrique absente, `getClient('3')` en échec, résolution
site→drive échouée, ou statut HTTP), au lieu d'un échec muet.
