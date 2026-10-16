"""Moteur de recommandation à base de connaissances (dossier, section 6).

Pipeline : filtrage dur -> enrichissement -> score sur 100 -> explication.
Le moteur ne dépend que d'un objet « repository » (voir repository.py pour la version
RDFlib/SPARQL ; tests/helpers.py fournit une version en Python pur pour les tests).

Interface attendue du repository :
    hebergements(commune)                          -> list[dict]
    eligibles(commune, budget, personnes, etoiles) -> dict[id, tarif_min]   (SPARQL R1)
    couverts(ids, souhaits)                        -> dict[id, int]         (SPARQL R2)
    mu()                                           -> float (moyenne générale des notes)
    repere(id)                                     -> (lat, lon, libellé) | None
    label(id, lang)                                -> str
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import scoring as sc


@dataclass
class Requete:
    commune: str = "Garoua"
    budget: float = 50000
    personnes: int = 2
    etoiles_min: int = 1
    equipements: list[str] = field(default_factory=list)   # ex ['Wifi', 'EquipementRestauration']
    profil: str | None = None                               # ex 'VoyageurAffaires'
    paiement: str | None = None                             # ex 'MobileMoney'
    pmr: bool = False
    repere: str | None = None                               # ex 'MarcheArtisanalGaroua'


def _fcfa(x: float) -> str:
    return f"{int(round(x)):,}".replace(",", " ") + " FCFA"


def _motifs_exclusion(h: dict, q: Requete) -> list[str]:
    motifs = []
    if h["etoiles"] < q.etoiles_min:
        motifs.append(f"moins de {q.etoiles_min} étoile(s) ({h['etoiles']}★)")
    adaptees = [o for o in h["offres"] if o["capacite"] >= q.personnes]
    if not h["offres"]:
        motifs.append("aucune offre tarifaire renseignée")
    elif not adaptees:
        cmax = max(o["capacite"] for o in h["offres"])
        motifs.append(f"capacité insuffisante (au plus {cmax} personne(s) par chambre)")
    else:
        tmin = min(o["tarif"] for o in adaptees)
        if tmin > q.budget:
            motifs.append(f"tarif supérieur au budget ({_fcfa(tmin)} pour la chambre la moins chère adaptée)")
    return motifs


def recommander(repo, q: Requete, config: dict | None = None, lang: str = "fr") -> dict:
    cfg = config or sc.charger_config()
    poids = cfg["poids"]
    k = cfg.get("lissage_k", 3)
    rayon = cfg.get("rayon_proximite_km", 5)

    tous = repo.hebergements(q.commune)
    elig = repo.eligibles(q.commune, q.budget, q.personnes, q.etoiles_min)
    mu = repo.mu()
    couv = repo.couverts(list(elig), q.equipements) if q.equipements else {}
    repere = repo.repere(q.repere) if q.repere else None

    resultats, ecartes = [], []
    for h in tous:
        if h["id"] not in elig:
            ecartes.append({"hebergement": h, "motifs": _motifs_exclusion(h, q)})
            continue

        offre = min((o for o in h["offres"]
                     if o["capacite"] >= q.personnes and o["tarif"] <= q.budget),
                    key=lambda o: o["tarif"])
        subs: dict[str, float | None] = {}
        details: dict[str, str] = {}

        subs["avis"] = sc.sous_score_avis(h["nb_avis"], h["moyenne"], mu, k)
        if h["nb_avis"]:
            details["avis"] = f"Note moyenne {h['moyenne']:.2f}/5 ({h['nb_avis']} avis)"
        else:
            details["avis"] = "Aucun avis (note neutre)"

        if q.equipements:
            n = couv.get(h["id"], 0)
            subs["equipements"] = sc.sous_score_equipements(n, len(q.equipements))
            noms = [repo.label(e, lang) for e in q.equipements]
            details["equipements"] = f"{n}/{len(q.equipements)} équipement(s) souhaité(s) : {', '.join(noms)}"
        else:
            subs["equipements"] = None

        if q.profil:
            subs["profil"] = sc.sous_score_profil(set(h["profils"]), q.profil)
            ok = q.profil in h["profils"]
            details["profil"] = (f"convient aux voyageurs « {repo.label(q.profil, lang)} »" if ok
                                 else f"profil « {repo.label(q.profil, lang)} » non indiqué")
        else:
            subs["profil"] = None

        subs["prix"] = sc.sous_score_prix(offre["tarif"], q.budget)
        details["prix"] = f"{_fcfa(offre['tarif'])} la nuit ({offre['type_label'].lower()}, {offre['capacite']} pers.)"

        if repere:
            d = sc.haversine_km(h["lat"], h["lon"], repere[0], repere[1])
            subs["proximite"] = sc.sous_score_proximite(d, rayon)
            details["proximite"] = f"à {d:.1f} km de « {repere[2]} »"
        else:
            d = None
            subs["proximite"] = None

        checks, txt = [], []
        if q.paiement:
            ok = q.paiement in h["paiements"]
            checks.append(ok)
            txt.append(f"{repo.label(q.paiement, lang)} {'accepté' if ok else 'non accepté'}")
        if q.pmr:
            checks.append(bool(h["pmr"]))
            txt.append("accessible PMR" if h["pmr"] else "non accessible PMR")
        if checks:
            subs["paiement"] = sc.sous_score_paiement(checks)
            details["paiement"] = " ; ".join(txt)
        else:
            subs["paiement"] = None

        score = sc.score_final(subs, poids)
        phrase = " · ".join(details[c] for c in sc.CRITERES if c in details)
        resultats.append({
            "hebergement": h, "score": round(score, 1), "score_brut": score,
            "sous_scores": subs, "details": details, "explication": phrase + ".",
            "offre": offre, "distance_km": d,
        })

    # Tri : score décroissant, puis note moyenne décroissante, puis tarif croissant
    resultats.sort(key=lambda r: (-round(r["score_brut"], 6),
                                  -(r["hebergement"]["moyenne"] or 0), r["offre"]["tarif"]))
    for i, r in enumerate(resultats, 1):
        r["rang"] = i
    return {"requete": q, "resultats": resultats, "ecartes": ecartes, "mu": mu,
            "criteres_actifs": [c for c in sc.CRITERES
                                if resultats and resultats[0]["sous_scores"].get(c) is not None]}


def propositions_assouplissement(repo, q: Requete, config: dict | None = None) -> list[dict]:
    """Si aucun résultat : propose d'assouplir une contrainte (budget +20 %, étoiles -1)."""
    cfg = config or sc.charger_config()
    marge = cfg.get("assouplissement_budget", 0.2)
    essais = []
    q1 = Requete(**{**q.__dict__, "budget": q.budget * (1 + marge)})
    essais.append((f"augmenter le budget de {int(marge * 100)} % ({_fcfa(q1.budget)})", q1))
    if q.etoiles_min > 1:
        q2 = Requete(**{**q.__dict__, "etoiles_min": q.etoiles_min - 1})
        essais.append((f"accepter {q2.etoiles_min} étoile(s) minimum", q2))
        q3 = Requete(**{**q.__dict__, "budget": q.budget * (1 + marge), "etoiles_min": q.etoiles_min - 1})
        essais.append(("combiner les deux assouplissements", q3))
    sorties = []
    for libelle, qq in essais:
        r = recommander(repo, qq, cfg)
        if r["resultats"]:
            sorties.append({"libelle": libelle, "requete": qq, "nb": len(r["resultats"])})
    return sorties


def tri_par_etoiles(repo, q: Requete) -> list[dict]:
    """Référence de comparaison : mêmes hébergements éligibles, triés par étoiles seulement."""
    elig = repo.eligibles(q.commune, q.budget, q.personnes, q.etoiles_min)
    hs = [h for h in repo.hebergements(q.commune) if h["id"] in elig]
    return sorted(hs, key=lambda h: (-h["etoiles"], h["label"]))
