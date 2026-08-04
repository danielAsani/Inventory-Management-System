# Gestion Inventaire

Gestion Inventaire est une application web de suivi du materiel, des consommables, des mouvements de stock, des affectations, des demandes internes, des inventaires et de la maintenance.

Le projet utilise Django REST Framework, MySQL et React/Vite. Il couvre un circuit simple : gestion du catalogue, entree en stock, affectation du materiel, demandes internes, suivi des reparations et impression des etiquettes.

## Fonctionnalites

- connexion par matricule ou email ;
- roles `ADMIN`, `GESTION` et `MAGASIN` ;
- gestion des departements, directions, services et magasins ;
- catalogue des familles, categories, unites et fournisseurs ;
- suivi des materiels et consommables ;
- mouvements de stock, affectations et consommations ;
- demandes internes avec validation et finalisation ;
- inventaires physiques ;
- entretiens, reparations et documents ;
- codes-barres, QR codes et impression d'etiquettes.

## Stack technique

- Backend : Python, Django, Django REST Framework, Simple JWT, PyMySQL.
- Base : MySQL.
- Frontend : React, Vite, Axios, React Router.

## Structure du depot

```text
.
|-- backend/   # API Django REST
|-- frontend/  # Interface React
`-- README.md  # Notes de presentation
```

## Demarrage rapide

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

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

En local, le frontend doit pointer vers :

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## Comptes initiaux

La commande `create_initial_users` cree quatre comptes de base :

| Matricule | Role | Perimetre |
|---|---|---|
| `ADMIN001` | Administrateur | General |
| `GEST001` | Gestion | Direction |
| `DEP001` | Gestion | Departement |
| `MAG001` | Magasin | General |

Le mot de passe est choisi au moment de la creation des comptes. Il peut aussi etre place dans `INITIAL_USER_PASSWORD`.

## Presentation

Pour une demonstration courte, suivre cet ordre :

1. connexion avec `ADMIN001` ;
2. consultation du tableau de bord ;
3. ajout ou consultation d'un materiel ;
4. impression d'une etiquette avec code-barres et QR code ;
5. creation d'une affectation ;
6. consultation des demandes, inventaires ou reparations.
