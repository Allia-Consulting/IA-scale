// Données de démonstration — Tour de contrôle (étape 2, T-0014).
//
// AUCUN chiffre réel ici : tout est fictif et le cockpit l'affiche comme tel
// (bandeau global + tag par zone). Les structures miment la forme des futures
// listes M365 (un item ≈ une ligne de liste) pour que le câblage ultérieur soit
// trivial : remplacer ces constantes par une lecture de liste, sans toucher l'UI.

export type Signal = 'info' | 'surveiller' | 'decision' | 'neutral';

export interface DetailItem {
  /** Libellé de la ligne (ex. « Acme Corp — refonte SI »). */
  readonly libelle: string;
  /** État court affiché à droite (étape, statut, ou valeur). */
  readonly statut: string;
  /**
   * Sémantique de la pastille :
   *  - info       : informatif/structurel (bleu) ;
   *  - surveiller : signal « à surveiller » (ambre, rare) ;
   *  - decision   : signal « ta décision » (ambre, rare) ;
   *  - neutral    : pas de pastille, texte sobre (métadonnée ou valeur).
   */
  readonly signal: Signal;
  /**
   * true si la ligne appelle une décision IRRÉVERSIBLE du manager (relecture
   * d'une proposition externe, décision de recrutement). Alimente le compteur
   * d'en-tête — calculé, jamais codé en dur ailleurs. Indépendant de `signal`.
   */
  readonly requiresDecision?: boolean;
}

export interface Compteur {
  /** Identifiant unique — sert au dépli/repli du panneau détail. */
  readonly id: string;
  readonly libelle: string;
  /** Valeur affichée telle quelle (string : « 7 », « 34% », « 1 »). */
  readonly valeur: string;
  readonly items: ReadonlyArray<DetailItem>;
}

export interface ZoneDemo {
  readonly compteurs: ReadonlyArray<Compteur>;
}

export const pipeCommercial: ZoneDemo = {
  compteurs: [
    {
      id: 'pipe-oppo',
      libelle: 'Opportunités',
      valeur: '7',
      items: [
        { libelle: 'Acme Corp — refonte SI', statut: 'qualifiée', signal: 'info' },
        { libelle: 'Banque Helios — cost analysis', statut: 'à relancer', signal: 'surveiller' },
        { libelle: 'Groupe Vela — TOM', statut: 'proposition envoyée', signal: 'info' }
      ]
    },
    {
      id: 'pipe-prop',
      libelle: 'Propositions à relire',
      valeur: '2',
      items: [
        { libelle: 'Acme Corp — proposition v2', statut: 'reçue il y a 2 j', signal: 'neutral', requiresDecision: true },
        { libelle: 'Groupe Vela — kickoff deck', statut: 'reçue hier', signal: 'neutral', requiresDecision: true }
      ]
    },
    {
      id: 'pipe-conv',
      libelle: 'Conversion',
      valeur: '34%',
      items: [
        { libelle: 'Opportunités gagnées (trim.)', statut: '4 / 12', signal: 'neutral' },
        { libelle: 'Délai moyen de cycle', statut: '38 j', signal: 'neutral' }
      ]
    }
  ]
};

export const recrutement: ZoneDemo = {
  compteurs: [
    {
      id: 'rec-cand',
      libelle: 'Candidats actifs',
      valeur: '5',
      items: [
        { libelle: 'C-021 — Consultant Senior', statut: 'E2', signal: 'info' },
        { libelle: 'C-022 — Manager', statut: 'E1', signal: 'info' },
        { libelle: 'C-019 — Consultant', statut: 'Proposition', signal: 'info' }
      ]
    },
    {
      id: 'rec-synth',
      libelle: 'Synthèses à valider',
      valeur: '3',
      items: [
        { libelle: 'C-021-E2 — en Zone-de-proposition', statut: 'à valider', signal: 'neutral' },
        { libelle: 'C-022-E1 — en Zone-de-proposition', statut: 'à valider', signal: 'neutral' },
        { libelle: 'C-018-E3 — en Zone-de-proposition', statut: 'à valider', signal: 'neutral' }
      ]
    },
    {
      id: 'rec-dec',
      libelle: 'Décisions en attente',
      valeur: '1',
      items: [
        { libelle: 'C-019 — décision finale', statut: 'ta décision', signal: 'decision', requiresDecision: true }
      ]
    }
  ]
};

/**
 * Compte les lignes appelant une décision irréversible, sur l'ensemble des
 * zones de démonstration. Le compteur d'en-tête en découle (dérivé) — il n'est
 * écrit nulle part en dur.
 */
export function compterDecisions(zones: ReadonlyArray<ZoneDemo>): number {
  return zones.reduce(
    (total, zone) =>
      total +
      zone.compteurs.reduce(
        (sous, compteur) => sous + compteur.items.filter(item => item.requiresDecision === true).length,
        0
      ),
    0
  );
}

// ── Suivi par étape (T-0013-b) ───────────────────────────────────────────────
// Enrichissement du cockpit : on suit la trajectoire d'un candidat le long du
// pipeline canonique du modele-donnees.md. Lecture seule, valeurs FICTIVES.

/** Pipeline canonique figé — ordre du modele-donnees.md (entité Candidat). */
export const ETAPES_PIPELINE = ['E1', 'E2', 'E3', 'Proposition', 'Acceptée', 'Refusée'] as const;
export type EtapePipeline = typeof ETAPES_PIPELINE[number];

export interface SuiviCandidat {
  /** Identifiant stable (ex. 'C-021'). */
  readonly id: string;
  /** Grade visé (ex. 'Consultant Senior'). */
  readonly grade: string;
  /** Position actuelle dans le pipeline. */
  readonly etapeCourante: EtapePipeline;
  /** Dernier interviewer / owner d'action — point d'ancrage de la sous-capacité 1b. */
  readonly responsableAction: string;
}

export interface SuiviDemo {
  readonly candidats: ReadonlyArray<SuiviCandidat>;
}

/**
 * Cohérent avec les candidats déjà présents dans `recrutement` (C-021, C-022,
 * C-019) ; complété pour atteindre les 5 « actifs » annoncés par le compteur
 * existant. Toutes les valeurs sont FICTIVES. C-020 illustre l'étape terminale.
 */
export const suiviCandidats: SuiviDemo = {
  candidats: [
    { id: 'C-021', grade: 'Consultant Senior', etapeCourante: 'E2', responsableAction: 'A. Martin' },
    { id: 'C-022', grade: 'Manager', etapeCourante: 'E1', responsableAction: 'A. Martin' },
    { id: 'C-019', grade: 'Consultant', etapeCourante: 'Proposition', responsableAction: 'C. Dubois' },
    { id: 'C-023', grade: 'Consultant Senior', etapeCourante: 'E3', responsableAction: 'C. Dubois' },
    { id: 'C-020', grade: 'Consultant', etapeCourante: 'Refusée', responsableAction: 'A. Martin' }
  ]
};

/** État d'un jalon vis-à-vis de la position courante du candidat. */
export type AvancementJalon = 'franchi' | 'courant' | 'a_venir';

/**
 * Trajectoire d'un candidat le long de ETAPES_PIPELINE : pour chaque étape, dit
 * si elle est franchie, courante ou à venir. Calcul par index, jamais codé en
 * dur. Cas terminal « Refusée » : c'est l'étape courante (terminale) ; les
 * étapes E1..Proposition sont marquées selon leur position réelle — on n'invente
 * aucun jalon franchi au-delà du réel, et « Acceptée » (issue alternative) reste
 * « à venir » puisqu'elle n'a pas eu lieu.
 */
export function avancement(
  etape: EtapePipeline
): ReadonlyArray<{ etape: EtapePipeline; etat: AvancementJalon }> {
  // Issues terminales alternatives : un candidat n'en franchit qu'une seule.
  const TERMINALES: ReadonlyArray<EtapePipeline> = ['Acceptée', 'Refusée'];
  const courantIdx = ETAPES_PIPELINE.indexOf(etape);
  return ETAPES_PIPELINE.map(e => {
    const idx = ETAPES_PIPELINE.indexOf(e);
    let etat: AvancementJalon;
    if (idx === courantIdx) {
      // L'étape courante (y compris une terminale comme « Refusée »).
      etat = 'courant';
    } else if (TERMINALES.indexOf(e) !== -1) {
      // L'autre issue terminale n'a pas eu lieu — jamais « franchie ».
      etat = 'a_venir';
    } else if (idx < courantIdx) {
      etat = 'franchi';
    } else {
      etat = 'a_venir';
    }
    return { etape: e, etat };
  });
}
