// Lecture Graph Workbook des gabarits actifs + référentiel de coûts — logique PURE, sans SPFx.
//
// Cockpit v2 point 2 (T-0035). Là où gabarits.ts DÉCOUVRE la présence/fraîcheur des gabarits
// (listing REST du dossier), ce module OUVRE les classeurs et lit le CONTENU de leurs tables
// nommées via l'API Microsoft Graph Workbook v1.0 (workbook/tables/{name}/columns), sous
// l'identité de l'utilisateur (Graph délégué — SSO SPFx, permission Sites.Read.All approuvée par
// le gardien). Aucun secret, aucune élévation.
//
// Isolé de React et de MSGraphClientV3 à dessein : la résolution (site → drive → driveItem par
// chemin), le parsing des tables et les NORMALISATIONS de lecture sont testables sans réseau. La
// primitive réseau `GrapheGet` est INJECTÉE par listes-reelles.ts (adaptateur MSGraphClientV3).
//
// Faits de lecture ÉPROUVÉS (épreuve T-0031, 2026-07-17) que ce module normalise :
//   - les dates écrites `AAAA-MM-JJ` reviennent en SÉRIE Excel (ex. 46143 = 2026-05-01) ;
//   - `CodeMission` écrit en chaîne revient coercé en ENTIER par le service Excel.
// Un gabarit/référentiel au schéma cassé (table manquante, en-tête inattendu) est une ANOMALIE
// SIGNALÉE (jamais un zéro inventé, jamais ignorée) ; le référentiel en 403/404 est un état
// d'accès 'restreint'/'indisponible' (jamais bloquant).

import type { AnomalieGabarit, EtatAcces } from './gabarits';

// ---------------------------------------------------------------------------
// Schéma normatif des tables — DÉRIVÉ de modele-donnees.md §5.2 / §5.3 (le contrat FAIT FOI).
// En-têtes figés, dans l'ordre du contrat. On valide la PRÉSENCE de chaque en-tête attendu ;
// tout écart (en-tête manquant) est signalé comme anomalie.
// ---------------------------------------------------------------------------
export const ENTETES_AFFECTATIONS = ['CodeMission', 'Ressource', 'Mois', 'JoursPrevus'] as const;
export const ENTETES_IMPUTATIONS = ['CodeMission', 'Ressource', 'Mois', 'JoursRealises', 'StatutValidation'] as const;
export const ENTETES_ECHEANCIER = ['NumFacture', 'CodeMission', 'MoisCA', 'MontantHT', 'Echeance', 'Statut', 'LienFacture'] as const;
export const ENTETES_RESSOURCES = ['Ressource', 'Type', 'CoutJour', 'DateEntree', 'DateSortie'] as const;
export const ENTETES_STRUCTURE = ['Mois', 'PosteCout', 'Montant'] as const;

/** Nom des trois tables du gabarit (modele-donnees.md §5.2). */
export const TABLE_AFFECTATIONS = 'T_Affectations';
export const TABLE_IMPUTATIONS = 'T_Imputations';
export const TABLE_ECHEANCIER = 'T_Echeancier';
/** Tables du référentiel de coûts (modele-donnees.md §5.3), une par classeur. */
export const TABLE_RESSOURCES = 'T_Ressources';
export const TABLE_STRUCTURE = 'T_Structure';

// ---------------------------------------------------------------------------
// Primitive réseau INJECTÉE (implémentée par listes-reelles.ts, liée à MSGraphClientV3).
// Ne lève JAMAIS : l'adaptateur capture tout échec et le rend en {ok:false,status}.
// ---------------------------------------------------------------------------
export interface ReponseGraphe {
  readonly ok: boolean;
  readonly status: number;
  /** Corps JSON déjà désérialisé (ou undefined si absent / échec). */
  readonly corps?: unknown;
}

/** Un GET Graph par chemin d'API relatif (ex. `/sites/{id}/drives`). Ne lève jamais. */
export type GrapheGet = (cheminApi: string) => Promise<ReponseGraphe>;

// ---------------------------------------------------------------------------
// NORMALISATIONS de lecture (faits éprouvés T-0031).
// ---------------------------------------------------------------------------
/** Époque du numéro de série Excel : jour 0 = 1899-12-30 (inclut le bug de l'an-bissextile 1900). */
const EPOQUE_EXCEL_MS = Date.UTC(1899, 11, 30);
const JOUR_MS = 86400000;

/**
 * Convertit une valeur de cellule de date en `Date` (UTC), en gérant les deux formes observées :
 *  - NOMBRE : série Excel (46143 = 2026-05-01) → epoch + série × un jour ;
 *  - CHAÎNE : `AAAA-MM-JJ` ou ISO → `Date` (interprétée en UTC pour rester stable en test).
 * Retourne `undefined` pour une cellule vide ou non interprétable (jamais une date inventée).
 */
export function versDate(cellule: unknown): Date | undefined {
  if (typeof cellule === 'number' && isFinite(cellule) && cellule > 0) {
    return new Date(EPOQUE_EXCEL_MS + Math.round(cellule) * JOUR_MS);
  }
  if (typeof cellule === 'string') {
    const t = cellule.trim();
    if (!t) { return undefined; }
    // `AAAA-MM-JJ` (10 car.) → fixé à minuit UTC (pas de dérive de fuseau).
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(t);
    if (m) { return new Date(Date.UTC(Number(m[1]), Number(m[2]) - 1, Number(m[3]))); }
    const d = new Date(t);
    return isNaN(d.getTime()) ? undefined : d;
  }
  return undefined;
}

/** Index de mois 0-based (0 = janvier) d'une cellule de date, ou `undefined`. Toujours en UTC. */
export function moisIndexDe(cellule: unknown): number | undefined {
  const d = versDate(cellule);
  return d ? d.getUTCMonth() : undefined;
}

/** Année d'une cellule de date, ou `undefined`. Toujours en UTC. */
export function anneeDe(cellule: unknown): number | undefined {
  const d = versDate(cellule);
  return d ? d.getUTCFullYear() : undefined;
}

/**
 * CodeMission TOUJOURS en chaîne : le service Excel coerce une chaîne numérique en entier à la
 * relecture (fait T-0031). `1` (number) et `'1'` (string) doivent donner la même clé `'1'`.
 */
export function codeMissionEnString(cellule: unknown): string {
  if (cellule === null || cellule === undefined) { return ''; }
  if (typeof cellule === 'number') { return String(cellule); }
  return String(cellule).trim();
}

/**
 * Nombre, ou `undefined` si absent/illisible (jamais 0 inventé). Gère le nombre natif et la chaîne
 * (virgule décimale et espaces/insécables de milliers tolérés).
 */
export function versNombre(cellule: unknown): number | undefined {
  if (typeof cellule === 'number') { return isFinite(cellule) ? cellule : undefined; }
  if (typeof cellule === 'string') {
    const t = cellule.replace(/[\s ]/g, '').replace(',', '.');
    if (!t) { return undefined; }
    const n = Number(t);
    return isNaN(n) ? undefined : n;
  }
  return undefined;
}

/** Chaîne strippée, ou '' si absente. */
export function versTexte(cellule: unknown): string {
  if (cellule === null || cellule === undefined) { return ''; }
  return String(cellule).trim();
}

// ---------------------------------------------------------------------------
// Lignes typées des tables (valeurs déjà normalisées). Une date absente reste `undefined`
// (le calcul en tiendra compte : « · », jamais un zéro).
// ---------------------------------------------------------------------------
export interface LigneAffectation { readonly codeMission: string; readonly ressource: string; readonly mois?: Date; readonly joursPrevus?: number; }
export interface LigneImputation { readonly codeMission: string; readonly ressource: string; readonly mois?: Date; readonly joursRealises?: number; readonly statutValidation: string; }
export interface LigneEcheancier { readonly numFacture: string; readonly codeMission: string; readonly moisCA?: Date; readonly montantHT?: number; readonly echeance?: Date; readonly statut: string; readonly lienFacture: string; }
export interface LigneRessource { readonly ressource: string; readonly type: string; readonly coutJour?: number; readonly dateEntree?: Date; readonly dateSortie?: Date; }
export interface LigneStructure { readonly mois?: Date; readonly posteCout: string; readonly montant?: number; }

/** Contenu lu d'un gabarit de mission (3 tables). */
export interface ContenuGabarit {
  readonly codeMission: string;
  readonly affectations: ReadonlyArray<LigneAffectation>;
  readonly imputations: ReadonlyArray<LigneImputation>;
  readonly echeancier: ReadonlyArray<LigneEcheancier>;
}

/** Contenu lu du référentiel de coûts (audience restreinte, §5.3). */
export interface ContenuReferentiel {
  readonly ressources: ReadonlyArray<LigneRessource>;
  readonly structure: ReadonlyArray<LigneStructure>;
}

// ---------------------------------------------------------------------------
// Parsing d'une table Graph (réponse de `.../workbook/tables/{name}/columns`).
// La réponse porte, par colonne : { name, values: [[enTête], [cell], [cell], …] }.
// On valide la présence des en-têtes attendus (sinon anomalie) et on transpose colonnes → lignes.
// ---------------------------------------------------------------------------
interface ColonneGraphe { readonly name: string; readonly values: ReadonlyArray<ReadonlyArray<unknown>>; }

interface TableParsee {
  /** Une entrée par ligne de corps : map en-tête → valeur brute (cellule). */
  readonly lignes: ReadonlyArray<Record<string, unknown>>;
  /** En-têtes attendus absents (déclenche une anomalie chez l'appelant). */
  readonly entetesManquants: ReadonlyArray<string>;
}

function estColonnes(corps: unknown): corps is { value: ReadonlyArray<ColonneGraphe> } {
  return !!corps && typeof corps === 'object' && Array.isArray((corps as { value?: unknown }).value);
}

/**
 * Transpose la réponse `columns` en lignes de corps + repère les en-têtes attendus manquants.
 * La cellule d'en-tête de chaque colonne est `values[0][0]`, ses cellules de corps `values[r][0]`.
 */
export function parserTableColonnes(
  corps: unknown,
  entetesAttendus: ReadonlyArray<string>
): TableParsee {
  if (!estColonnes(corps)) { return { lignes: [], entetesManquants: [...entetesAttendus] }; }
  const colonnes = corps.value;
  const parNom = new Map<string, ReadonlyArray<ReadonlyArray<unknown>>>();
  for (const c of colonnes) {
    if (c && typeof c.name === 'string' && Array.isArray(c.values)) { parNom.set(c.name.trim(), c.values); }
  }
  const entetesManquants = entetesAttendus.filter(e => !parNom.has(e));
  // Nombre de lignes de corps = (hauteur de colonne) − 1 (l'en-tête). Robuste si une colonne est vide.
  let nbLignes = 0;
  parNom.forEach(values => { nbLignes = Math.max(nbLignes, Math.max(0, values.length - 1)); });
  const lignes: Array<Record<string, unknown>> = [];
  for (let r = 1; r <= nbLignes; r++) {
    const ligne: Record<string, unknown> = {};
    for (const e of entetesAttendus) {
      const values = parNom.get(e);
      ligne[e] = values && values[r] ? values[r][0] : undefined;
    }
    lignes.push(ligne);
  }
  return { lignes, entetesManquants };
}

// --- Mappers typés (appliquent les normalisations) ---------------------------------------------
function mapAffectation(l: Record<string, unknown>): LigneAffectation {
  return { codeMission: codeMissionEnString(l.CodeMission), ressource: versTexte(l.Ressource), mois: versDate(l.Mois), joursPrevus: versNombre(l.JoursPrevus) };
}
function mapImputation(l: Record<string, unknown>): LigneImputation {
  return { codeMission: codeMissionEnString(l.CodeMission), ressource: versTexte(l.Ressource), mois: versDate(l.Mois), joursRealises: versNombre(l.JoursRealises), statutValidation: versTexte(l.StatutValidation) };
}
function mapEcheancier(l: Record<string, unknown>): LigneEcheancier {
  return { numFacture: versTexte(l.NumFacture), codeMission: codeMissionEnString(l.CodeMission), moisCA: versDate(l.MoisCA), montantHT: versNombre(l.MontantHT), echeance: versDate(l.Echeance), statut: versTexte(l.Statut), lienFacture: versTexte(l.LienFacture) };
}
function mapRessource(l: Record<string, unknown>): LigneRessource {
  return { ressource: versTexte(l.Ressource), type: versTexte(l.Type), coutJour: versNombre(l.CoutJour), dateEntree: versDate(l.DateEntree), dateSortie: versDate(l.DateSortie) };
}
function mapStructure(l: Record<string, unknown>): LigneStructure {
  return { mois: versDate(l.Mois), posteCout: versTexte(l.PosteCout), montant: versNombre(l.Montant) };
}

// ---------------------------------------------------------------------------
// Résolution site → drive → driveItem PAR CHEMIN (Microsoft Graph v1.0, grounded Learn 2026-07-17).
//   1. site : GET /sites/{hôte}:{cheminSite}?$select=id
//   2. drives : GET /sites/{siteId}/drives?$select=id,name,webUrl
//   3. table : GET /drives/{driveId}/root:{cheminDansDrive}:/workbook/tables/{table}/columns
// Le driveItem est adressé par chemin relatif à la racine du drive porteur (celui dont le webUrl
// préfixe l'URL server-relative du fichier). Aucune coordonnée en dur (tout vient du site + du
// chemin server-relative découvert / des props référentiel).
// ---------------------------------------------------------------------------

/** Décompose une URL absolue de site en (hôte, chemin server-relative). */
export function hoteEtCheminSite(siteUrl: string): { readonly hote: string; readonly chemin: string } | undefined {
  const m = /^https?:\/\/([^/]+)(\/.*)?$/.exec(siteUrl.trim());
  if (!m) { return undefined; }
  const chemin = (m[2] || '').replace(/\/+$/, '');
  return { hote: m[1], chemin };
}

/** Chemin server-relative (sans origine) d'une URL de drive (webUrl Graph). */
function cheminServerRelative(url: string): string {
  const m = /^https?:\/\/[^/]+(\/.*)$/.exec(url.trim());
  return (m ? m[1] : url).replace(/\/+$/, '');
}

/** Encode chaque segment d'un chemin (espaces, accents…) en préservant les « / ». */
function encoderChemin(chemin: string): string {
  return chemin.split('/').map(s => encodeURIComponent(s)).join('/');
}

/**
 * Décode UN segment de chemin, en tolérant un segment DÉJÀ en clair : `decodeURIComponent`
 * lève sur un « % » qui n'introduit pas un octet valide (ex. « 100% »), or un chemin issu des
 * props arrive en clair. On rend alors le segment inchangé plutôt que d'échouer.
 */
function decoderSegment(seg: string): string {
  try { return decodeURIComponent(seg); }
  catch { return seg; }
}

/** Segments DÉCODÉS d'un chemin server-relative (les vides — dont le trailing slash — sont ôtés). */
function segmentsDecodes(chemin: string): ReadonlyArray<string> {
  return chemin.split('/').filter(s => s.length > 0).map(decoderSegment);
}

/** `prefixe` est-il un préfixe (segment par segment) de `complet` ? */
function estPrefixeDeSegments(prefixe: ReadonlyArray<string>, complet: ReadonlyArray<string>): boolean {
  if (prefixe.length > complet.length) { return false; }
  for (let i = 0; i < prefixe.length; i++) {
    if (prefixe[i] !== complet[i]) { return false; }
  }
  return true;
}

/**
 * Calcule le chemin d'un fichier RELATIF à la racine de son drive porteur, en cherchant parmi
 * `drives` celui dont la racine préfixe l'URL server-relative du fichier.
 *
 * Le webUrl des drives revient de Graph PERCENT-ENCODÉ (« Documents%20partages ») alors que les
 * chemins des props arrivent EN CLAIR (espaces, accents, « & »). On compare donc des SEGMENTS
 * DÉCODÉS des deux côtés (insensible au trailing slash) ; le résiduel — en clair — est ré-encodé
 * segment par segment par `encoderChemin` avant l'appel `root:{chemin}:`.
 *
 * Retourne { driveId, cheminDansDrive } ou undefined si aucun drive ne porte le fichier.
 */
export function localiserDansDrive(
  drives: ReadonlyArray<{ readonly id: string; readonly webUrl: string }>,
  fichierServerRelative: string
): { readonly driveId: string; readonly cheminDansDrive: string } | undefined {
  const cibleSegs = segmentsDecodes(fichierServerRelative);
  // Le drive le plus SPÉCIFIQUE d'abord (racine la plus longue) — évite qu'un drive parent rafle.
  const candidats = drives
    .map(d => ({ id: d.id, segs: segmentsDecodes(cheminServerRelative(d.webUrl)) }))
    .filter(d => d.segs.length > 0 && estPrefixeDeSegments(d.segs, cibleSegs))
    .sort((a, b) => b.segs.length - a.segs.length);
  if (candidats.length === 0) { return undefined; }
  const c = candidats[0];
  const residuel = cibleSegs.slice(c.segs.length); // segments décodés restants (en clair)
  return { driveId: c.id, cheminDansDrive: residuel.length ? '/' + residuel.join('/') : '' };
}

/** Drive résolu (id + racine server-relative), une fois pour toutes les tables d'un même site. */
type Drive = { readonly id: string; readonly webUrl: string };

/**
 * Résout site → drives EN UN SEUL PASSAGE, en amont des lectures concurrentes (aucun état mutable
 * partagé après `await` : pas de course). Retourne la liste des drives, ou `undefined` si la
 * résolution échoue (site introuvable / drives illisibles).
 */
async function resoudreDrives(grapheGet: GrapheGet, siteUrl: string): Promise<ReadonlyArray<Drive> | undefined> {
  const hc = hoteEtCheminSite(siteUrl);
  if (!hc) { return undefined; }
  const site = await grapheGet(`/sites/${hc.hote}:${encoderChemin(hc.chemin)}?$select=id`);
  const siteId = site.ok && site.corps && typeof (site.corps as { id?: unknown }).id === 'string'
    ? (site.corps as { id: string }).id : undefined;
  if (!siteId) { return undefined; }
  const drivesRep = await grapheGet(`/sites/${siteId}/drives?$select=id,name,webUrl`);
  const value = drivesRep.ok && estColonnes(drivesRep.corps) ? drivesRep.corps.value : undefined;
  if (!value) { return undefined; }
  return value
    .map(d => ({ id: versTexte((d as { id?: unknown }).id), webUrl: versTexte((d as { webUrl?: unknown }).webUrl) }))
    .filter(d => d.id && d.webUrl);
}

/**
 * Résultat de lecture d'une table : lignes brutes + éventuelle anomalie (schéma cassé) + un état
 * d'accès (pour distinguer restreint/indisponible côté référentiel). Ne lève jamais. Ne MUTE rien
 * (les `drives` résolus sont passés en lecture seule → aucune course).
 */
interface LectureTable {
  readonly lignes: ReadonlyArray<Record<string, unknown>>;
  readonly anomalie?: AnomalieGabarit;
  readonly acces: EtatAcces;
}

async function lireTable(
  grapheGet: GrapheGet,
  drives: ReadonlyArray<Drive>,
  fichierServerRelative: string,
  libelleSource: string,
  table: string,
  entetesAttendus: ReadonlyArray<string>
): Promise<LectureTable> {
  const loc = localiserDansDrive(drives, fichierServerRelative);
  if (!loc) {
    return { lignes: [], acces: 'indisponible', anomalie: { source: libelleSource, raison: 'classeur hors des bibliothèques du site', cause: 'chemin hors des drives du site' } };
  }
  const chemin = `/drives/${loc.driveId}/root:${encoderChemin(loc.cheminDansDrive)}:/workbook/tables/${encodeURIComponent(table)}/columns`;
  const rep = await grapheGet(chemin);
  if (rep.status === 403 || rep.status === 404) {
    // Référentiel non visible pour cet utilisateur, ou classeur/table absent → restreint (non bloquant).
    return { lignes: [], acces: 'restreint' };
  }
  if (!rep.ok) {
    return { lignes: [], acces: 'indisponible', anomalie: { source: libelleSource, raison: `lecture de « ${table} » indisponible (HTTP ${rep.status})`, cause: `${table} : HTTP ${rep.status}` } };
  }
  const parsee = parserTableColonnes(rep.corps, entetesAttendus);
  if (parsee.entetesManquants.length > 0) {
    return { lignes: [], acces: 'accessible', anomalie: { source: libelleSource, raison: `table « ${table} » au schéma inattendu (en-têtes manquants : ${parsee.entetesManquants.join(', ')})`, cause: `${table} : en-têtes manquants ${parsee.entetesManquants.join(', ')}` } };
  }
  return { lignes: parsee.lignes, acces: 'accessible' };
}

// ---------------------------------------------------------------------------
// Orchestration de lecture — un gabarit (3 tables) et le référentiel (2 classeurs).
// Chaque anomalie est COLLECTÉE (jamais tue) et remontée à l'appelant (fraîcheur §3).
// ---------------------------------------------------------------------------
export interface ResultatContenus {
  readonly gabarits: ReadonlyArray<ContenuGabarit>;
  readonly referentiel?: ContenuReferentiel;
  readonly referentielEtat: EtatAcces;
  readonly anomalies: ReadonlyArray<AnomalieGabarit>;
}

export interface CibleGabarit { readonly codeMission: string; readonly url: string; }
export interface CiblesReferentiel { readonly ressources: string; readonly structure: string; }

/**
 * Lit le contenu des tables de chaque gabarit + du référentiel de coûts, via Graph (injecté).
 * `siteUrl` = site des gabarits (§5.2) ; `cibles` = URL server-relative de chaque gabarit
 * (découvertes par gabarits.ts) ; `referentiel` = chemins server-relative des 2 classeurs (props).
 * Ne lève jamais : toute défaillance devient anomalie (gabarit) ou état 'restreint'/'indisponible'
 * (référentiel).
 */
export async function lireContenus(
  grapheGet: GrapheGet,
  siteUrl: string,
  cibles: ReadonlyArray<CibleGabarit>,
  referentiel?: CiblesReferentiel
): Promise<ResultatContenus> {
  const anomalies: AnomalieGabarit[] = [];
  const gabarits: ContenuGabarit[] = [];

  // Résolution site → drives UNE SEULE FOIS, en amont (aucun état partagé muté en concurrence).
  const drives = await resoudreDrives(grapheGet, siteUrl);
  if (!drives) {
    // Résolution échouée : chaque gabarit devient une anomalie (jamais un zéro tu) ; référentiel
    // 'indisponible' s'il était demandé (échec réseau, pas un refus de droits).
    for (const cible of cibles) {
      anomalies.push({ source: `gabarit-${cible.codeMission}.xlsx`, raison: 'site/drive introuvable (résolution Graph échouée)', cause: 'résolution site→drive Graph échouée' });
      gabarits.push({ codeMission: cible.codeMission, affectations: [], imputations: [], echeancier: [] });
    }
    return { gabarits, referentiel: undefined, referentielEtat: referentiel ? 'indisponible' : 'restreint', anomalies };
  }

  for (const cible of cibles) {
    const src = `gabarit-${cible.codeMission}.xlsx`;
    const [aff, imp, ech] = await Promise.all([
      lireTable(grapheGet, drives, cible.url, src, TABLE_AFFECTATIONS, ENTETES_AFFECTATIONS),
      lireTable(grapheGet, drives, cible.url, src, TABLE_IMPUTATIONS, ENTETES_IMPUTATIONS),
      lireTable(grapheGet, drives, cible.url, src, TABLE_ECHEANCIER, ENTETES_ECHEANCIER)
    ]);
    for (const r of [aff, imp, ech]) { if (r.anomalie) { anomalies.push(r.anomalie); } }
    gabarits.push({
      codeMission: cible.codeMission,
      affectations: aff.lignes.map(mapAffectation),
      imputations: imp.lignes.map(mapImputation),
      echeancier: ech.lignes.map(mapEcheancier)
    });
  }

  // Référentiel de coûts : deux classeurs distincts (§5.3), audience restreinte.
  let contenuRef: ContenuReferentiel | undefined;
  let referentielEtat: EtatAcces = 'restreint';
  if (referentiel && referentiel.ressources && referentiel.structure) {
    const [res, str] = await Promise.all([
      lireTable(grapheGet, drives, referentiel.ressources, 'référentiel T_Ressources', TABLE_RESSOURCES, ENTETES_RESSOURCES),
      lireTable(grapheGet, drives, referentiel.structure, 'référentiel T_Structure', TABLE_STRUCTURE, ENTETES_STRUCTURE)
    ]);
    for (const r of [res, str]) { if (r.anomalie) { anomalies.push(r.anomalie); } }
    // Accès : accessible seulement si les DEUX classeurs sont lus ; 'indisponible' l'emporte sur
    // 'restreint' (un échec réseau n'est pas un refus de droits).
    if (res.acces === 'accessible' && str.acces === 'accessible') {
      referentielEtat = 'accessible';
      contenuRef = { ressources: res.lignes.map(mapRessource), structure: str.lignes.map(mapStructure) };
    } else if (res.acces === 'indisponible' || str.acces === 'indisponible') {
      referentielEtat = 'indisponible';
    } else {
      referentielEtat = 'restreint';
    }
  }

  return { gabarits, referentiel: contenuRef, referentielEtat, anomalies };
}
