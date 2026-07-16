// Tests unitaires de la couche de découverte des gabarits (cockpit v2, point 1).
// Cible : tour-de-controle.md v2.1 §3/§4, modele-donnees.md §5.2/§5.5. Aucune dépendance SPFx :
// les primitives réseau (LecteurDossier / SondeReferentiel) sont injectées par des faux.

import {
  FICHIER_SOUCHE_VIERGE,
  DOSSIER_GABARITS_ACTIFS,
  classerFichiersGabarits,
  decouvrirGabarits,
  formaterHorodatage,
  formaterFraicheur,
  type FichierDossier,
  type LecteurDossier,
  type SondeReferentiel,
  type ResultatDossier,
  type EtatAcces,
  type EtatGabarits
} from './gabarits';

const LU_LE = '16/07/2026 à 09:30';

function fichier(nom: string, modifieLe?: string): FichierDossier {
  return { nom, url: `/sites/Contratsetadministratif/Documents/06 - Gabarit ERP/${nom}`, modifieLe };
}

function lecteur(res: ResultatDossier): LecteurDossier {
  return async () => res;
}

function sonde(etat: EtatAcces): SondeReferentiel {
  return async () => etat;
}

describe('classerFichiersGabarits — convention de dépôt §5.2', () => {
  it('retient gabarit-<CodeMission>.xlsx et en extrait le CodeMission', () => {
    const { gabarits, anomalies } = classerFichiersGabarits(
      [fichier('gabarit-2.xlsx'), fichier('gabarit-SITEFLOW-1.xlsx')],
      LU_LE
    );
    expect(anomalies).toHaveLength(0);
    expect(gabarits.map(g => g.codeMission)).toEqual(['2', 'SITEFLOW-1']);
    expect(gabarits[0].derniereLecture).toBe(LU_LE);
  });

  it('exclut la souche vierge SANS la compter comme anomalie', () => {
    const { gabarits, anomalies } = classerFichiersGabarits([fichier(FICHIER_SOUCHE_VIERGE)], LU_LE);
    expect(gabarits).toHaveLength(0);
    expect(anomalies).toHaveLength(0);
  });

  it('signale un fichier étranger à la racine (jamais ignoré silencieusement)', () => {
    const { gabarits, anomalies } = classerFichiersGabarits(
      [fichier('gabarit-2.xlsx'), fichier('notes-reunion.docx')],
      LU_LE
    );
    expect(gabarits).toHaveLength(1);
    expect(anomalies).toHaveLength(1);
    expect(anomalies[0].source).toBe('notes-reunion.docx');
  });

  it('« gabarit-.xlsx » (sans code du tout) ne matche pas le motif → fichier non conforme', () => {
    const { gabarits, anomalies } = classerFichiersGabarits([fichier('gabarit-.xlsx')], LU_LE);
    expect(gabarits).toHaveLength(0);
    expect(anomalies).toHaveLength(1);
    expect(anomalies[0].raison).toContain('non conforme');
  });

  it('signale un gabarit dont le CodeMission est vide/blanc (« gabarit- .xlsx »)', () => {
    const { gabarits, anomalies } = classerFichiersGabarits([fichier('gabarit- .xlsx')], LU_LE);
    expect(gabarits).toHaveLength(0);
    expect(anomalies).toHaveLength(1);
    expect(anomalies[0].raison).toContain('CodeMission');
  });

  it('propage le modifieLe du fichier quand il est connu', () => {
    const { gabarits } = classerFichiersGabarits([fichier('gabarit-9.xlsx', '2026-07-15T05:00:00Z')], LU_LE);
    expect(gabarits[0].modifieLe).toBe('2026-07-15T05:00:00Z');
  });
});

describe('formaterHorodatage — local, zéro-remplissage sans padStart', () => {
  it('rend « JJ/MM/AAAA à HH:MM »', () => {
    // Date locale : le rendu utilise les getters locaux → déterministe quel que soit le fuseau.
    expect(formaterHorodatage(new Date(2026, 6, 16, 9, 5))).toBe('16/07/2026 à 09:05');
    expect(formaterHorodatage(new Date(2026, 0, 1, 14, 30))).toBe('01/01/2026 à 14:30');
  });
});

describe('decouvrirGabarits — orchestration, fail-visible', () => {
  const maintenant = new Date(2026, 6, 16, 9, 30);

  it('dossier ok : classe les gabarits, horodate, référentiel accessible → flag true', async () => {
    const etat = await decouvrirGabarits(
      lecteur({ etat: 'ok', fichiers: [fichier('gabarit-2.xlsx'), fichier(FICHIER_SOUCHE_VIERGE)] }),
      sonde('accessible'),
      maintenant
    );
    expect(etat.source).toBe('ok');
    expect(etat.gabarits).toHaveLength(1);
    expect(etat.anomalies).toHaveLength(0);
    expect(etat.luLe).toBe('16/07/2026 à 09:30');
    expect(etat.referentielCoutsAccessible).toBe(true);
    expect(etat.referentielEtat).toBe('accessible');
  });

  it('dossier non câblé : état LÉGITIME, ni gabarit ni anomalie', async () => {
    const etat = await decouvrirGabarits(lecteur({ etat: 'non_cable' }), sonde('restreint'), maintenant);
    expect(etat.source).toBe('non_cable');
    expect(etat.gabarits).toHaveLength(0);
    expect(etat.anomalies).toHaveLength(0);
  });

  it('dossier indisponible : signalé comme anomalie (jamais tu)', async () => {
    const etat = await decouvrirGabarits(lecteur({ etat: 'indisponible' }), sonde('restreint'), maintenant);
    expect(etat.source).toBe('indisponible');
    expect(etat.anomalies).toHaveLength(1);
    expect(etat.anomalies[0].source).toBe(DOSSIER_GABARITS_ACTIFS);
  });

  it('référentiel restreint (403/404) : flag false SANS anomalie bloquante', async () => {
    const etat = await decouvrirGabarits(
      lecteur({ etat: 'ok', fichiers: [] }),
      sonde('restreint'),
      maintenant
    );
    expect(etat.referentielCoutsAccessible).toBe(false);
    expect(etat.referentielEtat).toBe('restreint');
    expect(etat.anomalies).toHaveLength(0);
  });
});

describe('formaterFraicheur — bandeau de fraîcheur commun §3', () => {
  const base: EtatGabarits = {
    gabarits: [],
    anomalies: [],
    source: 'ok',
    luLe: LU_LE,
    referentielCoutsAccessible: false,
    referentielEtat: 'restreint'
  };

  it('sans anomalie : « lu le … » seul, aucune phrase d’anomalie', () => {
    const f = formaterFraicheur(base);
    expect(f.luLe).toBe(LU_LE);
    expect(f.anomalies).toBeUndefined();
  });

  it('avec anomalies : liste les sources, accord singulier/pluriel', () => {
    const un = formaterFraicheur({ ...base, anomalies: [{ source: 'gabarit-.xlsx', raison: 'x' }] });
    expect(un.anomalies).toBe('1 gabarit en anomalie : gabarit-.xlsx');
    const deux = formaterFraicheur({
      ...base,
      anomalies: [{ source: 'A', raison: 'x' }, { source: 'B', raison: 'y' }]
    });
    expect(deux.anomalies).toBe('2 gabarits en anomalie : A, B');
  });
});
