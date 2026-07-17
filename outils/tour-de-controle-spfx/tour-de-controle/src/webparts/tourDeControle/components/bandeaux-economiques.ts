// Modèles de rendu + CALCULS des trois bandeaux économiques — logique PURE, sans dépendance SPFx.
//
// Cible : tour-de-controle.md v2.1 §3 (bandeaux 1 staffing, 4 rentabilité, 5 factures) et
// modele-donnees.md §5.4 (formules des agrégats, appliquées STRICTEMENT). Ces builders
// transforment l'état des sources (`EtatGabarits` + contenus des tables lus par workbook-graph.ts)
// en structures d'affichage. Testables sans React ni réseau.
//
// HONNÊTETÉ (§3) : « · » partout où la donnée est ABSENTE (référentiel restreint, aucune ligne
// pour un mois…) — jamais un zéro inventé. Un zéro n'apparaît que lorsqu'il est CALCULÉ sur des
// données réellement présentes (ex. effectif salariés actifs = 0 quand le référentiel est lisible).
//
// TJM (décision gardien 2026-07-17, T-0035) : dérivé de l'ÉCHÉANCIER par mission —
//   TJM_mission = Σ MontantHT (T_Echeancier) ÷ Σ JoursPrevus (T_Affectations).
// Relation vérifiée sur le réel (épreuve T-0031 : 133 200 €/148 j = 900 ; 84 000 €/120 j = 700).

import type { EtatGabarits } from './gabarits';
import type { ContenuGabarit, LigneAffectation, LigneImputation } from './workbook-graph';
import { formaterEuros } from './pipe-recrutement';

/** Placeholder d'absence de donnée — « · », jamais « 0 » (tour-de-controle.md §3). */
export const PLACEHOLDER = '·';

/** Libellés courts des douze mois (fr) — index 0 = janvier. */
export const MOIS_COURTS: ReadonlyArray<string> = [
  'janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin',
  'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'
];

/** Amplitude du sélecteur d'année autour de l'année courante (±2, tour-de-controle.md §3). */
export const AMPLITUDE_ANNEES = 2;

// ===========================================================================
// Fonctions PURES d'agrégation (modele-donnees.md §5.4).
// ===========================================================================

/**
 * Jours ouvrés d'un mois = lundis→vendredis (fonction pure isolée, §5.4).
 * FÉRIÉS HORS PÉRIMÈTRE v1 (décision T-0035) : un jour férié tombant en semaine est compté comme
 * ouvré — un calendrier de fériés est une évolution ultérieure (aucun impact sur les totaux annuels
 * de jours, seulement sur le taux mensuel). Calcul en UTC (stable quel que soit le fuseau).
 */
export function joursOuvres(annee: number, moisIndex0: number): number {
  const dernierJour = new Date(Date.UTC(annee, moisIndex0 + 1, 0)).getUTCDate();
  let n = 0;
  for (let d = 1; d <= dernierJour; d++) {
    const jour = new Date(Date.UTC(annee, moisIndex0, d)).getUTCDay(); // 0 = dimanche, 6 = samedi
    if (jour !== 0 && jour !== 6) { n++; }
  }
  return n;
}

function memeMois(mois: Date | undefined, annee: number, moisIndex0: number): boolean {
  return !!mois && mois.getUTCFullYear() === annee && mois.getUTCMonth() === moisIndex0;
}

/** Σ JoursPrevus (T_Affectations) d'une mission — base du TJM et des totaux de charge. */
export function joursPrevusTotal(c: ContenuGabarit): number {
  return c.affectations.reduce((s, a) => s + (a.joursPrevus ?? 0), 0);
}

/** Σ JoursRealises (T_Imputations) d'une mission. */
export function joursRealisesTotal(c: ContenuGabarit): number {
  return c.imputations.reduce((s, i) => s + (i.joursRealises ?? 0), 0);
}

/**
 * TJM d'une mission = Σ MontantHT (échéancier) ÷ Σ JoursPrevus (affectations). `undefined` si la
 * dérivation est impossible (aucun jour prévu, ou échéancier vide) — jamais un TJM inventé.
 */
export function tjmParMission(c: ContenuGabarit): number | undefined {
  const jours = joursPrevusTotal(c);
  if (jours <= 0 || c.echeancier.length === 0) { return undefined; }
  const ca = c.echeancier.reduce((s, e) => s + (e.montantHT ?? 0), 0);
  return ca / jours;
}

/** CA budget d'une mission = TJM × Σ JoursPrevus (§5.4). `undefined` si TJM indérivable. */
export function caBudgetMission(c: ContenuGabarit): number | undefined {
  const tjm = tjmParMission(c);
  return tjm === undefined ? undefined : tjm * joursPrevusTotal(c);
}

/** CA réalisé d'une mission = TJM × Σ JoursRealises (§5.4). `undefined` si TJM indérivable. */
export function caRealiseMission(c: ContenuGabarit): number | undefined {
  const tjm = tjmParMission(c);
  return tjm === undefined ? undefined : tjm * joursRealisesTotal(c);
}

// ===========================================================================
// Bandeau 1 — Staffing (12 barres mensuelles, sélecteur d'année, réalisé/prévisionnel).
// ===========================================================================
export type RegimeMois = 'realise' | 'previsionnel';

export interface BarreStaffing {
  readonly moisIndex: number;
  readonly libelleMois: string;
  /** Effectif salariés ACTIFS au sommet de la barre (« · » si le référentiel n'est pas lisible). */
  readonly effectif: string;
  /** Taux moyen lisible DANS la barre (« · » si non calculable). */
  readonly pct: string;
  /** Hauteur de remplissage 0–100 (0 quand « · »). */
  readonly hauteurPct: number;
  readonly regime: RegimeMois;
}

export interface ModeleStaffing {
  readonly annee: number;
  readonly anneesDisponibles: ReadonlyArray<number>;
  readonly barres: ReadonlyArray<BarreStaffing>;
  /** true si aucun gabarit actif n'a été découvert. */
  readonly aucunGabarit: boolean;
}

/** Années sélectionnables : [anneeCourante − 2 … anneeCourante + 2]. */
export function anneesSelectionnables(anneeCourante: number): ReadonlyArray<number> {
  const annees: number[] = [];
  for (let d = -AMPLITUDE_ANNEES; d <= AMPLITUDE_ANNEES; d++) { annees.push(anneeCourante + d); }
  return annees;
}

/**
 * Régime d'un mois de l'année affichée par rapport à « maintenant » :
 *  - année passée → réalisé ; année future → prévisionnel ;
 *  - année courante → mois strictement antérieurs au mois courant = réalisé, sinon prévisionnel.
 */
export function regimeMois(moisIndex: number, annee: number, anneeCourante: number, moisCourant0: number): RegimeMois {
  if (annee < anneeCourante) { return 'realise'; }
  if (annee > anneeCourante) { return 'previsionnel'; }
  return moisIndex < moisCourant0 ? 'realise' : 'previsionnel';
}

/** Un poste du référentiel est-il un SALARIÉ (les sous-traitants sont exclus du staffing, §5.4) ? */
function estSalarie(type: string): boolean {
  return type.trim().toLowerCase().indexOf('salari') === 0; // « salarié » (accents/casse tolérés)
}

/** Le salarié est-il actif ce mois (DateEntree/DateSortie encadrant le mois) ? */
function estActifLeMois(dateEntree: Date | undefined, dateSortie: Date | undefined, annee: number, moisIndex0: number): boolean {
  const debut = Date.UTC(annee, moisIndex0, 1);
  const fin = Date.UTC(annee, moisIndex0 + 1, 0);
  if (dateEntree && dateEntree.getTime() > fin) { return false; }
  if (dateSortie && dateSortie.getTime() < debut) { return false; }
  return true;
}

/** Jours d'un salarié un mois donné, tous gabarits confondus, selon le régime. */
function joursSalarieMois(
  contenus: ReadonlyArray<ContenuGabarit>,
  ressource: string,
  annee: number,
  moisIndex0: number,
  regime: RegimeMois
): number {
  let s = 0;
  for (const c of contenus) {
    if (regime === 'realise') {
      for (const i of c.imputations) { if (i.ressource === ressource && memeMois(i.mois, annee, moisIndex0)) { s += i.joursRealises ?? 0; } }
    } else {
      for (const a of c.affectations) { if (a.ressource === ressource && memeMois(a.mois, annee, moisIndex0)) { s += a.joursPrevus ?? 0; } }
    }
  }
  return s;
}

function formaterPct(taux: number): string {
  return `${Math.round(taux * 100)} %`;
}

function bornerHauteur(x: number): number {
  return Math.max(0, Math.min(100, Math.round(x)));
}

export function construireStaffing(
  etat: EtatGabarits,
  annee: number,
  anneeCourante: number,
  moisCourant0: number
): ModeleStaffing {
  const aucunGabarit = etat.gabarits.length === 0;
  const contenus = etat.contenus;
  const ressources = etat.referentiel?.ressources;

  const barres: BarreStaffing[] = MOIS_COURTS.map((libelleMois, moisIndex) => {
    const regime = regimeMois(moisIndex, annee, anneeCourante, moisCourant0);
    // Sans référentiel (roster des salariés) OU sans contenus lus : « · » honnête —
    // impossible d'identifier les salariés actifs / de lire les jours (le staffing exclut les ST).
    if (!ressources || !contenus) {
      return { moisIndex, libelleMois, effectif: PLACEHOLDER, pct: PLACEHOLDER, hauteurPct: 0, regime };
    }
    const actifs = ressources.filter(r => estSalarie(r.type) && estActifLeMois(r.dateEntree, r.dateSortie, annee, moisIndex));
    if (actifs.length === 0) {
      // Référentiel lisible mais aucun salarié actif ce mois = FAIT réel → effectif 0 (honnête), taux « · ».
      return { moisIndex, libelleMois, effectif: '0', pct: PLACEHOLDER, hauteurPct: 0, regime };
    }
    const jo = joursOuvres(annee, moisIndex);
    const taux = actifs.map(r => (jo > 0 ? joursSalarieMois(contenus, r.ressource, annee, moisIndex, regime) / jo : 0));
    const moyenne = taux.reduce((a, b) => a + b, 0) / actifs.length;
    return { moisIndex, libelleMois, effectif: String(actifs.length), pct: formaterPct(moyenne), hauteurPct: bornerHauteur(moyenne * 100), regime };
  });

  return { annee, anneesDisponibles: anneesSelectionnables(anneeCourante), barres, aucunGabarit };
}

// ===========================================================================
// Bandeau 4 — Rentabilité (12 mois × (Budget | Réalisé) + Total ; lignes CA total, EBITDA).
// ===========================================================================
export interface CelluleRentabilite {
  readonly budget: string;
  readonly realise: string;
}

export interface LigneRentabilite {
  readonly libelle: string;
  readonly cellules: ReadonlyArray<CelluleRentabilite>;
  readonly total: CelluleRentabilite;
  readonly mention?: string;
}

export interface ModeleRentabilite {
  readonly annee: number;
  readonly mois: ReadonlyArray<string>;
  readonly lignes: ReadonlyArray<LigneRentabilite>;
}

/** Mention affichée sur la ligne EBITDA quand le référentiel de coûts n'est pas accessible. */
export const MENTION_REFERENTIEL_RESTREINT = 'référentiel à audience restreinte';

function celluleVide(): CelluleRentabilite {
  return { budget: PLACEHOLDER, realise: PLACEHOLDER };
}

function ligneVide(libelle: string, mention?: string): LigneRentabilite {
  const cellules: CelluleRentabilite[] = [];
  for (let i = 0; i < MOIS_COURTS.length; i++) { cellules.push(celluleVide()); }
  return { libelle, cellules, total: celluleVide(), mention };
}

/** Σ d'un champ de jours pour un mois donné + nombre de lignes concernées (présence de donnée). */
function sommeJoursMois(
  affectations: ReadonlyArray<LigneAffectation>,
  imputations: ReadonlyArray<LigneImputation>,
  annee: number,
  moisIndex0: number
): { readonly prevus: number; readonly prevusCount: number; readonly realises: number; readonly realisesCount: number } {
  let prevus = 0, prevusCount = 0, realises = 0, realisesCount = 0;
  for (const a of affectations) { if (memeMois(a.mois, annee, moisIndex0)) { prevus += a.joursPrevus ?? 0; prevusCount++; } }
  for (const i of imputations) { if (memeMois(i.mois, annee, moisIndex0)) { realises += i.joursRealises ?? 0; realisesCount++; } }
  return { prevus, prevusCount, realises, realisesCount };
}

/** Coût jour par ressource (mail), depuis le référentiel — pour l'EBITDA. */
function coutParRessource(etat: EtatGabarits): Map<string, number> {
  const m = new Map<string, number>();
  for (const r of etat.referentiel?.ressources ?? []) { if (r.coutJour !== undefined) { m.set(r.ressource, r.coutJour); } }
  return m;
}

/** Σ (jours × CoutJour) d'un mois, tous gabarits confondus, pour le régime demandé (budget/réalisé). */
function coutsMois(
  contenus: ReadonlyArray<ContenuGabarit>,
  couts: Map<string, number>,
  annee: number,
  moisIndex0: number,
  regime: 'budget' | 'realise'
): number {
  let s = 0;
  for (const c of contenus) {
    if (regime === 'budget') {
      for (const a of c.affectations) { if (memeMois(a.mois, annee, moisIndex0)) { s += (a.joursPrevus ?? 0) * (couts.get(a.ressource) ?? 0); } }
    } else {
      for (const i of c.imputations) { if (memeMois(i.mois, annee, moisIndex0)) { s += (i.joursRealises ?? 0) * (couts.get(i.ressource) ?? 0); } }
    }
  }
  return s;
}

/** Σ Montant (T_Structure) d'un mois. */
function structureMois(etat: EtatGabarits, annee: number, moisIndex0: number): number {
  let s = 0;
  for (const st of etat.referentiel?.structure ?? []) { if (memeMois(st.mois, annee, moisIndex0)) { s += st.montant ?? 0; } }
  return s;
}

export function construireRentabilite(etat: EtatGabarits, annee: number): ModeleRentabilite {
  const contenus = etat.contenus;
  const refAccessible = etat.referentielCoutsAccessible && !!etat.referentiel;

  // --- Ligne CA total (Σ jours × TJM par mois ; TJM dérivé de l'échéancier). N'a PAS besoin du référentiel. ---
  const caCells: CelluleRentabilite[] = [];
  let caBudTotal = 0, caBudAny = false, caRealTotal = 0, caRealAny = false;
  // Pré-calcul des CA budget/réalisé par mois (réutilisés par l'EBITDA).
  const caBudMois: Array<number | undefined> = [];
  const caRealMois: Array<number | undefined> = [];

  for (let m = 0; m < 12; m++) {
    let bud = 0, budAny = false, real = 0, realAny = false;
    if (contenus) {
      for (const c of contenus) {
        const tjm = tjmParMission(c);
        const j = sommeJoursMois(c.affectations, c.imputations, annee, m);
        if (j.prevusCount > 0) { budAny = true; if (tjm !== undefined) { bud += j.prevus * tjm; } }
        if (j.realisesCount > 0) { realAny = true; if (tjm !== undefined) { real += j.realises * tjm; } }
      }
    }
    caCells.push({ budget: budAny ? formaterEuros(bud) : PLACEHOLDER, realise: realAny ? formaterEuros(real) : PLACEHOLDER });
    caBudMois.push(budAny ? bud : undefined);
    caRealMois.push(realAny ? real : undefined);
    if (budAny) { caBudTotal += bud; caBudAny = true; }
    if (realAny) { caRealTotal += real; caRealAny = true; }
  }
  const caTotal: LigneRentabilite = {
    libelle: 'CA total',
    cellules: caCells,
    total: { budget: caBudAny ? formaterEuros(caBudTotal) : PLACEHOLDER, realise: caRealAny ? formaterEuros(caRealTotal) : PLACEHOLDER }
  };

  // --- Ligne EBITDA = CA − (jours × CoutJour) − T_Structure du mois (§5.4). Requiert le référentiel. ---
  let ebitda: LigneRentabilite;
  if (!refAccessible || !contenus) {
    // Référentiel non accessible (ou aucun contenu) : « · » + mention discrète (jamais un zéro inventé).
    ebitda = ligneVide('EBITDA', etat.referentielCoutsAccessible ? undefined : MENTION_REFERENTIEL_RESTREINT);
  } else {
    const couts = coutParRessource(etat);
    const cells: CelluleRentabilite[] = [];
    let ebBudTotal = 0, ebBudAny = false, ebRealTotal = 0, ebRealAny = false;
    for (let m = 0; m < 12; m++) {
      const struct = structureMois(etat, annee, m);
      let budStr = PLACEHOLDER, realStr = PLACEHOLDER;
      if (caBudMois[m] !== undefined) {
        const eb = (caBudMois[m] as number) - coutsMois(contenus, couts, annee, m, 'budget') - struct;
        budStr = formaterEuros(eb); ebBudTotal += eb; ebBudAny = true;
      }
      if (caRealMois[m] !== undefined) {
        const eb = (caRealMois[m] as number) - coutsMois(contenus, couts, annee, m, 'realise') - struct;
        realStr = formaterEuros(eb); ebRealTotal += eb; ebRealAny = true;
      }
      cells.push({ budget: budStr, realise: realStr });
    }
    ebitda = {
      libelle: 'EBITDA',
      cellules: cells,
      total: { budget: ebBudAny ? formaterEuros(ebBudTotal) : PLACEHOLDER, realise: ebRealAny ? formaterEuros(ebRealTotal) : PLACEHOLDER }
    };
  }

  return { annee, mois: MOIS_COURTS, lignes: [caTotal, ebitda] };
}

// ===========================================================================
// Bandeau 5 — Factures à émettre (échéanciers des gabarits actifs, statut « à émettre »).
// ===========================================================================
export interface LigneFacture {
  readonly numFacture: string;
  readonly codeMission: string;
  readonly montant: string;
  readonly echeance: string;
  /** Lien vers le PDF de la facture dans le dépôt Teams (T_Echeancier.LienFacture). */
  readonly lienPdf?: string;
}

export interface ModeleFactures {
  readonly lignes: ReadonlyArray<LigneFacture>;
  readonly messageVide?: string;
}

/** Statut « à émettre » (accents/casse tolérés ; les statuts sont normalisés accentués au gabarit, §4 skill). */
function estAEmettre(statut: string): boolean {
  return statut.trim().toLowerCase() === 'à émettre';
}

/** Date courte JJ/MM/AAAA (UTC — cohérent avec la normalisation des dates de lecture). */
function formaterDateCourte(d: Date): string {
  const pad = (n: number): string => (n < 10 ? `0${n}` : String(n));
  return `${pad(d.getUTCDate())}/${pad(d.getUTCMonth() + 1)}/${d.getUTCFullYear()}`;
}

/**
 * Lignes T_Echeancier au statut « à émettre », tous gabarits confondus. Message d'état vide
 * honnête : distingue « aucun gabarit actif lu » (rien à affirmer) de « aucune échéance à émettre »
 * (des gabarits existent, mais rien n'est dû).
 */
export function construireFactures(etat: EtatGabarits): ModeleFactures {
  const contenus = etat.contenus;
  const messageVide = etat.gabarits.length === 0
    ? 'Aucune facture à émettre — aucun gabarit actif lu'
    : 'Aucune facture à émettre.';
  if (!contenus) { return { lignes: [], messageVide }; }

  const lignes: LigneFacture[] = [];
  for (const c of contenus) {
    for (const e of c.echeancier) {
      if (!estAEmettre(e.statut)) { continue; }
      lignes.push({
        numFacture: e.numFacture || PLACEHOLDER,
        codeMission: e.codeMission || c.codeMission,
        montant: e.montantHT !== undefined ? formaterEuros(e.montantHT) : PLACEHOLDER,
        echeance: e.echeance ? formaterDateCourte(e.echeance) : PLACEHOLDER,
        lienPdf: e.lienFacture || undefined
      });
    }
  }
  if (lignes.length === 0) { return { lignes: [], messageVide }; }
  return { lignes };
}
