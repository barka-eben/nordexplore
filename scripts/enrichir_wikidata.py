#!/usr/bin/env python3
"""R6 : lit la population des communes sur Wikidata (requête fédérée) et la met en cache.

Nécessite : des owl:sameAs (voir lier_wikidata.py) et une connexion Internet.
Résultat : data/cache_wikidata.json (réutilisable hors ligne).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nordexplore import queries as Q                      # noqa: E402
from nordexplore.repository import charger_graphe         # noqa: E402

data = Path(__file__).resolve().parent.parent / "data"
g = charger_graphe(data)
try:
    res = {str(r.commune): str(r.population) for r in g.query(Q.R6)}
except Exception as e:
    raise SystemExit(f"Échec de la requête fédérée (réseau ? owl:sameAs absents ?) : {e}")
(data / "cache_wikidata.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print(res or "Aucun résultat : vérifiez les owl:sameAs.")
