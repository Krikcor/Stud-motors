			                      Stud-Motors

Stud-Motors est une plateforme de vente et location de voitures permettant de simplifier les démarches administratives et la transmission de documents en ligne. 
Ce projet a été fait pour un Bachelor en développement Python avec Django.

		        Les Fonctionnalités principales

	Gestion des utilisateurs :

Clients : création de compte, consultation de véhicules, transmission de documents, demande de réservation.

Professionnels : gestion des véhicules, gestion des réservations.

Superadmin : accès complet à l’interface Django Admin.

	Gestion des véhicules : 

CRUD côté pro.
Filtrage et pagination sur la page vehicles.

	Réservations : 

Possibilité pour les clients de réserver uniquement les véhicules disponibles.


		        Technologies utilisées

Backend : Python 3.12, Django 6.0

Frontend : HTML5, CSS3, Bootstrap 5

Base de données : SQLite

Dépendances : django-filter, python-dotenv, Pillow, sqlparse, tzdata

Hébergement : PythonAnywhere

		        Installation et lancement local

	Cloner le projet :

git clone https://github.com/Krikcor/Stud-motors.git
cd Stud-motors/src

	Créer et activer le virtualenv :

python3 -m venv venv
source venv/bin/activate

	Installer les dépendances :

pip install -r requirements.txt

	Créer le fichier secretenv avec :

SECRET_KEY=cle_secrete_django
DEBUG=True
BREVO_USER=utilisateur_smtp
BREVO_PASSWORD=mot_de_passe_smtp
BREVO_MAIL=email_expediteur

	Appliquer les migrations :

python manage.py migrate

	Créer un superuser :

python manage.py createsuperuser
	
	Configuration des emails

Le projet utilise Brevo pour l’envoi d’emails. Les informations doivent être renseignées dans le fichier secretenv.

	Tests et couverture

Les tests unitaires couvrent 97% de l'application totale.

		Pour lancer les tests :

python manage.py test

    Lancer le serveur de développement :

python manage.py runserver
