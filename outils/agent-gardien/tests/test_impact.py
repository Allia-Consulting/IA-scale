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


def test_changed_files_txt_exclu_du_scan(tmp_path):
    root = str(tmp_path)
    _ecrire(root, "contrats/local/comm/isole.md", "# isolé\nAucune référence entrante.\n")
    # Artefact de travail du workflow : liste les fichiers modifiés (chemins canoniques).
    # Il NE doit PAS être compté comme consommateur (faux positif corrigé, T-0020-c m2).
    _ecrire(root, "changed-files.txt", "contrats/local/comm/isole.md\n")
    res = impact.analyze(root, ["contrats/local/comm/isole.md"])
    pf = res["par_fichier"]["contrats/local/comm/isole.md"]
    assert "changed-files.txt" not in pf["consommateurs"]
    assert pf["n_artefacts"] == 0
    assert pf["risque"] == "faible"
    assert res["verdict"] == "pass"


def test_id_chantier_en_prose_resolu_en_consommation(tmp_path):
    root = str(tmp_path)
    _ecrire(root, "backlog/chantiers/T-0029.yaml", "id: T-0029\ndepend_de: []\n")
    # La doctrine (§10) cite le chantier par son id EN PROSE, sans chemin explicite.
    _ecrire(root, "doctrine/doctrine.md",
            "# Doctrine\nÉvolution nommée : le miroir de continuité `T-0029`.\n")
    res = impact.analyze(root, ["backlog/chantiers/T-0029.yaml"])
    pf = res["par_fichier"]["backlog/chantiers/T-0029.yaml"]
    assert "doctrine/doctrine.md" in pf["consommateurs"]
    assert pf["n_artefacts"] >= 1


# ---------------------------------------------------------------------------
# Périmètre délégué (CODEOWNERS) — exclusion du circuit d'auto-approbation.
# Un périmètre délégué relève de la porte humaine de SON délégué
# (organisation.md §4.1) : l'agent-gardien ne doit JAMAIS l'auto-merger.
# ---------------------------------------------------------------------------
# CODEOWNERS de référence : le gardien partout, plus un périmètre délégué.
_CODEOWNERS = (
    "# CODEOWNERS de test\n"
    "*                                 @Alliaconsulting\n"
    "/doctrine/                        @Alliaconsulting\n"
    "/contrats/socle/                  @Alliaconsulting\n"
    "\n"
    "# Périmètre délégué : l'animateur À CÔTÉ du gardien.\n"
    "/contrats/local/communication/    @SarahSK-75 @Alliaconsulting\n"
)


def test_changement_delegue_marque_delegue(tmp_path):
    root = str(tmp_path)
    _ecrire(root, ".github/CODEOWNERS", _CODEOWNERS)
    _ecrire(root, "contrats/local/communication/newsletter.md", "# newsletter\n")

    res = impact.analyze(root, ["contrats/local/communication/newsletter.md"])
    assert res["delegue"] is True

    md = impact.rapport_markdown(res)
    assert any(l.strip() == "DELEGUE: oui" for l in md.splitlines())


def test_changement_docs_non_delegue(tmp_path):
    root = str(tmp_path)
    _ecrire(root, ".github/CODEOWNERS", _CODEOWNERS)
    _ecrire(root, "docs/epreuves/e-2026.md", "# épreuve\n")

    res = impact.analyze(root, ["docs/epreuves/e-2026.md"])
    assert res["delegue"] is False

    md = impact.rapport_markdown(res)
    assert any(l.strip() == "DELEGUE: non" for l in md.splitlines())


def test_regle_etoile_ne_delegue_pas_tout(tmp_path):
    root = str(tmp_path)
    # La règle "*" est possédée par un NON-gardien : elle ne doit PAS déléguer
    # tout le dépôt (le pattern "*" est exclu du calcul de délégation).
    codeowners = (
        "*                                 @QuelquUnDAutre\n"
        "/contrats/local/communication/    @SarahSK-75 @Alliaconsulting\n"
    )
    _ecrire(root, ".github/CODEOWNERS", codeowners)
    _ecrire(root, "docs/epreuves/e-2026.md", "# épreuve\n")

    res = impact.analyze(root, ["docs/epreuves/e-2026.md"])
    assert res["delegue"] is False


def test_rapport_delegue_juste_avant_risque_verdict(tmp_path):
    root = str(tmp_path)
    _ecrire(root, ".github/CODEOWNERS", _CODEOWNERS)
    _ecrire(root, "contrats/local/communication/newsletter.md", "# newsletter\n")
    res = impact.analyze(root, ["contrats/local/communication/newsletter.md"])
    md = impact.rapport_markdown(res)
    lignes = md.rstrip().splitlines()
    # DELEGUE s'insère immédiatement AVANT les deux lignes finales contractuelles.
    assert lignes[-3].strip() == "DELEGUE: oui"
    assert lignes[-2].strip().startswith("RISQUE:")
    assert lignes[-1].strip().startswith("VERDICT:")
