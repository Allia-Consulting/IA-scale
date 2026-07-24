// Tests unitaires de la cascade « Acceptée » (T-0039) — logique PURE, primitives injectées.
// Cible : tour-de-controle.md §1 régime 2 (annonce exhaustive + confirmation), §6 (fail-closed,
// jamais de retour arrière silencieux) et rgpd-recrutement-candidats.md §3 (minimisation :
// Email/Telephone ne migrent pas). Aucune dépendance SPFx / réseau.

import type { Ecriture } from './types';
import { ENTETES_AFFECTATIONS } from './workbook-graph';
import {
  separerNomCandidat,
  champsAcceptationCandidat,
  champsFicheRessource,
  valeursAffectation,
  estSaisieDeMission,
  choisirSaisie,
  construireAnnonce,
  executerCascade,
  type CandidatCascade,
  type SaisieCascade,
  type DepsCascade,
  type CibleAffectation,
  type ResultatEtape
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
  codeMission: '3',
  mois: '2026-08-01',
  joursPrevus: 10
};

// Fausse fabrique de deps qui journalise l'ordre des primitives + capte les payloads.
function fakeDeps(over?: {
  loc?: CibleAffectation;
  ecrire?: (titre: string) => Ecriture;
  affect?: ResultatEtape;
}): { deps: DepsCascade; log: string[]; payloads: Array<{ titre: string; champs: Record<string, unknown> }>; valeurs: unknown[] } {
  const log: string[] = [];
  const payloads: Array<{ titre: string; champs: Record<string, unknown> }> = [];
  const valeurs: unknown[] = [];
  const deps: DepsCascade = {
    localiserAffectation: async (code) => { log.push(`loc:${code}`); return over?.loc ?? { etat: 'ok', item: { driveId: 'd', itemId: 'i', fichier: 'saisie-3-datalab.xlsx' } }; },
    ecrire: async (titre, champs) => { log.push(`ecrire:${titre}`); payloads.push({ titre, champs }); return (over?.ecrire ? over.ecrire(titre) : { etat: 'ok' }) as Ecriture; },
    ajouterLigneAffectation: async (_item, v) => { log.push('affect'); valeurs.push(v); return over?.affect ?? { etat: 'ok' }; }
  };
  return { deps, log, payloads, valeurs };
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

  it('valeursAffectation : une ligne, ordre = en-têtes T_Affectations [CodeMission, Ressource, Mois, JoursPrevus]', () => {
    const v = valeursAffectation({ codeMission: '3', identifiantEntra: 'a@b.c', mois: '2026-08-01', joursPrevus: 10 });
    expect(v).toEqual([['3', 'a@b.c', '2026-08-01', 10]]);
    // L'ordre DOIT suivre les en-têtes figés du contrat (§5.2).
    expect([...ENTETES_AFFECTATIONS]).toEqual(['CodeMission', 'Ressource', 'Mois', 'JoursPrevus']);
  });
});

describe('localisation du classeur de saisie (helpers purs)', () => {
  it('estSaisieDeMission : motif ^saisie-<code>- exact (pas de préfixe partiel)', () => {
    expect(estSaisieDeMission('saisie-3-datalab.xlsx', '3')).toBe(true);
    expect(estSaisieDeMission('saisie-3-datalab.xlsx', '30')).toBe(false);
    expect(estSaisieDeMission('saisie-30-x.xlsx', '3')).toBe(false);
    expect(estSaisieDeMission('gabarit-3.xlsx', '3')).toBe(false);
  });
  it('choisirSaisie : unique → nom, aucun → undefined, plusieurs → ambigu (fail-closed)', () => {
    expect(choisirSaisie(['saisie-3-a.xlsx', 'saisie-4-b.xlsx'], '3')).toEqual({ nom: 'saisie-3-a.xlsx', ambigu: false });
    expect(choisirSaisie(['saisie-4-b.xlsx'], '3')).toEqual({ ambigu: false });
    const amb = choisirSaisie(['saisie-3-a.xlsx', 'saisie-3-doublon.xlsx'], '3');
    expect(amb.ambigu).toBe(true);
  });
});

describe('construireAnnonce — exhaustive (3 écritures, ordre d’exécution)', () => {
  const annonce = construireAnnonce(CANDIDAT, SAISIE);
  it('trois lignes, dans l’ordre Candidats → Ressources-Profil → T_Affectations', () => {
    expect(annonce).toHaveLength(3);
    expect(annonce[0].cible).toContain('Candidats');
    expect(annonce[0].detail).toContain(ETAPE_CANDIDAT_ACCEPTEE);
    expect(annonce[1].cible).toContain('Ressources-Profil');
    expect(annonce[2].cible).toContain('T_Affectations');
  });
  it('rappelle explicitement que Email/Téléphone NE sont PAS repris (minimisation)', () => {
    expect(annonce[1].detail.toLowerCase()).toContain('non repris');
  });
  it('affiche l’identité, le grade, la mission et les jours', () => {
    expect(annonce[1].detail).toContain('julie.martin@allia-consulting.com');
    expect(annonce[1].detail).toContain('Manager');
    expect(annonce[2].detail).toContain('10');
    expect(annonce[2].cible).toContain('3');
  });
});

describe('executerCascade — chemin nominal', () => {
  it('pré-vol PUIS trois écritures, dans l’ordre exact', async () => {
    const { deps, log, payloads, valeurs } = fakeDeps();
    const etat = await executerCascade(CANDIDAT, SAISIE, deps);
    expect(etat.ok).toBe(true);
    expect(etat.ecrituresFaites).toBe(3);
    // Ordre : localisation (pré-vol) → étape candidat → fiche ressource → affectation.
    expect(log).toEqual(['loc:3', 'ecrire:Candidats', 'ecrire:Ressources-Profil', 'affect']);
    // Payload 1 = étape ; payload 2 = fiche SANS Email/Telephone.
    expect(payloads[0].champs[COL_ETAPE_CANDIDAT]).toBe(ETAPE_CANDIDAT_ACCEPTEE);
    expect(Object.keys(payloads[1].champs)).not.toContain('Email');
    expect(Object.keys(payloads[1].champs)).not.toContain('Telephone');
    expect(valeurs[0]).toEqual([['3', 'julie.martin@allia-consulting.com', '2026-08-01', 10]]);
  });
});

describe('executerCascade — fail-closed, jamais de retour arrière silencieux', () => {
  it('pré-vol : classeur introuvable → ZÉRO écriture', async () => {
    const { deps, log } = fakeDeps({ loc: { etat: 'introuvable', cause: 'aucun classeur saisie-3-…' } });
    const etat = await executerCascade(CANDIDAT, SAISIE, deps);
    expect(etat.ok).toBe(false);
    expect(etat.ecrituresFaites).toBe(0);
    expect(etat.etapeEchec).toBe('preflight');
    // Aucune écriture : le log ne contient que la localisation.
    expect(log).toEqual(['loc:3']);
    expect(etat.resume).toContain('Aucune écriture');
  });

  it('échec écriture 1 (étape) → 0 écriture effectuée, arrêt', async () => {
    const { deps, log } = fakeDeps({ ecrire: (t) => (t === 'Candidats' ? { etat: 'refuse' } : { etat: 'ok' }) });
    const etat = await executerCascade(CANDIDAT, SAISIE, deps);
    expect(etat.ok).toBe(false);
    expect(etat.ecrituresFaites).toBe(0);
    expect(etat.etapeEchec).toBe(1);
    // On n'est jamais allé jusqu'à la fiche ni l'affectation.
    expect(log).toEqual(['loc:3', 'ecrire:Candidats']);
  });

  it('échec écriture 2 (fiche) → 1 écriture DÉJÀ faite, aucun retour arrière', async () => {
    const { deps, log } = fakeDeps({ ecrire: (t) => (t === 'Ressources-Profil' ? { etat: 'indisponible' } : { etat: 'ok' }) });
    const etat = await executerCascade(CANDIDAT, SAISIE, deps);
    expect(etat.ok).toBe(false);
    expect(etat.ecrituresFaites).toBe(1);
    expect(etat.etapeEchec).toBe(2);
    expect(etat.resume).toMatch(/DÉJÀ effectuée|aucun retour arrière/i);
    // La séquence s'arrête AVANT l'affectation (pas de défaisement de l'écriture 1).
    expect(log).toEqual(['loc:3', 'ecrire:Candidats', 'ecrire:Ressources-Profil']);
  });

  it('échec écriture 3 (affectation) → 2 écritures DÉJÀ faites, aucun retour arrière', async () => {
    const { deps, log } = fakeDeps({ affect: { etat: 'indisponible', cause: 'HTTP 500' } });
    const etat = await executerCascade(CANDIDAT, SAISIE, deps);
    expect(etat.ok).toBe(false);
    expect(etat.ecrituresFaites).toBe(2);
    expect(etat.etapeEchec).toBe(3);
    expect(log).toEqual(['loc:3', 'ecrire:Candidats', 'ecrire:Ressources-Profil', 'affect']);
  });
});
