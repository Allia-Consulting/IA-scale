// Tests unitaires des bandeaux pipe commercial + recrutement (cockpit v2) — logique PURE.
// Cible : tour-de-controle.md v2.0 §3 (bandeaux 2 et 3). Aucune dépendance SPFx.

import type { Ecriture } from './types';
import {
  compterComptesClients,
  opportunitesEnProposition,
  montantPropose,
  pipePondere,
  projeterOpportunites,
  apercuNomMission,
  compterCandidatsEtape,
  formaterEuros,
  optionsEcriture,
  champsCreationOpportunite,
  champsChangementEtape,
  champsChangementMontant,
  creerOpportunite,
  changerEtapeOpportunite,
  changerMontantOpportunite,
  QUERY_RECRUTEMENT,
  Ecrivain,
  ETAPE_QUALIFICATION,
  COL_ETAPE_CRM,
  COL_MONTANT_CRM,
  COL_STATUT_COMPTE,
  COL_ETAPE_CANDIDAT,
  COL_NOM_OPPORTUNITE,
  COL_COMPTE,
  COL_ECHEANCE
} from './pipe-recrutement';

describe('pipe commercial — pondération', () => {
  const crm = [
    { [COL_ETAPE_CRM]: 'Proposition', [COL_MONTANT_CRM]: 1000 },
    { [COL_ETAPE_CRM]: 'Qualification', [COL_MONTANT_CRM]: 1000 }
  ];

  it('montant proposé = Σ Montant en Proposition uniquement (Qualification exclue)', () => {
    expect(montantPropose(crm)).toBe(1000);
  });

  it('pipe pondéré = 1000×0,60 + 1000×0,15 = 750 (pondérations figées 60/15)', () => {
    expect(pipePondere(crm)).toBe(750);
  });

  it('les étapes hors table (Gagnée, Perdue) pèsent 0 au pondéré', () => {
    const avecGagnee = [
      ...crm,
      { [COL_ETAPE_CRM]: 'Gagnée', [COL_MONTANT_CRM]: 100000 },
      { [COL_ETAPE_CRM]: 'Perdue', [COL_MONTANT_CRM]: 50000 }
    ];
    expect(pipePondere(avecGagnee)).toBe(750);
    expect(montantPropose(avecGagnee)).toBe(1000);
  });

  it('opportunitesEnProposition ne retient que l’étape Proposition', () => {
    expect(opportunitesEnProposition(crm)).toHaveLength(1);
  });

  it('montant robuste : une valeur string est coercée, une valeur absente vaut 0', () => {
    const sales = [
      { [COL_ETAPE_CRM]: 'Proposition', [COL_MONTANT_CRM]: '2000' },
      { [COL_ETAPE_CRM]: 'Proposition' }
    ];
    expect(montantPropose(sales)).toBe(2000);
  });
});

describe('pipe commercial — comptes actifs', () => {
  it('ne compte que Statut = Client (Prospect / Inactif exclus)', () => {
    const comptes = [
      { [COL_STATUT_COMPTE]: 'Client' },
      { [COL_STATUT_COMPTE]: 'Prospect' },
      { [COL_STATUT_COMPTE]: 'Client' },
      { [COL_STATUT_COMPTE]: 'Inactif' }
    ];
    expect(compterComptesClients(comptes)).toBe(2);
  });
});

describe('formaterEuros', () => {
  it('entier FR à espaces INSÉCABLES de milliers (U+00A0 — pas de coupure de devise)', () => {
    const nbsp = ' ';
    expect(formaterEuros(75000)).toBe(`75${nbsp}000${nbsp}€`);
    expect(formaterEuros(0)).toBe(`0${nbsp}€`);
    expect(formaterEuros(999.6)).toBe(`1${nbsp}000${nbsp}€`);
  });
});

describe('recrutement — agrégats par étape', () => {
  const candidats = [
    { [COL_ETAPE_CANDIDAT]: 'E1' },
    { [COL_ETAPE_CANDIDAT]: 'E1' },
    { [COL_ETAPE_CANDIDAT]: 'E2' },
    { [COL_ETAPE_CANDIDAT]: 'E3' },
    { [COL_ETAPE_CANDIDAT]: 'Proposition' }
  ];

  it('compte E1 / E2 / E3 et Décisions en cours (Proposition)', () => {
    expect(compterCandidatsEtape(candidats, 'E1')).toBe(2);
    expect(compterCandidatsEtape(candidats, 'E2')).toBe(1);
    expect(compterCandidatsEtape(candidats, 'E3')).toBe(1);
    expect(compterCandidatsEtape(candidats, 'Proposition')).toBe(1);
  });

  it('RGPD : la requête ne sélectionne QUE la colonne Etape — aucun champ nominatif', () => {
    expect(QUERY_RECRUTEMENT).toContain('$select=Etape');
    for (const nominatif of ['Title', 'NomCandidat', 'Owner', 'ResponsableAction', 'Email', 'Telephone', 'Interviewer']) {
      expect(QUERY_RECRUTEMENT).not.toContain(nominatif);
    }
  });
});

describe('ecrireListe — en-têtes (optionsEcriture, source unique de vérité)', () => {
  it('création : Accept odata.metadata=none, pas de MERGE', () => {
    const o = optionsEcriture('create', { Foo: 1 });
    expect(o.headers.Accept).toBe('application/json;odata.metadata=none');
    expect(o.headers['Content-Type']).toBe('application/json');
    expect(o.headers['X-HTTP-Method']).toBeUndefined();
    // Piège du 406 : jamais 'odata=nometadata'.
    expect(o.headers.Accept).not.toContain('nometadata');
  });

  it('mise à jour : X-HTTP-Method MERGE + IF-MATCH *', () => {
    const o = optionsEcriture('update', { Etape: 'Gagnée' });
    expect(o.headers['X-HTTP-Method']).toBe('MERGE');
    expect(o.headers['IF-MATCH']).toBe('*');
    expect(o.headers.Accept).toBe('application/json;odata.metadata=none');
    expect(JSON.parse(o.body).Etape).toBe('Gagnée');
  });
});

describe('gestes pipe — creerOpportunite / changerEtapeOpportunite / changerMontantOpportunite', () => {
  it('champsCreationOpportunite mappe noms internes + rattachement CompteId + échéance', () => {
    const corps = champsCreationOpportunite({ nom: 'O-009', compteId: 7, montant: 5000, etape: 'Proposition', echeance: '2026-09-01' });
    expect(corps[COL_NOM_OPPORTUNITE]).toBe('O-009');
    // Un lookup s'écrit par son champ id numérique `<NomInterne>Id`.
    expect(corps[`${COL_COMPTE}Id`]).toBe(7);
    expect(corps[COL_MONTANT_CRM]).toBe(5000);
    expect(corps[COL_ETAPE_CRM]).toBe('Proposition');
    expect(corps[COL_ECHEANCE]).toBe('2026-09-01');
    // Manques documentés (hors périmètre) : ni Title (O-NNN), ni Responsable, ni CodeMission.
    expect(corps.Title).toBeUndefined();
    expect(corps.Responsable).toBeUndefined();
    expect(corps.CodeMission).toBeUndefined();
  });

  it('champsCreationOpportunite : étape par défaut Qualification, échéance omise si absente', () => {
    const corps = champsCreationOpportunite({ nom: 'O-012', compteId: 3, montant: 100 });
    expect(corps[COL_ETAPE_CRM]).toBe(ETAPE_QUALIFICATION);
    expect(COL_ECHEANCE in corps).toBe(false);
  });

  it('champsChangementEtape ne touche que l’étape', () => {
    const corps = champsChangementEtape('Gagnée');
    expect(corps[COL_ETAPE_CRM]).toBe('Gagnée');
    expect(Object.keys(corps)).toEqual([COL_ETAPE_CRM]);
  });

  it('champsChangementMontant ne touche que le montant', () => {
    const corps = champsChangementMontant(8000);
    expect(corps[COL_MONTANT_CRM]).toBe(8000);
    expect(Object.keys(corps)).toEqual([COL_MONTANT_CRM]);
  });

  it('creerOpportunite délègue à l’Ecrivain sur la liste CRM, sans id (création)', async () => {
    const appels: Array<{ titre: string; champs: Record<string, unknown>; id?: number }> = [];
    const ecrire: Ecrivain = async (titre, champs, id) => {
      appels.push({ titre, champs, id });
      return { etat: 'ok' } as Ecriture;
    };
    const r = await creerOpportunite(ecrire, { nom: 'O-010', compteId: 5, montant: 12000, etape: 'Proposition' });
    expect(r.etat).toBe('ok');
    expect(appels).toHaveLength(1);
    expect(appels[0].titre).toBe('CRM');
    expect(appels[0].id).toBeUndefined();
    expect(appels[0].champs[COL_NOM_OPPORTUNITE]).toBe('O-010');
    expect(appels[0].champs[`${COL_COMPTE}Id`]).toBe(5);
  });

  it('changerEtapeOpportunite délègue avec l’id (mise à jour)', async () => {
    const appels: Array<{ titre: string; champs: Record<string, unknown>; id?: number }> = [];
    const ecrire: Ecrivain = async (titre, champs, id) => {
      appels.push({ titre, champs, id });
      return { etat: 'ok' } as Ecriture;
    };
    await changerEtapeOpportunite(ecrire, 42, 'Gagnée');
    expect(appels[0].titre).toBe('CRM');
    expect(appels[0].id).toBe(42);
    expect(appels[0].champs[COL_ETAPE_CRM]).toBe('Gagnée');
  });

  it('changerMontantOpportunite délègue avec l’id + le seul champ Montant', async () => {
    const appels: Array<{ titre: string; champs: Record<string, unknown>; id?: number }> = [];
    const ecrire: Ecrivain = async (titre, champs, id) => {
      appels.push({ titre, champs, id });
      return { etat: 'ok' } as Ecriture;
    };
    await changerMontantOpportunite(ecrire, 7, 9000);
    expect(appels[0].titre).toBe('CRM');
    expect(appels[0].id).toBe(7);
    expect(appels[0].champs[COL_MONTANT_CRM]).toBe(9000);
    expect(Object.keys(appels[0].champs)).toEqual([COL_MONTANT_CRM]);
  });

  it('propage un refus d’écriture (403 → refuse) sans lever', async () => {
    const ecrire: Ecrivain = async () => ({ etat: 'refuse' } as Ecriture);
    const r = await creerOpportunite(ecrire, { nom: 'O-011', compteId: 1, montant: 1, etape: 'Qualification' });
    expect(r.etat).toBe('refuse');
  });
});

describe('projection OpportuniteLigne', () => {
  it('mappe Id + colonnes, avec le NOM LISIBLE du compte (expand Compte/NomCompte)', () => {
    const lignes = [
      { Id: 3, NomOpportunite: 'O-003', Etape: 'Proposition', Montant: 4000, Compte: { Title: 'CPT-002', NomCompte: 'Arabelle Solutions' } }
    ];
    const [o] = projeterOpportunites(lignes);
    expect(o.id).toBe(3);
    expect(o.nom).toBe('O-003');
    expect(o.etape).toBe('Proposition');
    expect(o.montant).toBe(4000);
    // Nom LISIBLE (« Arabelle Solutions »), jamais le code Title (« CPT-002 »).
    expect(o.compte).toBe('Arabelle Solutions');
  });

  it('compte = undefined si seul le Title (code CPT-xxx) est présent — pas de repli silencieux', () => {
    const [o] = projeterOpportunites([{ Compte: { Title: 'CPT-009' } }]);
    expect(o.compte).toBeUndefined();
  });

  it('tolère les champs absents (id 0, nom de repli, étape vide, montant 0, compte indéfini)', () => {
    const [o] = projeterOpportunites([{}]);
    expect(o.id).toBe(0);
    expect(o.nom).toBe('(sans nom)');
    expect(o.etape).toBe('');
    expect(o.montant).toBe(0);
    expect(o.compte).toBeUndefined();
  });

  it('coerce un Montant string et lit un Id string (robustesse SharePoint)', () => {
    const [o] = projeterOpportunites([{ ID: '11', Montant: '2500' }]);
    expect(o.id).toBe(11);
    expect(o.montant).toBe(2500);
  });
});

describe('apercuNomMission — miroir 3 segments de _composer_nom_espace', () => {
  it('cas nominal → « AAAA - Client - Nom » (3 segments, sans code)', () => {
    const r = apercuNomMission('2026', 'Arabelle Solutions', 'Leader M365');
    expect(r).toEqual({ ok: true, nom: '2026 - Arabelle Solutions - Leader M365' });
  });

  it('accents et espaces internes autorisés', () => {
    const r = apercuNomMission('2026', 'Éléa Conseil', 'Revue à mi-parcours');
    expect(r).toEqual({ ok: true, nom: '2026 - Éléa Conseil - Revue à mi-parcours' });
  });

  it('réduit les espaces multiples et strippe les extrémités', () => {
    const r = apercuNomMission('2026', '  Arabelle   Solutions  ', ' Leader   M365 ');
    expect(r).toEqual({ ok: true, nom: '2026 - Arabelle Solutions - Leader M365' });
  });

  it('caractère interdit dans une composante → refus (ok:false, raison)', () => {
    const r = apercuNomMission('2026', 'Arabelle/Solutions', 'Leader M365');
    expect(r.ok).toBe(false);
    if (!r.ok) { expect(r.raison).toMatch(/interdit/); }
  });

  it('composante vide (client absent) → refus', () => {
    const r = apercuNomMission('2026', '   ', 'Leader M365');
    expect(r.ok).toBe(false);
  });

  it('composante > 60 caractères → refus (cap 60)', () => {
    const r = apercuNomMission('2026', 'A'.repeat(61), 'Leader M365');
    expect(r.ok).toBe(false);
  });

  it('séquence « .. » et point en tête/fin → refus', () => {
    expect(apercuNomMission('2026', 'Arabelle', 'a..b').ok).toBe(false);
    expect(apercuNomMission('2026', 'Arabelle', '.leader').ok).toBe(false);
    expect(apercuNomMission('2026', 'Arabelle', 'leader.').ok).toBe(false);
  });

  it('année invalide (non 4 chiffres) ou hors bornes [2020..2100] → refus', () => {
    expect(apercuNomMission('20260', 'Arabelle', 'Leader').ok).toBe(false);
    expect(apercuNomMission('abcd', 'Arabelle', 'Leader').ok).toBe(false);
    expect(apercuNomMission('1999', 'Arabelle', 'Leader').ok).toBe(false);
    expect(apercuNomMission('2101', 'Arabelle', 'Leader').ok).toBe(false);
  });
});
