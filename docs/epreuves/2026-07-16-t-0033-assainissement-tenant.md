# Épreuve T-0033 (2/2) — assainissement tenant : STOP n°1 avant toute écriture (chemin d'écriture délégué indisponible)

Entrée d'épreuve du 2026-07-16 (session S36). Fait nouveau ; aucune requalification d'un soldé,
aucune réécriture d'entrée existante. **T-0033 reste `à_faire`** : l'épreuve tenant ne s'est PAS
soldée cette session. Un seul arrêt, **STOP n°1, AVANT tout geste d'écriture** — le tenant est
**strictement inchangé** (vérifié par relecture, cf. §4). Zéro geste gardien (ni clic, ni saisie).

But visé : sur le tenant, archiver la souche polluée et les gabarits pollués de S35 vers « 00 - Old »,
déposer la souche propre (HEAD, 9886 o) dans « 06 - Gabarit ERP », ré-instancier les gabarits des deux
missions actives (Siteflow = code 1, Datalab = code 2), et prouver `count:0` sur les 6 tables
(3 tables × 2 gabarits). **Non atteint** : aucun chemin d'écriture-fichier disponible pour la machine
dans cette session (détail §3).

## 1. Garde-fou SHA (vert)

- `git fetch origin` ; `origin/main` = `a428665f82a1afd615e53b92ca7819a1fa71ddef`.
- `a428665f` (merge PR #224, souche propre au canon) est **ancêtre de `origin/main`** (`ANCESTOR_OK`) —
  en fait `a428665f` **EST** le tip de `origin/main`.
- Branche de travail créée depuis `main` à jour : `feat/t0033-tenant-assainissement`.
- Working tree : nettoyage `.mcp.json` (retrait de l'entrée obsolète `allia-mcp-graph`, config OAuth
  publique S35, aucun secret) conservé — il fait partie de cette PR (hygiène). Le branchement vivant du
  MCP reste en config locale, hors dépôt.

## 2. Lecture du réel (verte) — coordonnées tenant découvertes (non secrètes)

Découverte **par le connecteur M365 délégué** (voir §3 pour pourquoi pas par jeton Graph az) sur le site
`AlliaConsulting-Contratsetadministratif` (host `alliaconsuling.sharepoint.com` — une seule « t » au
tenant, deux au site, piège §5.6 confirmé). Consignées ici comme le prescrit le prompt (ce ne sont pas
des secrets) :

- **site id** : `alliaconsuling.sharepoint.com,71a280e3-f578-46ea-aa6d-d6de96c4e73d,0f75a74b-7b10-4a92-9819-3b900c658d13`
- **drive id** (bibliothèque « Documents partages ») : `b!44CicXj16kaqbdbelsTnPUundQ8Qe5JKmBk7kAxljRO8Hx-KrTj1QJbs4Mp6eHK7`
- **« 06 - Gabarit ERP »** (dossier) item id : `01BWFCBZHUYHKQWWD2IZDLEAVEXO4PVCFS`
- **« 00 - Old »** (sous-dossier de « 06 - Gabarit ERP ») item id : `01BWFCBZADO5QA7ZWTUBGZSBGWWCKQZH65`

État de « 06 - Gabarit ERP » **avant** (et **après**, cf. §4 — inchangé) :

| Fichier | Taille (o) | item id | État |
|---|---|---|---|
| `gabarit-1.xlsx` (Siteflow) | 22 592 | `01BWFCBZCUZH2W65N2QFCJNHIJSALL5WS4` | pollué S35 |
| `gabarit-2.xlsx` (Datalab) | 22 551 | `01BWFCBZGEFQB35NVNJ5CZWQZ6ZMYMDW2D` | pollué S35 |
| `gabarit-pilotage-mission.xlsx` (souche) | 22 594 | `01BWFCBZH6BD2AON6G7ZC2VOEDJKLLJUNN` | **polluée** (≠ souche propre 9 886 o) |
| `00 - Old` (dossier) | 0 | `01BWFCBZADO5QA7ZWTUBGZSBGWWCKQZH65` | **vide** |

**Souche propre (HEAD) pré-vérifiée** localement (openpyxl) avant tout dépôt : 3 tables nommées
`T_Affectations` (ref `A1:D1`) / `T_Imputations` (`A1:E1`) / `T_Echeancier` (`A1:G1`) — **en-têtes seuls,
0 ligne de corps** ; en-têtes conformes §5.2. C'est bien ce classeur (9 886 o) qui aurait produit
`count:0` à l'instanciation.

**Preuve de vie du MCP allia-graph (LECTURE SEULE, verte — pas de 401)** :

```
workbook_lire_table(drive_id=…KrTj1QJbs4Mp6eHK7, item_id=01BWFCBZCUZH2W65N2QFCJNHIJSALL5WS4, table=T_Affectations)
→ {"table":"T_Affectations","lignes":[["","","",""]],"count":1}
```

Le serveur MCP répond (jeton délégué valide). `count:1` avec une ligne **entièrement vide** confirme,
sur le réel, exactement l'état laissé par **STOP n°3 de S35** (vider une ligne de tableau à la main ≠
supprimer la ligne : une table nommée conserve ≥ 1 ligne de corps). C'est l'état que T-0033 doit
assainir par ré-instanciation complète depuis une souche propre.

## 3. STOP n°1 — aucun chemin d'écriture-fichier disponible pour la machine

Le geste 1 (archivage-déplacement) exige de **déplacer** des fichiers hors de « 06 - Gabarit ERP », le
geste 2 (dépôt) exige de **téléverser** un binaire dans « 06 - Gabarit ERP », le geste 3
(ré-instanciation) exige que les noms `gabarit-1/2.xlsx` soient **libres** et que la souche en place soit
**propre**. Les trois chemins d'écriture-fichier accessibles à la machine sont bloqués :

1. **Jeton Graph délégué via Azure CLI** (`az account get-access-token --resource https://graph.microsoft.com`) —
   le prompt le prescrivait pour découvrir les coordonnées et déposer. Il **fonctionne** (jeton acquis,
   `aud=https://graph.microsoft.com`, utilisateur `adrien.raque@allia-consulting.com`) **mais ses scopes
   ne couvrent PAS SharePoint** : `scp = Application.ReadWrite.All AppRoleAssignment.ReadWrite.All
   AuditLog.Read.All DelegatedPermissionGrant.ReadWrite.All Directory.AccessAsUser.All email
   Group.ReadWrite.All openid profile User.Read.All User.ReadWrite.All` — **ni `Sites.*` ni `Files.*`**.
   Conséquence observée : `GET /sites/{id}/drives` renvoie `{"value":[]}` (aucun drive visible),
   `GET /sites/{id}/drive` renvoie `null`. Impossible de découvrir un drive/item **ni a fortiori d'écrire
   un fichier** avec ce jeton. L'app Azure CLTI a un jeu de permissions déléguées Graph **figé** :
   ajouter `Sites.ReadWrite.All` / `Files.ReadWrite.All` = **consentement OAuth**, geste d'authentification
   **réservé au gardien** (garde-fou CLAUDE.md « configurer l'authentification (SSO/OAuth) ») — non fait.

2. **Connecteur M365 délégué (claude.ai Microsoft 365)** — ses outils de **lecture** fonctionnent
   (recherche de dossiers, `read_resource` : c'est par eux que §2 a découvert les coordonnées et l'état).
   Mais ses outils d'**écriture** sont **verrouillés** : `sharepoint_move_item(...)` →
   `permission_error : "This tool is not available."` (rejet au niveau connecteur, **avant** tout appel
   Graph — aucune mutation). Même verrou attendu pour `sharepoint_upload_file` / `sharepoint_delete_item`
   (connecteur en lecture seule pour cette session). **Non contourné** (aucune tentative de mutation
   spéculative).

3. **Primitives MCP allia-graph (identité managée, écriture bornée « 06 - Gabarit ERP »)** — elles
   écrivent, mais **aucune ne couvre les deux prérequis** :
   - **Dépôt de la souche propre** : il n'existe **aucune primitive de téléversement/remplacement d'un
     binaire souche**. La souche en place resterait la **polluée** (22 594 o) ; instancier par-dessus
     reproduirait la pollution S35 (`count≠0`) → ce serait rejouer STOP n°2 de S35.
   - **Libération des noms** : `workbook_archiver_gabarit` fait une **COPIE** vers « 00 - Old » (POST
     `/copy`) et **laisse l'original** dans « 06 - Gabarit ERP ». Aucune primitive ne **supprime** ni ne
     **déplace-hors** un gabarit. Or `workbook_instancier_gabarit` est **fail-closed**
     (`conflictBehavior=fail`) : tant que `gabarit-1/2.xlsx` occupent leur nom, la ré-instanciation
     lèverait `409` (`FileExistsError`).

**Conclusion.** Le flux « machine, zéro geste gardien » demandé par ce prompt est **infaisable avec les
outils disponibles dans cette session** : les deux prérequis durs (déposer la souche propre ; libérer les
noms `gabarit-1/2`) n'ont **aucun chemin machine**. Conformément à la règle S35 (STOP au premier
incident, aucune retouche, aucun rafistolage), **arrêt AVANT toute écriture**. Aucune primitive d'écriture
allia-graph n'a été appelée (une instanciation aveugle aurait soit `409`, soit — pire — propagé la souche
polluée).

## 4. État exact du tenant après l'arrêt — INCHANGÉ

Relecture de « 06 - Gabarit ERP » **après** l'arrêt (identique à §2) :

```
00 - Old                        (folder, 0 bytes)      01BWFCBZADO5QA7ZWTUBGZSBGWWCKQZH65   [vide]
gabarit-1.xlsx                  (file, 22592 bytes)    01BWFCBZCUZH2W65N2QFCJNHIJSALL5WS4
gabarit-2.xlsx                  (file, 22551 bytes)    01BWFCBZGEFQB35NVNJ5CZWQZ6ZMYMDW2D
gabarit-pilotage-mission.xlsx   (file, 22594 bytes)    01BWFCBZH6BD2AON6G7ZC2VOEDJKLLJUNN   [souche polluée]
```

Le seul appel d'écriture émis (`sharepoint_move_item`) a été **refusé au niveau connecteur sans effet** ;
aucune primitive allia-graph d'écriture n'a été appelée. **Rien n'a été créé, déplacé, supprimé ou écrit
sur le tenant.**

## 5. Reprise proposée (décision gardien)

L'assainissement machine ne pourra aboutir qu'une fois **l'un** de ces chemins ouvert (chacun est un
geste de gouvernance/auth réservé au gardien, hors de la main de l'agent) :

- **(A) — le plus simple, conforme aux critères T-0033.** Le gardien exécute **par la main** les deux
  gestes que l'agent ne peut pas faire par machine et qui sont **hors périmètre des primitives** :
  (1) le **« clic de dépôt du binaire »** (déjà explicitement autorisé par les critères d'acceptation de
  T-0033) — déposer `contrats/socle/gabarit-pilotage-mission.xlsx` (HEAD, 9 886 o) dans « 06 - Gabarit
  ERP » **en remplaçant** la souche polluée (l'ancienne étant d'abord glissée dans « 00 - Old ») ; et
  (2) **déplacer** `gabarit-1.xlsx` et `gabarit-2.xlsx` pollués vers « 00 - Old » (libère les noms).
  Ensuite **la machine reprend** : `workbook_instancier_gabarit(1)` puis `(2)` (création pure depuis la
  souche propre), puis `workbook_lire_table` × 6 pour la preuve `count:0`. — Écart avec ce prompt : ce
  dernier interdisait tout geste gardien ; les critères de T-0033.yaml, eux, tolèrent « un éventuel clic
  de dépôt du binaire ». La lever de STOP suppose donc de relâcher la contrainte « zéro geste gardien »
  du prompt sur ces deux gestes fichier bornés.

- **(B) — plus outillé, garde le flux 100 % machine.** Ouvrir à l'agent un **jeton Graph délégué avec
  scope SharePoint** (`Sites.ReadWrite.All` / `Files.ReadWrite.All`) — soit en **activant les outils
  d'écriture du connecteur M365** pour la session, soit via un `az login` **consenti** pour ces scopes.
  La machine ferait alors tout : déplacer les 3 fichiers pollués vers « 00 - Old », téléverser la souche
  propre, `instancier ×2`, preuve `count:0 ×6`. — C'est un geste de **consentement OAuth / activation de
  connecteur**, réservé au gardien.

- **(C) — durcissement du canon (chantier serveur, T-0031).** Doter allia-graph de deux primitives
  bornées manquantes : **remplacement de la souche** (`06 - Gabarit ERP/gabarit-pilotage-mission.xlsx`,
  cible figée) et **retrait/déplacement d'un gabarit** vers « 00 - Old » (le miroir « move » de
  l'actuel `archiver` qui n'est qu'un « copy »). Cela lèverait la **lacune de conception** révélée ici :
  `workbook_archiver_gabarit` copie sans libérer le nom, alors que la ré-instanciation fail-closed exige
  le nom libre — aujourd'hui aucun geste machine ne comble cet écart.

## 6. Fait nouveau consigné

Leçon durable de cette session : **la ré-instanciation d'un gabarit à nom fixe (`1 mission = 1 gabarit`,
§5.2) suppose de LIBÉRER le nom au préalable ; or `workbook_archiver_gabarit` COPIE et ne libère pas.**
Le geste « archiver puis ré-instancier » de T-0033 comporte donc un maillon (retrait de l'ancien /
dépôt de la souche propre) **sans primitive machine** dans l'outillage actuel — d'où le STOP. Journalisé
comme fait nouveau ; aucune entrée existante réécrite.
