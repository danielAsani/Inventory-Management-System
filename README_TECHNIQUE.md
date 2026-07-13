# README technique - Gestion Inventaire

## Architecture

```text
Gestion Inventaire
|-- backend/   API REST Django
`-- frontend/  Interface React
```

Le backend expose une API JSON sous `/api/`. Le frontend consomme cette API via Axios et gere l'authentification avec des tokens JWT.

## Backend

### Technologies

- Python
- Django
- Django REST Framework
- djangorestframework-simplejwt
- django-cors-headers
- PyMySQL
- MySQL

### Applications Django

| App | Responsabilite |
|---|---|
| `core` | auth custom, permissions, pagination, dashboard, commandes de seed |
| `comptes` | roles, utilisateurs, login, refresh, profil |
| `organisation` | departements, directions, services |
| `catalogue` | familles, categories, unites, fournisseurs |
| `stock` | magasins, materiels, consommables |
| `operations` | mouvements, affectations, consommations |
| `demandes` | workflow de demandes |
| `inventaires` | inventaires et ecarts |
| `maintenance` | entretiens et reparations |
| `documents` | pieces rattachees |

### Installation backend

```bash
cd backend
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Configurer `.env` :

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=gestion_inventaire
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
INITIAL_USER_PASSWORD=replace-with-a-strong-password
```

Creer la base MySQL :

```sql
CREATE DATABASE gestion_inventaire CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Appliquer les migrations :

```bash
python manage.py migrate
```

Charger la structure organisationnelle :

```bash
python manage.py load_fictional_entities --replace
```

Creer les comptes initiaux :

```bash
python manage.py create_initial_users --password "VotreMotDePasseFort"
```

Generer un historique operationnel realiste :

```bash
python manage.py seed_operational_history --keep-existing
```

Lancer le serveur :

```bash
python manage.py runserver
```

## Frontend

### Technologies

- React
- Vite
- React Router
- Axios
- Lucide React
- Oxlint

### Installation frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Configurer `.env` :

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

Build production :

```bash
npm run build
```

## Authentification

Endpoints :

- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`
- `POST /api/auth/logout/`

Le backend ajoute dans les tokens les informations utiles :

- `id_users`
- `matricule`
- `role`
- `scope_type`
- `id_departement`
- `id_direction`
- `id_service`
- `id_magasin`

## Roles et permissions

### Roles

- `ADMIN` : acces global.
- `GESTION` : acces selon perimetre.
- `MAGASIN` : traitement magasin, global si scope `GENERAL`.

### Perimetres

- `GENERAL`
- `DEPARTEMENT`
- `DIRECTION`
- `SERVICE`
- `MAGASIN`

Le filtrage n'est pas seulement visuel. Il est applique cote API :

- demandes filtrees par direction, departement ou service ;
- materiels, consommables et magasins filtres par perimetre ;
- dashboard filtre par perimetre ;
- admin et magasinier general conservent la vue globale.

## Workflow demandes

Statuts :

- `EN_ATTENTE_DEPARTEMENT`
- `EN_TRAITEMENT_MAGASIN`
- `TRAITEE`
- `REJETEE`
- `ANNULEE`

Actions :

- creation par direction ;
- validation/rejet par departement ;
- finalisation par magasinier general.

Regles :

- `REPARATION` exige un materiel ;
- `REAPPROVISIONNEMENT` exige un consommable et une quantite ;
- `ACHAT` et `AUTRE` peuvent etre de simples observations.

## API principale

Base :

```text
/api/
```

Modules :

- `/api/dashboard/`
- `/api/auth/`
- `/api/comptes/`
- `/api/organisation/`
- `/api/catalogue/`
- `/api/stock/`
- `/api/operations/`
- `/api/inventaires/`
- `/api/maintenance/`
- `/api/demandes/`
- `/api/documents/`

Les listes sont paginees avec :

- `count`
- `page`
- `perpage`
- `total_pages`
- `results`

## Tests et verification

Backend :

```bash
cd backend
python manage.py check
python manage.py test apps.core.tests_integration.AuthDashboardIntegrationTests
```

Frontend :

```bash
cd frontend
npm run lint
npm run build
```

## Publication GitHub

Ne pas publier :

- `.env`
- logs ;
- caches ;
- `node_modules` ;
- `dist` ;
- environnements virtuels ;
- dumps locaux.

Publier :

- code source ;
- migrations ;
- `.env.example` ;
- README ;
- documentation ;
- fichiers de lock (`package-lock.json`) ;
- `requirements.txt`.

## Deploiement

Backend :

- definir `DJANGO_DEBUG=False` ;
- configurer `DJANGO_ALLOWED_HOSTS` ;
- configurer CORS avec le domaine frontend ;
- utiliser une vraie cle `DJANGO_SECRET_KEY` ;
- utiliser MySQL avec un utilisateur dedie ;
- servir les fichiers statiques apres `collectstatic`.

Frontend :

- configurer `VITE_API_BASE_URL` vers l'URL publique du backend ;
- lancer `npm run build` ;
- deployer le dossier `dist/` sur un hebergeur statique.
