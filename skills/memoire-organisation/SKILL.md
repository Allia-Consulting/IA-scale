# Mémoire d'organisation — Skill

> **id** : `memoire-organisation`
> **Version** : 1.1 — *promu*. **Nature** : skill.
> **Changelog** : v1.1 — promu via procédure allégée, 30 juin 2026 : **domicile d'exécution = session claude.ai de l'espace Allia** (rendez-vous hebdomadaire le vendredi), alignement sur `memoire-organisation.md` v1.4. La mention « batch Cowork jeudi→vendredi » de v1.0 est **corrigée** : l'écoute des conversations Claude n'est accessible qu'en session claude.ai (Cowork et Claude Code n'exposent pas l'historique de chat). Corps de procédure inchangé (déjà fondé sur la recherche d'historique de chat). v1.0 — candidat, 30 juin 2026 : mécanisme initial (T-0005) — synthèse hebdomadaire candidate de la mémoire d'organisation (batch Cowork jeudi→vendredi, écrite en Zone-de-proposition, validée ligne à ligne le vendredi). Périmètre d'écoute borné au gardien (annexe 1 §3).
> **Domicile** : `skills/memoire-organisation/SKILL.md`. **Autorité de promotion** : gardien (procédure allégée).
> **Adossé à** : `contrats/socle/memoire-organisation.md`, `contrats/socle/rgpd-ecoute-teams.md` (+ annexes 1/2/3), `contrats/socle/modele-donnees.md` (§2 bis/§3), `contrats/socle/anonymisation.md` (§1), `doctrine/doctrine.md` (§2, §6, §7, §9), `outils/mcp-graph/server.py` (`create_list_item`), `CLAUDE.md`.
> **Rattachement** : capacité *Connaissance, contenu & IP / Mémoire d'organisation* ; chantier `backlog/chantiers/T-0005.yaml`.

## Ce que fait ce skill

Une fois par semaine (rendez-vous du vendredi), il lit les apprentissages et décisions
**collectifs** de la semaine et en produit **UNE** synthèse **candidate**, écrite en zone
de proposition pour validation ligne à ligne par le gardien. C'est le mécanisme « l'intelligence
se compose entre missions » (doctrine §9). L'écriture continue est abandonnée : un seul rendez-vous,
une seule synthèse, examinée d'un bloc.

## Contrats qui font foi (résous-les, ne les recopie pas)

- `contrats/socle/memoire-organisation.md` — le mécanisme (cadence, domicile, validation, nature).
- `contrats/socle/rgpd-ecoute-teams.md` + annexes 1 (mise en balance, périmètre §3, rétention §5),
  2 (AIPD), 3 (gabarit d'information préalable) — le cadre RGPD de l'écoute.
- `contrats/socle/modele-donnees.md` §2 bis/§3 — la liste « Zone-de-proposition » et ses colonnes.
- `contrats/socle/anonymisation.md` §1 — la porte de sortie externe (ne joue PAS pour l'usage interne).
- `doctrine/doctrine.md` §2 (le dérivé n'est jamais le saisi), §6/§7 (crans, promotion), §9 (l'avantage qui compose).

## Périmètre d'écoute — NON négociable (annexe 1 §3)

- **Claude** : uniquement les conversations de l'**espace Allia Consulting** de **l'utilisateur courant**
  (le gardien). Les conversations personnelles hors espace firme sont exclues. Tant qu'un autre
  collaborateur n'a pas reçu l'**information préalable** (annexe 3, via l'onboarding T-0007), il
  **n'est pas écouté** — défaut : gardien seul.
- **Teams** : uniquement les **canaux d'équipe** et les **conversations de mission**. Les
  **conversations privées 1-à-1 sont EXCLUES** — filtre-les explicitement.
- **Finalité (cadre §1)** : apprentissages et décisions **COLLECTIFS** uniquement.
  **INTERDIT EN DUR** : toute surveillance, évaluation ou mesure de performance individuelle ;
  tout profilage. Un usage hors finalité est une violation du contrat, pas une maladresse.

## Procédure

1. **Borne temporelle** : la semaine écoulée (du vendredi précédent à aujourd'hui inclus).
2. **Collecte Claude** : recherche l'historique de chat de l'espace Allia (utilisateur courant) sur la
   semaine. Ne sors pas de l'espace firme.
3. **Collecte Teams** : `chat_message_search` borné à la semaine, **puis écarte tout 1-à-1**
   (ne garde que canaux d'équipe et conversations de mission) ; utilise `read_resource`
   (`teams:///teams/{teamId}/channels/{channelId}/messages/{messageId}`) pour le détail si besoin.
   Si rien d'éligible n'existe encore au tenant, c'est normal (firme jeune) — n'invente rien.
4. **Synthèse** : produis **UNE** synthèse structurée en **lignes validables**. Chaque ligne est un
   apprentissage ou une décision **collectif**, formulé de façon **auto-portante**, rattaché à un sujet
   ou une mission si pertinent. La synthèse est **interne et nominative** (cadre §3) : tu peux nommer
   personnes, missions, clients comme la matière interne le fait. **Aucune appréciation individuelle.**
   Si une semaine n'a produit aucun apprentissage collectif, écris une synthèse à zéro ligne plutôt que
   de remplir artificiellement.
5. **Écriture (cran auto)** : appelle `create_list_item` du connecteur MCP `allia-graph-proposition`.
   La cible (« Zone-de-proposition ») est **figée côté serveur** — ne passe **aucun** identifiant de liste.

   ~~~
   create_list_item(fields = {
     "Title":   "MEM-{ISO_YEAR}-S{ISO_WEEK}",     # ex. MEM-2026-S27
     "Origine": "mémoire hebdo",
     "Contenu": "<corps multiligne : une ligne validable par puce>"
   })
   ~~~

6. **Vérifie le réel** : après l'écriture, relis (`list_items` sur la zone de proposition) et confirme
   qu'un élément `Origine = « mémoire hebdo »` daté de cette semaine **existe réellement**. Une réponse
   « créé » n'est pas une preuve tant que la relecture ne l'a pas confirmé.

## Rétention (cadre §4 ; annexe 1 §5)

- **Ne persiste JAMAIS le verbatim brut.** Les conversations restent à leur source ; ce que tu lis en
  session est éphémère et ne doit être écrit nulle part. Seule la **synthèse candidate** est écrite.
- La synthèse candidate **non validée** est **oubliée/supprimée** après la décision du vendredi.
- Le verbatim brut, s'il devait subsister, est supprimé **J+7 calendaires après la validation du vendredi**.

## Validation du vendredi — geste du GARDIEN, pas de l'agent

- Le gardien valide **ligne à ligne**. Les lignes retenues sont **promues** (acte tracé du gardien) ;
  le **non-validé est oublié**.
- L'agent **ne promeut jamais** et **n'écrit jamais** une ligne de mémoire comme une source.

## Garde-fous

- L'entrée du MCP exige `scp=access_as_user` : la tâche tourne dans la session du **gardien**.
- Périmètre élargi à un collaborateur **non informé** → ne l'écoute pas.
- Aucune sortie hors firme ici : la porte d'anonymisation (`anonymisation.md` §1) ne joue pas pour
  cette synthèse interne. Elle ne s'armerait qu'à une communication grand public d'un fragment.
