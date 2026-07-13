# Registre des activités de traitement (RGPD art. 30) — Allia Consulting

> **Version** : 1.0 — *candidat*. **Statut** : contrat socle — **attend la promotion du gardien-DPO**.
> **Changelog** : v1.0 — candidat, 13 juillet 2026 : création. Chantier `backlog/chantiers/T-0028.yaml` (manque nommé à l'audit du 07/07/2026 : le registre art. 30 n'existait pas encore au canon). Recense les traitements réels identifiés à date — écoute Teams/Claude, recrutement candidats, mémoire d'organisation, journal d'appel MCP, cockpit « Tour de contrôle » — chacun rattaché à sa base légale, ses durées et ses mesures, **par renvoi** aux contrats et analyses existants. Aucune analyse n'est dupliquée : ce registre est l'**index**.
> **Domicile** : `contrats/socle/registre-traitements-art30.md`. **Autorité de promotion** : gardien du temple.
> **Responsable de traitement** : **Allia Consulting** (coordonnées légales complètes — SIRET, adresse — *à compléter par le DPO*). **DPO** : **Adrien Raque** (adrien.raque@allia-consulting.com).
> **Adossé à** : `doctrine/doctrine.md` (§9 confidentialité/conformité), `contrats/socle/rgpd-ecoute-teams.md` (+ annexes 1 mise en balance / 2 AIPD / 3 information), `contrats/socle/rgpd-recrutement-candidats.md` (+ annexes 1 mise en balance / 3 information), `contrats/socle/memoire-organisation.md`, `contrats/socle/tour-de-controle.md`, `contrats/socle/identites-et-secrets.md` (mesures de sécurité — zéro secret), `backlog/chantiers/T-0025.yaml` (domicile de purge) et `backlog/chantiers/T-0013-d.yaml` (mécanisme de purge recrutement).
> **Nature des décisions** : ce registre **consigne** l'état du canon ; il ne tranche aucune question juridique. Tout champ non tranché par le canon est marqué **« à compléter par le DPO »** — un trou visible plutôt qu'une fiction. Les analyses (mise en balance, AIPD) **font foi dans leurs annexes**, pas ici.

## 0. Objet et principe d'index

Tenir le **registre des activités de traitement** exigé du responsable de traitement (RGPD **art. 30(1)**). Une **fiche par traitement réel** ; chaque fiche porte les champs de l'art. 30(1) et **renvoie** (pull) au contrat, à l'AIPD, à la mise en balance et au chantier de purge qui font foi. Le registre est **l'index qui fait foi de la liste des traitements** — il n'est pas un double des analyses.

**Règle d'honnêteté (inscrite en dur).** Aucun fait juridique ou factuel n'est inventé ici. Là où le canon est **muet** (base légale non tranchée, durée non chiffrée, sous-traitant/localisation non documenté), la fiche écrit **« à compléter par le DPO »** avec le renvoi utile. Le §9 récapitule tous ces trous.

**Règle de tenue.** Toute **nouvelle activité de traitement ouvre une entrée ICI AVANT sa mise en service** (boucle de promotion) ; chaque contrat RGPD existant **pointe** vers sa fiche (pull, pas de copie).

## 1. Responsable, DPO, portée

- **Responsable de traitement** : Allia Consulting — décide des finalités et des moyens.
- **DPO** : Adrien Raque (adrien.raque@allia-consulting.com) — conseille et contrôle, en indépendance fonctionnelle.
- **Cumul de rôles assumé (firme solo)** : responsable de traitement / gardien / DPO sont **distincts par nature**, portés aujourd'hui par une même personne (`rgpd-ecoute-teams.md` §9, `rgpd-recrutement-candidats.md` §9). La séparation se concrétisera à l'échelle.
- **Portée** : les traitements de données personnelles opérés par le SI d'Allia identifiés à date. La liste est **ouverte** — elle s'étend par la règle de tenue (§0).

## 2. Convention de lecture d'une fiche

Chaque fiche (§3 à §7) porte les champs de l'**art. 30(1)** : finalité(s) · base légale · catégories de personnes concernées · catégories de données · catégories de destinataires (dont sous-traitants) · transferts hors UE · délais d'effacement · mesures de sécurité (renvoi art. 32, §8). La colonne « fait foi / renvoi » dit **où vit la vérité** : ici on indexe, là-bas on analyse.

---

## 3. Traitement T1 — Écoute Teams/Claude → mémoire d'organisation (collecte & production)

| Champ art. 30(1) | Valeur | Fait foi / renvoi |
|---|---|---|
| Finalité | Produire une **synthèse hebdomadaire candidate d'apprentissages et de décisions COLLECTIFS** ; **interdit** : surveillance, évaluation ou mesure de performance individuelle, profilage | `rgpd-ecoute-teams.md` §1 |
| Base légale | **Intérêt légitime** (art. 6.1.f) — mise en balance documentée | `rgpd-ecoute-teams.md` §2 ; **annexe 1** (mise en balance) |
| Personnes concernées | **Collaborateurs** de la firme (conversations Teams/Claude de la semaine) ; **clients mentionnés incidemment** | `rgpd-ecoute-teams.md` §0, §5 ; annexe 1 §3 (périmètre : Claude = espace Allia, utilisateur courant ; Teams = canaux/missions, **hors 1-à-1**) |
| Catégories de données | Verbatim de conversations professionnelles (Teams + Claude) ; synthèse nominative d'apprentissages collectifs | `rgpd-ecoute-teams.md` §3 ; `memoire-organisation.md` §4 |
| Destinataires / sous-traitants | Interne : le gardien-DPO (et rôles désignés). **Sous-traitants** : **Microsoft** (M365/SharePoint — écriture en Zone-de-proposition) ; **Anthropic** (éditeur du modèle traitant les conversations en session claude.ai) | `rgpd-ecoute-teams.md` §7 ; **annexe 2 (AIPD) §1, §3(b)** (Anthropic sous-traitant) |
| Transferts hors UE | Exécution/écriture M365 sous identité du tenant ; **localisation et régime de transfert du sous-traitant Anthropic** : *à compléter par le DPO* (le canon nomme Anthropic sous-traitant mais ne documente ni sa localisation ni le mécanisme de transfert) | annexe 2 §1, §3(b) |
| Délais d'effacement | **Verbatim brut : J+7 calendaires** après la validation du vendredi ; **synthèse candidate non validée : supprimée** après la décision du vendredi ; **ne subsiste que la ligne validée** (voir T2) | `rgpd-ecoute-teams.md` §4 ; **annexe 1 §5** (J+7) |
| Mesures de sécurité (art. 32) | Zéro secret ; identité Entra (OAuth délégué) ; périmètre gardien seul ; écriture MCP restreinte à la seule liste Zone-de-proposition (cible figée) ; substrat M365 | §8 ; annexe 2 §3(b) ; `identites-et-secrets.md` |
| Formalités | **AIPD produite** (art. 35) ; **information préalable** obligatoire avant première écoute d'un collaborateur (via onboarding) | annexe 2 (AIPD) ; annexe 3 (gabarit d'information) ; `rgpd-ecoute-teams.md` §5, §7 |

## 4. Traitement T2 — Mémoire d'organisation (conservation des lignes validées)

| Champ art. 30(1) | Valeur | Fait foi / renvoi |
|---|---|---|
| Finalité | Conserver, comme mémoire de la firme, **les seuls apprentissages/décisions collectifs explicitement validés** ligne à ligne le vendredi | `memoire-organisation.md` §0, §3 |
| Base légale | **Intérêt légitime** (art. 6.1.f) — aval du traitement d'écoute T1, même cadre | `memoire-organisation.md` §5 ; `rgpd-ecoute-teams.md` §2 |
| Personnes concernées | Collaborateurs (et clients) nommés dans les lignes de mémoire retenues | `memoire-organisation.md` §4 |
| Catégories de données | Lignes de synthèse **internes et nominatives** (apprentissages, décisions) promues | `memoire-organisation.md` §4 |
| Destinataires / sous-traitants | Interne (collaborateurs de la firme). Sous-traitant : **Microsoft** (M365/SharePoint — liste Zone-de-proposition puis mémoire promue) | `memoire-organisation.md` §2 |
| Transferts hors UE | Substrat M365 du tenant ; **localisation M365 / transferts** : *à compléter par le DPO* (non documenté au canon) | — |
| Délais d'effacement | **Non-validé = oublié** (pas de rétention par défaut). **Durée de conservation de la ligne VALIDÉE (promue)** : *à compléter par le DPO* — le canon pose « ne subsiste que le validé » et l'effacement sur **opposition/retrait tracé**, mais **ne chiffre pas** de durée de conservation de la ligne promue | `memoire-organisation.md` §3 ; `rgpd-ecoute-teams.md` §6 (opposition/retrait) |
| Mesures de sécurité (art. 32) | Idem T1 (écriture Zone-de-proposition, identité Entra, zéro secret) ; retrait/rectification d'une ligne = action tracée | §8 ; `rgpd-ecoute-teams.md` §6 |
| Formalités | Couvert par l'AIPD et l'information préalable de T1 (même mécanisme d'écoute) | annexe 2 ; annexe 3 |

## 5. Traitement T3 — Recrutement & données candidats

| Champ art. 30(1) | Valeur | Fait foi / renvoi |
|---|---|---|
| Finalité | **Instruire** les candidatures (sourcing → décision) et **alimenter un vivier** de profils non retenus ; **interdit** : décision entièrement automatisée (art. 22), profilage, données sensibles | `rgpd-recrutement-candidats.md` §1 |
| Base légale | **Double régime** : instruction = **mesures précontractuelles (art. 6.1.b)** ; vivier = **intérêt légitime (art. 6.1.f)**, mise en balance documentée | `rgpd-recrutement-candidats.md` §2 ; **annexe 1** (mise en balance) |
| Personnes concernées | **Candidats externes** à la firme | `rgpd-recrutement-candidats.md` §0 |
| Catégories de données | Données pertinentes au poste (parcours, compétences, expérience, coordonnées) ; **synthèses d'entretien** (appréciation, accessible au candidat) ; **jamais** de données sensibles | `rgpd-recrutement-candidats.md` §3, §4 (checklist figée) ; `modele-donnees.md` §2 bis/§2 ter (listes Candidats / Candidats-Synthèses) |
| Destinataires / sous-traitants | Interne : personnes en charge du recrutement du poste. Sous-traitant : **Microsoft** (M365/SharePoint) | `rgpd-recrutement-candidats.md` §3 |
| Transferts hors UE | Substrat M365 du tenant ; **localisation M365 / transferts** : *à compléter par le DPO* (non documenté au canon) | — |
| Délais d'effacement | **Instruction** : jusqu'à la décision (s'éteint avec elle). **Vivier** : **2 ans à compter de la date d'inscription** (horloge FIXE, non glissante, « Créé le »), puis suppression/anonymisation irréversible. **Notes brutes** d'entretien : **éphémères** (purgées à la clôture de l'instruction). Purge **outillée** (T-0013-d), domicile de croisière = T-0025 | `rgpd-recrutement-candidats.md` §5 ; `T-0013-d` ; `T-0025` |
| Mesures de sécurité (art. 32) | Journalisation d'audit (prérequis `T-0003`), moindre privilège, purge gouvernée sous identité dédiée (T-0025) | §8 ; `T-0025` |
| Formalités | **AIPD non requise** (conclusion motivée du gardien-DPO — pas de surveillance systématique, pas de décision automatisée, pas de profilage) ; **information préalable** produite | **annexe 1 §6** (AIPD non requise) ; annexe 3 (gabarit d'information) ; `rgpd-recrutement-candidats.md` §6, §11 |

## 6. Traitement T4 — Journal d'appel du service MCP Graph (observabilité)

| Champ art. 30(1) | Valeur | Fait foi / renvoi |
|---|---|---|
| Finalité | **Traçabilité et observabilité** des appels d'outils du service MCP Graph (bon fonctionnement, sécurité, traçabilité par personne) | `T-0020.yaml` (sous-tâche b) ; `T-0009.yaml` (traçabilité par personne) |
| Base légale | *À compléter par le DPO* — le canon **ne tranche pas** de base légale pour ce journal (vraisemblablement intérêt légitime : sécurité et bon fonctionnement du SI, **à confirmer**) | — |
| Personnes concernées | **Collaborateurs appelant le service** (identité appelante journalisée) | `T-0009.yaml` (en-têtes `X-MS-CLIENT-PRINCIPAL-*`) |
| Catégories de données | **Identité appelante** (en-têtes `X-MS-CLIENT-PRINCIPAL-*`, T-0009) + **métadonnées d'appel** : horodatage (UTC), outil, cran, résultat (succès/refus/erreur), durée — **sans donnée personnelle en clair au-delà de l'identité appelante** (T-0020-b) | `T-0009.yaml` ; `T-0020.yaml` §b (critère « sans donnée personnelle en clair ») |
| Destinataires / sous-traitants | Interne (gardien) ; sous-traitant : **Microsoft Azure** (Azure Container Apps + **Log Analytics**) | `architecture.md` Partie C ; `T-0020.yaml` §b |
| Transferts hors UE | **Non** — Log Analytics `workspace-rgiascaleQW10`, région **France Central** (UE) | `T-0020.yaml` §b ; `T-0018.yaml` ; `architecture.md` |
| Délais d'effacement | **Durée de rétention Log Analytics** : *à compléter par le DPO* (aucune valeur fixée au canon) | — |
| Mesures de sécurité (art. 32) | Identité managée / identité Entra ; Easy Auth (bearer OAuth 2.0, sinon 401) ; TLS ingress ; zéro secret Graph | §8 ; `identites-et-secrets.md` §2 ; `architecture.md` |

## 7. Traitement T5 — Cockpit « Tour de contrôle » (restitution)

| Champ art. 30(1) | Valeur | Fait foi / renvoi |
|---|---|---|
| Finalité | Restituer à l'utilisateur ce qui le concerne et les actions qu'il peut déclencher (pilotage) — **cockpit consommateur** des listes M365, **jamais un double éditable** | `tour-de-controle.md` §0, §1 |
| Base légale | *À compléter par le DPO* — non tranchée au canon (le cockpit **consomme** des traitements existants ; vraisemblablement intérêt légitime de pilotage, **à confirmer**) | — |
| Personnes concernées | **Collaborateurs** (activité des équipes) ; **candidats** uniquement en **agrégats** | `tour-de-controle.md` §3 |
| Catégories de données | **Agrégats / KPI** lus des listes M365 (pipe commercial, recrutement en agrégats, rentabilité, activité) ; **le recrutement n'est affiché qu'en agrégats** | `tour-de-controle.md` §3 |
| Destinataires / sous-traitants | Interne (collaborateurs). Sous-traitant : **Microsoft** (SharePoint/SPFx) | `tour-de-controle.md` §4 |
| Transferts hors UE | Substrat M365 du tenant ; **localisation M365 / transferts** : *à compléter par le DPO* | — |
| Délais d'effacement | **Aucun stockage propre** : le cockpit lit les listes en *pull* (pas de double éditable) — la rétention est **celle des traitements sources** (T2, T3, missions/CRM `modele-donnees.md`) | `tour-de-controle.md` §1, §6 |
| Mesures de sécurité (art. 32) | SSO M365 (SPFx dans SharePoint) ; lecture native des listes sous droits du tenant ; les actions déclenchées portent le cran de l'action sous-jacente | §8 ; `tour-de-controle.md` §5 |

---

## 8. Mesures de sécurité communes (art. 32) — renvoi

Les mesures ne sont pas recopiées ici ; elles **font foi** dans les contrats d'infrastructure et de sécurité. Principales, attestées au canon :

- **Zéro secret applicatif** : humains par identité Entra (OAuth PKCE), workloads par **identité managée** — `identites-et-secrets.md` §1/§2.
- **Entrée du service MCP** : Easy Auth Entra (bearer OAuth 2.0, sinon 401) ; TLS assuré par l'ingress Container Apps — `architecture.md` Partie C.
- **Écriture agent restreinte** à la liste **Zone-de-proposition** (cible figée côté serveur) ; le dérivé n'est jamais le saisi — `doctrine.md` §2.
- **Moindre privilège** M365 (`Sites.Selected`) et rôle Entra scopé à une Administrative Unit de périmètre — `organisation.md` §5.
- **Compte break-glass durci + alerte de connexion** (routage Entra → Log Analytics → Azure Monitor → email) — `T-0018.yaml`.
- **Purge gouvernée** du recrutement sous identité dédiée au moindre privilège — `T-0013-d.yaml`, domicile de croisière `T-0025.yaml`.

## 9. Champs « à compléter par le DPO » (récapitulatif des trous)

Trous **assumés et visibles** à date, à trancher par le DPO (aucune valeur inventée) :

1. **Coordonnées légales complètes du responsable** (SIRET, adresse) — en-tête.
2. **T1 — transferts hors UE / localisation du sous-traitant Anthropic** et régime de transfert (le canon le nomme sous-traitant sans documenter sa localisation) — §3.
3. **T2 — durée de conservation de la ligne de mémoire VALIDÉE (promue)** : non chiffrée au canon (« non-validé = oublié » est posé ; la durée du validé ne l'est pas) — §4.
4. **T3 — localisation des données M365 / transferts hors UE** : non documentée au canon — §5.
5. **T4 — base légale du journal d'appel MCP** : non tranchée — §6.
6. **T4 — durée de rétention Log Analytics** : non fixée — §6.
7. **T5 — base légale du cockpit** : non tranchée — §7.
8. **T5 / T3 — localisation M365 / transferts hors UE** : non documentée — §5, §7.
9. **Interface concrète d'exercice des droits** des personnes (accès, rectification, effacement, opposition) — `rgpd-ecoute-teams.md` §11.5 ; `rgpd-recrutement-candidats.md` §11.5.
10. **Information-consultation des représentants du personnel** (droit du travail, aux seuils d'effectif) — `rgpd-ecoute-teams.md` §11.3 ; `rgpd-recrutement-candidats.md` §11.6.
11. **Validation juridique RGPD** d'ensemble, idéalement avec un conseil — `rgpd-recrutement-candidats.md` §11.7.

## 10. Gouvernance et évolution

Contrat socle : ce registre n'évolue que par la **boucle de promotion** (`doctrine.md` §7) — candidat (PR), avis d'impact, décision du gardien attachée à l'empreinte exacte, promotion, retour arrière par repointage. Il est **opposable à l'autorité de contrôle** : sa promotion et sa tenue à jour relèvent du gardien-DPO.

**Règle de tenue (inscrite en dur)** : *toute nouvelle activité de traitement ouvre une entrée ICI **avant** sa mise en service* ; chaque contrat RGPD existant **pointe** vers sa fiche (pull, pas de copie). Fermer un champ « à compléter » (§9) est lui-même un candidat promu.

---

*Contrat socle candidat — registre des activités de traitement (RGPD art. 30). Index des traitements réels d'Allia : il renvoie aux contrats et analyses qui font foi, il ne les duplique pas. Les trous du §9 restent à la main du gardien-DPO. Il attend la promotion du gardien.*
