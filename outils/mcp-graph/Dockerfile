# syntax=docker/dockerfile:1
# Image du serveur MCP Graph (Allia) — T-0002b-2 (part agent : Dockerfile).
# Contraintes aval (contrat_interface de T-0002b-1) : Linux/amd64 uniquement, conteneur NON privilégié,
# stateless only, TOUTES les dépendances dans l'image. Ne modifie PAS server.py (promu) — on le
# conteneurise tel quel. Aucun secret dans l'image (la SORTIE Graph s'authentifie par identité managée).
# Plateforme amd64 : garantie PAR LA COMMANDE DE BUILD (`az acr build --platform linux/amd64` ;
# défaut ACR Tasks = Linux/AMD64), PAS par un flag `--platform` inline dans le FROM — le scanner de
# dépendances d'ACR Tasks ne parse pas `FROM --platform=...` (« unable to understand line », build
# avorté avant exécution). Ne pas réintroduire ce flag ici.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances d'abord (couche de cache) — toutes embarquées dans l'image (exigence Container Apps).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Code du connecteur uniquement. Le .env n'entre JAMAIS (voir .dockerignore) : aucun secret embarqué.
COPY server.py ./

# Hôte d'écoute : `mcp.run(transport="streamable-http")` écoute par DÉFAUT sur 127.0.0.1:8000,
# INJOIGNABLE par une sonde externe / l'ingress. FastMCP lit FASTMCP_HOST / FASTMCP_PORT depuis
# l'environnement → on force l'écoute sur 0.0.0.0:8000 SANS toucher server.py (code promu).
ENV FASTMCP_HOST=0.0.0.0 \
    FASTMCP_PORT=8000
EXPOSE 8000

# Conteneur NON privilégié : exécution sous un utilisateur non-root.
RUN useradd --create-home --uid 10001 appuser
USER appuser

# Lancement direct par le SDK MCP (transport HTTP streamable) — PAS uvicorn/FastAPI : notre code
# promu ne les utilise pas. /mcp (JSON-RPC POST) et /healthz (liveness pur) sont exposés par server.py.
CMD ["python", "server.py"]
