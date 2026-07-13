# Documentation backend

## Vue d'ensemble

Le backend est une API Django REST Framework pour la gestion d'inventaire. Il gere l'authentification, les roles, les perimetres d'acces, les ressources d'inventaire, les demandes, les operations, les inventaires, la maintenance et les documents.

## Configuration

Le backend lit sa configuration depuis `.env`.

Variables importantes :

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Cle secrete Django |
| `DJANGO_DEBUG` | `True` en local, `False` en production |
| `DJANGO_ALLOWED_HOSTS` | Domaines autorises |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Origines frontend autorisees |
| `DB_NAME` | Nom de la base MySQL |
| `DB_USER` | Utilisateur MySQL |
| `DB_PASSWORD` | Mot de passe MySQL |
| `DB_HOST` | Hote MySQL |
| `DB_PORT` | Port MySQL |
| `INITIAL_USER_PASSWORD` | Mot de passe des comptes initiaux si la commande est appelee sans `--password` |

Un exemple complet est fourni dans `.env.example`.

## Installation

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py load_fictional_entities --replace
python manage.py create_initial_users --password "VotreMotDePasseFort"
python manage.py runserver
```

## Base de donnees

Le backend cible MySQL avec `PyMySQL`.

```sql
CREATE DATABASE gestion_inventaire CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Les migrations Django creent les tables. Les donnees locales ne sont pas exportees automatiquement dans le depot.

## Modules

- `comptes` : roles, utilisateurs, authentification.
- `organisation` : departements, directions, services.
- `catalogue` : familles, categories, unites, fournisseurs.
- `stock` : magasins, materiels, consommables.
- `operations` : mouvements, affectations, consommations.
- `demandes` : workflow direction -> departement -> magasin.
- `inventaires` : inventaires physiques et details.
- `maintenance` : entretiens et reparations.
- `documents` : fichiers et references.
- `core` : dashboard, permissions, pagination, authentification custom.

## Authentification

Le backend utilise JWT.

Endpoints :

- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`
- `POST /api/auth/logout/`

Le token access doit etre envoye dans l'en-tete :

```http
Authorization: Bearer <access_token>
```

## Permissions

Les roles actifs sont :

- `ADMIN`
- `GESTION`
- `MAGASIN`

Les utilisateurs peuvent aussi avoir un perimetre :

- `GENERAL`
- `DEPARTEMENT`
- `DIRECTION`
- `SERVICE`
- `MAGASIN`

Le filtrage par perimetre est applique dans les endpoints sensibles :

- demandes ;
- materiels ;
- consommables ;
- magasins ;
- dashboard.

## Workflow demandes

Une direction cree une demande. Le departement rattache la valide ou la rejette. Le magasinier general finalise les demandes validees.

Types :

- `ACHAT`
- `REAPPROVISIONNEMENT`
- `REPARATION`
- `AUTRE`

Statuts :

- `EN_ATTENTE_DEPARTEMENT`
- `EN_TRAITEMENT_MAGASIN`
- `TRAITEE`
- `REJETEE`
- `ANNULEE`

Actions custom :

- `POST /api/demandes/{id}/valider-departement/`
- `POST /api/demandes/{id}/rejeter-departement/`
- `POST /api/demandes/{id}/finaliser-magasin/`

## Donnees initiales

Structure organisationnelle :

```bash
python manage.py load_fictional_entities --replace
```

Comptes initiaux :

```bash
python manage.py create_initial_users --password "VotreMotDePasseFort"
```

Historique operationnel :

```bash
python manage.py seed_operational_history --keep-existing
```

## Tests

```bash
python manage.py check
python manage.py test apps.core.tests_integration.AuthDashboardIntegrationTests
```

Les tests couvrent notamment :

- login ;
- dashboard ;
- permissions ;
- workflow demandes ;
- mouvements et consommations ;
- affectations ;
- filtrage par perimetre ;
- regles de validation des demandes.

## Production

Avant de deployer :

- `DJANGO_DEBUG=False`
- definir `DJANGO_ALLOWED_HOSTS`
- definir `DJANGO_CORS_ALLOWED_ORIGINS`
- utiliser une cle secrete forte ;
- utiliser un compte MySQL dedie ;
- executer `python manage.py collectstatic` si necessaire ;
- ne jamais publier `.env`.
