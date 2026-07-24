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
export const COL_NOM_COMPTE = 'NomCompte';       // Liste « Comptes » — nom LISIBLE du client (≠ Title/code)
export const COL_ETAPE_CANDIDAT = 'Etape';       // Liste « Candidats » — choix unique
export const COL_NOM_CANDIDAT = 'NomCandidat';   // Liste « Candidats » — donnée personnelle (pertinente au poste)
export const COL_GRADE = 'Grade';                // Candidats & Ressources-Profil — choix unique (attribut de poste, non identifiant)
export const COL_SOURCE = 'Source';              // Liste « Candidats » — choix unique
export const COL_EMAIL = 'Email';                // Liste « Candidats » — NE migre PAS vers Ressources-Profil (minimisation RGPD §3)
export const COL_TELEPHONE = 'Telephone';        // Liste « Candidats » — optionnel ; NE migre PAS (minimisation RGPD §3)
// Liste « Ressources-Profil » (modele-donnees.md §2 bis) — cible n°2 de la cascade « Acceptée ».
export const COL_PRENOM = 'Prenom';
export const COL_NOM = 'Nom';
export const COL_IDENTIFIANT_ENTRA = 'IdentifiantEntra';
// Disponibilité : colonne CRÉÉE LIBELLÉ-FIRST au tenant → nom interne encodé Graph `_x00e9_`
// (contraire à la convention §2 ter « nom interne ASCII figé » ; état RÉEL constaté au 24/07, on
// écrit sur le nom interne réel, jamais sur le libellé).
export const COL_DISPONIBILITE = 'Disponibilit_x00e9_';

/** Domicile des opportunités (couture Missions par CodeMission à la bascule Gagnée). */
export const LISTE_CRM = 'CRM';
/** Domicile des candidats (recrutement) — accès restreint (modele-donnees.md §2 bis). */
export const LISTE_CANDIDATS = 'Candidats';
/** Domicile des fiches ressource (profil) — cible de la cascade « Acceptée ». */
export const LISTE_RESSOURCES_PROFIL = 'Ressources-Profil';

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
export const ETAPE_CANDIDAT_ACCEPTEE = 'Acceptée';
export const ETAPE_CANDIDAT_REFUSEE = 'Refusée';
/**
 * Les six étapes candidat, ordre figé de modele-donnees.md §2 ter (source du sélecteur en ligne).
 * « Acceptée » figure ici pour le rendu du sélecteur, mais NE s'écrit JAMAIS par changement
 * d'étape direct : elle ouvre la cascade (garde `champsChangementEtapeCandidat`, cascade-acceptee.ts).
 */
export const ETAPES_CANDIDAT: ReadonlyArray<string> = [
  ETAPE_CANDIDAT_E1,
  ETAPE_CANDIDAT_E2,
  ETAPE_CANDIDAT_E3,
  ETAPE_CANDIDAT_PROPOSITION,
  ETAPE_CANDIDAT_ACCEPTEE,
  ETAPE_CANDIDAT_REFUSEE
];
/** Grades visés (choix unique, sans ajout manuel — modele-donnees.md §2 ter). */
export const GRADES_CANDIDAT: ReadonlyArray<string> = [
  'Consultant Junior', 'Consultant', 'Consultant Senior', 'Manager', 'Senior Manager', 'Directeur', 'Associé'
];
/** Sources de candidature (choix unique, sans ajout manuel — modele-donnees.md §2 ter). */
export const SOURCES_CANDIDAT: ReadonlyArray<string> = [
  'Cooptation', 'Chasseur', 'Candidature spontanée', 'LinkedIn'
];

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

/**
 * Requête des GESTES recrutement (édition en ligne + cascade) — DISTINCTE de QUERY_RECRUTEMENT.
 * Sélectionne les champs NOMINATIFS nécessaires à l'action (Id, Title, NomCandidat, Grade, Etape).
 * Elle est lue sous l'identité de l'utilisateur : son succès dépend de l'ACL de la liste
 * « Candidats » (destinataires internes du recrutement — rgpd-recrutement-candidats.md §3). Un
 * utilisateur non habilité obtient un 403 → gestes masqués, seuls les compteurs agrégés subsistent
 * (QUERY_RECRUTEMENT reste, elle, strictement Etape). Le cockpit n'élève aucun droit (§1 régime 1).
 */
export const QUERY_GESTES_RECRUTEMENT =
  `$select=Id,Title,${COL_NOM_CANDIDAT},${COL_GRADE},${COL_ETAPE_CANDIDAT}&$top=2000`;

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

/**
 * Nom LISIBLE du client rattaché — la colonne `NomCompte` du compte (« Arabelle Solutions »),
 * lue depuis l'expansion du lookup. Le `Title` (code « CPT-001 ») N'EST PAS un repli : l'aperçu
 * de bascule Gagnée exige le nom lisible (modele-donnees.md §2 bis). À défaut de `NomCompte`, on
 * renvoie `undefined` (fallback sobre « · » côté table, refus d'aperçu) — jamais le code en douce.
 */
function compteRattache(l: Ligne): string | undefined {
  const c = l[COL_COMPTE];
  if (c && typeof c === 'object') {
    const nom = (c as { NomCompte?: unknown }).NomCompte;
    if (typeof nom === 'string' && nom) { return nom; }
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
// Apercu du nom d'espace de mission (bascule Gagnee) — MIROIR EXACT de
// `_composer_nom_espace` (outils/mcp-graph/server.py) : memes validations, meme ordre.
// A 3 SEGMENTS « AAAA - Client - Nom de la mission » — le 4e segment (code mission)
// N'EXISTE PAS a la bascule : le code est attribue A L'OUVERTURE (modele-donnees.md §2 bis,
// geste gardien / T-0024), jamais par le cockpit. Un apercu qui divergerait mentirait.
// ---------------------------------------------------------------------------

/** Caracteres interdits dans une composante (miroir server.py `_CARACTERES_INTERDITS_ESPACE`). */
const CARACTERES_INTERDITS_ESPACE = new Set('"*:<>?/\\|#%,');

/** Resultat d'apercu : le nom compose, ou une raison de refus (pour un refus sobre AVANT ecriture). */
export type ApercuNom =
  | { readonly ok: true; readonly nom: string }
  | { readonly ok: false; readonly raison: string };

/** Valide une composante (client / nom de mission) comme le serveur ; renvoie sa forme normalisee. */
function validerComposante(valeur: string, etiquette: string): { ok: true; v: string } | { ok: false; raison: string } {
  // Reduction des espaces multiples + strip des extremites (miroir de `" ".join(valeur.split())`).
  const v = (typeof valeur === 'string' ? valeur : '').replace(/\s+/g, ' ').trim();
  if (!v) { return { ok: false, raison: `${etiquette} manquant` }; }
  if (v.length > 60) { return { ok: false, raison: `${etiquette} trop long (60 caracteres maximum)` }; }
  for (const c of v) {
    if (CARACTERES_INTERDITS_ESPACE.has(c) || c.charCodeAt(0) < 32) {
      return { ok: false, raison: `${etiquette} : caractere interdit` };
    }
  }
  if (v.indexOf('..') >= 0) { return { ok: false, raison: `${etiquette} : la sequence « .. » est interdite` }; }
  if (v.startsWith('.') || v.endsWith('.')) { return { ok: false, raison: `${etiquette} : pas de point en tete ni en fin` }; }
  return { ok: true, v };
}

/**
 * Apercu du nom d'espace « AAAA - Client - Nom de la mission » (3 SEGMENTS), MIROIR EXACT
 * de `_composer_nom_espace` (server.py). Le 4e segment (code mission) n'existe PAS ici : il
 * est attribue a l'ouverture (§2 bis, geste gardien / T-0024). Renvoie `{ok:false, raison}`
 * sur composante invalide — jamais un faux nom affiche.
 */
export function apercuNomMission(annee: string, client: string, nomOpportunite: string): ApercuNom {
  if (typeof annee !== 'string' || !/^\d{4}$/.test(annee)) {
    return { ok: false, raison: 'annee invalide (4 chiffres attendus)' };
  }
  const a = Number(annee);
  if (a < 2020 || a > 2100) {
    return { ok: false, raison: 'annee hors bornes (2020..2100)' };
  }
  const c = validerComposante(client, 'client');
  if (!c.ok) { return { ok: false, raison: c.raison }; }
  const n = validerComposante(nomOpportunite, 'nom de la mission');
  if (!n.ok) { return { ok: false, raison: n.raison }; }
  return { ok: true, nom: `${annee} - ${c.v} - ${n.v}` };
}

// ---------------------------------------------------------------------------
// Recrutement (tour-de-controle.md v2.0 §3 bandeau 3, option A RGPD).
// ---------------------------------------------------------------------------

/** Compte les candidats à une étape donnée (agrégat pur — aucun champ nominatif). */
export function compterCandidatsEtape(candidats: ReadonlyArray<Ligne>, etape: string): number {
  return candidats.filter(c => c[COL_ETAPE_CANDIDAT] === etape).length;
}

/**
 * Alloue le prochain identifiant candidat au motif C-NNN : (max des Title conformes `^C-(\d+)$`) + 1,
 * zéro-paddé sur 3 chiffres. Une liste SANS aucun motif C- (ou vide) démarre à `C-001`. Les Title
 * non conformes (scorie nommée : candidats 1..7 au tenant) sont IGNORÉS du calcul du max (jamais
 * une erreur). Le défaut Title du geste CRM (Title laissé à SharePoint, plan §13.2) n'est PAS
 * reproduit : l'identifiant candidat est un id stable (modele-donnees.md §2 ter) alloué explicitement.
 */
export function prochainTitleCandidat(candidats: ReadonlyArray<Ligne>): string {
  let max = 0;
  for (const c of candidats) {
    const t = c.Title ?? c.title;
    if (typeof t === 'string') {
      const m = /^C-(\d+)$/.exec(t.trim());
      if (m) {
        const n = Number(m[1]);
        if (Number.isFinite(n) && n > max) { max = n; }
      }
    }
  }
  // Zéro-paddé sur 3 (sans String.padStart — lib TS antérieure à ES2017 dans ce projet).
  const s = String(max + 1);
  return `C-${s.length >= 3 ? s : ('000' + s).slice(-3)}`;
}

/**
 * Une ligne candidat projetée pour l'édition en ligne (geste « changement d'étape »). Porte le
 * strict nécessaire à l'action : `id` (clé MERGE), `title` (id stable C-NNN), `nom` (repère pour
 * l'opérateur), `grade` (repris à l'acceptation), `etape`. Lue sous l'identité de l'utilisateur ;
 * l'accès à ces champs nominatifs est gouverné par l'ACL de la liste « Candidats » (destinataires
 * internes, rgpd-recrutement-candidats.md §3) — voir `chargerGestesRecrutement` (listes-reelles.ts).
 */
export interface CandidatLigne {
  readonly id: number;
  readonly title: string;
  readonly nom: string;
  readonly grade: string;
  readonly etape: string;
}

/** Projette les lignes brutes de la Liste « Candidats » en CandidatLigne[] (mappage PUR, tolérant). */
export function projeterCandidats(lignes: ReadonlyArray<Ligne>): ReadonlyArray<CandidatLigne> {
  return lignes.map(l => ({
    id: idLigne(l),
    title: typeof l.Title === 'string' ? l.Title : (typeof l.title === 'string' ? l.title : ''),
    nom: typeof l[COL_NOM_CANDIDAT] === 'string' ? (l[COL_NOM_CANDIDAT] as string) : '',
    grade: typeof l[COL_GRADE] === 'string' ? (l[COL_GRADE] as string) : '',
    etape: typeof l[COL_ETAPE_CANDIDAT] === 'string' ? (l[COL_ETAPE_CANDIDAT] as string) : ''
  }));
}

/**
 * Payload de création d'un candidat en Liste « Candidats » (geste « ajouter un candidat »).
 * Étape posée à `E1` (candidat créé en début de tunnel, tour-de-controle.md §3 bandeau 3). `Title`
 * alloué au motif C-NNN (`prochainTitleCandidat`) et écrit EXPLICITEMENT. Le téléphone n'est écrit
 * que fourni (optionnel). Aucune donnée hors de celles pertinentes au poste (minimisation §3).
 */
export function champsCreationCandidat(
  params: {
    readonly title: string;
    readonly nom: string;
    readonly grade: string;
    readonly source: string;
    readonly email: string;
    readonly telephone?: string;
  }
): Record<string, unknown> {
  const champs: Record<string, unknown> = {
    Title: params.title,
    [COL_NOM_CANDIDAT]: params.nom,
    [COL_GRADE]: params.grade,
    [COL_SOURCE]: params.source,
    [COL_EMAIL]: params.email,
    [COL_ETAPE_CANDIDAT]: ETAPE_CANDIDAT_E1
  };
  if (params.telephone && params.telephone.trim()) {
    champs[COL_TELEPHONE] = params.telephone.trim();
  }
  return champs;
}

/**
 * Payload de changement d'étape d'un candidat — avec GARDE. La bascule vers « Acceptée » ne s'écrit
 * JAMAIS par cette voie : elle passe par la cascade déterministe (annonce exhaustive + confirmation
 * explicite, tour-de-controle.md §1 régime 2 / §3 bandeau 3). Toute tentative directe LÈVE — c'est
 * un défaut d'appelant, pas un cas d'exécution (une cascade qui écrirait sans confirmation est un
 * défaut, §6). Voir `cascade-acceptee.ts`.
 */
export function champsChangementEtapeCandidat(etape: string): Record<string, unknown> {
  if (etape === ETAPE_CANDIDAT_ACCEPTEE) {
    throw new Error(
      'Bascule « Acceptée » interdite par changement d’étape direct : elle passe par la cascade ' +
      '(annonce + confirmation, tour-de-controle.md §1 régime 2). Voir cascade-acceptee.ts.'
    );
  }
  return { [COL_ETAPE_CANDIDAT]: etape };
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

/** Geste « ajouter un candidat » — création en Liste « Candidats », étape E1, Title C-NNN alloué. */
export function creerCandidat(
  ecrire: Ecrivain,
  params: {
    readonly title: string;
    readonly nom: string;
    readonly grade: string;
    readonly source: string;
    readonly email: string;
    readonly telephone?: string;
  }
): Promise<Ecriture> {
  return ecrire(LISTE_CANDIDATS, champsCreationCandidat(params));
}

/**
 * Geste « changer l'étape d'un candidat » (mise à jour MERGE). La garde de
 * `champsChangementEtapeCandidat` interdit « Acceptée » par cette voie (cascade seule).
 */
export function changerEtapeCandidat(
  ecrire: Ecrivain,
  id: number,
  etape: string
): Promise<Ecriture> {
  return ecrire(LISTE_CANDIDATS, champsChangementEtapeCandidat(etape), id);
}
