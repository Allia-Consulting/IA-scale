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
import {
  COLONNE_STATUT_MISSION,
  compterMissionsActives,
  compterCreesDepuis,
  apparierBriefKickoff,
  moyenneDeltas,
  formaterDuree
} from './kpi-organisation';

export interface CockpitData {
  /** T-0020-d — les 3 KPI d'organisation (mesure de valeur, dernier maillon Phase 2). */
  readonly indicateurs: Zone;
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
  dataSiteUrl: string,
  titre: string,
  query: string
): Promise<Lecture> {
  const url = `${dataSiteUrl}/_api/web/lists/getByTitle('${encodeURIComponent(titre)}')/items?${query}`;
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
async function chargerPipeCommercial(sp: SPHttpClient, dataSiteUrl: string): Promise<Zone> {
  const [comptes, propositions] = await Promise.all([
    lireListe(sp, dataSiteUrl, 'Comptes', '$select=Id&$top=1000'),
    lireListe(sp, dataSiteUrl, 'Propositions', '$select=Id&$top=1000')
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
async function chargerRecrutement(sp: SPHttpClient, dataSiteUrl: string): Promise<Zone> {
  const lecture = await lireListe(
    sp,
    dataSiteUrl,
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
async function chargerActivite(sp: SPHttpClient, dataSiteUrl: string): Promise<Zone> {
  const [zone, imputations] = await Promise.all([
    lireListe(
      sp,
      dataSiteUrl,
      'Zone-de-proposition',
      '$select=Title,Origine,Created&$orderby=Created desc&$top=5'
    ),
    lireListe(sp, dataSiteUrl, 'Imputations', '$select=Id&$top=2000')
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

/**
 * Section « Indicateurs d'organisation » (T-0020-d) — les 3 KPI figés, lecture seule.
 * Réutilise `lireListe` (canal unique T-0014, spHttpClient, SSO) ; jamais de $filter
 * serveur (leçon T-0013-d) — on lit puis on filtre côté client. Chaque KPI dégrade en
 * « — » sobre si sa source est absente/illisible, jamais d'erreur ni de chiffre inventé.
 */
async function chargerIndicateursOrganisation(sp: SPHttpClient, dataSiteUrl: string): Promise<Zone> {
  const [missions, imputations, crm, zone] = await Promise.all([
    lireListe(sp, dataSiteUrl, 'Missions', `$select=${COLONNE_STATUT_MISSION},Created&$top=2000`),
    lireListe(sp, dataSiteUrl, 'Imputations', '$select=Created&$top=2000'),
    lireListe(sp, dataSiteUrl, 'CRM', '$select=Created&$top=2000'),
    lireListe(sp, dataSiteUrl, 'Zone-de-proposition', '$select=Title,Created&$top=2000')
  ]);

  // KPI 1 — Missions actives.
  let kpiMissions: Compteur;
  if (missions.etat === 'ok') {
    const n = compterMissionsActives(missions.valeurs);
    kpiMissions = {
      id: 'kpi-missions-actives',
      libelle: 'Missions actives',
      valeur: String(n),
      items: [],
      note: n === 0 ? 'Aucune mission active pour l’instant.' : undefined
    };
  } else {
    kpiMissions = {
      id: 'kpi-missions-actives',
      libelle: 'Missions actives',
      valeur: '—',
      items: [],
      note: missions.etat === 'non_cable' ? NOTE_NON_CABLE : NOTE_INDISPONIBLE
    };
  }

  // KPI 2 — Dérivés promus (7 jours glissants) : Missions + Imputations + CRM.
  // Proxy exact : une création en liste SOURCE ne peut venir que d'une promotion humaine
  // (l'agent n'écrit qu'en Zone-de-proposition — verrou serveur MCP). Voir kpi-organisation.ts.
  const maintenant = new Date();
  const sources: ReadonlyArray<{ readonly libelle: string; readonly lecture: Lecture }> = [
    { libelle: 'Missions', lecture: missions },
    { libelle: 'Imputations', lecture: imputations },
    { libelle: 'CRM', lecture: crm }
  ];
  const detailsPromus: DetailItem[] = [];
  let sommePromus = 0;
  let auMoinsUneSourceLue = false;
  for (const s of sources) {
    if (s.lecture.etat === 'ok') {
      auMoinsUneSourceLue = true;
      const n = compterCreesDepuis(s.lecture.valeurs, maintenant, 7);
      sommePromus += n;
      detailsPromus.push({ libelle: s.libelle, statut: String(n), signal: 'neutral' });
    } else {
      detailsPromus.push({ libelle: s.libelle, statut: '—', signal: 'neutral' });
    }
  }
  const kpiPromus: Compteur = {
    id: 'kpi-derives-promus-7j',
    libelle: 'Dérivés promus (7 j)',
    valeur: auMoinsUneSourceLue ? String(sommePromus) : '—',
    items: detailsPromus,
    note: auMoinsUneSourceLue
      ? 'Créations en listes sources sur 7 jours glissants — proxy des promotions humaines (l’agent n’écrit qu’en Zone-de-proposition).'
      : NOTE_INDISPONIBLE
  };

  // KPI 3 — Délai brief→kick-off : appariement BRIEF-<n> / KICKOFF-<n>-* dans la Zone.
  let kpiDelai: Compteur;
  if (zone.etat === 'ok') {
    const paires = apparierBriefKickoff(zone.valeurs);
    if (paires.length === 0) {
      kpiDelai = {
        id: 'kpi-delai-brief-kickoff',
        libelle: 'Délai brief→kick-off',
        valeur: '—',
        items: [],
        note: 'Aucune paire brief→kick-off à ce jour.'
      };
    } else {
      const dernier = paires[paires.length - 1];
      const items: DetailItem[] = [
        { libelle: `Dernier (mission n°${dernier.n})`, statut: formaterDuree(dernier.deltaSecondes), signal: 'neutral' }
      ];
      if (paires.length > 1) {
        items.push({
          libelle: `Moyenne (${paires.length} paires)`,
          statut: formaterDuree(moyenneDeltas(paires)),
          signal: 'neutral'
        });
      }
      kpiDelai = {
        id: 'kpi-delai-brief-kickoff',
        libelle: 'Délai brief→kick-off',
        valeur: formaterDuree(dernier.deltaSecondes),
        items
      };
    }
  } else {
    kpiDelai = {
      id: 'kpi-delai-brief-kickoff',
      libelle: 'Délai brief→kick-off',
      valeur: '—',
      items: [],
      note: zone.etat === 'non_cable' ? NOTE_NON_CABLE : NOTE_INDISPONIBLE
    };
  }

  return { compteurs: [kpiMissions, kpiPromus, kpiDelai] };
}

/** Charge l'ensemble du cockpit. Chaque zone échoue indépendamment (fail-visible). */
export async function chargerCockpit(sp: SPHttpClient, dataSiteUrl: string): Promise<CockpitData> {
  const [indicateurs, pipeCommercial, recrutement, activite] = await Promise.all([
    chargerIndicateursOrganisation(sp, dataSiteUrl),
    chargerPipeCommercial(sp, dataSiteUrl),
    chargerRecrutement(sp, dataSiteUrl),
    chargerActivite(sp, dataSiteUrl)
  ]);
  return { indicateurs, pipeCommercial, recrutement, activite };
}
