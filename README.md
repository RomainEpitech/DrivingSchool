# My Driving School - Application de gestion d'auto-école

## Fonctionnalités implémentées

L'application "My Driving School" est un intranet de gestion pour auto-école qui permet de gérer l'ensemble des aspects de l'entreprise, notamment :

### Gestion des utilisateurs
- 4 types d'utilisateurs : Élève, Instructeur, Secrétaire et Administrateur
- Système d'authentification complet
- Profils détaillés pour chaque type d'utilisateur
- Tableaux de bord personnalisés selon le type d'utilisateur

### Gestion des cours et forfaits
- Catalogue de forfaits d'heures de conduite
- Système d'achat de forfaits par les secrétaires ou admins
- Historique complet des achats effectués
- Suivi du nombre d'heures restantes pour chaque élève

### Gestion des rendez-vous
- Prise de rendez-vous pour les leçons de conduite
- Calendrier visuel pour visualiser les disponibilités
- Vérification automatique des contraintes :
  - Disponibilité des instructeurs et élèves
  - Heures restantes suffisantes
- Modification et annulation de rendez-vous

### Interface administrative
- Interface d'administration Django complète
- Gestion des utilisateurs, forfaits et rendez-vous
- Filtres et recherches avancées pour faciliter la gestion

## Modèles de données

### Utilisateurs
- **User** : Utilisateur de base avec type (admin, secretary, instructor, student)
- **Student** : Profil élève avec suivi des heures restantes
- **Instructor** : Profil instructeur avec spécialisation

### Cours et Forfaits
- **CoursePackage** : Définition des forfaits disponibles (heures, prix)
- **Purchase** : Enregistrement des achats de forfaits par les élèves

### Rendez-vous
- **Appointment** : Rendez-vous de cours avec date, heure, durée, élève et instructeur

## Technologies utilisées

- **Django** : Framework Python pour le développement web
- **SQLite** : Base de données relationnelle
- **Tailwind CSS** : Framework CSS pour l'interface utilisateur
- **Font Awesome** : Icônes pour l'interface utilisateur
- **AlpineJS** : Interactions JavaScript minimales

## Commandes d'installation et de lancement

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

1. Cloner le dépôt Git :
```bash
git clone https://github.com/username/my_driving_school.git
cd my_driving_school
```

2. Créer et activer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer la base de données :
```bash
python manage.py migrate
```

5. Charger les données initiales :
```bash
python manage.py loaddata accounts/fixtures/initial_data.json
python manage.py loaddata courses/fixtures/initial_data.json
python manage.py loaddata scheduling/fixtures/initial_data.json
```

6. Démarrer le serveur de développement :
```bash
python manage.py runserver
```

7. Accéder à l'application via un navigateur : http://localhost:8000

### Accès à l'application

Plusieurs comptes sont disponibles pour tester l'application :

- **Admin** : 
  - Identifiant : admin
  - Mot de passe : motdepasse1234

- **Secrétaire** : 
  - Identifiant : marie.dupont 
  - Mot de passe : motdepasse1234

- **Instructeur** : 
  - Identifiant : pierre.durand
  - Mot de passe : motdepasse1234

- **Élève** : 
  - Identifiant : lucas.petit
  - Mot de passe : motdepasse1234

## Perspectives d'amélioration

Pour une version future, plusieurs améliorations pourraient être envisagées :

1. Développement d'une plateforme d'entraînement au code de la route
2. Système de demande de rendez-vous avec validation par l'instructeur
3. Intégration d'un système de paiement en ligne
4. Application mobile pour les élèves et instructeurs
5. Système de notifications par email ou SMS
6. Rapports et statistiques avancés pour l'administration

## Conclusion

Cette application représente une solution complète de gestion pour les auto-écoles, permettant d'optimiser l'organisation des cours, de suivre la progression des élèves et de faciliter le travail administratif au quotidien. L'architecture modulaire permet d'ajouter facilement de nouvelles fonctionnalités selon les besoins.