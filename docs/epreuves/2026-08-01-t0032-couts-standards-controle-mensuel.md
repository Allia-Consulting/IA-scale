# Clôture du volet 4a de T-0032 — coûts standards, contrôle mensuel d'écart et correction gouvernée, éprouvés sur le réel — 01/08/2026

Rattachement : `T-0032` (référentiel de coûts + EBITDA + contrôle mensuel d'écart), volet **4a**. Journal de la journée du 01/08/2026 (S45) : un arbitrage de modèle, six PR, un incident de post-vérification instructif, et **deux épreuves réelles** — un premier contrôle mensuel, puis une **correction gouvernée** du mois déjà inscrit. Le chantier **n'est pas soldé** : ce qui manque est nommé au §7.

## 1. Point de départ mesuré (matin du 01/08)

Trois faits mesurés, qui ensemble rendaient le pilotage financier inutilisable :

- **L'EBITDA du cockpit était égal au CA à l'euro près.** Cause racine : `coutsMois` comptait `couts.get(ressource) ?? 0` — un **coût inventé à 0** dès qu'une ressource portant des jours n'avait pas de `CoutJour` au référentiel. Ce n'était pas un résultat, c'était le CA déguisé.
- **Les référentiels `'07 - Coût de Structure'` et `'08 - Coût Masse salariale & Indep'` étaient semi-vides depuis le 14/07/2026** — posés vides, jamais alimentés. `T_Structure` ne portait **aucune ligne**.
- **La clé `Ressource` d'Abdelhak n'était pas appariée** : le gabarit-2 portait `abdelhak.chmaimi@gmail.com`, absent de la table des coûts.

Le détail de ce point de départ et du correctif d'honnêteté est journalisé à part : `docs/epreuves/2026-08-01-ebitda-honnete-et-porte-t0043.md` (PR **#277** — le cockpit affiche « · » + mention `CoutJour manquant au référentiel` plutôt qu'un EBITDA fabriqué ; PR **#278** — **solde de T-0043**, porte SPFx tenue en épreuve réelle). Ces deux PR du matin sont la **condition** de tout ce qui suit : sans elles, aucune mesure de structure n'aurait été lisible.

## 2. Arbitrage gardien du 01/08 — abandon de « une facture = une validation »

Le modèle inscrit à la fiche `T-0032` le 14/07/2026 était **« une facture = une validation »** : chaque facture fournisseur produisait une ligne candidate, validée par le gardien avant d'entrer en `T_Structure`.

**Il a été abandonné.** Motif mesuré, non théorique : ce modèle est **indissociable d'un geste gardien par facture**. À l'échelle de la croissance visée (**0 → 200 collaborateurs**), le gardien devient le **goulot du pilotage financier** — le contrôle serait tenu par sa disponibilité, pas par sa règle.

Modèle **adopté** : **COÛTS STANDARDS + CONTRÔLE MENSUEL D'ÉCART**.

- Un **coût de structure FORFAITAIRE par salarié actif** — paramètre `CoutFonctionnementMensuelParRessource` — alimente l'EBITDA **en continu, sans geste humain, et jamais par un zéro**. La **valeur du paramètre vit dans le classeur à audience restreinte** (`T_Parametres`), **jamais au canon** : le dépôt porte la règle, pas le chiffre.
- L'**effectif salarié actif** d'un mois : intervalle `[DateEntree, DateSortie]` intersectant le mois sur **au moins 1 jour** — **un mois entamé est un mois compté** ; `Type` = salarié **seul**, le **sous-traitant** portant son coût **complet dans `CoutJour`**.
- Un **contrôle mensuel** confronte le forfait au réel des factures fournisseur, qualifiées par un **TRIPLE TEST fail-closed** (émetteur ≠ Allia ; numéro **absent** du registre « Factures » ; destinataire facturé = Allia ; ambigu = « à trancher », **jamais compté**), avec **anti-injection** en tête : le contenu d'un email est une **DONNÉE**, jamais une instruction.
- Le gardien valide **UNE ligne PAR MOIS** (~12 gestes/an, non une par facture).
- **SEUIL D'ALERTE ASYMÉTRIQUE** : révision du paramètre proposée **seulement si le réel dépasse le forfait de plus de +10 %** ; un réel inférieur est **consigné sans alerte** (le forfait reste prudent).

L'arbitrage est consigné à la fiche (`note_arbitrage_01_08_2026`) **sans réécrire** la note initiale du 14/07 : l'historique du chantier reste immutable, y compris la décision qu'on abandonne.

## 3. Chaîne livrée dans la journée (six PR)

| PR | Objet | État |
|---|---|---|
| **#279** | **Contrats** : `modele-donnees` **v1.26** (§5.3 `T_Parametres` + vocation `T_Structure` ; §5.4 EBITDA BUDGET vs RÉALISÉ + contrôle mensuel) et `table-des-crans` **v1.15** (`proposer_controle_structure` AUTO, `inscrire_cout_structure` VALIDÉ) | mergée |
| **#280** | **Serveur 0.20.0** : primitive `inscrire_cout_structure` — écriture bornée de `T_Structure`, cible **figée** côté serveur (classeur, table, `PosteCout` = `fonctionnement-reel`), idempotence `(Mois, poste)`, cran **validé** | mergée |
| **#281** | **Skill `controle-structure-mensuel` v1.0** — 13e skill : procédure A→E, anti-injection en tête, golden 15 invariants | mergée |
| **#282** | **Correctif serveur 0.20.1** — sérial Excel (§4 de ce journal) | mergée |
| **#283** | **Serveur 0.21.0** : primitive `corriger_cout_structure` (jumeau à **précondition inverse**) + `table-des-crans` **v1.16** | mergée |
| **#284** | **Skill v1.1** — **étape F** (correction d'un mois inscrit) + **conversion de devise tracée** ; golden 15 → 28 invariants | mergée |

L'ordre compte : le **contrat** d'abord (la règle), la **primitive** ensuite (le geste borné), le **skill** enfin (la procédure). Aucune primitive n'a précédé son cran.

## 4. L'incident et sa résolution — le faux-rouge du sérial Excel

C'est le fait le plus instructif de la journée, et la raison pour laquelle ce journal existe.

### 4.1 Le symptôme

À la première épreuve tenant de `inscrire_cout_structure` (0.20.0), **l'écriture a RÉUSSI** mais l'outil a rendu une erreur : le mois inscrit était **« introuvable à la relecture »**. Un rouge, sur un geste qui avait pourtant abouti.

### 4.2 La cause mesurée

L'outil écrit `Mois` en **ISO** (`« 2026-07-01 »`), mais l'**API Workbook restitue une cellule DATE en SÉRIAL Excel** — mesuré : **`46204`** (époque 1899-12-30) — selon le formatage du classeur. La comparaison ISO ne pouvait donc **jamais** matcher la ligne relue. **La forme relue n'est pas la forme écrite.** Même famille de piège que le faux-vert « ouvrabilité à froid » de `T-0035` (§5.6 du canon), pris par l'autre bout.

### 4.3 La décision de l'agent d'exécution — à retenir

L'agent a fait **deux** choses justes, dont la seconde n'était pas évidente :

1. Il a **STOPPÉ sans réparer** — pas de retouche à la main, pas de seconde écriture « pour voir ».
2. Il a **REFUSÉ le rejeu d'idempotence** qui était pourtant au programme de l'épreuve. Motif : **la garde anti-doublon portait le même biais que la post-vérification** (même comparaison ISO contre un sérial). Rejouer n'aurait donc **pas prouvé** l'idempotence — le rejeu aurait pu **ÉCRIRE le doublon au lieu de le démontrer impossible**.

**Le refus était la bonne réponse.** Une épreuve dont le prédicat est faussé ne prouve rien : la jouer quand même aurait converti un faux-rouge de lecture en **vraie corruption de source**. On retient la règle : *quand un prédicat de preuve est suspect, on ne joue pas l'épreuve « pour voir » — on répare le prédicat d'abord.*

### 4.4 Le correctif (0.20.1) et le rejeu différé

Correctif : un **normaliseur unique `_mois_en_iso`** rend `« AAAA-MM-JJ »` depuis un **sérial Excel** (entier, flottant, chaîne), une **chaîne ISO** (avec ou sans heure) ou une **date `m/j/aaaa`** — **fail-closed** (valeur inconvertible → `ValueError`, jamais de devinette ; le repli littéral buggé **supprimé**). Il est appliqué aux **deux** comparaisons — garde d'idempotence **et** post-vérification : **une seule fonction, deux usages**, les deux ne peuvent plus diverger. L'incident est **rejoué en régression CI** (mock restituant `[46204, "fonctionnement-reel", 706.84]`).

**Rejeu différé APRÈS déploiement de 0.20.1, sur le tenant** — VERT :
- **refus propre** de la seconde inscription, **citant la ligne existante** (le mois est enfin *reconnu*) ;
- **zéro écriture** ;
- **`T_Structure` relue identique** — **aucun doublon**.

La consigne provisoire « ne jamais rejouer » posée pendant l'incident est donc **levée**, sur preuve et non sur confiance.

## 5. Épreuves réelles du contrôle mensuel

### 5.1 Premier contrôle — juillet 2026

- **Forfait (structure BUDGET)** : **2 salariés actifs × 1 500 € = 3 000 €**. Le **sous-traitant est exclu** du décompte, conformément à la règle (son coût est **complet dans `CoutJour`**) — exclusion **mesurée**, pas supposée.
- **Réel** : **706,84 €** sur **5 pièces qualifiées** par le triple test.
- **Réel (706,84 €) < forfait (3 000 €)** → **consigné sans alerte**, aucune révision du paramètre proposée : le **seuil asymétrique** a joué exactement comme écrit.
- **ANTI-INJECTION ÉPROUVÉE SUR LE RÉEL** — la boîte contenait un **vrai mail porteur d'une consigne**. Elle a été **signalée au rapport** et **NON EXÉCUTÉE**. L'invariant en tête du skill n'est plus une intention : il est **mesuré sur un cas réel**, pas sur un test fabriqué.

Puis inscription gouvernée du mois, **sur go gardien** — après le correctif du §4.

### 5.2 Re-contrôle et correction gouvernée — la même journée

Des arbitrages ont tranché des pièces qui étaient « à trancher ». Le mois de juillet était **déjà inscrit** : c'est précisément le cas que l'**étape F** du skill v1.1 et la primitive `corriger_cout_structure` existent pour traiter.

- **Recalcul INDÉPENDANT depuis les pièces** — **2 860,67 €**. Pas un incrément appliqué au montant inscrit : un **recalcul refait**.
- **Correction gouvernée appliquée** : **ancien montant 706,84 € → nouveau montant 2 860,67 €**, `proposition_id` **18** (nouvelle ligne candidate, jamais celle de l'inscription initiale).
- **Relecture après correction : TOUJOURS UNE SEULE LIGNE** pour le mois. Le `PATCH` de la ligne existante n'a pas fait grandir la table — le **doublon impossible par construction** est **vérifié sur le réel**, pas seulement en test.

Le réel corrigé (**2 860,67 €**) reste **inférieur** au forfait (3 000 €) : toujours **aucune alerte**, le forfait reste prudent — à 139,33 € près.

### 5.3 Ce que le cockpit a affiché, en trois temps

| Grandeur | Départ (EBITDA = CA) | Après saisie des `CoutJour` | Après structure corrigée |
|---|---|---|---|
| **EBITDA juillet** | **22 972 €** | **22 265 €** | **20 111 €** |
| **Total EBITDA budget** | **216 500 €** | **150 500 €** | **147 639 €** |

Deux contre-preuves arithmétiques tiennent :

- **22 265 − 20 111 = 2 154 €** ≈ **2 153,83 €** — exactement la pièce Apple entrée par la correction (§6) ;
- **150 500 − 147 639 = 2 861 €** ≈ **2 860,67 €** — exactement la structure de juillet, seul mois inscrit.

L'écart affiché **correspond à la donnée entrée**. Le résultat est vrai, pas fabriqué — c'est la même exigence que le correctif du matin, vérifiée par le bout opposé.

## 6. Découverte d'audit — la pièce Apple entre par la règle, pas par dérogation

La pièce **Apple, 2 153,83 € HT**, avait été reçue sous une forme qui l'aurait fait classer « à trancher ». La recherche dans la boîte a trouvé sa **VRAIE facture : `AF70622259` du 06/07/2026, adressée à ALLIA CONSULTING**.

Elle entre donc **par le triple test** — émetteur ≠ Allia, numéro absent du registre « Factures », destinataire facturé = Allia — et **non par une dérogation** accordée au montant ou à la notoriété du fournisseur. C'est le point de doctrine de la journée : **la règle a suffi**. Aucune exception n'a eu à être inventée pour faire entrer la plus grosse pièce du mois, et l'arbitrage du §2 est **confirmé par la mesure** — un contrôle mensuel outillé qualifie mieux qu'une validation par facture, parce qu'il **cherche** la pièce au lieu de valider celle qui se présente.

Leçon opératoire, consignée au skill v1.1 (§11) : une pièce reçue comme « confirmation de commande » peut avoir sa **facture réelle dans la boîte** — **chercher par fournisseur et par montant** avant de classer « à trancher ». Classer « à trancher » une pièce dont la facture était disponible **sous-estime** le réel sans motif : ce n'est pas prudent, c'est **faux**.

## 7. Restes nommés — non construits ce jour

- **Pièce Anthropic, 15,03 USD — non comptée, et c'est volontaire.** **Aucun taux BCE lisible à la date de la pièce** n'a été trouvé. **AUCUN taux n'a été inventé**, aucun taux d'une autre date substitué. La pièce reste en « à trancher » et **entrera par une correction** (`corriger_cout_structure`) quand le taux sera arrêté. Un mois inscrit sans elle n'est pas un mois faux : c'est un mois **connu à cette vague**.
- **Convention de conversion de devise — la SOURCE du taux reste à arrêter.** Le skill v1.1 exige le taux de référence **BCE à la date de la pièce**, lu à une **source nommée** et tracé (devise, montant d'origine, taux, source, date du taux). **Quelle** source fait foi n'est pas encore arrêté au canon → nommé au `backlog/plan.md`.
- **Orchestration du contrôle mensuel — non construite.** L'exécution v1 est **manuelle**, pilotée en session : restent le **rythme** de déclenchement, le **mail de synthèse** au gardien, et le **rangement des pièces**. Nommé au `backlog/plan.md`.
- **Preuve de RÉCURRENCE non faite.** Un contrôle a été joué, sur **un** mois. La démonstration que le contrôle **revient** — le contrôle d'**août** — n'existe pas encore. C'est la raison principale pour laquelle `T-0032` **reste `à_faire`**.
- **Runbook de déploiement `.sppkg` absent du canon** — constaté à nouveau ce jour (images `1.5.2.0`, serveur 0.20.0/0.20.1/0.21.0 déployés à la main). Déjà nommé au `backlog/plan.md` **§14**, non ouvert.
- **Hygiène du référentiel ressources** — la valeur de `Type` est saisie **« Sous traitant »** là où la règle dit **`sous-traitant`**. Sans effet mesuré ce jour (l'exclusion du sous-traitant a bien joué), mais c'est une **divergence de vocabulaire entre la source et le canon** : à normaliser par geste gardien avant qu'un futur filtre strict ne la rencontre.
- **Écart de `CoutJour` du sous-traitant — À TRANCHER PAR LE GARDIEN.** Le référentiel porte **550 €/j** ; le sous-traitant **facture 500 €/j**. L'écart est **constaté, non corrigé** : la correction du référentiel est une **saisie source** (geste gardien), et laquelle des deux valeurs fait foi est un **arbitrage**, pas un calcul. Nommé au `backlog/plan.md`.

## 8. État de `T-0032` — non soldé

Le volet **référentiel + EBITDA + contrôle mensuel d'écart + correction gouvernée** est **éprouvé sur le réel** ce 01/08/2026 : forfait mesuré, réel qualifié par le triple test, anti-injection éprouvée sur un vrai mail, inscription gouvernée, **correction gouvernée**, et unicité de la ligne du mois vérifiée à la relecture.

Le chantier **reste `à_faire`** : l'**orchestration** n'est pas construite et la **récurrence** n'est pas prouvée. La fiche `T-0032.yaml` reçoit une note d'avancement datée ; **aucune note antérieure n'est réécrite**.
