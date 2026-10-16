"""Point d'entrée WSGI utilisé par l'hébergeur en production."""
from nordexplore.app import create_app

app = create_app()
