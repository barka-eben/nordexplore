"""Accès au graphe RDF (RDFlib). La couche services ne passe que par SPARQL.

Implémente l'interface décrite en tête de recommend.py, plus les méthodes utilisées par
l'interface (fiches, liens typés, exports).
"""
from __future__ import annotations

import math
import re
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL

from . import queries as Q

EX = Namespace("http://example.org/nord#")
NS = str(EX)
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

FICHIERS = ["ontologie.ttl", "donnees.ttl", "liens_wikidata.ttl"]  # le dernier est facultatif


def _id(term) -> str:
    return str(term).replace(NS, "")


def _check_id(x: str) -> str:
    if not ID_RE.match(x or ""):
        raise ValueError(f"Identifiant invalide : {x!r}")
    return x


def _num(x) -> float | None:
    return None if x is None else float(x.toPython() if hasattr(x, "toPython") else x)


def charger_graphe(data_dir: Path, activer_owlrl: bool = False) -> Graph:
    g = Graph()
    g.bind("ex", EX)
    g.bind("geo", GEO)
    for nom in FICHIERS:
        f = Path(data_dir) / nom
        if f.exists():
            g.parse(f, format="turtle")
    # Règle métier R4 (CONSTRUCT) : les triplets produits sont ajoutés au graphe
    for triple in list(g.query(Q.R4)):
        g.add(triple)
    # Inverse exploite / exploitePar (owl:inverseOf), matérialisé sans raisonneur externe
    for h, e in list(g.subject_objects(EX.exploitePar)):
        g.add((e, EX.exploite, h))
    if activer_owlrl:
        try:
            import owlrl
            owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
        except ImportError:
            print("owlrl non installé : raisonnement OWL-RL ignoré (pip install owlrl)")
    return g


class RdflibRepository:
    def __init__(self, graph: Graph):
        self.g = graph
        self._cache: dict = {}

    # ---------- utilitaires ----------
    def q(self, text: str):
        return self.g.query(text)

    def label(self, i: str, lang: str = "fr") -> str:
        uri = EX[i] if not i.startswith("http") else URIRef(i)
        labels = list(self.g.objects(uri, RDFS.label))
        for l in labels:
            if isinstance(l, Literal) and l.language == lang:
                return str(l)
        return str(labels[0]) if labels else i

    # ---------- interface du moteur ----------
    def mu(self) -> float:
        if "mu" not in self._cache:
            rows = list(self.q(Q.PREFIXES + "SELECT (AVG(?n) AS ?mu) WHERE { ?a a ex:Avis ; ex:note ?n }"))
            v = rows[0][0] if rows else None
            self._cache["mu"] = _num(v) if v is not None else 3.0
        return self._cache["mu"]

    def eligibles(self, commune, budget, personnes, etoiles) -> dict[str, float]:
        budget = float(budget)
        if not math.isfinite(budget):
            raise ValueError("budget invalide")
        txt = Q.R1 % {"commune": _check_id(commune), "etoiles": int(etoiles),
                      "budget": repr(budget), "personnes": int(personnes)}
        return {_id(r[0]): _num(r[1]) for r in self.q(txt)}

    def couverts(self, ids, souhaits) -> dict[str, int]:
        if not ids or not souhaits:
            return {}
        txt = Q.R2 % {"hebergements": " ".join("ex:" + _check_id(i) for i in ids),
                      "souhaits": " ".join("ex:" + _check_id(s) for s in souhaits)}
        res = {i: 0 for i in ids}
        for r in self.q(txt):
            res[_id(r[0])] = int(r[1].toPython())
        return res

    def repere(self, rid: str):
        rid = _check_id(rid)
        rows = list(self.q(Q.PREFIXES + f"SELECT ?lat ?lon WHERE {{ ex:{rid} geo:lat ?lat ; geo:long ?lon }}"))
        if not rows:
            return None
        return (_num(rows[0][0]), _num(rows[0][1]), self.label(rid))

    def hebergements(self, commune: str) -> list[dict]:
        commune = _check_id(commune)
        if commune in self._cache:
            return self._cache[commune]
        P = Q.PREFIXES
        base = {}
        for r in self.q(P + f"""
            SELECT ?h ?cls ?etoiles ?chambres ?lat ?lon ?pmr ?expl WHERE {{
              VALUES ?cls {{ ex:Hotel ex:Auberge }}
              ?h a ?cls ; ex:situeDans ex:{commune} ; ex:nombreEtoiles ?etoiles ;
                 geo:lat ?lat ; geo:long ?lon .
              OPTIONAL {{ ?h ex:nombreChambres ?chambres }}
              OPTIONAL {{ ?h ex:accessiblePMR ?pmr }}
              OPTIONAL {{ ?h ex:exploitePar ?expl }}
            }}"""):
            hid = _id(r.h)
            base[hid] = {
                "id": hid, "label": self.label(hid), "classe": _id(r.cls),
                "etoiles": int(r.etoiles.toPython()), "chambres": int(r.chambres.toPython()) if r.chambres else None,
                "lat": _num(r.lat), "lon": _num(r.lon), "pmr": bool(r.pmr.toPython()) if r.pmr else False,
                "exploitant": ({"id": _id(r.expl), "label": self.label(_id(r.expl))} if r.expl else None),
                "commune": commune, "offres": [], "equipements": [], "paiements": [],
                "profils": set(), "nb_avis": 0, "moyenne": None,
            }
        ids = " ".join("ex:" + i for i in base) or "ex:AucunHebergement"
        for r in self.q(P + f"""SELECT ?h ?o ?t ?tarif ?cap WHERE {{ VALUES ?h {{ {ids} }}
              ?h ex:aOffre ?o . ?o ex:typeChambre ?t ; ex:tarifNuit ?tarif ; ex:capacite ?cap }}"""):
            base[_id(r.h)]["offres"].append({
                "id": _id(r.o), "type": _id(r.t), "type_label": self.label(_id(r.t)),
                "tarif": _num(r.tarif), "capacite": int(r.cap.toPython())})
        for champ, prop in (("equipements", "proposeEquipement"), ("paiements", "accepteMode")):
            for r in self.q(P + f"SELECT ?h ?x WHERE {{ VALUES ?h {{ {ids} }} ?h ex:{prop} ?x }}"):
                base[_id(r.h)][champ].append(_id(r.x))
        for r in self.q(P + f"SELECT ?h ?x WHERE {{ VALUES ?h {{ {ids} }} ?h ex:convientA ?x }}"):
            base[_id(r.h)]["profils"].add(_id(r.x))
        for r in self.q(Q.R3):
            hid = _id(r.h)
            if hid in base:
                base[hid]["moyenne"] = _num(r.moyenne)
                base[hid]["nb_avis"] = int(r.nbAvis.toPython())
        res = sorted(base.values(), key=lambda h: h["label"])
        self._cache[commune] = res
        return res

    # ---------- listes pour les formulaires ----------
    def communes(self) -> list[dict]:
        rows = self.q(Q.PREFIXES + "SELECT DISTINCT ?c WHERE { ?c a ex:Commune . ?h ex:situeDans ?c "
                      ". VALUES ?k { ex:Hotel ex:Auberge } ?h a ?k }")
        return sorted(({"id": _id(r.c), "label": self.label(_id(r.c))} for r in rows), key=lambda x: x["label"])

    def reperes(self) -> list[dict]:
        rows = self.q(Q.PREFIXES + "SELECT ?s WHERE { ?s a ex:SitePatrimonial ; geo:lat ?a }")
        return sorted(({"id": _id(r.s), "label": self.label(_id(r.s))} for r in rows), key=lambda x: x["label"])

    def equipements_catalogue(self, lang="fr") -> list[dict]:
        """Catégories (sous-classes d'Equipement) puis instances."""
        out = []
        for r in self.q(Q.PREFIXES + "SELECT ?c WHERE { ?c rdfs:subClassOf ex:Equipement }"):
            out.append({"id": _id(r.c), "label": "Tous : " + self.label(_id(r.c), lang), "categorie": True})
        rows = self.q(Q.PREFIXES + "SELECT ?e WHERE { ?e a ?c . ?c rdfs:subClassOf ex:Equipement }")
        out += [{"id": _id(r.e), "label": self.label(_id(r.e), lang), "categorie": False} for r in rows]
        return sorted(out, key=lambda x: (not x["categorie"], x["label"]))

    def vocabulaire(self, classe: str, lang="fr") -> list[dict]:
        rows = self.q(Q.PREFIXES + f"SELECT ?x WHERE {{ ?x a ex:{_check_id(classe)} }}")
        return sorted(({"id": _id(r.x), "label": self.label(_id(r.x), lang)} for r in rows),
                      key=lambda x: x["label"])

    # ---------- fiche et navigation ----------
    def avis(self, hid: str) -> list[dict]:
        hid = _check_id(hid)
        rows = self.q(Q.PREFIXES + f"""SELECT ?a ?note ?date ?com ?pr ?ac ?rq ?auteur WHERE {{
            ?a a ex:Avis ; ex:concerne ex:{hid} ; ex:note ?note .
            OPTIONAL {{ ?a ex:dateAvis ?date }} OPTIONAL {{ ?a ex:commentaire ?com }}
            OPTIONAL {{ ?a ex:noteProprete ?pr }} OPTIONAL {{ ?a ex:noteAccueil ?ac }}
            OPTIONAL {{ ?a ex:noteRapportQualitePrix ?rq }} OPTIONAL {{ ?a ex:redigePar ?auteur }} }}
            ORDER BY DESC(?date)""")
        out = []
        for r in rows:
            out.append({"id": _id(r.a), "note": int(r.note.toPython()),
                        "date": str(r.date) if r.date else "", "commentaire": str(r.com) if r.com else "",
                        "proprete": int(r.pr.toPython()) if r.pr else None,
                        "accueil": int(r.ac.toPython()) if r.ac else None,
                        "rqp": int(r.rq.toPython()) if r.rq else None,
                        "auteur": self.label(_id(r.auteur)) if r.auteur else "Anonyme"})
        return out

    def media(self, hid: str) -> list[dict]:
        hid = _check_id(hid)
        rows = self.q(Q.PREFIXES + f"SELECT ?m ?u WHERE {{ ?m ex:illustre ex:{hid} ; ex:urlMedia ?u }}")
        return [{"id": _id(r.m), "url": str(r.u), "alt": self.label(_id(r.m))} for r in rows]

    def hebergement(self, hid: str) -> dict | None:
        hid = _check_id(hid)
        rows = list(self.q(Q.PREFIXES + f"SELECT ?c WHERE {{ ex:{hid} ex:situeDans ?c }}"))
        if not rows:
            return None
        h = next((x for x in self.hebergements(_id(rows[0][0])) if x["id"] == hid), None)
        return h

    def proches(self, h: dict, n=3) -> list[dict]:
        from .scoring import haversine_km
        autres = [x for x in self.hebergements(h["commune"]) if x["id"] != h["id"]]
        for x in autres:
            x["_d"] = haversine_km(h["lat"], h["lon"], x["lat"], x["lon"])
        return sorted(autres, key=lambda x: x["_d"])[:n]

    def liens(self, rid: str, lang="fr") -> dict:
        """Liens typés : chaque propriété RDF devient un type de lien (section 7)."""
        rid = _check_id(rid)
        sortants, entrants = {}, {}
        for r in self.q(Q.PREFIXES + f"SELECT ?p ?o WHERE {{ ex:{rid} ?p ?o . FILTER(isIRI(?o)) }}"):
            p = _id(r.p)
            if p.startswith("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"):
                continue
            if str(r.o).startswith(NS):
                sortants.setdefault(self.label(p, lang), []).append({"id": _id(r.o), "label": self.label(_id(r.o), lang)})
        for r in self.q(Q.PREFIXES + f"SELECT ?s ?p WHERE {{ ?s ?p ex:{rid} . FILTER(isIRI(?s)) }}"):
            if str(r.s).startswith(NS) and str(r.p).startswith(NS):
                entrants.setdefault(self.label(_id(r.p), lang), []).append(
                    {"id": _id(r.s), "label": self.label(_id(r.s), lang)})
        return {"sortants": sortants, "entrants": entrants}

    def types(self, rid: str) -> list[str]:
        return [_id(t) for t in self.g.objects(EX[_check_id(rid)], RDF.type)]

    # ---------- exports ----------
    def description(self, hid: str) -> Graph:
        """Sous-graphe décrivant un hébergement (offres, médias, avis inclus) pour export."""
        hid = _check_id(hid)
        out = Graph()
        out.bind("ex", EX)
        out.bind("geo", GEO)
        h = EX[hid]
        noeuds = {h}
        noeuds |= set(self.g.objects(h, EX.aOffre))
        noeuds |= set(self.g.subjects(EX.illustre, h))
        noeuds |= set(self.g.subjects(EX.concerne, h))
        for n in noeuds:
            for t in self.g.triples((n, None, None)):
                out.add(t)
        for _, _, o in list(out):
            if isinstance(o, URIRef) and str(o).startswith(NS):
                for t in self.g.triples((o, RDFS.label, None)):
                    out.add(t)
        return out

    def sparql(self, texte: str):
        """Point d'accès en lecture seule : refuse SERVICE (pas de requêtes sortantes depuis le serveur)."""
        if re.search(r"\bSERVICE\b", texte, re.I):
            raise ValueError("SERVICE n'est pas autorisé sur ce point d'accès.")
        if len(texte) > 5000:
            raise ValueError("Requête trop longue.")
        return self.g.query(texte)   # .query() n'exécute jamais de mise à jour (SPARQL Update)
