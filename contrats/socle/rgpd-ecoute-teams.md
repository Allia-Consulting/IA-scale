# Cadre RGPD — écoute Teams/Claude de la mémoire d'organisation — Allia Consulting

> **Version** : 1.2 — *promu*. **Statut** : contrat socle — fait foi.
> **Changelog** : v1.2 — alignement minimal, 12 juin 2026 : §3 et §8 — la formule de déclenchement de la porte d'anonymisation renvoie au régime révisé d'`anonymisation.md` §1 (**communication grand public** ; matière d'un client tiers). Rien d'autre ; les annexes ne sont pas touchées (leur renvoi vers `anonymisation.md` §1 reste résolvable). v1.1 — 12 juin 2026 : adossement des deux annexes normatives (annexe 1 mise en balance §2 ; annexe 2 AIPD §7) ; périmètre d'écoute précisé par l'annexe 1 §3 (exclusion des 1-à-1 Teams ; côté Claude, espace Allia Consulting uniquement) ; durée de suppression du brut fixée à J+7 (annexe 1 §5) ; cases 1, 2 et 4 du §11 produites. Aucun autre changement de fond. 12 juin 2026 — promu via boucle de promotion ; contenu inchangé hors en-tête/statut. Rappel : AIPD (§7) et information préalable (§5) restent des préalables à l'écoute réelle.
> **Domicile** : `contrats/socle/rgpd-ecoute-teams.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `doctrine/doctrine.md` (§2 « le dérivé n'est jamais le saisi », §9 confidentialité/conformité), `contrats/socle/memoire-organisation.md`, `contrats/socle/anonymisation.md`.
> **Rattachement** : capacité *Corporate & conformité / Gouvernance IA responsable* ; chantiers `backlog/chantiers/T-0005.yaml` (mécanisme d'écoute) et `backlog/chantiers/T-0007.yaml` (onboarding — porteur de l'information préalable).
> **Nature des décisions** : ce contrat **consigne les arbitrages du gardien-DPO**, pas un avis juridique. Les points marqués *« à confirmer / produire par le gardien-DPO »* restent à sa main (voir §11).

## 0. Objet

Encadrer, au regard du RGPD, le **traitement de données personnelles** que constitue l'**écoute** des conversations **Teams + Claude** de la semaine par le batch de **mémoire d'organisation** (`memoire-organisation.md`, mécanisme `T-0005`). L'écoute porte sur des données de **collaborateurs** et, incidemment, de **clients mentionnés**. Ce contrat dit la **finalité**, la **base légale**, le **régime** des données, la **minimisation/rétention**, la **transparence**, les **droits des personnes** et les **formalités** — tels que le **gardien-DPO** les a tranchés.

Il ne duplique pas `memoire-organisation.md` (le mécanisme) ni `anonymisation.md` (la porte de sortie externe) : il **renvoie** à ces contrats et ajoute la **couche de conformité** de l'écoute.

## 1. Finalité — apprentissages et décisions collectifs, jamais la personne

**Décision du gardien-DPO.** La finalité du traitement est de produire une **synthèse hebdomadaire candidate d'apprentissages et de décisions COLLECTIFS** de la firme. Elle est **inscrite en dur** et **limite l'usage** :

- **interdit** — toute **surveillance**, **évaluation** ou **mesure de performance individuelle** ; tout profilage des personnes ; tout usage disciplinaire ou managérial individuel ;
- **autorisé** — capter ce que la firme **apprend et décide** collectivement, pour le retenir comme mémoire.

Le principe de **limitation des finalités** (RGPD) est ici une **contrainte d'exécution** : un usage hors de cette finalité est une violation du contrat, pas une simple mauvaise pratique.

## 2. Base légale — intérêt légitime (art. 6.1.f), test de mise en balance à documenter

**Décision du gardien-DPO.** La base légale retenue est l'**intérêt légitime** (RGPD **art. 6.1.f**) : faire vivre une mémoire d'organisation qui compose l'intelligence inter-missions (doctrine §9).

L'intérêt légitime exige un **test de mise en balance** (intérêt de la firme vs droits et libertés des personnes écoutées), **à documenter en annexe** de ce contrat. Ce test est **à produire / valider par le gardien-DPO** (§11) — il n'est pas réputé acquis par la seule mention de l'article. **Produit** : annexe 1 — `contrats/socle/annexes/rgpd-ecoute-teams--annexe-1-mise-en-balance.md` (12 juin 2026).

## 3. Régime des données — interne et nominatif

**Décision du gardien-DPO**, cohérente avec `memoire-organisation.md` §4 (régime **confirmé**, non modifié) :

- la **synthèse** est **interne et nominative** — elle nomme personnes, missions, clients comme la matière interne (avantage qui compose, doctrine §9) ;
- la **communication grand public** d'un fragment **déclenche la porte d'anonymisation** (`anonymisation.md` §1, régime révisé le 12 juin 2026) ; voir §8.

Le caractère nominatif **interne** ne dispense d'aucune obligation RGPD : il impose au contraire les garde-fous des §1, §4, §5 et §6.

## 4. Minimisation et rétention — le brut et le non-validé sont supprimés

**Décision du gardien-DPO.**

- **Verbatim brut écouté** (transcriptions Teams/Claude de la semaine) : matière **éphémère de traitement**, **supprimée après la décision de validation du vendredi** (§ validation : `memoire-organisation.md` §3). **Pas de rétention du brut.**
- **Synthèse candidate NON validée** : **supprimée** après la décision du vendredi. **Pas d'accumulation silencieuse.**
- **Ne subsiste que la ligne explicitement validée** ligne à ligne le vendredi (« non-validé = oublié », `memoire-organisation.md` §3). C'est la **minimisation** rendue exécutable.
- **Durée exacte de conservation du brut avant suppression** : *à fixer par le gardien-DPO* (§11) — aucune valeur n'est inventée ici ; le principe (« supprimé après la décision du vendredi ») est posé, le délai chiffré est laissé à sa main.

## 5. Transparence et information — préalable, via l'onboarding, AVANT l'écoute

**Décision du gardien-DPO.** L'**information préalable** des personnes est **obligatoire AVANT la première écoute** concernant un collaborateur.

- **Vecteur** : l'**onboarding** (`T-0007`). Mais c'est une **étape d'ordonnancement** : l'information **PRÉCÈDE l'activation de l'écoute** dans la séquence d'intégration — **pas** une case de fin de parcours. La contrainte est : *pas d'écoute d'un collaborateur tant qu'il n'a pas été informé.*
- **Firme solo aujourd'hui** : **rien à exécuter** (le fondateur est seul). L'obligation est néanmoins **posée comme déclencheur** : elle s'arme dès le premier collaborateur écouté.
- **Clients mentionnés incidemment** : l'information et la proportionnalité de leur traitement relèvent du test de mise en balance (§2) et des clauses NDA (`anonymisation.md` §5).

## 6. Droits des personnes — dont l'opposition (clé sous intérêt légitime)

**Décision du gardien-DPO.** Les personnes écoutées disposent des droits d'**accès**, **rectification**, **effacement** et **opposition**. L'**opposition** compte **particulièrement** ici, parce que la base légale est l'intérêt légitime (art. 6.1.f) : une personne peut s'opposer au traitement pour des raisons tenant à sa situation particulière.

- **Moyen concret** : prévoir qu'un collaborateur puisse faire **corriger ou retirer** une ligne le concernant **de la mémoire promue** (repointage / retrait tracé, cohérent avec « retour arrière en une action », doctrine §7).
- Le retrait d'une ligne validée suit la même traçabilité que sa promotion.
- L'**interface concrète** d'exercice des droits est *à définir par le gardien-DPO* (§11) ; le **droit**, lui, est inscrit ici.

## 7. Formalités — registre (art. 30) et AIPD (art. 35)

**Décision du gardien-DPO**, tenue par lui :

- **Registre des traitements** (RGPD **art. 30**) : ce traitement « écoute Teams/Claude → mémoire d'organisation » y est **inscrit** (finalité §1, base légale §2, catégories de données, durées §4, destinataires internes).
- **Analyse d'impact (AIPD / DPIA)** (RGPD **art. 35**) : une **surveillance systématique de communications** relève **typiquement** des cas où une analyse d'impact est requise. L'AIPD est **à produire / valider par le gardien-DPO** (§11) **avant l'écoute réelle**. **Produite** : annexe 2 — `contrats/socle/annexes/rgpd-ecoute-teams--annexe-2-aipd.md` (12 juin 2026).

## 8. Articulation avec l'anonymisation

Ce cadre régit l'**entrée** (l'écoute) et la **vie interne** (synthèse nominative, rétention minimale). La **communication grand public** d'un fragment de mémoire reste gouvernée par `anonymisation.md` (porte automatique, §1, régime révisé le 12 juin 2026 : communication grand public ; matière d'un client tiers), irréversibilité visée, porte du cran *validé*. Les deux contrats sont **complémentaires et orthogonaux** : l'un protège la **collecte et la rétention**, l'autre la **diffusion externe**.

## 9. Note de rôles — responsable de traitement, gardien, DPO

*Note formulée neutrement ; le gardien peut la retirer du canon à la review s'il préfère la tenir hors contrat.*

Aujourd'hui, le **fondateur cumule** trois rôles **distincts par nature** :

- **responsable de traitement** — décide des finalités et moyens (RGPD) ;
- **gardien du temple** — promeut les règles (doctrine §3) ;
- **DPO** — **conseille et contrôle** la conformité, en indépendance fonctionnelle.

Le **DPO conseille et contrôle** ; il ne décide pas à la place du responsable de traitement. Ces rôles ne se confondent pas — la distinction est **nommée** pour le jour où la firme grandit, **analogue à la double casquette gardien/associé** (`organisation.md` §3 bis). Tant que la firme est solo, une même personne les porte ; la séparation se concrétisera à l'échelle.

## 10. Crans et gouvernance

- **Produire la synthèse candidate** (écoute + écriture en zone de proposition) : cran **auto**, mais **subordonné** au respect du présent cadre — *pas d'écoute sans information préalable (§5) ni avant l'AIPD (§7)*.
- **Promouvoir ce cadre** : `promouvoir_contrat_socle` = **validé**, **porte humaine du gardien** (doctrine §6/§7).
- **Exercer un droit (rectification/retrait d'une ligne promue)** : action tracée, sous contrôle du gardien-DPO (§6).
- L'agent **n'écoute pas** un collaborateur non informé, **ne conserve pas** le brut, **ne promeut jamais**.

## 11. Cases laissées à la main du gardien-DPO (à confirmer / produire)

Explicitement **non tranchées** dans ce candidat — à produire/valider par le gardien-DPO **avant l'écoute réelle** :

1. **Test de mise en balance** de l'intérêt légitime (§2) — à documenter en annexe. **Produite — voir annexe 1** (`contrats/socle/annexes/rgpd-ecoute-teams--annexe-1-mise-en-balance.md`).
2. **AIPD / DPIA** (§7, art. 35) — surveillance systématique de communications. **Produite — voir annexe 2** (`contrats/socle/annexes/rgpd-ecoute-teams--annexe-2-aipd.md`).
3. **Information-consultation des représentants du personnel** — verrou **droit du travail**, le jour où les **seuils d'effectif** l'imposent. *(Aucun seuil ni délai n'est inventé ici ; à fixer par le gardien-DPO selon le droit applicable.)*
4. **Durée exacte de suppression du verbatim brut** (§4) — *à fixer par le gardien-DPO*. **Produite — voir annexe 1 §5** (J+7 calendaires après la validation du vendredi).
5. **Interface d'exercice des droits** des personnes (§6).

## 12. Comment ce contrat évolue

Contrat socle **promu** — il fait foi (doctrine §7). Toute évolution (finalité, durées, base légale, annexes de conformité) est elle-même un candidat, promu par le gardien. La promotion de ce cadre était un **prérequis normatif de l'écoute réelle** (`T-0005`) ; l'AIPD (§7) et l'information préalable (§5) en restent des préalables.

---

*Contrat socle promu — cadre RGPD de l'écoute Teams/Claude. Il fait foi et évolue par la boucle de promotion. Il consigne les décisions du gardien-DPO ; les cases juridiques du §11 restent à sa main.*
