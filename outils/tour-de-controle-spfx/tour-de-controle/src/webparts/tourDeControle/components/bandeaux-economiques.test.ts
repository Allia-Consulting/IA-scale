// Tests unitaires des modèles de rendu des trois bandeaux économiques (cockpit v2, point 1).
// Cible : tour-de-controle.md v2.1 §3 (bandeaux 1/4/5). Vérifie l'HONNÊTETÉ des états vides :
// « · » partout (jamais 0 inventé), structure présente, mention référentiel, messages vides.

import type { EtatGabarits, GabaritActif } from './gabarits';
import {
  PLACEHOLDER,
  MOIS_COURTS,
  anneesSelectionnables,
  regimeMois,
  construireStaffing,
  construireRentabilite,
  construireFactures,
  MENTION_REFERENTIEL_RESTREINT
} from './bandeaux-economiques';

function etatBase(over: Partial<EtatGabarits> = {}): EtatGabarits {
  return {
    gabarits: [],
    anomalies: [],
    source: 'ok',
    luLe: '16/07/2026 à 09:30',
    referentielCoutsAccessible: false,
    referentielEtat: 'restreint',
    ...over
  };
}

const UN_GABARIT: GabaritActif = { codeMission: '2', url: '/x/gabarit-2.xlsx', derniereLecture: '16/07/2026 à 09:30' };

describe('staffing — sélecteur d’année et régime réalisé/prévisionnel', () => {
  it('propose l’année courante ±2 (cinq années)', () => {
    expect(anneesSelectionnables(2026)).toEqual([2024, 2025, 2026, 2027, 2028]);
  });

  it('régime : année passée = réalisé, future = prévisionnel', () => {
    expect(regimeMois(11, 2025, 2026, 6)).toBe('realise');
    expect(regimeMois(0, 2027, 2026, 6)).toBe('previsionnel');
  });

  it('régime année courante : mois écoulés = réalisé, mois courant et suivants = prévisionnel', () => {
    // moisCourant0 = 6 (juillet). Juin (5) écoulé → réalisé ; juillet (6) en cours → prévisionnel.
    expect(regimeMois(5, 2026, 2026, 6)).toBe('realise');
    expect(regimeMois(6, 2026, 2026, 6)).toBe('previsionnel');
    expect(regimeMois(7, 2026, 2026, 6)).toBe('previsionnel');
  });
});

describe('staffing — états vides honnêtes (point 1)', () => {
  it('12 barres, chacune « · » pour effectif et pct, hauteur 0 (jamais un faux niveau)', () => {
    const m = construireStaffing(etatBase(), 2026, 2026, 6);
    expect(m.barres).toHaveLength(12);
    expect(m.barres.map(b => b.libelleMois)).toEqual(MOIS_COURTS as string[]);
    for (const b of m.barres) {
      expect(b.effectif).toBe(PLACEHOLDER);
      expect(b.pct).toBe(PLACEHOLDER);
      expect(b.hauteurPct).toBe(0);
    }
  });

  it('aucunGabarit = true sans gabarit actif, false dès qu’un gabarit est lu', () => {
    expect(construireStaffing(etatBase(), 2026, 2026, 6).aucunGabarit).toBe(true);
    expect(construireStaffing(etatBase({ gabarits: [UN_GABARIT] }), 2026, 2026, 6).aucunGabarit).toBe(false);
  });
});

describe('rentabilité — tableau 12 mois × (Budget|Réalisé) + Total, lignes CA/EBITDA', () => {
  it('deux lignes CA total / EBITDA, 12 cellules chacune, tout « · »', () => {
    const m = construireRentabilite(etatBase(), 2026);
    expect(m.mois).toHaveLength(12);
    expect(m.lignes.map(l => l.libelle)).toEqual(['CA total', 'EBITDA']);
    for (const ligne of m.lignes) {
      expect(ligne.cellules).toHaveLength(12);
      for (const c of ligne.cellules) {
        expect(c.budget).toBe(PLACEHOLDER);
        expect(c.realise).toBe(PLACEHOLDER);
      }
      expect(ligne.total.budget).toBe(PLACEHOLDER);
      expect(ligne.total.realise).toBe(PLACEHOLDER);
    }
  });

  it('EBITDA porte la mention « référentiel à audience restreinte » quand inaccessible', () => {
    const m = construireRentabilite(etatBase({ referentielCoutsAccessible: false }), 2026);
    const ebitda = m.lignes.find(l => l.libelle === 'EBITDA');
    expect(ebitda && ebitda.mention).toBe(MENTION_REFERENTIEL_RESTREINT);
  });

  it('EBITDA sans mention quand le référentiel est accessible', () => {
    const m = construireRentabilite(etatBase({ referentielCoutsAccessible: true, referentielEtat: 'accessible' }), 2026);
    const ebitda = m.lignes.find(l => l.libelle === 'EBITDA');
    expect(ebitda && ebitda.mention).toBeUndefined();
    const caTotal = m.lignes.find(l => l.libelle === 'CA total');
    expect(caTotal && caTotal.mention).toBeUndefined();
  });
});

describe('factures — état vide honnête (point 1 : échéanciers non ouverts)', () => {
  it('aucun gabarit lu → message « aucun gabarit actif lu »', () => {
    const m = construireFactures(etatBase());
    expect(m.lignes).toHaveLength(0);
    expect(m.messageVide).toBe('Aucune facture à émettre — aucun gabarit actif lu');
  });

  it('des gabarits existent → message « Aucune facture à émettre. »', () => {
    const m = construireFactures(etatBase({ gabarits: [UN_GABARIT] }));
    expect(m.lignes).toHaveLength(0);
    expect(m.messageVide).toBe('Aucune facture à émettre.');
  });
});
