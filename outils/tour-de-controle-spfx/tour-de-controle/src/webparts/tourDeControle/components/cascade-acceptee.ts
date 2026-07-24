// Cascade « Acceptée » du bandeau recrutement — logique PURE, sans dépendance SPFx.
//
// Cible normative : tour-de-controle.md §1 (régime 2 — cascade déterministe) et §3 bandeau 3
// (« passage en Acceptée → cascade « fiche Ressources-Profil + affectation initiale », sur
// confirmation »). Une cascade S'ANNONCE AVANT D'EXÉCUTER (liste exhaustive des écritures) et
// N'EXÉCUTE QUE SUR CONFIRMATION EXPLICITE ; une cascade qui écrirait sans confirmation est un
// défaut (§6).
//
// Trois écritures, dans cet ordre :
//   (1) Candidats.Etape → « Acceptée »              (liste — SharePoint REST, identité utilisateur)
//   (2) création d'une fiche « Ressources-Profil »   (liste — SharePoint REST, identité utilisateur)
//   (3) ajout d'une ligne d'affectation initiale     (classeur de SAISIE — Graph Workbook)
//       dans la table T_Affectations du classeur `saisie-<CodeMission>-….xlsx` (modele-donnees.md
//       §5.6 : l'affectation est un geste économique qui vit dans la SAISIE, source humaine — pas
//       dans le gabarit, qui est un dérivé régénéré par l'agent).
//
// Fail-closed, jamais de retour arrière silencieux (tour-de-controle.md §6) :
//   - la cible d'affectation est VÉRIFIÉE en pré-vol (localisation du classeur + présence de la
//     table) AVANT toute écriture : si elle manque, ZÉRO écriture (message précis) ;
//   - un échec en cours de cascade ARRÊTE la séquence et affiche l'état EXACT (écritures 1..n
//     déjà faites), sans jamais tenter de défaire ce qui a été écrit ;
//   - l'annulation avant confirmation = zéro écriture (garantie par l'UI : `executerCascade`
//     n'est appelée qu'à la confirmation).
//
// Minimisation RGPD (rgpd-recrutement-candidats.md §3) : l'Email et le Téléphone du candidat NE
// migrent PAS vers la fiche Ressources-Profil — seuls Prénom, Nom, identité Entra, grade et
// disponibilité y figurent.

import type { Ecriture } from './types';
import {
  LISTE_CANDIDATS,
  LISTE_RESSOURCES_PROFIL,
  COL_ETAPE_CANDIDAT,
  COL_PRENOM,
  COL_NOM,
  COL_IDENTIFIANT_ENTRA,
  COL_GRADE,
  COL_DISPONIBILITE,
  ETAPE_CANDIDAT_ACCEPTEE
} from './pipe-recrutement';

// ---------------------------------------------------------------------------
// Entrées de la cascade.
// ---------------------------------------------------------------------------

/** Le candidat basculé (repère + champs repris dans la fiche). */
export interface CandidatCascade {
  /** Id numérique de l'item Candidats (clé du MERGE d'étape). */
  readonly id: number;
  /** Id stable C-NNN (affiché dans l'annonce). */
  readonly title: string;
  /** NomCandidat (nom complet) — scindé en Prénom/Nom pour la fiche (`separerNomCandidat`). */
  readonly nom: string;
  /** Grade visé — repris TEL QUEL dans la fiche Ressources-Profil. */
  readonly grade: string;
  /** Étape actuelle (affichée dans l'annonce « … → Acceptée »). */
  readonly etape: string;
}

/** Les champs saisis par l'opérateur dans le dialogue de cascade (confirmés avant exécution). */
export interface SaisieCascade {
  /** UPN / identité Entra de la nouvelle ressource — Title + IdentifiantEntra de la fiche, et
   *  Ressource de la ligne d'affectation (couture Ressources-Profil ↔ T_Affectations). */
  readonly identifiantEntra: string;
  /** Disponibilité (choix) écrite dans la fiche. */
  readonly disponibilite: string;
  /** CodeMission de l'affectation initiale (mission réelle). */
  readonly codeMission: string;
  /** Mois de l'affectation, 1er du mois (AAAA-MM-01). */
  readonly mois: string;
  /** Jours prévus de l'affectation initiale. */
  readonly joursPrevus: number;
}

// ---------------------------------------------------------------------------
// Décomposition du nom + payloads (PURS).
// ---------------------------------------------------------------------------

/**
 * Scinde un NomCandidat (champ unique) en { prenom, nom } pour la fiche Ressources-Profil.
 * HEURISTIQUE (micro-décision à relire) : le premier mot = Prénom, le reste = Nom ; un nom d'un
 * seul mot va ENTIER dans Nom (Prénom vide). Le canon ne porte pas de règle de scission — l'opérateur
 * confirme l'annonce, qui affiche le découpage retenu.
 */
export function separerNomCandidat(nomComplet: string): { readonly prenom: string; readonly nom: string } {
  const net = (typeof nomComplet === 'string' ? nomComplet : '').replace(/\s+/g, ' ').trim();
  if (!net) { return { prenom: '', nom: '' }; }
  const i = net.indexOf(' ');
  if (i < 0) { return { prenom: '', nom: net }; }
  return { prenom: net.slice(0, i), nom: net.slice(i + 1) };
}

/** Payload (1) — bascule d'étape du candidat vers « Acceptée » (le seul champ touché). */
export function champsAcceptationCandidat(): Record<string, unknown> {
  return { [COL_ETAPE_CANDIDAT]: ETAPE_CANDIDAT_ACCEPTEE };
}

/**
 * Payload (2) — création de la fiche Ressources-Profil.
 * `Title` = IdentifiantEntra : MICRO-DÉCISION à relire — le canon (modele-donnees.md §2 bis) est
 * SILENCIEUX sur le Title de Ressources-Profil ; l'UPN en est l'identifiant stable naturel.
 * Minimisation RGPD (§3) : NI Email NI Téléphone du candidat (ils ne sont pas dans le payload).
 */
export function champsFicheRessource(
  params: {
    readonly identifiantEntra: string;
    readonly prenom: string;
    readonly nom: string;
    readonly grade: string;
    readonly disponibilite: string;
  }
): Record<string, unknown> {
  return {
    Title: params.identifiantEntra,
    [COL_PRENOM]: params.prenom,
    [COL_NOM]: params.nom,
    [COL_IDENTIFIANT_ENTRA]: params.identifiantEntra,
    [COL_GRADE]: params.grade,
    [COL_DISPONIBILITE]: params.disponibilite
  };
}

/**
 * Valeurs (3) — une ligne d'affectation pour `workbook/tables/T_Affectations/rows/add`.
 * ORDRE FIGÉ = en-têtes de T_Affectations (modele-donnees.md §5.2 / `ENTETES_AFFECTATIONS` de
 * workbook-graph.ts) : [CodeMission, Ressource, Mois, JoursPrevus]. Ressource = IdentifiantEntra
 * (couture Ressources-Profil). Une seule ligne, forme `values: [[...]]` de l'API Graph.
 */
export function valeursAffectation(
  params: {
    readonly codeMission: string;
    readonly identifiantEntra: string;
    readonly mois: string;
    readonly joursPrevus: number;
  }
): ReadonlyArray<ReadonlyArray<unknown>> {
  return [[params.codeMission, params.identifiantEntra, params.mois, params.joursPrevus]];
}

// ---------------------------------------------------------------------------
// Localisation du classeur de saisie (helpers PURS ; le réseau vit dans listes-reelles.ts).
// ---------------------------------------------------------------------------

/** Un nom de fichier est-il le classeur de saisie de `codeMission` ? Motif §5.6 `^saisie-(\d+)-`. */
export function estSaisieDeMission(nomFichier: string, codeMission: string): boolean {
  const m = /^saisie-(\d+)-/.exec((typeof nomFichier === 'string' ? nomFichier : '').trim());
  return !!m && m[1] === String(codeMission).trim();
}

/**
 * Choisit le classeur de saisie d'une mission parmi une liste de noms. Renvoie le nom retenu (ou
 * `undefined` si aucun) et un drapeau `ambigu` si plusieurs candidats matchent (l'appelant refuse
 * alors, plutôt que d'écrire dans le mauvais classeur — fail-closed).
 */
export function choisirSaisie(
  noms: ReadonlyArray<string>,
  codeMission: string
): { readonly nom?: string; readonly ambigu: boolean } {
  const trouves = noms.filter(n => estSaisieDeMission(n, codeMission));
  if (trouves.length === 0) { return { ambigu: false }; }
  if (trouves.length > 1) { return { nom: trouves[0], ambigu: true }; }
  return { nom: trouves[0], ambigu: false };
}

// ---------------------------------------------------------------------------
// Annonce EXHAUSTIVE (§1 régime 2) — construite AVANT toute écriture, affichée à l'opérateur.
// ---------------------------------------------------------------------------

export interface LigneAnnonce {
  /** Cible lisible de l'écriture (liste / classeur + table). */
  readonly cible: string;
  /** Détail lisible de ce qui sera écrit. */
  readonly detail: string;
}

/**
 * Construit l'annonce exhaustive des TROIS écritures — l'ordre est celui de l'exécution. Affiche
 * le découpage Prénom/Nom retenu et rappelle explicitement que Email/Téléphone NE sont PAS repris.
 */
export function construireAnnonce(candidat: CandidatCascade, saisie: SaisieCascade): ReadonlyArray<LigneAnnonce> {
  const { prenom, nom } = separerNomCandidat(candidat.nom);
  const nomFiche = `${prenom} ${nom}`.trim() || candidat.nom || candidat.title;
  return [
    {
      cible: `Liste « Candidats » — ${candidat.title}`,
      detail: `Étape « ${candidat.etape || '—'} » → « ${ETAPE_CANDIDAT_ACCEPTEE} ».`
    },
    {
      cible: 'Liste « Ressources-Profil » — création',
      detail:
        `${nomFiche} · ${saisie.identifiantEntra} · grade « ${candidat.grade || '—'} » · ` +
        `disponibilité « ${saisie.disponibilite || '—'} ». Email et téléphone NON repris (minimisation RGPD).`
    },
    {
      cible: `Classeur de saisie de la mission ${saisie.codeMission} — table T_Affectations (ajout de ligne)`,
      detail: `Ressource ${saisie.identifiantEntra} · mois ${saisie.mois} · ${saisie.joursPrevus} jours prévus.`
    }
  ];
}

// ---------------------------------------------------------------------------
// Primitives INJECTÉES (implémentées par listes-reelles.ts, liées à SPHttpClient / MSGraphClientV3).
// ---------------------------------------------------------------------------

/** Écriture de liste (SharePoint REST, identité utilisateur) — même signature que `Ecrivain`. */
export type EcrivainCascade = (
  titre: string,
  champs: Record<string, unknown>,
  id?: number
) => Promise<Ecriture>;

/** Le classeur de saisie résolu (opaque à ce module — passé tel quel à `ajouterLigneAffectation`). */
export interface ItemAffectation {
  readonly driveId: string;
  readonly itemId: string;
  /** Nom du classeur retenu (affiché en cas d'échec, jamais un chemin inventé). */
  readonly fichier: string;
}

/** Résultat du pré-vol de localisation (aucune écriture) : cible prête, ou motif précis d'échec. */
export type CibleAffectation =
  | { readonly etat: 'ok'; readonly item: ItemAffectation }
  | { readonly etat: 'introuvable'; readonly cause: string }
  | { readonly etat: 'indisponible'; readonly cause: string };

/** Résultat d'une étape d'écriture (aligné sur `Ecriture`, avec une cause optionnelle). */
export type ResultatEtape =
  | { readonly etat: 'ok' }
  | { readonly etat: 'refuse' }
  | { readonly etat: 'indisponible'; readonly cause?: string };

export interface DepsCascade {
  readonly ecrire: EcrivainCascade;
  /** Pré-vol : localise le classeur de saisie de la mission et vérifie la table T_Affectations. */
  readonly localiserAffectation: (codeMission: string) => Promise<CibleAffectation>;
  /** Ajout de la ligne d'affectation dans la table (Graph Workbook `rows/add`). */
  readonly ajouterLigneAffectation: (
    item: ItemAffectation,
    valeurs: ReadonlyArray<ReadonlyArray<unknown>>
  ) => Promise<ResultatEtape>;
}

// ---------------------------------------------------------------------------
// Exécution séquentielle, fail-closed, sans retour arrière silencieux.
// ---------------------------------------------------------------------------

export interface EtatCascade {
  /** true seulement si les TROIS écritures ont abouti. */
  readonly ok: boolean;
  /** Nombre d'écritures RÉELLEMENT effectuées (0..3) — l'état exact, jamais masqué. */
  readonly ecrituresFaites: 0 | 1 | 2 | 3;
  /** Étape en échec (ou 'preflight'), si échec. */
  readonly etapeEchec?: 'preflight' | 1 | 2 | 3;
  /** Cause technique courte, si échec. */
  readonly cause?: string;
  /** Résumé lisible de l'état exact (affiché à l'opérateur). */
  readonly resume: string;
}

function libelleEcriture(etat: 'refuse' | 'indisponible'): string {
  return etat === 'refuse' ? 'refusée (droits)' : 'indisponible';
}

/**
 * Exécute la cascade « Acceptée ». À N'APPELER QU'APRÈS confirmation explicite de l'annonce
 * (`construireAnnonce`). Séquentielle et fail-closed :
 *   0. pré-vol de la cible d'affectation — si absente/illisible : ZÉRO écriture ;
 *   1. étape candidat → Acceptée ; 2. fiche Ressources-Profil ; 3. ligne d'affectation.
 * Tout échec ARRÊTE et retourne l'état exact (écritures faites), sans retour arrière.
 */
export async function executerCascade(
  candidat: CandidatCascade,
  saisie: SaisieCascade,
  deps: DepsCascade
): Promise<EtatCascade> {
  // 0. Pré-vol (AVANT toute écriture) : la cible d'affectation doit exister.
  const cible = await deps.localiserAffectation(saisie.codeMission);
  if (cible.etat !== 'ok') {
    const mot = cible.etat === 'introuvable' ? 'introuvable' : 'illisible';
    return {
      ok: false,
      ecrituresFaites: 0,
      etapeEchec: 'preflight',
      cause: cible.cause,
      resume:
        `Cascade non lancée : classeur de saisie de la mission ${saisie.codeMission} ${mot} ` +
        `(${cible.cause}). Aucune écriture effectuée.`
    };
  }

  // 1. Candidats.Etape → Acceptée.
  const r1 = await deps.ecrire(LISTE_CANDIDATS, champsAcceptationCandidat(), candidat.id);
  if (r1.etat !== 'ok') {
    return {
      ok: false,
      ecrituresFaites: 0,
      etapeEchec: 1,
      cause: r1.etat,
      resume:
        `Arrêt à l'écriture 1/3 (étape candidat → Acceptée) : ${libelleEcriture(r1.etat)}. ` +
        `Aucune écriture effectuée.`
    };
  }

  // 2. Création de la fiche Ressources-Profil (Email/Téléphone NON repris — §3).
  const { prenom, nom } = separerNomCandidat(candidat.nom);
  const r2 = await deps.ecrire(
    LISTE_RESSOURCES_PROFIL,
    champsFicheRessource({
      identifiantEntra: saisie.identifiantEntra,
      prenom,
      nom,
      grade: candidat.grade,
      disponibilite: saisie.disponibilite
    })
  );
  if (r2.etat !== 'ok') {
    return {
      ok: false,
      ecrituresFaites: 1,
      etapeEchec: 2,
      cause: r2.etat,
      resume:
        `Arrêt à l'écriture 2/3 (fiche Ressources-Profil) : ${libelleEcriture(r2.etat)}. ` +
        `L'écriture 1/3 (étape → Acceptée) est DÉJÀ effectuée — aucun retour arrière automatique.`
    };
  }

  // 3. Ligne d'affectation initiale dans le classeur de saisie (Graph Workbook).
  const r3 = await deps.ajouterLigneAffectation(
    cible.item,
    valeursAffectation({
      codeMission: saisie.codeMission,
      identifiantEntra: saisie.identifiantEntra,
      mois: saisie.mois,
      joursPrevus: saisie.joursPrevus
    })
  );
  if (r3.etat !== 'ok') {
    return {
      ok: false,
      ecrituresFaites: 2,
      etapeEchec: 3,
      cause: r3.etat === 'indisponible' ? (r3.cause ?? 'indisponible') : r3.etat,
      resume:
        `Arrêt à l'écriture 3/3 (ligne d'affectation, ${cible.item.fichier}) : ` +
        `${r3.etat === 'refuse' ? 'refusée (droits)' : (r3.cause ?? 'indisponible')}. ` +
        `Les écritures 1/3 et 2/3 sont DÉJÀ effectuées — aucun retour arrière automatique.`
    };
  }

  return {
    ok: true,
    ecrituresFaites: 3,
    resume:
      `Cascade complète : étape → Acceptée, fiche Ressources-Profil créée, ` +
      `ligne d'affectation initiale ajoutée (${cible.item.fichier}).`
  };
}
