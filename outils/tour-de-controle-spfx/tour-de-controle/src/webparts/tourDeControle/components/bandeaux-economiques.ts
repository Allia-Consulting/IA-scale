// Modèles de rendu des trois bandeaux économiques — logique PURE, sans dépendance SPFx.
//
// Cible : tour-de-controle.md v2.1 §3 (bandeaux 1 staffing, 4 rentabilité, 5 factures) et
// §4 (modèle économique distribué). Ces builders transforment l'état des sources
// (`EtatGabarits`, gabarits.ts) en structures d'affichage. Ils sont testables sans React.
//
// PÉRIMÈTRE (point 1 — états vides honnêtes) : AUCUN agrégat n'est calculé. Toute valeur
// économique est le placeholder « · » (jamais un zéro inventé, tour-de-controle.md §3).
// Le câblage des calculs réels (ouverture des classeurs, tables T_Affectations /
// T_Imputations / T_Echeancier, TJM, référentiel de coûts) est le point 2 — ces builders
// portent DÉJÀ la forme (12 mois, réalisé/prévisionnel, lignes CA/EBITDA, colonnes) que
// le point 2 remplira.

import type { EtatGabarits } from './gabarits';

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
// Bandeau 1 — Staffing (12 barres mensuelles, sélecteur d'année, réalisé/prévisionnel).
// ===========================================================================
export type RegimeMois = 'realise' | 'previsionnel';

export interface BarreStaffing {
  /** Index du mois (0 = janvier). */
  readonly moisIndex: number;
  readonly libelleMois: string;
  /** Effectif actif au sommet de la barre (« · » au point 1 — source Ressources-Profil au point 2). */
  readonly effectif: string;
  /** Pourcentage lisible DANS la barre (« · » au point 1). */
  readonly pct: string;
  /** Hauteur de remplissage 0–100 (0 au point 1 : barre vide, jamais un faux niveau). */
  readonly hauteurPct: number;
  /** Mois écoulé (réalisé) vs à venir (prévisionnel) — traitement visuel sobre. */
  readonly regime: RegimeMois;
}

export interface ModeleStaffing {
  readonly annee: number;
  readonly anneesDisponibles: ReadonlyArray<number>;
  readonly barres: ReadonlyArray<BarreStaffing>;
  /** true si aucun gabarit actif n'a été lu : chaque barre affiche « · ». */
  readonly aucunGabarit: boolean;
}

/** Années sélectionnables : [anneeCourante − 2 … anneeCourante + 2]. */
export function anneesSelectionnables(anneeCourante: number): ReadonlyArray<number> {
  const annees: number[] = [];
  for (let d = -AMPLITUDE_ANNEES; d <= AMPLITUDE_ANNEES; d++) {
    annees.push(anneeCourante + d);
  }
  return annees;
}

/**
 * Régime d'un mois de l'année affichée par rapport à « maintenant » :
 *  - année passée → tout réalisé ; année future → tout prévisionnel ;
 *  - année courante → mois strictement antérieurs au mois courant = réalisé (écoulés),
 *    le mois courant et les suivants = prévisionnel (à venir).
 */
export function regimeMois(
  moisIndex: number,
  annee: number,
  anneeCourante: number,
  moisCourant0: number
): RegimeMois {
  if (annee < anneeCourante) { return 'realise'; }
  if (annee > anneeCourante) { return 'previsionnel'; }
  return moisIndex < moisCourant0 ? 'realise' : 'previsionnel';
}

export function construireStaffing(
  etat: EtatGabarits,
  annee: number,
  anneeCourante: number,
  moisCourant0: number
): ModeleStaffing {
  const aucunGabarit = etat.gabarits.length === 0;
  const barres: BarreStaffing[] = MOIS_COURTS.map((libelleMois, moisIndex) => ({
    moisIndex,
    libelleMois,
    // Point 1 : aucun agrégat — l'effectif (Ressources-Profil, salariés hors ST) et le
    // taux (T_Affectations / T_Imputations) sont câblés au point 2. Ici, « · » honnête.
    effectif: PLACEHOLDER,
    pct: PLACEHOLDER,
    hauteurPct: 0,
    regime: regimeMois(moisIndex, annee, anneeCourante, moisCourant0)
  }));
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
  /** Douze cellules mensuelles. */
  readonly cellules: ReadonlyArray<CelluleRentabilite>;
  /** Cellule de la colonne Total. */
  readonly total: CelluleRentabilite;
  /** Mention discrète (ex. EBITDA sans référentiel accessible). */
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

export function construireRentabilite(etat: EtatGabarits, annee: number): ModeleRentabilite {
  // CA total : « · » partout au point 1 (Σ jours × TJM au point 2).
  const caTotal = ligneVide('CA total');
  // EBITDA : « · » partout ; la mention « référentiel à audience restreinte » explique
  // discrètement l'absence quand le référentiel de coûts n'est pas accessible à l'utilisateur.
  const ebitda = ligneVide('EBITDA', etat.referentielCoutsAccessible ? undefined : MENTION_REFERENTIEL_RESTREINT);
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
  /** Message d'état vide, sinon undefined si des lignes existent. */
  readonly messageVide?: string;
}

/**
 * Point 1 : les échéanciers ne sont pas encore ouverts (câblage T_Echeancier = point 2) —
 * la liste est donc vide. Le message distingue honnêtement les deux cas d'absence :
 *  - aucun gabarit actif lu → on ne peut RIEN affirmer sur les échéances ;
 *  - des gabarits existent mais aucune échéance « à émettre » n'en ressort.
 */
export function construireFactures(etat: EtatGabarits): ModeleFactures {
  const messageVide = etat.gabarits.length === 0
    ? 'Aucune facture à émettre — aucun gabarit actif lu'
    : 'Aucune facture à émettre.';
  return { lignes: [], messageVide };
}
