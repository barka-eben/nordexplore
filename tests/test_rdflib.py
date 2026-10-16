"""Tests nécessitant RDFlib et Flask : parité SPARQL/Python et routes de l'application.

Ignorés automatiquement si RDFlib n'est pas installé (pip install -r requirements.txt).
"""
import unittest

try:
    import rdflib  # noqa: F401
    HAS = True
except ImportError:
    HAS = False

from nordexplore.evaluation import SCENARIOS
from nordexplore.recommend import recommander
from tests.helpers import DATA, DictRepository


@unittest.skipUnless(HAS, "rdflib non installé")
class TestParite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from nordexplore.repository import RdflibRepository, charger_graphe
        cls.g = charger_graphe(DATA)
        cls.rdf = RdflibRepository(cls.g)
        cls.ref = DictRepository()

    def test_meme_classement_que_la_reference_python(self):
        for sc in SCENARIOS:
            a = [(x["hebergement"]["id"], x["score"]) for x in recommander(self.rdf, sc["requete"])["resultats"]]
            b = [(x["hebergement"]["id"], x["score"]) for x in recommander(self.ref, sc["requete"])["resultats"]]
            self.assertEqual(a, b, sc["nom"])

    def test_mu_identique(self):
        self.assertAlmostEqual(self.rdf.mu(), self.ref.mu(), places=6)

    def test_requetes_de_controle_renvoient_zero_ligne(self):
        from nordexplore import queries as Q
        for nom in ("C1", "C2", "C3", "C4"):
            self.assertEqual(len(list(self.g.query(getattr(Q, nom)))), 0, nom)

    def test_ask_r5(self):
        from nordexplore import queries as Q
        self.assertTrue(self.g.query(Q.R5).askAnswer)

    def test_au_moins_six_requetes_types(self):
        from nordexplore import queries as Q
        self.assertEqual(len([n for n in ("R1", "R2", "R3", "R4", "R5", "R6") if hasattr(Q, n)]), 6)


@unittest.skipUnless(HAS, "rdflib non installé")
class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from nordexplore.app import create_app
        cls.c = create_app(DATA).test_client()

    def test_pages_principales(self):
        for url in ("/", "/preferences", "/resultats?commune=Garoua&budget=50000&personnes=2",
                    "/carte", "/donnees", "/evaluation", "/hebergement/HotelLeBenoue.html",
                    "/ressource/Garoua", "/comparer?ids=HotelLeBenoue&ids=AubergeDeLaFalaise",
                    "/api/resultats.json?budget=50000", "/sparql"):
            r = self.c.get(url)
            self.assertEqual(r.status_code, 200, url)

    def test_exports(self):
        self.assertIn(b"HotelLeBenoue", self.c.get("/hebergement/HotelLeBenoue.ttl").data)
        self.assertEqual(self.c.get("/hebergement/HotelLeBenoue.jsonld").status_code, 200)

    def test_404_et_identifiant_invalide(self):
        self.assertEqual(self.c.get("/hebergement/Inexistant.html").status_code, 404)
        self.assertEqual(self.c.get("/hebergement/a%20b.html").status_code, 404)

    def test_sparql_lecture_seule_et_sans_service(self):
        ok = self.c.post("/sparql", data={"query": "ASK { ?s ?p ?o }"})
        self.assertEqual(ok.status_code, 200)
        for q in ("INSERT DATA { <a:b> <a:c> <a:d> }",
                  "SELECT * WHERE { SERVICE <http://example.org/s> { ?s ?p ?o } }"):
            self.assertEqual(self.c.post("/sparql", data={"query": q}).status_code, 400)

    def test_json_ld_embarque(self):
        html = self.c.get("/hebergement/HotelLeBenoue.html").data.decode()
        self.assertIn("application/ld+json", html)
        self.assertIn("aggregateRating", html)


if __name__ == "__main__":
    unittest.main()
