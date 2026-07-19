// Tests unitaires de la lecture Graph Workbook (cockpit v2 point 2, T-0035). Aucune dépendance
// SPFx / réseau : la primitive `GrapheGet` est injectée par un faux. Couvre les NORMALISATIONS de
// lecture éprouvées T-0031 (date série Excel, CodeMission coercé en entier), le parsing des
// colonnes (dont l'IGNORANCE de la ligne d'insertion Excel vide), la résolution
// site→drive→id du driveItem puis la lecture Workbook PAR ITEM ID (la forme chemin échoue à WAC,
// mesuré S39), et la remontée d'anomalies (schéma cassé) / d'état d'accès référentiel (403 → restreint).

import {
  versDate,
  moisIndexDe,
  anneeDe,
  codeMissionEnString,
  versNombre,
  versTexte,
  parserTableColonnes,
  hoteEtCheminSite,
  localiserDansDrive,
  lireContenus,
  ENTETES_AFFECTATIONS,
  type GrapheGet,
  type ReponseGraphe
} from './workbook-graph';

// ---------------------------------------------------------------------------
// Normalisations de lecture (faits T-0031).
// ---------------------------------------------------------------------------
describe('normalisations de lecture (faits éprouvés T-0031)', () => {
  it('versDate : série Excel 46143 → 2026-05-01 (UTC)', () => {
    const d = versDate(46143);
    expect(d && d.getUTCFullYear()).toBe(2026);
    expect(d && d.getUTCMonth()).toBe(4); // mai (0-based)
    expect(d && d.getUTCDate()).toBe(1);
  });

  it('versDate : chaîne « AAAA-MM-JJ » → même date UTC que la série', () => {
    const d = versDate('2026-05-01');
    expect(d && d.getUTCFullYear()).toBe(2026);
    expect(d && d.getUTCMonth()).toBe(4);
    expect(d && d.getUTCDate()).toBe(1);
  });

  it('versDate : cellule vide / non interprétable → undefined (jamais une date inventée)', () => {
    expect(versDate('')).toBeUndefined();
    expect(versDate(undefined)).toBeUndefined();
    expect(versDate('pas une date')).toBeUndefined();
  });

  it('moisIndexDe / anneeDe extraient mois (0-based) et année en UTC', () => {
    expect(moisIndexDe(46143)).toBe(4);
    expect(anneeDe(46143)).toBe(2026);
  });

  it('codeMissionEnString : entier coercé et chaîne donnent la MÊME clé', () => {
    expect(codeMissionEnString(1)).toBe('1');
    expect(codeMissionEnString('1')).toBe('1');
    expect(codeMissionEnString('  2 ')).toBe('2');
    expect(codeMissionEnString(null)).toBe('');
  });

  it('versNombre : nombre natif, chaîne à virgule décimale et séparateurs de milliers', () => {
    expect(versNombre(148)).toBe(148);
    expect(versNombre('1 234,5')).toBe(1234.5);
    expect(versNombre('')).toBeUndefined();
    expect(versNombre('abc')).toBeUndefined();
  });

  it('versTexte : strip, vide sûr', () => {
    expect(versTexte('  à émettre ')).toBe('à émettre');
    expect(versTexte(undefined)).toBe('');
  });
});

// ---------------------------------------------------------------------------
// Parsing des colonnes Graph (workbook/tables/{name}/columns).
// ---------------------------------------------------------------------------
function colonnes(headers: ReadonlyArray<string>, rows: ReadonlyArray<ReadonlyArray<unknown>>): unknown {
  return {
    value: headers.map((h, ci) => ({
      name: h,
      values: [[h], ...rows.map(r => [r[ci]])]
    }))
  };
}

describe('parserTableColonnes — transpose colonnes → lignes, repère les en-têtes manquants', () => {
  it('transpose et conserve les cellules brutes (normalisation faite par les mappers en aval)', () => {
    const corps = colonnes(ENTETES_AFFECTATIONS, [[1, 'r@allia', 46143, 17], [1, 'b@allia', 46174, 22]]);
    const { lignes, entetesManquants } = parserTableColonnes(corps, ENTETES_AFFECTATIONS);
    expect(entetesManquants).toHaveLength(0);
    expect(lignes).toHaveLength(2);
    expect(lignes[0].CodeMission).toBe(1);
    expect(lignes[0].JoursPrevus).toBe(17);
    expect(lignes[1].Ressource).toBe('b@allia');
  });

  it('en-tête attendu absent → signalé dans entetesManquants (anomalie en aval)', () => {
    const corps = colonnes(['CodeMission', 'Ressource', 'Mois'], [[1, 'r@allia', 46143]]); // JoursPrevus manquant
    const { entetesManquants } = parserTableColonnes(corps, ENTETES_AFFECTATIONS);
    expect(entetesManquants).toEqual(['JoursPrevus']);
  });

  it('corps non conforme (pas de value) → aucune ligne, tous en-têtes manquants', () => {
    const { lignes, entetesManquants } = parserTableColonnes({}, ENTETES_AFFECTATIONS);
    expect(lignes).toHaveLength(0);
    expect(entetesManquants).toEqual([...ENTETES_AFFECTATIONS]);
  });

  it('table avec unique ligne d’insertion vide → zéro ligne de données, aucune anomalie (en-têtes présents)', () => {
    // Fait mesuré S39 : toute table Excel matérialise une ligne de corps entièrement vide (ligne
    // d'insertion), y compris un T_Imputations sans réalisé. Elle ne doit PAS devenir une ligne.
    const corps = colonnes(ENTETES_AFFECTATIONS, [['', '', '', '']]);
    const { lignes, entetesManquants } = parserTableColonnes(corps, ENTETES_AFFECTATIONS);
    expect(lignes).toHaveLength(0);
    expect(entetesManquants).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// Résolution par chemin.
// ---------------------------------------------------------------------------
describe('hoteEtCheminSite — décompose une URL de site', () => {
  it('sépare hôte et chemin server-relative', () => {
    expect(hoteEtCheminSite('https://alliaconsulting.sharepoint.com/sites/Contratsetadministratif'))
      .toEqual({ hote: 'alliaconsulting.sharepoint.com', chemin: '/sites/Contratsetadministratif' });
  });
  it('URL invalide → undefined', () => {
    expect(hoteEtCheminSite('pas une url')).toBeUndefined();
  });
});

describe('localiserDansDrive — chemin du fichier relatif à la racine de SON drive', () => {
  const drives = [
    { id: 'DRIVE_DOCS', webUrl: 'https://h/sites/CA/Documents partages' },
    { id: 'DRIVE_AUTRE', webUrl: 'https://h/sites/CA/Autre' }
  ];
  it('choisit le drive porteur et calcule le chemin interne (espaces intacts)', () => {
    const loc = localiserDansDrive(drives, '/sites/CA/Documents partages/06 - Gabarit ERP/gabarit-1.xlsx');
    expect(loc).toEqual({ driveId: 'DRIVE_DOCS', cheminDansDrive: '/06 - Gabarit ERP/gabarit-1.xlsx' });
  });
  it('aucun drive porteur → undefined', () => {
    expect(localiserDansDrive(drives, '/sites/CA/Inconnu/x.xlsx')).toBeUndefined();
  });
});

// Reproduction du RÉEL (épreuve 2026-07-17) : Graph renvoie le webUrl des drives PERCENT-ENCODÉ
// (« Documents%20partages ») alors que les chemins des props arrivent EN CLAIR (espaces, accents,
// « & »). La comparaison de préfixe doit se faire sur des segments DÉCODÉS des deux côtés, puis le
// résiduel doit être RÉ-ENCODÉ correctement pour l'API `root:{chemin}:`.
describe('localiserDansDrive — webUrl percent-encodé vs chemin props en clair (cas réel)', () => {
  const drives = [
    // webUrl tel que renvoyé par Graph : espaces encodés en %20.
    { id: 'DRIVE_DOCS', webUrl: 'https://h/sites/CA/Documents%20partages' }
  ];

  it('gabarit « 06 - Gabarit ERP » (espaces) : trouve le drive, résiduel ré-encodable', () => {
    const loc = localiserDansDrive(drives, '/sites/CA/Documents partages/06 - Gabarit ERP/gabarit-1.xlsx');
    expect(loc).toEqual({ driveId: 'DRIVE_DOCS', cheminDansDrive: '/06 - Gabarit ERP/gabarit-1.xlsx' });
  });

  it('référentiel « 07 - Coût de Structure » (accent) : trouve le drive', () => {
    const loc = localiserDansDrive(drives, '/sites/CA/Documents partages/07 - Coût de Structure/referentiel-structure.xlsx');
    expect(loc).toEqual({ driveId: 'DRIVE_DOCS', cheminDansDrive: '/07 - Coût de Structure/referentiel-structure.xlsx' });
  });

  it('référentiel « 08 - Coût Masse salariale & Indep » (accent + &) : trouve le drive', () => {
    const loc = localiserDansDrive(drives, '/sites/CA/Documents partages/08 - Coût Masse salariale & Indep/referentiel-ressources.xlsx');
    expect(loc).toEqual({ driveId: 'DRIVE_DOCS', cheminDansDrive: '/08 - Coût Masse salariale & Indep/referentiel-ressources.xlsx' });
  });

  it('symétrie : webUrl en clair + chemin props percent-encodé se correspondent aussi', () => {
    const drivesClair = [{ id: 'DRIVE_DOCS', webUrl: 'https://h/sites/CA/Documents partages' }];
    const loc = localiserDansDrive(drivesClair, '/sites/CA/Documents%20partages/06%20-%20Gabarit%20ERP/gabarit-1.xlsx');
    expect(loc).toEqual({ driveId: 'DRIVE_DOCS', cheminDansDrive: '/06 - Gabarit ERP/gabarit-1.xlsx' });
  });
});

// ---------------------------------------------------------------------------
// Lecture bout-en-bout (lireContenus) avec un Graph injecté.
// ---------------------------------------------------------------------------
const SITE_URL = 'https://alliaconsulting.sharepoint.com/sites/Contratsetadministratif';
const RACINE_DRIVE = 'https://alliaconsulting.sharepoint.com/sites/Contratsetadministratif/Documents partages';
const URL_GAB1 = '/sites/Contratsetadministratif/Documents partages/06 - Gabarit ERP/gabarit-1.xlsx';

/** Faux GrapheGet : route par motif d'URL ; l'ordre des règles compte (plus spécifique d'abord). */
function fauxGraphe(regles: ReadonlyArray<{ readonly quand: (c: string) => boolean; readonly rep: ReponseGraphe }>): GrapheGet {
  return async (chemin: string) => {
    for (const r of regles) { if (r.quand(chemin)) { return r.rep; } }
    return { ok: false, status: 404 };
  };
}

const REP_SITE: ReponseGraphe = { ok: true, status: 200, corps: { id: 'SITE1' } };
const REP_DRIVES: ReponseGraphe = { ok: true, status: 200, corps: { value: [{ id: 'DRIVE1', name: 'Documents partages', webUrl: RACINE_DRIVE }] } };

// Étape 3 : résolution de l'id du driveItem par chemin (`/drives/{id}/root:{chemin}`, SANS /workbook).
// Les appels Workbook passent ensuite par `/drives/{id}/items/{id}/workbook/...` (adressage par id).
const REGLE_ITEM = {
  quand: (c: string) => c.indexOf('root:') >= 0 && c.indexOf('/workbook') < 0,
  rep: { ok: true, status: 200, corps: { id: 'ITEM1' } } as ReponseGraphe
};

function repColonnes(headers: ReadonlyArray<string>, rows: ReadonlyArray<ReadonlyArray<unknown>>): ReponseGraphe {
  return { ok: true, status: 200, corps: colonnes(headers, rows) };
}

describe('lireContenus — nominal, un gabarit (normalisation appliquée)', () => {
  it('lit et normalise les 3 tables ; CodeMission entier → string, série date → Date', async () => {
    const graphe = fauxGraphe([
      { quand: c => c.indexOf('/workbook/tables/T_Affectations/columns') >= 0, rep: repColonnes(ENTETES_AFFECTATIONS, [[1, 'r@allia', 46143, 17]]) },
      { quand: c => c.indexOf('/workbook/tables/T_Imputations/columns') >= 0, rep: repColonnes(['CodeMission', 'Ressource', 'Mois', 'JoursRealises', 'StatutValidation'], [[1, 'r@allia', 46143, 17, 'à valider']]) },
      { quand: c => c.indexOf('/workbook/tables/T_Echeancier/columns') >= 0, rep: repColonnes(['NumFacture', 'CodeMission', 'MoisCA', 'MontantHT', 'Echeance', 'Statut', 'LienFacture'], [['F-1', 1, 46143, 15300, 46160, 'à émettre', 'https://teams/f1.pdf']]) },
      REGLE_ITEM,
      { quand: c => c.indexOf('/drives?') >= 0, rep: REP_DRIVES },
      { quand: c => c.indexOf('$select=id') >= 0 && c.indexOf('/drives/') < 0, rep: REP_SITE }
    ]);

    const res = await lireContenus(graphe, SITE_URL, [{ codeMission: '1', url: URL_GAB1 }]);
    expect(res.anomalies).toHaveLength(0);
    expect(res.gabarits).toHaveLength(1);
    const g = res.gabarits[0];
    expect(g.affectations[0].codeMission).toBe('1'); // entier 1 → « 1 »
    expect(g.affectations[0].ressource).toBe('r@allia');
    expect(g.affectations[0].mois && g.affectations[0].mois.getUTCMonth()).toBe(4); // mai
    expect(g.affectations[0].joursPrevus).toBe(17);
    expect(g.imputations[0].joursRealises).toBe(17);
    expect(g.echeancier[0].montantHT).toBe(15300);
    expect(g.echeancier[0].statut).toBe('à émettre');
    // Pas de référentiel demandé → restreint (non bloquant), aucune anomalie.
    expect(res.referentielEtat).toBe('restreint');
    expect(res.referentiel).toBeUndefined();
  });
});

describe('lireContenus — T_Imputations sans réalisé (unique ligne d’insertion vide)', () => {
  it('gabarit sans réalisé → 0 imputation, aucune anomalie (ligne d’insertion ignorée)', async () => {
    const graphe = fauxGraphe([
      { quand: c => c.indexOf('/workbook/tables/T_Affectations/columns') >= 0, rep: repColonnes(ENTETES_AFFECTATIONS, [[2, 'r@allia', 46143, 23]]) },
      // T_Imputations renvoie l'unique ligne d'insertion, toutes cellules vides (cas mesuré S39).
      { quand: c => c.indexOf('/workbook/tables/T_Imputations/columns') >= 0, rep: repColonnes(['CodeMission', 'Ressource', 'Mois', 'JoursRealises', 'StatutValidation'], [['', '', '', '', '']]) },
      { quand: c => c.indexOf('/workbook/tables/T_Echeancier/columns') >= 0, rep: repColonnes(['NumFacture', 'CodeMission', 'MoisCA', 'MontantHT', 'Echeance', 'Statut', 'LienFacture'], []) },
      REGLE_ITEM,
      { quand: c => c.indexOf('/drives?') >= 0, rep: REP_DRIVES },
      { quand: c => c.indexOf('$select=id') >= 0 && c.indexOf('/drives/') < 0, rep: REP_SITE }
    ]);
    const res = await lireContenus(graphe, SITE_URL, [{ codeMission: '2', url: URL_GAB1 }]);
    expect(res.anomalies).toHaveLength(0);
    expect(res.gabarits[0].imputations).toHaveLength(0);
    expect(res.gabarits[0].affectations).toHaveLength(1);
  });
});

describe('lireContenus — schéma cassé et référentiel restreint', () => {
  it('table au schéma inattendu (en-tête manquant) → anomalie SIGNALÉE (jamais un zéro tu)', async () => {
    const graphe = fauxGraphe([
      { quand: c => c.indexOf('/workbook/tables/T_Affectations/columns') >= 0, rep: repColonnes(['CodeMission', 'Ressource', 'Mois'], [[1, 'r@allia', 46143]]) }, // JoursPrevus manquant
      { quand: c => c.indexOf('/workbook/tables/') >= 0, rep: repColonnes(['x'], []) },
      REGLE_ITEM,
      { quand: c => c.indexOf('/drives?') >= 0, rep: REP_DRIVES },
      { quand: c => c.indexOf('$select=id') >= 0 && c.indexOf('/drives/') < 0, rep: REP_SITE }
    ]);
    const res = await lireContenus(graphe, SITE_URL, [{ codeMission: '1', url: URL_GAB1 }]);
    expect(res.anomalies.length).toBeGreaterThanOrEqual(1);
    expect(res.anomalies.some(a => a.raison.indexOf('schéma inattendu') >= 0)).toBe(true);
  });

  it('référentiel en 403 → referentielEtat « restreint », jamais bloquant', async () => {
    const graphe = fauxGraphe([
      { quand: c => c.indexOf('/workbook/tables/T_Ressources/columns') >= 0, rep: { ok: false, status: 403 } },
      { quand: c => c.indexOf('/workbook/tables/T_Structure/columns') >= 0, rep: { ok: false, status: 403 } },
      { quand: c => c.indexOf('/workbook/tables/') >= 0, rep: repColonnes(ENTETES_AFFECTATIONS, []) },
      REGLE_ITEM,
      { quand: c => c.indexOf('/drives?') >= 0, rep: REP_DRIVES },
      { quand: c => c.indexOf('$select=id') >= 0 && c.indexOf('/drives/') < 0, rep: REP_SITE }
    ]);
    const res = await lireContenus(graphe, SITE_URL, [{ codeMission: '1', url: URL_GAB1 }], {
      ressources: '/sites/Contratsetadministratif/Documents partages/08 - Coût Masse salariale & Indep/referentiel-ressources.xlsx',
      structure: '/sites/Contratsetadministratif/Documents partages/07 - Coût de Structure/referentiel-structure.xlsx'
    });
    expect(res.referentielEtat).toBe('restreint');
    expect(res.referentiel).toBeUndefined();
  });
});
