// Tests unitaires des modèles de rendu des trois bandeaux économiques (cockpit v2, point 1).
// Cible : tour-de-controle.md v2.1 §3 (bandeaux 1/4/5). Vérifie l'HONNÊTETÉ des états vides :
// « · » partout (jamais 0 inventé), structure présente, mention référentiel, messages vides.

import type { EtatGabarits, GabaritActif } from './gabarits';
import type { ContenuGabarit, ContenuReferentiel } from './workbook-graph';
// Séparateur de milliers de formaterEuros = espace INSÉCABLE ; on construit les attendus via la
// fonction elle-même plutôt que de coder un littéral (robuste au codepoint exact du séparateur).
import { formaterEuros } from './pipe-recrutement';
import {
  PLACEHOLDER,
  MOIS_COURTS,
  anneesSelectionnables,
  regimeMois,
  construireStaffing,
  construireRentabilite,
  construireFactures,
  MENTION_REFERENTIEL_RESTREINT,
  joursOuvres,
  tjmParMission,
  joursPrevusTotal,
  joursRealisesTotal,
  caBudgetMission,
  caRealiseMission
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

describe('factures — état vide honnête (aucun contenu lu)', () => {
  it('aucun gabarit lu → message « aucun gabarit actif lu »', () => {
    const m = construireFactures(etatBase());
    expect(m.lignes).toHaveLength(0);
    expect(m.messageVide).toBe('Aucune facture à émettre — aucun gabarit actif lu');
  });

  it('des gabarits existent mais contenus non lus → message « Aucune facture à émettre. »', () => {
    const m = construireFactures(etatBase({ gabarits: [UN_GABARIT] }));
    expect(m.lignes).toHaveLength(0);
    expect(m.messageVide).toBe('Aucune facture à émettre.');
  });
});

// ===========================================================================
// GOLDEN ancré sur l'épreuve T-0031 (2026-07-17) — calculs §5.4 STRICTS.
// gabarit-1 (Siteflow, code « 1 ») : 8 affectations Σ 148 j ; 2 imputations Σ 39 j ;
//   échéancier Σ 133 200 € → TJM 900. gabarit-2 (Datalab, code « 2 ») : 6 affectations Σ 120 j ;
//   0 imputation ; échéancier Σ 84 000 € → TJM 700.
// ===========================================================================
function moisDate(m0: number): Date { return new Date(Date.UTC(2026, m0, 1)); }

const JP1 = [17, 22, 23, 7, 22, 22, 21, 14]; // Σ = 148
const JP2 = [23, 15, 22, 22, 21, 17];        // Σ = 120

function gabarit1(statutEcheancier: string = 'émise'): ContenuGabarit {
  return {
    codeMission: '1',
    affectations: JP1.map((j, i) => ({ codeMission: '1', ressource: 'r@allia', mois: moisDate(i), joursPrevus: j })),
    // Réalisé : mai (index 4) 17 j + juin (index 5) 22 j = 39 j (T-0031).
    imputations: [
      { codeMission: '1', ressource: 'r@allia', mois: moisDate(4), joursRealises: 17, statutValidation: 'à valider' },
      { codeMission: '1', ressource: 'r@allia', mois: moisDate(5), joursRealises: 22, statutValidation: 'à valider' }
    ],
    echeancier: JP1.map((j, i) => ({ numFacture: `F1-${i}`, codeMission: '1', moisCA: moisDate(i), montantHT: j * 900, echeance: moisDate(i), statut: statutEcheancier, lienFacture: '' }))
  };
}

function gabarit2(): ContenuGabarit {
  return {
    codeMission: '2',
    affectations: JP2.map((j, i) => ({ codeMission: '2', ressource: 's@allia', mois: moisDate(i), joursPrevus: j })),
    imputations: [],
    echeancier: JP2.map((j, i) => ({ numFacture: `F2-${i}`, codeMission: '2', moisCA: moisDate(i), montantHT: j * 700, echeance: moisDate(i), statut: 'émise', lienFacture: '' }))
  };
}

function etatEconomique(contenus: ReadonlyArray<ContenuGabarit>, referentiel?: ContenuReferentiel, refAccessible = false): EtatGabarits {
  return {
    gabarits: contenus.map(c => ({ codeMission: c.codeMission, url: `/x/gabarit-${c.codeMission}.xlsx`, derniereLecture: '17/07/2026 à 09:30' })),
    anomalies: [],
    source: 'ok',
    luLe: '17/07/2026 à 09:30',
    referentielCoutsAccessible: refAccessible,
    referentielEtat: refAccessible ? 'accessible' : 'restreint',
    contenus,
    referentiel
  };
}

describe('§5.4 — TJM dérivé de l’échéancier + CA par mission (golden T-0031)', () => {
  it('Σ JoursPrevus = 148 (m1) / 120 (m2)', () => {
    expect(joursPrevusTotal(gabarit1())).toBe(148);
    expect(joursPrevusTotal(gabarit2())).toBe(120);
  });

  it('TJM = 900 (m1) / 700 (m2) — Σ MontantHT ÷ Σ JoursPrevus', () => {
    expect(tjmParMission(gabarit1())).toBe(900);
    expect(tjmParMission(gabarit2())).toBe(700);
  });

  it('CA budget = 133 200 € (m1) / 84 000 € (m2) = TJM × Σ JoursPrevus', () => {
    expect(caBudgetMission(gabarit1())).toBe(133200);
    expect(caBudgetMission(gabarit2())).toBe(84000);
  });

  it('CA réalisé = 35 100 € (m1 : 39 j × 900) / 0 € (m2 : aucune imputation)', () => {
    expect(joursRealisesTotal(gabarit1())).toBe(39);
    expect(caRealiseMission(gabarit1())).toBe(35100);
    expect(caRealiseMission(gabarit2())).toBe(0);
  });

  it('TJM indérivable (aucun jour prévu ou échéancier vide) → undefined (jamais inventé)', () => {
    expect(tjmParMission({ codeMission: 'X', affectations: [], imputations: [], echeancier: [] })).toBeUndefined();
    expect(caBudgetMission({ codeMission: 'X', affectations: [], imputations: [], echeancier: [] })).toBeUndefined();
  });
});

describe('§5.4 — bandeau Rentabilité (firme, 12 mois) sur le golden', () => {
  it('Total budget = 217 200 € (133 200 + 84 000), Total réalisé = 35 100 €', () => {
    const m = construireRentabilite(etatEconomique([gabarit1(), gabarit2()]), 2026);
    const caTotal = m.lignes.find(l => l.libelle === 'CA total');
    expect(caTotal && caTotal.total.budget).toBe(formaterEuros(217200));
    expect(caTotal && caTotal.total.realise).toBe(formaterEuros(35100));
  });

  it('cellule d’un mois sans affectation = « · » (jamais un zéro inventé)', () => {
    const m = construireRentabilite(etatEconomique([gabarit1(), gabarit2()]), 2026);
    const caTotal = m.lignes.find(l => l.libelle === 'CA total');
    // Décembre (index 11) : aucune affectation dans le golden → budget « · ».
    expect(caTotal && caTotal.cellules[11].budget).toBe(PLACEHOLDER);
    // Janvier (index 0) : m1 (17 j × 900) + m2 (23 j × 700) = 15 300 + 16 100 = 31 400 €.
    expect(caTotal && caTotal.cellules[0].budget).toBe(formaterEuros(31400));
  });

  it('EBITDA sans référentiel accessible → « · » + mention (CA reste calculé)', () => {
    const m = construireRentabilite(etatEconomique([gabarit1(), gabarit2()]), 2026);
    const ebitda = m.lignes.find(l => l.libelle === 'EBITDA');
    expect(ebitda && ebitda.total.budget).toBe(PLACEHOLDER);
    expect(ebitda && ebitda.mention).toBe(MENTION_REFERENTIEL_RESTREINT);
  });

  it('EBITDA avec référentiel accessible = CA − (jours × CoutJour) − structure', () => {
    // Un seul mois (janvier) pour un calcul vérifiable à la main.
    const c: ContenuGabarit = {
      codeMission: '1',
      affectations: [{ codeMission: '1', ressource: 'r@allia', mois: moisDate(0), joursPrevus: 10 }],
      imputations: [],
      echeancier: [{ numFacture: 'F', codeMission: '1', moisCA: moisDate(0), montantHT: 9000, echeance: moisDate(0), statut: 'émise', lienFacture: '' }]
    };
    // TJM = 9000/10 = 900 ; CA budget janvier = 10 × 900 = 9 000.
    const ref: ContenuReferentiel = {
      ressources: [{ ressource: 'r@allia', type: 'salarié', coutJour: 400, dateEntree: moisDate(0) }],
      structure: [{ mois: moisDate(0), posteCout: 'Loyer', montant: 1000 }]
    };
    // EBITDA budget janvier = 9 000 − (10 × 400) − 1 000 = 4 000.
    const m = construireRentabilite(etatEconomique([c], ref, true), 2026);
    const ebitda = m.lignes.find(l => l.libelle === 'EBITDA');
    expect(ebitda && ebitda.mention).toBeUndefined();
    expect(ebitda && ebitda.cellules[0].budget).toBe(formaterEuros(4000));
    expect(ebitda && ebitda.total.budget).toBe(formaterEuros(4000));
  });
});

describe('§5.4 — bandeau Staffing (salariés actifs, hors sous-traitants)', () => {
  it('sans référentiel : « · » partout (impossible d’identifier les salariés)', () => {
    const m = construireStaffing(etatEconomique([gabarit1()]), 2026, 2026, 11);
    for (const b of m.barres) { expect(b.effectif).toBe(PLACEHOLDER); expect(b.pct).toBe(PLACEHOLDER); }
  });

  it('avec référentiel : effectif = salariés actifs, ST exclus, taux = jours ÷ jours ouvrés', () => {
    // Janvier 2026 : 22 jours ouvrés. 1 salarié (r@allia) 11 j prévus → 50 % ; 1 sous-traitant exclu.
    const c: ContenuGabarit = {
      codeMission: '1',
      affectations: [
        { codeMission: '1', ressource: 'r@allia', mois: moisDate(0), joursPrevus: 11 },
        { codeMission: '1', ressource: 'st@ext', mois: moisDate(0), joursPrevus: 20 }
      ],
      imputations: [],
      echeancier: [{ numFacture: 'F', codeMission: '1', moisCA: moisDate(0), montantHT: 9000, echeance: moisDate(0), statut: 'émise', lienFacture: '' }]
    };
    const ref: ContenuReferentiel = {
      ressources: [
        { ressource: 'r@allia', type: 'salarié', coutJour: 400, dateEntree: moisDate(0) },
        { ressource: 'st@ext', type: 'sous-traitant', coutJour: 600, dateEntree: moisDate(0) }
      ],
      structure: []
    };
    // Année future par rapport à « maintenant=2026, mois courant 11 » ? annee 2026 == courante ; janvier (0) < 11 → réalisé.
    // Réalisé sans imputation → 0 jour ; test le régime PRÉVISIONNEL en plaçant le mois courant à 0.
    const m = construireStaffing(etatEconomique([c], ref, true), 2026, 2026, 0);
    const janv = m.barres[0];
    expect(janv.regime).toBe('previsionnel');
    expect(janv.effectif).toBe('1');       // le sous-traitant est exclu
    expect(janv.pct).toBe('50 %');          // 11 j ÷ 22 j ouvrés
  });
});

describe('§5.4 — jours ouvrés (lun-ven, fériés hors périmètre v1)', () => {
  it('janvier 2026 = 22 jours ouvrés ; mai 2026 = 21', () => {
    expect(joursOuvres(2026, 0)).toBe(22);
    expect(joursOuvres(2026, 4)).toBe(21);
  });
});

describe('factures — lignes « à émettre » lues (golden)', () => {
  it('ne retient que les échéances « à émettre », avec montant formaté et lien PDF', () => {
    const g = gabarit1('à émettre'); // les 8 lignes deviennent « à émettre »
    const m = construireFactures(etatEconomique([g]));
    expect(m.lignes).toHaveLength(8);
    expect(m.messageVide).toBeUndefined();
    expect(m.lignes[0].codeMission).toBe('1');
    expect(m.lignes[0].montant).toBe(formaterEuros(15300)); // 17 j × 900
    expect(m.lignes[0].echeance).toBe('01/01/2026');
  });

  it('des gabarits lus mais aucune échéance « à émettre » → message honnête', () => {
    const m = construireFactures(etatEconomique([gabarit1('émise')]));
    expect(m.lignes).toHaveLength(0);
    expect(m.messageVide).toBe('Aucune facture à émettre.');
  });
});
