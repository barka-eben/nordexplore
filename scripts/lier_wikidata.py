#!/usr/bin/env python3
"""Génère data/liens_wikidata.ttl (owl:sameAs) à partir de data/wikidata_ids.json.

Les identifiants ne sont volontairement pas fournis : ils doivent être relevés et vérifiés
sur wikidata.org (objectif O3 du dossier). Le fichier produit est chargé automatiquement.
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
ids = json.loads((DATA / "wikidata_ids.json").read_text(encoding="utf-8"))
lignes = ["@prefix ex:  <http://example.org/nord#> .",
          "@prefix owl: <http://www.w3.org/2002/07/owl#> .", ""]
n = 0
for nom, q in ids.items():
    if nom.startswith("_") or not q:
        continue
    if not re.fullmatch(r"Q\d+", q):
        raise SystemExit(f"Identifiant invalide pour {nom} : {q!r} (attendu : Q suivi de chiffres)")
    lignes.append(f"ex:{nom} owl:sameAs <http://www.wikidata.org/entity/{q}> .")
    n += 1
if n == 0:
    raise SystemExit("Aucun identifiant renseigné dans data/wikidata_ids.json : rien à générer.")
(DATA / "liens_wikidata.ttl").write_text("\n".join(lignes) + "\n", encoding="utf-8")
print(f"{n} lien(s) owl:sameAs écrits dans data/liens_wikidata.ttl")
