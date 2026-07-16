import * as React from 'react';
import styles from './BandeauxEconomiques.module.scss';
import type { EtatGabarits } from './gabarits';
import { construireStaffing } from './bandeaux-economiques';

const { useState, useMemo } = React;

export interface IBandeauStaffingProps {
  readonly etat: EtatGabarits;
}

/**
 * Bandeau 1 — Staffing (tour-de-controle.md v2.1 §3). LECTURE SEULE : aucun geste d'édition
 * (les affectations s'éditent dans le classeur de saisie, hors cockpit). Point 1 : sans
 * gabarit actif, chaque barre affiche « · » — jamais un 0 % inventé. Le taux réel et
 * l'effectif (Ressources-Profil, salariés hors sous-traitance) sont câblés au point 2.
 */
export default function BandeauStaffing(props: IBandeauStaffingProps): React.ReactElement {
  // Année courante / mois courant : lus une fois au montage (horloge du navigateur).
  const now = useMemo(() => new Date(), []);
  const anneeCourante = now.getFullYear();
  const moisCourant0 = now.getMonth();

  const [annee, setAnnee] = useState<number>(anneeCourante);
  const modele = construireStaffing(props.etat, annee, anneeCourante, moisCourant0);

  return (
    <div>
      <div className={styles.staffingHead}>
        <div className={styles.anneePicker} role="group" aria-label="Sélecteur d'année">
          {modele.anneesDisponibles.map(a => (
            <button
              key={a}
              type="button"
              className={`${styles.anneeBtn} ${a === annee ? styles.anneeBtnActif : ''}`}
              aria-pressed={a === annee}
              onClick={() => setAnnee(a)}
            >
              {a}
            </button>
          ))}
        </div>
        <div className={styles.legende}>
          <span className={styles.legendeItem}>
            <span className={`${styles.legendeSwatch} ${styles.legendeRealise}`} aria-hidden="true" />
            réalisé
          </span>
          <span className={styles.legendeItem}>
            <span className={`${styles.legendeSwatch} ${styles.legendePrevisionnel}`} aria-hidden="true" />
            prévisionnel
          </span>
        </div>
      </div>

      <div className={styles.barres}>
        {modele.barres.map(b => (
          <div className={styles.barreCol} key={b.moisIndex}>
            <span className={styles.barreEffectif}>{b.effectif}</span>
            <div
              className={`${styles.barreTrack} ${b.regime === 'previsionnel' ? styles.trackPrevisionnel : ''}`}
              title={`${b.libelleMois} — ${b.regime === 'realise' ? 'réalisé' : 'prévisionnel'}`}
            >
              <div className={styles.barreFill} style={{ height: `${b.hauteurPct}%` }} aria-hidden="true" />
              <span className={styles.barrePct}>{b.pct}</span>
            </div>
            <span className={styles.barreMois}>{b.libelleMois}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
