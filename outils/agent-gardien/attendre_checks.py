#!/usr/bin/env python3
"""Anti-faux-vert de l'auto-approbation (T-0020-c marche 2).

Attend que les checks REQUIS du ruleset main-protection soient tous
completed/success sur le head_sha EXACT, puis autorise le merge. Toute
incertitude (check manquant ou en cours au-delà du délai, ou non-success)
=> refus : la porte reste humaine (fail-closed).

Écrit `merge=oui|non` dans $GITHUB_OUTPUT. N'exécute AUCUN merge lui-même.
Dépend de `gh` (présent sur les runners) et de la stdlib.
"""
import os
import subprocess
import sys
import time

REQUIS = ["Avis d'impact", "Harnais skills", "Tests garde-fous server.py"]
DELAI_S = int(os.environ.get("DELAI_S", "900"))
INTERVALLE_S = int(os.environ.get("INTERVALLE_S", "15"))


def _etat(repo, sha):
    out = subprocess.run(
        ["gh", "api", "repos/%s/commits/%s/check-runs" % (repo, sha), "--paginate",
         "--jq", '.check_runs[] | [.name, .status, (.conclusion // "")] | @tsv'],
        check=True, capture_output=True, text=True).stdout
    state = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        state[parts[0]] = (parts[1], parts[2] if len(parts) > 2 else "")
    return state


def verdict(state):
    failed = [c for c in REQUIS
              if state.get(c, ("", ""))[0] == "completed" and state[c][1] != "success"]
    if failed:
        return "fail", failed
    notdone = [c for c in REQUIS if c not in state or state[c][0] != "completed"]
    if notdone:
        return "wait", notdone
    return "ok", []


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    sha = os.environ["HEAD_SHA"]
    fin = time.monotonic() + DELAI_S
    while True:
        v, reste = verdict(_etat(repo, sha))
        if v == "ok":
            decision, motif = "oui", "les 3 checks requis sont completed/success"
            break
        if v == "fail":
            decision, motif = "non", "check requis non success : %s" % ", ".join(reste)
            break
        if time.monotonic() >= fin:
            decision, motif = "non", "délai dépassé, checks non finis : %s" % ", ".join(reste)
            break
        time.sleep(INTERVALLE_S)
    print("Auto-approbation : merge=%s (%s)" % (decision, motif))
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as fh:
            fh.write("merge=%s\n" % decision)
    return 0


if __name__ == "__main__":
    sys.exit(main())
