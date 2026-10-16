"""Formules de score du moteur NordExplore (dossier de conception, section 6.2).

Module en Python pur : aucune dépendance à RDFlib ni à Flask, donc testable seul.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("config.json")

# Ordre d'affichage des critères
CRITERES = ["avis", "equipements", "profil", "prix", "proximite", "paiement"]


def charger_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance à vol d'oiseau en km (formule de Haversine, rayon terrestre 6371 km)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def moyenne_lissee(n: int, m: float, mu: float, k: float = 3) -> float:
    """m' = (n*m + k*mu) / (n + k) : évite qu'un seul bon avis surclasse un établissement bien noté."""
    if n <= 0:
        return mu
    return (n * m + k * mu) / (n + k)


def sous_score_avis(n: int, m: float | None, mu: float, k: float = 3) -> float:
    mm = moyenne_lissee(n, m if m is not None else mu, mu, k)
    return 100.0 * mm / 5.0


def sous_score_equipements(couverts: int, souhaites: int) -> float:
    if souhaites <= 0:
        return 0.0
    return 100.0 * min(couverts, souhaites) / souhaites


def sous_score_profil(profils: set[str], profil_demande: str) -> float:
    return 100.0 if profil_demande in profils else 0.0


def sous_score_prix(tarif: float, budget: float) -> float:
    """100 * min(1, (B - t) / (0,3 B)) ; 0 si le tarif dépasse le budget."""
    if budget <= 0:
        return 0.0
    return 100.0 * max(0.0, min(1.0, (budget - tarif) / (0.3 * budget)))


def sous_score_proximite(d_km: float, rayon_km: float = 5.0) -> float:
    return 100.0 * max(0.0, 1.0 - d_km / rayon_km)


def sous_score_paiement(verifications: list[bool]) -> float:
    """Part des exigences (mode de paiement, accès PMR) satisfaites, sur 100."""
    if not verifications:
        return 0.0
    return 100.0 * sum(1 for v in verifications if v) / len(verifications)


def score_final(sous_scores: dict[str, float | None], poids: dict[str, float]) -> float:
    """Σ(poids × sous-score) / Σ poids, calculé sur les critères actifs.

    Un critère inactif a la valeur None : son poids est redistribué proportionnellement
    sur les autres (il n'entre ni au numérateur ni au dénominateur).
    """
    num = den = 0.0
    for c, s in sous_scores.items():
        if s is None:
            continue
        w = poids.get(c, 0.0)
        num += w * s
        den += w
    return num / den if den else 0.0
