import unittest

from nordexplore.evaluation import SCENARIOS, evaluer
from nordexplore.recommend import Requete, propositions_assouplissement, recommander, tri_par_etoiles
from tests.helpers import DictRepository


class TestMoteur(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = DictRepository()

    def test_filtrage_dur_respecte_budget_capacite_etoiles(self):
        q = Requete(commune="Garoua", budget=50000, personnes=2, etoiles_min=2)
        r = recommander(self.repo, q)
        for x in r["resultats"]:
            self.assertGreaterEqual(x["hebergement"]["etoiles"], 2)
            self.assertLessEqual(x["offre"]["tarif"], 50000)
            self.assertGreaterEqual(x["offre"]["capacite"], 2)

    def test_les_exclus_ont_un_motif(self):
        q = Requete(commune="Garoua", budget=50000, personnes=2, etoiles_min=2)
        r = recommander(self.repo, q)
        self.assertTrue(r["ecartes"])
        for e in r["ecartes"]:
            self.assertTrue(e["motifs"], e["hebergement"]["id"])
        ids = {e["hebergement"]["id"] for e in r["ecartes"]}
        self.assertIn("ResidenceDuFleuve", ids)   # 62 000 FCFA > 50 000
        motifs = next(e["motifs"] for e in r["ecartes"] if e["hebergement"]["id"] == "ResidenceDuFleuve")
        self.assertIn("tarif supérieur au budget", motifs[0])

    def test_resultats_et_ecartes_partitionnent_la_commune(self):
        q = Requete(commune="Garoua", budget=40000, personnes=2)
        r = recommander(self.repo, q)
        tous = {h["id"] for h in self.repo.hebergements("Garoua")}
        vus = {x["hebergement"]["id"] for x in r["resultats"]} | {e["hebergement"]["id"] for e in r["ecartes"]}
        self.assertEqual(tous, vus)

    def test_tri_decroissant_et_explication_pour_chaque_resultat(self):
        q = Requete(commune="Garoua", budget=60000, personnes=2, equipements=["Wifi"], profil="VoyageurAffaires")
        r = recommander(self.repo, q)
        scores = [x["score_brut"] for x in r["resultats"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        for x in r["resultats"]:
            self.assertTrue(x["explication"].strip(". "))
            self.assertTrue(0 <= x["score"] <= 100)

    def test_regle_affaires_et_sous_classes(self):
        hs = {h["id"]: h for h in self.repo.hebergements("Garoua")}
        self.assertIn("VoyageurAffaires", hs["HotelLeBenoue"]["profils"])      # 4★ + wifi + restaurant
        self.assertNotIn("VoyageurAffaires", hs["HotelPanoramaGaroua"]["profils"])   # pas de wifi
        self.assertNotIn("VoyageurAffaires", hs["ResidenceEtoileDuNord"]["profils"])  # 2★
        # PetitDejeuner est une EquipementRestauration : couvert par la catégorie
        c = self.repo.couverts(["AubergeDuMarche"], ["EquipementRestauration"])
        self.assertEqual(c["AubergeDuMarche"], 1)

    def test_criteres_inactifs_ne_penalisent_pas(self):
        q = Requete(commune="Garoua", budget=50000, personnes=2)
        r = recommander(self.repo, q)
        self.assertEqual(r["criteres_actifs"], ["avis", "prix"])

    def test_aucun_resultat_et_assouplissement(self):
        q = Requete(commune="Garoua", budget=50000, personnes=4, etoiles_min=3)
        self.assertEqual(recommander(self.repo, q)["resultats"], [])
        alt = propositions_assouplissement(self.repo, q)
        self.assertTrue(alt)
        self.assertTrue(all(a["nb"] > 0 for a in alt))

    def test_egalite_departagee_par_note_puis_tarif(self):
        q = Requete(commune="Garoua", budget=100000, personnes=1)
        r = recommander(self.repo, q)
        for a, b in zip(r["resultats"], r["resultats"][1:]):
            if round(a["score_brut"], 6) == round(b["score_brut"], 6):
                ma, mb = a["hebergement"]["moyenne"] or 0, b["hebergement"]["moyenne"] or 0
                self.assertTrue(ma > mb or (ma == mb and a["offre"]["tarif"] <= b["offre"]["tarif"]))

    def test_evaluation_cinq_scenarios_toujours_expliques(self):
        ev = evaluer(self.repo)
        self.assertEqual(len(ev["lignes"]), 5)
        self.assertEqual(ev["part_expliquee"], 100.0)
        self.assertTrue(ev["sans_resultat_detecte"])

    def test_tri_par_etoiles_reference(self):
        q = Requete(commune="Garoua", budget=60000, personnes=1, etoiles_min=1)
        base = tri_par_etoiles(self.repo, q)
        etoiles = [h["etoiles"] for h in base]
        self.assertEqual(etoiles, sorted(etoiles, reverse=True))


if __name__ == "__main__":
    unittest.main()
