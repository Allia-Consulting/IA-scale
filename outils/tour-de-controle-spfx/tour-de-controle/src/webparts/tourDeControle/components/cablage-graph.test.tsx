// Test de CÂBLAGE — le trou des 81 tests purs (T-0035, reprise du 17/07/2026).
//
// Les 81 tests d'origine étaient tous PURS : normalisations, parsing, calculs — jamais le câblage.
// L'épreuve du réel a échoué SANS qu'aucun test rouge ne l'annonce : aucun appel Graph n'était
// émis et l'échec était MUET. Ce test monte le VRAI composant React avec des props CÂBLÉES et un
// Graph mocké, et asserte que :
//   1. la lecture Graph EST invoquée au montage (getClient('3') + GET workbook/tables/.../columns) ;
//   2. les modèles chargés ne sont PAS vides (le placeholder de chargement a disparu) ;
//   3. quand le client Graph échoue, l'anomalie est SURFACÉE avec sa cause + console.error (jamais muet).

jest.mock('@microsoft/sp-http', () => ({
  SPHttpClient: { configurations: { v1: {} } }
}), { virtual: true });

import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { act } from 'react-dom/test-utils';
import TourDeControle from './TourDeControle';
import type { ITourDeControleProps } from './ITourDeControleProps';

const HOTE = 'https://alliaconsulting.sharepoint.com';
const SITE_CA = `${HOTE}/sites/CA`;
const RACINE_DRIVE = `${HOTE}/sites/CA/Documents partages`;
const DOSSIER = '/sites/CA/Documents partages/06 - Gabarit ERP';

function rep(status: number, body: unknown): unknown {
  return { status, ok: status >= 200 && status < 300, json: async () => body };
}

/** spHttpClient mocké : listing REST du dossier des gabarits (1 gabarit actif) + sonde référentiel. */
function fauxSp(): { get: jest.Mock } {
  const listing = { value: [
    { Name: 'gabarit-1.xlsx', ServerRelativeUrl: `${DOSSIER}/gabarit-1.xlsx`, TimeLastModified: '2026-07-17T10:00:00Z' }
  ] };
  return {
    get: jest.fn(async (url: string) => {
      if (url.indexOf('GetFolderByServerRelativePath') >= 0) { return rep(200, listing); }
      if (url.indexOf('GetFileByServerRelativePath') >= 0) { return rep(200, { Exists: true }); }
      return rep(200, { value: [] }); // listes du site de données (pipe/recrutement/kpi) : vides.
    })
  };
}

function colonnes(headers: ReadonlyArray<string>, rows: ReadonlyArray<ReadonlyArray<unknown>>): unknown {
  return { value: headers.map((h, ci) => ({ name: h, values: [[h], ...rows.map(r => [r[ci]])] })) };
}

/** Fabrique Graph mockée qui répond site→drives→tables ; enregistre les chemins d'API appelés. */
function fauxGraph(apiPaths: string[]): { getClient: jest.Mock } {
  const repondre = (p: string): unknown => {
    // Ordre des règles : le plus spécifique d'abord (drives avant site, sinon `$select=id` capte
    // aussi l'appel `/drives?$select=id,...`).
    if (p.indexOf('/drives?') >= 0) { return { value: [{ id: 'DRIVE1', name: 'Documents partages', webUrl: RACINE_DRIVE }] }; }
    if (p.indexOf('$select=id') >= 0 && p.indexOf('/drives/') < 0) { return { id: 'SITE1' }; }
    if (p.indexOf('T_Affectations/columns') >= 0) { return colonnes(['CodeMission', 'Ressource', 'Mois', 'JoursPrevus'], [[1, 'r@allia', 46143, 17]]); }
    if (p.indexOf('T_Imputations/columns') >= 0) { return colonnes(['CodeMission', 'Ressource', 'Mois', 'JoursRealises', 'StatutValidation'], [[1, 'r@allia', 46143, 15, 'validé']]); }
    if (p.indexOf('T_Echeancier/columns') >= 0) { return colonnes(['NumFacture', 'CodeMission', 'MoisCA', 'MontantHT', 'Echeance', 'Statut', 'LienFacture'], [['F1', 1, 46143, 15300, 46160, 'à émettre', 'https://teams/f1.pdf']]); }
    return {};
  };
  const client = { api: (p: string) => { apiPaths.push(p); return { get: async () => repondre(p) }; } };
  return { getClient: jest.fn(async () => client) };
}

function propsCablees(over: Partial<ITourDeControleProps>): ITourDeControleProps {
  return {
    description: 'x', isDarkTheme: false, environmentMessage: '', hasTeamsContext: false,
    userDisplayName: 'Adrien',
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    spHttpClient: fauxSp() as any,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    msGraphClientFactory: undefined as any,
    dataSiteUrl: `${HOTE}/sites/data`,
    gabaritsSiteUrl: SITE_CA,
    gabaritsFolderPath: DOSSIER,
    referentielRessourcesPath: '',
    referentielStructurePath: '',
    ...over
  };
}

async function monter(props: ITourDeControleProps): Promise<{ container: HTMLDivElement; demonter: () => void }> {
  const container = document.createElement('div');
  document.body.appendChild(container);
  await act(async () => { ReactDOM.render(React.createElement(TourDeControle, props), container); });
  // Plusieurs tours de boucle pour drainer la chaîne asynchrone complète de chargerCockpit
  // (REST de découverte → getClient → résolution site→drives → Promise.all des tables) puis re-render.
  for (let i = 0; i < 8; i++) {
    await act(async () => { await new Promise(resolve => setTimeout(resolve, 0)); });
  }
  return { container, demonter: () => ReactDOM.unmountComponentAtNode(container) };
}

describe('câblage Graph du cockpit — le montage émet bien la lecture (régression épreuve 17/07)', () => {
  it('props câblées + Graph mocké → getClient(3) ET la lecture des tables SONT invoqués, modèles non vides', async () => {
    const apiPaths: string[] = [];
    const graph = fauxGraph(apiPaths);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const { container, demonter } = await monter(propsCablees({ msGraphClientFactory: graph as any }));

    // 1. La fabrique de client Graph a été sollicitée (le câblage n'était PAS émis lors de l'épreuve).
    expect(graph.getClient).toHaveBeenCalledWith('3');
    // 2. La LECTURE de contenu (pas seulement la résolution site/drive) a été invoquée.
    expect(apiPaths.some(p => p.indexOf('/workbook/tables/T_Affectations/columns') >= 0)).toBe(true);
    // 3. Les modèles ne sont pas en état vide : le placeholder de première lecture a disparu.
    expect(container.textContent || '').not.toContain('Lecture des listes');
    // 4. Chemin nominal : aucune anomalie affichée.
    expect(container.textContent || '').not.toContain('en anomalie');

    demonter();
  });

  it('client Graph en échec (getClient rejette) → anomalie SURFACÉE avec sa cause + console.error (jamais muet)', async () => {
    const spyErr = jest.spyOn(console, 'error').mockImplementation(() => { /* silence en test */ });
    const graphKo = { getClient: jest.fn(async () => { throw new Error('token refusé'); }) };
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const { container, demonter } = await monter(propsCablees({ msGraphClientFactory: graphKo as any }));

    // getClient a bien été tenté (le montage émet la lecture)...
    expect(graphKo.getClient).toHaveBeenCalledWith('3');
    // ...et l'échec n'est PAS muet : la ligne d'anomalies expose la cause dans le cockpit.
    expect(container.textContent || '').toContain('en anomalie');
    expect(container.textContent || '').toContain('getClient');
    // ...et un console.error a été émis (diagnostic exploitable).
    expect(spyErr).toHaveBeenCalled();

    demonter();
    spyErr.mockRestore();
  });
});
