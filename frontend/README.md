# Frontend - Gestion Inventaire

Interface React de l'application Gestion Inventaire.

## Stack

- React
- Vite
- React Router
- Axios
- Lucide React
- Oxlint

## Installation

```bash
npm install
copy .env.example .env
npm run dev
```

Configurer `.env` :

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Scripts

```bash
npm run dev
npm run lint
npm run build
npm run preview
```

## Fonctionnalites UI

- tableau de bord ;
- authentification ;
- navigation selon role ;
- pages ressources generiques ;
- affichage en cartes ou tableau ;
- filtres rapides ;
- tri par boutons ;
- modales de detail ;
- notifications de demandes ;
- etude des donnees avec previsions, verification et risques stock.

## Securite

Les tokens sont stockes cote client et supprimes a la deconnexion ou expiration. Le frontend ne contient aucun secret applicatif. L'URL API publique est configuree par variable d'environnement.

