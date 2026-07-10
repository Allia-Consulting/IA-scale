"""Tests du calcul d'impact fin de l'agent-gardien (T-0020-c marche 1).

TDD : ces cas décrivent le comportement attendu du parser de dépendances et du
moteur de risque AVANT l'implémentation. Chaque test construit un mini-dépôt
temporaire (fixtures) et appelle `impact.analyze(repo_root, changed)`.

Couverture minimale demandée (plan §7 T-2.2) :
  (a) contrat socle très consommé      -> rayon=large, RISQUE=large, consommateurs>0
  (b) fichier local isolé (0 conso)    -> rayon=local, RISQUE=faible
  (c) skills:[id] résolu en skills/id/SKILL.md, compté comme consommation réelle
  (d) référence cassée (chemin supprimé par le diff) -> flag casse_structurelle + VERDICT fail
  (e) transitivité A -> B -> C : modifier C remonte A et B
"""

import os
import sys

import pytest

# impact.py vit dans le dossier parent de tests/.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import impact  # noqa: E402


def _ecrire(root, chemin, contenu):
    """Écrit un fichier fixture (crée les dossiers)."""
    p = os.path.join(root, chemin)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(contenu)
    return chemin


# ---------------------------------------------------------------------------
# (a) contrat socle très consommé -> rayon=large, RISQUE=large, consommateurs>0
# ---------------------------------------------------------------------------
def test_socle_tres_consomme_rayon_et_risque_large(tmp_path):
    root = str(tmp_path)
    _ecrire(root, "contrats/socle/table-des-crans.yaml",
            'domicile: "contrats/socle/table-des-crans.yaml"\nstatut: "socle"\n')
    # Cinq consommateurs déclarés de formes variées (backticks, (§x), leading slash).
    for i in range(5):
        _ecrire(root, f"skills/s{i}/SKILL.md",
                f"# skill {i}\n> **Adossé à** : `contrats/socle/table-des-crans.yaml` (§6)\n")

    res = impact.analyze(root, ["contrats/socle/table-des-crans.yaml"])
    pf = res["par_fichier"]["contrats/socle/table-des-crans.yaml"]

    assert pf["n_artefacts"] > 0
    assert len(pf["consommateurs"]) >= 5
    assert pf["rayon"] == "large"
    assert pf["risque"] == "large"
    assert res["risque"] == "large"
    assert res["verdict"] == "pass"  # pas de casse structurelle


# ---------------------------------------------------------------------------
# (b) fichier local isolé (0 consommateur) -> rayon=local, RISQUE=faible
# ---------------------------------------------------------------------------
def test_local_isole_rayon_local_risque_faible(tmp_path):
    root = str(tmp_path)
    _ecrire(root, "contrats/local/comm/isole.md", "# isolé\nAucune référence entrante.\n")
    # Un autre fichier sans lien, pour peupler l'index.
    _ecrire(root, "backlog/chantiers/T-9999.yaml", "id: T-9999\ndepend_de: []\n")

    res = impact.analyze(root, ["contrats/local/comm/isole.md"])
    pf = res["par_fichier"]["contrats/local/comm/isole.md"]

    assert pf["n_artefacts"] == 0
    assert pf["consommateurs"] == []
    assert pf["rayon"] == "local"
    assert pf["risque"] == "faible"
    assert res["risque"] == "faible"
    assert res["verdict"] == "pass"


# ---------------------------------------------------------------------------
# (c) skills:[id] -> skills/id/SKILL.md compté comme consommation réelle
# ---------------------------------------------------------------------------
def test_skill_id_resolu_en_consommation(tmp_path):
    root = str(tmp_path)
    _ecrire(root, "skills/cadrage-mission/SKILL.md", "# cadrage\n")
    _ecrire(root, "agents/agent-mission/profil.yaml",
            'id: agent-mission\n'
            'domicile: "agents/agent-mission/profil.yaml"\n'
            'skills:\n'
            '  - cadrage-mission  # skill promu (T-0021)\n')

    res = impact.analyze(root, ["skills/cadrage-mission/SKILL.md"])
    pf = res["par_fichier"]["skills/cadrage-mission/SKILL.md"]

    assert "agents/agent-mission/profil.yaml" in pf["consommateurs"]
    assert pf["n_artefacts"] >= 1


# ---------------------------------------------------------------------------
# (d) référence cassée : un consommateur pointe un chemin supprimé par le diff
# ---------------------------------------------------------------------------
def test_reference_cassee_flag_casse_structurelle(tmp_path):
    root = str(tmp_path)
    # Consommateur qui pointe un chemin socle...
    _ecrire(root, "skills/s0/SKILL.md",
            "# s0\n> **Adossé à** : `contrats/socle/supprime.md`\n")
    # ...mais contrats/socle/supprime.md N'EXISTE PAS sur le disque (supprimé par le diff).
    # On le passe quand même comme fichier modifié (une suppression est un changement).
    res = impact.analyze(root, ["contrats/socle/supprime.md"])

    assert res["casse_structurelle"] is True
    assert res["verdict"] == "fail"
    pf = res["par_fichier"]["contrats/socle/supprime.md"]
    assert "skills/s0/SKILL.md" in pf["consommateurs"]


# ---------------------------------------------------------------------------
# (e) transitivité : A consomme B consomme C ; modifier C remonte A et B
# ---------------------------------------------------------------------------
def test_transitivite_remonte_toute_la_chaine(tmp_path):
    root = str(tmp_path)
    _ecrire(root, "contrats/socle/c.md", "# C — feuille\n")
    _ecrire(root, "contrats/socle/b.md", "# B\n> **Adossé à** : `contrats/socle/c.md`\n")
    _ecrire(root, "contrats/local/dom/a.md", "# A\n> **Adossé à** : `contrats/socle/b.md`\n")

    res = impact.analyze(root, ["contrats/socle/c.md"])
    consommateurs = res["par_fichier"]["contrats/socle/c.md"]["consommateurs"]

    assert "contrats/socle/b.md" in consommateurs      # direct
    assert "contrats/local/dom/a.md" in consommateurs  # transitif
    assert res["par_fichier"]["contrats/socle/c.md"]["n_artefacts"] == 2


# ---------------------------------------------------------------------------
# Sortie CLI : le rapport markdown se termine par les deux lignes exactes.
# ---------------------------------------------------------------------------
def test_rapport_markdown_termine_par_risque_puis_verdict(tmp_path):
    root = str(tmp_path)
    _ecrire(root, "contrats/local/comm/isole.md", "# isolé\n")
    res = impact.analyze(root, ["contrats/local/comm/isole.md"])
    md = impact.rapport_markdown(res)
    lignes = md.rstrip().splitlines()
    assert lignes[-2].strip() == "RISQUE: faible"
    assert lignes[-1].strip() == "VERDICT: pass"
