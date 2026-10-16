"""Aides de test sans dépendance externe.

- mini_parse_turtle : parse le sous-ensemble de Turtle utilisé par data/*.ttl
  (préfixes, a, ;, ',', littéraux typés ou étiquetés). Sert à vérifier le jeu de données
  et à tester le moteur sans RDFlib.
- DictRepository : implémente l'interface attendue par recommend.py en Python pur ;
  son comportement doit rester identique à celui de repository.RdflibRepository.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
EX = "http://example.org/nord#"
RDF_TYPE = "rdf:type"

TOKEN = re.compile(r'''
    \s*(?:
      (?P<comment>\#[^\n]*)
    | (?P<str>"(?:[^"\\]|\\.)*")(?:@(?P<lang>[A-Za-z-]+)|\^\^(?P<dt>[A-Za-z]+:[A-Za-z]+))?
    | (?P<iri><[^>]*>)
    | (?P<punct>[;,.])
    | (?P<pname>@prefix|[A-Za-z@][\w\-]*:[\w\-\.]*[\w\-]|[A-Za-z@][\w\-]*:|a(?=\s))
    )''', re.X)


def mini_parse_turtle(text: str):
    prefixes, triples = {}, []
    pos, toks = 0, []
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m or m.end() == pos:
            if text[pos:].strip() == "":
                break
            raise ValueError(f"Jeton illisible près de : {text[pos:pos+60]!r}")
        pos = m.end()
        if m.group("comment"):
            continue
        if m.group("str") is not None:
            val = bytes(m.group("str")[1:-1], "utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8") \
                if "\\" in m.group("str") else m.group("str")[1:-1]
            toks.append(("lit", val, m.group("lang"), m.group("dt")))
        elif m.group("iri"):
            toks.append(("iri", m.group("iri")[1:-1]))
        elif m.group("punct"):
            toks.append(("p", m.group("punct")))
        else:
            toks.append(("n", m.group("pname")))
    # instructions
    i = 0
    stmt = []
    stmts = []
    while i < len(toks):
        t = toks[i]
        if t[0] == "p" and t[1] == ".":
            stmts.append(stmt)
            stmt = []
        else:
            stmt.append(t)
        i += 1

    def expand(tok):
        if tok[0] == "iri":
            return tok[1]
        if tok[0] == "lit":
            return ("lit", tok[1], tok[2], tok[3])
        name = tok[1]
        if name == "a":
            return RDF_TYPE
        pre, loc = name.split(":", 1)
        return prefixes.get(pre, pre + ":") + loc

    for s in stmts:
        if s and s[0] == ("n", "@prefix"):
            prefixes[s[1][1][:-1]] = s[2][1]
            continue
        subj = expand(s[0])
        j = 1
        pred = None
        expecting = "pred"
        while j < len(s):
            t = s[j]
            if t[0] == "p" and t[1] == ";":
                expecting = "pred"
            elif t[0] == "p" and t[1] == ",":
                expecting = "obj"
            elif expecting == "pred":
                pred = expand(t)
                expecting = "obj"
            else:
                triples.append((subj, pred, expand(t)))
            j += 1
    return triples


def load_triples():
    out = []
    for f in ("ontologie.ttl", "donnees.ttl"):
        out += mini_parse_turtle((DATA / f).read_text(encoding="utf-8"))
    return out


def short(uri):
    return uri.replace(EX, "") if isinstance(uri, str) else uri


class DictRepository:
    """Repository en Python pur construit depuis les triplets (jeu de données complet)."""

    def __init__(self, triples=None):
        self.t = triples if triples is not None else load_triples()
        self.by_s = defaultdict(lambda: defaultdict(list))
        for s, p, o in self.t:
            self.by_s[short(s)][short(p)].append(o)
        self._sub = {}
        for s, p, o in self.t:
            if short(p) == "rdfs:subClassOf" or p.endswith("subClassOf"):
                self._sub[short(s)] = short(o)
        self._mu = None
        self._cache = {}

    # -- utilitaires
    def objs(self, s, p):
        return [short(o) for o in self.by_s[s].get(short(p), [])]

    def lit(self, s, p):
        v = self.by_s[s].get(short(p), [])
        return v[0][1] if v else None

    def types(self, s):
        return [short(o) for o in self.by_s[s].get(RDF_TYPE, [])]

    def label(self, i, lang="fr"):
        ls = [o for o in self.by_s[i].get("http://www.w3.org/2000/01/rdf-schema#label", [])]
        for l in ls:
            if l[2] == lang:
                return l[1]
        return ls[0][1] if ls else i

    def sous_classes(self, cls):
        """Classes dont cls est ancêtre (reflexif), pour imiter rdfs:subClassOf*."""
        res = {cls}
        for c, parent in self._sub.items():
            x = c
            while x in self._sub:
                if self._sub[x] == cls:
                    res.add(c)
                    break
                x = self._sub[x]
        return res

    def est_de_type(self, s, cls):
        ts = set()
        for t in self.types(s):
            x = t
            ts.add(x)
            while x in self._sub:
                x = self._sub[x]
                ts.add(x)
        return cls in ts

    # -- interface du moteur
    def _heb_ids(self):
        return [s for s in self.by_s if self.est_de_type(s, "Hebergement")]

    def regle_affaires(self, h):
        return (self.lit(h, EX + "nombreEtoiles") and int(self.lit(h, EX + "nombreEtoiles")) >= 3
                and "Wifi" in self.objs(h, EX + "proposeEquipement")
                and any(self.est_de_type(e, "EquipementRestauration")
                        for e in self.objs(h, EX + "proposeEquipement")))

    def hebergements(self, commune):
        out = []
        for h in self._heb_ids():
            if self.objs(h, EX + "situeDans") != [commune]:
                continue
            offres = []
            for o in self.objs(h, EX + "aOffre"):
                tc = self.objs(o, EX + "typeChambre")[0]
                offres.append({"id": o, "type": tc, "type_label": self.label(tc),
                               "tarif": float(self.lit(o, EX + "tarifNuit")),
                               "capacite": int(self.lit(o, EX + "capacite"))})
            notes = [int(self.lit(a, EX + "note")) for a in self.by_s
                     if self.objs(a, EX + "concerne") == [h]]
            profils = set(self.objs(h, EX + "convientA"))
            if self.regle_affaires(h):
                profils.add("VoyageurAffaires")
            out.append({
                "id": h, "label": self.label(h), "classe": self.types(h)[0],
                "etoiles": int(self.lit(h, EX + "nombreEtoiles")),
                "lat": float(self.lit(h, "http://www.w3.org/2003/01/geo/wgs84_pos#lat")),
                "lon": float(self.lit(h, "http://www.w3.org/2003/01/geo/wgs84_pos#long")),
                "offres": offres, "equipements": self.objs(h, EX + "proposeEquipement"),
                "paiements": self.objs(h, EX + "accepteMode"), "profils": profils,
                "pmr": self.lit(h, EX + "accessiblePMR") == "true",
                "nb_avis": len(notes), "moyenne": (sum(notes) / len(notes)) if notes else None,
            })
        return out

    def eligibles(self, commune, budget, personnes, etoiles):
        res = {}
        for h in self.hebergements(commune):
            if h["etoiles"] < etoiles:
                continue
            ok = [o["tarif"] for o in h["offres"] if o["tarif"] <= budget and o["capacite"] >= personnes]
            if ok:
                res[h["id"]] = min(ok)
        return res

    def couverts(self, ids, souhaits):
        res = {}
        for h in ids:
            eq = self.objs(h, EX + "proposeEquipement")
            n = 0
            for s in souhaits:
                if any(e == s or self.est_de_type(e, s) for e in eq):
                    n += 1
            res[h] = n
        return res

    def mu(self):
        if self._mu is None:
            notes = [int(self.lit(a, EX + "note")) for a in self.by_s if EX + "Avis" in
                     [o if isinstance(o, str) else o for o in self.by_s[a].get(RDF_TYPE, [])]]
            self._mu = sum(notes) / len(notes)
        return self._mu

    def repere(self, rid):
        if rid not in self.by_s:
            return None
        return (float(self.lit(rid, "http://www.w3.org/2003/01/geo/wgs84_pos#lat")),
                float(self.lit(rid, "http://www.w3.org/2003/01/geo/wgs84_pos#long")),
                self.label(rid))
