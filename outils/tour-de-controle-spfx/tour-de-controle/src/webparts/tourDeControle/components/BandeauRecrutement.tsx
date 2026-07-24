import * as React from 'react';
import styles from './TourDeControle.module.scss';
import pipe from './BandeauPipe.module.scss';
import type { SPHttpClient, MSGraphClientFactory } from '@microsoft/sp-http';
import type { Compteur, DetailItem, Ecriture } from './types';
import {
  ETAPES_CANDIDAT,
  ETAPE_CANDIDAT_ACCEPTEE,
  GRADES_CANDIDAT,
  SOURCES_CANDIDAT,
  prochainTitleCandidat,
  type CandidatLigne
} from './pipe-recrutement';
import { creerCandidat, changerEtapeCandidat, depsCascadePour } from './listes-reelles';
import { construireAnnonce, executerCascade, type EtatCascade, type SaisieCascade } from './cascade-acceptee';

const { useState, useCallback, useMemo } = React;

export interface IBandeauRecrutementProps {
  readonly spHttpClient: SPHttpClient;
  readonly dataSiteUrl: string;
  /** Fabrique Graph (délégué) — écriture de l'affectation de la cascade (Files.ReadWrite.All). */
  readonly msGraphClientFactory?: MSGraphClientFactory;
  /** Coordonnées de la couche de saisie (§5.6) — cible de la ligne d'affectation. */
  readonly saisieSiteUrl: string;
  readonly saisieFolderPath: string;
  /** Compteurs agrégés par étape (voir → creuser) — conservés au-dessus des gestes. */
  readonly compteurs: ReadonlyArray<Compteur>;
  /** Lignes candidat éditables (agir). Vide si l'utilisateur n'est pas habilité (ACL, §3). */
  readonly candidats: ReadonlyArray<CandidatLigne>;
  /** Title déjà pris — base de l'allocation C-NNN du geste « ajouter ». */
  readonly titresPris: ReadonlyArray<string>;
  /** true si la lecture nominative a abouti (sinon : gestes masqués, compteurs seuls). */
  readonly gestesAccessibles: boolean;
  /** CodeMission des missions réelles (gabarits actifs) — options du dialogue de cascade. */
  readonly missionsConnues: ReadonlyArray<string>;
  /** Relit l'état persisté (anti-faux-vert) — résout APRÈS relecture. */
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

function statutNode(item: DetailItem): React.ReactElement {
  if (item.signal === 'neutral') {
    return <span className={styles.metaText}>{item.statut}</span>;
  }
  const variante = item.signal === 'info' ? styles.pillInfo : styles.pillSignal;
  return <span className={`${styles.pill} ${variante}`}>{item.statut}</span>;
}

/**
 * Bandeau 3 — Recrutement (tour-de-controle.md §3 bandeau 3). Voir → creuser → AGIR :
 * conserve les compteurs agrégés (RGPD option A) et ajoute, dessous, la table candidat éditable
 * (étape en ligne) et le formulaire « ajouter un candidat ». La bascule « Acceptée » n'écrit
 * jamais directement : elle ouvre la cascade déterministe (annonce exhaustive + confirmation,
 * §1 régime 2). Gestes sous l'identité de l'utilisateur (SSO), aucune élévation.
 */
export default function BandeauRecrutement(props: IBandeauRecrutementProps): React.ReactElement {
  const {
    spHttpClient, dataSiteUrl, msGraphClientFactory, saisieSiteUrl, saisieFolderPath,
    compteurs, candidats, titresPris, gestesAccessibles, missionsConnues, onMutation
  } = props;

  const [ouverts, setOuverts] = useState<ReadonlySet<string>>(() => new Set<string>());
  const basculer = useCallback((id: string): void => {
    setOuverts(prev => {
      const s = new Set(prev);
      if (s.has(id)) { s.delete(id); } else { s.add(id); }
      return s;
    });
  }, []);

  const [occupe, setOccupe] = useState<ReadonlySet<string>>(() => new Set<string>());
  const [retours, setRetours] = useState<Readonly<Record<string, Retour>>>({});

  const marquerOccupe = useCallback((slot: string, on: boolean): void => {
    setOccupe(prev => {
      const s = new Set(prev);
      if (on) { s.add(slot); } else { s.delete(slot); }
      return s;
    });
  }, []);

  const appliquer = useCallback(async (slot: string, faire: () => Promise<Ecriture>): Promise<Retour> => {
    marquerOccupe(slot, true);
    setRetours(prev => { const c = { ...prev }; delete c[slot]; return c; });
    const r = retourDe(await faire());
    if (r.kind === 'ok') { await onMutation(); }
    setRetours(prev => ({ ...prev, [slot]: r }));
    marquerOccupe(slot, false);
    return r;
  }, [marquerOccupe, onMutation]);

  // --- Cascade « Acceptée » -------------------------------------------------
  const deps = useMemo(
    () => depsCascadePour(spHttpClient, dataSiteUrl, { siteUrl: saisieSiteUrl, folderPath: saisieFolderPath }, msGraphClientFactory),
    [spHttpClient, dataSiteUrl, saisieSiteUrl, saisieFolderPath, msGraphClientFactory]
  );

  const [pendingCascade, setPendingCascade] = useState<CandidatLigne | null>(null);
  const [identifiantEntra, setIdentifiantEntra] = useState('');
  const [disponibilite, setDisponibilite] = useState('');
  const [codeMission, setCodeMission] = useState('');
  const [mois, setMois] = useState('');            // format « AAAA-MM » (input month)
  const [joursPrevus, setJoursPrevus] = useState('');
  const [cascadeEtat, setCascadeEtat] = useState<EtatCascade | null>(null);
  const [cascadeEnCours, setCascadeEnCours] = useState(false);

  const fermerCascade = useCallback((): void => {
    setPendingCascade(null);
    setCascadeEtat(null);
    setIdentifiantEntra(''); setDisponibilite(''); setCodeMission(''); setMois(''); setJoursPrevus('');
  }, []);

  // Le mois est saisi en « AAAA-MM » (input month) ; l'affectation le veut au 1er du mois (§5.2).
  const moisPremierDuMois = mois ? `${mois}-01` : '';
  const joursNombre = Number(joursPrevus);
  const saisieCascade: SaisieCascade = {
    identifiantEntra: identifiantEntra.trim(),
    disponibilite: disponibilite.trim(),
    codeMission: codeMission.trim(),
    mois: moisPremierDuMois,
    joursPrevus: joursNombre
  };
  const cascadeValide =
    saisieCascade.identifiantEntra !== '' &&
    saisieCascade.disponibilite !== '' &&
    saisieCascade.codeMission !== '' &&
    saisieCascade.mois !== '' &&
    Number.isFinite(joursNombre) && joursNombre > 0;

  const confirmerCascade = useCallback(async (candidat: CandidatLigne): Promise<void> => {
    setCascadeEnCours(true);
    const etat = await executerCascade(
      { id: candidat.id, title: candidat.title, nom: candidat.nom, grade: candidat.grade, etape: candidat.etape },
      saisieCascade,
      deps
    );
    setCascadeEtat(etat);
    if (etat.ok) { await onMutation(); }
    setCascadeEnCours(false);
  }, [deps, onMutation, saisieCascade]);

  // --- Geste « ajouter un candidat » ---------------------------------------
  const [nomC, setNomC] = useState('');
  const [gradeC, setGradeC] = useState('');
  const [sourceC, setSourceC] = useState('');
  const [emailC, setEmailC] = useState('');
  const [telC, setTelC] = useState('');

  const prochainTitle = useMemo(
    () => prochainTitleCandidat(titresPris.map(t => ({ Title: t }))),
    [titresPris]
  );

  const formValide = nomC.trim() !== '' && gradeC !== '' && sourceC !== '' && emailC.trim() !== '';

  const soumettreAjout = useCallback(async (): Promise<void> => {
    if (!formValide) { return; }
    const r = await appliquer('ajout', () =>
      creerCandidat(spHttpClient, dataSiteUrl, {
        title: prochainTitle,
        nom: nomC.trim(),
        grade: gradeC,
        source: sourceC,
        email: emailC.trim(),
        telephone: telC.trim() || undefined
      })
    );
    if (r.kind === 'ok') { setNomC(''); setGradeC(''); setSourceC(''); setEmailC(''); setTelC(''); }
  }, [appliquer, formValide, spHttpClient, dataSiteUrl, prochainTitle, nomC, gradeC, sourceC, emailC, telC]);

  const changerEtape = useCallback((c: CandidatLigne, etape: string): void => {
    if (etape === c.etape) { return; }
    // « Acceptée » : ouvre la cascade (annonce + confirmation) — jamais d'écriture directe (§3).
    if (etape === ETAPE_CANDIDAT_ACCEPTEE) { setCascadeEtat(null); setPendingCascade(c); return; }
    appliquer(`cand-${c.id}`, () => changerEtapeCandidat(spHttpClient, dataSiteUrl, c.id, etape)).catch(() => undefined);
  }, [appliquer, spHttpClient, dataSiteUrl]);

  const messageRetour = (slot: string): React.ReactElement | null => {
    const r = retours[slot];
    if (!r) { return null; }
    if (r.kind === 'ok') { return <span className={`${pipe.msg} ${pipe.msgOk}`}>Enregistré</span>; }
    if (r.kind === 'refuse') { return <span className={`${pipe.msg} ${pipe.msgRefuse}`}>Écriture refusée (droits)</span>; }
    return <span className={`${pipe.msg} ${pipe.msgIndispo}`}>Écriture indisponible</span>;
  };

  return (
    <div>
      {/* Compteurs agrégés (voir → creuser) */}
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

      {/* Gestes : masqués si l'utilisateur n'est pas habilité au recrutement (ACL, §3) */}
      {!gestesAccessibles ? (
        <p className={pipe.note}>
          Les gestes de recrutement (édition d’étape, ajout, décision) sont réservés aux personnes
          habilitées au recrutement — seuls les compteurs agrégés sont affichés ici.
        </p>
      ) : (
        <>
          {/* Table des candidats (agir — étape en ligne) */}
          <div className={pipe.section}>
            <p className={pipe.sectionTitre}>Candidats</p>
            {candidats.length === 0 ? (
              <p className={pipe.videText}>Aucun candidat à éditer pour l’instant.</p>
            ) : (
              <div>
                {candidats.map(c => {
                  const slot = `cand-${c.id}`;
                  const busy = occupe.has(slot);
                  const enCascade = pendingCascade?.id === c.id;
                  const annonce = enCascade ? construireAnnonce(
                    { id: c.id, title: c.title, nom: c.nom, grade: c.grade, etape: c.etape },
                    saisieCascade
                  ) : null;
                  return (
                    <React.Fragment key={c.id}>
                      <div className={pipe.oppRow}>
                        <span className={pipe.oppNom}>
                          <span className={pipe.oppTitre}>{c.title || '·'}</span>
                          <span className={pipe.oppCompte}>{c.nom || '·'}{c.grade ? ` — ${c.grade}` : ''}</span>
                        </span>
                        <select
                          className={`${pipe.champ} ${pipe.select}`}
                          aria-label={`Étape de ${c.title || c.nom}`}
                          value={ETAPES_CANDIDAT.indexOf(c.etape) >= 0 ? c.etape : ''}
                          disabled={busy}
                          onChange={e => changerEtape(c, e.target.value)}
                        >
                          {ETAPES_CANDIDAT.indexOf(c.etape) < 0 ? <option value="">·</option> : null}
                          {ETAPES_CANDIDAT.map(et => <option key={et} value={et}>{et}</option>)}
                        </select>
                        {messageRetour(slot)}
                      </div>

                      {/* Dialogue de cascade « Acceptée » (annonce exhaustive + confirmation, §1 régime 2) */}
                      {enCascade ? (
                        <div className={pipe.confirm}>
                          {cascadeEtat === null ? (
                            <>
                              <p className={pipe.confirmText}>
                                Accepter <span className={pipe.confirmNom}>{c.title || c.nom}</span> déclenchera
                                trois écritures. Renseignez la fiche, puis confirmez.
                              </p>
                              <div className={pipe.formGrid}>
                                <label className={pipe.formField}>
                                  <span className={pipe.formLabel}>Identité Entra (UPN)</span>
                                  <input className={pipe.champ} type="text" value={identifiantEntra} disabled={cascadeEnCours}
                                    onChange={e => setIdentifiantEntra(e.target.value)} />
                                </label>
                                <label className={pipe.formField}>
                                  <span className={pipe.formLabel}>Disponibilité</span>
                                  <input className={pipe.champ} type="text" value={disponibilite} disabled={cascadeEnCours}
                                    onChange={e => setDisponibilite(e.target.value)} />
                                </label>
                                <label className={pipe.formField}>
                                  <span className={pipe.formLabel}>Code mission</span>
                                  {missionsConnues.length > 0 ? (
                                    <select className={pipe.champ} value={codeMission} disabled={cascadeEnCours}
                                      onChange={e => setCodeMission(e.target.value)}>
                                      <option value="">· choisir une mission</option>
                                      {missionsConnues.map(m => <option key={m} value={m}>{m}</option>)}
                                    </select>
                                  ) : (
                                    <input className={pipe.champ} type="text" inputMode="numeric" value={codeMission}
                                      disabled={cascadeEnCours} onChange={e => setCodeMission(e.target.value)} />
                                  )}
                                </label>
                                <label className={pipe.formField}>
                                  <span className={pipe.formLabel}>Mois</span>
                                  <input className={pipe.champ} type="month" value={mois} disabled={cascadeEnCours}
                                    onChange={e => setMois(e.target.value)} />
                                </label>
                                <label className={pipe.formField}>
                                  <span className={pipe.formLabel}>Jours prévus</span>
                                  <input className={pipe.champ} type="number" inputMode="numeric" value={joursPrevus}
                                    disabled={cascadeEnCours} onChange={e => setJoursPrevus(e.target.value)} />
                                </label>
                              </div>
                              {/* Annonce EXHAUSTIVE des trois écritures */}
                              <p className={pipe.confirmMention}>Écritures qui seront effectuées, sur confirmation :</p>
                              {annonce?.map((l, i) => (
                                <div key={i} className={styles.detailRow}>
                                  <span>{i + 1}. {l.cible}</span>
                                  <span className={styles.metaText}>{l.detail}</span>
                                </div>
                              ))}
                              <div className={pipe.confirmActions}>
                                <button type="button" className={pipe.btn} disabled={!cascadeValide || cascadeEnCours}
                                  onClick={() => { confirmerCascade(c).catch(() => undefined); }}>
                                  Confirmer la cascade
                                </button>
                                <button type="button" className={pipe.btnSecondaire} disabled={cascadeEnCours}
                                  onClick={fermerCascade}>
                                  Annuler
                                </button>
                              </div>
                            </>
                          ) : (
                            <>
                              <p className={cascadeEtat.ok ? pipe.confirmText : pipe.refus}>{cascadeEtat.resume}</p>
                              <div className={pipe.confirmActions}>
                                <button type="button" className={pipe.btnSecondaire} onClick={fermerCascade}>Fermer</button>
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
          </div>

          {/* Formulaire « ajouter un candidat » (agir — création, étape E1) */}
          <div className={pipe.section}>
            <p className={pipe.sectionTitre}>Ajouter un candidat <span className={pipe.euro}>{prochainTitle}</span></p>
            <div className={pipe.form}>
              <div className={pipe.formGrid}>
                <label className={pipe.formField}>
                  <span className={pipe.formLabel}>Nom du candidat</span>
                  <input className={pipe.champ} type="text" value={nomC} onChange={e => setNomC(e.target.value)} />
                </label>
                <label className={pipe.formField}>
                  <span className={pipe.formLabel}>Grade visé</span>
                  <select className={pipe.champ} value={gradeC} onChange={e => setGradeC(e.target.value)}>
                    <option value="">· choisir un grade</option>
                    {GRADES_CANDIDAT.map(g => <option key={g} value={g}>{g}</option>)}
                  </select>
                </label>
                <label className={pipe.formField}>
                  <span className={pipe.formLabel}>Source</span>
                  <select className={pipe.champ} value={sourceC} onChange={e => setSourceC(e.target.value)}>
                    <option value="">· choisir une source</option>
                    {SOURCES_CANDIDAT.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </label>
                <label className={pipe.formField}>
                  <span className={pipe.formLabel}>Email</span>
                  <input className={pipe.champ} type="email" value={emailC} onChange={e => setEmailC(e.target.value)} />
                </label>
                <label className={pipe.formField}>
                  <span className={pipe.formLabel}>Téléphone (optionnel)</span>
                  <input className={pipe.champ} type="tel" value={telC} onChange={e => setTelC(e.target.value)} />
                </label>
                <label className={pipe.formField}>
                  <span className={pipe.formLabel}>Étape</span>
                  <input className={pipe.champ} type="text" value="E1" disabled readOnly />
                </label>
              </div>
              <div className={pipe.formActions}>
                <button type="button" className={pipe.btn} disabled={!formValide || occupe.has('ajout')}
                  onClick={() => { soumettreAjout().catch(() => undefined); }}>
                  Ajouter le candidat
                </button>
                {messageRetour('ajout')}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
