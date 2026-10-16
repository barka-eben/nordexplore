#!/usr/bin/env python3
"""Requêtes SPARQL de contrôle qualité (dossier, section 4.5). Chaque contrôle doit renvoyer 0 ligne."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nordexplore import queries as Q                      # noqa: E402
from nordexplore.repository import charger_graphe         # noqa: E402

g = charger_graphe(Path(__file__).resolve().parent.parent / "data")
print(f"Graphe : {len(g)} triplets")
titres = {"C1": "ressource sans type", "C2": "ressource typée sans libellé",
          "C3": "hébergement sans commune", "C4": "hébergement sans offre"}
ko = 0
for nom, titre in titres.items():
    lignes = [str(r[0]) for r in g.query(getattr(Q, nom))]
    print(f"[{'OK' if not lignes else 'KO'}] {nom} - {titre} : {len(lignes)}")
    for l in lignes[:10]:
        print("      ", l)
    ko += bool(lignes)
print("\nRappel : vérifiez aussi la cohérence avec le raisonneur de Protégé (ontologie.ttl + donnees.ttl).")
sys.exit(1 if ko else 0)
