"""Mécanisme de purge gouvernée des données de recrutement — Allia Consulting.

Skill : skills/purge-recrutement/SKILL.md (CANDIDAT — non promu à ce jour).
Chantier : backlog/chantiers/T-0013.yaml (T-0013-d).
Contrat de référence : contrats/socle/rgpd-recrutement-candidats.md §5 (v1.4).
Exception gouvernée : contrats/socle/table-des-crans.yaml v1.7.

ARTEFACT CANDIDAT — NON EXÉCUTABLE EN PRODUCTION tant que les prérequis §6 du skill
ne sont pas TOUS soldés. État au jour de l'écriture :
  - [fait]   colonne OppositionVivier sur liste Candidats (runbook 19 juin 2026)
  - [fait]   identité id-allia-purge-recrutement créée + Sites.Selected write (runbook 19 juin 2026)
  - [reste]  PROMOTION du skill purge-recrutement (geste du gardien) — PRÉREQUIS À LA MISE EN SERVICE
  - [fait]   journalisation active sur liste Candidats (T-0003)

Ce script applique la règle de rétention DÉJÀ PROMUE au canon :
  - Cible : fiches « Candidats » dont Etape = Refusée ET Créé le < aujourd'hui − 730 jours
  - Sauf opposition active (OppositionVivier = true)
  - Journal en Zone-de-proposition AVANT toute suppression
  - Suppression via l'identité managée dédiée id-allia-purge-recrutement (clientId env PURGE_CLIENT_ID)
  - Rapport final en Zone-de-proposition

Identités :
  - LECTURE liste Candidats + ÉCRITURE Zone-de-proposition :
      identité managée id-allia-mcp-graph (clientId env MCP_CLIENT_ID)
  - SUPPRESSION liste Candidats + Candidats-Synthèses :
      identité managée id-allia-purge-recrutement (clientId env PURGE_CLIENT_ID)

Variables d'environnement requises (aucun secret — clientIds publics) :
  GRAPH_SITE_ID, GRAPH_CANDIDATS_LIST_ID, GRAPH_SYNTHESES_LIST_ID,
  GRAPH_PROPOSITION_LIST_ID, MCP_CLIENT_ID, PURGE_CLIENT_ID, AZURE_ENV (local|prod, défaut prod)
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Any

import httpx
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"
DUREE_RETENTION_JOURS = 730  # 2 ans — durée promue (rgpd §5 v1.4) ; ne pas modifier ici


class ConfigManquante(RuntimeError):
    """Levée quand une variable d'environnement requise est absente."""


def _config() -> dict[str, str]:
    cles = {
        "site_id": "GRAPH_SITE_ID",
        "candidats_list_id": "GRAPH_CANDIDATS_LIST_ID",
        "syntheses_list_id": "GRAPH_SYNTHESES_LIST_ID",
        "proposition_list_id": "GRAPH_PROPOSITION_LIST_ID",
        "mcp_client_id": "MCP_CLIENT_ID",
        "purge_client_id": "PURGE_CLIENT_ID",
    }
    valeurs = {k: os.environ.get(v, "") for k, v in cles.items()}
    manquantes = [cles[k] for k, v in valeurs.items() if not v]
    if manquantes:
        raise ConfigManquante("Variables d'environnement manquantes : " + ", ".join(manquantes))
    return valeurs


def _credential(client_id: str):
    env = (os.environ.get("AZURE_ENV", "") or "prod").strip().lower()
    if env == "local":
        return DefaultAzureCredential()
    return ManagedIdentityCredential(client_id=client_id)


def _entetes(client_id: str) -> dict[str, str]:
    token = _credential(client_id).get_token(GRAPH_SCOPE).token
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def lire_candidats_refuses(cfg: dict[str, str]) -> list[dict[str, Any]]:
    """Lit toutes les fiches Candidats dont Etape = Refusée (lecture seule)."""
    url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{cfg['candidats_list_id']}/items"
    params = {"$expand": "fields", "$filter": "fields/Etape eq 'Refusée'", "$top": "500"}
    items: list[dict[str, Any]] = []
    with httpx.Client(timeout=30) as client:
        while url:
            r = client.get(url, headers=_entetes(cfg["mcp_client_id"]), params=params)
            r.raise_for_status()
            corps = r.json()
            items.extend(corps.get("value", []))
            url = corps.get("@odata.nextLink")
            params = {}
    return items


def journaliser(cfg: dict[str, str], id_candidat: str, date_inscription: str, motif: str) -> None:
    """Écrit une entrée de traçabilité en Zone-de-proposition AVANT toute suppression."""
    aujourd_hui = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fields = {
        "Title": f"PURGE-{id_candidat}-{aujourd_hui}",
        "Origine": "purge-recrutement",
        "Contenu": (
            f"Purge gouvernee — fiche candidat {id_candidat}\n"
            f"Date d'inscription : {date_inscription}\n"
            f"Motif : {motif}\n"
            f"Date d'execution : {aujourd_hui}\n"
            f"Regle : Etape=Refusee, Cree le > 2 ans (730 jours), pas d'opposition active."
        ),
    }
    url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{cfg['proposition_list_id']}/items"
    with httpx.Client(timeout=30) as client:
        r = client.post(url, headers=_entetes(cfg["mcp_client_id"]), json={"fields": fields})
        r.raise_for_status()


def supprimer_syntheses(cfg: dict[str, str], id_candidat_item: str) -> int:
    """Supprime les synthèses rattachées à un candidat (lookup Candidat → Candidats-Synthèses)."""
    url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{cfg['syntheses_list_id']}/items"
    params = {"$expand": "fields", "$filter": f"fields/CandidatLookupId eq '{id_candidat_item}'", "$top": "50"}
    supprimees = 0
    with httpx.Client(timeout=30) as client:
        r = client.get(url, headers=_entetes(cfg["purge_client_id"]), params=params)
        r.raise_for_status()
        for s in r.json().get("value", []):
            del_url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{cfg['syntheses_list_id']}/items/{s['id']}"
            rd = client.delete(del_url, headers=_entetes(cfg["purge_client_id"]))
            rd.raise_for_status()
            supprimees += 1
    return supprimees


def supprimer_candidat(cfg: dict[str, str], item_id: str) -> None:
    """Supprime définitivement une fiche candidat."""
    url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{cfg['candidats_list_id']}/items/{item_id}"
    with httpx.Client(timeout=30) as client:
        r = client.delete(url, headers=_entetes(cfg["purge_client_id"]))
        r.raise_for_status()


def rapport_final(cfg: dict[str, str], purges: list[dict], total_eligible: int) -> None:
    """Écrit le rapport de fin d'exécution en Zone-de-proposition."""
    aujourd_hui = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ids_purges = ", ".join(p["id_candidat"] for p in purges) if purges else "aucune"
    fields = {
        "Title": f"PURGE-RAPPORT-{aujourd_hui}",
        "Origine": "purge-recrutement-rapport",
        "Contenu": (
            f"Rapport de purge gouvernee — {aujourd_hui}\n"
            f"Fiches eligibles detectees : {total_eligible}\n"
            f"Fiches purgees : {len(purges)}\n"
            f"Identifiants purges : {ids_purges}\n"
            f"Syntheses supprimees : {sum(p['syntheses'] for p in purges)}\n"
            f"Regle appliquee : Etape=Refusee, Cree le > 730 jours, OppositionVivier != true.\n"
            f"Identite de suppression : id-allia-purge-recrutement."
        ),
    }
    url = f"{GRAPH_BASE}/sites/{cfg['site_id']}/lists/{cfg['proposition_list_id']}/items"
    with httpx.Client(timeout=30) as client:
        r = client.post(url, headers=_entetes(cfg["mcp_client_id"]), json={"fields": fields})
        r.raise_for_status()


def purger() -> None:
    """Procédure de purge gouvernée — exécute les étapes §3 du skill."""
    cfg = _config()
    seuil = datetime.now(timezone.utc) - timedelta(days=DUREE_RETENTION_JOURS)
    print(f"[purge] Demarrage — seuil : {seuil.strftime('%Y-%m-%d')} (J-{DUREE_RETENTION_JOURS})")

    refuses = lire_candidats_refuses(cfg)
    print(f"[purge] Fiches Refusees lues : {len(refuses)}")

    eligibles = []
    for item in refuses:
        fields = item.get("fields", {})
        cree_le_str = item.get("createdDateTime") or fields.get("Created", "")
        if not cree_le_str:
            continue
        try:
            cree_le = datetime.fromisoformat(cree_le_str.replace("Z", "+00:00"))
        except ValueError:
            print(f"[purge] AVERTISSEMENT : date illisible pour item {item.get('id')} — ignore")
            continue
        if cree_le >= seuil:
            continue
        if fields.get("OppositionVivier") is True:
            print(f"[purge] Opposition active — fiche {fields.get('Title', item['id'])} exclue")
            continue
        eligibles.append(item)

    print(f"[purge] Fiches eligibles a la purge : {len(eligibles)}")

    if not eligibles:
        rapport_final(cfg, [], 0)
        print("[purge] Aucune fiche eligible. Rapport ecrit. Fin.")
        return

    purges = []
    for item in eligibles:
        fields = item.get("fields", {})
        id_candidat = fields.get("Title", item["id"])
        date_inscription = item.get("createdDateTime", "inconnue")
        item_id = item["id"]

        try:
            journaliser(cfg, id_candidat, date_inscription, "Duree de retention echue (2 ans)")
        except Exception as e:
            print(f"[purge] ERREUR journal pour {id_candidat} : {e} — suppression annulee pour cette fiche")
            continue

        try:
            nb_syntheses = supprimer_syntheses(cfg, item_id)
        except Exception as e:
            print(f"[purge] ERREUR suppression syntheses pour {id_candidat} : {e}")
            nb_syntheses = 0

        try:
            supprimer_candidat(cfg, item_id)
            purges.append({"id_candidat": id_candidat, "syntheses": nb_syntheses})
            print(f"[purge] Purge : {id_candidat} ({nb_syntheses} synthese(s))")
        except Exception as e:
            print(f"[purge] ERREUR suppression fiche {id_candidat} : {e}")

    rapport_final(cfg, purges, len(eligibles))
    print(f"[purge] Termine — {len(purges)}/{len(eligibles)} fiches purgees. Rapport ecrit.")


if __name__ == "__main__":
    try:
        purger()
    except ConfigManquante as e:
        print(f"[purge] CONFIGURATION MANQUANTE : {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[purge] ERREUR INATTENDUE : {e}", file=sys.stderr)
        sys.exit(2)
