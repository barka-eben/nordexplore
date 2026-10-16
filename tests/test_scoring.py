import unittest

from nordexplore import scoring as sc


class TestFormules(unittest.TestCase):
    def test_exemple_chiffre_du_dossier(self):
        """Section 6.3 du dossier : 81,9 pour Le Bénoué et 63,4 pour l'Auberge de la Falaise (μ = 3,8)."""
        poids = sc.charger_config()["poids"]
        mu = 3.8
        benoue = sc.score_final({
            "avis": sc.sous_score_avis(4, 4.25, mu), "equipements": sc.sous_score_equipements(2, 2),
            "profil": 100, "prix": sc.sous_score_prix(45000, 50000),
            "proximite": sc.sous_score_proximite(1.2), "paiement": 100}, poids)
        falaise = sc.score_final({
            "avis": sc.sous_score_avis(2, 3.5, mu), "equipements": sc.sous_score_equipements(1, 2),
            "profil": 0, "prix": sc.sous_score_prix(18000, 50000),
            "proximite": sc.sous_score_proximite(0.6), "paiement": 100}, poids)
        self.assertEqual(round(benoue, 1), 81.9)
        self.assertEqual(round(falaise, 1), 63.4)

    def test_sous_scores_du_dossier(self):
        self.assertAlmostEqual(sc.sous_score_avis(4, 4.25, 3.8), 81.14, places=1)
        self.assertAlmostEqual(sc.sous_score_prix(45000, 50000), 33.33, places=1)
        self.assertEqual(sc.sous_score_prix(18000, 50000), 100.0)
        self.assertAlmostEqual(sc.sous_score_proximite(1.2), 76.0)

    def test_lissage_tire_un_avis_isole_vers_la_moyenne(self):
        # Un seul 5/5 est ramené vers μ, et reste sous 10 avis à 5/5.
        self.assertLess(sc.moyenne_lissee(1, 5.0, 3.8), 5.0)
        self.assertLess(sc.moyenne_lissee(1, 5.0, 3.8), sc.moyenne_lissee(10, 5.0, 3.8))

    def test_limite_connue_du_lissage_k3(self):
        """Avec k = 3, UN avis à 5/5 (m' = 4,10) dépasse encore 4 avis à 4,25 (m' = 4,06) :
        l'affirmation du dossier (section 6.2) n'est vraie qu'à partir de k = 6 (k = 5 donne une égalité exacte à 4,00).
        Ce test documente la limite ; k se règle dans config.json (lissage_k)."""
        self.assertGreater(sc.moyenne_lissee(1, 5.0, 3.8, k=3), sc.moyenne_lissee(4, 4.25, 3.8, k=3))
        self.assertAlmostEqual(sc.moyenne_lissee(1, 5.0, 3.8, k=5), sc.moyenne_lissee(4, 4.25, 3.8, k=5))
        self.assertLess(sc.moyenne_lissee(1, 5.0, 3.8, k=6), sc.moyenne_lissee(4, 4.25, 3.8, k=6))

    def test_sans_avis_note_neutre(self):
        self.assertAlmostEqual(sc.sous_score_avis(0, None, 3.8), 76.0)

    def test_critere_inactif_redistribue(self):
        poids = {"a": 50, "b": 50}
        self.assertEqual(sc.score_final({"a": 80, "b": None}, poids), 80.0)
        self.assertEqual(sc.score_final({"a": 80, "b": 40}, poids), 60.0)

    def test_prix_hors_budget_zero(self):
        self.assertEqual(sc.sous_score_prix(60000, 50000), 0.0)

    def test_haversine(self):
        self.assertAlmostEqual(sc.haversine_km(9.3, 13.4, 9.3, 13.4), 0.0)
        # 1 degré de latitude ≈ 111,2 km
        self.assertAlmostEqual(sc.haversine_km(0, 0, 1, 0), 111.19, delta=0.2)

    def test_poids_somme_100(self):
        self.assertEqual(sum(sc.charger_config()["poids"].values()), 100)


if __name__ == "__main__":
    unittest.main()
