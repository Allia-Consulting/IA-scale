// Couche de découverte des gabarits de pilotage actifs — logique PURE, sans dépendance SPFx.
//
// Miroir de pipe-recrutement.ts / kpi-organisation.ts : ce module CONNAÎT la convention de
// dépôt (modele-donnees.md §5.2 / §5.5) et CLASSE des fichiers déjà listés ; il n'ouvre aucun
// canal réseau. La lecture réelle (REST cross-site sous l'identité de l'utilisateur, SSO,
// zéro secret, aucune élévation) est INJECTÉE par listes-reelles.ts via les primitives
// `LecteurDossier` / `SondeReferentiel` — exactement le patron `Ecrivain` du bandeau pipe.
// Isolé de React et de `@microsoft/sp-http` à dessein : le rendu et les tests unitaires le
// consomment sans charger le runtime du web part.
//
// PÉRIMÈTRE (point 1 — états vides honnêtes) : ce module expose la PRÉSENCE/ABSENCE des
// sources (gabarits actifs, référentiel de coûts), leur fraîcheur et leurs anomalies. Il ne
// calcule AUCUN agrégat économique — le câblage des calculs (ouverture des classeurs,
// tables T_Affectations / T_Imputations / T_Echeancier, référentiel de coûts) est le point 2.

// ---------------------------------------------------------------------------
// Convention de dépôt — modele-donnees.md §5.2 / §5.5 (fait foi).
// ---------------------------------------------------------------------------
/** Dossier racine des gabarits ACTIFS (bibliothèque « Documents », site Contrats et administratif). §5.2 */
export const DOSSIER_GABARITS_ACTIFS = '06 - Gabarit ERP';
/** Fichier souche vierge — jamais un gabarit de mission (exclu de la découverte). §5.2 */
export const FICHIER_SOUCHE_VIERGE = 'gabarit-pilotage-mission.xlsx';
/** Sous-dossier d'archivage des gabarits périmés — jamais un gabarit actif. §5.2 */
export const SOUS_DOSSIER_ARCHIVE = '00 - Old';
/**
 * Nom d'un gabarit actif : `gabarit-<CodeMission>.xlsx` (modele-donnees.md §5.2).
 * La souche `gabarit-pilotage-mission.xlsx` matcherait aussi ce motif — elle est exclue
 * AVANT le test par comparaison exacte au nom de souche.
 */
const RE_GABARIT = /^gabarit-(.+)\.xlsx$/i;

// ---------------------------------------------------------------------------
// Primitives INJECTÉES (implémentées par listes-reelles.ts, liées à `sp`).
// ---------------------------------------------------------------------------
/** Un fichier listé dans un dossier SharePoint (sous-ensemble des champs sélectionnés). */
export interface FichierDossier {
  readonly nom: string;
  /** URL (server-relative) du fichier — pointe vers son dépôt réel. */
  readonly url: string;
  /** Horodatage de dernière modification côté SharePoint (ISO), si connu. */
  readonly modifieLe?: string;
}

/**
 * Résultat d'une lecture de dossier. Ne lève JAMAIS (symétrique de `Lecture` de
 * listes-reelles.ts) :
 *  - ok           : dossier lu (liste éventuellement vide — vide assumé, honnête) ;
 *  - non_cable    : dossier non configuré / 404 — état LÉGITIME (pas une anomalie) ;
 *  - indisponible : échec réseau/serveur — signalé comme anomalie (jamais ignoré).
 */
export type ResultatDossier =
  | { readonly etat: 'ok'; readonly fichiers: ReadonlyArray<FichierDossier> }
  | { readonly etat: 'non_cable' }
  | { readonly etat: 'indisponible' };

/** Liste les fichiers du dossier des gabarits actifs (`06 - Gabarit ERP`). */
export type LecteurDossier = () => Promise<ResultatDossier>;

/**
 * État d'accès au référentiel de coûts (audience restreinte, §5.3) :
 *  - accessible : lu — les coûts pourront être joints au point 2 ;
 *  - restreint  : 403/404 — état LÉGITIME pour la plupart des collaborateurs (flag false,
 *                 jamais une erreur bloquante) ;
 *  - indisponible : échec réseau/serveur.
 */
export type EtatAcces = 'accessible' | 'restreint' | 'indisponible';

/** Sonde d'accessibilité du référentiel de coûts, sous l'identité de l'utilisateur. */
export type SondeReferentiel = () => Promise<EtatAcces>;

// ---------------------------------------------------------------------------
// Résultat de la découverte.
// ---------------------------------------------------------------------------
export interface GabaritActif {
  /** CodeMission stable, porté par le nom `gabarit-<CodeMission>.xlsx`. */
  readonly codeMission: string;
  /** URL du gabarit dans son dépôt réel (`06 - Gabarit ERP`). */
  readonly url: string;
  /** Moment où le cockpit a lu ce gabarit (fraîcheur), rendu lisible. */
  readonly derniereLecture: string;
  /** Dernière modification SharePoint (ISO), si connue — informatif. */
  readonly modifieLe?: string;
}

export interface AnomalieGabarit {
  /** Nom du fichier ou libellé de la source en anomalie. */
  readonly source: string;
  /** Raison lisible — signalée, jamais tue. */
  readonly raison: string;
}

export interface EtatGabarits {
  /** Gabarits de pilotage ACTIFS découverts (racine de `06 - Gabarit ERP`). */
  readonly gabarits: ReadonlyArray<GabaritActif>;
  /** Anomalies signalées (source inaccessible, nom non conforme…). */
  readonly anomalies: ReadonlyArray<AnomalieGabarit>;
  /** État de la lecture du dossier des gabarits (fail-visible). */
  readonly source: 'ok' | 'non_cable' | 'indisponible';
  /** Moment de la lecture, rendu lisible (« JJ/MM/AAAA à HH:MM »). */
  readonly luLe: string;
  /** true ssi le référentiel de coûts est accessible à cet utilisateur. */
  readonly referentielCoutsAccessible: boolean;
  /** État détaillé d'accès au référentiel (pour la mention discrète du bandeau 4). */
  readonly referentielEtat: EtatAcces;
}

// ---------------------------------------------------------------------------
// Horodatage lisible — local (jamais Intl : locale ICU non garantie dans le bundle,
// cf. formaterEuros). Zéro-remplissage à 2 chiffres sans padStart (hors lib ES2017).
// ---------------------------------------------------------------------------
export function formaterHorodatage(d: Date): string {
  const pad = (n: number): string => (n < 10 ? `0${n}` : String(n));
  const date = `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
  const heure = `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  return `${date} à ${heure}`;
}

// ---------------------------------------------------------------------------
// Classement PUR des fichiers de la racine `06 - Gabarit ERP`.
//
// La racine ne doit contenir QUE des gabarits actifs + la souche vierge (§5.2 :
// « ne garder à la racine que les gabarits actifs »). Le sous-dossier `00 - Old`
// n'apparaît pas ici (les dossiers ne sont pas listés comme fichiers). Tout écart
// est signalé comme anomalie, jamais ignoré silencieusement.
// ---------------------------------------------------------------------------
export interface Classement {
  readonly gabarits: ReadonlyArray<GabaritActif>;
  readonly anomalies: ReadonlyArray<AnomalieGabarit>;
}

export function classerFichiersGabarits(
  fichiers: ReadonlyArray<FichierDossier>,
  luLe: string
): Classement {
  const gabarits: GabaritActif[] = [];
  const anomalies: AnomalieGabarit[] = [];
  for (const f of fichiers) {
    // Souche vierge : ni gabarit de mission, ni anomalie — exclue en silence.
    if (f.nom === FICHIER_SOUCHE_VIERGE) { continue; }
    const m = RE_GABARIT.exec(f.nom);
    if (!m) {
      // Fichier étranger à la racine des gabarits actifs — signalé (jamais tu).
      anomalies.push({ source: f.nom, raison: 'fichier non conforme à la racine des gabarits actifs' });
      continue;
    }
    const codeMission = m[1].trim();
    if (!codeMission) {
      anomalies.push({ source: f.nom, raison: 'nom de gabarit sans CodeMission' });
      continue;
    }
    gabarits.push({ codeMission, url: f.url, derniereLecture: luLe, modifieLe: f.modifieLe });
  }
  return { gabarits, anomalies };
}

// ---------------------------------------------------------------------------
// Orchestration — PURE au regard de SPFx (ne dépend que des primitives injectées).
// ---------------------------------------------------------------------------
export async function decouvrirGabarits(
  lireDossier: LecteurDossier,
  sonderReferentiel: SondeReferentiel,
  maintenant: Date
): Promise<EtatGabarits> {
  const luLe = formaterHorodatage(maintenant);

  const [dossier, refEtat] = await Promise.all([lireDossier(), sonderReferentiel()]);

  let gabarits: ReadonlyArray<GabaritActif> = [];
  let anomalies: ReadonlyArray<AnomalieGabarit> = [];
  let source: EtatGabarits['source'];
  if (dossier.etat === 'ok') {
    const classement = classerFichiersGabarits(dossier.fichiers, luLe);
    gabarits = classement.gabarits;
    anomalies = classement.anomalies;
    source = 'ok';
  } else if (dossier.etat === 'non_cable') {
    // Non configuré : état légitime (le gardien câble les coordonnées au point 2).
    source = 'non_cable';
  } else {
    // Échec de lecture : le dossier attendu est inaccessible → anomalie explicite.
    source = 'indisponible';
    anomalies = [{ source: DOSSIER_GABARITS_ACTIFS, raison: 'dossier des gabarits inaccessible' }];
  }

  return {
    gabarits,
    anomalies,
    source,
    luLe,
    referentielCoutsAccessible: refEtat === 'accessible',
    referentielEtat: refEtat
  };
}

// ---------------------------------------------------------------------------
// Bandeau de fraîcheur commun (tour-de-controle.md §3 — honnêteté des données).
// « lu le J à H » + « N gabarit(s) en anomalie : M-XXX, … » le cas échéant.
// ---------------------------------------------------------------------------
export interface Fraicheur {
  readonly luLe: string;
  /** Phrase d'anomalies, ou undefined si aucune (jamais « 0 anomalie » superflu). */
  readonly anomalies?: string;
}

export function formaterFraicheur(etat: EtatGabarits): Fraicheur {
  const n = etat.anomalies.length;
  if (n === 0) {
    return { luLe: etat.luLe };
  }
  const liste = etat.anomalies.map(a => a.source).join(', ');
  const mot = n > 1 ? 'gabarits en anomalie' : 'gabarit en anomalie';
  return { luLe: etat.luLe, anomalies: `${n} ${mot} : ${liste}` };
}
