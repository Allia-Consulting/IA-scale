# Annexe 2 — Analyse d'impact (AIPD, art. 35) — écoute Teams/Claude — Allia Consulting

> **Version** : 1.1 — *promu*. **Statut** : contrat socle (annexe normative de `contrats/socle/rgpd-ecoute-teams.md` §7) — fait foi.
> **Changelog** : v1.1 — alignement en-tête candidat → promu, 16 juin 2026 : le gardien-DPO acte le fond de cette annexe (risque résiduel maîtrisé et non élevé au sens de l'art. 36 — pas de consultation préalable CNIL ; mesures du §3 ; revue bimestrielle). Contenu de fond byte-inchangé hors en-tête et note de clôture. v1.0 — candidat, 12 juin 2026.
> **Domicile** : `contrats/socle/annexes/rgpd-ecoute-teams--annexe-2-aipd.md`. **Autorité de promotion** : gardien du temple.
> **Adossé à** : `contrats/socle/rgpd-ecoute-teams.md` (§7 — formalités, art. 35), `contrats/socle/annexes/rgpd-ecoute-teams--annexe-1-mise-en-balance.md` (nécessité et proportionnalité), `contrats/socle/identites-et-secrets.md` (§2 — identités appelantes), `contrats/socle/memoire-organisation.md` (mécanisme).
> **Nature** : consigne les **arbitrages du gardien-DPO** (12 juin 2026) ; **pas un avis juridique**.

## 1. Description systématique du traitement

- **Mécanisme** : un **batch hebdomadaire Cowork local**, exécuté **sur le poste du gardien**, sous l'**identité Entra du gardien** — **zéro secret** (`identites-et-secrets.md` §2, cas 3).
- **Sources écoutées** : **Teams** — canaux d'équipe et conversations de mission, **HORS conversations privées 1-à-1** ; **Claude** — conversations de l'**espace Allia Consulting uniquement**.
- **Production** : **UNE synthèse candidate** par semaine, écrite en **Zone-de-proposition** (champ d'origine **« mémoire hebdo »**, `modele-donnees.md` §2 bis/§3).
- **Validation** : **ligne à ligne, le vendredi**, par le gardien (non-validé = oublié).
- **Personnes concernées** : les **collaborateurs** de la firme et, incidemment, les **clients mentionnés**.
- **Durées** : verbatim brut **supprimé à J+7 calendaires après la validation du vendredi** (annexe 1 §5) ; synthèse **non validée supprimée** ; **seule la ligne explicitement promue subsiste**.

## 2. Nécessité et proportionnalité

**RENVOI** : la nécessité et la proportionnalité sont établies par l'**annexe 1** (`rgpd-ecoute-teams--annexe-1-mise-en-balance.md`) — non dupliquées ici. Rappel des choix **minimisants** : **batch hebdomadaire** plutôt qu'écoute continue ; **synthèse** plutôt que verbatim ; **non-validé = oublié** (pas d'accumulation silencieuse).

## 3. Risques pour les personnes et mesures

| Risque | Mesures |
|---|---|
| **(a) Détournement de finalité** vers la surveillance ou l'évaluation individuelle | **Interdits en dur** (contrat parent §1) ; validation par le **seul gardien** ; **traçabilité** des promotions (historique Git / promotion tracée) |
| **(b) Accès illégitime** à la synthèse ou au brut | **Zéro secret** applicatif ; **identité Entra** ; exécution **sur le poste du gardien** ; substrat **M365** (droits du tenant) |
| **(c) Captation de contenus personnels** | **Exclusions structurelles** : 1-à-1 Teams exclus ; conversations Claude **hors espace Allia Consulting** exclues (annexe 1 §3) |
| **(d) Conservation excessive** | Brut supprimé à **J+7** après la validation du vendredi ; **non-validé = oublié** |
| **(e) Ré-identification à la sortie externe** | **Porte d'anonymisation** (`anonymisation.md` §1), **orthogonale** au présent cadre |

**Consultation des personnes (art. 35.9)** : **impossible en firme solo** (le fondateur est seul). L'avis des personnes concernées sera recueilli **à l'arrivée du premier collaborateur, AVANT l'activation de son écoute**, lors de l'information préalable (`T-0007`).

## 4. Conclusion du gardien-DPO (12 juin 2026)

Le **risque résiduel est MAÎTRISÉ et NON ÉLEVÉ** au sens de l'**art. 36** : **pas de consultation préalable de la CNIL**. Cette conclusion est **conditionnée au maintien effectif des mesures du §3** et **révisée au même rythme que l'annexe 1** : **bimestriel dès le premier collaborateur écouté**, et à chaque évolution du périmètre d'écoute.

---

*Annexe normative promue du cadre RGPD de l'écoute Teams/Claude (§7). Elle consigne l'analyse d'impact et la conclusion du gardien-DPO du 12 juin 2026 ; elle fait foi et évolue par la boucle de promotion.*
