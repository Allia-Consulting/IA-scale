import * as React from 'react';
import styles from './BandeauxEconomiques.module.scss';
import type { EtatGabarits } from './gabarits';
import { formaterFraicheur } from './gabarits';

export interface IBandeauFraicheurProps {
  readonly etat: EtatGabarits;
}

/**
 * Bandeau de fraîcheur commun (tour-de-controle.md v2.1 §3 — honnêteté des données).
 * « lu le J à H » + « N gabarit(s) en anomalie : M-XXX, … » le cas échéant. Jamais de
 * chiffre inventé ; les anomalies sont signalées (signal ambre discret, aucune pastille).
 */
export default function BandeauFraicheur(props: IBandeauFraicheurProps): React.ReactElement {
  const f = formaterFraicheur(props.etat);
  return (
    <div className={styles.fraicheur}>
      <span className={styles.fraicheurLu}>lu le {f.luLe}</span>
      {f.anomalies ? <span className={styles.fraicheurAnomalies}>{f.anomalies}</span> : null}
    </div>
  );
}
