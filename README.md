# Gestion Inventaire

Gestion Inventaire est une application web de suivi du materiel, des consommables, des demandes internes, des mouvements de stock, des affectations, des inventaires physiques et de la maintenance.

Le projet est construit avec un backend Django REST Framework, une base MySQL et un frontend React/Vite. Il couvre un workflow metier complet : une direction cree une demande, le departement concerne la valide, puis le magasinier general finalise le traitement.

## Objectif

L'application aide une organisation a :

- centraliser son inventaire de materiels et consommables ;
- connaitre l'emplacement et l'etat des biens ;
- suivre les demandes d'achat, de reapprovisionnement, de reparation ou les demandes simples ;
- limiter les acces selon le role et le perimetre de l'utilisateur ;
- analyser les donnees de stock sur plusieurs mois ;
- detecter les incoherences, ruptures probables et dossiers a verifier.

## Fonctionnalites principales

- Authentification par tokens JWT.
- Roles applicatifs : `ADMIN`, `GESTION`, `MAGASIN`.
- Perimetres utilisateur : general, departement, direction, service, magasin.
- Gestion de l'organisation : departements, directions, services.
- Catalogue : familles, categories, unites, fournisseurs.
- Stock : magasins, materiels, consommables.
- Operations : mouvements, affectations, consommations.
- Demandes : creation, validation departement, rejet, finalisation magasin.
- Inventaires physiques et details d'ecart.
- Maintenance : entretiens et reparations.
- Documents rattaches aux materiels ou consommables.
- Notifications de demandes a traiter.
- Tableaux, cartes, filtres rapides et tri par boutons.
- Etude des donnees : risques stock, previsions, verification des incoherences et flux.

## Stack technique

- Backend : Python, Django, Django REST Framework, Simple JWT, PyMySQL.
- Base de donnees : MySQL.
- Frontend : React, Vite, Axios, React Router, Lucide React.
- Tests : Django `TestCase`, DRF `APIClient`, Oxlint, build Vite.

## Structure du depot

```text
.
|-- backend/       # API Django REST
|-- frontend/      # Interface React
|-- README.md            # Presentation generale
|-- README_TECHNIQUE.md  # Installation, architecture et verification
`-- README_UTILISATEUR.md # Guide fonctionnel non technique
```

## Demarrage rapide

### Backend

```bash
cd backend
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py load_fictional_entities --replace
python manage.py create_initial_users --password "VotreMotDePasseFort"
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Par defaut, le backend expose l'API sur `/api/`. En local, configurez `VITE_API_BASE_URL=http://localhost:8000/api` dans le `.env` frontend.

## Comptes initiaux

La commande `create_initial_users` cree les matricules suivants :

| Matricule | Role | Perimetre |
|---|---|---|
| `ADMIN001` | Administrateur | General |
| `GEST001` | Gestion | Direction |
| `DEP001` | Gestion | Departement |
| `MAG001` | Magasin | General |

Le mot de passe n'est pas stocke dans le depot. Il doit etre fourni via `--password` ou `INITIAL_USER_PASSWORD`.

## Verification

Commandes executees avant publication :

```bash
cd backend
python manage.py check
python manage.py test apps.core.tests_integration.AuthDashboardIntegrationTests
```

```bash
cd frontend
npm run lint
npm run build
```

## Securite de publication

Les fichiers suivants ne doivent pas etre commits :

- `.env`
- logs (`*.log`)
- environnements virtuels (`env/`, `.venv/`)
- `node_modules/`
- builds frontend (`dist/`, `build/`)
- caches Python (`__pycache__/`, `*.pyc`)
- dumps locaux de base de donnees.

Les fichiers `.env.example` restent publics et ne contiennent pas de secret reel.

## Documentation

- [README utilisateur](README_UTILISATEUR.md)
- [README technique](README_TECHNIQUE.md)
- [Documentation backend](backend/docs/DOCUMENTATION_BACKEND.md)
- [Documentation API](backend/docs/API_DOCUMENTATION.md)
