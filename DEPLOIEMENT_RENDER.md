# Déployer NordExplore sur Render

## Préparation du dépôt
1. Créez un dépôt GitHub nommé `nordexplore`.
2. Décompressez cette archive et envoyez **le contenu de cette archive** à la racine du dépôt (ne placez pas tous les fichiers dans un deuxième sous-dossier `nordexplore`).
3. Vérifiez que `requirements.txt`, `wsgi.py`, `Procfile`, `render.yaml`, `data/` et `nordexplore/` sont visibles à la racine du dépôt.

## Déploiement
1. Connectez-vous à Render et choisissez **New → Web Service**.
2. Connectez le dépôt GitHub `nordexplore`.
3. Utilisez les paramètres suivants si Render ne les détecte pas automatiquement :
   - Runtime : Python 3
   - Build command : `pip install -r requirements.txt`
   - Start command : `gunicorn wsgi:app --bind 0.0.0.0:$PORT`
4. Lancez le déploiement et consultez les logs jusqu'à la fin du build.
5. Ouvrez l'URL publique Render et vérifiez l'accueil, la recherche, les résultats, une fiche, les exports RDF/JSON-LD, la carte, la comparaison, les données, l'évaluation et `/sparql`.

## À savoir
- L'application charge `data/ontologie.ttl` et `data/donnees.ttl` depuis le dépôt. Ne déplacez pas ces fichiers sans mettre à jour la configuration.
- Les données du prototype sont illustratives, pas des offres réelles vérifiées.
- Le plan gratuit peut mettre le service en veille après une période d'inactivité ; la première requête suivante peut être lente.
- L'URL publique ne sera connue qu'après création effective du service dans votre compte Render.
- Avant de rendre le dépôt public, vérifiez qu'il ne contient aucun secret ou donnée personnelle.
