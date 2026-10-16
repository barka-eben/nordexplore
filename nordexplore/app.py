"""Application web NordExplore (Flask + Jinja2) - voir dossier de conception, sections 5 et 7."""
from __future__ import annotations

import json
import os
from pathlib import Path

from flask import (Flask, Response, abort, jsonify, make_response, redirect, render_template,
                   request, url_for)

from . import queries as Q
from . import scoring as sc
from .evaluation import SCENARIOS, evaluer
from .recommend import Requete, propositions_assouplissement, recommander, tri_par_etoiles
from .repository import EX, RdflibRepository, charger_graphe

RACINE = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("NORDEXPLORE_DATA", RACINE / "data"))

UI = {
    "fr": {"accueil": "Accueil", "preferences": "Préférences", "carte": "Carte", "donnees": "Données",
           "evaluation": "Évaluation", "meilleurs": "Les mieux notés", "rechercher": "Rechercher",
           "ecartes": "Hébergements écartés", "comparer": "Comparer la sélection",
           "tarif_indicatif": "Tarifs indicatifs en FCFA, susceptibles de changer."},
    "en": {"accueil": "Home", "preferences": "Preferences", "carte": "Map", "donnees": "Data",
           "evaluation": "Evaluation", "meilleurs": "Top rated", "rechercher": "Search",
           "ecartes": "Excluded lodgings", "comparer": "Compare selection",
           "tarif_indicatif": "Indicative prices in FCFA, subject to change."},
}


def create_app(data_dir: Path | None = None, config: dict | None = None) -> Flask:
    app = Flask(__name__)
    cfg = config or sc.charger_config()
    graphe = charger_graphe(data_dir or DATA_DIR, cfg.get("activer_owlrl", False))
    repo = RdflibRepository(graphe)
    app.config["REPO"] = repo
    app.config["CFG"] = cfg

    def lang() -> str:
        l = request.cookies.get("lang", "fr")
        return l if l in UI else "fr"

    def lien(rid: str) -> str:
        """Fiche détaillée pour un hébergement, page générique de ressource sinon."""
        try:
            if set(repo.types(rid)) & {"Hotel", "Auberge"}:
                return url_for("fiche", hid=rid)
        except ValueError:
            pass
        return url_for("ressource", rid=rid)

    @app.context_processor
    def ctx():
        return {"t": UI[lang()], "lang": lang(), "repo": repo, "lien": lien}

    # ------------------------------------------------------------ requête utilisateur
    def lire_requete(args) -> Requete:
        communes = {c["id"] for c in repo.communes()}
        eqs = {e["id"] for e in repo.equipements_catalogue()}
        profils = {p["id"] for p in repo.vocabulaire("ProfilVoyageur")}
        modes = {p["id"] for p in repo.vocabulaire("ModePaiement")}
        reperes = {p["id"] for p in repo.reperes()}

        def entier(nom, defaut, lo, hi):
            try:
                return max(lo, min(hi, int(float(args.get(nom, defaut)))))
            except (TypeError, ValueError):
                return defaut

        commune = args.get("commune", "Garoua")
        if commune not in communes:
            commune = "Garoua" if "Garoua" in communes else sorted(communes)[0]
        return Requete(
            commune=commune,
            budget=entier("budget", 50000, 1000, 5_000_000),
            personnes=entier("personnes", 2, 1, 12),
            etoiles_min=entier("etoiles", 1, 1, 5),
            equipements=[e for e in args.getlist("equipements") if e in eqs],
            profil=args.get("profil") if args.get("profil") in profils else None,
            paiement=args.get("paiement") if args.get("paiement") in modes else None,
            pmr=args.get("pmr") == "1",
            repere=args.get("repere") if args.get("repere") in reperes else None,
        )

    def formulaire_donnees():
        l = lang()
        return {"communes": repo.communes(), "equipements": repo.equipements_catalogue(l),
                "profils": repo.vocabulaire("ProfilVoyageur", l),
                "modes": repo.vocabulaire("ModePaiement", l), "reperes": repo.reperes()}

    # ------------------------------------------------------------ pages
    @app.route("/")
    def accueil():
        tous = []
        for c in repo.communes():
            tous += repo.hebergements(c["id"])
        top = sorted((h for h in tous if h["nb_avis"] >= 2),
                     key=lambda h: (-sc.moyenne_lissee(h["nb_avis"], h["moyenne"], repo.mu()), h["label"]))[:5]
        return render_template("accueil.html", top=top, nb=len(tous), mu=repo.mu())

    @app.route("/preferences")
    def preferences():
        q = lire_requete(request.args)
        return render_template("preferences.html", q=q, **formulaire_donnees())

    @app.route("/resultats")
    def resultats():
        q = lire_requete(request.args)
        r = recommander(repo, q, cfg, lang())
        alternatives = [] if r["resultats"] else propositions_assouplissement(repo, q, cfg)
        return render_template("resultats.html", q=q, r=r, alternatives=alternatives,
                               poids=cfg["poids"], criteres=sc.CRITERES, args=request.args,
                               **formulaire_donnees())

    @app.route("/hebergement/<hid>.html")
    def fiche(hid):
        try:
            h = repo.hebergement(hid)
        except ValueError:
            abort(404)
        if not h:
            abort(404)
        avis = repo.avis(hid)
        eq = [{"id": e, "label": repo.label(e, lang())} for e in h["equipements"]]
        pay = [{"id": p, "label": repo.label(p, lang())} for p in h["paiements"]]
        prof = [{"id": p, "label": repo.label(p, lang())} for p in sorted(h["profils"])]
        moyennes = {}
        for cle in ("proprete", "accueil", "rqp"):
            vals = [a[cle] for a in avis if a[cle] is not None]
            moyennes[cle] = round(sum(vals) / len(vals), 2) if vals else None
        jsonld = {
            "@context": "https://schema.org", "@type": "Hotel", "name": h["label"],
            "url": request.url_root.rstrip("/") + f"/hebergement/{hid}.html",
            "starRating": {"@type": "Rating", "ratingValue": h["etoiles"]},
            "geo": {"@type": "GeoCoordinates", "latitude": h["lat"], "longitude": h["lon"]},
            "address": {"@type": "PostalAddress", "addressLocality": repo.label(h["commune"]),
                        "addressCountry": "CM"},
            "priceRange": f"{int(min(o['tarif'] for o in h['offres']))}-{int(max(o['tarif'] for o in h['offres']))} XAF",
            "paymentAccepted": ", ".join(p["label"] for p in pay),
            "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": e["label"], "value": True} for e in eq],
        }
        if h["nb_avis"]:
            jsonld["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": round(h["moyenne"], 2),
                                         "reviewCount": h["nb_avis"], "bestRating": 5}
        return render_template("fiche.html", h=h, avis=avis, eq=eq, pay=pay, prof=prof, moyennes=moyennes,
                               liens=repo.liens(hid, lang()), proches=repo.proches(h),
                               media=repo.media(hid), jsonld=jsonld,
                               offres=sorted(h["offres"], key=lambda o: o["tarif"]))

    @app.route("/hebergement/<hid>.ttl")
    def export_ttl(hid):
        try:
            g = repo.description(hid)
        except ValueError:
            abort(404)
        if not len(g):
            abort(404)
        return Response(g.serialize(format="turtle"), mimetype="text/turtle")

    @app.route("/hebergement/<hid>.jsonld")
    def export_jsonld(hid):
        try:
            g = repo.description(hid)
        except ValueError:
            abort(404)
        if not len(g):
            abort(404)
        return Response(g.serialize(format="json-ld", indent=2), mimetype="application/ld+json")

    @app.route("/ressource/<rid>")
    def ressource(rid):
        try:
            liens = repo.liens(rid, lang())
            types = repo.types(rid)
        except ValueError:
            abort(404)
        if not types:
            abort(404)
        return render_template("ressource.html", rid=rid, label=repo.label(rid, lang()),
                               types=[repo.label(t, lang()) for t in types], liens=liens)

    @app.route("/carte")
    def carte():
        q = lire_requete(request.args)
        return render_template("carte.html", q=q, args=request.args, **formulaire_donnees())

    @app.route("/api/resultats.json")
    def api_resultats():
        q = lire_requete(request.args)
        r = recommander(repo, q, cfg, lang())
        return jsonify({
            "requete": q.__dict__,
            "resultats": [{"id": x["hebergement"]["id"], "nom": x["hebergement"]["label"],
                           "etoiles": x["hebergement"]["etoiles"], "lat": x["hebergement"]["lat"],
                           "lon": x["hebergement"]["lon"], "score": x["score"], "rang": x["rang"],
                           "tarif": x["offre"]["tarif"], "explication": x["explication"],
                           "url": url_for("fiche", hid=x["hebergement"]["id"])} for x in r["resultats"]],
            "ecartes": [{"id": e["hebergement"]["id"], "nom": e["hebergement"]["label"],
                         "motifs": e["motifs"]} for e in r["ecartes"]],
        })

    @app.route("/comparer")
    def comparer():
        ids = [i for i in request.args.getlist("ids") if i][:3]
        hs = []
        for i in ids:
            try:
                h = repo.hebergement(i)
            except ValueError:
                h = None
            if h:
                hs.append(h)
        if len(hs) < 2:
            return render_template("comparer.html", hs=[], erreur=True)
        return render_template("comparer.html", hs=hs, erreur=False)

    @app.route("/donnees")
    def donnees():
        demos = []
        for titre, texte in Q.DEMOS.items():
            demos.append({"titre": titre, "texte": texte.strip()})
        return render_template("donnees.html", demos=demos,
                               fichiers=[f for f in ("ontologie.ttl", "donnees.ttl") if (DATA_DIR / f).exists()],
                               nb_triplets=len(graphe))

    @app.route("/telecharger/<nom>")
    def telecharger(nom):
        if nom not in ("ontologie.ttl", "donnees.ttl"):
            abort(404)
        return Response((DATA_DIR / nom).read_text(encoding="utf-8"), mimetype="text/turtle",
                        headers={"Content-Disposition": f"attachment; filename={nom}"})

    @app.route("/evaluation")
    def evaluation():
        return render_template("evaluation.html", ev=evaluer(repo, cfg), scenarios=SCENARIOS, poids=cfg["poids"])

    @app.route("/sparql", methods=["GET", "POST"])
    def sparql():
        texte = request.values.get("query", "")
        if not texte:
            return render_template("sparql.html", exemple=Q.DEMOS[next(iter(Q.DEMOS))].strip())
        try:
            res = repo.sparql(texte)
        except Exception as e:  # requête invalide ou interdite
            return Response(f"Erreur : {e}", status=400, mimetype="text/plain")
        if res.type in ("SELECT", "ASK"):
            return Response(res.serialize(format="json"), mimetype="application/sparql-results+json")
        return Response(res.serialize(format="turtle"), mimetype="text/turtle")

    @app.route("/langue/<code>")
    def changer_langue(code):
        rep = make_response(redirect(request.referrer or url_for("accueil")))
        if code in UI:
            rep.set_cookie("lang", code, max_age=60 * 60 * 24 * 365, samesite="Lax")
        return rep

    @app.errorhandler(404)
    def introuvable(_):
        return render_template("404.html"), 404

    return app


def main():
    app = create_app()
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 5000)), debug=False)


if __name__ == "__main__":
    main()
