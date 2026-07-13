// Indicateurs d'organisation — logique PURE, sans aucune dépendance SPFx (unit-testable).
//
// Dernier maillon de la Phase 2 (T-0020-d) : la mesure de valeur organisationnelle.
// Les DÉFINITIONS des 3 KPI sont FIGÉES (décision gardien/architecte) — ce module ne
// fait que les calculer sur des lignes déjà lues ; il n'ouvre aucun canal de données
// (le seul canal d'accès reste `lireListe` de listes-reelles.ts, réutilisé — T-0014).
//
// Isolé des types SPFx et de React à dessein : le rendu et les tests unitaires
// consomment ces fonctions pures sans charger le contexte du web part.

/** Une ligne de liste lue (sous-ensemble des champs sélectionnés). */
export type Ligne = Record<string, unknown>;

/** Nom interne EXACT (Graph) de la colonne de statut de la Liste « Missions ». */
export const COLONNE_STATUT_MISSION = 'EnCours_x002f_Termin_x00e9_e_x00';
/** Valeur de statut « active » d'une mission (modele-donnees.md ; observée au tenant). */
export const STATUT_MISSION_ACTIVE = 'En cours';

function lireCreated(l: Ligne): Date | undefined {
  const v = l.Created;
  if (typeof v !== 'string' || !v) { return undefined; }
  const d = new Date(v);
  return isNaN(d.getTime()) ? undefined : d;
}

function lireTitre(l: Ligne): string {
  return typeof l.Title === 'string' ? l.Title : '';
}

// ---------------------------------------------------------------------------
// KPI 1 — « Missions actives » : count Liste Missions où statut == "En cours".
// ---------------------------------------------------------------------------
export function compterMissionsActives(missions: ReadonlyArray<Ligne>): number {
  return missions.filter(m => m[COLONNE_STATUT_MISSION] === STATUT_MISSION_ACTIVE).length;
}

// ---------------------------------------------------------------------------
// KPI 2 — « Dérivés promus (7 jours) » : somme des items créés depuis 7 jours
// glissants dans Missions + Imputations + CRM.
//
// PROXY EXACT — et non approximatif : le verrou serveur du connecteur MCP Graph
// n'autorise l'écriture agent QUE dans la Zone-de-proposition (garde-fou structurel,
// modele-donnees.md §3/§4). Aucun agent ne peut donc créer un item dans une liste
// SOURCE (Missions / Imputations / CRM). Toute création récente dans une liste source
// est par construction une PROMOTION opérée par un humain (le gardien). Compter les
// créations récentes des sources = compter les dérivés promus. (Fenêtre = 7 jours
// glissants ; on lit `Created` natif et on filtre côté client — jamais de $filter
// serveur sur colonne non indexée : 400 non déterministe, leçon T-0013-d.)
// ---------------------------------------------------------------------------
export function compterCreesDepuis(
  lignes: ReadonlyArray<Ligne>,
  maintenant: Date,
  joursGlissants = 7
): number {
  const seuil = maintenant.getTime() - joursGlissants * 24 * 60 * 60 * 1000;
  return lignes.filter(l => {
    const c = lireCreated(l);
    return c !== undefined && c.getTime() >= seuil;
  }).length;
}

// ---------------------------------------------------------------------------
// KPI 3 — « Délai brief→kick-off » : dans la Zone-de-proposition, apparier
// BRIEF-<n> et KICKOFF-<n>-* par <n> (code mission) via Title ;
// Δ = Created(KICKOFF) − Created(BRIEF). On affiche le dernier Δ et, si plusieurs
// paires, la moyenne.
// ---------------------------------------------------------------------------
export interface PaireBriefKickoff {
  /** Code mission <n> (clé d'appariement). */
  readonly n: string;
  readonly briefCreated: Date;
  readonly kickoffCreated: Date;
  /** Δ en secondes = Created(KICKOFF) − Created(BRIEF). */
  readonly deltaSecondes: number;
}

const RE_BRIEF = /^BRIEF-(\d+)$/;
const RE_KICKOFF = /^KICKOFF-(\d+)(?:-.*)?$/;

/**
 * Apparie BRIEF-<n> ↔ KICKOFF-<n>-* par <n>. Ne retient qu'une paire complète.
 * Trié par Created(KICKOFF) croissant : le DERNIER élément est le plus récent.
 */
export function apparierBriefKickoff(lignes: ReadonlyArray<Ligne>): ReadonlyArray<PaireBriefKickoff> {
  const briefs = new Map<string, Date>();
  const kickoffs = new Map<string, Date>();
  for (const l of lignes) {
    const created = lireCreated(l);
    if (!created) { continue; }
    const titre = lireTitre(l);
    const mb = RE_BRIEF.exec(titre);
    if (mb) { briefs.set(mb[1], created); continue; }
    const mk = RE_KICKOFF.exec(titre);
    if (mk) { kickoffs.set(mk[1], created); }
  }
  const paires: PaireBriefKickoff[] = [];
  briefs.forEach((briefCreated, n) => {
    const kickoffCreated = kickoffs.get(n);
    if (!kickoffCreated) { return; }
    const deltaSecondes = Math.round((kickoffCreated.getTime() - briefCreated.getTime()) / 1000);
    paires.push({ n, briefCreated, kickoffCreated, deltaSecondes });
  });
  return paires.sort((a, b) => a.kickoffCreated.getTime() - b.kickoffCreated.getTime());
}

/** Moyenne (arrondie) des Δ d'une liste de paires ; 0 si aucune paire. */
export function moyenneDeltas(paires: ReadonlyArray<PaireBriefKickoff>): number {
  if (paires.length === 0) { return 0; }
  const somme = paires.reduce((t, p) => t + p.deltaSecondes, 0);
  return Math.round(somme / paires.length);
}

/**
 * Format lisible d'une durée en secondes : « 42 s », « 3 min 07 s », « 7 h 16 min ».
 * Secondes zéro-remplies à 2 chiffres dans le palier minutes (ex. « 3 min 07 s »).
 */
export function formaterDuree(secondes: number): string {
  const s = Math.max(0, Math.round(secondes));
  // Zéro-remplissage à 2 chiffres sans padStart (hors lib ES2017 du projet).
  const pad = (n: number): string => (n < 10 ? `0${n}` : String(n));
  if (s < 60) { return `${s} s`; }
  if (s < 3600) {
    return `${Math.floor(s / 60)} min ${pad(s % 60)} s`;
  }
  const h = Math.floor(s / 3600);
  const min = Math.floor((s % 3600) / 60);
  return `${h} h ${pad(min)} min`;
}
