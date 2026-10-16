#!/usr/bin/env python3
"""Génère data/donnees.ttl à partir des tableaux ci-dessous.

ATTENTION : les établissements, tarifs, coordonnées et avis ci-dessous sont
ILLUSTRATIFS (sauf la structure reprise du TD3). Remplacez-les par vos données
de terrain avant la soutenance : modifiez les tableaux puis relancez
    python scripts/build_data.py
ou éditez directement data/donnees.ttl (source de vérité).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "donnees.ttl"

COMMUNES = {
    "Garoua":  ("Garoua", 9.3014, 13.3977),
    "Guider":  ("Guider", 9.9333, 13.9500),
    "Lagdo":   ("Lagdo", 9.0500, 13.7167),
    "Pitoa":   ("Pitoa", 9.3833, 13.5333),
}
# Identifiants Wikidata à relever sur wikidata.org (voir README) : laissés vides
WIKIDATA = {"Garoua": None, "Guider": None, "Lagdo": None, "Pitoa": None, "Nord": None}

SITES = {
    "MarcheArtisanalGaroua": ("Marché artisanal de Garoua", "Garoua", 9.3050, 13.3950, 1998),
    "PontSurLaBenoue": ("Pont sur la Bénoué", "Garoua", 9.3090, 13.4060, None),
}

# id, label, classe, étoiles, chambres, année, commune, lat, long, exploitant(id, label, classe),
# équipements, paiements, profils explicites, PMR
HEB = [
    ("HotelLeBenoue", "Hôtel Le Bénoué", "Hotel", 4, 48, 2015, "Garoua", 9.3140, 13.3990,
     ("HotelNordSA", "HôtelNord SA", "Societe"),
     ["Restaurant", "Wifi", "Climatisation", "Piscine", "Parking", "PetitDejeuner"],
     ["MobileMoney", "Especes"], ["VoyageurCouple"], True),
    ("AubergeDeLaFalaise", "Auberge de la Falaise", "Auberge", 2, 12, None, "Garoua", 9.3000, 13.3990,
     ("CooperativeFalaise", "Coopérative Falaise", "Cooperative"),
     ["Wifi"], ["MobileMoney", "Especes"], ["VoyageurBudget"], False),
    ("ResidenceDuFleuve", "Résidence du Fleuve", "Hotel", 3, 30, 2012, "Garoua", 9.3200, 13.4100,
     ("FleuveHotellerie", "Fleuve Hôtellerie SARL", "Societe"),
     ["Restaurant", "Wifi", "Climatisation", "Bar"], ["MobileMoney", "CarteBancaire"],
     ["VoyageurCouple"], True),
    ("HotelSahelPlaza", "Hôtel Sahel Plaza", "Hotel", 3, 36, 2018, "Garoua", 9.3080, 13.3900,
     ("SahelGroupe", "Sahel Groupe SA", "Societe"),
     ["Restaurant", "Wifi", "Climatisation", "Parking"], ["MobileMoney", "Especes", "CarteBancaire"],
     ["VoyageurFamille"], False),
    ("HotelPanoramaGaroua", "Hôtel Panorama", "Hotel", 3, 24, 2010, "Garoua", 9.2950, 13.4050,
     ("PanoramaSARL", "Panorama SARL", "Societe"),
     ["Restaurant", "Climatisation", "Bar"], ["Especes", "MobileMoney"],
     ["VoyageurFamille", "VoyageurCouple"], False),
    ("ResidenceEtoileDuNord", "Résidence Étoile du Nord", "Hotel", 2, 20, 2016, "Garoua", 9.3100, 13.3850,
     ("EtoileNordSARL", "Étoile du Nord SARL", "Societe"),
     ["Wifi", "Climatisation"], ["MobileMoney", "Especes"], ["VoyageurBudget"], False),
    ("AubergeDuMarche", "Auberge du Marché", "Auberge", 2, 10, None, "Garoua", 9.3045, 13.3955,
     ("CoopMarche", "Coopérative des artisans", "Cooperative"),
     ["PetitDejeuner", "Wifi"], ["Especes", "MobileMoney"], ["VoyageurBudget"], False),
    ("AubergeKarite", "Auberge Karité", "Auberge", 1, 8, None, "Garoua", 9.2900, 13.3800,
     ("CoopKarite", "Coopérative Karité", "Cooperative"),
     [], ["Especes"], ["VoyageurBudget"], False),
    ("HotelAmbassadeurGaroua", "Hôtel Ambassadeur", "Hotel", 4, 60, 2019, "Garoua", 9.3170, 13.3930,
     ("AmbassadeurHoldings", "Ambassadeur Holdings SA", "Societe"),
     ["Restaurant", "Wifi", "Climatisation", "Piscine", "Parking", "Bar", "Groupe"],
     ["MobileMoney", "CarteBancaire", "Especes"], ["VoyageurCouple"], True),
    ("HotelLaBenoueVue", "Hôtel La Vue du Fleuve", "Hotel", 3, 28, 2014, "Garoua", 9.3230, 13.4020,
     ("VueFleuveSARL", "Vue du Fleuve SARL", "Societe"),
     ["Restaurant", "Wifi", "PetitDejeuner", "Parking"], ["MobileMoney", "Especes"],
     ["VoyageurFamille"], False),
    ("AubergeAcacia", "Auberge de l'Acacia", "Auberge", 2, 14, None, "Garoua", 9.2980, 13.4120,
     ("CoopAcacia", "Coopérative Acacia", "Cooperative"),
     ["Wifi", "Climatisation"], ["MobileMoney", "Especes"], ["VoyageurBudget", "VoyageurCouple"], False),
    ("ResidenceLesPalmiers", "Résidence Les Palmiers", "Hotel", 3, 22, 2013, "Garoua", 9.3260, 13.3880,
     ("PalmiersSARL", "Palmiers SARL", "Societe"),
     ["Wifi", "Climatisation", "Restaurant"], ["MobileMoney"], ["VoyageurCouple"], False),
    ("HotelGuiderCentre", "Hôtel de Guider Centre", "Hotel", 2, 18, 2011, "Guider", 9.9340, 13.9490,
     ("GuiderHotelSARL", "Guider Hôtel SARL", "Societe"),
     ["Restaurant", "Climatisation"], ["Especes", "MobileMoney"], ["VoyageurFamille"], False),
    ("AubergeGuiderSahel", "Auberge Sahel de Guider", "Auberge", 1, 9, None, "Guider", 9.9300, 13.9540,
     ("CoopGuider", "Coopérative de Guider", "Cooperative"),
     ["PetitDejeuner"], ["Especes"], ["VoyageurBudget"], False),
    ("HotelLagdoLac", "Hôtel du Lac de Lagdo", "Hotel", 3, 26, 2017, "Lagdo", 9.0510, 13.7160,
     ("LacLagdoSARL", "Lac de Lagdo SARL", "Societe"),
     ["Restaurant", "Wifi", "Climatisation", "Piscine", "Bar"], ["MobileMoney", "Especes"],
     ["VoyageurCouple", "VoyageurFamille"], False),
    ("AubergePitoaRoute", "Auberge de la Route de Pitoa", "Auberge", 2, 11, None, "Pitoa", 9.3830, 13.5340,
     ("CoopPitoa", "Coopérative de Pitoa", "Cooperative"),
     ["Wifi", "Restaurant"], ["Especes", "MobileMoney"], ["VoyageurBudget"], False),
]

# hébergement -> liste d'offres (type, tarif FCFA, capacité)
OFFRES = {
    "HotelLeBenoue": [("ChambreSimple", 38000, 1), ("ChambreDouble", 45000, 2),
                      ("ChambreFamiliale", 70000, 4), ("Suite", 95000, 2)],
    "AubergeDeLaFalaise": [("ChambreSimple", 12000, 1), ("ChambreDouble", 18000, 2)],
    "ResidenceDuFleuve": [("ChambreDouble", 62000, 2), ("Suite", 110000, 3)],
    "HotelSahelPlaza": [("ChambreSimple", 30000, 1), ("ChambreDouble", 42000, 2),
                        ("ChambreFamiliale", 65000, 4)],
    "HotelPanoramaGaroua": [("ChambreDouble", 35000, 2), ("ChambreFamiliale", 55000, 4)],
    "ResidenceEtoileDuNord": [("ChambreSimple", 15000, 1), ("ChambreDouble", 22000, 2)],
    "AubergeDuMarche": [("ChambreSimple", 9000, 1), ("ChambreDouble", 14000, 2)],
    "AubergeKarite": [("ChambreSimple", 6000, 1), ("ChambreDouble", 9000, 2)],
    "HotelAmbassadeurGaroua": [("ChambreDouble", 75000, 2), ("Suite", 140000, 3),
                               ("ChambreFamiliale", 110000, 4)],
    "HotelLaBenoueVue": [("ChambreDouble", 40000, 2), ("ChambreFamiliale", 60000, 4)],
    "AubergeAcacia": [("ChambreSimple", 11000, 1), ("ChambreDouble", 16000, 2)],
    "ResidenceLesPalmiers": [("ChambreDouble", 38000, 2)],
    "HotelGuiderCentre": [("ChambreDouble", 20000, 2), ("ChambreFamiliale", 32000, 4)],
    "AubergeGuiderSahel": [("ChambreSimple", 7000, 1)],
    "HotelLagdoLac": [("ChambreDouble", 36000, 2), ("ChambreFamiliale", 52000, 4)],
    "AubergePitoaRoute": [("ChambreDouble", 13000, 2)],
}

# hébergement -> liste d'avis : (note, propreté, accueil, rapport qualité/prix, date, commentaire, pseudo)
AVIS = {
    "HotelLeBenoue": [
        (4, 4, 5, 3, "2025-11-12", "Accueil chaleureux.", "Aicha"),
        (5, 5, 5, 4, "2026-01-20", "Séjour d'affaires parfait, wifi stable.", "Hamadou"),
        (4, 4, 4, 3, "2026-03-08", "Chambre confortable, restaurant correct.", "Clarisse"),
        (4, 5, 4, 3, "2026-05-02", "Très propre, un peu cher.", "Yaya"),
    ],
    "AubergeDeLaFalaise": [
        (4, 4, 5, 5, "2026-02-14", "Simple et bien tenue, super prix.", "Moussa"),
        (3, 3, 4, 4, "2026-04-10", "Correct pour une nuit.", "Fadimatou"),
    ],
    "ResidenceDuFleuve": [
        (4, 4, 4, 3, "2026-01-05", "Belle vue sur le fleuve.", "Ibrahim"),
        (4, 4, 3, 3, "2026-02-27", "Calme, personnel discret.", "Salamatou"),
        (3, 3, 3, 2, "2026-05-19", "Prix élevé pour le service.", "Joël"),
    ],
    "HotelSahelPlaza": [
        (4, 4, 4, 4, "2025-12-02", "Bon rapport qualité-prix.", "Abdou"),
        (4, 4, 5, 4, "2026-02-11", "Parfait pour une famille.", "Mariam"),
        (3, 3, 3, 3, "2026-04-23", "Climatisation bruyante.", "Paul"),
    ],
    "HotelPanoramaGaroua": [
        (3, 3, 4, 4, "2025-10-30", "Ambiance conviviale.", "Aissatou"),
        (4, 4, 4, 4, "2026-03-15", "Bon restaurant.", "Boubakari"),
    ],
    "ResidenceEtoileDuNord": [
        (3, 3, 3, 4, "2026-01-18", "Propre, wifi lent.", "Nafissatou"),
        (4, 4, 4, 5, "2026-03-29", "Très bon prix.", "Samuel"),
        (3, 3, 4, 4, "2026-05-30", "Correct.", "Rakia"),
    ],
    "AubergeDuMarche": [
        (3, 3, 4, 4, "2026-02-03", "Bien placée près du marché.", "Oumarou"),
        (4, 4, 5, 5, "2026-04-17", "Accueil très aimable.", "Hadjara"),
    ],
    "AubergeKarite": [
        (2, 2, 3, 3, "2026-01-26", "Très basique.", "Daouda"),
        (3, 2, 4, 4, "2026-03-03", "Prix bas, accueil sympathique.", "Esther"),
    ],
    "HotelAmbassadeurGaroua": [
        (5, 5, 5, 3, "2025-12-21", "Excellent établissement.", "Alioum"),
        (5, 5, 4, 3, "2026-02-09", "Piscine et service de qualité.", "Danielle"),
        (4, 4, 4, 3, "2026-04-04", "Très bien, mais cher.", "Mahamat"),
        (5, 5, 5, 4, "2026-06-12", "Notre meilleur séjour.", "Zenabou"),
    ],
    "HotelLaBenoueVue": [
        (4, 4, 4, 4, "2026-01-30", "Bon petit-déjeuner, vue agréable.", "Haman"),
        (4, 4, 5, 4, "2026-03-22", "Personnel attentionné.", "Bernadette"),
        (3, 3, 3, 3, "2026-05-14", "Wifi capricieux.", "Idrissou"),
    ],
    "AubergeAcacia": [
        (3, 3, 4, 4, "2026-02-19", "Tranquille.", "Pauline"),
        (4, 4, 4, 5, "2026-04-26", "Bon pour un couple à petit budget.", "Sali"),
    ],
    "ResidenceLesPalmiers": [
        (4, 4, 4, 4, "2026-02-08", "Calme et confortable.", "Ngo"),
        (5, 5, 5, 4, "2026-04-14", "Très agréable pour un week-end.", "Fanta"),
        (4, 4, 4, 3, "2026-06-01", "Bon séjour.", "Adamou"),
    ],
    "HotelGuiderCentre": [
        (3, 3, 4, 4, "2026-01-12", "Simple mais propre.", "Kaigama"),
        (4, 4, 4, 4, "2026-03-27", "Restaurant familial agréable.", "Rose"),
    ],
    "AubergeGuiderSahel": [
        (2, 3, 3, 3, "2026-02-22", "Basique.", "Bello"),
    ],
    "HotelLagdoLac": [
        (4, 4, 4, 3, "2026-01-09", "Vue sur le lac, très calme.", "Carine"),
        (5, 5, 5, 4, "2026-03-05", "Parfait pour se détendre.", "Gilbert"),
        (4, 4, 4, 4, "2026-05-25", "Piscine agréable.", "Hawa"),
    ],
    "AubergePitoaRoute": [
        (3, 3, 4, 4, "2026-02-16", "Étape pratique sur la route.", "Tidjani"),
    ],
}


TYPES = {"ChambreSimple": "Chambre simple", "ChambreDouble": "Chambre double",
         "ChambreFamiliale": "Chambre familiale", "Suite": "Suite"}


def lit(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def main():
    L = []
    w = L.append
    w("""@prefix ex:   <http://example.org/nord#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix geo:  <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix dct:  <http://purl.org/dc/terms/> .

# DONNÉES ILLUSTRATIVES - à remplacer par les données collectées sur le terrain.
# Fichier généré par scripts/build_data.py (peut aussi être édité à la main).
""")
    w('ex:Nord a ex:Region ; rdfs:label "Nord"@fr .\n')
    for cid, (lab, lat, lon) in COMMUNES.items():
        w(f'ex:{cid} a ex:Commune ; rdfs:label "{lab}"@fr ; ex:partieDe ex:Nord ;\n'
          f'    geo:lat "{lat}"^^xsd:decimal ; geo:long "{lon}"^^xsd:decimal .')
    w("")
    for sid, (lab, com, lat, lon, annee) in SITES.items():
        s = (f'ex:{sid} a ex:SitePatrimonial ; rdfs:label "{lab}"@fr ; ex:situeDans ex:{com} ;\n'
             f'    geo:lat "{lat}"^^xsd:decimal ; geo:long "{lon}"^^xsd:decimal')
        if annee:
            s += f' ;\n    ex:anneeClassement "{annee}"^^xsd:gYear'
        if sid == "MarcheArtisanalGaroua":
            s += " ;\n    ex:proposeVisite ex:VisiteMarche"
        w(s + " .")
    w('\nex:VisiteMarche a ex:VisiteGuidee ; ex:langueVisite ex:Francais , ex:Fulfulde .')
    w('ex:Francais a ex:Langue ; rdfs:label "français"@fr .')
    w('ex:Fulfulde a ex:Langue ; rdfs:label "fulfulde"@fr .\n')

    exploitants = {}
    for h in HEB:
        eid, elab, ecls = h[9]
        exploitants[eid] = (elab, ecls)
    for eid, (elab, ecls) in exploitants.items():
        w(f'ex:{eid} a ex:{ecls} ; rdfs:label "{lit(elab)}"@fr .')
    w("")

    n_offres = n_avis = 0
    pseudos = {}
    for (hid, lab, cls, et, ch, an, com, lat, lon, expl, equips, pays, profs, pmr) in HEB:
        lines = [f'ex:{hid} a ex:{cls} ;', f'    rdfs:label "{lit(lab)}"@fr ;',
                 f'    ex:nombreEtoiles "{et}"^^xsd:integer ;',
                 f'    ex:nombreChambres "{ch}"^^xsd:integer ;']
        if an:
            lines.append(f'    ex:anneeOuverture "{an}"^^xsd:gYear ;')
        lines += [f'    ex:situeDans ex:{com} ;', f'    ex:exploitePar ex:{expl[0]} ;',
                  f'    geo:lat "{lat}"^^xsd:decimal ; geo:long "{lon}"^^xsd:decimal ;',
                  f'    ex:accessiblePMR "{str(pmr).lower()}"^^xsd:boolean ;']
        if equips:
            lines.append("    ex:proposeEquipement " + " , ".join(f"ex:{e}" for e in equips) + " ;")
        lines.append("    ex:accepteMode " + " , ".join(f"ex:{p}" for p in pays) + " ;")
        if profs:
            lines.append("    ex:convientA " + " , ".join(f"ex:{p}" for p in profs) + " ;")
        offs = []
        for i, (t, tarif, cap) in enumerate(OFFRES[hid], 1):
            offs.append(f"ex:Offre{hid}{i:02d}")
        lines.append("    ex:aOffre " + " , ".join(offs) + " ;")
        lines.append('    dct:source "Données illustratives (à remplacer par la collecte terrain)"@fr ;')
        lines.append('    dct:modified "2026-10-01"^^xsd:date .')
        w("\n".join(lines))
        w("")
        for i, (t, tarif, cap) in enumerate(OFFRES[hid], 1):
            n_offres += 1
            w(f'ex:Offre{hid}{i:02d} a ex:Offre ; ex:typeChambre ex:{t} ;\n'
              f'    rdfs:label "{TYPES[t]} - {lit(lab)}"@fr ;\n'
              f'    ex:tarifNuit "{tarif}"^^xsd:decimal ; ex:capacite "{cap}"^^xsd:integer .')
        w("")
        w(f'ex:Media{hid} a ex:Media ; ex:illustre ex:{hid} ;\n'
          f'    ex:urlMedia "/static/img/placeholder-{"hotel" if cls == "Hotel" else "auberge"}.svg"^^xsd:anyURI ;\n'
          f'    rdfs:label "Photo de {lit(lab)}"@fr .')
        w("")
        for j, (note, pr, ac, rq, date, com_, pseudo) in enumerate(AVIS.get(hid, []), 1):
            n_avis += 1
            pid = "Visiteur" + pseudo
            pseudos[pid] = pseudo
            w(f'ex:avis{n_avis:03d} a ex:Avis ; rdfs:label "Avis {n_avis:03d}"@fr ;\n'
              f'    ex:concerne ex:{hid} ; ex:redigePar ex:{pid} ;\n'
              f'    ex:dateAvis "{date}"^^xsd:date ; ex:note "{note}"^^xsd:integer ;\n'
              f'    ex:noteProprete "{pr}"^^xsd:integer ; ex:noteAccueil "{ac}"^^xsd:integer ;\n'
              f'    ex:noteRapportQualitePrix "{rq}"^^xsd:integer ;\n'
              f'    ex:commentaire "{lit(com_)}"@fr .')
        w("")
    for pid, p in sorted(pseudos.items()):
        w(f'ex:{pid} a ex:Visiteur ; rdfs:label "{lit(p)}"@fr .')
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{OUT}: {len(HEB)} hébergements, {n_offres} offres, {n_avis} avis")


if __name__ == "__main__":
    main()
