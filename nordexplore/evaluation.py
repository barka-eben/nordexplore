"""Évaluation du moteur sur 5 scénarios (dossier, section 6.5).

Le classement attendu (« attendu ») est fixé à la main AVANT de lancer le moteur,
en lisant les données ; il ne doit pas être ajusté pour faire coïncider les résultats.
Deux mesures : concordance du premier résultat avec le choix attendu, et part des
résultats expliqués (objectif : 100 %). Le moteur est comparé à un simple tri par étoiles.
"""
from __future__ import annotations

from .recommend import Requete, recommander, tri_par_etoiles

SCENARIOS = [
    {"nom": "Affaires (Hadiza)",
     "requete": Requete(commune="Garoua", budget=60000, personnes=1, etoiles_min=3,
                        equipements=["Wifi", "EquipementRestauration"], profil="VoyageurAffaires",
                        paiement="MobileMoney", repere="MarcheArtisanalGaroua"),
     "attendu": "HotelLeBenoue",
     "raison": "4 étoiles, wifi + restaurant, bien noté, proche du centre, Mobile Money"},
    {"nom": "Famille Abdou",
     "requete": Requete(commune="Garoua", budget=70000, personnes=4, etoiles_min=2,
                        equipements=["Climatisation", "EquipementRestauration"],
                        profil="VoyageurFamille", paiement="Especes"),
     "attendu": "HotelSahelPlaza",
     "raison": "chambre familiale, clim + restaurant, profil famille, tarif raisonnable, bien noté"},
    {"nom": "Petit budget (Moussa)",
     "requete": Requete(commune="Garoua", budget=15000, personnes=1, etoiles_min=1,
                        profil="VoyageurBudget", paiement="Especes"),
     "attendu": "AubergeDuMarche",
     "raison": "tarif très bas, accueil bien noté, espèces acceptées"},
    {"nom": "Couple (détente)",
     "requete": Requete(commune="Garoua", budget=80000, personnes=2, etoiles_min=3,
                        equipements=["Climatisation", "Piscine"], profil="VoyageurCouple"),
     "attendu": "HotelAmbassadeurGaroua",
     "raison": "confort maximal (clim + piscine), meilleure note globale"},
    {"nom": "Requête sans résultat",
     "requete": Requete(commune="Garoua", budget=10000, personnes=4, etoiles_min=4),
     "attendu": None,
     "raison": "aucun hébergement 4★ n'a de chambre à 4 personnes à ce prix : le moteur doit le dire"},
]


def evaluer(repo, config=None) -> dict:
    lignes = []
    conc_moteur = conc_etoiles = n_avec_attendu = 0
    total = expliques = 0
    for sc in SCENARIOS:
        r = recommander(repo, sc["requete"], config)
        base = tri_par_etoiles(repo, sc["requete"])
        top = r["resultats"][0]["hebergement"]["id"] if r["resultats"] else None
        top_base = base[0]["id"] if base else None
        total += len(r["resultats"])
        expliques += sum(1 for x in r["resultats"] if x["explication"].strip(". "))
        if sc["attendu"] is not None:
            n_avec_attendu += 1
            conc_moteur += top == sc["attendu"]
            conc_etoiles += top_base == sc["attendu"]
            ok_scenario = top == sc["attendu"]
        else:
            ok_scenario = top is None
        lignes.append({"scenario": sc["nom"], "attendu": sc["attendu"], "moteur": top,
                       "tri_etoiles": top_base, "ok": ok_scenario, "nb": len(r["resultats"]),
                       "ecartes": len(r["ecartes"]), "raison": sc["raison"]})
    return {"lignes": lignes,
            "concordance_moteur": f"{conc_moteur}/{n_avec_attendu}",
            "concordance_tri_etoiles": f"{conc_etoiles}/{n_avec_attendu}",
            "part_expliquee": 100.0 * expliques / total if total else 100.0,
            "sans_resultat_detecte": next((l["ok"] for l, s in zip(lignes, SCENARIOS) if s["attendu"] is None), None)}
