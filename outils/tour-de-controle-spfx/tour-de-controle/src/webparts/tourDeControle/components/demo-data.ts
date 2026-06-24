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
