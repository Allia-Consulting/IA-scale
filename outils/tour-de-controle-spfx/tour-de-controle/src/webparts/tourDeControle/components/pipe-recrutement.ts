// Bandeaux « Pipe commercial » et « Recrutement » — logique PURE, sans dépendance SPFx.
//
// Miroir de kpi-organisation.ts : ce module CALCULE sur des lignes déjà lues et
// CONSTRUIT les requêtes/payloads ; il n'ouvre aucun canal de données (le seul canal
// reste lireListe/ecrireListe de listes-reelles.ts). Isolé de React et des types SPFx
// à dessein — le rendu et les tests unitaires le consomment sans contexte de web part.
//
// Cible fonctionnelle : contrat socle tour-de-controle.md v2.0 §3 (bandeaux 2 et 3).
// Noms internes de colonnes et valeurs d'étape : ils FONT FOI dans modele-donnees.md
// §2 ter (convention « nom interne ASCII figé, libellé accentué » — les listes CRM /
// Comptes / Candidats ont été créées ASCII-first, donc pas d'encodage Graph `_x00e9_`).

import type { Ecriture } from './types';

/** Une ligne de liste lue (sous-ensemble des champs sélectionnés). */
export type Ligne = Record<string, unknown>;

// ---------------------------------------------------------------------------
// Noms internes de colonnes (Graph) — modele-donnees.md §2 ter (fait foi).
// ---------------------------------------------------------------------------
export const COL_ETAPE_CRM = 'Etape';            // Liste « CRM » — choix unique
export const COL_MONTANT_CRM = 'Montant';        // Liste « CRM » — nombre, € HT
export const COL_NOM_OPPORTUNITE = 'NomOpportunite'; // Liste « CRM » — texte
export const COL_COMPTE = 'Compte';              // Liste « CRM » — lookup → Comptes (écrit via `CompteId`)
export const COL_ECHEANCE = 'Echeance';          // Liste « CRM » — date (signature attendue)
export const COL_RESPONSABLE = 'Responsable';    // Liste « CRM » — personne (hors périmètre du formulaire minimal)
export const COL_CODEMISSION = 'CodeMission';    // Liste « CRM » — renseigné à la bascule « Gagnée » (hors périmètre)
export const COL_STATUT_COMPTE = 'Statut';       // Liste « Comptes » — choix unique
export const COL_ETAPE_CANDIDAT = 'Etape';       // Liste « Candidats » — choix unique

/** Domicile des opportunités (couture Missions par CodeMission à la bascule Gagnée). */
export const LISTE_CRM = 'CRM';

// ---------------------------------------------------------------------------
// Valeurs d'énumération (modele-donnees.md §2 bis / §2 ter).
// ---------------------------------------------------------------------------
export const ETAPE_QUALIFICATION = 'Qualification';
export const ETAPE_PROPOSITION = 'Proposition';
export const ETAPE_GAGNEE = 'Gagnée';
export const ETAPE_PERDUE = 'Perdue';
/** Les quatre étapes CRM, dans l'ordre figé de modele-donnees.md §2 ter (source du sélecteur). */
export const ETAPES_CRM: ReadonlyArray<string> = [
  ETAPE_QUALIFICATION,
  ETAPE_PROPOSITION,
  ETAPE_GAGNEE,
  ETAPE_PERDUE
];
export const STATUT_COMPTE_CLIENT = 'Client';
export const ETAPE_CANDIDAT_E1 = 'E1';
export const ETAPE_CANDIDAT_E2 = 'E2';
export const ETAPE_CANDIDAT_E3 = 'E3';
export const ETAPE_CANDIDAT_PROPOSITION = 'Proposition';

/**
 * Pondérations du pipe pondéré — FIGÉES au contrat tour-de-controle.md v2.0 §3
 * (bandeau 2). Toute étape absente de cette table pèse 0 (Gagnée/Perdue exclues du
 * pondéré : une affaire gagnée n'est plus « en cours », une perdue vaut 0).
 */
export const PONDERATIONS_PIPE: Readonly<Record<string, number>> = {
  Proposition: 0.60,   // figé tour-de-controle.md v2.0 §3
  Qualification: 0.15  // figé tour-de-controle.md v2.0 §3
};

/**
 * Requête OData du bandeau recrutement — $select=Etape UNIQUEMENT.
 * RÈGLE INVIOLABLE (RGPD, rgpd-recrutement-candidats.md, option A) : la page est
 * tenant-wide ; aucun champ nominatif (Title, NomCandidat, ResponsableAction, Email,
 * Telephone…) n'est jamais sélectionné ni lu. Seuls des AGRÉGATS par étape sortent.
 */
export const QUERY_RECRUTEMENT = `$select=${COL_ETAPE_CANDIDAT}&$top=2000`;

// ---------------------------------------------------------------------------
// Lectures robustes (Nombre SharePoint peut arriver en number ou en string).
// ---------------------------------------------------------------------------
export function montantOpportunite(l: Ligne): number {
  const v = l[COL_MONTANT_CRM];
  const n = typeof v === 'number' ? v : Number(v);
  return Number.isFinite(n) ? n : 0;
}

function etapeCrm(l: Ligne): string {
  const v = l[COL_ETAPE_CRM];
  return typeof v === 'string' ? v : '';
}

export function nomOpportunite(l: Ligne): string {
  const v = l[COL_NOM_OPPORTUNITE];
  return typeof v === 'string' && v ? v : '(sans nom)';
}

// ---------------------------------------------------------------------------
// Pipe commercial (tour-de-controle.md v2.0 §3 bandeau 2).
// ---------------------------------------------------------------------------

/** Comptes « actifs » = Statut « Client » (Prospect / Inactif exclus). */
export function compterComptesClients(comptes: ReadonlyArray<Ligne>): number {
  return comptes.filter(c => c[COL_STATUT_COMPTE] === STATUT_COMPTE_CLIENT).length;
}

/** Opportunités à l'étape « Proposition » (détail creusable — données commerciales). */
export function opportunitesEnProposition(crm: ReadonlyArray<Ligne>): ReadonlyArray<Ligne> {
  return crm.filter(o => etapeCrm(o) === ETAPE_PROPOSITION);
}

/** Montant proposé = Σ Montant des opportunités en Proposition. */
export function montantPropose(crm: ReadonlyArray<Ligne>): number {
  return opportunitesEnProposition(crm).reduce((t, o) => t + montantOpportunite(o), 0);
}

/** Pipe pondéré = Σ (Montant × pondération d'étape), pondérations figées au contrat. */
export function pipePondere(crm: ReadonlyArray<Ligne>): number {
  return crm.reduce((t, o) => t + montantOpportunite(o) * (PONDERATIONS_PIPE[etapeCrm(o)] ?? 0), 0);
}

/**
 * Format € FR entier (Math.round), séparateur de milliers = espace insécable.
 * N'utilise pas Intl (locale ICU non garantie dans le bundle) — construit à la main.
 * Ex. 75000 → « 75 000 € ».
 */
export function formaterEuros(montant: number): string {
  const n = Math.round(montant);
  const chiffres = String(Math.abs(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  return `${n < 0 ? '-' : ''}${chiffres} €`;
}

// ---------------------------------------------------------------------------
// Projection des opportunités pour la table éditable (voir → creuser → agir).
// ---------------------------------------------------------------------------

/**
 * Une opportunité projetée pour l'affichage/l'édition en ligne. `id` = Id numérique de
 * l'item (clé des mises à jour MERGE) ; `compte` = libellé du compte rattaché (lu via
 * `$expand=Compte/Title`). Forme volontairement plate, découplée du brut SharePoint.
 */
export interface OpportuniteLigne {
  readonly id: number;
  readonly nom: string;
  readonly etape: string;
  readonly montant: number;
  readonly compte?: string;
}

/** Id numérique d'une ligne SharePoint (tolère `Id`/`ID`, number ou string). */
function idLigne(l: Ligne): number {
  const v = l.Id ?? l.ID;
  const n = typeof v === 'number' ? v : Number(v);
  return Number.isFinite(n) ? n : 0;
}

/** Libellé du compte rattaché, lu depuis l'expansion du lookup (`Compte/Title`). */
function compteRattache(l: Ligne): string | undefined {
  const c = l[COL_COMPTE];
  if (c && typeof c === 'object' && 'Title' in c) {
    const t = (c as { Title?: unknown }).Title;
    return typeof t === 'string' && t ? t : undefined;
  }
  return undefined;
}

/**
 * Projette les lignes brutes de la Liste « CRM » en OpportuniteLigne[] — tolérante aux
 * champs absents (chaque lecteur a son défaut). PURE : ne lit aucun canal, mappe seulement.
 */
export function projeterOpportunites(lignes: ReadonlyArray<Ligne>): ReadonlyArray<OpportuniteLigne> {
  return lignes.map(l => ({
    id: idLigne(l),
    nom: nomOpportunite(l),
    etape: etapeCrm(l),
    montant: montantOpportunite(l),
    compte: compteRattache(l)
  }));
}

// ---------------------------------------------------------------------------
// Recrutement (tour-de-controle.md v2.0 §3 bandeau 3, option A RGPD).
// ---------------------------------------------------------------------------

/** Compte les candidats à une étape donnée (agrégat pur — aucun champ nominatif). */
export function compterCandidatsEtape(candidats: ReadonlyArray<Ligne>, etape: string): number {
  return candidats.filter(c => c[COL_ETAPE_CANDIDAT] === etape).length;
}

// ---------------------------------------------------------------------------
// Écriture guidée — constructeurs PURS (payloads + options HTTP).
//
// Source Microsoft Learn (14/07/2026) : SharePoint REST OData 4.0 —
//   learn.microsoft.com/sharepoint/dev/spfx/connect-to-sharepoint
//   learn.microsoft.com/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest
// Le digest de formulaire est injecté AUTOMATIQUEMENT par SPHttpClient — jamais géré ici.
// ---------------------------------------------------------------------------

export type ModeEcriture = 'create' | 'update';

export interface OptionsEcriture {
  readonly headers: Record<string, string>;
  readonly body: string;
}

/**
 * Options d'un POST d'écriture de liste — source unique de vérité des en-têtes que
 * `ecrireListe` (listes-reelles.ts) passe à `sp.post`.
 *  - Accept = 'application/json;odata.metadata=none' (PAS 'odata=nometadata' → 406) ;
 *  - Content-Type = 'application/json' ;
 *  - mise à jour : POST tunnellisé MERGE via 'X-HTTP-Method':'MERGE' + 'IF-MATCH':'*'.
 */
export function optionsEcriture(mode: ModeEcriture, champs: Record<string, unknown>): OptionsEcriture {
  const headers: Record<string, string> = {
    'Accept': 'application/json;odata.metadata=none',
    'Content-Type': 'application/json'
  };
  if (mode === 'update') {
    headers['X-HTTP-Method'] = 'MERGE';
    headers['IF-MATCH'] = '*';
  }
  return { headers, body: JSON.stringify(champs) };
}

/**
 * Payload de création d'une opportunité en Liste « CRM » (écriture guidée).
 * Rattachement au compte OBLIGATOIRE : un lookup SharePoint s'écrit par son champ id
 * numérique `<NomInterne>Id` (ici `CompteId`) = Id de l'item Comptes cible (réf. Microsoft
 * Learn « working-with-lists-and-list-items-with-rest »). Étape par défaut Qualification.
 * L'échéance n'est écrite que si fournie (champ optionnel du formulaire).
 * NON écrits ici (manques documentés, hors périmètre de cette PR) : `Title` (l'identifiant
 * O-NNN, laissé à SharePoint), `Responsable` (Person), `CodeMission` (bascule « Gagnée »).
 */
export function champsCreationOpportunite(
  params: {
    readonly nom: string;
    readonly compteId: number;
    readonly montant: number;
    readonly etape?: string;
    readonly echeance?: string;
  }
): Record<string, unknown> {
  const champs: Record<string, unknown> = {
    [COL_NOM_OPPORTUNITE]: params.nom,
    [`${COL_COMPTE}Id`]: params.compteId,
    [COL_MONTANT_CRM]: params.montant,
    [COL_ETAPE_CRM]: params.etape || ETAPE_QUALIFICATION
  };
  if (params.echeance) {
    champs[COL_ECHEANCE] = params.echeance;
  }
  return champs;
}

/** Payload de changement d'étape d'une opportunité existante. */
export function champsChangementEtape(etape: string): Record<string, unknown> {
  return { [COL_ETAPE_CRM]: etape };
}

/** Payload de changement du montant d'une opportunité existante. */
export function champsChangementMontant(montant: number): Record<string, unknown> {
  return { [COL_MONTANT_CRM]: montant };
}

/**
 * Primitif d'écriture injecté — permet aux gestes ci-dessous de rester PURS et
 * testables sans charger le runtime SPFx (`@microsoft/sp-http` exige `window`).
 * listes-reelles.ts fournit l'implémentation réelle liée à `sp` + `dataSiteUrl`.
 */
export type Ecrivain = (
  titre: string,
  champs: Record<string, unknown>,
  id?: number
) => Promise<Ecriture>;

/** Geste « nouvelle opportunité » — création avec rattachement au compte (CompteId). */
export function creerOpportunite(
  ecrire: Ecrivain,
  params: {
    readonly nom: string;
    readonly compteId: number;
    readonly montant: number;
    readonly etape?: string;
    readonly echeance?: string;
  }
): Promise<Ecriture> {
  return ecrire(LISTE_CRM, champsCreationOpportunite(params));
}

/** Geste « changer l'étape d'une opportunité » (mise à jour MERGE). */
export function changerEtapeOpportunite(
  ecrire: Ecrivain,
  id: number,
  etape: string
): Promise<Ecriture> {
  return ecrire(LISTE_CRM, champsChangementEtape(etape), id);
}

/** Geste « changer le montant d'une opportunité » (mise à jour MERGE), symétrique. */
export function changerMontantOpportunite(
  ecrire: Ecrivain,
  id: number,
  montant: number
): Promise<Ecriture> {
  return ecrire(LISTE_CRM, champsChangementMontant(montant), id);
}
