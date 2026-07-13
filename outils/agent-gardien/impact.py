#!/usr/bin/env python3
"""Calcul d'impact fin de l'agent-gardien — T-0020-c marche 1 (plan §7 T-2.2).

Remplace le « grep fruste » de l'agent-gardien CI v0 par un calcul DÉTERMINISTE :
qui consomme réellement un fichier modifié (dépendances déclarées + citations
canoniques), le rayon d'impact, et le RISQUE (règles doctrine §3 / §6). Il ne
juge PAS la casse sémantique d'un contrat (ça reste au LLM dans le workflow) ;
il calcule la structure, et signale une casse STRUCTURELLE (référence pendante).

Zéro dépendance hors stdlib + PyYAML. Aucune écriture : lecture seule du dépôt.

CLI :
    python impact.py --changed <path...>          # rapport markdown
    python impact.py --changed <path...> --json    # rapport JSON
    python impact.py                                # lit changed-files.txt

Le rapport markdown se termine TOUJOURS par deux lignes exactes :
    RISQUE: faible|large
    VERDICT: pass|fail
"""

import argparse
import json
import os
import re
import sys

try:
    import yaml
except ImportError:  # PyYAML est le seul prérequis hors stdlib.
    yaml = None

# --- Règles de risque déterministes (doctrine §6 : rayon large => validé) -----
SOCLE_PREFIXES = ("contrats/socle/", "doctrine/")
MID_PREFIXES = ("contrats/local/", "skills/", "agents/")
LOW_PREFIXES = ("backlog/", "evals/", "outils/", "docs/")
# Workflows produisant un check REQUIS au ruleset main-protection (rayon large).
REQUIRED_WORKFLOWS = frozenset({
    ".github/workflows/conformite.yml",      # « Avis d'impact »
    ".github/workflows/evals.yml",           # « Harnais skills »
    ".github/workflows/tests-garde-fous.yml",  # « Tests garde-fous server.py »
})
# Seuils explicites (déterministes, ajustables par promotion).
N_CONSOMMATEURS_LARGE = 3   # au-delà : un fichier « mid » devient large
N_RAYON_LARGE = 3           # au-delà de N artefacts touchés : rayon large

# Arbres de dépôt reconnus dans les chemins canoniques.
_ARBRES = "doctrine|contrats|skills|agents|backlog|evals|outils"
# Extrait un chemin canonique : backticks/guillemets/leading-slash tolérés,
# suffixe « (§x) » ignoré (il suit le chemin, pas capturé). CLAUDE.md à la racine.
_PATH_RE = re.compile(
    r"(?:/)?((?:" + _ARBRES + r")/[\w./-]+\.(?:md|ya?ml|py)|CLAUDE\.md)"
)
# Citation d'un chantier par son id en prose (« T-0029 »), résolue vers son
# fichier backlog — au même titre que les ids de skills (T-0020-c marche 2).
_CHANTIER_ID_RE = re.compile(r"\bT-\d{4}[a-z]?(?:-[a-z0-9]+)?\b")
_IGNORE_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache"}
# Artefacts de travail transitoires du workflow, jamais canoniques : exclus de
# l'index pour ne pas être comptés comme faux consommateurs (T-0020-c marche 2).
_ARTEFACTS_TRAVAIL = frozenset({"changed-files.txt"})

# Propriétaire « gardien » au sens CODEOWNERS. Un périmètre est DÉLÉGUÉ dès qu'un
# propriétaire AUTRE que le gardien y figure (organisation.md §4.1) : il relève
# alors de la porte humaine de son délégué et l'agent-gardien l'exclut de son
# circuit d'auto-approbation — jamais d'auto-merge d'un périmètre délégué.
_GARDIEN = "@Alliaconsulting"
_CODEOWNERS_REL = ".github/CODEOWNERS"


def _lister_fichiers(root):
    """Index de tous les fichiers du dépôt, en chemins relatifs POSIX."""
    fichiers = set()
    for base, dirs, noms in os.walk(root):
        dirs[:] = [d for d in dirs if d not in _IGNORE_DIRS]
        for nom in noms:
            if nom in _ARTEFACTS_TRAVAIL:
                continue
            rel = os.path.relpath(os.path.join(base, nom), root)
            fichiers.add(rel.replace(os.sep, "/"))
    return fichiers


def _lire(root, rel):
    try:
        with open(os.path.join(root, rel), "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except (OSError, UnicodeError):
        return ""


def _refs_texte(raw):
    """Chemins canoniques cités dans le texte brut (backticks, guillemets, nus),
    plus les citations d'un chantier par son id en prose
    (« T-0029 » -> backlog/chantiers/T-0029.yaml), au même titre que les ids de skills."""
    refs = set(_PATH_RE.findall(raw))
    for cid in _CHANTIER_ID_RE.findall(raw):
        refs.add("backlog/chantiers/%s.yaml" % cid)
    return refs


def _refs_yaml(raw, rel):
    """Résout les formes SANS chemin explicite : skills:[id] et depend_de:[T-xxxx]."""
    refs = set()
    if yaml is None or not rel.endswith((".yaml", ".yml")):
        return refs
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError:
        return refs
    if not isinstance(doc, dict):
        return refs

    def _ids(valeur):
        if isinstance(valeur, list):
            return [v for v in valeur if isinstance(v, str)]
        if isinstance(valeur, str):
            return [valeur]
        return []

    for skid in _ids(doc.get("skills")):
        refs.add("skills/%s/SKILL.md" % skid.strip())
    for dep in _ids(doc.get("depend_de")):
        dep = dep.strip()
        if re.match(r"^T-\d", dep):  # id de chantier -> fichier backlog
            refs.add("backlog/chantiers/%s.yaml" % dep)
    return refs


def _construire_graphe(root, index):
    """consommateurs[cible] = {fichiers qui la référencent}. Les cibles pendantes
    (référencées mais hors index — p. ex. supprimées par le diff) sont conservées."""
    consommateurs = {}
    for f in index:
        raw = _lire(root, f)
        refs = _refs_texte(raw) | _refs_yaml(raw, f)
        for cible in refs:
            if cible == f:
                continue  # pas d'auto-consommation (domicile, etc.)
            consommateurs.setdefault(cible, set()).add(f)
    return consommateurs


def _consommateurs_transitifs(cible, consommateurs):
    """BFS sur le graphe inverse : consommateurs directs + transitifs (cycles gérés)."""
    vus = set()
    file = [cible]
    while file:
        courant = file.pop()
        for c in consommateurs.get(courant, ()):
            if c not in vus and c != cible:
                vus.add(c)
                file.append(c)
    return vus


def _normaliser_pattern(pattern):
    """Pattern CODEOWNERS -> préfixe POSIX : « / » de tête retiré ; un répertoire
    conserve son « / » de queue pour un match par préfixe robuste."""
    return pattern.strip().replace(os.sep, "/").lstrip("/")


def _perimetres_delegues(root):
    """Préfixes normalisés des périmètres délégués, lus dans .github/CODEOWNERS.

    Un (pattern, owners) est délégué si owners contient au moins un propriétaire
    différent du gardien. Le pattern « * » (défaut global) est TOUJOURS exclu —
    il ne rend jamais tout le dépôt délégué. Commentaires et lignes vides ignorés."""
    prefixes = []
    for ligne in _lire(root, _CODEOWNERS_REL).splitlines():
        ligne = ligne.split("#", 1)[0].strip()
        if not ligne:
            continue
        champs = ligne.split()
        if len(champs) < 2:
            continue
        pattern, owners = champs[0], champs[1:]
        if pattern == "*":
            continue
        if any(o != _GARDIEN for o in owners):
            prefixes.append(_normaliser_pattern(pattern))
    return prefixes


def _chemin_delegue(chemin, prefixes):
    """Un chemin (normalisé POSIX) matche-t-il un périmètre délégué ?"""
    chemin = chemin.strip().replace(os.sep, "/").lstrip("/")
    for p in prefixes:
        if p.endswith("/"):
            if chemin == p.rstrip("/") or chemin.startswith(p):
                return True
        elif chemin == p or chemin.startswith(p + "/"):
            return True
    return False


def _sous(prefixes, chemin):
    return any(chemin.startswith(p) for p in prefixes)


def _risque_fichier(chemin, consommateurs_transitifs, index):
    """Règle de risque déterministe (doctrine §3/§6)."""
    if _sous(SOCLE_PREFIXES, chemin):
        return "large"
    if chemin in REQUIRED_WORKFLOWS:
        return "large"
    if _sous(MID_PREFIXES, chemin):
        conso_socle = any(_sous(SOCLE_PREFIXES, c) for c in consommateurs_transitifs)
        if conso_socle or len(consommateurs_transitifs) > N_CONSOMMATEURS_LARGE:
            return "large"
        return "faible"
    if _sous(LOW_PREFIXES, chemin):
        return "faible"
    return "faible"


def _rayon_fichier(risque, n_artefacts):
    if risque == "large" or n_artefacts > N_RAYON_LARGE:
        return "large"
    return "local"


def analyze(repo_root, changed):
    """Cœur du calcul. Retourne un dict sérialisable décrivant l'impact."""
    index = _lister_fichiers(repo_root)
    consommateurs = _construire_graphe(repo_root, index)
    prefixes_delegues = _perimetres_delegues(repo_root)

    par_fichier = {}
    casse_structurelle = False
    risque_global = "faible"
    delegue = False

    for chemin in changed:
        chemin = chemin.strip().replace(os.sep, "/").lstrip("/")
        if not chemin:
            continue
        if _chemin_delegue(chemin, prefixes_delegues):
            delegue = True
        conso = _consommateurs_transitifs(chemin, consommateurs)
        n = len(conso)
        risque = _risque_fichier(chemin, conso, index)
        rayon = _rayon_fichier(risque, n)

        existe = os.path.exists(os.path.join(repo_root, chemin))
        pendante = (not existe) and n > 0  # chemin supprimé mais encore référencé
        if pendante:
            casse_structurelle = True

        if risque == "large":
            risque_global = "large"

        par_fichier[chemin] = {
            "consommateurs": sorted(conso),
            "n_artefacts": n,
            "rayon": rayon,
            "risque": risque,
            "existe": existe,
            "reference_pendante": pendante,
        }

    verdict = "fail" if casse_structurelle else "pass"
    return {
        "changed": [c.strip().replace(os.sep, "/").lstrip("/") for c in changed if c.strip()],
        "par_fichier": par_fichier,
        "risque": risque_global,
        "casse_structurelle": casse_structurelle,
        "delegue": delegue,
        "verdict": verdict,
    }


def rapport_markdown(res):
    """Rapport lisible, terminé par les deux lignes contractuelles RISQUE puis VERDICT."""
    out = []
    out.append("### 🔎 Calcul d'impact déterministe (agent-gardien — marche 1)")
    out.append("")
    out.append("Rayon et risque sont calculés sur les **consommateurs réels** "
               "(dépendances déclarées + citations canoniques), pas par grep fruste.")
    out.append("")
    if not res["par_fichier"]:
        out.append("_Aucun fichier modifié analysable._")
    for chemin, pf in sorted(res["par_fichier"].items()):
        out.append("- **`%s`**" % chemin)
        out.append("  - rayon : **%s** · risque : **%s** · artefacts consommateurs : **%d**"
                   % (pf["rayon"], pf["risque"], pf["n_artefacts"]))
        if pf["reference_pendante"]:
            out.append("  - ⚠️ **casse structurelle** : chemin absent du dépôt mais "
                       "encore référencé par %d fichier(s)." % pf["n_artefacts"])
        if pf["consommateurs"]:
            apercu = ", ".join("`%s`" % c for c in pf["consommateurs"][:8])
            reste = pf["n_artefacts"] - min(8, pf["n_artefacts"])
            out.append("  - consommateurs : %s%s" % (apercu, (" … +%d" % reste) if reste else ""))
    out.append("")
    if res["casse_structurelle"]:
        out.append("> ❌ Casse structurelle détectée — au moins un consommateur pointe "
                   "un chemin supprimé par le diff.")
        out.append("")
    out.append("> Tête-agent du gardien (**doctrine §3**) — il **calcule et filtre**, "
               "il **n'approuve pas**, il **ne merge jamais**.")
    out.append("")
    out.append("DELEGUE: %s" % ("oui" if res.get("delegue") else "non"))
    out.append("RISQUE: %s" % res["risque"])
    out.append("VERDICT: %s" % res["verdict"])
    return "\n".join(out)


def _lire_changed(args):
    if args.changed:
        return args.changed
    if os.path.exists("changed-files.txt"):
        with open("changed-files.txt", "r", encoding="utf-8") as fh:
            return [l.strip() for l in fh if l.strip()]
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calcul d'impact fin de l'agent-gardien.")
    parser.add_argument("--changed", nargs="*", default=None,
                        help="chemins modifiés ; à défaut, lit changed-files.txt")
    parser.add_argument("--repo-root", default=".", help="racine du dépôt (défaut : .)")
    parser.add_argument("--json", action="store_true", help="sortie JSON au lieu du markdown")
    args = parser.parse_args(argv)

    changed = _lire_changed(args)
    res = analyze(args.repo_root, changed)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(rapport_markdown(res))
    # Code de sortie : 0 tant que le calcul aboutit (le VERDICT vit dans le rapport,
    # le workflow décide du statut du check). Ne bloque pas sur son propre calcul.
    return 0


if __name__ == "__main__":
    sys.exit(main())
