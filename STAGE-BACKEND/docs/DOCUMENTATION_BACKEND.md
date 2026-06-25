# Documentation complète du backend - Inventaire SNEL

## 1. Présentation générale

Ce backend expose une API REST destinée à une application de gestion d'inventaire de matériels et de consommables.

Il couvre les principaux besoins suivants :

- gestion de l'organisation interne : départements, directions et services ;
- gestion du catalogue : familles, catégories, unités de mesure et fournisseurs ;
- gestion du stock : magasins, matériels et consommables ;
- suivi des mouvements de stock : entrées, sorties, transferts et ajustements ;
- affectation des matériels ;
- consommation des consommables ;
- inventaires et détails d'inventaire ;
- demandes internes ;
- maintenance : entretiens et réparations ;
- documents liés aux matériels ou aux consommables ;
- authentification et contrôle d'accès par rôles.

## 2. Objectif du backend

Le backend centralise les données métier de l'inventaire et fournit des endpoints sécurisés pour les applications clientes.

Ses objectifs sont :

- structurer les données dans une base SQL relationnelle ;
- exposer les ressources métier via une API REST ;
- contrôler les accès selon le rôle de l'utilisateur connecté ;
- assurer la cohérence des données avec des validations métier ;
- fournir une pagination commune sur les listes ;
- sécuriser les champs texte et les mots de passe ;
- faciliter les tests manuels avec des utilisateurs de test.

## 3. Technologies utilisées

- Python
- Django
- Django REST Framework
- Base de données SQL relationnelle
- MySQL dans la configuration actuelle du projet
- SimpleJWT avec `djangorestframework-simplejwt`
- `django-cors-headers`
- `bleach` pour l'assainissement des champs texte
- Cache Django `LocMemCache`

## 4. Architecture du projet

Le projet suit une organisation Django modulaire. Chaque domaine métier est placé dans une application dédiée sous `apps/`.

```text
STAGE-BACKEND/
├── apps/
│   ├── core/
│   ├── comptes/
│   ├── organisation/
│   ├── catalogue/
│   ├── stock/
│   ├── operations/
│   ├── inventaires/
│   ├── maintenance/
│   ├── demandes/
│   └── documents/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── docs/
├── manage.py
└── requirements.txt
```

## 5. Structure des dossiers

### `config/`

Contient la configuration globale Django :

- paramètres du projet ;
- configuration de la base de données ;
- routes globales ;
- configuration WSGI/ASGI.

### `apps/core/`

Contient les éléments transversaux :

- authentification par token ;
- permissions basées sur les rôles ;
- pagination ;
- cache ;
- validateurs et assainissement des serializers.

### Applications métier

Chaque application métier contient généralement :

- `models.py` : modèles SQL ;
- `serializers.py` : sérialisation et validation des données ;
- `views.py` : ViewSets REST ;
- `urls.py` : routes de l'application ;
- `admin.py` : configuration de l'administration Django ;
- `migrations/` : migrations de base de données.

## 6. Modules Django

### `comptes`

Gère les rôles, les utilisateurs métier, l'authentification JWT et le profil connecté.

Modèles principaux :

- `Role`
- `Users`

### `organisation`

Gère la structure administrative.

Modèles principaux :

- `Departement`
- `Direction`
- `Service`

### `catalogue`

Gère les référentiels utilisés par le stock.

Modèles principaux :

- `Famille`
- `Categorie`
- `UniteMesure`
- `Fournisseur`

### `stock`

Gère les magasins, les matériels et les consommables.

Modèles principaux :

- `Magasin`
- `Materiel`
- `Consommable`

### `operations`

Gère les opérations liées aux flux de stock et aux affectations.

Modèles principaux :

- `MouvementStock`
- `Affectation`
- `Consommation`

### `inventaires`

Gère les campagnes d'inventaire et leurs lignes de détail.

Modèles principaux :

- `Inventaire`
- `InventaireDetail`

### `maintenance`

Gère les interventions de maintenance.

Modèles principaux :

- `Entretien`
- `Reparation`

### `demandes`

Gère les demandes internes liées aux matériels ou consommables.

Modèle principal :

- `Demande`

### `documents`

Gère les documents associés aux matériels ou consommables.

Modèle principal :

- `Document`

## 7. Base de données SQL

Le backend utilise une base de données SQL relationnelle. Les tables sont créées et maintenues par les migrations Django.

La configuration actuelle pointe vers une base MySQL :

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "stage_inventaire_snel",
        "USER": "root",
        "HOST": "localhost",
        "PORT": "3306",
    }
}
```

Les modèles définissent :

- les tables SQL via `db_table` ;
- les clés primaires ;
- les relations entre tables avec `ForeignKey` ;
- les contraintes d'unicité ;
- les règles de validation métier ;
- les valeurs autorisées pour certains champs avec `TextChoices`.

Les migrations doivent être générées et appliquées après toute modification structurelle des modèles.

Commandes utiles :

```powershell
py manage.py makemigrations
py manage.py migrate
py manage.py showmigrations
```

## 8. Authentification

L'authentification repose sur JWT.

Le login se fait avec :

- un matricule et un mot de passe ;
- ou un email et un mot de passe.

Après connexion, l'API retourne :

- un token `access` ;
- un token `refresh` ;
- les informations principales de l'utilisateur connecté.

Le token `access` doit être envoyé dans les requêtes protégées :

```text
Authorization: Bearer <access_token>
```

Le backend utilise une authentification personnalisée dans `apps.core.authentication.CustomTokenAuthentication`.

## 9. Rôles utilisateurs

Le système utilise quatre rôles principaux :

| Rôle | Description |
| --- | --- |
| `ADMIN` | Administrateur système, accès complet |
| `GESTIONNAIRE` | Gestion administrative de l'inventaire |
| `MAGASINIER` | Gestion physique du stock |
| `AUDITEUR` | Consultation en lecture seule |

Le rôle actif est rattaché à l'utilisateur via la relation `Users.id_role`.

## 10. Permissions

Les permissions sont centralisées dans `apps.core.permissions.RoleBasedPermission`.

Règles générales :

- `ADMIN` peut effectuer toutes les actions ;
- `AUDITEUR` peut effectuer les actions de lecture ;
- les autres rôles obtiennent leurs droits selon la configuration `role_permissions` de chaque ViewSet ;
- une requête sans token est refusée ;
- une requête avec un rôle insuffisant est refusée.

Les actions de lecture correspondent aux méthodes HTTP sûres :

- `GET`
- `HEAD`
- `OPTIONS`

## 11. Périmètre utilisateur

Le modèle `Users` contient un champ `scope_type` qui permet de rattacher un utilisateur à un périmètre :

- `GENERAL`
- `DEPARTEMENT`
- `DIRECTION`
- `SERVICE`
- `MAGASIN`

Selon le périmètre choisi, l'utilisateur peut être lié à un département, une direction, un service ou un magasin.

Le filtrage automatique des données par périmètre est prévu comme évolution. À l'état actuel, le champ est présent dans les modèles et dans les tokens, mais le filtrage par périmètre doit être appliqué module par module lorsque les règles métier sont finalisées.

## 12. Logique métier principale

### Catalogue et organisation

Ces modules fournissent les référentiels nécessaires aux autres modules.

### Stock

Le stock distingue :

- les matériels, généralement suivis individuellement ;
- les consommables, suivis par quantité ;
- les magasins, lieux de stockage.

Les modèles contrôlent notamment :

- l'unicité des codes ;
- les relations avec les catégories, unités et fournisseurs ;
- les états possibles d'un matériel ;
- les quantités et seuils des consommables.

### Opérations

Les mouvements de stock permettent de tracer :

- les entrées ;
- les sorties ;
- les transferts ;
- les ajustements.

Une opération doit respecter des règles de cohérence, par exemple un transfert doit avoir un magasin source et un magasin destination différents.

### Inventaires

Un inventaire regroupe une campagne de contrôle et des détails. Chaque détail compare une quantité théorique à une quantité réelle. L'écart est calculé automatiquement.

### Maintenance

La maintenance suit les entretiens et réparations liés aux matériels.

### Documents

Les documents peuvent être liés à un matériel ou à un consommable, mais pas aux deux en même temps.

## 13. Sécurité et validation

Le backend applique plusieurs protections :

- authentification JWT sur les endpoints protégés ;
- permissions par rôle ;
- stockage des mots de passe sous forme de hash ;
- champ `password` en écriture seule ;
- exclusion de `password_hash` des réponses API ;
- assainissement des champs texte avec `bleach` ;
- validation des champs obligatoires ;
- validation des dates, quantités et choix métier ;
- contrôle des relations entre modèles.

## 14. Cache

Un cache local `LocMemCache` est configuré pour le développement.

Les ressources principalement concernées sont :

- données d'organisation ;
- catalogue ;
- rôles ;
- magasins.

Les données dynamiques comme les mouvements, inventaires, demandes, maintenances et documents doivent rester peu ou pas cachées.

## 15. Installation

Créer un environnement virtuel :

```powershell
py -m venv env
```

Activer l'environnement :

```powershell
.\env\Scripts\Activate.ps1
```

Installer les dépendances :

```powershell
py -m pip install -r requirements.txt
```

Configurer la base de données dans `config/settings.py` ou via variables d'environnement si le projet est adapté pour cela.

Appliquer les migrations :

```powershell
py manage.py migrate
```

Vérifier l'état du projet :

```powershell
py manage.py check
```

## 16. Lancement du serveur

Lancer le serveur de développement :

```powershell
py manage.py runserver
```

L'API est ensuite disponible par défaut sur :

```text
http://127.0.0.1:8000/api/
```

## 17. Utilisateurs de test

Le projet contient une commande pour créer ou mettre à jour des utilisateurs de test :

```powershell
py manage.py create_test_users --password Test@123
```

Cette commande prépare notamment des profils utiles pour les tests manuels :

- gestionnaire ;
- magasinier ;
- auditeur.

Les rôles correspondants doivent exister dans la table `role`.

## 18. Tests manuels

Tests recommandés :

- vérifier `py manage.py check` ;
- vérifier `py manage.py showmigrations` ;
- créer ou vérifier les rôles ;
- créer les utilisateurs de test ;
- tester le login ;
- tester `/api/auth/me/` avec un token valide ;
- tester une lecture avec chaque rôle ;
- tester une action interdite avec `AUDITEUR` ;
- tester une création autorisée avec `GESTIONNAIRE` ou `MAGASINIER` selon le module ;
- vérifier les messages d'erreur pour les données invalides.

## 19. Bonnes pratiques du projet

- garder les modèles alignés avec les migrations ;
- générer une migration après toute modification de structure ;
- ne pas exposer `password_hash` ;
- ne pas stocker de mot de passe en clair ;
- limiter les permissions au rôle nécessaire ;
- valider les données côté serializer et côté modèle si la règle est métier ;
- documenter les nouvelles routes dans `docs/API_DOCUMENTATION.md` ;
- éviter les changements non liés dans les migrations ;
- tester les endpoints critiques après chaque évolution.

## 20. Documentation API

La documentation détaillée des endpoints est séparée dans :

```text
docs/API_DOCUMENTATION.md
```
