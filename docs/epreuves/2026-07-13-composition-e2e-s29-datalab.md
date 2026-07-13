# Épreuve de composition bout-en-bout S29 — mission Datalab (Arabelle Solutions)

Journalisation rétroactive (2026-07-13, décision gardien) d'une épreuve advenue en session S29
le 2026-07-10. Précédent de journalisation rétroactive : lot S30-4.0 (PR #191). Fait nouveau ;
aucune requalification d'un soldé, aucune réécriture d'entrée existante.

But : prouver sur le réel que la chaîne « gain d'affaire → mission » se compose de bout en bout
par l'agent-mission v1.0 — de l'opportunité CRM gagnée jusqu'au kick-off — sous les crans, dérivés
en zone, rien hors firme, la porte humaine tenue là où elle doit l'être.

## Chaîne éprouvée sur le réel tenant (2026-07-10)

Opportunité CRM **O-002 « Leader PowerBI »** (projet Datalab, compte Arabelle Solutions CPT-001,
Étape=Gagnée à l'entrée) → **brief de mission** (skill cadrage-mission v1.1, composé par
l'agent-mission v1.0 ; porte « le brief suffit » franchie par le gardien) → **espace de mission
réel** via `creer_espace_mission` (code mission 2, « 2026 - Arabelle Solutions - Datalab »,
collision=fail) → **imputations dérivées IMP-2** écrites en Zone-de-proposition → **kick-off**
(skill kick-off v1.1). Notification d'équipe **PRÉPARÉE mais NON ENVOYÉE** (cran notifié) : aucun
collaborateur staffé sur Datalab à ce moment ; aucun envoi.

Traces zone (lues à la source le 2026-07-13) : BRIEF-2 (item 12, Created 2026-07-10T13:32:02Z),
IMP-2 dérivé (item 13, Created 2026-07-10T13:32:29Z), KICKOFF-2 (item 14, Created
2026-07-10T13:35:09Z).

**Première preuve réelle de bout en bout de `deposer_document_mission`** : support de kick-off
« Kick-off - Datalab.md » (1767 octets, sha256 `bdead50f…`) déposé avec succès dans 01 - Pilotage
(item_id `01OFZO2MQISWAACWHY6BE2AR3QOYXHX3TQ`), intégrité fail-closed vérifiée. L'épreuve Siteflow
avait dû se replier sur l'UI pour un .pptx corrompu en transit ; ici le dépôt par connecteur a payé.

## KPI brief→kick-off

Delta mesuré = **187 s**. Qualification obligatoire : **borne basse machine, non calendaire** —
O-002 était déjà Gagnée à l'entrée, le T0 n'est pas issu d'un geste gardien de bascule réel. La
première donnée gouvernée du KPI brief→kick-off est attendue de la prochaine affaire réelle.

## Promotions zone→sources — gestes gardien du 2026-07-13 (lus à la source)

| Source promue | Fait lu | Modified (source) |
|---|---|---|
| Liste Missions — « Projet Datalab » (item 3) | CodeMission=2 ; DateDebut 2026-07-01 → DateFin 2026-12-31 ; En cours | 2026-07-13T17:32:44Z |
| Liste CRM — O-002 « Leader PowerBI » (item 2) | Étape=Gagnée ; CodeMission=2 | 2026-07-13T17:35:22Z |
| Liste Imputations — IMP-2 (item 2) | « IMP-2 - Abdelhak Chmaimi - Projet Datalab » ; Mission=2 ; Temps « 80 J/H » ; Statut Affecté | 2026-07-13T17:39:25Z |

## Fait gardien du 2026-07-13 : la mission Datalab est réelle et staffée

La fiche Mission a été promue avec les **dates réelles 2026-07-01 → 2026-12-31**, qui prévalent sur
les dates cibles du dérivé BRIEF-2 (2026-09-01 → 2026-12-19). L'imputation IMP-2 a été promue
**nominative** — Abdelhak Chmaimi, 80 j-h, statut Affecté — là où le dérivé la laissait « à staffer »
(grade et affectation nominative renvoyés à la décision humaine).

Ces divergences dérivé→réel sont consignées ici **comme un fait**. Elles ne requalifient pas le
dérivé en zone : les items 12/13/14 restent tels quels, l'écart est la trace normale d'une porte
humaine qui a tranché entre proposition et réel.

## Décision gardien du 2026-07-13

L'épreuve de composition bout-en-bout est **réputée soldée par S29**. Le parcours de reprise S30
(Zone-de-proposition item 15, O-EPREUVE-S30) est **abandonné** ; le nettoyage de l'item 15 est un
geste gardien UI ultérieur, traçable T-0025.

Journalisé comme fait nouveau.
