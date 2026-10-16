# NordExplore – Prototype fonctionnel (livrable 2/5)

Système de recommandation sémantique d'hébergements dans la région du Nord (Cameroun).
IBAI – Université de Garoua · M1 Art et Intelligence Artificielle · UE Hypermédia et Web sémantique (IBAI4172) · Module 3.3.

Ce prototype met en œuvre le dossier de conception v2.0 : jeu de données RDF/OWL, requêtes SPARQL, moteur de recommandation explicable et interface hypermédia (Flask).

## Démarrage rapide

```bash
python3 -m venv .venv && source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt
./run.sh                                                 # Windows : run.bat
# puis ouvrir http://127.0.0.1:5000
```

Tests et contrôles :

```bash
python3 -m unittest discover -s tests -t . -v   # 38 tests (28 sans RDFlib, 10 avec)
python3 scripts/controle_qualite.py             # requêtes SPARQL de contrôle C1 à C4
python3 scripts/evaluer.py                      # évaluation sur 5 scénarios
```

## Contenu

| Chemin | Rôle |
|---|---|
| `data/ontologie.ttl` | Ontologie : 24 classes (16 du TD3 + 8 pour l'hôtellerie), propriétés, axiomes OWL, vocabulaires contrôlés |
| `data/donnees.ttl` | Instances : 16 hébergements, 33 offres, 40 avis (**données illustratives**) |
| `scripts/build_data.py` | Régénère `donnees.ttl` depuis des tableaux Python (ou éditez le Turtle à la main) |
| `nordexplore/scoring.py` | Formules de score (Python pur) |
| `nordexplore/recommend.py` | Pipeline : filtrage dur → enrichissement → score → explication ; écartés avec motifs ; assouplissement |
| `nordexplore/repository.py` | Accès RDFlib : chargement, règle CONSTRUCT R4, requêtes SPARQL |
| `nordexplore/queries.py` | Requêtes R1–R6 du dossier et contrôles C1–C4 |
| `nordexplore/app.py` | Routes Flask, API JSON, exports Turtle / JSON-LD, point d'accès `/sparql` |
| `nordexplore/config.json` | Poids des critères et paramètres (lissage, rayon de proximité) |
| `nordexplore/evaluation.py` | Cinq scénarios et comparaison au tri par étoiles |
| `tests/` | Tests unitaires ; `helpers.py` contient un repository en Python pur servant de référence |

## Guide d'utilisation

1. **Préférences** : commune, budget par nuit, nombre de personnes, étoiles minimales sont des contraintes strictes. Équipements, profil, paiement, accès PMR et repère de proximité sont facultatifs : un critère non demandé est ignoré et son poids redistribué.
2. **Résultats** : liste classée avec score /100, phrase d'explication construite à partir des valeurs du graphe, détail du calcul, et section « écartés » avec le motif de chaque exclusion. Sans résultat, le moteur propose d'assouplir le budget (+20 %) et/ou les étoiles quand cela suffit.
3. **Fiche** : offres par type de chambre, équipements, avis, liens typés générés depuis le graphe, hébergements proches, export `.ttl` et `.jsonld`, bloc JSON-LD schema.org intégré.
4. **Carte** (Leaflet/OpenStreetMap, connexion nécessaire pour les fonds de carte ; la liste fonctionne hors ligne) et **Comparaison** de 2 à 3 hébergements (cases « Comparer » sur la page de résultats).
5. **Données** : téléchargement du Turtle, exemples SPARQL. **/sparql** : point d'accès en lecture seule (SELECT, ASK, CONSTRUCT ; `SERVICE` refusé pour éviter des requêtes sortantes depuis le serveur). **Évaluation** : tableau des 5 scénarios.
6. Langue FR/EN : bascule en haut de page (libellés du vocabulaire ; l'interface n'est que partiellement traduite).

## Remplacer les données illustratives (à faire avant la soutenance)

Les hébergements, tarifs, coordonnées et avis fournis sont **fictifs**, à l'exception de la structure reprise du TD3 (Hôtel Le Bénoué, Auberge de la Falaise, Marché artisanal). Pour passer au jeu réel : éditez les tableaux de `scripts/build_data.py` puis relancez-le, ou modifiez `data/donnees.ttl` directement. Respectez le consentement et la pseudonymisation des avis (dossier, section 3.3). Licence des données à valider avec l'enseignant.

Liens Wikidata (objectif O3, **non réalisé par défaut** car les identifiants doivent être vérifiés) : renseignez `data/wikidata_ids.json`, lancez `python3 scripts/lier_wikidata.py`, puis `python3 scripts/enrichir_wikidata.py` (réseau requis) pour la requête R6.

## État par rapport aux objectifs du dossier

| Objectif | État |
|---|---|
| O1 Ontologie étendue, sans incohérence au raisonneur | Ontologie écrite (24 classes). **Cohérence non vérifiée dans Protégé** : à faire. |
| O2 ≥15 hébergements, ≥25 offres, ≥30 avis, tout typé et étiqueté | 16 / 33 / 40, contrôlé par `tests/test_donnees.py`. Données illustratives. |
| O3 Liens Wikidata | Scripts fournis, identifiants à renseigner. |
| O4 ≥6 requêtes SPARQL | R1–R6 + C1–C4 écrites. R6 exige réseau et owl:sameAs. |
| O5 Recommandations explicables | Oui : score, critères et valeurs réelles pour chaque résultat. |
| O6 Navigation hypermédia | Formulaire, résultats, fiches, liens typés, carte, comparaison. |
| O7 Évaluation sur 5 scénarios | Implémentée (voir ci-dessous). |
| O8 Léger, utilisable sur mobile | Pages d'environ 20 Ko, CSS adaptatif, sans framework ; Leaflet chargé depuis un CDN uniquement sur la page carte. |

## Résultats d'évaluation (référence Python pure sur le jeu illustratif)

- L'exemple chiffré du dossier (section 6.3) est reproduit exactement : **81,9** (Le Bénoué) et **63,4** (Auberge de la Falaise).
- Concordance du premier résultat avec le choix fixé à la main avant les tests : **moteur 2/4, tri par étoiles 2/4**. Part des résultats expliqués : 100 %. Le scénario sans résultat est bien détecté.
- Écarts : *Famille* (attendu Sahel Plaza, le moteur place Panorama, moins cher et aussi adapté) et *Couple* (attendu Ambassadeur, le moteur place Le Bénoué grâce au prix). Ils montrent la sensibilité aux poids (`config.json`). Les attentes n'ont pas été modifiées pour faire coïncider les résultats : à discuter lors de la soutenance, comme le prévoit le dossier.
- Ces chiffres dépendent du jeu **illustratif** : à refaire avec les données réelles.

## Écarts et limites à connaître

- **Lissage des avis** : avec k = 3 (valeur du dossier), un seul avis à 5/5 obtient une moyenne lissée (4,10) supérieure à celle de 4 avis à 4,25 (4,06). L'affirmation de la section 6.2 n'est vraie qu'à partir de k = 6 (`lissage_k` dans `config.json`). Test : `test_limite_connue_du_lissage_k3`.
- **Critères actifs** : tout critère facultatif non demandé (équipements, profil, proximité, paiement/PMR) est exclu du score, pas seulement la proximité.
- **Paiement et PMR** : si les deux sont demandés, le sous-score est la part des exigences satisfaites (50 si une seule l'est).
- **Hébergements de la commune uniquement** : le filtrage dur est limité à la commune choisie.
- Hors périmètre, comme prévu au dossier : réservation, comptes, saisie d'avis, langage naturel → SPARQL.

## Vérifications effectuées et non effectuées

Vérifié : formules de score, moteur et jeu de données (via un repository en Python pur et un mini-parseur Turtle), syntaxe de tous les gabarits et rendu des pages de résultats, comparaison, accueil, évaluation avec des routes simulées.

**Non exécuté lors de la préparation** (RDFlib indisponible sur la machine de génération) : chargement du graphe avec RDFlib, requêtes SPARQL de `repository.py`, routes Flask réelles, exports Turtle/JSON-LD, carte Leaflet. Lancez `python3 -m unittest discover -s tests -t . -v` après `pip install -r requirements.txt` : `tests/test_rdflib.py` compare le classement SPARQL à la référence Python sur les 5 scénarios, exécute les contrôles C1–C4 et teste les routes. Si un test échoue, c'est probablement là qu'il faut corriger.
