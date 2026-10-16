"""Contrôles du jeu de données (objectif O2) sans RDFlib, via le mini-parseur."""
import unittest
from collections import defaultdict

from tests.helpers import EX, RDF_TYPE, load_triples, mini_parse_turtle, DATA

RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"


class TestDonnees(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = mini_parse_turtle((DATA / "donnees.ttl").read_text(encoding="utf-8"))
        cls.types = defaultdict(set)
        cls.labels = defaultdict(list)
        for s, p, o in cls.t:
            if p == RDF_TYPE:
                cls.types[s].add(o)
            if p == RDFS_LABEL:
                cls.labels[s].append(o)

    def compte(self, cls):
        return sum(1 for s, ts in self.types.items() if EX + cls in ts)

    def test_volumes_minimaux(self):
        self.assertGreaterEqual(self.compte("Hotel") + self.compte("Auberge"), 15)
        self.assertGreaterEqual(self.compte("Offre"), 25)
        self.assertGreaterEqual(self.compte("Avis"), 30)

    def test_toutes_les_ressources_sont_typees(self):
        sujets = {s for s, _, _ in self.t}
        sans_type = [s for s in sujets if s not in self.types]
        self.assertEqual(sans_type, [])

    def test_toutes_les_ressources_ont_un_libelle_sauf_visite(self):
        manquants = [s.replace(EX, "") for s in self.types
                     if s not in self.labels and EX + "VisiteGuidee" not in self.types[s]]
        self.assertEqual(manquants, [])

    def test_libelles_ont_etiquette_de_langue(self):
        sans_langue = [(s, o) for s, p, o in self.t if p == RDFS_LABEL and not o[2]]
        self.assertEqual(sans_langue, [])

    def test_un_seul_nombre_d_etoiles_par_hebergement(self):
        cnt = defaultdict(int)
        for s, p, o in self.t:
            if p == EX + "nombreEtoiles":
                cnt[s] += 1
        self.assertTrue(all(v == 1 for v in cnt.values()))

    def test_hotel_et_auberge_disjoints(self):
        for s, ts in self.types.items():
            self.assertFalse({EX + "Hotel", EX + "Auberge"} <= ts, s)

    def test_notes_entre_1_et_5(self):
        for s, p, o in self.t:
            if p in (EX + "note", EX + "noteProprete", EX + "noteAccueil", EX + "noteRapportQualitePrix"):
                self.assertTrue(1 <= int(o[1]) <= 5, (s, o))

    def test_chaque_hebergement_a_commune_offre_paiement(self):
        for h, ts in self.types.items():
            if ts & {EX + "Hotel", EX + "Auberge"}:
                preds = {p for s, p, o in self.t if s == h}
                for need in ("situeDans", "aOffre", "accepteMode", "nombreEtoiles"):
                    self.assertIn(EX + need, preds, f"{h} sans {need}")

    def test_donnees_marquees_illustratives(self):
        txt = (DATA / "donnees.ttl").read_text(encoding="utf-8")
        self.assertIn("ILLUSTRATIVES", txt)


if __name__ == "__main__":
    unittest.main()
