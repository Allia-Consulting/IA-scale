import * as React from 'react';
import styles from './BandeauxEconomiques.module.scss';
import type { EtatGabarits } from './gabarits';
import { construireFactures } from './bandeaux-economiques';

export interface IBandeauFacturesProps {
  readonly etat: EtatGabarits;
}

/**
 * Bandeau 5 — Factures à émettre (tour-de-controle.md v2.1 §3). LECTURE SEULE : PAS de
 * bouton « Émise » (le statut s'écrit dans le classeur de saisie, hors cockpit) ni de
 * création de facture. Chaque ligne prévoit le lien vers le PDF dans le dépôt Teams
 * (T_Echeancier.LienFacture). Point 1 : les échéanciers ne sont pas encore ouverts —
 * la liste est vide et le message le dit honnêtement (câblage T_Echeancier = point 2).
 */
export default function BandeauFactures(props: IBandeauFacturesProps): React.ReactElement {
  const modele = construireFactures(props.etat);

  if (modele.lignes.length === 0) {
    return <p className={styles.videText}>{modele.messageVide}</p>;
  }

  return (
    <div>
      {modele.lignes.map(f => (
        <div className={styles.factureRow} key={f.numFacture}>
          <span className={styles.factureNum}>{f.numFacture}</span>
          <span className={styles.factureMeta}>mission {f.codeMission}</span>
          <span className={styles.factureMeta}>échéance {f.echeance}</span>
          <span className={styles.factureMontant}>{f.montant}</span>
          {f.lienPdf ? (
            <a className={styles.factureLien} href={f.lienPdf} target="_blank" rel="noreferrer">PDF</a>
          ) : (
            <span className={styles.factureLien}>PDF —</span>
          )}
        </div>
      ))}
    </div>
  );
}
