# Documentation API

Base API :

```text
/api/
```

En local :

```text
http://localhost:8000/api/
```

## Authentification

### Connexion

```http
POST /api/auth/login/
Content-Type: application/json
```

```json
{
  "matricule": "ADMIN001",
  "password": "<mot_de_passe>"
}
```

Reponse :

```json
{
  "access": "<jwt_access>",
  "refresh": "<jwt_refresh>",
  "user": {
    "id_users": 1,
    "matricule": "ADMIN001",
    "nom_users": "Administrateur",
    "role": "ADMIN",
    "scope_type": "GENERAL"
  }
}
```

### Profil connecte

```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

### Rafraichir le token

```http
POST /api/auth/refresh/
Content-Type: application/json
```

```json
{
  "refresh": "<jwt_refresh>"
}
```

### Deconnexion

```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
```

## Pagination

Les endpoints de liste retournent :

```json
{
  "count": 100,
  "page": 1,
  "perpage": 10,
  "total_pages": 10,
  "results": []
}
```

Parametres utiles :

- `page`
- `perpage`
- `search`

## Dashboard

```http
GET /api/dashboard/
Authorization: Bearer <access_token>
```

Retourne les indicateurs, mouvements recents et alertes stock. Les donnees sont filtrees selon le perimetre de l'utilisateur.

## Organisation

Base :

```text
/api/organisation/
```

Ressources :

- `departements/`
- `directions/`
- `services/`

Operations standard :

- `GET /`
- `GET /{id}/`
- `POST /`
- `PATCH /{id}/`
- `DELETE /{id}/`

## Catalogue

Base :

```text
/api/catalogue/
```

Ressources :

- `familles/`
- `categories/`
- `unites/`
- `fournisseurs/`

## Stock

Base :

```text
/api/stock/
```

Ressources :

- `magasins/`
- `materiels/`
- `consommables/`

Le filtrage par perimetre est applique aux magasins, materiels et consommables.

## Operations

Base :

```text
/api/operations/
```

Ressources :

- `mouvements/`
- `affectations/`
- `consommations/`

Regles :

- un mouvement concerne soit un materiel, soit un consommable ;
- une entree exige un magasin destination ;
- une sortie exige un magasin source ;
- un transfert exige une source et une destination differentes ;
- une affectation active met le materiel en etat `AFFECTE` ;
- une restitution remet le materiel en stock.

## Demandes

Base :

```text
/api/demandes/
```

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

Actions :

```http
POST /api/demandes/{id}/valider-departement/
POST /api/demandes/{id}/rejeter-departement/
POST /api/demandes/{id}/finaliser-magasin/
```

Exemple creation :

```json
{
  "code_demande": "DEM-2026-001",
  "type_demande": "REAPPROVISIONNEMENT",
  "id_consommable": 12,
  "quantite_demandee": 20,
  "id_service_destinataire": 5,
  "observation": "Stock faible"
}
```

## Inventaires

Base :

```text
/api/inventaires/
```

Ressources :

- `inventaires/`
- `details/`

## Maintenance

Base :

```text
/api/maintenance/
```

Ressources :

- `entretiens/`
- `reparations/`

## Documents

Base :

```text
/api/documents/
```

Permet de rattacher des references documentaires a un materiel ou a un consommable.

## Erreurs courantes

| Code | Cause probable |
|---|---|
| `400` | donnees invalides ou regle metier non respectee |
| `401` | token manquant, invalide ou expire |
| `403` | role non autorise |
| `404` | ressource introuvable |

