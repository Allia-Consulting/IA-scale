import * as React from 'react';
import styles from './TourDeControle.module.scss';
import type { ITourDeControleProps } from './ITourDeControleProps';
import type { Compteur, DetailItem, Zone } from './types';
import { compterDecisions } from './types';
import { chargerCockpit, CockpitData } from './listes-reelles';

const { useState, useCallback, useEffect } = React;

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
  const { userDisplayName, spHttpClient, dataSiteUrl } = props;

  // Un seul état, l'ensemble des panneaux ouverts (clé = id de compteur).
  // Modèle voir → creuser → agir : un compteur déplie/replie SON détail dans le cockpit.
  const [ouverts, setOuverts] = useState<ReadonlySet<string>>(() => new Set<string>());

  // Données réelles des listes M365. `null` tant que la première lecture n'a pas répondu.
  const [data, setData] = useState<CockpitData | null>(null);

  useEffect(() => {
    let vivant = true;
    chargerCockpit(spHttpClient, dataSiteUrl)
      .then(d => { if (vivant) { setData(d); } })
      .catch(() => { /* fail-visible : data reste null → zones en « lecture indisponible » */ });
    return () => { vivant = false; };
  }, [spHttpClient, dataSiteUrl]);

  const basculer = useCallback((id: string): void => {
    setOuverts(prev => {
      const suivant = new Set(prev);
      if (suivant.has(id)) { suivant.delete(id); } else { suivant.add(id); }
      return suivant;
    });
  }, []);

  // Compteur d'en-tête : DÉRIVÉ des données réelles, jamais codé en dur. 0 est honnête.
  const zones: ReadonlyArray<Zone> = data ? [data.pipeCommercial, data.recrutement, data.activite] : [];
  const nbDecisions = compterDecisions(zones);

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

      {/* 1 — Pipe commercial */}
      <div className={styles.zone}>
        <div className={styles.zoneHead}>
          <span className={styles.zoneNum}>1</span>
          <div>
            <p className={styles.zoneTitle}>Pipe commercial</p>
            <p className={styles.zoneSub}>Le premier coup d&rsquo;œil</p>
          </div>
        </div>
        {data ? renderCompteurs(data.pipeCommercial.compteurs) : chargement}
        {actionInerte('Relancer une opportunité')}
      </div>

      {/* 2 — Recrutement (agrégats par étape uniquement — page tenant-wide, RGPD) */}
      <div className={styles.zone}>
        <div className={styles.zoneHead}>
          <span className={styles.zoneNum}>2</span>
          <div>
            <p className={styles.zoneTitle}>Recrutement</p>
            <p className={styles.zoneSub}>Synthèses d&rsquo;entretien par étape</p>
          </div>
        </div>
        {data ? renderCompteurs(data.recrutement.compteurs) : chargement}
        {actionInerte('Valider les synthèses en attente')}
      </div>

      {/* 3 & 4 — états réels */}
      <div className={styles.twoCol}>
        <div className={styles.zone}>
          <div className={styles.zoneHead}>
            <span className={styles.zoneNum}>3</span>
            <p className={styles.zoneTitleSm}>Rentabilité &amp; résultats</p>
          </div>
          <button
            type="button"
            className={`${styles.counter} ${styles.counterWide}`}
            aria-expanded={ouverts.has('rent')}
            aria-controls="panneau-rent"
            onClick={() => basculer('rent')}
          >
            <span className={styles.counterLabel}>Missions à surveiller</span>
            <span className={styles.counterVal}>—</span>
          </button>
          {ouverts.has('rent') && (
            <div id="panneau-rent" className={styles.detail}>
              <p className={styles.emptyText}>
                Aucune mission active facturée. La marge et le TACE s&rsquo;afficheront dès que les temps et imputations seront saisis.
              </p>
            </div>
          )}
          {actionInerte('Comprendre le calcul')}
        </div>

        {/* 4 — Activité des équipes : Zone-de-proposition + Imputations (réel) */}
        <div className={styles.zone}>
          <div className={styles.zoneHead}>
            <span className={styles.zoneNum}>4</span>
            <p className={styles.zoneTitleSm}>Activité des équipes</p>
          </div>
          {data ? renderCompteurs(data.activite.compteurs) : chargement}
          {actionInerte('Relancer la saisie')}
        </div>
      </div>

      {/* Demande à ton SI — la face « action » */}
      <div className={styles.footer}>
        <p className={styles.footerTitle}>Demande à ton SI</p>
        <p className={styles.footerNote}>L&rsquo;agent exécute en Zone-de-proposition ; tu valides l&rsquo;irréversible.</p>
        <div className={styles.askRow}>
          {actionInerte('Affecter')}
          {actionInerte('Synthèse')}
          {actionInerte('Vue d\'ensemble')}
        </div>
      </div>
    </section>
  );
}
