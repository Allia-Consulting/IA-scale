import * as React from 'react';
import styles from './BandeauxEconomiques.module.scss';
import type { EtatGabarits } from './gabarits';
import { construireRentabilite } from './bandeaux-economiques';

export interface IBandeauRentabiliteProps {
  readonly etat: EtatGabarits;
  readonly annee: number;
}

/**
 * Bandeau 4 — Rentabilité et résultats (tour-de-controle.md v2.1 §3). LECTURE SEULE.
 * Tableau 12 mois × (Budget | Réalisé) + colonne Total ; lignes CA total et EBITDA.
 * Point 1 : toute cellule = « · » (jamais un 0 inventé). Si le référentiel de coûts n'est
 * pas accessible à l'utilisateur, la ligne EBITDA porte la mention discrète
 * « référentiel à audience restreinte ». Les agrégats réels sont câblés au point 2.
 */
export default function BandeauRentabilite(props: IBandeauRentabiliteProps): React.ReactElement {
  const modele = construireRentabilite(props.etat, props.annee);

  return (
    <div>
      <div className={styles.tableWrap}>
        <table className={styles.rentaTable}>
          <thead>
            <tr>
              <th rowSpan={2} className={styles.rentaLabel} aria-label="Indicateur" />
              {modele.mois.map(m => (
                <th key={m} colSpan={2} className={styles.rentaMoisTh}>{m}</th>
              ))}
              <th colSpan={2} className={`${styles.rentaMoisTh} ${styles.rentaTotalCol}`}>Total</th>
            </tr>
            <tr>
              {modele.mois.map(m => (
                <React.Fragment key={m}>
                  <th className={styles.rentaSubTh}>Bud.</th>
                  <th className={styles.rentaSubTh}>Réal.</th>
                </React.Fragment>
              ))}
              <th className={`${styles.rentaSubTh} ${styles.rentaTotalCol}`}>Bud.</th>
              <th className={`${styles.rentaSubTh} ${styles.rentaTotalCol}`}>Réal.</th>
            </tr>
          </thead>
          <tbody>
            {modele.lignes.map(ligne => (
              <tr key={ligne.libelle}>
                <td className={styles.rentaLabel}>{ligne.libelle}</td>
                {ligne.cellules.map((c, i) => (
                  <React.Fragment key={`${ligne.libelle}-${i}`}>
                    <td className={styles.rentaCell}>{c.budget}</td>
                    <td className={styles.rentaCell}>{c.realise}</td>
                  </React.Fragment>
                ))}
                <td className={`${styles.rentaCell} ${styles.rentaTotalCol}`}>{ligne.total.budget}</td>
                <td className={`${styles.rentaCell} ${styles.rentaTotalCol}`}>{ligne.total.realise}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {modele.lignes
        .filter(l => l.mention)
        .map(l => (
          <p key={l.libelle} className={styles.rentaMention}>{l.libelle} — {l.mention}</p>
        ))}
    </div>
  );
}
