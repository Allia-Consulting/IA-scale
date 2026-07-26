// Tests unitaires de la cascade « Acceptée » (T-0039, contrat v2.2) — logique PURE, primitives
// injectées. Cible : tour-de-controle.md v2.2 §1 régime 2 (annonce exhaustive + confirmation), §3
// bandeau 3 (DEUX écritures + rappel d'affectation), §6 (fail-closed sur les écritures, jamais de
// retour arrière silencieux) et rgpd-recrutement-candidats.md §3 (minimisation : Email/Telephone ne
// migrent pas). Aucune dépendance SPFx / réseau. L'affectation initiale N'EST PLUS écrite (arbitrage
// gardien du 26/07) : elle fait l'objet d'un RAPPEL (non-écriture).

import type { Ecriture } from './types';
import {
  separerNomCandidat,
  champsAcceptationCandidat,
  champsFicheRessource,
  estSaisieDeMission,
  choisirSaisie,
  rappelAffectation,
  construireAnnonce,
  executerCascade,
  type CandidatCascade,
  type SaisieCascade,
  type DepsCascade
} from './cascade-acceptee';
import {
  COL_ETAPE_CANDIDAT,
  COL_PRENOM,
  COL_NOM,
  COL_IDENTIFIANT_ENTRA,
  COL_GRADE,
  COL_DISPONIBILITE,
  ETAPE_CANDIDAT_ACCEPTEE
} from './pipe-recrutement';

const CANDIDAT: CandidatCascade = { id: 5, title: 'C-005', nom: 'Julie Martin', grade: 'Manager', etape: 'Proposition' };
const SAISIE: SaisieCascade = {
  identifiantEntra: 'julie.martin@allia-consulting.com',
  disponibilite: 'Immédiate',
  codeMission: '3'
};

// Fausse fabrique de deps qui journalise l'ordre des écritures + capte les payloads.
function fakeDeps(over?: {
  ecrire?: (titre: string) => Ecriture;
}): { deps: DepsCascade; log: string[]; payloads: Array<{ titre: string; champs: Record<string, unknown> }> } {
  const log: string[] = [];
  const payloads: Array<{ titre: string; champs: Record<string, unknown> }> = [];
  const deps: DepsCascade = {
    ecrire: async (titre, champs) => { log.push(`ecrire:${titre}`); payloads.push({ titre, champs }); return (over?.ecrire ? over.ecrire(titre) : { etat: 'ok' }) as Ecriture; }
  };
  return { deps, log, payloads };
}

describe('separerNomCandidat', () => {
  it('scinde au premier espace : premier mot = Prénom, reste = Nom', () => {
    expect(separerNomCandidat('Julie Martin')).toEqual({ prenom: 'Julie', nom: 'Martin' });
    expect(separerNomCandidat('Jean Pierre Dupont')).toEqual({ prenom: 'Jean', nom: 'Pierre Dupont' });
  });
  it('un seul mot → tout dans Nom (Prénom vide)', () => {
    expect(separerNomCandidat('Madonna')).toEqual({ prenom: '', nom: 'Madonna' });
  });
  it('vide / espaces → deux chaînes vides', () => {
    expect(separerNomCandidat('   ')).toEqual({ prenom: '', nom: '' });
  });
});

describe('payloads de la cascade', () => {
  it('champsAcceptationCandidat ne touche que l’étape → Acceptée', () => {
    const c = champsAcceptationCandidat();
    expect(c[COL_ETAPE_CANDIDAT]).toBe(ETAPE_CANDIDAT_ACCEPTEE);
    expect(Object.keys(c)).toEqual([COL_ETAPE_CANDIDAT]);
  });

  it('champsFicheRessource : Title=IdentifiantEntra, grade repris, disponibilité ; NI Email NI Telephone (minimisation)', () => {
    const f = champsFicheRessource({ identifiantEntra: 'a@b.c', prenom: 'Julie', nom: 'Martin', grade: 'Manager', disponibilite: 'Immédiate' });
    expect(f.Title).toBe('a@b.c');
    expect(f[COL_IDENTIFIANT_ENTRA]).toBe('a@b.c');
    expect(f[COL_PRENOM]).toBe('Julie');
    expect(f[COL_NOM]).toBe('Martin');
    expect(f[COL_GRADE]).toBe('Manager');
    expect(f[COL_DISPONIBILITE]).toBe('Immédiate');
    // Minimisation RGPD (§3) : aucune trace d'Email ni de Telephone.
    expect(Object.keys(f)).not.toContain('Email');
    expect(Object.keys(f)).not.toContain('Telephone');
  });
});

describe('localisation du classeur de saisie (helpers purs, pour NOMMER le rappel)', () => {
  it('estSaisieDeMission : motif ^saisie-<code>- exact (pas de préfixe partiel)', () => {
    expect(estSaisieDeMission('saisie-3-datalab.xlsx', '3')).toBe(true);
    expect(estSaisieDeMission('saisie-3-datalab.xlsx', '30')).toBe(false);
    expect(estSaisieDeMission('saisie-30-x.xlsx', '3')).toBe(false);
    expect(estSaisieDeMission('gabarit-3.xlsx', '3')).toBe(false);
  });
  it('choisirSaisie : unique → nom, aucun → undefined, plusieurs → ambigu', () => {
    expect(choisirSaisie(['saisie-3-a.xlsx', 'saisie-4-b.xlsx'], '3')).toEqual({ nom: 'saisie-3-a.xlsx', ambigu: false });
    expect(choisirSaisie(['saisie-4-b.xlsx'], '3')).toEqual({ ambigu: false });
    const amb = choisirSaisie(['saisie-3-a.xlsx', 'saisie-3-doublon.xlsx'], '3');
    expect(amb.ambigu).toBe(true);
  });
});

describe('rappelAffectation — non-écriture (geste humain, §5.6)', () => {
  it('nom RÉEL fourni → il est nommé dans le rappel', () => {
    const r = rappelAffectation('3', 'saisie-3-datalab.xlsx');
    expect(r).toContain('saisie-3-datalab.xlsx');
    expect(r.toLowerCase()).toContain('reste à saisir');
    expect(r.toLowerCase()).toContain('geste humain');
    // Un rappel, pas une écriture : la saisie est matricielle, hors cockpit.
    expect(r.toLowerCase()).toContain('saisie matricielle');
  });
  it('nom absent, code connu → motif générique avec le code (fail-open)', () => {
    const r = rappelAffectation('3');
    expect(r).toContain('saisie-3-….xlsx');
  });
  it('nom absent, code vide → motif générique <code>', () => {
    const r = rappelAffectation('');
    expect(r).toContain('saisie-<code>-….xlsx');
  });
});

describe('construireAnnonce — exhaustive (2 écritures, ordre d’exécution ; PAS d’affectation)', () => {
  const annonce = construireAnnonce(CANDIDAT, SAISIE);
  it('deux lignes, dans l’ordre Candidats → Ressources-Profil', () => {
    expect(annonce).toHaveLength(2);
    expect(annonce[0].cible).toContain('Candidats');
    expect(annonce[0].detail).toContain(ETAPE_CANDIDAT_ACCEPTEE);
    expect(annonce[1].cible).toContain('Ressources-Profil');
  });
  it('aucune ligne d’écriture ne cible l’affectation / T_Affectations', () => {
    for (const l of annonce) {
      expect(l.cible).not.toContain('T_Affectations');
      expect(l.cible.toLowerCase()).not.toContain('affectation');
    }
  });
  it('rappelle explicitement que Email/Téléphone NE sont PAS repris (minimisation)', () => {
    expect(annonce[1].detail.toLowerCase()).toContain('non repris');
  });
  it('affiche l’identité et le grade dans la fiche', () => {
    expect(annonce[1].detail).toContain('julie.martin@allia-consulting.com');
    expect(annonce[1].detail).toContain('Manager');
  });
});

describe('executerCascade — chemin nominal (2 écritures + rappel)', () => {
  it('deux écritures de listes dans l’ordre exact, PAS d’écriture d’affectation', async () => {
    const { deps, log, payloads } = fakeDeps();
    const etat = await executerCascade(CANDIDAT, SAISIE, deps, 'saisie-3-datalab.xlsx');
    expect(etat.ok).toBe(true);
    expect(etat.ecrituresFaites).toBe(2);
    // Ordre : étape candidat → fiche ressource. Aucune primitive d'affectation n'existe plus.
    expect(log).toEqual(['ecrire:Candidats', 'ecrire:Ressources-Profil']);
    // Payload 1 = étape ; payload 2 = fiche SANS Email/Telephone.
    expect(payloads[0].champs[COL_ETAPE_CANDIDAT]).toBe(ETAPE_CANDIDAT_ACCEPTEE);
    expect(Object.keys(payloads[1].champs)).not.toContain('Email');
    expect(Object.keys(payloads[1].champs)).not.toContain('Telephone');
  });

  it('le RAPPEL (nom réel) figure dans le résumé de succès ET le champ rappel', async () => {
    const { deps } = fakeDeps();
    const etat = await executerCascade(CANDIDAT, SAISIE, deps, 'saisie-3-datalab.xlsx');
    expect(etat.rappel).toContain('saisie-3-datalab.xlsx');
    expect(etat.resume).toContain('Ressources-Profil');
    expect(etat.resume).toContain('saisie-3-datalab.xlsx'); // rappel inclus dans le message de succès
  });

  it('nom non résolu → rappel générique (fail-open), les écritures ont quand même lieu', async () => {
    const { deps, log } = fakeDeps();
    const etat = await executerCascade(CANDIDAT, SAISIE, deps); // pas de nomClasseur
    expect(etat.ok).toBe(true);
    expect(etat.ecrituresFaites).toBe(2);
    expect(log).toEqual(['ecrire:Candidats', 'ecrire:Ressources-Profil']);
    expect(etat.rappel).toContain('saisie-3-….xlsx');
  });
});

describe('executerCascade — fail-closed sur les écritures, jamais de retour arrière silencieux', () => {
  it('échec écriture 1 (étape) → 0 écriture effectuée, arrêt ; rappel présent', async () => {
    const { deps, log } = fakeDeps({ ecrire: (t) => (t === 'Candidats' ? { etat: 'refuse' } : { etat: 'ok' }) });
    const etat = await executerCascade(CANDIDAT, SAISIE, deps, 'saisie-3-datalab.xlsx');
    expect(etat.ok).toBe(false);
    expect(etat.ecrituresFaites).toBe(0);
    expect(etat.etapeEchec).toBe(1);
    expect(etat.resume).toContain('Aucune écriture');
    expect(etat.rappel).toContain('saisie-3-datalab.xlsx');
    // On n'est jamais allé jusqu'à la fiche.
    expect(log).toEqual(['ecrire:Candidats']);
  });

  it('échec écriture 2 (fiche) → 1 écriture DÉJÀ faite, aucun retour arrière', async () => {
    const { deps, log } = fakeDeps({ ecrire: (t) => (t === 'Ressources-Profil' ? { etat: 'indisponible' } : { etat: 'ok' }) });
    const etat = await executerCascade(CANDIDAT, SAISIE, deps, 'saisie-3-datalab.xlsx');
    expect(etat.ok).toBe(false);
    expect(etat.ecrituresFaites).toBe(1);
    expect(etat.etapeEchec).toBe(2);
    expect(etat.resume).toMatch(/DÉJÀ effectuée|aucun retour arrière/i);
    expect(log).toEqual(['ecrire:Candidats', 'ecrire:Ressources-Profil']);
  });
});
