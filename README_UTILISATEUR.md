# Guide utilisateur - Gestion Inventaire

Ce document presente l'application sans entrer dans le code.

## A quoi sert l'application ?

Gestion Inventaire permet a une organisation de suivre ses biens, ses consommables et ses demandes internes. Elle repond a trois questions simples :

- quel materiel ou consommable existe dans l'organisation ?
- ou se trouve-t-il et dans quel etat est-il ?
- quelle demande est en attente, validee, traitee ou rejetee ?

L'application ajoute aussi une partie analytique pour anticiper les ruptures, verifier les incoherences et suivre l'activite sur plusieurs mois.

## Roles

### Administrateur

L'administrateur configure l'application :

- utilisateurs ;
- roles ;
- departements, directions et services ;
- catalogue ;
- toutes les donnees de stock.

Il a une vue globale.

### Gestion

Le role gestion correspond aux utilisateurs metier rattaches a une direction, un departement ou un service.

Selon son perimetre, un gestionnaire ne voit que les donnees qui le concernent :

- direction : demandes et biens de sa direction ;
- departement : demandes et biens de son departement ;
- service : demandes et biens de son service.

### Magasin

Le magasinier general traite les demandes validees par les departements et finalise les operations de stock.

## Workflow des demandes

1. Une direction cree une demande.
2. La demande est envoyee au departement concerne.
3. Le departement valide ou rejette.
4. Si elle est validee, elle part au magasinier general.
5. Le magasinier finalise.

Types de demandes :

- achat ;
- reapprovisionnement ;
- reparation ;
- autre demande simple.

Pour une reparation, le materiel concerne doit etre identifie. Pour un reapprovisionnement, le consommable et la quantite doivent etre indiques. Pour une demande simple, une observation suffit.

## Modules fonctionnels

### Tableau de bord

Affiche les indicateurs importants :

- total materiels ;
- total consommables ;
- stock disponible ;
- alertes de stock faible ;
- materiels affectes ;
- materiels en reparation ;
- mouvements recents ;
- alertes stock.

### Organisation

Permet de gerer :

- departements ;
- directions ;
- services.

### Catalogue

Permet de classifier les biens :

- familles ;
- categories ;
- unites de mesure ;
- fournisseurs.

### Stock

Permet de suivre :

- magasins ;
- materiels ;
- consommables.

Chaque fiche peut etre ouverte en detail.

### Operations

Permet de suivre :

- mouvements de stock ;
- affectations ;
- consommations.

### Inventaires

Permet de creer des sessions d'inventaire et de comparer les quantites theoriques aux quantites reelles.

### Maintenance

Permet de suivre les entretiens et reparations.

### Etude des donnees

Cette partie aide a analyser l'exploitation :

- risques de rupture ;
- previsions sur plusieurs horizons ;
- verification des incoherences ;
- demandes bloquees ;
- flux de stock ;
- maintenances ouvertes.

Dans l'onglet Verification, chaque domaine est cliquable. L'application affiche ce qu'il faut verifier et les elements concernes.

## Notifications

La cloche de notification signale les demandes a traiter selon le role connecte. Une notification deja traitee ou deja vue peut etre retiree de l'interface sans supprimer la demande de la base.

## Filtres et affichage

Les listes proposent :

- recherche ;
- vue cartes ou tableau ;
- filtres rapides par type, statut ou etat ;
- tri par boutons ;
- details par fiche.

## Donnees

Les donnees locales restent dans la base MySQL. Le depot GitHub ne publie pas les fichiers `.env`, les logs, les caches ou les dumps locaux.

