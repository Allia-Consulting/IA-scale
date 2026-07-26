// Fournisseur de données réelles — Tour de contrôle (T-0014-b).
//
// Lit les listes M365 du site courant via spHttpClient (aucun Graph, aucun secret,
// SSO du contexte SPFx). Renvoie EXACTEMENT les types de `types.ts`, consommés tels
// quels par le rendu. Trois règles inviolables :
//   1. Liste absente (404) → note « non câblé » sobre, jamais une erreur bloquante.
//   2. Échec de lecture → note « lecture indisponible » sobre. JAMAIS de repli
//      silencieux sur des constantes de démonstration.
//   3. Liste vide → vide assumé (0 / —), aucune invention.
// Recrutement : COMPTEURS AGRÉGÉS PAR ÉTAPE UNIQUEMENT — la page est tenant-wide,
// aucun champ nominatif candidat n'est lu ni affiché (RGPD, rgpd-recrutement-candidats.md,
// option A). La lecture ne sélectionne que la colonne `Etape` (cf. QUERY_RECRUTEMENT).

import { SPHttpClient, SPHttpClientResponse, MSGraphClientFactory, MSGraphClientV3 } from '@microsoft/sp-http';
import type { Zone, ZonePipe, ZoneRecrutement, CompteOption, Compteur, DetailItem, Ecriture } from './types';
import {
  decouvrirGabarits,
  fusionnerContenus,
  type EtatGabarits,
  type AnomalieGabarit,
  type LecteurDossier,
  type SondeReferentiel,
  type ResultatDossier,
  type EtatAcces,
  type FichierDossier
} from './gabarits';
import {
  lireContenus,
  versTexte,
  type GrapheGet,
  type CibleGabarit,
  type CiblesReferentiel
} from './workbook-graph';
import {
  choisirSaisie,
  type DepsCascade
} from './cascade-acceptee';
import {
  COLONNE_STATUT_MISSION,
  compterMissionsActives,
  compterCreesDepuis,
  apparierBriefKickoff,
  moyenneDeltas,
  formaterDuree
} from './kpi-organisation';
import {
  Ecrivain,
  optionsEcriture,
  creerOpportunite as creerOpportunitePure,
  changerEtapeOpportunite as changerEtapeOpportunitePure,
  changerMontantOpportunite as changerMontantOpportunitePure,
  COL_STATUT_COMPTE,
  COL_ETAPE_CRM,
  COL_MONTANT_CRM,
  COL_NOM_OPPORTUNITE,
  COL_COMPTE,
  COL_NOM_COMPTE,
  QUERY_RECRUTEMENT,
  QUERY_GESTES_RECRUTEMENT,
  ETAPE_CANDIDAT_E1,
  ETAPE_CANDIDAT_E2,
  ETAPE_CANDIDAT_E3,
  ETAPE_CANDIDAT_PROPOSITION,
  compterComptesClients,
  opportunitesEnProposition,
  montantPropose,
  montantOpportunite,
  nomOpportunite,
  pipePondere,
  projeterOpportunites,
  projeterCandidats,
  compterCandidatsEtape,
  formaterEuros,
  creerCandidat as creerCandidatPure,
  changerEtapeCandidat as changerEtapeCandidatPure
} from './pipe-recrutement';

export interface CockpitData {
  /** T-0020-d — les 3 KPI d'organisation (mesure de valeur, dernier maillon Phase 2). */
  readonly indicateurs: Zone;
  readonly pipeCommercial: ZonePipe;
  readonly recrutement: ZoneRecrutement;
  /** Cockpit v2 — présence/absence des sources économiques (gabarits actifs + référentiel). */
  readonly gabarits: EtatGabarits;
}

/**
 * Coordonnées du classeur de SAISIE (modele-donnees.md §5.6) — site « Management et Gestion »,
 * racine de la bibliothèque « Documents ». Sert au RAPPEL d'affectation de la cascade « Acceptée »
 * (contrat v2.2) : un listing READ-ONLY du dossier NOMME le classeur `saisie-<code>-….xlsx` dans le
 * rappel. Aucune écriture n'y a lieu (l'affectation est un geste humain, saisie matricielle). Posées
 * par le gardien (property pane) ; vides = rappel générique (motif `saisie-<code>-….xlsx`), fail-OPEN.
 */
export interface ConfigSaisie {
  /** URL absolue du site de la saisie (base `_api`). */
  readonly siteUrl: string;
  /** Chemin server-relative du dossier des classeurs `saisie-<code>-….xlsx`. */
  readonly folderPath: string;
}

/**
 * Coordonnées de découverte des gabarits (cockpit v2) — posées par le gardien (runbook,
 * point 2), jamais au canon. Champs vides = découverte « non câblée » → états vides
 * honnêtes (aucun chemin inventé). Les gabarits vivent sur un AUTRE site que les listes
 * (Contrats et administratif, `06 - Gabarit ERP`), d'où une base `_api` distincte.
 */
export interface ConfigGabarits {
  /** URL absolue du site des gabarits (base `_api`, ex. .../sites/Contratsetadministratif). */
  readonly siteUrl: string;
  /** Chemin server-relative du dossier des gabarits actifs (`06 - Gabarit ERP`). */
  readonly dossierGabarits: string;
  /** Chemin server-relative du classeur référentiel `T_Ressources` (audience restreinte, §5.3). */
  readonly referentielRessources: string;
  /** Chemin server-relative du classeur référentiel `T_Structure` (audience restreinte, §5.3). */
  readonly referentielStructure: string;
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

/**
 * Écriture guidée d'un item de liste (création ou mise à jour), symétrique de
 * `lireListe`. POST via SPHttpClient sous l'identité de l'utilisateur connecté —
 * aucune élévation de droits, le digest est injecté automatiquement.
 *   - CRÉATION : POST sur .../items ;
 *   - MISE À JOUR : POST sur .../items(<id>) tunnellisé MERGE (cf. optionsEcriture).
 * Les en-têtes (Accept odata.metadata=none, X-HTTP-Method/IF-MATCH) sont construits par
 * `optionsEcriture` (pipe-recrutement.ts — source unique de vérité, unit-testée).
 * Ne lève JAMAIS : 403 → `refuse` (fail-visible), tout autre échec → `indisponible`.
 * Source Microsoft Learn (14/07/2026) : connect-to-sharepoint + working-with-lists-and-
 * list-items-with-rest (SharePoint REST OData 4.0).
 */
async function ecrireListe(
  sp: SPHttpClient,
  dataSiteUrl: string,
  titre: string,
  champs: Record<string, unknown>,
  id?: number
): Promise<Ecriture> {
  const base = `${dataSiteUrl}/_api/web/lists/getByTitle('${encodeURIComponent(titre)}')/items`;
  const url = id === undefined ? base : `${base}(${id})`;
  const { headers, body } = optionsEcriture(id === undefined ? 'create' : 'update', champs);
  try {
    const res: SPHttpClientResponse = await sp.post(url, SPHttpClient.configurations.v1, { headers, body });
    if (res.status === 403) {
      return { etat: 'refuse' };
    }
    if (!res.ok) {
      return { etat: 'indisponible' };
    }
    return { etat: 'ok' };
  } catch {
    return { etat: 'indisponible' };
  }
}

/** Lie le primitif d'écriture pur (Ecrivain) au contexte `sp` + `dataSiteUrl`. */
function ecrivainPour(sp: SPHttpClient, dataSiteUrl: string): Ecrivain {
  return (titre, champs, id) => ecrireListe(sp, dataSiteUrl, titre, champs, id);
}

/**
 * Gestes d'écriture guidée du bandeau pipe — BRANCHÉS par BandeauPipe.tsx (table éditable
 * + formulaire « nouvelle opportunité »). La logique pure (payloads + délégation) est dans
 * pipe-recrutement.ts et unit-testée ; ces enveloppes ne font que fournir l'Ecrivain lié
 * au contexte SPFx (SSO utilisateur, aucune élévation, digest injecté automatiquement).
 */
export function creerOpportunite(
  sp: SPHttpClient,
  dataSiteUrl: string,
  params: {
    readonly nom: string;
    readonly compteId: number;
    readonly montant: number;
    readonly etape?: string;
    readonly echeance?: string;
  }
): Promise<Ecriture> {
  return creerOpportunitePure(ecrivainPour(sp, dataSiteUrl), params);
}

export function changerEtapeOpportunite(
  sp: SPHttpClient,
  dataSiteUrl: string,
  id: number,
  etape: string
): Promise<Ecriture> {
  return changerEtapeOpportunitePure(ecrivainPour(sp, dataSiteUrl), id, etape);
}

export function changerMontantOpportunite(
  sp: SPHttpClient,
  dataSiteUrl: string,
  id: number,
  montant: number
): Promise<Ecriture> {
  return changerMontantOpportunitePure(ecrivainPour(sp, dataSiteUrl), id, montant);
}

/**
 * Gestes d'écriture guidée du bandeau RECRUTEMENT — même motif que les gestes pipe : la logique
 * pure (payloads, garde « Acceptée », allocation C-NNN) vit dans pipe-recrutement.ts et est
 * unit-testée ; ces enveloppes ne font que lier l'Ecrivain au contexte SPFx (SSO utilisateur,
 * aucune élévation). La bascule « Acceptée » N'EST PAS ici (garde de `changerEtapeCandidatPure`) :
 * elle passe par la cascade (`depsCascadePour` + `executerCascade`, cascade-acceptee.ts).
 */
export function creerCandidat(
  sp: SPHttpClient,
  dataSiteUrl: string,
  params: {
    readonly title: string;
    readonly nom: string;
    readonly grade: string;
    readonly source: string;
    readonly email: string;
    readonly telephone?: string;
  }
): Promise<Ecriture> {
  return creerCandidatPure(ecrivainPour(sp, dataSiteUrl), params);
}

export function changerEtapeCandidat(
  sp: SPHttpClient,
  dataSiteUrl: string,
  id: number,
  etape: string
): Promise<Ecriture> {
  return changerEtapeCandidatPure(ecrivainPour(sp, dataSiteUrl), id, etape);
}

/** Compteur « — » sobre pour une source non lisible (non câblé / indisponible). */
function compteurAbsent(id: string, libelle: string, etat: 'non_cable' | 'indisponible'): Compteur {
  return { id, libelle, valeur: '—', items: [], note: etat === 'non_cable' ? NOTE_NON_CABLE : NOTE_INDISPONIBLE };
}

/**
 * Bandeau « Pipe commercial » (tour-de-controle.md v2.0 §3 bandeau 2).
 * Source RÉELLE : Liste « CRM » (Étape, Montant) + Liste « Comptes » (Statut).
 * La bibliothèque « Propositions » n'est PAS utilisée (vide). Quatre compteurs :
 * Comptes actifs · Propositions en cours · Montant proposé · Pipe pondéré (60/15 figé).
 * Chaque source échoue indépendamment (fail-visible ; jamais de constante de démo).
 */
async function chargerPipeCommercial(sp: SPHttpClient, dataSiteUrl: string): Promise<ZonePipe> {
  const [comptes, crm] = await Promise.all([
    // Comptes : Id + Title + NomCompte alimentent le sélecteur du formulaire (le lookup s'écrit
    // par l'Id numérique) ; Statut reste lu pour le compteur « Comptes actifs ».
    lireListe(sp, dataSiteUrl, 'Comptes', `$select=${COL_STATUT_COMPTE},Id,Title,NomCompte&$top=1000`),
    // CRM : Id (clé des mises à jour) + rattachement Compte via $expand pour la table éditable.
    lireListe(sp, dataSiteUrl, 'CRM', `$select=Id,${COL_NOM_OPPORTUNITE},${COL_ETAPE_CRM},${COL_MONTANT_CRM},${COL_COMPTE}/Title,${COL_COMPTE}/${COL_NOM_COMPTE}&$expand=${COL_COMPTE}&$top=2000`)
  ]);

  // Comptes actifs (Statut = Client).
  const cComptes: Compteur = comptes.etat !== 'ok'
    ? compteurAbsent('pipe-comptes', 'Comptes actifs', comptes.etat)
    : (() => {
        const n = compterComptesClients(comptes.valeurs);
        return {
          id: 'pipe-comptes',
          libelle: 'Comptes actifs',
          valeur: String(n),
          items: [],
          note: n === 0 ? 'Aucun compte client pour l’instant.' : undefined
        };
      })();

  // Les trois compteurs CRM partagent une seule lecture.
  let cProp: Compteur, cMontant: Compteur, cPondere: Compteur;
  if (crm.etat !== 'ok') {
    cProp = compteurAbsent('pipe-prop', 'Propositions en cours', crm.etat);
    cMontant = compteurAbsent('pipe-montant', 'Montant proposé', crm.etat);
    cPondere = compteurAbsent('pipe-pondere', 'Pipe pondéré', crm.etat);
  } else {
    const props = opportunitesEnProposition(crm.valeurs);
    // Détail creusable : opportunités en Proposition — données commerciales, pas personnelles.
    const items: ReadonlyArray<DetailItem> = props.map(o => ({
      libelle: nomOpportunite(o),
      statut: formaterEuros(montantOpportunite(o)),
      signal: 'neutral' as const
    }));
    cProp = {
      id: 'pipe-prop',
      libelle: 'Propositions en cours',
      valeur: String(props.length),
      items,
      note: props.length === 0 ? 'Aucune proposition en cours.' : undefined
    };
    cMontant = {
      id: 'pipe-montant',
      libelle: 'Montant proposé',
      valeur: formaterEuros(montantPropose(crm.valeurs)),
      items: []
    };
    cPondere = {
      id: 'pipe-pondere',
      libelle: 'Pipe pondéré',
      valeur: formaterEuros(pipePondere(crm.valeurs)),
      items: []
    };
  }

  // Lignes d'opportunités projetées (table éditable) + comptes sélectionnables (formulaire).
  // Source vide/illisible → tableaux vides (voir → creuser → agir dégrade en « rien à éditer »).
  const opportunites = crm.etat === 'ok' ? projeterOpportunites(crm.valeurs) : [];
  const comptesOptions: ReadonlyArray<CompteOption> = comptes.etat === 'ok'
    ? comptes.valeurs
        .map(c => ({
          id: Number((c.Id ?? c.ID) ?? 0) || 0,
          libelle: (typeof c.NomCompte === 'string' && c.NomCompte)
            ? c.NomCompte
            : (typeof c.Title === 'string' && c.Title) ? c.Title : '(compte)'
        }))
        .filter(o => o.id > 0)
    : [];

  return { compteurs: [cComptes, cProp, cMontant, cPondere], opportunites, comptes: comptesOptions };
}

/**
 * Bandeau « Recrutement » (tour-de-controle.md §3 bandeau 3).
 *
 * DEUX lectures INDÉPENDANTES de la Liste « Candidats », chacune faillant seule (fail-visible) :
 *   1. COMPTEURS agrégés — `QUERY_RECRUTEMENT` (Etape UNIQUEMENT). RÈGLE INVIOLABLE conservée :
 *      aucun champ nominatif n'est sélectionné pour l'agrégat (RGPD option A, page tenant-wide).
 *   2. GESTES (T-0039) — `QUERY_GESTES_RECRUTEMENT` (Id, Title, NomCandidat, Grade, Etape). Lecture
 *      NOMINATIVE nécessaire aux gestes « étape en ligne » et « cascade Acceptée ». Elle est gouvernée
 *      par l'ACL de la liste sous l'identité de l'utilisateur (destinataires internes du recrutement,
 *      rgpd-recrutement-candidats.md §3) : un 403 (non habilité) → `gestesAccessibles=false`, aucune
 *      ligne exposée, seuls les compteurs subsistent. Le cockpit n'élève aucun droit (§1 régime 1, §6).
 *      (Départ ASSUMÉ de l'ancienne posture « jamais de nominatif sur la page tenant-wide », désormais
 *      que le contrat socle §3 bandeau 3 exige des gestes par candidat — à relire, gardien.)
 * `missionsConnues` est rempli par `chargerCockpit` depuis les gabarits (ici : vide).
 */
async function chargerRecrutement(sp: SPHttpClient, dataSiteUrl: string): Promise<ZoneRecrutement> {
  const [agg, gestes] = await Promise.all([
    lireListe(sp, dataSiteUrl, 'Candidats', QUERY_RECRUTEMENT),
    lireListe(sp, dataSiteUrl, 'Candidats', QUERY_GESTES_RECRUTEMENT)
  ]);

  const etapes: ReadonlyArray<{ readonly id: string; readonly libelle: string; readonly etape: string }> = [
    { id: 'rec-e1', libelle: 'Entretien E1', etape: ETAPE_CANDIDAT_E1 },
    { id: 'rec-e2', libelle: 'Entretien E2', etape: ETAPE_CANDIDAT_E2 },
    { id: 'rec-e3', libelle: 'Entretien E3', etape: ETAPE_CANDIDAT_E3 },
    { id: 'rec-dec', libelle: 'Décisions en cours', etape: ETAPE_CANDIDAT_PROPOSITION }
  ];

  const compteurs: ReadonlyArray<Compteur> = agg.etat !== 'ok'
    ? etapes.map(e => compteurAbsent(e.id, e.libelle, agg.etat as 'non_cable' | 'indisponible'))
    // Agrégat pur — un NOMBRE par étape, aucun item nominatif (jamais de liste de candidats).
    : etapes.map(e => {
        const n = compterCandidatsEtape(agg.valeurs, e.etape);
        return { id: e.id, libelle: e.libelle, valeur: String(n), items: [], note: n === 0 ? 'Aucun pour l’instant.' : undefined };
      });

  // Gestes : disponibles seulement si la lecture nominative a abouti (ACL de liste, §3).
  const gestesAccessibles = gestes.etat === 'ok';
  const candidats = gestesAccessibles ? projeterCandidats(gestes.valeurs) : [];
  const titresPris = gestesAccessibles
    ? gestes.valeurs.map(v => (typeof v.Title === 'string' ? v.Title : '')).filter(t => t !== '')
    : [];

  return { compteurs, candidats, titresPris, gestesAccessibles, missionsConnues: [] };
}

// ---------------------------------------------------------------------------
// Découverte des gabarits (cockpit v2) — primitives réseau liées à `sp`, sous
// l'identité de l'utilisateur (SSO, zéro secret, aucune élévation). Les gabarits
// vivent sur un AUTRE site (Contrats et administratif) : lecture REST cross-site par
// URL absolue. Symétriques de `lireListe`/`ecrivainPour` : ne lèvent JAMAIS.
//   - config vide → 'non_cable' (état légitime : le gardien câble au point 2) ;
//   - 404 → 'non_cable' ; référentiel 403/404 → 'restreint' ; autre échec → 'indisponible'.
// ---------------------------------------------------------------------------
/**
 * Échappe une apostrophe pour un littéral chaîne OData (doublement). On cible la forme
 * moderne `...ByServerRelativePath(decodedUrl='…')` : elle prend le chemin DÉCODÉ (slashes
 * et espaces intacts, ex. « 06 - Gabarit ERP »), sans encoder les slashes — le transport
 * est encodé par SPHttpClient. Robuste pour les chemins avec espaces (leçon vs encodeURIComponent).
 */
function litteralOData(v: string): string {
  return v.replace(/'/g, "''");
}

function lecteurGabaritsPour(sp: SPHttpClient, cfg: ConfigGabarits): LecteurDossier {
  return async (): Promise<ResultatDossier> => {
    if (!cfg.siteUrl || !cfg.dossierGabarits) { return { etat: 'non_cable' }; }
    const url = `${cfg.siteUrl}/_api/web/GetFolderByServerRelativePath(decodedUrl='${litteralOData(cfg.dossierGabarits)}')`
      + `/Files?$select=Name,ServerRelativeUrl,TimeLastModified&$top=2000`;
    try {
      const res: SPHttpClientResponse = await sp.get(url, SPHttpClient.configurations.v1);
      if (res.status === 404) { return { etat: 'non_cable' }; }
      if (!res.ok) { return { etat: 'indisponible' }; }
      const body: { value?: ReadonlyArray<Record<string, unknown>> } = await res.json();
      const fichiers: ReadonlyArray<FichierDossier> = (body.value ?? []).map(f => ({
        nom: typeof f.Name === 'string' ? f.Name : '',
        url: typeof f.ServerRelativeUrl === 'string' ? f.ServerRelativeUrl : '',
        modifieLe: typeof f.TimeLastModified === 'string' ? f.TimeLastModified : undefined
      }));
      return { etat: 'ok', fichiers };
    } catch {
      return { etat: 'indisponible' };
    }
  };
}

function sondeReferentielPour(sp: SPHttpClient, cfg: ConfigGabarits): SondeReferentiel {
  return async (): Promise<EtatAcces> => {
    // Non configuré : l'utilisateur courant n'a pas (encore) de vue sur le référentiel →
    // 'restreint' (flag false, non bloquant), état légitime pour la plupart des collaborateurs.
    // NB : sonde de DÉCOUVERTE (présence du classeur ressources) ; l'état d'accès AUTORITAIRE
    // vient ensuite de la lecture Graph des tables (workbook-graph.ts, fusionnerContenus).
    if (!cfg.siteUrl || !cfg.referentielRessources) { return 'restreint'; }
    const url = `${cfg.siteUrl}/_api/web/GetFileByServerRelativePath(decodedUrl='${litteralOData(cfg.referentielRessources)}')?$select=Exists`;
    try {
      const res: SPHttpClientResponse = await sp.get(url, SPHttpClient.configurations.v1);
      if (res.ok) { return 'accessible'; }
      if (res.status === 403 || res.status === 404) { return 'restreint'; }
      return 'indisponible';
    } catch {
      return 'indisponible';
    }
  };
}

/**
 * Adaptateur GET Graph lié à MSGraphClientV3 (Graph DÉLÉGUÉ — SSO SPFx, permission Sites.Read.All
 * approuvée par le gardien). Ne lève JAMAIS : une GraphError porte `statusCode` (403/404…) que l'on
 * remonte pour distinguer restreint/indisponible côté workbook-graph.
 */
function grapheGetPour(client: MSGraphClientV3): GrapheGet {
  return async (cheminApi: string) => {
    try {
      const corps: unknown = await client.api(cheminApi).get();
      return { ok: true, status: 200, corps };
    } catch (e) {
      const brut = (e && typeof e === 'object' && 'statusCode' in e) ? Number((e as { statusCode?: unknown }).statusCode) : 0;
      const status = isFinite(brut) ? brut : 0;
      // Jamais d'échec muet (point 3) : chaque GET Graph en échec est journalisé avec son statut et
      // son chemin. Un status 0 = échec AVANT réponse HTTP (jeton refusé, réseau, client non résolu).
      console.error('[tour-de-controle] échec GET Graph', { chemin: cheminApi, status, erreur: e instanceof Error ? e.message : String(e) });
      return { ok: false, status };
    }
  };
}

// ---------------------------------------------------------------------------
// Cascade « Acceptée » (T-0039, contrat v2.2) — primitives liées au contexte SPFx. La cascade
// n'écrit QUE des LISTES (SharePoint REST, identité utilisateur) : Candidats.Etape puis fiche
// Ressources-Profil. L'affectation initiale N'EST PLUS écrite (arbitrage gardien 26/07 : saisie
// matricielle, T_Affectations n'existe que dans les gabarits) — elle fait l'objet d'un RAPPEL, pour
// lequel on NOMME le classeur de saisie via un listing READ-ONLY (aucun Graph, aucune écriture).
// Toutes ne lèvent JAMAIS.
// ---------------------------------------------------------------------------

/**
 * Résout, en LECTURE seule, le NOM du classeur de saisie de la mission (`saisie-<code>-….xlsx`) pour
 * le RAPPEL d'affectation. Simple listing REST du dossier de saisie sous l'identité de l'utilisateur ;
 * jamais d'écriture, jamais de Graph. Fail-OPEN : renvoie `undefined` dès que le nom n'est pas
 * résoluble sûrement (config vide, dossier illisible, aucun match, ou plusieurs candidats ambigus) —
 * l'appelant retombe alors sur le motif générique. Ne lève jamais.
 */
export function resoudreNomSaisiePour(
  sp: SPHttpClient,
  cfgSaisie: ConfigSaisie
): (codeMission: string) => Promise<string | undefined> {
  return async (codeMission) => {
    if (!cfgSaisie.siteUrl || !cfgSaisie.folderPath) { return undefined; }
    const url = `${cfgSaisie.siteUrl}/_api/web/GetFolderByServerRelativePath(decodedUrl='${litteralOData(cfgSaisie.folderPath)}')`
      + `/Files?$select=Name&$top=2000`;
    try {
      const res: SPHttpClientResponse = await sp.get(url, SPHttpClient.configurations.v1);
      if (!res.ok) { return undefined; }
      const body: { value?: ReadonlyArray<Record<string, unknown>> } = await res.json();
      const noms = (body.value ?? []).map(f => versTexte(f.Name));
      const choix = choisirSaisie(noms, codeMission);
      // Ambigu → on ne nomme pas au hasard : fail-OPEN vers le motif générique (rappel, pas écriture).
      return choix.ambigu ? undefined : choix.nom;
    } catch {
      return undefined;
    }
  };
}

/**
 * Construit les primitives d'écriture de la cascade « Acceptée » liées au contexte SPFx : écriture de
 * listes en SharePoint REST (SSO utilisateur, aucune élévation). Consommé par BandeauRecrutement +
 * `executerCascade` (cascade-acceptee.ts). Le RAPPEL d'affectation ne passe pas par ici : il est
 * NOMMÉ en lecture seule (`resoudreNomSaisiePour`) et formaté par `rappelAffectation`.
 */
export function depsCascadePour(
  sp: SPHttpClient,
  dataSiteUrl: string
): DepsCascade {
  return {
    ecrire: ecrivainPour(sp, dataSiteUrl)
  };
}

/**
 * Surface un SAUT ou un ÉCHEC de la lecture du CONTENU (Graph Workbook) comme anomalie VISIBLE
 * (portant sa cause) + `console.error` — JAMAIS muet. Retourne la découverte enrichie de l'anomalie.
 *
 * Cause racine de l'épreuve ÉCHOUÉE du 17/07 (T-0035 reprise) : le code retournait la découverte
 * seule en SILENCE (guard « non câblé », `catch` autour de `getClient` avalant l'erreur) et le
 * bandeau de fraîcheur n'affichait pas la cause → aucun appel Graph, aucune anomalie explicite,
 * console vide : échec indiagnosticable. On ne saute/n'échoue plus jamais sans le dire.
 */
function diagnostiquer(etat: EtatGabarits, source: string, raison: string, cause: string): EtatGabarits {
  console.error('[tour-de-controle] lecture du contenu des gabarits ignorée', { raison, cause });
  const anomalie: AnomalieGabarit = { source, raison, cause };
  return { ...etat, anomalies: [...etat.anomalies, anomalie] };
}

/**
 * Découvre les gabarits actifs (REST, listing/fraîcheur) PUIS lit le contenu de leurs tables +
 * du référentiel de coûts via Graph Workbook délégué (point 2). Ne lève jamais. TOUT saut ou échec
 * de la lecture de contenu est SURFACÉ (anomalie + `console.error`) — jamais muet (point 3).
 */
async function chargerGabarits(
  sp: SPHttpClient,
  cfg: ConfigGabarits,
  graphFactory?: MSGraphClientFactory
): Promise<EtatGabarits> {
  const etat = await decouvrirGabarits(lecteurGabaritsPour(sp, cfg), sondeReferentielPour(sp, cfg), new Date());

  // Découverte non 'ok' : 'non_cable' = état LÉGITIME (rien n'est câblé → aucun bruit) ; 'indisponible'
  // = échec RÉEL du listing → déjà porté en anomalie par decouvrirGabarits, on le journalise aussi.
  if (etat.source !== 'ok') {
    if (etat.source === 'indisponible') {
      console.error('[tour-de-controle] découverte des gabarits indisponible', { siteUrl: cfg.siteUrl });
    }
    return etat;
  }
  // Dossier découvert mais site non câblé (incohérence : source 'ok' implique normalement siteUrl) :
  // défensif, surfacé plutôt que tu.
  if (!cfg.siteUrl) {
    return diagnostiquer(etat, 'contenu des gabarits', 'site des gabarits non câblé', 'gabaritsSiteUrl vide');
  }
  // Fabrique Graph absente : le contenu ne sera pas lu → on le DIT (au lieu de retourner en silence).
  if (!graphFactory) {
    return diagnostiquer(etat, 'contenu des gabarits', 'fabrique de client Graph indisponible', 'msGraphClientFactory absente');
  }

  let grapheGet: GrapheGet;
  try {
    grapheGet = grapheGetPour(await graphFactory.getClient('3'));
  } catch (e) {
    // getClient('3') a échoué (jeton, permission, résolution) : SURFACÉ, plus jamais avalé.
    const msg = e instanceof Error ? e.message : String(e);
    return diagnostiquer(etat, 'contenu des gabarits', "client Graph non résolu (getClient('3') a échoué)", `getClient('3') : ${msg}`);
  }

  const cibles: ReadonlyArray<CibleGabarit> = etat.gabarits.map(g => ({ codeMission: g.codeMission, url: g.url }));
  const referentiel: CiblesReferentiel | undefined = (cfg.referentielRessources && cfg.referentielStructure)
    ? { ressources: cfg.referentielRessources, structure: cfg.referentielStructure }
    : undefined;
  const contenus = await lireContenus(grapheGet, cfg.siteUrl, cibles, referentiel);
  // Un `console.error` par échec de contenu (point 3) — la fraîcheur affiche déjà source + cause.
  for (const a of contenus.anomalies) {
    console.error('[tour-de-controle] anomalie gabarit', a.source, '—', a.cause ?? a.raison);
  }
  return fusionnerContenus(etat, contenus);
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

/** Charge l'ensemble du cockpit. Chaque source échoue indépendamment (fail-visible). */
export async function chargerCockpit(
  sp: SPHttpClient,
  dataSiteUrl: string,
  cfgGabarits: ConfigGabarits,
  graphFactory?: MSGraphClientFactory
): Promise<CockpitData> {
  const [indicateurs, pipeCommercial, recrutementBase, gabarits] = await Promise.all([
    chargerIndicateursOrganisation(sp, dataSiteUrl),
    chargerPipeCommercial(sp, dataSiteUrl),
    chargerRecrutement(sp, dataSiteUrl),
    chargerGabarits(sp, cfgGabarits, graphFactory)
  ]);
  // Missions réelles connues = CodeMission des gabarits actifs (options du dialogue de cascade).
  const missionsConnues = gabarits.gabarits.map(g => g.codeMission).filter(c => c !== '');
  const recrutement: ZoneRecrutement = { ...recrutementBase, missionsConnues };
  return { indicateurs, pipeCommercial, recrutement, gabarits };
}
