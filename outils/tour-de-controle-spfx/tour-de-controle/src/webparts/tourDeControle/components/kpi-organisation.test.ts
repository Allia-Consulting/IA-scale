// Tests unitaires des indicateurs d'organisation (T-0020-d) — logique PURE.
// Vérité sur données réelles : la paire Datalab (n=2) de la Zone-de-proposition
// doit produire exactement 187 s (BRIEF-2 → KICKOFF-2, 10/07/2026).

import {
  apparierBriefKickoff,
  moyenneDeltas,
  formaterDuree,
  compterMissionsActives,
  compterCreesDepuis,
  COLONNE_STATUT_MISSION
} from './kpi-organisation';

describe('apparierBriefKickoff', () => {
  // Created réels lus au tenant (Zone-de-proposition) le 13/07/2026.
  const BRIEF_2 = { Title: 'BRIEF-2', Created: '2026-07-10T13:32:02Z' };
  const KICKOFF_2 = { Title: 'KICKOFF-2-20260710', Created: '2026-07-10T13:35:09Z' };
  const BRIEF_1 = { Title: 'BRIEF-1', Created: '2026-07-02T09:28:53Z' };
  const KICKOFF_1 = { Title: 'KICKOFF-1-20260702', Created: '2026-07-02T16:43:59Z' };

  it('apparie Datalab (n=2) à 187 s — la vérité sur données réelles', () => {
    const paires = apparierBriefKickoff([KICKOFF_2, BRIEF_2]);
    expect(paires).toHaveLength(1);
    expect(paires[0].n).toBe('2');
    expect(paires[0].deltaSecondes).toBe(187);
  });

  it('n\'apparie que les paires complètes (un BRIEF orphelin est ignoré)', () => {
    expect(apparierBriefKickoff([{ Title: 'BRIEF-9', Created: '2026-07-10T00:00:00Z' }])).toHaveLength(0);
  });

  it('trie par kick-off croissant : le dernier est le plus récent (n=2)', () => {
    const paires = apparierBriefKickoff([BRIEF_1, KICKOFF_1, BRIEF_2, KICKOFF_2]);
    expect(paires).toHaveLength(2);
    expect(paires[paires.length - 1].n).toBe('2');
    expect(paires[paires.length - 1].deltaSecondes).toBe(187);
  });

  it('ignore les lignes sans Created valide', () => {
    expect(apparierBriefKickoff([
      { Title: 'BRIEF-2', Created: '' },
      { Title: 'KICKOFF-2-x', Created: '2026-07-10T13:35:09Z' }
    ])).toHaveLength(0);
  });
});

describe('moyenneDeltas', () => {
  it('moyenne des Δ, 0 si aucune paire', () => {
    expect(moyenneDeltas([])).toBe(0);
    expect(moyenneDeltas([
      { n: '2', briefCreated: new Date(0), kickoffCreated: new Date(0), deltaSecondes: 187 },
      { n: '3', briefCreated: new Date(0), kickoffCreated: new Date(0), deltaSecondes: 213 }
    ])).toBe(200);
  });
});

describe('formaterDuree', () => {
  it('187 s → « 3 min 07 s » (secondes zéro-remplies)', () => {
    expect(formaterDuree(187)).toBe('3 min 07 s');
  });
  it('sous la minute → « N s »', () => {
    expect(formaterDuree(42)).toBe('42 s');
  });
  it('au-delà de l\'heure → « H h MM min »', () => {
    expect(formaterDuree(3600 + 16 * 60)).toBe('1 h 16 min');
  });
  it('borne basse : négatif ramené à 0 s', () => {
    expect(formaterDuree(-5)).toBe('0 s');
  });
});

describe('compterMissionsActives', () => {
  it('compte les missions au statut « En cours » (nom interne exact)', () => {
    const missions = [
      { [COLONNE_STATUT_MISSION]: 'En cours' },
      { [COLONNE_STATUT_MISSION]: 'En cours' },
      { [COLONNE_STATUT_MISSION]: 'Terminée' }
    ];
    expect(compterMissionsActives(missions)).toBe(2);
  });
});

describe('compterCreesDepuis', () => {
  it('compte les créations dans la fenêtre glissante de 7 jours', () => {
    const maintenant = new Date('2026-07-13T12:00:00Z');
    const lignes = [
      { Created: '2026-07-13T09:00:00Z' }, // dans la fenêtre
      { Created: '2026-07-08T09:00:00Z' }, // dans la fenêtre (>= J-7)
      { Created: '2026-07-01T09:00:00Z' }, // hors fenêtre
      { Created: '' }                       // ignorée
    ];
    expect(compterCreesDepuis(lignes, maintenant)).toBe(2);
  });
});
