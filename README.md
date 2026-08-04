# Gestion d’inventaire

Application web de gestion d’inventaire pour suivre le matériel, les consommables, les mouvements de stock, les affectations, les demandes internes, les inventaires physiques, la maintenance et les documents associés.

Le projet repose sur une API Django REST, une base MySQL et une interface React/Vite. Il conserve les règles métier côté serveur : rôles, permissions, génération des codes, état physique du matériel, situation de stock, mouvements, affectations et traçabilité.

## Fonctionnalités principales

- Authentification par matricule ou adresse e-mail.
- Gestion des rôles `ADMIN`, `GESTION` et `MAGASIN`.
- Organisation : départements, directions, services et magasins.
- Catalogue : familles, catégories, unités et fournisseurs.
- Gestion des matériels et consommables.
- Mouvements de stock, affectations et consommations.
- Demandes internes avec validation et finalisation.
- Inventaires physiques.
- Entretiens, réparations et documents.
- Génération et impression des QR codes et codes-barres.

## Stack technique

- Backend : Python, Django, Django REST Framework, Simple JWT.
- Base de données : MySQL.
- Frontend : React, Vite, Axios, React Router.

## Structure du dépôt

```text
.
|-- backend/   # API Django REST et règles métier
|-- frontend/  # Interface React
`-- README.md  # Présentation du projet
```

## Démarrage rapide

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

En local, le frontend doit pointer vers :

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## Comptes initiaux

La commande `create_initial_users` crée quatre comptes de base :

| Matricule | Rôle | Périmètre |
|---|---|---|
| `ADMIN001` | Administrateur | Général |
| `GEST001` | Gestion | Direction |
| `DEP001` | Gestion | Département |
| `MAG001` | Magasin | Général |

Le mot de passe est choisi au moment de la création des comptes. Il peut aussi être défini avec `INITIAL_USER_PASSWORD`.

## Parcours de démonstration

Pour une démonstration courte :

1. Se connecter avec `ADMIN001`.
2. Consulter le tableau de bord.
3. Ajouter ou consulter un matériel.
4. Imprimer une étiquette avec QR code et code-barres.
5. Créer une affectation.
6. Consulter les demandes, inventaires ou réparations.

## Qualité du dépôt

- Les fichiers d’environnement, dépendances locales, sauvegardes, captures et livrables de travail sont ignorés par Git.
- Le backend et le frontend restent séparés pour faciliter la maintenance.
- Les évolutions fonctionnelles doivent être livrées par commits clairs, idéalement rédigés en français.
