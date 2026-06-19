# purge-recrutement — mécanisme de purge gouvernée (CANDIDAT)

Skill de référence : `skills/purge-recrutement/SKILL.md` — **CANDIDAT (non promu)**.
Chantier : `backlog/chantiers/T-0013.yaml` (T-0013-d).

> **Artefact candidat — non exécutable en production** tant que les prérequis §6 du skill
> ne sont pas tous soldés. En particulier : **la promotion du skill** (geste du gardien)
> reste à faire. Les runbooks « colonne OppositionVivier » et « identité dédiée » sont posés.

## Objet

Script autonome appliquant la règle de rétention promue
(`contrats/socle/rgpd-recrutement-candidats.md` §5, v1.4) : purge les fiches candidat
Refusées dont la date d'inscription dépasse 2 ans, sauf opposition active.

## Variables d'environnement

~~~
GRAPH_SITE_ID             id Graph du site AlliaConsuling
GRAPH_CANDIDATS_LIST_ID   GUID liste Candidats (4d1ae938-fc3c-427b-8e4e-5380f88daa66)
GRAPH_SYNTHESES_LIST_ID   GUID liste Candidats-Synthèses (e33994a5-170f-484e-829b-672a35ac7aee)
GRAPH_PROPOSITION_LIST_ID GUID liste Zone-de-proposition (2590d442-6e7d-4802-b271-451212ea10d4)
MCP_CLIENT_ID             clientId id-allia-mcp-graph (lecture + journal) : f2a3c40a-a447-4295-90da-76d6b0898d61
PURGE_CLIENT_ID           clientId id-allia-purge-recrutement (suppression) : d47d2fa5-8684-4ee8-8d94-1053623bbd7d
AZURE_ENV                 local | prod (défaut prod)
~~~

Aucun secret. Les clientIds sont des identifiants publics — ils ne sont pas inscrits au
canon socle (`identites-et-secrets.md` ne registre que les dettes de secrets, pas les
identités managées, qui sont « zéro secret » par construction).

## Exécution (après promotion du skill uniquement)

~~~bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export GRAPH_SITE_ID="..."   # + autres variables
python purge.py
~~~

## Garde-fous

- Journal en Zone-de-proposition avant toute suppression (si le journal échoue, pas de suppression).
- Opposition active (OppositionVivier = true) exclut la fiche sans exception.
- Suppression sous identité dédiée `id-allia-purge-recrutement` uniquement.
- Rapport final systématique, même si 0 fiche éligible.

## Identité dédiée (runbook 19 juin 2026)

`id-allia-purge-recrutement` — identité managée user-assigned, groupe de ressources
`rg-allia-consulting`, région `francecentral`, clientId `d47d2fa5-8684-4ee8-8d94-1053623bbd7d`.
Octrois : `Sites.Selected` (app role) + `write` sur le site AlliaConsuling.
