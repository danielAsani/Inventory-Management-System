# Documentation API - Inventaire SNEL

## 1. URL de base

En développement, l'API est disponible sous :

```text
http://127.0.0.1:8000/api/
```

Toutes les routes décrites ci-dessous sont relatives à cette URL.

Exemple :

```text
GET http://127.0.0.1:8000/api/catalogue/categories/
```

## 2. Authentification

L'API utilise une authentification JWT.

Les endpoints protégés attendent le header suivant :

```text
Authorization: Bearer <access_token>
```

Sans token valide, l'accès est refusé.

### Connexion

```http
POST /api/auth/login/
```

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
  "access": "jwt_access",
  "refresh": "jwt_refresh",
  "user": {
    "id_users": 1,
    "nom_users": "Administrateur SNEL",
    "email": "admin@snel.cd",
    "matricule": "ADMIN001",
    "telephone": "000000000",
    "role": "ADMIN",
    "scope_type": "GENERAL",
    "id_departement": null,
    "id_direction": null,
    "id_service": null,
    "id_magasin": null
  }
}
```

### Rafraîchir le token

```http
POST /api/auth/refresh/
```

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

### Profil connecté

```http
GET /api/auth/me/
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
  "scope_type": "GENERAL",
  "id_departement": null,
  "id_direction": null,
  "id_service": null,
  "id_magasin": null
}
```

### Déconnexion

```http
POST /api/auth/logout/
```

Réponse :

```json
{
  "detail": "Déconnexion réussie. Supprimez le token côté frontend."
}
```

Le backend ne stocke pas de session côté serveur pour cette déconnexion. Le client doit supprimer ses tokens localement.

## 3. Format des requêtes

Les requêtes de création et de modification utilisent généralement le format JSON :

```text
Content-Type: application/json
```

Exemple :

```json
{
  "code_categorie": "ORDI",
  "nom_categorie": "Ordinateurs",
  "description": "Matériel informatique",
  "id_famille": 1,
  "statut": true
}
```

## 4. Format des réponses

### Réponse simple

```json
{
  "id_role": 1,
  "code_role": "ADMIN",
  "nom_role": "Administrateur",
  "description": "Accès complet",
  "statut": true
}
```

### Réponse paginée

Les listes utilisent une pagination commune :

```json
{
  "count": 100,
  "page": 1,
  "perpage": 10,
  "total_pages": 10,
  "results": []
}
```

## 5. Codes HTTP

| Code | Signification |
| --- | --- |
| `200 OK` | Requête réussie |
| `201 Created` | Ressource créée |
| `204 No Content` | Ressource supprimée |
| `400 Bad Request` | Données invalides |
| `403 Forbidden` | Token absent, invalide ou rôle insuffisant |
| `404 Not Found` | Ressource inexistante |
| `500 Internal Server Error` | Erreur serveur non gérée |

## 6. Pagination

Paramètres disponibles sur les endpoints de liste :

| Paramètre | Description | Défaut | Limite |
| --- | --- | --- | --- |
| `page` | Numéro de page | `1` | entier supérieur à 0 |
| `perpage` | Nombre d'éléments par page | `10` | maximum `50` |

Exemple :

```http
GET /api/stock/materiels/?page=1&perpage=10
```

Erreur si `page` n'est pas un entier :

```json
{
  "detail": "Le paramètre page doit être un nombre entier."
}
```

Erreur si `perpage` dépasse la limite :

```json
{
  "detail": "Vous ne pouvez pas demander plus de 50 éléments par page."
}
```

## 7. Tri, recherche et filtres

À l'état actuel du code, aucun backend global de recherche, de filtre ou de tri n'est configuré dans les ViewSets.

Le paramètre `order` peut être prévu côté cahier des charges, mais il n'est pas appliqué globalement par les vues actuelles. Il doit être documenté endpoint par endpoint lorsqu'il sera réellement implémenté.

## 8. Rôles et règles d'accès

Rôles utilisés :

| Rôle | Accès général |
| --- | --- |
| `ADMIN` | Toutes les actions |
| `GESTIONNAIRE` | Actions de gestion selon les modules |
| `MAGASINIER` | Actions de stock selon les modules |
| `AUDITEUR` | Lecture seule |

Méthodes de lecture :

- `GET`
- `HEAD`
- `OPTIONS`

Méthodes d'écriture :

- `POST`
- `PUT`
- `PATCH`
- `DELETE`

Si une action d'écriture n'est pas explicitement ouverte à un rôle dans le ViewSet, elle reste réservée à `ADMIN`.

## 9. Méthodes standard des ressources

Les ressources exposées par `ModelViewSet` suivent les routes standard :

| Méthode | URL | Action |
| --- | --- | --- |
| `GET` | `/ressource/` | Liste paginée |
| `POST` | `/ressource/` | Création |
| `GET` | `/ressource/{id}/` | Détail |
| `PUT` | `/ressource/{id}/` | Remplacement complet |
| `PATCH` | `/ressource/{id}/` | Modification partielle |
| `DELETE` | `/ressource/{id}/` | Suppression |

## 10. Endpoints d'authentification

| Méthode | URL | Description | Accès |
| --- | --- | --- | --- |
| `POST` | `/api/auth/login/` | Connexion JWT | Public |
| `POST` | `/api/auth/refresh/` | Renouvellement du token access | Public avec refresh valide |
| `GET` | `/api/auth/me/` | Profil connecté | Authentifié |
| `POST` | `/api/auth/logout/` | Déconnexion côté client | Authentifié |

## 11. Endpoints comptes

| Ressource | URL | Lecture | Création | Modification | Suppression |
| --- | --- | --- | --- | --- | --- |
| Utilisateurs | `/api/comptes/users/` | `ADMIN`, `AUDITEUR` | `ADMIN` | `ADMIN` | `ADMIN` |
| Rôles | `/api/comptes/roles/` | `ADMIN`, `AUDITEUR` | `ADMIN` | `ADMIN` | `ADMIN` |

Exemple de création d'utilisateur :

```json
{
  "email": "user@snel.cd",
  "nom_users": "Utilisateur SNEL",
  "matricule": "USR001",
  "telephone": "000000000",
  "password": "Test@123",
  "statut": true,
  "id_role": 2,
  "scope_type": "GENERAL",
  "id_departement": null,
  "id_direction": null,
  "id_service": null,
  "id_magasin": null
}
```

Le champ `password` est en écriture seule. Le champ `password_hash` n'est pas retourné par l'API.

## 12. Endpoints organisation

| Ressource | URL | Lecture | Création | Modification | Suppression |
| --- | --- | --- | --- | --- | --- |
| Départements | `/api/organisation/departements/` | Tous les rôles authentifiés | `ADMIN` | `ADMIN` | `ADMIN` |
| Directions | `/api/organisation/directions/` | Tous les rôles authentifiés | `ADMIN` | `ADMIN` | `ADMIN` |
| Services | `/api/organisation/services/` | Tous les rôles authentifiés | `ADMIN` | `ADMIN` | `ADMIN` |

## 13. Endpoints catalogue

| Ressource | URL | Lecture | Création | Modification | Suppression |
| --- | --- | --- | --- | --- | --- |
| Familles | `/api/catalogue/familles/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |
| Catégories | `/api/catalogue/categories/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |
| Unités | `/api/catalogue/unites/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |
| Fournisseurs | `/api/catalogue/fournisseurs/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |

Exemple de catégorie :

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

## 14. Endpoints stock

| Ressource | URL | Lecture | Création | Modification | Suppression |
| --- | --- | --- | --- | --- | --- |
| Magasins | `/api/stock/magasins/` | Tous les rôles authentifiés | `ADMIN` | `ADMIN` | `ADMIN` |
| Matériels | `/api/stock/materiels/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |
| Consommables | `/api/stock/consommables/` | Tous les rôles authentifiés | `ADMIN` | `ADMIN` | `ADMIN` |

Exemple de matériel :

```json
{
  "id_materiel": 1,
  "code_materiel": "MAT-001",
  "id_categorie": 1,
  "id_magasin": 1,
  "id_fournisseur": 1,
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

## 15. Endpoints opérations

| Ressource | URL | Lecture | Création | Modification | Suppression |
| --- | --- | --- | --- | --- | --- |
| Mouvements | `/api/operations/mouvements/` | Tous les rôles authentifiés | `ADMIN`, `MAGASINIER` | `ADMIN` | `ADMIN` |
| Affectations | `/api/operations/affectations/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |
| Consommations | `/api/operations/consommations/` | Tous les rôles authentifiés | `ADMIN`, `MAGASINIER` | `ADMIN` | `ADMIN` |

Exemple de mouvement :

```json
{
  "id_materiel": null,
  "id_consommable": 1,
  "type_mouvement": "ENTREE",
  "quantite": 10,
  "magasin_source": null,
  "magasin_destination": 1,
  "date_mouvement": "2026-06-24",
  "fait_par": 1,
  "reference_document": "BL-001",
  "observation": "Entrée initiale"
}
```

## 16. Endpoints inventaires

| Ressource | URL | Lecture | Création | Modification | Suppression |
| --- | --- | --- | --- | --- | --- |
| Inventaires | `/api/inventaires/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |
| Détails d'inventaire | `/api/inventaires/details/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |

Le champ `ecart` des détails d'inventaire est calculé automatiquement à partir de `quantite_reelle - quantite_theorique`.

## 17. Endpoints maintenance

| Ressource | URL | Lecture | Création | Modification | Suppression |
| --- | --- | --- | --- | --- | --- |
| Entretiens | `/api/maintenance/entretiens/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |
| Réparations | `/api/maintenance/reparations/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |

## 18. Endpoints demandes

| Ressource | URL | Lecture | Création | Modification | Suppression |
| --- | --- | --- | --- | --- | --- |
| Demandes | `/api/demandes/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN`, `GESTIONNAIRE` | `ADMIN` |

## 19. Endpoints documents

| Ressource | URL | Lecture | Création | Modification | Suppression |
| --- | --- | --- | --- | --- | --- |
| Documents | `/api/documents/` | Tous les rôles authentifiés | `ADMIN`, `GESTIONNAIRE` | `ADMIN` | `ADMIN` |

Un document doit être lié à un matériel ou à un consommable.

## 20. Gestion des erreurs

### Token manquant

```json
{
  "detail": "Token manquant."
}
```

### Token invalide ou expiré

```json
{
  "detail": "Token invalide ou expiré."
}
```

### Rôle insuffisant

```json
{
  "detail": "Vous n'avez pas la permission d'effectuer cette action."
}
```

### Identifiants invalides

```json
{
  "non_field_errors": [
    "Identifiants invalides."
  ]
}
```

### Ressource inexistante

```json
{
  "detail": "Not found."
}
```

## 21. Exemples de tests manuels

### Tester le login

```http
POST /api/auth/login/
```

```json
{
  "matricule": "ADMIN001",
  "password": "Admin@123"
}
```

### Tester le profil connecté

```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

### Tester une liste paginée

```http
GET /api/catalogue/categories/?page=1&perpage=10
Authorization: Bearer <access_token>
```

### Tester la lecture seule d'un auditeur

```http
GET /api/catalogue/categories/
Authorization: Bearer <access_token_auditeur>
```

Le `GET` doit réussir.

```http
POST /api/catalogue/categories/
Authorization: Bearer <access_token_auditeur>
Content-Type: application/json
```

Le `POST` doit être refusé.

### Tester une création par gestionnaire

```http
POST /api/stock/materiels/
Authorization: Bearer <access_token_gestionnaire>
Content-Type: application/json
```

### Tester une création par magasinier

```http
POST /api/operations/mouvements/
Authorization: Bearer <access_token_magasinier>
Content-Type: application/json
```
