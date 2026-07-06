"""Insère le dossier du connecteur (outils/mcp-graph) dans sys.path pour `import server`.

Les tests importent le module `server` directement (comme le fait la preuve d'import du
workflow build-mcp-graph.yml). `import server` ne déclenche AUCUN appel réseau et n'exige
AUCUNE variable d'environnement M365 : le serveur « dort » à l'import (credential et config
ne sont lus qu'au moment d'un appel d'outil). Tous les garde-fous testés ici s'exécutent
AVANT `_config_mission()` / httpx — donc aucun test n'a besoin de secret ni de tenant.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
