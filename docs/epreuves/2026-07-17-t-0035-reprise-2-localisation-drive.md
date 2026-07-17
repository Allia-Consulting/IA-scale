# Épreuve T-0035 (reprise n°2) — localisation drive : webUrl percent-encodé ≠ chemin en clair

Entrée d'épreuve du 2026-07-17. Fait nouveau ; aucune requalification d'un soldé, aucune réécriture
d'entrée existante. **T-0035 reste `en_cours`** : le point 2 (câblage économique réel) est repris une
seconde fois, cette fois-ci la reprise n°1 (auto-diagnostiquante) ayant **rempli son office** —
l'épreuve du réel a **nommé la cause** au lieu d'un échec muet. Historique immutable — cette entrée
s'ajoute au journal, elle n'efface rien.

## Faits observés — l'épreuve du réel (17/07/2026, après déploiement 1.4.1.0)

La solution `1.4.1.0` (reprise n°1) a été déployée et la page rejouée. Symptômes au navigateur :

- **Fraîcheur vivante** : « lu le 17/07/2026 à 13:36 » — le composant se monte, rend, et le câblage
  s'exécute jusqu'au bout.
- **8 anomalies**, toutes portant désormais **la même cause explicite** :
  **« chemin hors des drives du site »** (`gabarit-1.xlsx` ×3, `gabarit-2.xlsx` ×3, référentiel
  `T_Ressources`, référentiel `T_Structure`).

La reprise n°1 a donc fait exactement ce pour quoi elle a été construite : **il n'y a plus d'échec
muet**. La cause est nommée, et elle **innocente** tout le haut de la chaîne — `getClient('3')`, la
résolution `site → drives`, le passage de la fabrique fonctionnent (sinon la cause affichée serait
tout autre). Le **seul** point de rupture est `localiserDansDrive`, qui ne trouvait aucun drive
porteur et rendait pour chaque table l'anomalie `cause: 'chemin hors des drives du site'`
(`workbook-graph.ts`, `lireTable`).

## Diagnostic — encodage asymétrique des deux côtés de la comparaison

`localiserDansDrive` cherche, parmi les drives du site, celui dont la racine **préfixe** l'URL
server-relative du fichier, puis en déduit le chemin résiduel. La comparaison d'origine était une
comparaison de **chaînes brutes** :

```
cible.indexOf(d.racine + '/') === 0
```

Or les deux côtés n'arrivent **pas dans le même encodage** :

- **`d.racine`** est dérivée du **`webUrl` des drives renvoyé par Graph**, qui est **percent-encodé**
  (ex. `.../sites/Contratsetadministratif/Documents%20partages`).
- **`fichierServerRelative`** provient des **props / de la découverte** et arrive **EN CLAIR** :
  espaces, accents (`« Coût »`), `« & »` (`« Masse salariale & Indep »`).

`'/…/Documents partages/…'.indexOf('/…/Documents%20partages/')` échoue systématiquement → **aucun
drive porteur** → anomalie « chemin hors des drives du site » pour les 8 tables. Un seul octet de
divergence d'encodage (`%20` vs espace) suffit à faire échouer tout un cockpit.

## Correction (PR de reprise n°2, solution SPFx `1.4.1.0` → `1.4.2.0`)

`localiserDansDrive` (`workbook-graph.ts`) compare désormais des **segments décodés** des deux côtés,
et **ré-encode** le résiduel pour l'API :

- **`decoderSegment`** : `decodeURIComponent` par segment, **tolérant** à un segment déjà en clair —
  `decodeURIComponent('100%')` lèverait ; on rend alors le segment **inchangé** plutôt que d'échouer.
- **`segmentsDecodes`** : découpe sur `/`, ôte les vides (donc **insensible au trailing slash**),
  décode chaque segment.
- **`estPrefixeDeSegments`** : préfixe **segment par segment** (plus de comparaison de sous-chaîne
  fragile), drive le plus **spécifique** d'abord (plus grand nombre de segments).
- **Résiduel ré-encodé** : les segments restants (en clair) sont rejoints, puis **ré-encodés segment
  par segment** par `encoderChemin` avant l'appel `root:{chemin}:` (espaces, accents, `« & »`
  correctement re-percent-encodés).

## Vérification (banc) — rouge puis vert

- **4 nouveaux tests reproduisant le RÉEL** (`workbook-graph.test.ts`) : `webUrl` de drive
  **percent-encodé** (`.../Documents%20partages`) + chemins props **en clair** avec les VRAIS chemins
  de l'épreuve — `« 06 - Gabarit ERP »` (espaces), `« 07 - Coût de Structure »` (accent),
  `« 08 - Coût Masse salariale & Indep »` (accent + `&`), plus un cas **symétrique** (webUrl en clair
  + chemin props encodé). **ROUGES** sur le code d'avant (4 échecs), **VERTS** après correction.
- **heft : 87 tests verts** (83 + 4), aucune régression.
- **Build SPFx complet vert**, `.sppkg` **`1.4.2.0`** produit
  (`sharepoint/solution/tour-de-controle.sppkg`).
- **Rien déployé, tenant intact.** Permission Graph, App Catalog et page non touchés.

## Reste (mise en service gardien, hors périmètre agent)

L'épreuve du réel reste **à rejouer par le gardien** : déploiement du `.sppkg` `1.4.2.0` à l'App
Catalog, puis vérification navigateur des 3 bandeaux (staffing, rentabilité, factures) sur données
réelles. Les gabarits et référentiels doivent désormais être **localisés et lus** ; toute anomalie
résiduelle continuera de **nommer sa cause exacte** (acquis de la reprise n°1).
