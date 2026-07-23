import * as React from 'react';
import styles from './TourDeControle.module.scss';
import pipe from './BandeauPipe.module.scss';
import type { SPHttpClient } from '@microsoft/sp-http';
import type { Compteur, DetailItem, CompteOption, Ecriture } from './types';
import { ETAPES_CRM, ETAPE_QUALIFICATION, ETAPE_GAGNEE, formaterEuros, apercuNomMission, type OpportuniteLigne } from './pipe-recrutement';
import { creerOpportunite, changerEtapeOpportunite, changerMontantOpportunite } from './listes-reelles';

const { useState, useCallback } = React;

export interface IBandeauPipeProps {
  /** Client REST du contexte SPFx — écriture sous l'identité de l'utilisateur (SSO, zéro secret). */
  readonly spHttpClient: SPHttpClient;
  /** URL absolue du site des listes (base `_api/web/lists`). */
  readonly dataSiteUrl: string;
  /** Compteurs du bandeau (voir → creuser) — inchangés, conservés au-dessus des gestes. */
  readonly compteurs: ReadonlyArray<Compteur>;
  /** Opportunités projetées (table éditable). */
  readonly opportunites: ReadonlyArray<OpportuniteLigne>;
  /** Comptes sélectionnables pour le rattachement du formulaire. */
  readonly comptes: ReadonlyArray<CompteOption>;
  /** Relit l'état persisté (re-run chargerCockpit) — résout APRÈS la relecture (anti-faux-vert). */
  readonly onMutation: () => Promise<void>;
}

type Retour =
  | { readonly kind: 'ok' }
  | { readonly kind: 'refuse' }
  | { readonly kind: 'indispo' };

function retourDe(e: Ecriture): Retour {
  if (e.etat === 'ok') { return { kind: 'ok' }; }
  if (e.etat === 'refuse') { return { kind: 'refuse' }; }
  return { kind: 'indispo' };
}

// Même sémantique de pastille que TourDeControle : les items pipe sont « neutral » (texte sobre).
function statutNode(item: DetailItem): React.ReactElement {
  if (item.signal === 'neutral') {
    return <span className={styles.metaText}>{item.statut}</span>;
  }
  const variante = item.signal === 'info' ? styles.pillInfo : styles.pillSignal;
  return <span className={`${styles.pill} ${variante}`}>{item.statut}</span>;
}

/**
 * Bandeau 2 — Pipe commercial (tour-de-controle.md v2.1 §3). Voir → creuser → AGIR :
 * conserve les compteurs (repliables) et ajoute, dessous, la table d'opportunités éditable
 * (étape + montant en ligne) et le formulaire « nouvelle opportunité ». Écriture guidée sous
 * l'identité de l'utilisateur (SSO SPHttpClient), aucune élévation. Le passage en « Gagnée »
 * n'écrit QUE l'étape ici : la cascade mission+espace est hors périmètre de cette PR.
 */
export default function BandeauPipe(props: IBandeauPipeProps): React.ReactElement {
  const { spHttpClient, dataSiteUrl, compteurs, opportunites, comptes, onMutation } = props;

  // Détail repliable des compteurs (creuser) — état local à ce bandeau.
  const [ouverts, setOuverts] = useState<ReadonlySet<string>>(() => new Set<string>());
  const basculer = useCallback((id: string): void => {
    setOuverts(prev => {
      const s = new Set(prev);
      if (s.has(id)) { s.delete(id); } else { s.add(id); }
      return s;
    });
  }, []);

  // Écriture en cours (par emplacement) + retour affiché (par emplacement). Jamais bloquant.
  const [occupe, setOccupe] = useState<ReadonlySet<string>>(() => new Set<string>());
  const [retours, setRetours] = useState<Readonly<Record<string, Retour>>>({});
  // Brouillons de montant par id d'opportunité (édition en ligne, non encore enregistrée).
  const [montants, setMontants] = useState<Readonly<Record<number, string>>>({});

  // Bascule « Gagnée » : geste PROPOSANT sur confirmation (§3) — l'opportunité en attente
  // de confirmation (aucune écriture tant qu'elle est posée). Année courante côté client
  // pour l'aperçu du nom (le serveur borne [2020..2100]).
  const [pendingGagnee, setPendingGagnee] = useState<OpportuniteLigne | null>(null);
  const anneeCourante = String(new Date().getFullYear());

  // Formulaire « nouvelle opportunité ».
  const [nom, setNom] = useState('');
  const [compteId, setCompteId] = useState(0);
  const [montantForm, setMontantForm] = useState('');

  const marquerOccupe = useCallback((slot: string, on: boolean): void => {
    setOccupe(prev => {
      const s = new Set(prev);
      if (on) { s.add(slot); } else { s.delete(slot); }
      return s;
    });
  }, []);

  /**
   * Applique une écriture puis, sur succès SEULEMENT, relit l'état persisté avant d'annoncer
   * « enregistré » (anti-faux-vert). 403 → « refusée (droits) », autre échec → « indisponible » :
   * notes sobres, jamais bloquantes.
   */
  const appliquer = useCallback(async (slot: string, faire: () => Promise<Ecriture>): Promise<Retour> => {
    marquerOccupe(slot, true);
    setRetours(prev => { const c = { ...prev }; delete c[slot]; return c; });
    const r = retourDe(await faire());
    if (r.kind === 'ok') { await onMutation(); }
    setRetours(prev => ({ ...prev, [slot]: r }));
    marquerOccupe(slot, false);
    return r;
  }, [marquerOccupe, onMutation]);

  const enregistrerEtape = useCallback((o: OpportuniteLigne, etape: string): void => {
    if (etape === o.etape) { return; }
    // « Gagnée » : geste PROPOSANT sur confirmation (tour-de-controle.md §3) — on ouvre une
    // confirmation, on N'ÉCRIT PAS directement. Les autres étapes restent en écriture directe.
    if (etape === ETAPE_GAGNEE) { setPendingGagnee(o); return; }
    appliquer(`row-${o.id}`, () => changerEtapeOpportunite(spHttpClient, dataSiteUrl, o.id, etape)).catch(() => undefined);
  }, [appliquer, spHttpClient, dataSiteUrl]);

  // Confirmation de la bascule « Gagnée » : écrit SEULEMENT l'étape (la source), sous SSO.
  // N'ALLOUE PAS le code mission (attribué à l'ouverture, geste gardien / T-0024) et NE CRÉE
  // PAS l'espace (dérivation agent-mission). Relecture via appliquer (anti-faux-vert).
  const confirmerGagnee = useCallback(async (o: OpportuniteLigne): Promise<void> => {
    await appliquer(`row-${o.id}`, () => changerEtapeOpportunite(spHttpClient, dataSiteUrl, o.id, ETAPE_GAGNEE));
    setPendingGagnee(null);
  }, [appliquer, spHttpClient, dataSiteUrl]);

  const enregistrerMontant = useCallback(async (o: OpportuniteLigne): Promise<void> => {
    const brut = montants[o.id];
    const n = Number(brut);
    if (brut === undefined || !Number.isFinite(n) || n === o.montant) { return; }
    const r = await appliquer(`row-${o.id}`, () => changerMontantOpportunite(spHttpClient, dataSiteUrl, o.id, n));
    if (r.kind === 'ok') {
      setMontants(prev => { const c = { ...prev }; delete c[o.id]; return c; });
    }
  }, [appliquer, montants, spHttpClient, dataSiteUrl]);

  const soumettreForm = useCallback(async (): Promise<void> => {
    const nomNet = nom.trim();
    const n = Number(montantForm);
    if (!nomNet || compteId <= 0 || montantForm.trim() === '' || !Number.isFinite(n)) { return; }
    const r = await appliquer('form', () =>
      creerOpportunite(spHttpClient, dataSiteUrl, { nom: nomNet, compteId, montant: n })
    );
    if (r.kind === 'ok') {
      setNom(''); setCompteId(0); setMontantForm('');
    }
  }, [appliquer, nom, compteId, montantForm, spHttpClient, dataSiteUrl]);

  const messageRetour = (slot: string): React.ReactElement | null => {
    const r = retours[slot];
    if (!r) { return null; }
    if (r.kind === 'ok') { return <span className={`${pipe.msg} ${pipe.msgOk}`}>Enregistré</span>; }
    if (r.kind === 'refuse') { return <span className={`${pipe.msg} ${pipe.msgRefuse}`}>Écriture refusée (droits)</span>; }
    return <span className={`${pipe.msg} ${pipe.msgIndispo}`}>Écriture indisponible</span>;
  };

  const formValide = nom.trim() !== '' && compteId > 0 && montantForm.trim() !== '' && Number.isFinite(Number(montantForm));

  return (
    <div>
      {/* Compteurs (voir → creuser) — inchangés */}
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
              {c.valeur === '—' && c.note ? <span className={styles.counterNote}>{c.note}</span> : null}
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

      {/* Table des opportunités (agir — édition en ligne étape + montant) */}
      <div className={pipe.section}>
        <p className={pipe.sectionTitre}>Opportunités</p>
        {opportunites.length === 0 ? (
          <p className={pipe.videText}>Aucune opportunité à éditer pour l’instant.</p>
        ) : (
          <div>
            {opportunites.map(o => {
              const slot = `row-${o.id}`;
              const busy = occupe.has(slot);
              const brut = montants[o.id];
              const valeurMontant = brut !== undefined ? brut : String(o.montant);
              const montantChange = brut !== undefined && Number.isFinite(Number(brut)) && Number(brut) !== o.montant;
              const enConfirmation = pendingGagnee?.id === o.id;
              const apercu = enConfirmation ? apercuNomMission(anneeCourante, o.compte ?? '', o.nom) : null;
              return (
                <React.Fragment key={o.id}>
                <div className={pipe.oppRow}>
                  <span className={pipe.oppNom}>
                    <span className={pipe.oppTitre}>{o.nom}</span>
                    <span className={pipe.oppCompte}>{o.compte ? o.compte : '·'}</span>
                  </span>
                  <select
                    className={`${pipe.champ} ${pipe.select}`}
                    aria-label={`Étape de ${o.nom}`}
                    value={ETAPES_CRM.indexOf(o.etape) >= 0 ? o.etape : ''}
                    disabled={busy}
                    onChange={e => enregistrerEtape(o, e.target.value)}
                  >
                    {ETAPES_CRM.indexOf(o.etape) < 0 ? <option value="">·</option> : null}
                    {ETAPES_CRM.map(et => <option key={et} value={et}>{et}</option>)}
                  </select>
                  <input
                    className={`${pipe.champ} ${pipe.montant}`}
                    type="number"
                    inputMode="numeric"
                    aria-label={`Montant de ${o.nom} (€ HT)`}
                    value={valeurMontant}
                    disabled={busy}
                    onChange={e => setMontants(prev => ({ ...prev, [o.id]: e.target.value }))}
                  />
                  <span className={pipe.euro}>€</span>
                  {montantChange ? (
                    <button
                      type="button"
                      className={pipe.btn}
                      disabled={busy}
                      onClick={() => { enregistrerMontant(o).catch(() => undefined); }}
                    >
                      Enregistrer
                    </button>
                  ) : null}
                  {messageRetour(slot)}
                </div>
                {enConfirmation ? (
                  <div className={pipe.confirm}>
                    {apercu && apercu.ok ? (
                      <>
                        <p className={pipe.confirmText}>
                          Passer « {o.nom} » en « {ETAPE_GAGNEE} » ouvrira la mission{' '}
                          <span className={pipe.confirmNom}>{apercu.nom}</span>.
                        </p>
                        <p className={pipe.confirmMention}>
                          Le code mission sera attribué à l’ouverture ; l’espace est créé par l’agent-mission.
                        </p>
                        <div className={pipe.confirmActions}>
                          <button
                            type="button"
                            className={pipe.btn}
                            disabled={busy}
                            onClick={() => { confirmerGagnee(o).catch(() => undefined); }}
                          >
                            Confirmer
                          </button>
                          <button
                            type="button"
                            className={pipe.btnSecondaire}
                            disabled={busy}
                            onClick={() => setPendingGagnee(null)}
                          >
                            Annuler
                          </button>
                        </div>
                      </>
                    ) : (
                      <>
                        <p className={pipe.refus}>
                          Nom de mission invalide : {apercu ? apercu.raison : '—'}. Aucune écriture.
                        </p>
                        <div className={pipe.confirmActions}>
                          <button
                            type="button"
                            className={pipe.btnSecondaire}
                            onClick={() => setPendingGagnee(null)}
                          >
                            Fermer
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                ) : null}
                </React.Fragment>
              );
            })}
          </div>
        )}
        <p className={pipe.note}>
          Le passage en « {ETAPE_GAGNEE} » propose l’ouverture de la mission et demande confirmation,
          puis enregistre l’étape. Le code mission est attribué à l’ouverture et l’espace est créé
          par l’agent-mission (non automatique depuis le cockpit).
        </p>
      </div>

      {/* Formulaire « nouvelle opportunité » (agir — création) */}
      <div className={pipe.section}>
        <p className={pipe.sectionTitre}>Nouvelle opportunité</p>
        {comptes.length === 0 ? (
          <p className={pipe.videText}>
            Aucun compte disponible — le rattachement à un compte est requis (liste Comptes non câblée ou vide).
          </p>
        ) : (
          <div className={pipe.form}>
            <div className={pipe.formGrid}>
              <label className={pipe.formField}>
                <span className={pipe.formLabel}>Nom de l’opportunité</span>
                <input
                  className={pipe.champ}
                  type="text"
                  value={nom}
                  onChange={e => setNom(e.target.value)}
                />
              </label>
              <label className={pipe.formField}>
                <span className={pipe.formLabel}>Compte</span>
                <select
                  className={pipe.champ}
                  value={compteId}
                  onChange={e => setCompteId(Number(e.target.value))}
                >
                  <option value={0}>· choisir un compte</option>
                  {comptes.map(c => <option key={c.id} value={c.id}>{c.libelle}</option>)}
                </select>
              </label>
              <label className={pipe.formField}>
                <span className={pipe.formLabel}>Montant (€ HT)</span>
                <input
                  className={pipe.champ}
                  type="number"
                  inputMode="numeric"
                  value={montantForm}
                  onChange={e => setMontantForm(e.target.value)}
                />
              </label>
              <label className={pipe.formField}>
                <span className={pipe.formLabel}>Étape</span>
                <input className={pipe.champ} type="text" value={ETAPE_QUALIFICATION} disabled readOnly />
              </label>
            </div>
            <div className={pipe.formActions}>
              <button
                type="button"
                className={pipe.btn}
                disabled={!formValide || occupe.has('form')}
                onClick={() => { soumettreForm().catch(() => undefined); }}
              >
                Créer l’opportunité
              </button>
              {montantForm.trim() !== '' && Number.isFinite(Number(montantForm)) ? (
                <span className={pipe.euro}>{formaterEuros(Number(montantForm))}</span>
              ) : null}
              {messageRetour('form')}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
