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
  QUERY_GESTES_RECRUTEMENT,
  Ecrivain,
  ETAPE_QUALIFICATION,
  COL_ETAPE_CRM,
  COL_MONTANT_CRM,
  COL_STATUT_COMPTE,
  COL_ETAPE_CANDIDAT,
  COL_NOM_OPPORTUNITE,
  COL_COMPTE,
  COL_ECHEANCE,
  COL_NOM_CANDIDAT,
  COL_GRADE,
  COL_SOURCE,
  COL_EMAIL,
  COL_TELEPHONE,
  ETAPE_CANDIDAT_E1,
  ETAPE_CANDIDAT_ACCEPTEE,
  ETAPE_CANDIDAT_REFUSEE,
  prochainTitleCandidat,
  projeterCandidats,
  champsCreationCandidat,
  champsChangementEtapeCandidat,
  creerCandidat,
  changerEtapeCandidat,
  LISTE_CANDIDATS
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

  it('RGPD : la requête AGRÉGAT ne sélectionne QUE la colonne Etape — aucun champ nominatif', () => {
    expect(QUERY_RECRUTEMENT).toContain('$select=Etape');
    for (const nominatif of ['Title', 'NomCandidat', 'Owner', 'ResponsableAction', 'Email', 'Telephone', 'Interviewer']) {
      expect(QUERY_RECRUTEMENT).not.toContain(nominatif);
    }
  });

  it('RGPD : la requête des GESTES est distincte, borne les champs, et n’expose NI Email NI Telephone', () => {
    // La requête nominative des gestes est ACL-gated (§3) ; elle ne tire que le strict nécessaire
    // à l'action et JAMAIS Email/Telephone (qui ne migrent pas non plus vers Ressources-Profil).
    expect(QUERY_GESTES_RECRUTEMENT).toContain('NomCandidat');
    expect(QUERY_GESTES_RECRUTEMENT).toContain('Grade');
    expect(QUERY_GESTES_RECRUTEMENT).not.toContain('Email');
    expect(QUERY_GESTES_RECRUTEMENT).not.toContain('Telephone');
    expect(QUERY_GESTES_RECRUTEMENT).not.toContain('ResponsableAction');
  });
});

describe('recrutement — allocation C-NNN (prochainTitleCandidat)', () => {
  it('max des ^C-(\\d+)$ + 1, zéro-paddé sur 3', () => {
    const candidats = [{ Title: 'C-001' }, { Title: 'C-014' }, { Title: 'C-007' }];
    expect(prochainTitleCandidat(candidats)).toBe('C-015');
  });

  it('liste vide → C-001', () => {
    expect(prochainTitleCandidat([])).toBe('C-001');
  });

  it('liste SANS aucun motif C- (Title non conformes / absents) → C-001', () => {
    // Scorie réelle : candidats 1..7 aux Title non conformes — ils sont IGNORÉS, jamais une erreur.
    const candidats = [{ Title: 'Julie Martin' }, { Title: '' }, { NomCandidat: 'X' }, {}];
    expect(prochainTitleCandidat(candidats)).toBe('C-001');
  });

  it('mélange conformes / non conformes → max des seuls conformes + 1', () => {
    const candidats = [{ Title: 'Julie Martin' }, { Title: 'C-009' }, { Title: 'brouillon' }];
    expect(prochainTitleCandidat(candidats)).toBe('C-010');
  });

  it('au-delà de 999, le padding ne tronque pas (C-1000)', () => {
    expect(prochainTitleCandidat([{ Title: 'C-999' }])).toBe('C-1000');
  });
});

describe('recrutement — projeterCandidats', () => {
  it('mappe Id + Title + NomCandidat + Grade + Etape (tolérant aux absents)', () => {
    const [c] = projeterCandidats([
      { Id: 5, Title: 'C-005', [COL_NOM_CANDIDAT]: 'Julie Martin', [COL_GRADE]: 'Manager', [COL_ETAPE_CANDIDAT]: 'E2' }
    ]);
    expect(c).toEqual({ id: 5, title: 'C-005', nom: 'Julie Martin', grade: 'Manager', etape: 'E2' });
  });

  it('champs absents → défauts sobres (id 0, chaînes vides)', () => {
    const [c] = projeterCandidats([{}]);
    expect(c).toEqual({ id: 0, title: '', nom: '', grade: '', etape: '' });
  });
});

describe('recrutement — geste « ajouter un candidat »', () => {
  it('champsCreationCandidat : Title alloué, étape E1, téléphone inclus si fourni', () => {
    const corps = champsCreationCandidat({
      title: 'C-008', nom: 'Julie Martin', grade: 'Consultant', source: 'LinkedIn',
      email: 'julie@example.com', telephone: '0600000000'
    });
    expect(corps.Title).toBe('C-008');
    expect(corps[COL_NOM_CANDIDAT]).toBe('Julie Martin');
    expect(corps[COL_GRADE]).toBe('Consultant');
    expect(corps[COL_SOURCE]).toBe('LinkedIn');
    expect(corps[COL_EMAIL]).toBe('julie@example.com');
    expect(corps[COL_ETAPE_CANDIDAT]).toBe(ETAPE_CANDIDAT_E1);
    expect(corps[COL_TELEPHONE]).toBe('0600000000');
  });

  it('champsCreationCandidat : téléphone OMIS si vide/absent (optionnel)', () => {
    const corps = champsCreationCandidat({ title: 'C-009', nom: 'A B', grade: 'Consultant', source: 'Cooptation', email: 'a@b.c' });
    expect(COL_TELEPHONE in corps).toBe(false);
    const corps2 = champsCreationCandidat({ title: 'C-010', nom: 'A B', grade: 'Consultant', source: 'Cooptation', email: 'a@b.c', telephone: '   ' });
    expect(COL_TELEPHONE in corps2).toBe(false);
  });

  it('creerCandidat délègue à l’Ecrivain sur la liste Candidats, sans id (création)', async () => {
    const appels: Array<{ titre: string; champs: Record<string, unknown>; id?: number }> = [];
    const ecrire: Ecrivain = async (titre, champs, id) => { appels.push({ titre, champs, id }); return { etat: 'ok' }; };
    const r = await creerCandidat(ecrire, { title: 'C-011', nom: 'A B', grade: 'Manager', source: 'Chasseur', email: 'a@b.c' });
    expect(r.etat).toBe('ok');
    expect(appels[0].titre).toBe(LISTE_CANDIDATS);
    expect(appels[0].id).toBeUndefined();
    expect(appels[0].champs.Title).toBe('C-011');
  });
});

describe('recrutement — geste « changement d’étape » avec garde « Acceptée »', () => {
  it('champsChangementEtapeCandidat ne touche que l’étape (cas nominal)', () => {
    const corps = champsChangementEtapeCandidat(ETAPE_CANDIDAT_REFUSEE);
    expect(corps[COL_ETAPE_CANDIDAT]).toBe(ETAPE_CANDIDAT_REFUSEE);
    expect(Object.keys(corps)).toEqual([COL_ETAPE_CANDIDAT]);
  });

  it('GARDE : « Acceptée » par cette voie LÈVE (la cascade seule y mène)', () => {
    expect(() => champsChangementEtapeCandidat(ETAPE_CANDIDAT_ACCEPTEE)).toThrow(/cascade/i);
  });

  it('changerEtapeCandidat délègue avec l’id (mise à jour), et propage la garde « Acceptée »', async () => {
    const appels: Array<{ titre: string; id?: number }> = [];
    const ecrire: Ecrivain = async (titre, _champs, id) => { appels.push({ titre, id }); return { etat: 'ok' }; };
    await changerEtapeCandidat(ecrire, 42, 'E3');
    expect(appels[0].titre).toBe(LISTE_CANDIDATS);
    expect(appels[0].id).toBe(42);
    // La garde interdit « Acceptée » AVANT tout appel réseau (aucun nouvel appel enregistré).
    await expect(async () => { await changerEtapeCandidat(ecrire, 42, ETAPE_CANDIDAT_ACCEPTEE); }).rejects.toThrow(/cascade/i);
    expect(appels).toHaveLength(1);
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
