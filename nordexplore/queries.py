"""Requêtes SPARQL du projet (dossier de conception, section 6.4 et 4.5).

R1 à R6 : requêtes fonctionnelles. C1 à C4 : contrôles qualité (section 4.5).
Les requêtes paramétrées (R1, R2) sont construites par repository.py avec des valeurs validées.
"""

PREFIXES = """PREFIX ex:   <http://example.org/nord#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX geo:  <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX dct:  <http://purl.org/dc/terms/>
"""

# R1 - Filtrage dur : offres compatibles (budget, capacité, étoiles)
R1 = PREFIXES + """
SELECT ?h (MIN(?tarif) AS ?tarifMin) WHERE {
  ?h a ?t . ?t rdfs:subClassOf* ex:Hebergement .
  ?h ex:situeDans ex:%(commune)s ;
     ex:nombreEtoiles ?etoiles ; ex:aOffre ?o .
  ?o ex:tarifNuit ?tarif ; ex:capacite ?cap .
  FILTER(?etoiles >= %(etoiles)d && ?tarif <= %(budget)s && ?cap >= %(personnes)d)
} GROUP BY ?h
"""

# R2 - Équipements souhaités couverts (instances ou catégories, via les sous-classes)
R2 = PREFIXES + """
SELECT ?h (COUNT(DISTINCT ?souhait) AS ?couverts) WHERE {
  VALUES ?h { %(hebergements)s }
  VALUES ?souhait { %(souhaits)s }
  { ?h ex:proposeEquipement ?souhait }
  UNION
  { ?h ex:proposeEquipement ?e . ?e a/rdfs:subClassOf* ?souhait }
} GROUP BY ?h
"""

# R3 - Note moyenne et nombre d'avis
R3 = PREFIXES + """
SELECT ?h (AVG(?note) AS ?moyenne) (COUNT(?a) AS ?nbAvis) WHERE {
  ?a a ex:Avis ; ex:concerne ?h ; ex:note ?note .
} GROUP BY ?h
"""

# R4 - Règle : hébergement adapté aux voyageurs d'affaires (appliquée au chargement)
R4 = PREFIXES + """
CONSTRUCT { ?h ex:convientA ex:VoyageurAffaires } WHERE {
  ?h ex:nombreEtoiles ?e ; ex:proposeEquipement ex:Wifi ; ex:proposeEquipement ?r .
  ?r a ex:EquipementRestauration . FILTER(?e >= 3)
}
"""

# R5 - Vérification d'un mode de paiement
R5 = PREFIXES + """
ASK { ex:HotelLeBenoue ex:accepteMode ex:MobileMoney }
"""

# R6 - Enrichissement optionnel via Wikidata (nécessite des owl:sameAs et le réseau)
R6 = PREFIXES + """
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT ?commune ?population WHERE {
  ?c a ex:Commune ; rdfs:label ?commune ; owl:sameAs ?wd .
  SERVICE <https://query.wikidata.org/sparql> { ?wd wdt:P1082 ?population . }
}
"""

# Contrôles qualité (section 4.5) : chaque requête doit renvoyer 0 ligne
C1 = PREFIXES + """
# Ressource de l'espace ex: sans type
SELECT ?s WHERE {
  ?s ?p ?o . FILTER(STRSTARTS(STR(?s), "http://example.org/nord#"))
  FILTER NOT EXISTS { ?s a ?t }
}
"""
C2 = PREFIXES + """
# Ressource typée sans libellé (hors visites et propriétés/classes de l'ontologie)
SELECT DISTINCT ?s WHERE {
  ?s a ?t . FILTER(STRSTARTS(STR(?s), "http://example.org/nord#"))
  FILTER(?t NOT IN (owl:Class, owl:ObjectProperty, owl:DatatypeProperty, owl:FunctionalProperty,
                    ex:VisiteGuidee))
  FILTER NOT EXISTS { ?s rdfs:label ?l }
}
"""
C3 = PREFIXES + """
# Hébergement sans commune
SELECT ?h WHERE {
  VALUES ?c { ex:Hotel ex:Auberge } ?h a ?c .
  FILTER NOT EXISTS { ?h ex:situeDans ?x }
}
"""
C4 = PREFIXES + """
# Hébergement sans offre
SELECT ?h WHERE {
  VALUES ?c { ex:Hotel ex:Auberge } ?h a ?c .
  FILTER NOT EXISTS { ?h ex:aOffre ?o }
}
"""

# Requêtes de démonstration affichées sur la page « Données » (sans paramètres)
DEMOS = {
    "R1 - Hébergements de Garoua à moins de 50 000 FCFA pour 2 personnes (2★ min)":
        R1 % {"commune": "Garoua", "etoiles": 2, "budget": "50000", "personnes": 2},
    "R2 - Équipements couverts (Wifi + catégorie Restauration)":
        R2 % {"hebergements": "ex:HotelLeBenoue ex:AubergeDeLaFalaise",
              "souhaits": "ex:Wifi ex:EquipementRestauration"},
    "R3 - Note moyenne et nombre d'avis par hébergement": R3,
    "R4 - Règle CONSTRUCT : hébergements pour voyageurs d'affaires": R4,
    "R5 - ASK : Le Bénoué accepte-t-il Mobile Money ?": R5,
}
