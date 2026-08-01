# Deux épreuves VERTES — 01/08/2026 — T-0045 : accès `Sites.Selected read` puis lecture bornée de la couche de saisie (0.22.0)

Rattachement : `T-0045` (« Lecteur machine fidèle des classeurs de saisie »), ouvert le 01/08 par l'épreuve 3g. Deux épreuves successives du même jour : **1/2** l'accès en lecture machine aux classeurs de saisie (diagnostic + octroi + preuve), **2/2** la primitive bornée `lire_saisie_table` (image **0.22.0**, révision **--0000032**). Les deux sont **vertes**. Elles **expliquent** l'écart de 22 j nommé par l'épreuve 3g. Le chantier **reste `à_faire`** : ce qui est soldé est l'accès et la lecture, pas le dérivateur.

## 1. Diagnostic — le 403 était une ABSENCE D'OCTROI, ni le code ni l'API

L'épreuve 3g avait laissé trois voies fermées, dont un `403` de l'identité managée sur `GRAPH_SAISIE_DRIVE_ID`, interprété alors comme « l'API Workbook n'est pas ouverte à l'app sur ce drive ». **Cette interprétation était fausse**, et c'est le premier acquis du jour.

Relevé des droits de l'identité managée (`883ea226-0bf2-4a8f-9f9d-92c9162a727d`, vérifié à la source Learn) : elle ne porte **QUE `Sites.Selected`** — un scope qui, seul, ne donne accès à **rien** : il n'ouvre que ce qu'un **octroi par site** lui concède, site par site. Relevé des octrois existants :

- site des **gabarits** (Contrats et administratif) : octroi présent, `role=write` — d'où la chaîne gabarit vivante depuis T-0031 ;
- site **Management et Gestion** (la saisie) : **AUCUN octroi**.

**Cause unique du `403` : il n'y avait rien à révoquer, rien à corriger dans le code — il manquait un octroi.** Le diagnostic de l'épreuve 3g avait attribué à l'API une limite qui était un défaut de configuration ; le journal 3g reste tel qu'écrit (on ne réécrit pas un relevé), et cette entrée porte la rectification.

## 2. Épreuve 1/2 — l'octroi `role=read` et le fait CONTRE LA DOCUMENTATION

Octroi posé par le **gardien** via Graph Explorer (geste humain, hors agent — proscrit de doctrine côté machine) : **`role=read`** sur le **seul** site Management et Gestion. Moindre privilège, périmètre nominatif, **pas `write`**.

**FAIT MESURÉ CONTRE LA DOC.** La lecture app-only **FONCTIONNE** sous `read` seul, alors que la page Learn de l'endpoint exact que nous appelons — `GET /drives/{id}/items/{id}/workbook/tables/{name}/rows`, [table-list-rows](https://learn.microsoft.com/graph/api/table-list-rows?view=graph-rest-1.0) — annonce noir sur blanc « **Application : Not supported.** » (idem `table-list`, `workbook-list-tables`). **Le réel tranche : la doc est incomplète sur ce point.** Conséquence pratique durable : un `403` sur ce chemin est un **défaut d'octroi**, jamais une limite de l'API — ne plus jamais conclure « API fermée » sans avoir relevé les octrois du site.

**CONSÉQUENCE DOCTRINALE — l'invariant descend du code vers le DROIT.** L'invariant §5.6 « **la machine n'écrit JAMAIS la saisie** » n'était garanti que par le code : un bug pouvait le violer. Il est désormais garanti **au niveau du droit** — sous `role=read`, aucune écriture n'est possible, quel que soit le code. Corollaire à tenir : **ne JAMAIS ajouter de scope `Files.*`** à l'identité managée — il outrepasserait `Sites.Selected` et ferait tomber la garantie.

**La preuve que la porte est ouverte est un `404`, pas un `200`.** Premier appel après octroi : `404` — et non plus `403` — sur un nom de table erroné. Graph **résout l'autorisation AVANT la ressource** : un `404` prouve donc que l'appelant est **autorisé** et que c'est la *ressource* qui manque. Le nom fautif était **`T_Imputations`** — la table du **GABARIT** (`modele-donnees.md` §5.2), jamais de la saisie. Deux causes distinctes (`403` sans octroi / `404` mauvais nom) que le corps d'erreur avalé nous avait empêché de séparer : c'est ce qui a coûté le temps de diagnostic.

## 3. Fait mesuré — la grille est lisible par position ; l'aplatissement venait du CONNECTEUR

Relevé du classeur `saisie-1-siteflow.xlsx` : il porte **TROIS tables nommées** — `SAISIE_Prevu_2026` (onglet « Prevu 2026 »), `SAISIE_Realise_2026` (« Realise 2026 »), `SAISIE_Facturation` (« Facturation »), le **millésime dans le nom** des deux grilles.

La grille est donc lisible **par l'API table, positions conservées** : schéma `[Ressource, Janvier … Décembre (12 positions), TOTAL]`, **14 colonnes**, un mois sans imputation étant une **cellule VIDE, jamais une colonne absente**. Troisième rectification du jour : **« le connecteur M365 aplatit la grille » était un défaut du CONNECTEUR** (surface humaine), **pas de Graph** — la voie machine, elle, n'a jamais aplati quoi que ce soit. Consigné au canon en candidat `modele-donnees.md` **v1.28** §5.6.

## 4. L'ÉCART DE 22 j DE L'ÉPREUVE 3g EST EXPLIQUÉ — c'était JUILLET

L'épreuve 3g avait dérivé **39 j** contre **61 j** au total réel, écart de **22 j** nommé sans être résolu (positions déduites par recoupement, **aucun mois forgé** — le fail-closed a tenu). Lecture positionnelle du 01/08, ligne `adrien.raque@allia-consulting.com` de `SAISIE_Realise_2026` :

| Grille | Positions renseignées | Σ 12 positions | `TOTAL` | Contrôle |
|---|---|---|---|---|
| `SAISIE_Realise_2026` | Mai **17**, Juin **22**, Juillet **22** | **61** | **61** | ✔ |
| `SAISIE_Prevu_2026` | Mai 17, Juin 22, Juil. 22, Août 10, Sept. 22, Oct. 21, Nov. 20, Déc. 14 | **148** | **148** | ✔ |

**Les 22 j manquants étaient JUILLET**, mesuré à sa **position** dans la grille. **Rien n'était perdu ni corrompu** : seule la lecture positionnelle manquait. Le contrôle obligatoire §5.6 — **Σ des douze positions == `TOTAL`** — tombe juste sur les deux grilles.

## 5. Épreuve 2/2 — `lire_saisie_table` (image 0.22.0, révision --0000032) : VERTE

Quatre étapes, aucune écriture, aucun incident. Variables `GRAPH_SAISIE_DRIVE_ID` / `GRAPH_SAISIE_FOLDER_ID` posées par le gardien (elles étaient **absentes** du conteneur, quatrième cause du jour).

**Chemin nominal** — `lire_saisie_table(code_mission=1, table="SAISIE_Realise_2026")` :

- **résolution sans aucun chemin fourni** : seuls `code_mission` et `table` sont transmis ; le serveur résout `saisie-1-siteflow.xlsx` (item `013OHVIUF4ZOYRBRIC3NDJTWYOABSZUMKD`) par la convention **`^saisie-(\d+)-`** dans le dossier figé — le libellé après le code étant libre, le nom n'est pas déductible : on liste et on apparie. Aucune cible libre n'est exposée à l'appelant (ni `drive_id`, ni `item_id`, ni chemin) ;
- **fidélité** : 14 éléments par ligne, **vides préservés** (`""` pour Janvier–Avril et Août–Décembre), `count: 21` lignes rendues **telles que Graph les sert** — le serveur ne dérive pas, ne filtre pas, n'interprète pas ;
- **contrôle Σ == TOTAL** vert (§4 ci-dessus) ;
- **métadonnées d'item exposées** : `eTag "{10B1CBBC-02C5-46DB-99DB-0E00659A3143},8"`, `cTag …,9`, `lastModifiedDateTime 2026-07-31T15:30:53Z` — de quoi prouver plus tard qu'une lecture n'a rien écrit.

**Les trois refus** (ce sont des refus, aucune écriture) :

| Appel | Résultat mesuré |
|---|---|
| `table="T_Imputations"` | Refus **pré-réseau**, **nommant la cause** : « *T_Imputations est la table du GABARIT (§5.2), PAS de la saisie … C'est la cause EXACTE du 404 mesuré le 01/08/2026* ». Le fait du jour est **rejoué en garde** : la cause du 404 ne peut plus se reproduire silencieusement |
| `table="SAISIE_Realise_2025"` | **404 Graph remonté AVEC son corps** : code « **ItemNotFound** », message « *La ressource demandée n'existe pas.* », enrichi du classeur et de la table. Ce n'est **pas** un refus pré-réseau — voir l'arbitrage §6 |
| `code_mission=99` | Refus explicite : « *aucun classeur de saisie pour le code 99 dans le dossier de saisie figé (attendu : `saisie-99-<Libellé>.xlsx`, §5.6). Rien n'est lu.* » |

**ACQUIS 0.22.0 — le corps d'erreur Graph n'est plus avalé.** Le refus réseau remonte désormais le **code** et le **message Graph mot pour mot**. C'est exactement ce qui manquait le matin du 01/08 et qui nous a coûté le diagnostic entre « 403 sans octroi » et « 404 mauvais nom » : la même ambiguïté, aujourd'hui, se lit en une ligne.

**Bouclage** — `SAISIE_Prevu_2026` : Σ = **148** == `TOTAL`, même `eTag …,8` que la lecture du Réalisé (un seul classeur, deux tables).

## 6. Arbitrage gardien du 01/08 — le millésime n'est PAS gaté : DÉCISION, pas dette

La garde serveur valide le **motif** `SAISIE_Realise_<millésime>` / `SAISIE_Prevu_<millésime>`, **et non une liste blanche de millésimes**. Conséquence assumée : `SAISIE_Realise_2025` part au réseau et rend un `404`, au lieu d'être refusé avant.

**Arbitrage du gardien : c'est le bon comportement.** Une liste blanche exigerait une **maintenance annuelle** et **casserait en janvier** (la table de l'année neuve serait refusée par la garde le jour où elle devient la seule utile) ; un **404 lisible** — désormais lisible, précisément grâce à l'acquis ci-dessus — est préférable à une garde qui périme. **Décision tracée, pas dette technique** : ne pas la « corriger » par réflexe.

## 7. Piège consigné pour le futur dérivateur

La table rend **21 lignes**, dont **2 seulement portent du sens** au regard de la dérivation :

- la **ligne d'entête technique « Nb. jours ouvres max »** (`22, 20, 22, 22, 21, 22, 23, 21, 22, 22, 21, 23`, `TOTAL` vide) — ce n'est **pas une ressource**, c'est un plafond de calendrier : **à écarter** ;
- **19 lignes de la zone de saisie pré-dimensionnée** à `Ressource` vide et **`TOTAL = 0`** — des **lignes fantômes**, même famille que le prédicat « vierge » de T-0035 : **à écarter**.

La primitive les rend **volontairement** : lire n'est pas interpréter, le filtrage appartient au **consommateur** (règle de dérivation §5.6). Un dérivateur naïf qui compte les lignes ou somme la colonne `TOTAL` sans écarter ces 20 lignes se tromperait — et le contrôle **Σ douze positions == `TOTAL`** est ce qui doit tomber juste **ligne à ligne**, l'écart étant une **anomalie signalée**, jamais un mois forgé ni déduit par recoupement.

## 8. Ce qui est soldé, ce qui reste

**SOLDÉ par ces deux épreuves** : l'**accès** en lecture machine à la couche de saisie (octroi `read` au moindre privilège, invariant garanti au niveau du droit) et la **lecture fidèle** (positions conservées, Σ == TOTAL, refus nominatifs, corps d'erreur Graph remonté). Les quatre causes du blocage — absence d'octroi, mauvais nom de table, corps d'erreur avalé, variable d'environnement absente — sont **toutes levées**.

**RESTE, et `T-0045` demeure donc `à_faire`** : le **dérivateur du Réalisé** (`T_Imputations` depuis `SAISIE_Realise_2026`, application de la règle §5.6) côté **consommateur**, et **son épreuve**. C'est la **dernière condition de solde** du chantier — la lecture est acquise, la dérivation n'est pas construite.

**Aucune écriture tenant, aucun code, aucun contrat modifié par cette entrée** — consignation seule. Le candidat `modele-donnees.md` v1.28 (PR #286) et le serveur 0.22.0 (PR #287) sont déjà au canon.
