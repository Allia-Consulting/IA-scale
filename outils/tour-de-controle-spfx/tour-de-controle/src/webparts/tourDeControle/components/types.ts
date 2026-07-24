// Types partagés du cockpit — Tour de contrôle (T-0014).
//
// Portés ici (module partagé) pour que le rendu et le fournisseur de données
// réelles (listes-reelles.ts) parlent la même forme. Un « compteur »
// mime toujours une lecture de liste M365 (voir → creuser → agir) ; la source des
// valeurs est désormais le tenant, jamais des constantes.

import type { OpportuniteLigne, CandidatLigne } from './pipe-recrutement';

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
 * Option de rattachement au compte pour le formulaire « nouvelle opportunité ».
 * `id` = Id numérique de l'item Comptes (valeur écrite dans le lookup `CompteId`) ;
 * `libelle` = NomCompte, avec repli sur Title.
 */
export interface CompteOption {
  readonly id: number;
  readonly libelle: string;
}

/**
 * Zone « Pipe commercial » — enrichit la Zone (compteurs = voir → creuser) des lignes
 * d'opportunités éditables et des comptes sélectionnables (agir). Les compteurs restent
 * intacts (tour-de-controle.md v2.1 §3 bandeau 2).
 */
export interface ZonePipe extends Zone {
  readonly opportunites: ReadonlyArray<OpportuniteLigne>;
  readonly comptes: ReadonlyArray<CompteOption>;
}

/**
 * Zone « Recrutement » — enrichit la Zone (compteurs agrégés par étape, RGPD option A) des lignes
 * candidat éditables (gestes : étape en ligne + cascade Acceptée) et de la liste des Title déjà
 * pris (allocation C-NNN du geste « ajouter »).
 *
 * `gestesAccessibles` : true seulement si la lecture nominative de « Candidats » a abouti sous
 * l'identité de l'utilisateur. Sur 403 (utilisateur non habilité au recrutement, ACL de liste —
 * rgpd-recrutement-candidats.md §3) ou source absente/illisible : false, `candidats` vide → l'UI
 * n'affiche QUE les compteurs agrégés (aucun nom exposé, aucune erreur bloquante). Le cockpit
 * n'élève aucun droit (tour-de-controle.md §1 régime 1, §6).
 */
export interface ZoneRecrutement extends Zone {
  readonly candidats: ReadonlyArray<CandidatLigne>;
  /** Title déjà attribués (conformes ou non) — base de l'allocation C-NNN du prochain candidat. */
  readonly titresPris: ReadonlyArray<string>;
  readonly gestesAccessibles: boolean;
  /** CodeMission des missions réelles connues (gabarits actifs) — options du dialogue de cascade. */
  readonly missionsConnues: ReadonlyArray<string>;
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
