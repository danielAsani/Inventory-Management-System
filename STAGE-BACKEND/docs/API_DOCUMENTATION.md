# Documentation Backend - API Inventaire SNEL

## 1. Présentation du projet

Ce backend expose une API REST pour une application de gestion d'inventaire matériel et consommables de la SNEL.

Il couvre les besoins principaux suivants :

- gestion de l'organisation : départements, directions, services ;
- gestion du catalogue : familles, catégories, unités de mesure, fournisseurs ;
- gestion du stock : magasins, matériels, consommables ;
- mouvements de stock : entrées, sorties, transferts ;
- affectations de matériels ;
- consommations de consommables ;
- inventaires et détails d'inventaire ;
- demandes ;
- maintenance : entretiens et réparations ;
- documents liés aux matériels ou consommables.

## 2. Stack technique

- Python
- Django
- Django REST Framework
- Oracle Database
- `oracledb`
- SimpleJWT avec `djangorestframework-simplejwt`
- `django-cors-headers`
- `bleach` pour l'assainissement des champs texte
- Cache Django `LocMemCache`

## 3. Architecture du backend

- `config/` : configuration Django, routes globales, settings.
- `apps/core/` : éléments transversaux : authentification, permissions, pagination, cache, validators.
- `apps/comptes/` : utilisateurs métier `USERS`, rôles `ROLE`, login JWT, profil connecté.
- `apps/organisation/` : départements, directions, services.
- `apps/catalogue/` : familles, catégories, unités de mesure, fournisseurs.
- `apps/stock/` : magasins, matériels, consommables.
- `apps/operations/` : mouvements de stock, affectations, consommations.
- `apps/inventaires/` : inventaires et détails d'inventaire.
- `apps/maintenance/` : entretiens et réparations.
- `apps/demandes/` : demandes.
- `apps/documents/` : documents.

## 4. Base de données Oracle

La base Oracle existe déjà dans le schéma `STAGE_INVENTAIRE_SNEL`.

Les modèles Django viennent de `inspectdb` et restent en lecture de structure :

```python
class Meta:
    managed = False
```

Conséquences importantes :

- Django ne doit pas créer, modifier ou supprimer les tables métier Oracle.
- Ne pas lancer de migrations pour les tables métier Oracle.
- Les noms `db_table` et `db_column` doivent rester alignés avec Oracle.
- Certains identifiants sont générés par Oracle avec `GENERATED ALWAYS AS IDENTITY`.
- Le backend ne doit pas insérer manuellement les IDs générés automatiquement, par exemple `USERS.ID_USERS`.

## 5. Authentification JWT

L'authentification utilise SimpleJWT, mais avec la table métier Oracle `USERS`.

Le backend n'utilise pas `auth_user` pour connecter les utilisateurs métier, et n'utilise pas `USER_ROLE`.

Le rôle vient uniquement de :

```text
USERS.ID_ROLE -> ROLE.ID_ROLE
```

### POST `/api/auth/login/`

Connecte un utilisateur avec son matricule ou son email.

Body avec matricule :

```json
{
  "matricule": "ADMIN001",
  "password": "Admin@123"
}
```

Body avec email :

```json
{
  "email": "admin@snel.cd",
  "password": "Admin@123"
}
```

Réponse réussie :

```json
{
  "access": "jwt_access_en_3_parties",
  "refresh": "jwt_refresh_en_3_parties",
  "user": {
    "id_users": 1,
    "nom_users": "Administrateur SNEL",
    "email": "admin@snel.cd",
    "matricule": "ADMIN001",
    "telephone": "000000000",
    "role": "ADMIN",
    "scope_type": "CENTRAL",
    "id_departement": null,
    "id_direction": null,
    "id_service": null,
    "id_magasin": null
  }
}
```

Erreurs possibles :

```json
{
  "non_field_errors": ["Identifiants invalides."]
}
```

```json
{
  "non_field_errors": ["Utilisateur inactif."]
}
```

```json
{
  "non_field_errors": ["Rôle utilisateur introuvable ou inactif."]
}
```

### POST `/api/auth/refresh/`

Génère un nouveau token `access` à partir d'un `refresh`.

Body :

```json
{
  "refresh": "jwt_refresh"
}
```

Réponse :

```json
{
  "access": "nouveau_jwt_access"
}
```

Erreur :

```json
{
  "non_field_errors": ["Token invalide ou expiré."]
}
```

### GET `/api/auth/me/`

Retourne l'utilisateur connecté.

Header obligatoire :

```text
Authorization: Bearer <access_token>
```

Réponse :

```json
{
  "id_users": 1,
  "nom_users": "Administrateur SNEL",
  "email": "admin@snel.cd",
  "matricule": "ADMIN001",
  "telephone": "000000000",
  "role": "ADMIN",
  "scope_type": "CENTRAL",
  "id_departement": null,
  "id_direction": null,
  "id_service": null,
  "id_magasin": null
}
```

### POST `/api/auth/logout/`

Avec JWT stateless, le backend ne stocke pas la session.
Le frontend doit supprimer le token localement.

Réponse :

```json
{
  "detail": "Déconnexion réussie. Supprimez le token côté frontend."
}
```

## 6. Rôles et permissions

| Rôle | Description | Droits principaux |
| --- | --- | --- |
| ADMIN | Administrateur système | Accès complet |
| GESTIONNAIRE | Gestion administrative de l'inventaire | Matériels, affectations, inventaires, demandes |
| MAGASINIER | Gestion physique du stock | Mouvements, entrées, sorties, consommations |
| AUDITEUR | Consultation | Lecture seule |

Règles générales :

- ADMIN peut tout faire.
- GESTIONNAIRE ne gère pas les utilisateurs ni les rôles.
- MAGASINIER ne gère pas les utilisateurs, les rôles ni l'organisation.
- AUDITEUR est en lecture seule.
- Sans token, l'accès est refusé.
- Avec un mauvais rôle, l'accès est refusé côté backend.

Messages fréquents :

```json
{
  "detail": "Token manquant."
}
```

```json
{
  "detail": "Token invalide ou expiré."
}
```

```json
{
  "detail": "Vous n'avez pas la permission d'effectuer cette action."
}
```

## 7. Format général des réponses

Réponse de succès simple :

```json
{
  "id_role": 1,
  "nom_role": "Administrateur",
  "code_role": "ADMIN"
}
```

Réponse paginée :

```json
{
  "count": 100,
  "page": 1,
  "perpage": 10,
  "total_pages": 10,
  "results": []
}
```

Erreurs possibles :

- `400 Bad Request` : données invalides, identifiants invalides, pagination invalide.
- `403 Forbidden` : token manquant, token invalide, rôle insuffisant.
- `404 Not Found` : ressource inexistante.

## 8. Pagination

Les endpoints de liste utilisent une pagination commune.

Paramètres :

- `page` : page demandée, défaut `1`.
- `perpage` : nombre d'éléments par page, défaut `10`.
- limite maximale : `50`.

Exemple :

```text
GET /api/catalogue/categories/?page=1&perpage=10
```

Réponse :

```json
{
  "count": 100,
  "page": 1,
  "perpage": 10,
  "total_pages": 10,
  "results": []
}
```

Erreurs :

```json
{
  "detail": "Le paramètre page doit être un nombre entier."
}
```

```json
{
  "detail": "Vous ne pouvez pas demander plus de 50 éléments par page."
}
```

## 9. Tri / ordering

Le cahier des charges prévoit un paramètre `order`.

Exemples attendus :

```text
GET /api/stock/materiels/?order=code_materiel
GET /api/stock/materiels/?order=-date_achat
GET /api/stock/materiels/?order=code_materiel,-date_achat
```

À vérifier selon l'état exact des vues : si un backend d'ordering DRF n'est pas encore configuré, cette section devra être finalisée lors de l'ajout officiel du tri.

## 10. Filtrage et recherche

À compléter selon les filtres disponibles.

Le projet peut évoluer vers :

- recherche par code matériel ;
- recherche par numéro de série ;
- filtrage par catégorie ;
- filtrage par magasin ;
- filtrage par statut ;
- filtrage par date.

## 11. Liste des endpoints principaux

Les endpoints ci-dessous sont exposés via `DefaultRouter`.

Pour chaque ressource ViewSet, les méthodes standard sont disponibles selon les permissions :

- `GET /ressource/` : liste ;
- `POST /ressource/` : création ;
- `GET /ressource/{id}/` : détail ;
- `PUT /ressource/{id}/` : remplacement ;
- `PATCH /ressource/{id}/` : modification partielle ;
- `DELETE /ressource/{id}/` : suppression.

### Auth

| Méthode | URL | Description | Accès |
| --- | --- | --- | --- |
| POST | `/api/auth/login/` | Connexion JWT | Public |
| POST | `/api/auth/refresh/` | Renouveler access token | Public avec refresh valide |
| GET | `/api/auth/me/` | Profil connecté | Authentifié |
| POST | `/api/auth/logout/` | Déconnexion côté frontend | Authentifié |

### Comptes

| Ressource | URL | Rôles |
| --- | --- | --- |
| Users | `/api/comptes/users/` | ADMIN |
| Roles | `/api/comptes/roles/` | ADMIN |

Exemple création utilisateur :

```json
{
  "email": "user@snel.cd",
  "nom_users": "Utilisateur SNEL",
  "matricule": "USR001",
  "telephone": "000000000",
  "password": "Test@123",
  "statut": true,
  "id_role": 2,
  "scope_type": "CENTRAL"
}
```

Le champ `password` est en écriture seule. `password_hash` n'est jamais retourné.

### Organisation

| Ressource | URL | Rôles |
| --- | --- | --- |
| Départements | `/api/organisation/departements/` | ADMIN écriture, autres rôles lecture |
| Directions | `/api/organisation/directions/` | ADMIN écriture, autres rôles lecture |
| Services | `/api/organisation/services/` | ADMIN écriture, autres rôles lecture |

### Catalogue

| Ressource | URL | Rôles |
| --- | --- | --- |
| Familles | `/api/catalogue/familles/` | ADMIN tout, GESTIONNAIRE création/modification, MAGASINIER/AUDITEUR lecture |
| Catégories | `/api/catalogue/categories/` | ADMIN tout, GESTIONNAIRE création/modification, MAGASINIER/AUDITEUR lecture |
| Unités | `/api/catalogue/unites/` | ADMIN tout, GESTIONNAIRE création/modification, MAGASINIER/AUDITEUR lecture |
| Fournisseurs | `/api/catalogue/fournisseurs/` | ADMIN tout, GESTIONNAIRE création/modification, MAGASINIER/AUDITEUR lecture |

Exemple catégorie :

```json
{
  "id_categorie": 1,
  "code_categorie": "ORDI",
  "nom_categorie": "Ordinateurs",
  "description": "Matériel informatique",
  "id_famille": 1,
  "statut": true
}
```

### Stock

| Ressource | URL | Rôles |
| --- | --- | --- |
| Magasins | `/api/stock/magasins/` | ADMIN écriture, autres rôles lecture |
| Matériels | `/api/stock/materiels/` | ADMIN tout, GESTIONNAIRE création/modification, MAGASINIER/AUDITEUR lecture |
| Consommables | `/api/stock/consommables/` | ADMIN écriture, autres rôles lecture |

Exemple matériel :

```json
{
  "id_materiel": 1,
  "code_materiel": "MAT-001",
  "id_categorie": 1,
  "id_magasin": 1,
  "numero_serie": "SN-001",
  "marque": "Dell",
  "modele": "Latitude",
  "date_achat": "2026-01-10",
  "prix_achat": "1500.00",
  "devise": "USD",
  "etat": "NEUF",
  "date_enregistrement": "2026-01-10"
}
```

### Operations

| Ressource | URL | Rôles |
| --- | --- | --- |
| Mouvements | `/api/operations/mouvements/` | ADMIN tout, MAGASINIER création, autres rôles lecture selon permissions |
| Affectations | `/api/operations/affectations/` | ADMIN tout, GESTIONNAIRE création/modification, autres lecture |
| Consommations | `/api/operations/consommations/` | ADMIN tout, MAGASINIER création, autres lecture |

Exemple mouvement :

```json
{
  "id_mouvement": 1,
  "id_materiel": null,
  "id_consommable": 1,
  "type_mouvement": "ENTREE",
  "quantite": 10,
  "magasin_destination_id": 1,
  "date_mouvement": "2026-06-24",
  "fait_par": 1,
  "observation": "Entrée initiale"
}
```

### Inventaires

| Ressource | URL | Rôles |
| --- | --- | --- |
| Inventaires | `/api/inventaires/` | ADMIN tout, GESTIONNAIRE création/modification, autres lecture |
| Détails | `/api/inventaires/details/` | ADMIN tout, GESTIONNAIRE création/modification, autres lecture |

### Maintenance

| Ressource | URL | Rôles |
| --- | --- | --- |
| Entretiens | `/api/maintenance/entretiens/` | ADMIN tout, GESTIONNAIRE création/modification, autres lecture |
| Réparations | `/api/maintenance/reparations/` | ADMIN tout, GESTIONNAIRE création/modification, autres lecture |

### Demandes

| Ressource | URL | Rôles |
| --- | --- | --- |
| Demandes | `/api/demandes/` | ADMIN tout, GESTIONNAIRE création/modification, autres lecture |

### Documents

| Ressource | URL | Rôles |
| --- | --- | --- |
| Documents | `/api/documents/` | ADMIN tout, GESTIONNAIRE création, autres lecture |

## 12. Exemples Insomnia

### Login admin

```text
POST /api/auth/login/
```

Body :

```json
{
  "matricule": "ADMIN001",
  "password": "Admin@123"
}
```

### Tester `/me`

```text
GET /api/auth/me/
Authorization: Bearer <access_token>
```

### Tester refresh

```text
POST /api/auth/refresh/
```

Body :

```json
{
  "refresh": "<refresh_token>"
}
```

### Tester auditeur lecture seule

```text
POST /api/auth/login/
```

Body :

```json
{
  "matricule": "AUD001",
  "password": "Test@123"
}
```

Puis :

```text
GET /api/catalogue/categories/
POST /api/catalogue/categories/
```

Le `GET` doit réussir. Le `POST` doit être refusé.

### Tester magasinier

```text
POST /api/auth/login/
```

Body :

```json
{
  "matricule": "MAG001",
  "password": "Test@123"
}
```

Puis :

```text
POST /api/operations/mouvements/
```

### Tester gestionnaire

```text
POST /api/auth/login/
```

Body :

```json
{
  "matricule": "GEST001",
  "password": "Test@123"
}
```

Puis :

```text
POST /api/stock/materiels/
```

## 13. Commandes utiles

Créer et activer l'environnement virtuel :

```powershell
py -m venv env
.\env\Scripts\Activate.ps1
```

Installer les dépendances :

```powershell
py -m pip install -r requirements.txt
```

Vérifier le projet :

```powershell
py manage.py check
```

Lancer le serveur :

```powershell
py manage.py runserver
```

Créer ou mettre à jour les utilisateurs de test :

```powershell
py manage.py create_test_users --password Test@123
```

Ne pas lancer `makemigrations` ou `migrate` pour modifier les tables métier Oracle existantes.

## 14. Sécurité

- Authentification par JWT `access` et `refresh`.
- Le token `access` doit être envoyé avec `Authorization: Bearer <access_token>`.
- `password_hash` n'est jamais exposé dans les serializers de sortie.
- `password` est en `write_only`.
- Les mots de passe sont stockés avec `make_password`.
- Le rôle est toujours lu depuis la base via `USERS.ID_ROLE -> ROLE`.
- `USER_ROLE` n'est pas utilisé en V1.
- Les données texte sont assainies avec `bleach`.
- Le SQL brut est évité. Quand il est nécessaire, il doit être paramétré.
- Les permissions sont vérifiées côté backend.
- Les endpoints sensibles refusent les requêtes sans token.

## 15. Cache

Un cache local `LocMemCache` est configuré pour le développement.

Endpoints principalement cachés :

- données d'organisation ;
- catalogue ;
- rôles ;
- magasins.

Les endpoints dynamiques ou sensibles comme users, mouvements, inventaires, demandes, maintenance et documents ne doivent pas être cachés longtemps.

## 16. TODO

- Ajouter le filtrage par périmètre `SCOPE_TYPE` quand les relations Oracle sont claires.
- Finaliser officiellement le tri `order` si le backend d'ordering DRF n'est pas encore configuré.
- Ajouter des filtres/recherches métier par module.
- Ajouter une documentation OpenAPI/Swagger automatique, par exemple avec `drf-spectacular`.
- Ajouter des tests automatiques complets.
- Finaliser le frontend React.
- Insérer ou valider les données officielles de référence.

