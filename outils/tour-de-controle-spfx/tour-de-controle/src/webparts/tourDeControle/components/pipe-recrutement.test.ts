// Tests unitaires des bandeaux pipe commercial + recrutement (cockpit v2) — logique PURE.
// Cible : tour-de-controle.md v2.0 §3 (bandeaux 2 et 3). Aucune dépendance SPFx.

import type { Ecriture } from './types';
import {
  compterComptesClients,
  opportunitesEnProposition,
  montantPropose,
  pipePondere,
  compterCandidatsEtape,
  formaterEuros,
  optionsEcriture,
  champsCreationOpportunite,
  champsChangementEtape,
  creerOpportunite,
  changerEtapeOpportunite,
  QUERY_RECRUTEMENT,
  Ecrivain,
  COL_ETAPE_CRM,
  COL_MONTANT_CRM,
  COL_STATUT_COMPTE,
  COL_ETAPE_CANDIDAT,
  COL_NOM_OPPORTUNITE
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

describe('gestes pipe — creerOpportunite / changerEtapeOpportunite (prêts à brancher)', () => {
  it('champsCreationOpportunite mappe les noms internes de colonnes', () => {
    const corps = champsCreationOpportunite({ nom: 'O-009', montant: 5000, etape: 'Qualification' });
    expect(corps[COL_NOM_OPPORTUNITE]).toBe('O-009');
    expect(corps[COL_MONTANT_CRM]).toBe(5000);
    expect(corps[COL_ETAPE_CRM]).toBe('Qualification');
  });

  it('champsChangementEtape ne touche que l’étape', () => {
    const corps = champsChangementEtape('Gagnée');
    expect(corps[COL_ETAPE_CRM]).toBe('Gagnée');
    expect(Object.keys(corps)).toEqual([COL_ETAPE_CRM]);
  });

  it('creerOpportunite délègue à l’Ecrivain sur la liste CRM, sans id (création)', async () => {
    const appels: Array<{ titre: string; champs: Record<string, unknown>; id?: number }> = [];
    const ecrire: Ecrivain = async (titre, champs, id) => {
      appels.push({ titre, champs, id });
      return { etat: 'ok' } as Ecriture;
    };
    const r = await creerOpportunite(ecrire, { nom: 'O-010', montant: 12000, etape: 'Proposition' });
    expect(r.etat).toBe('ok');
    expect(appels).toHaveLength(1);
    expect(appels[0].titre).toBe('CRM');
    expect(appels[0].id).toBeUndefined();
    expect(appels[0].champs[COL_NOM_OPPORTUNITE]).toBe('O-010');
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

  it('propage un refus d’écriture (403 → refuse) sans lever', async () => {
    const ecrire: Ecrivain = async () => ({ etat: 'refuse' } as Ecriture);
    const r = await creerOpportunite(ecrire, { nom: 'O-011', montant: 1, etape: 'Qualification' });
    expect(r.etat).toBe('refuse');
  });
});
