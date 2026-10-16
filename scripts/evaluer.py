#!/usr/bin/env python3
"""Évalue le moteur sur les 5 scénarios et le compare au tri par étoiles (objectif O7)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nordexplore.evaluation import evaluer                          # noqa: E402
from nordexplore.repository import RdflibRepository, charger_graphe  # noqa: E402

repo = RdflibRepository(charger_graphe(Path(__file__).resolve().parent.parent / "data"))
ev = evaluer(repo)
for l in ev["lignes"]:
    print(f"{'OK ' if l['ok'] else 'ÉCART'} {l['scenario']:<24} attendu={l['attendu']} moteur={l['moteur']} étoiles={l['tri_etoiles']}")
print(f"\nConcordance du 1er résultat : moteur {ev['concordance_moteur']} · tri par étoiles {ev['concordance_tri_etoiles']}")
print(f"Part des résultats expliqués : {ev['part_expliquee']:.0f} %")
