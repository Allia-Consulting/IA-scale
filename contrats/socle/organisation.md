# Organisation & délégations — Allia Consulting

> **Version** : 1.0 — *candidat*. Troisième contrat socle, aux côtés de `/doctrine/doctrine.md` et `/backlog/plan.md`.
> **Statut** : Contrat socle — fait foi.
> **Domicile** : Dépôt de fondations (Git), `/contrats/socle/organisation.md`.
> **Autorité de promotion** : Gardien du temple.
> **Portée** : Toute l'organisation Allia.

La doctrine définit *les règles et les rôles* (en abstrait). Le plan définit *le chantier*. Ce document définit **qui répond de quoi** : il lie les rôles abstraits de la doctrine à des périmètres concrets et à leurs titulaires, et il gouverne la délégation. C'est la « réalisation » de la gouvernance, rendue canonique et gouvernable — ce que la doctrine laisse délibérément de côté pour rester stable (principe « capacités stables, réalisation volatile »).

---

## 0. Objet et frontière

Ce document **dit** : la carte des périmètres, qui tient quel rôle sur quel périmètre, et ce qu'une délégation accorde.

Ce document **ne dit pas** : la définition des rôles (→ doctrine §3), ni les dossiers RH des personnes (→ M365). Il référence, il ne duplique pas.

## 1. Trois vérités distinctes : identité, décision, droits

Chacune vit à un seul endroit ; aucune n'est copiée.

- **L'identité** (qui est la personne : compte, profil, grade) → M365 / Entra. *Source.*
- **La décision de délégation** (qui anime quel périmètre) → ce contrat, dans le dépôt (« le guide »). *Source.*
- **Les droits d'accès** (ce à quoi la personne accède) → *dérivés* de la décision, réconciliés dans M365, jamais saisis à la main (voir §5).

Ce contrat nomme « le titulaire du rôle R sur le périmètre P » par un identifiant Entra ; il ne duplique aucun dossier RH.

## 2. La carte des périmètres (dérivée de la carte des capacités)

Un périmètre est une capacité, ou un groupe cohérent de capacités, dont un animateur peut répondre. Grille de départ, alignée sur la carte des capacités :

- **Pilotage** — stratégie & offre · performance & gouvernance.
- **Cœur de métier** — développement commercial · delivery · relation client · connaissance, contenu & IP (dont **communication & marque**).
- **Capacités habilitantes** — talent & RH · gestion financière · ressources & capacité · corporate & conformité.
- **Socle d'exploitation & gouvernance** — orchestration des agents · référentiel & cycle de vie des agents · évaluation & observabilité · adoption multi-utilisateurs (RBAC).

Le gardien décide de la granularité : on délègue rarement une capacité isolée, plus souvent un domaine cohérent.

## 3. Les titulaires aujourd'hui (état réel)

La firme repose aujourd'hui sur une personne. Par défaut, **le gardien (fondateur) tient le rôle de gardien et anime tous les périmètres** ; aucune délégation n'est encore active.

| Périmètre | Animateur (titulaire) | Statut |
|---|---|---|
| Tous les périmètres | Le gardien (fondateur) | non délégué |
| Communication & marque | Le gardien (fondateur) | délégable en priorité |
| … | — | à déléguer |

*Aucun nom de futur collaborateur n'est inventé : les lignes futures restent en attente jusqu'à une délégation réelle.*

## 4. Ce qu'une délégation accorde — et n'accorde pas

Déléguer l'animation d'un périmètre P à une personne Y :

- **accorde** : proposer des candidats sur les **contrats locaux** de P (procédure allégée, doctrine §5 et §7) ; faire évoluer le périmètre ;
- **n'accorde pas** : promouvoir (le gardien promeut) ; toucher au socle ; animer hors de P.

Une délégation est elle-même un **acte de promotion** sur ce contrat (gardien seul). La **révocation** est un repointage — une seule action, comme tout retour arrière.

À l'échelle 50-200 (fédération de la promotion, doctrine §10), le gardien pourra déléguer en plus le **droit de promotion local** par domaine ; c'est ici qu'il sera enregistré, le gardien conservant le socle.

## 5. Droits d'accès — décision dans le guide, droits réconciliés dans M365

Les droits ne se saisissent pas à la main : ils sont le **dérivé** d'une décision de délégation promue. La décision est la *source* (ce contrat, dans le dépôt — « le guide ») ; les droits M365 en sont la *projection*, réconciliée, jamais éditée directement. C'est « le dérivé n'est jamais le saisi » appliqué aux accès.

**Chaîne d'autorité — le guide → Claude → M365 :**

1. **Identité (SSO)** — une seule identité par personne, fournie par Entra, pour accéder au guide (GitHub), à Claude et à M365. Pas de second annuaire.
2. **Décision (le guide, Git)** — ce contrat nomme, par périmètre, le titulaire par son identifiant Entra. La décision n'entre en vigueur que **promue** par le gardien (porte humaine, cran *validé* — modifier des droits est à large rayon d'impact et sensible).
3. **Réconciliation (Claude)** — un réconciliateur, au **moindre privilège**, lit le canon et fait correspondre l'appartenance au **groupe Entra du périmètre** (ex. `anim-communication`), en idempotent (il n'applique que le delta). Les ressources SharePoint / Teams sont liées au groupe, jamais aux individus.
4. **Application (M365)** — l'appartenance au groupe ouvre l'accès. Attribuer = ajouter au groupe ; révoquer = retirer. Le « retour arrière en une action » s'étend ainsi aux accès.

**Inscrit en dur (non négociable, dès qu'il y a délégation) :**

- la porte humaine reste à la **promotion** du contrat — c'est la décision du gardien qui autorise ;
- le réconciliateur est au **moindre privilège** : une app registration qui ne sait gérer *que* ces groupes, rien d'autre ; tout changement tracé ;
- le **déploiement et la mise en production restent sous le contrôle du gardien** : il modifie le guide (le canon), et Claude puis M365 suivent en conséquence. Aucun droit ne change hors de cette chaîne.

**Runbook humain (ni Claude ni agent) :** créer l'app registration, donner le consentement admin, stocker le secret. Ni Claude ni un agent ne configurent de permissions ni ne saisissent de secret (plan §2).

Tant que la firme est solo, il n'y a rien à réconcilier : le modèle se *conçoit* maintenant (groupes + champ titulaire + interface du réconciliateur) et s'*active* à la première délégation réelle — au cap Ouverture.

## 6. Cycle de vie d'une délégation — exemple « Communication & marque »

1. **Candidat** : préparer (via Claude) une modification de ce contrat affectant Communication à Y.
2. **Conformité** : l'agent-gardien vérifie que rien ne casse et calcule le rayon d'impact.
3. **Promotion** : le gardien approuve ; Y devient animateur de Communication.
4. **Effet** : Y peut proposer sur `/contrats/local/communication/*` (piliers éditoriaux, voix de marque, templates) ; il ne promeut pas.
5. **Réconciliation** : les droits se projettent sur le groupe Entra du périmètre (réconciliateur au moindre privilège — ou à la main lors des toutes premières délégations).
6. **Communication (option)** : annonce à l'équipe (cran *notifié*).
7. **Révocation** : repointer en une action.

## 7. Confidentialité

Ce contrat est interne à la firme et référence les personnes par identifiant ; aucun dossier RH n'y est dupliqué. Les identités et leurs détails restent dans M365, sous contrôle d'accès. La règle d'anonymisation (contrat socle dédié) gouverne la réutilisation inter-client ; elle ne s'applique pas ici, qui relève de la donnée d'organisation interne — mais l'accès y est restreint au strict nécessaire.

## 8. Articulation avec les grades

Un **animateur** est typiquement un Manager ou un Associé qui pilote un savoir-faire ; tout collaborateur est **utilisateur** ; le **gardien** est au niveau firme. Le grade est un détail RH (M365 / documents talents) ; ce contrat enregistre la tenue d'un rôle sur un périmètre, pas le grade.

## 9. Comment ce document évolue

Contrat socle : chaque délégation, révocation ou redécoupage de périmètre est un candidat promu par le gardien (doctrine §7). Il se gouverne comme il prêche.

## 10. Hypothèses prises (à corriger par le gardien)

1. Les périmètres dérivent de la carte des capacités ; la granularité est au choix du gardien.
2. Identités / RH dans M365 (référencées par identifiant), délégations dans Git. Séparation recommandée dès maintenant.
3. Aujourd'hui : gardien unique tenant tous les périmètres ; aucun nom futur inventé.
4. Les droits sont un dérivé réconcilié de la décision promue (groupes Entra), jamais saisis ; la porte humaine reste à la promotion, le réconciliateur au moindre privilège. La mise en place du privilège (app registration, secret) reste un runbook humain.

> Pour corriger : ouvre un candidat, ne modifie pas ce fichier directement.
