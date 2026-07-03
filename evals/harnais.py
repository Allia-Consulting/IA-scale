#!/usr/bin/env python3
"""Harnais d'evals des skills — v0 déterministe (chantier T-0020-a, plan §7 T-2.1).

Non-régression des prompts/skills en CI sur chaque PR :
  1. Couverture bidirectionnelle : chaque skills/<id>/SKILL.md a son
     evals/skills/<id>/golden.yaml, et réciproquement.
  2. Validation sémantique de chaque golden.yaml (clés racine, structure).
  3. Invariants d'en-tête universels sur chaque SKILL.md.
  4. Cas de type 'invariant' : ancres verbatim (contient) et motifs (regex).
Le type 'scenario' (scoring LLM) est réservé au schéma, ignoré en v0.
Sortie : rapport par cas ; code retour 1 à la première famille d'échecs.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
GOLDEN_DIR = ROOT / "evals" / "skills"

def skill_ids():
    return sorted(p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md"))

def golden_ids():
    return sorted(p.parent.name for p in GOLDEN_DIR.glob("*/golden.yaml"))

def check_universal(skill, text, errors):
    checks = [
        (re.search(r"\*\*id\*\*\s*:\s*`%s`" % re.escape(skill), text),
         f"[{skill}] en-tête : id `{skill}` absent"),
        (re.search(r"\*\*Version\*\*", text),
         f"[{skill}] en-tête : champ Version absent"),
        (re.search(r"\*(candidat|promu)\*", text),
         f"[{skill}] en-tête : statut *candidat*/*promu* absent"),
        (f"skills/{skill}/SKILL.md" in text,
         f"[{skill}] en-tête : Domicile canonique absent"),
    ]
    for ok, msg in checks:
        if not ok:
            errors.append(msg)

def check_golden(skill, errors):
    path = GOLDEN_DIR / skill / "golden.yaml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"[{skill}] golden.yaml illisible : {exc}")
        return
    if not isinstance(data, dict):
        errors.append(f"[{skill}] golden.yaml : racine non-dict")
        return
    if data.get("skill") != skill:
        errors.append(f"[{skill}] golden.yaml : clé skill != nom du répertoire")
    if data.get("version_harnais") != 1:
        errors.append(f"[{skill}] golden.yaml : version_harnais != 1")
    cas = data.get("cas")
    if not isinstance(cas, list) or not cas:
        errors.append(f"[{skill}] golden.yaml : liste cas vide ou absente")
        return
    text = (SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8")
    seen, n_ok, n_scen = set(), 0, 0
    for c in cas:
        cid = c.get("id")
        if not cid or cid in seen:
            errors.append(f"[{skill}] cas id manquant ou dupliqué : {cid!r}")
            continue
        seen.add(cid)
        ctype = c.get("type")
        if ctype == "scenario":
            n_scen += 1
            continue
        if ctype != "invariant":
            errors.append(f"[{skill}:{cid}] type inconnu : {ctype!r}")
            continue
        anchors = c.get("contient") or []
        patterns = c.get("regex") or []
        if not anchors and not patterns:
            errors.append(f"[{skill}:{cid}] invariant sans contient ni regex")
            continue
        ok = True
        for a in anchors:
            if a not in text:
                errors.append(f"[{skill}:{cid}] ancre absente : {a!r}")
                ok = False
        for p in patterns:
            if not re.search(p, text):
                errors.append(f"[{skill}:{cid}] regex sans correspondance : {p!r}")
                ok = False
        n_ok += 1 if ok else 0
    print(f"  {skill}: {n_ok}/{len(seen) - n_scen} invariants verts"
          + (f", {n_scen} scenario ignorés (v0)" if n_scen else ""))

if __name__ == "__main__":
    errs = []
    s_ids, g_ids = skill_ids(), golden_ids()
    print(f"Harnais v0 — {len(s_ids)} skills, {len(g_ids)} golden sets")
    for missing in sorted(set(s_ids) - set(g_ids)):
        errs.append(f"[couverture] skill sans golden set : {missing}")
    for orphan in sorted(set(g_ids) - set(s_ids)):
        errs.append(f"[couverture] golden orphelin sans skill : {orphan}")
    if errs:
        print("\nÉCHECS :")
        for e in errs:
            print(f"  ✗ {e}")
        sys.exit(1)
    for skill in s_ids:
        check_universal(skill, (SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8"), errs)
        check_golden(skill, errs)
    if errs:
        print("\nÉCHECS :")
        for e in errs:
            print(f"  ✗ {e}")
        sys.exit(1)
    print("\nHarnais VERT — non-régression des skills confirmée.")
