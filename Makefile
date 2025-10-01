APP_NAME = driving_school
IMAGE_NAME = driving_school_app
IMAGE_TAG = latest
DOCKER_STACK_FILE = docker-stack.yml

DIRS = data logs prometheus logstash/config logstash/pipeline nginx/conf.d

.PHONY: all init build deploy stop clean logs help

all: init build deploy

init:
	@echo "Initialisation de l'environnement..."
	@if ! docker info | grep -q "Swarm: active"; then \
		echo "Initialisation de Docker Swarm..."; \
		docker swarm init; \
	else \
		echo "Docker Swarm est déjà actif."; \
	fi
	@echo "Création des répertoires nécessaires..."
	@mkdir -p $(DIRS)
	@echo "Environnement initialisé avec succès."

build:
	@echo "Construction de l'image Docker..."
	@set -a && . .env && docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "Image construite avec succès."

deploy:
	@echo "Déploiement de la stack $(APP_NAME)..."
	@set -a && . .env && docker stack deploy -c $(DOCKER_STACK_FILE) $(APP_NAME)
	@echo "Stack déployée avec succès."

stop:
	@echo "Arrêt de la stack $(APP_NAME)..."
	@set -a && . .env && docker stack rm $(APP_NAME)
	@echo "Stack arrêtée avec succès."

clean: stop
	@echo "Nettoyage de l'environnement..."
	@echo "Suppression des volumes..."
	@for volume in $$(docker volume ls -q -f "name=$(APP_NAME)"); do \
		docker volume rm $$volume; \
	done
	@echo "Suppression des réseaux..."
	@for network in $$(docker network ls -q -f "name=$(APP_NAME)"); do \
		docker network rm $$network; \
	done
	@echo "Nettoyage des répertoires..."
	@rm -rf data/* logs/*
	@echo "Environnement nettoyé avec succès."

leave-swarm:
	@echo "Quitter le swarm Docker..."
	@set -a && . .env && docker swarm leave --force
	@echo "Swarm quitté avec succès."

logs:
	@echo "Affichage des logs pour le service $(SERVICE)..."
	@if [ -z "$(SERVICE)" ]; then \
		echo "Erreur: SERVICE n'est pas défini. Utilisez 'make logs SERVICE=nom_du_service'"; \
		exit 1; \
	fi
	@set -a && . .env && docker service logs $(APP_NAME)_$(SERVICE)

django-shell:
	@echo "Ouverture d'un shell Django..."
	@set -a && . .env && docker exec -it $$(docker ps -q -f "name=$(APP_NAME)_web") python manage.py shell

django-migrations:
	@echo "Exécution des migrations Django..."
	@set -a && . .env && docker exec -it $$(docker ps -q -f "name=$(APP_NAME)_web") python manage.py migrate

django-makemigrations:
	@echo "Création des migrations Django..."
	@set -a && . .env && docker exec -it $$(docker ps -q -f "name=$(APP_NAME)_web") python manage.py makemigrations

django-createsuperuser:
	@echo "Création d'un superutilisateur Django..."
	@set -a && . .env && docker exec -it $$(docker ps -q -f "name=$(APP_NAME)_web") python manage.py createsuperuser

django-loaddata:
	@echo "Chargement des données initiales..."
	@set -a && . .env && docker exec -it $$(docker ps -q -f "name=$(APP_NAME)_web") python manage.py loaddata initial_data

restart-service:
	@echo "Redémarrage du service $(SERVICE)..."
	@if [ -z "$(SERVICE)" ]; then \
		echo "Erreur: SERVICE n'est pas défini. Utilisez 'make restart-service SERVICE=nom_du_service'"; \
		exit 1; \
	fi
	@set -a && . .env && docker service update --force $(APP_NAME)_$(SERVICE)

scale-service:
	@echo "Mise à l'échelle du service $(SERVICE) à $(REPLICAS) réplicas..."
	@if [ -z "$(SERVICE)" ] || [ -z "$(REPLICAS)" ]; then \
		echo "Erreur: SERVICE ou REPLICAS n'est pas défini. Utilisez 'make scale-service SERVICE=nom_du_service REPLICAS=n'"; \
		exit 1; \
	fi
	@set -a && . .env && docker service scale $(APP_NAME)_$(SERVICE)=$(REPLICAS)

status:
	@echo "État des services de la stack $(APP_NAME):"
	@set -a && . .env && docker stack services $(APP_NAME)

help:
	@echo "Commandes disponibles:"
	@echo "  make init                    - Initialiser l'environnement Docker Swarm"
	@echo "  make build                   - Construire l'image Docker de l'application"
	@echo "  make deploy                  - Déployer la stack Docker Swarm"
	@echo "  make stop                    - Arrêter la stack"
	@echo "  make clean                   - Nettoyer l'environnement (arrête la stack et supprime les volumes)"
	@echo "  make leave-swarm             - Quitter le swarm Docker"
	@echo "  make logs SERVICE=nom        - Afficher les logs d'un service spécifique"
	@echo "  make django-shell            - Ouvrir un shell Django"
	@echo "  make django-migrations       - Exécuter les migrations Django"
	@echo "  make django-makemigrations   - Créer des migrations Django"
	@echo "  make django-createsuperuser  - Créer un superutilisateur Django"
	@echo "  make django-loaddata         - Charger les données initiales"
	@echo "  make restart-service SERVICE=nom - Redémarrer un service spécifique"
	@echo "  make scale-service SERVICE=nom REPLICAS=n - Mettre à l'échelle un service"
	@echo "  make status                  - Afficher l'état des services"
	@echo "  make help                    - Afficher cette aide"
