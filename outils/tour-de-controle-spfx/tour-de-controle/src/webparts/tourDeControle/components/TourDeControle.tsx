import * as React from 'react';
import styles from './TourDeControle.module.scss';
import type { ITourDeControleProps } from './ITourDeControleProps';
import type { Compteur, DetailItem, SuiviCandidat, AvancementJalon } from './demo-data';
import { pipeCommercial, recrutement, compterDecisions, suiviCandidats, avancement } from './demo-data';

const { useState, useCallback } = React;

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

// Trajectoire d'un candidat le long du pipeline : jalons rendus SOBREMENT —
// distinction franchi / courant / à venir par le STYLE seul (graisse, opacité,
// soulignement du courant). Jamais de pastille, jamais de vert : une étape
// franchie n'est pas une décision en attente, et l'ambre reste « ta décision ».
function classeJalon(etat: AvancementJalon): string {
  if (etat === 'franchi') { return `${styles.jalon} ${styles.jalonFranchi}`; }
  if (etat === 'courant') { return `${styles.jalon} ${styles.jalonCourant}`; }
  return `${styles.jalon} ${styles.jalonAVenir}`;
}

function trajectoireNode(candidat: SuiviCandidat): React.ReactElement {
  const jalons = avancement(candidat.etapeCourante);
  return (
    <span className={styles.trajectoire}>
      {jalons.map((j, i) => (
        <React.Fragment key={j.etape}>
          {i > 0 ? <span className={styles.jalonSep} aria-hidden="true">›</span> : null}
          <span className={classeJalon(j.etat)}>{j.etape}</span>
        </React.Fragment>
      ))}
    </span>
  );
}

export default function TourDeControle(props: ITourDeControleProps): React.ReactElement {
  const { userDisplayName } = props;

  // Un seul état, l'ensemble des panneaux ouverts (clé = id de compteur).
  // Modèle voir → creuser → agir : un compteur déplie/replie SON détail dans le cockpit.
  const [ouverts, setOuverts] = useState<ReadonlySet<string>>(() => new Set<string>());

  const basculer = useCallback((id: string): void => {
    setOuverts(prev => {
      const suivant = new Set(prev);
      if (suivant.has(id)) { suivant.delete(id); } else { suivant.add(id); }
      return suivant;
    });
  }, []);

  // Compteur d'en-tête : DÉRIVÉ des données démo, jamais codé en dur.
  const nbDecisions = compterDecisions([pipeCommercial, recrutement]);

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
            </button>
          );
        })}
      </div>
      {compteurs.map(c =>
        ouverts.has(c.id) ? (
          <div key={c.id} id={`panneau-${c.id}`} className={styles.detail}>
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
      <p className={styles.banner}>
        Pipe &amp; recrutement : données de démonstration. Rentabilité &amp; activité reflètent l&rsquo;état réel (encore vide).
      </p>

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
            <p className={styles.zoneSub}>
              Le premier coup d&rsquo;œil — <span className={styles.demoTag}>données de démonstration</span>
            </p>
          </div>
        </div>
        {renderCompteurs(pipeCommercial.compteurs)}
        {actionInerte('Relancer une opportunité')}
      </div>

      {/* 2 — Recrutement */}
      <div className={styles.zone}>
        <div className={styles.zoneHead}>
          <span className={styles.zoneNum}>2</span>
          <div>
            <p className={styles.zoneTitle}>Recrutement</p>
            <p className={styles.zoneSub}>
              Pipeline candidats par étape — <span className={styles.demoTag}>données de démonstration</span>
            </p>
          </div>
        </div>
        {renderCompteurs(recrutement.compteurs)}

        {/* Suivi par étape (T-0013-b) — compteur autonome, même mécanique
            dépli/repli. Valeur DÉRIVÉE du nombre de candidats suivis ; le détail
            montre la trajectoire de chacun + le dernier interviewer. Lecture seule. */}
        <button
          type="button"
          className={`${styles.counter} ${styles.counterWide}`}
          aria-expanded={ouverts.has('rec-suivi')}
          aria-controls="panneau-rec-suivi"
          onClick={() => basculer('rec-suivi')}
        >
          <span className={styles.counterLabel}>Suivi par étape</span>
          <span className={styles.counterVal}>{suiviCandidats.candidats.length}</span>
        </button>
        {ouverts.has('rec-suivi') && (
          <div id="panneau-rec-suivi" className={styles.detail}>
            {suiviCandidats.candidats.map(c => (
              <div key={c.id} className={`${styles.detailRow} ${styles.suiviRow}`}>
                <span className={styles.suiviIdent}>{c.id} — {c.grade}</span>
                {trajectoireNode(c)}
                <span className={styles.metaText}>tenue par {c.responsableAction}</span>
              </div>
            ))}
          </div>
        )}
        {actionInerte('Valider les synthèses en attente')}
      </div>

      {/* 3 & 4 — états réels (vides honnêtes : aucun chiffre simulé) */}
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

        <div className={styles.zone}>
          <div className={styles.zoneHead}>
            <span className={styles.zoneNum}>4</span>
            <p className={styles.zoneTitleSm}>Activité des équipes</p>
          </div>
          <button
            type="button"
            className={`${styles.counter} ${styles.counterWide}`}
            aria-expanded={ouverts.has('act')}
            aria-controls="panneau-act"
            onClick={() => basculer('act')}
          >
            <span className={styles.counterLabel}>Temps non saisis</span>
            <span className={styles.counterVal}>—</span>
          </button>
          {ouverts.has('act') && (
            <div id="panneau-act" className={styles.detail}>
              <p className={styles.emptyText}>
                Pas encore de collaborateurs équipés. La charge par personne s&rsquo;affichera après l&rsquo;onboarding des premiers collaborateurs.
              </p>
            </div>
          )}
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
