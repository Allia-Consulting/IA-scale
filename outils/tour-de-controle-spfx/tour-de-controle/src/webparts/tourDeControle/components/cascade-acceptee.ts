// Cascade « Acceptée » du bandeau recrutement — logique PURE, sans dépendance SPFx.
//
// Cible normative : tour-de-controle.md v2.2 §1 (régime 2 — cascade déterministe), §3 bandeau 3
// (« passage en Acceptée → cascade « fiche Ressources-Profil + rappel d'affectation », sur
// confirmation ») et §6 (fail-closed, jamais de retour arrière silencieux). Une cascade S'ANNONCE
// AVANT D'EXÉCUTER (liste exhaustive des écritures) et N'EXÉCUTE QUE SUR CONFIRMATION EXPLICITE ;
// une cascade qui écrirait sans confirmation est un défaut.
//
// DEUX écritures, dans cet ordre (arbitrage gardien du 26/07/2026, contrat v2.2) :
//   (1) Candidats.Etape → « Acceptée »              (liste — SharePoint REST, identité utilisateur)
//   (2) création d'une fiche « Ressources-Profil »   (liste — SharePoint REST, identité utilisateur)
//
// PLUS un RAPPEL d'affectation, qui N'EST PAS une écriture (`rappelAffectation`) : l'affectation
// initiale reste un GESTE HUMAIN dans le classeur de SAISIE `saisie-<code>-….xlsx` (modele-donnees.md
// §5.6 — saisie matricielle, hors cockpit). La cascade ne fait que le rappeler, en nommant le
// classeur (nom réel si résolu en lecture seule, motif générique sinon — fail-OPEN, un rappel n'est
// pas une écriture). Motif de la réduction : la table T_Affectations n'existe que dans les gabarits
// dérivés (§5.2), pas dans la saisie ; le pré-vol fail-closed du 24/07 l'a prouvé (2 refus, zéro
// écriture) — d'où le retrait de l'ancienne écriture Graph Workbook d'affectation.
//
// Fail-closed sur les écritures, jamais de retour arrière silencieux (tour-de-controle.md §6) :
//   - un échec en cours de cascade ARRÊTE la séquence et affiche l'état EXACT (écritures 1..n déjà
//     faites), sans jamais tenter de défaire ce qui a été écrit ;
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
  /** UPN / identité Entra de la nouvelle ressource — Title + IdentifiantEntra de la fiche. */
  readonly identifiantEntra: string;
  /** Disponibilité (choix) écrite dans la fiche. */
  readonly disponibilite: string;
  /** CodeMission de la mission d'accueil — NON écrit ; sert au RAPPEL (nom du classeur de saisie). */
  readonly codeMission: string;
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

// ---------------------------------------------------------------------------
// Localisation du classeur de saisie (helpers PURS) — READ-ONLY, pour NOMMER le classeur dans le
// RAPPEL (jamais pour écrire). Le réseau (listing REST) vit dans listes-reelles.ts.
// ---------------------------------------------------------------------------

/** Un nom de fichier est-il le classeur de saisie de `codeMission` ? Motif §5.6 `^saisie-(\d+)-`. */
export function estSaisieDeMission(nomFichier: string, codeMission: string): boolean {
  const m = /^saisie-(\d+)-/.exec((typeof nomFichier === 'string' ? nomFichier : '').trim());
  return !!m && m[1] === String(codeMission).trim();
}

/**
 * Choisit le classeur de saisie d'une mission parmi une liste de noms. Renvoie le nom retenu (ou
 * `undefined` si aucun) et un drapeau `ambigu` si plusieurs candidats matchent. Comme la résolution
 * ne sert qu'à NOMMER le classeur dans le rappel (aucune écriture), l'appelant traite l'ambiguïté et
 * l'absence en fail-OPEN (motif générique), pas en fail-closed.
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

/**
 * RAPPEL d'affectation (PUR) — texte affiché dans l'annonce ET le message de succès. Ce n'est PAS
 * une écriture : l'affectation initiale reste un geste humain dans le classeur de SAISIE
 * `saisie-<code>-….xlsx` (modele-donnees.md §5.6). `nomClasseur` = nom RÉEL résolu en lecture seule
 * quand il l'est ; sinon on retombe (fail-OPEN) sur le motif générique avec le code de mission.
 */
export function rappelAffectation(codeMission: string, nomClasseur?: string): string {
  const code = (typeof codeMission === 'string' ? codeMission : '').trim();
  const classeur = (typeof nomClasseur === 'string' && nomClasseur.trim() !== '')
    ? nomClasseur.trim()
    : `saisie-${code !== '' ? code : '<code>'}-….xlsx`;
  return (
    `L'affectation initiale reste à saisir (geste humain) dans le classeur de saisie ` +
    `${classeur} — le cockpit ne l'écrit pas (saisie matricielle, modele-donnees.md §5.6).`
  );
}

// ---------------------------------------------------------------------------
// Annonce EXHAUSTIVE (§1 régime 2) — construite AVANT toute écriture, affichée à l'opérateur.
// ---------------------------------------------------------------------------

export interface LigneAnnonce {
  /** Cible lisible de l'écriture (liste). */
  readonly cible: string;
  /** Détail lisible de ce qui sera écrit. */
  readonly detail: string;
}

/**
 * Construit l'annonce exhaustive des DEUX écritures — l'ordre est celui de l'exécution. Affiche
 * le découpage Prénom/Nom retenu et rappelle explicitement que Email/Téléphone NE sont PAS repris.
 * Le RAPPEL d'affectation (non-écriture) est produit à part par `rappelAffectation`.
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
    }
  ];
}

// ---------------------------------------------------------------------------
// Primitives INJECTÉES (implémentées par listes-reelles.ts, liées à SPHttpClient).
// ---------------------------------------------------------------------------

/** Écriture de liste (SharePoint REST, identité utilisateur) — même signature que `Ecrivain`. */
export type EcrivainCascade = (
  titre: string,
  champs: Record<string, unknown>,
  id?: number
) => Promise<Ecriture>;

export interface DepsCascade {
  readonly ecrire: EcrivainCascade;
}

// ---------------------------------------------------------------------------
// Exécution séquentielle, fail-closed sur les écritures, sans retour arrière silencieux.
// ---------------------------------------------------------------------------

export interface EtatCascade {
  /** true seulement si les DEUX écritures ont abouti. */
  readonly ok: boolean;
  /** Nombre d'écritures RÉELLEMENT effectuées (0..2) — l'état exact, jamais masqué. */
  readonly ecrituresFaites: 0 | 1 | 2;
  /** Étape en échec (1 = candidat, 2 = fiche), si échec. */
  readonly etapeEchec?: 1 | 2;
  /** Cause technique courte, si échec. */
  readonly cause?: string;
  /** Résumé lisible de l'état exact (affiché à l'opérateur), rappel d'affectation inclus. */
  readonly resume: string;
  /** RAPPEL d'affectation (non-écriture) — également exposé pour l'affichage indépendant. */
  readonly rappel: string;
}

function libelleEcriture(etat: 'refuse' | 'indisponible'): string {
  return etat === 'refuse' ? 'refusée (droits)' : 'indisponible';
}

/**
 * Exécute la cascade « Acceptée ». À N'APPELER QU'APRÈS confirmation explicite de l'annonce
 * (`construireAnnonce`). Séquentielle et fail-closed sur les écritures :
 *   1. étape candidat → Acceptée ; 2. fiche Ressources-Profil.
 * Tout échec ARRÊTE et retourne l'état exact (écritures faites), sans retour arrière. Le RAPPEL
 * d'affectation (non-écriture) est joint dans TOUS les cas : `nomClasseur` est le nom RÉEL résolu
 * en lecture seule par l'appelant (fail-OPEN vers le motif générique si non résolu).
 */
export async function executerCascade(
  candidat: CandidatCascade,
  saisie: SaisieCascade,
  deps: DepsCascade,
  nomClasseur?: string
): Promise<EtatCascade> {
  const rappel = rappelAffectation(saisie.codeMission, nomClasseur);

  // 1. Candidats.Etape → Acceptée.
  const r1 = await deps.ecrire(LISTE_CANDIDATS, champsAcceptationCandidat(), candidat.id);
  if (r1.etat !== 'ok') {
    return {
      ok: false,
      ecrituresFaites: 0,
      etapeEchec: 1,
      cause: r1.etat,
      resume:
        `Arrêt à l'écriture 1/2 (étape candidat → Acceptée) : ${libelleEcriture(r1.etat)}. ` +
        `Aucune écriture effectuée.`,
      rappel
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
        `Arrêt à l'écriture 2/2 (fiche Ressources-Profil) : ${libelleEcriture(r2.etat)}. ` +
        `L'écriture 1/2 (étape → Acceptée) est DÉJÀ effectuée — aucun retour arrière automatique.`,
      rappel
    };
  }

  return {
    ok: true,
    ecrituresFaites: 2,
    resume:
      `Cascade complète : étape → Acceptée, fiche Ressources-Profil créée. ${rappel}`,
    rappel
  };
}
