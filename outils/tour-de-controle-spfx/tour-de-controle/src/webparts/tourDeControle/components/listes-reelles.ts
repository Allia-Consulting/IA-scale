// Fournisseur de données réelles — Tour de contrôle (T-0014-b).
//
// Lit les listes M365 du site courant via spHttpClient (aucun Graph, aucun secret,
// SSO du contexte SPFx). Renvoie EXACTEMENT les types de `types.ts`, consommés tels
// quels par le rendu. Trois règles inviolables :
//   1. Liste absente (404) → note « non câblé » sobre, jamais une erreur bloquante.
//   2. Échec de lecture → note « lecture indisponible » sobre. JAMAIS de repli
//      silencieux sur des constantes de démonstration.
//   3. Liste vide → vide assumé (0 / —), aucune invention.
// Recrutement : COMPTEURS AGRÉGÉS PAR STATUT UNIQUEMENT — la page est tenant-wide,
// aucun champ nominatif candidat n'est lu ni affiché (RGPD, rgpd-recrutement-candidats.md).

import { SPHttpClient, SPHttpClientResponse } from '@microsoft/sp-http';
import type { Zone, Compteur, DetailItem } from './types';

export interface CockpitData {
  readonly pipeCommercial: Zone;
  readonly recrutement: Zone;
  readonly activite: Zone;
}

const NOTE_NON_CABLE = 'Liste non câblée sur ce site.';
const NOTE_INDISPONIBLE = 'Lecture indisponible pour le moment.';

type Lecture =
  | { readonly etat: 'ok'; readonly valeurs: ReadonlyArray<Record<string, unknown>> }
  | { readonly etat: 'non_cable' }
  | { readonly etat: 'indisponible' };

/** Une lecture OData bornée sur une liste par son titre. Ne lève jamais. */
async function lireListe(
  sp: SPHttpClient,
  webUrl: string,
  titre: string,
  query: string
): Promise<Lecture> {
  const url = `${webUrl}/_api/web/lists/getByTitle('${encodeURIComponent(titre)}')/items?${query}`;
  try {
    const res: SPHttpClientResponse = await sp.get(url, SPHttpClient.configurations.v1);
    if (res.status === 404) {
      return { etat: 'non_cable' };
    }
    if (!res.ok) {
      return { etat: 'indisponible' };
    }
    const body: { value?: ReadonlyArray<Record<string, unknown>> } = await res.json();
    return { etat: 'ok', valeurs: body.value ?? [] };
  } catch {
    return { etat: 'indisponible' };
  }
}

/** Compteur « nombre d'éléments » d'une liste, fail-visible, vide assumé. */
function compteurCompte(
  id: string,
  libelle: string,
  lecture: Lecture,
  libelleUnite: string
): Compteur {
  if (lecture.etat === 'non_cable') {
    return { id, libelle, valeur: '—', items: [], note: NOTE_NON_CABLE };
  }
  if (lecture.etat === 'indisponible') {
    return { id, libelle, valeur: '—', items: [], note: NOTE_INDISPONIBLE };
  }
  const n = lecture.valeurs.length;
  return {
    id,
    libelle,
    valeur: String(n),
    items: [],
    note: n === 0 ? `Aucun ${libelleUnite} pour l'instant.` : undefined
  };
}

/** Zone 1 — Pipe commercial : Comptes + Propositions (réellement vides aujourd'hui). */
async function chargerPipeCommercial(sp: SPHttpClient, webUrl: string): Promise<Zone> {
  const [comptes, propositions] = await Promise.all([
    lireListe(sp, webUrl, 'Comptes', '$select=Id&$top=1000'),
    lireListe(sp, webUrl, 'Propositions', '$select=Id&$top=1000')
  ]);
  return {
    compteurs: [
      compteurCompte('pipe-comptes', 'Comptes', comptes, 'compte client'),
      compteurCompte('pipe-prop', 'Propositions', propositions, 'proposition')
    ]
  };
}

/**
 * Zone 2 — Recrutement : Candidats-Synthèses AGRÉGÉES PAR STATUT (EtapeSynthese).
 * On ne lit QUE la colonne de statut — aucun Title, nom, ni interviewer (RGPD).
 */
async function chargerRecrutement(sp: SPHttpClient, webUrl: string): Promise<Zone> {
  const lecture = await lireListe(
    sp,
    webUrl,
    'Candidats-Synthèses',
    '$select=EtapeSynthese&$top=2000'
  );
  if (lecture.etat === 'non_cable') {
    return { compteurs: [{ id: 'rec-synth', libelle: 'Synthèses d’entretien', valeur: '—', items: [], note: NOTE_NON_CABLE }] };
  }
  if (lecture.etat === 'indisponible') {
    return { compteurs: [{ id: 'rec-synth', libelle: 'Synthèses d’entretien', valeur: '—', items: [], note: NOTE_INDISPONIBLE }] };
  }
  // Agrégation par statut — les libellés d'étape ne sont pas des données personnelles.
  const parEtape = new Map<string, number>();
  for (const item of lecture.valeurs) {
    const etape = typeof item.EtapeSynthese === 'string' && item.EtapeSynthese ? item.EtapeSynthese : '(sans étape)';
    parEtape.set(etape, (parEtape.get(etape) ?? 0) + 1);
  }
  const total = lecture.valeurs.length;
  const items: ReadonlyArray<DetailItem> = Array.from(parEtape.entries())
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([etape, n]) => ({ libelle: etape, statut: String(n), signal: 'neutral' as const }));
  return {
    compteurs: [
      {
        id: 'rec-synth',
        libelle: 'Synthèses d’entretien',
        valeur: String(total),
        items,
        note: total === 0 ? 'Aucune synthèse pour l’instant.' : undefined
      }
    ]
  };
}

/** Zone 4 — Activité : Zone-de-proposition (dérivés récents) + Imputations. */
async function chargerActivite(sp: SPHttpClient, webUrl: string): Promise<Zone> {
  const [zone, imputations] = await Promise.all([
    lireListe(
      sp,
      webUrl,
      'Zone-de-proposition',
      '$select=Title,Origine,Created&$orderby=Created desc&$top=5'
    ),
    lireListe(sp, webUrl, 'Imputations', '$select=Id&$top=2000')
  ]);

  let compteurZone: Compteur;
  if (zone.etat === 'ok') {
    const items: ReadonlyArray<DetailItem> = zone.valeurs.map(v => ({
      libelle: typeof v.Title === 'string' && v.Title ? v.Title : '(sans titre)',
      statut: typeof v.Origine === 'string' && v.Origine ? v.Origine : '—',
      signal: 'neutral' as const
    }));
    compteurZone = {
      id: 'act-zone',
      libelle: 'Dérivés récents (Zone-de-proposition)',
      valeur: String(zone.valeurs.length),
      items,
      note: zone.valeurs.length === 0 ? 'Aucun dérivé récent.' : undefined
    };
  } else {
    compteurZone = {
      id: 'act-zone',
      libelle: 'Dérivés récents (Zone-de-proposition)',
      valeur: '—',
      items: [],
      note: zone.etat === 'non_cable' ? NOTE_NON_CABLE : NOTE_INDISPONIBLE
    };
  }

  return {
    compteurs: [
      compteurZone,
      compteurCompte('act-imput', 'Imputations', imputations, 'imputation')
    ]
  };
}

/** Charge l'ensemble du cockpit. Chaque zone échoue indépendamment (fail-visible). */
export async function chargerCockpit(sp: SPHttpClient, webUrl: string): Promise<CockpitData> {
  const [pipeCommercial, recrutement, activite] = await Promise.all([
    chargerPipeCommercial(sp, webUrl),
    chargerRecrutement(sp, webUrl),
    chargerActivite(sp, webUrl)
  ]);
  return { pipeCommercial, recrutement, activite };
}
