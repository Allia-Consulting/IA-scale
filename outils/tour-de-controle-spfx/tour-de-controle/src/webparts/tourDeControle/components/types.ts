// Types partagés du cockpit — Tour de contrôle (T-0014).
//
// Portés ici (module partagé) pour que le rendu et le fournisseur de données
// réelles (listes-reelles.ts) parlent la même forme. Un « compteur »
// mime toujours une lecture de liste M365 (voir → creuser → agir) ; la source des
// valeurs est désormais le tenant, jamais des constantes.

export type Signal = 'info' | 'surveiller' | 'decision' | 'neutral';

export interface DetailItem {
  /** Libellé de la ligne. */
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
   * true si la ligne appelle une décision IRRÉVERSIBLE du manager. Alimente le
   * compteur d'en-tête — calculé, jamais codé en dur ailleurs. Indépendant de `signal`.
   */
  readonly requiresDecision?: boolean;
}

export interface Compteur {
  /** Identifiant unique — sert au dépli/repli du panneau détail. */
  readonly id: string;
  readonly libelle: string;
  /** Valeur affichée telle quelle (« 7 », « 0 », « — »). */
  readonly valeur: string;
  readonly items: ReadonlyArray<DetailItem>;
  /**
   * Note sobre affichée au-dessus du détail : vide assumé, « non câblé »
   * (liste absente), ou « lecture indisponible » (échec). JAMAIS un repli démo.
   */
  readonly note?: string;
}

export interface Zone {
  readonly compteurs: ReadonlyArray<Compteur>;
}

/**
 * Résultat d'une écriture guidée (symétrique de `Lecture` de listes-reelles.ts) :
 *  - ok           : l'écriture a abouti ;
 *  - refuse       : écriture interdite (403) — fail-VISIBLE, jamais silencieux ;
 *  - indisponible : tout autre échec (réseau, 4xx/5xx).
 * Ne porte jamais d'exception : le geste d'écriture ne casse pas le cockpit.
 */
export type Ecriture =
  | { readonly etat: 'ok' }
  | { readonly etat: 'refuse' }
  | { readonly etat: 'indisponible' };

/**
 * Compte les lignes appelant une décision irréversible, sur l'ensemble des zones.
 * Le compteur d'en-tête en découle (dérivé) — il n'est écrit nulle part en dur.
 * Sur données réelles vides, retourne 0 (honnête).
 */
export function compterDecisions(zones: ReadonlyArray<Zone>): number {
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
