# Harnais d'evals des skills — contrat du répertoire

> **Chantier** : T-0020-a (plan §7, T-2.1) — soldé le 03/07/2026 (PR #153, épreuve rouge PR #154).
> **Rôle** : non-régression des prompts/skills en CI sur chaque PR (`.github/workflows/evals.yml`, check « Harnais skills » — REQUIS par le ruleset `main-protection`).

## Ce que le harnais vérifie (v0 déterministe)

1. **Couverture bidirectionnelle** : chaque `skills/<id>/SKILL.md` a son `evals/skills/<id>/golden.yaml`, et réciproquement. Un skill sans golden set = rouge ; un golden orphelin = rouge. Tout nouveau skill paie sa dette d'eval à la naissance.
2. **Invariants d'en-tête universels** : id conforme au répertoire, champ Version, statut `*candidat*` ou `*promu*` (les deux régimes passent — la boucle de promotion n'est pas bloquée), Domicile canonique.
3. **Cas `invariant`** : ancres sémantiques VERBATIM (`contient`) et motifs (`regex`) contre le corps du SKILL.md.

## Schéma d'un golden set

~~~yaml
skill: <id>            # identique au nom du répertoire
version_harnais: 1
cas:
  - id: ancre-01       # unique dans le fichier
    type: invariant    # ou scenario (réservé, ignoré en v0)
    description: "pourquoi cette ancre est un invariant du skill"
    contient:
      - "ancre verbatim, copiée à l'octet près depuis le SKILL.md"
~~~

## Règle de co-évolution

Une évolution légitime d'un skill qui déplace une ancre DOIT mettre à jour son golden.yaml **dans la même PR** — c'est le point : rendre le changement conscient, jamais silencieux.

## Exécution locale

~~~
python3 evals/harnais.py
~~~

Sortie : rapport par skill, code retour 1 au premier échec.

## Extension prévue (non implémentée en v0)

Type `scenario` : exécution du skill sur des entrées golden avec scoring LLM (plan §7 T-2.1 complet). Le schéma le réserve ; l'implémentation viendra sans casser les golden sets existants.
