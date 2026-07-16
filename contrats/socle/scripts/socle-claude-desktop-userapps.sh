#!/bin/zsh
# socle-claude-desktop-userapps.sh — v1.1 — T-0036
# Migration/consolidation de Claude Desktop en ~/Applications de l'utilisateur console.
# v1.1 : SUPPRESSION du téléchargement curl (endpoint public protégé par challenge
#        Cloudflare -> 403 systématique). L'installation du bundle est désormais du
#        ressort de l'app PKG Intune (Claude.pkg figé). Ce script ne fait plus que du
#        déplacement LOCAL + nettoyage anti-doublon + télémétrie. ZÉRO réseau.
# Contexte Intune : root. Idempotent. Sans effet de bord réseau.
set -euo pipefail

APP="Claude.app"
SYS="/Applications/${APP}"

# --- 0. Utilisateur console (pattern socle-cli-collaborateur / T-0006) ---
CONSOLE_USER=$(stat -f%Su /dev/console)
if [[ -z "$CONSOLE_USER" || "$CONSOLE_USER" == "root" || "$CONSOLE_USER" == "_mbsetupuser" ]]; then
  echo "anomalie:aucun-utilisateur-console — report (Intune retentera)." >&2
  exit 1
fi
USER_HOME=$(dscl . -read "/Users/${CONSOLE_USER}" NFSHomeDirectory | awk '{print $2}')
DEST="${USER_HOME}/Applications"
USER_APP="${DEST}/${APP}"

vlire() { defaults read "${1}/Contents/Info" CFBundleShortVersionString 2>/dev/null || echo "?"; }

# --- 1. Déjà conforme : user présent, système propre -> rien à faire ---
if [[ -d "${USER_APP}" && ! -d "${SYS}" ]]; then
  echo "ok:$(vlire "${USER_APP}")  (emplacement-utilisateur, /Applications propre)"
  exit 0
fi

# --- 2. Rien déposé nulle part -> l'app PKG n'a pas encore posé le bundle ---
if [[ ! -d "${USER_APP}" && ! -d "${SYS}" ]]; then
  echo "attente:app-pkg  (aucun Claude.app détecté — install PKG en attente, aucun échec)"
  exit 0
fi

# --- 3. Au moins /Applications présent (cas migration ou doublon) ---
pkill -x "Claude" 2>/dev/null || true
sleep 3
mkdir -p "${DEST}"
rm -rf "${USER_APP}"
ditto "${SYS}" "${USER_APP}"
chown -R "${CONSOLE_USER}:staff" "${DEST}"
rm -rf "${SYS}"

# --- 4. Verdict ---
if [[ -d "${USER_APP}" && ! -d "${SYS}" ]]; then
  echo "ok:$(vlire "${USER_APP}")  (migré vers emplacement-utilisateur, /Applications nettoyé)"
  exit 0
else
  echo "anomalie:migration-incomplete  (user:$([[ -d ${USER_APP} ]] && echo oui || echo non) sys:$([[ -d ${SYS} ]] && echo oui || echo non))" >&2
  exit 1
fi
