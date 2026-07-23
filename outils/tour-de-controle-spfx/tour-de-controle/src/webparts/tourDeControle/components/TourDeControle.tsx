import * as React from 'react';
import styles from './TourDeControle.module.scss';
import type { ITourDeControleProps } from './ITourDeControleProps';
import type { Compteur, DetailItem, Zone } from './types';
import { compterDecisions } from './types';
import { chargerCockpit, CockpitData } from './listes-reelles';
import BandeauStaffing from './BandeauStaffing';
import BandeauRentabilite from './BandeauRentabilite';
import BandeauFactures from './BandeauFactures';
import BandeauFraicheur from './BandeauFraicheur';
import BandeauPipe from './BandeauPipe';

const { useState, useCallback, useEffect, useMemo } = React;

// La couleur de la pastille est portée par le « signal » : bleu = info/structurel ;
// ambre = signal rare (à surveiller / ta décision) ; neutre = texte sobre, sans pastille.
// Aucun vert : le design system n'a pas de token « succès ».
function statutNode(item: DetailItem): React.ReactElement {
  if (item.signal === 'neutral') {
    return <span className={styles.metaText}>{item.statut}</span>;
  }
  const variante = item.signal === 'info' ? styles.pillInfo : styles.pillSignal;
  return <span className={`${styles.pill} ${variante}`}>{item.statut}</span>;
}

export default function TourDeControle(props: ITourDeControleProps): React.ReactElement {
  const { userDisplayName, spHttpClient, dataSiteUrl, msGraphClientFactory } = props;
  const { gabaritsSiteUrl, gabaritsFolderPath, referentielRessourcesPath, referentielStructurePath } = props;

  // Un seul état, l'ensemble des panneaux ouverts (clé = id de compteur).
  // Modèle voir → creuser → agir : un compteur déplie/replie SON détail dans le cockpit.
  const [ouverts, setOuverts] = useState<ReadonlySet<string>>(() => new Set<string>());

  // Données réelles des listes M365 + découverte des gabarits. `null` tant que la
  // première lecture n'a pas répondu.
  const [data, setData] = useState<CockpitData | null>(null);

  // Config de découverte des gabarits — posée par le gardien (property pane, point 2) ;
  // vide = non câblée → états vides honnêtes.
  const cfgGabarits = useMemo(
    () => ({
      siteUrl: gabaritsSiteUrl,
      dossierGabarits: gabaritsFolderPath,
      referentielRessources: referentielRessourcesPath,
      referentielStructure: referentielStructurePath
    }),
    [gabaritsSiteUrl, gabaritsFolderPath, referentielRessourcesPath, referentielStructurePath]
  );

  useEffect(() => {
    let vivant = true;
    chargerCockpit(spHttpClient, dataSiteUrl, cfgGabarits, msGraphClientFactory)
      .then(d => { if (vivant) { setData(d); } })
      .catch(() => { /* fail-visible : data reste null → zones en « lecture indisponible » */ });
    return () => { vivant = false; };
  }, [spHttpClient, dataSiteUrl, cfgGabarits, msGraphClientFactory]);

  // Relecture après une écriture guidée (onMutation de BandeauPipe) : relance chargerCockpit
  // et ne résout qu'une fois l'état persisté relu — c'est ce qui permet à BandeauPipe de
  // n'annoncer « enregistré » qu'APRÈS relecture (anti-faux-vert). Fail-visible : sur échec,
  // l'état reste inchangé (les bandeaux gardent la dernière lecture, jamais d'invention).
  const recharger = useCallback(async (): Promise<void> => {
    try {
      const d = await chargerCockpit(spHttpClient, dataSiteUrl, cfgGabarits, msGraphClientFactory);
      setData(d);
    } catch { /* fail-visible : data inchangé */ }
  }, [spHttpClient, dataSiteUrl, cfgGabarits, msGraphClientFactory]);

  const basculer = useCallback((id: string): void => {
    setOuverts(prev => {
      const suivant = new Set(prev);
      if (suivant.has(id)) { suivant.delete(id); } else { suivant.add(id); }
      return suivant;
    });
  }, []);

  // Compteur d'en-tête : DÉRIVÉ des données réelles, jamais codé en dur. 0 est honnête.
  const zones: ReadonlyArray<Zone> = data ? [data.pipeCommercial, data.recrutement] : [];
  const nbDecisions = compterDecisions(zones);

  // Année courante pour la rentabilité (le staffing porte son propre sélecteur).
  const anneeCourante = useMemo(() => new Date().getFullYear(), []);

  const renderCompteurs = (compteurs: ReadonlyArray<Compteur>): React.ReactElement => (
    <>
      <div className={styles.counters}>
        {compteurs.map(c => {
          const ouvert = ouverts.has(c.id);
          return (
            <button
              key={c.id}
              type="button"
              className={styles.counter}
              aria-expanded={ouvert}
              aria-controls={`panneau-${c.id}`}
              onClick={() => basculer(c.id)}
            >
              <span className={styles.counterLabel}>{c.libelle}</span>
              <span className={styles.counterVal}>{c.valeur}</span>
              {/* Non câblée / indisponible (valeur « — ») : libellé VISIBLE sous
                  la valeur, jamais confondu avec un vrai zéro. */}
              {c.valeur === '—' && c.note ? (
                <span className={styles.counterNote}>{c.note}</span>
              ) : null}
            </button>
          );
        })}
      </div>
      {compteurs.map(c =>
        ouverts.has(c.id) ? (
          <div key={c.id} id={`panneau-${c.id}`} className={styles.detail}>
            {c.note ? <p className={styles.emptyText}>{c.note}</p> : null}
            {c.items.map(item => (
              <div key={item.libelle} className={styles.detailRow}>
                <span>{item.libelle}</span>
                {statutNode(item)}
              </div>
            ))}
          </div>
        ) : null
      )}
    </>
  );

  // Placeholder sobre pendant la première lecture — jamais de chiffre inventé.
  const chargement = (
    <p className={styles.emptyText}>Lecture des listes…</p>
  );

  // L'action est un geste SÉPARÉ et délibéré — inerte en v1 (jamais câblée à l'agent).
  const actionInerte = (libelle: string): React.ReactElement => (
    <button
      type="button"
      className={styles.action}
      disabled
      title="À venir — action non câblée en v1 (le câblage portera le cran de l'action sous-jacente)."
    >
      <span>{libelle}</span>
      <span className={styles.actionTag}>à venir</span>
    </button>
  );

  return (
    <section className={styles.cockpit}>
      <div className={styles.header}>
        <div>
          <p className={styles.hello}>Bonjour {userDisplayName}</p>
          <p className={styles.helloSub}>
            {nbDecisions > 1
              ? `${nbDecisions} choses appellent ta décision aujourd'hui`
              : `${nbDecisions} chose appelle ta décision aujourd'hui`}
          </p>
        </div>
        <span className={styles.alertBadge} aria-label={`${nbDecisions} éléments à décider`}>
          {nbDecisions} à décider
        </span>
      </div>

      {/* Hiérarchie figée des cinq bandeaux (tour-de-controle.md v2.1 §3, priorité
          décroissante) : 1 staffing · 2 pipe commercial · 3 recrutement · 4 rentabilité ·
          5 factures à émettre. */}

      {/* 1 — Staffing (lecture seule ; source gabarits actifs, §4) */}
      <div className={styles.zone}>
        <div className={styles.zoneHead}>
          <span className={styles.zoneNum}>1</span>
          <div>
            <p className={styles.zoneTitle}>Staffing</p>
            <p className={styles.zoneSub}>Taux mensuel des salariés (hors sous-traitance), lecture seule</p>
          </div>
        </div>
        {data ? <BandeauStaffing etat={data.gabarits} /> : chargement}
      </div>

      {/* 2 — Pipe commercial */}
      <div className={styles.zone}>
        <div className={styles.zoneHead}>
          <span className={styles.zoneNum}>2</span>
          <div>
            <p className={styles.zoneTitle}>Pipe commercial</p>
            <p className={styles.zoneSub}>Comptes actifs, propositions, pipe pondéré</p>
          </div>
        </div>
        {data ? (
          <BandeauPipe
            spHttpClient={spHttpClient}
            dataSiteUrl={dataSiteUrl}
            compteurs={data.pipeCommercial.compteurs}
            opportunites={data.pipeCommercial.opportunites}
            comptes={data.pipeCommercial.comptes}
            onMutation={recharger}
          />
        ) : chargement}
      </div>

      {/* 3 — Recrutement (agrégats par étape uniquement — page tenant-wide, RGPD) */}
      <div className={styles.zone}>
        <div className={styles.zoneHead}>
          <span className={styles.zoneNum}>3</span>
          <div>
            <p className={styles.zoneTitle}>Recrutement</p>
            <p className={styles.zoneSub}>Entretiens en cours par étape (agrégat)</p>
          </div>
        </div>
        {data ? renderCompteurs(data.recrutement.compteurs) : chargement}
        {actionInerte('Ajouter un candidat')}
      </div>

      {/* 4 — Rentabilité et résultats (lecture seule ; gabarits actifs + référentiel, §4) */}
      <div className={styles.zone}>
        <div className={styles.zoneHead}>
          <span className={styles.zoneNum}>4</span>
          <div>
            <p className={styles.zoneTitle}>Rentabilité &amp; résultats</p>
            <p className={styles.zoneSub}>Budget vs réalisé — CA total, EBITDA (lecture seule)</p>
          </div>
        </div>
        {data ? <BandeauRentabilite etat={data.gabarits} annee={anneeCourante} /> : chargement}
      </div>

      {/* 5 — Factures à émettre (lecture seule ; échéanciers des gabarits actifs, §4) */}
      <div className={styles.zone}>
        <div className={styles.zoneHead}>
          <span className={styles.zoneNum}>5</span>
          <div>
            <p className={styles.zoneTitle}>Factures à émettre</p>
            <p className={styles.zoneSub}>Échéances « à émettre » des missions (lecture seule)</p>
          </div>
        </div>
        {data ? <BandeauFactures etat={data.gabarits} /> : chargement}
      </div>

      {/* Fraîcheur commune (§3 — honnêteté des données) : « lu le J à H » + anomalies */}
      {data ? <BandeauFraicheur etat={data.gabarits} /> : null}

      {/* Indicateurs d'organisation (T-0020-d) — les 3 KPI v1, conservés en bande compacte
          SOUS les cinq bandeaux (décision gardien-copilote : le contrat fige l'ordre des
          bandeaux, il n'abroge pas les KPI). Lecture seule, aucun vert, aucune pastille. */}
      <div className={styles.zone}>
        <div className={styles.zoneHead}>
          <div>
            <p className={styles.zoneTitle}>Indicateurs d&rsquo;organisation</p>
            <p className={styles.zoneSub}>La valeur, en trois mesures</p>
          </div>
        </div>
        {data ? renderCompteurs(data.indicateurs.compteurs) : chargement}
      </div>
    </section>
  );
}
