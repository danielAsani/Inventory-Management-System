import random
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.catalogue.models import Categorie, Famille, Fournisseur, UniteMesure
from apps.comptes.models import Users
from apps.demandes.models import Demande
from apps.documents.models import Document
from apps.inventaires.models import Inventaire, InventaireDetail
from apps.maintenance.models import Entretien, Reparation
from apps.operations.models import Affectation, Consommation, MouvementStock
from apps.organisation.models import Departement, Direction, Service
from apps.stock.models import Consommable, Magasin, Materiel


class Command(BaseCommand):
    help = "Cree un historique operationnel realiste sur environ deux ans."

    def add_arguments(self, parser):
        parser.add_argument("--seed", type=int, default=20260712)
        parser.add_argument("--keep-existing", action="store_true")

    def handle(self, *args, **options):
        random.seed(options["seed"])

        with transaction.atomic():
            call_command("load_fictional_entities", replace=True, verbosity=0)
            call_command("create_initial_users", verbosity=0)

            if not options["keep_existing"]:
                self._clear_previous_history()

            context = self._base_context()
            self._seed_catalogue(context)
            self._seed_magasins(context)
            self._seed_stock(context)
            self._seed_operations(context)
            self._seed_demandes(context)
            self._seed_maintenance(context)
            self._seed_inventaires(context)
            self._seed_documents(context)

        self._print_summary()

    def _clear_previous_history(self):
        Document.objects.filter(numero_document__startswith="HIST-").delete()
        Inventaire.objects.filter(code_inventaire__startswith="HIST-").delete()
        Reparation.objects.filter(observation__startswith="HIST-").delete()
        Entretien.objects.filter(observation__startswith="HIST-").delete()
        Demande.objects.filter(code_demande__startswith="HIST-").delete()
        Consommation.objects.filter(observation__startswith="HIST-").delete()
        MouvementStock.objects.filter(reference_document__startswith="HIST-").delete()
        Affectation.objects.filter(observation__startswith="HIST-").delete()
        Materiel.objects.filter(code_materiel__startswith="HIST-").delete()
        Consommable.objects.filter(code_consommable__startswith="HIST-").delete()
        Magasin.objects.filter(code_magasin__startswith="HIST-").delete()
        Fournisseur.objects.filter(rccm__startswith="HIST-").delete()
        Categorie.objects.filter(code_categorie__startswith="HIST-").delete()
        Famille.objects.filter(code_famille__startswith="HIST-").delete()

    def _base_context(self):
        today = timezone.localdate()
        start = today - timedelta(days=730)
        users = {
            "admin": Users.objects.get(matricule="ADMIN001"),
            "direction": Users.objects.get(matricule="GEST001"),
            "departement": Users.objects.get(matricule="DEP001"),
            "magasin": Users.objects.get(matricule="MAG001"),
        }
        return {
            "today": today,
            "start": start,
            "users": users,
            "departements": list(Departement.objects.filter(statut=True).order_by("code_departement")),
            "directions": list(Direction.objects.filter(statut=True).order_by("code_direction")),
            "services": list(Service.objects.filter(statut=True).order_by("code_service")),
            "familles": [],
            "categories": [],
            "unites": {},
            "fournisseurs": [],
            "magasins": [],
            "materiels": [],
            "consommables": [],
        }

    def _seed_catalogue(self, context):
        familles = [
            ("HIST-ELEC", "Equipements electriques", "Materiels et accessoires electriques"),
            ("HIST-INFO", "Materiel informatique", "Postes, serveurs et accessoires IT"),
            ("HIST-RESEAU", "Reseaux et telecommunications", "Equipements reseaux et telecom"),
            ("HIST-SEC", "Securite et protection", "EPI, controle et securite"),
            ("HIST-OUT", "Outillage technique", "Outils de maintenance et exploitation"),
            ("HIST-BUR", "Fournitures de bureau", "Consommables administratifs"),
            ("HIST-AUTO", "Charroi et accessoires", "Pieces et accessoires vehicules"),
        ]
        for code, name, description in familles:
            famille, _ = Famille.objects.update_or_create(
                code_famille=code,
                defaults={"nom_famille": name, "description": description, "statut": True},
            )
            context["familles"].append(famille)

        categories = [
            ("HIST-TRANSFO", "Transformateurs", "HIST-ELEC"),
            ("HIST-DISJ", "Disjoncteurs", "HIST-ELEC"),
            ("HIST-CABLE", "Cables electriques", "HIST-ELEC"),
            ("HIST-COMPTEUR", "Compteurs electriques", "HIST-ELEC"),
            ("HIST-PC", "Ordinateurs portables", "HIST-INFO"),
            ("HIST-IMP", "Imprimantes", "HIST-INFO"),
            ("HIST-SRV", "Serveurs", "HIST-INFO"),
            ("HIST-OND", "Onduleurs", "HIST-INFO"),
            ("HIST-ROUT", "Routeurs et switches", "HIST-RESEAU"),
            ("HIST-RADIO", "Radios et terminaux", "HIST-RESEAU"),
            ("HIST-CASQ", "Casques et EPI", "HIST-SEC"),
            ("HIST-EXT", "Extincteurs", "HIST-SEC"),
            ("HIST-OUTIL", "Outils specialises", "HIST-OUT"),
            ("HIST-PAP", "Papeterie", "HIST-BUR"),
            ("HIST-TONER", "Toners et cartouches", "HIST-BUR"),
            ("HIST-PNEU", "Pneumatiques", "HIST-AUTO"),
            ("HIST-BATT", "Batteries", "HIST-AUTO"),
        ]
        familles_by_code = {famille.code_famille: famille for famille in context["familles"]}
        for code, name, family_code in categories:
            category, _ = Categorie.objects.update_or_create(
                code_categorie=code,
                defaults={
                    "nom_categorie": name,
                    "description": f"Historique {name.lower()}",
                    "id_famille": familles_by_code[family_code],
                    "statut": True,
                },
            )
            context["categories"].append(category)

        for code, name, symbol in [
            ("PCS", "Piece", "pcs"),
            ("M", "Metre", "m"),
            ("RLX", "Rouleau", "rlx"),
            ("L", "Litre", "l"),
            ("KG", "Kilogramme", "kg"),
            ("BT", "Boite", "bt"),
        ]:
            unit, _ = UniteMesure.objects.update_or_create(
                code_unite=code,
                defaults={"nom_unite": name, "symbole": symbol},
            )
            context["unites"][code] = unit

        fournisseurs = [
            "Congo Electric Supply",
            "Kin Tech Solutions",
            "Global Power Services",
            "Africa Safety Equipements",
            "Electro Maintenance Demo",
            "Bureau Plus Demo",
            "Atlas Industrial Parts",
            "Rivage Telecom",
        ]
        for index, name in enumerate(fournisseurs, start=1):
            supplier, _ = Fournisseur.objects.update_or_create(
                rccm=f"HIST-RCCM-{index:03d}",
                defaults={
                    "nom_fournisseur": name,
                    "email": f"contact{index}@fournisseur-demo.example.com",
                    "adresse": random.choice(["Centre-Nova", "Port-Lumiere", "Montclair", "Rive-Est"]),
                    "nif": f"HIST-NIF-{index:03d}",
                    "statut": True,
                },
            )
            context["fournisseurs"].append(supplier)

    def _seed_magasins(self, context):
        services = context["services"]
        magasins = [
            ("HIST-MAG-CENT", "Magasin central", "Depot central"),
            ("HIST-MAG-TECH", "Magasin technique exploitation", "Zone technique"),
            ("HIST-MAG-INFO", "Magasin informatique", "Siege administratif"),
            ("HIST-MAG-SEC", "Magasin securite et EPI", "Depot securite"),
            ("HIST-MAG-NORD", "Magasin regional Nord", "Centre-Nord"),
            ("HIST-MAG-SUD", "Magasin regional Sud", "Centre-Sud"),
            ("HIST-MAG-EST", "Magasin regional Est", "Centre-Est"),
            ("HIST-MAG-OUEST", "Magasin regional Ouest", "Centre-Ouest"),
        ]
        for index, (code, name, location) in enumerate(magasins):
            magasin, _ = Magasin.objects.update_or_create(
                code_magasin=code,
                defaults={
                    "nom_magasin": name,
                    "id_service": services[index % len(services)],
                    "description_localisation": location,
                    "statut": True,
                },
            )
            context["magasins"].append(magasin)

    def _seed_stock(self, context):
        category_by_code = {category.code_categorie: category for category in context["categories"]}
        materiel_templates = [
            ("TRANSFO", "HIST-TRANSFO", "Schneider", "TRF-250KVA", 8500),
            ("DISJ", "HIST-DISJ", "Legrand", "DX3-400A", 420),
            ("COMP", "HIST-COMPTEUR", "Itron", "ACE6000", 180),
            ("PC", "HIST-PC", "Dell", "Latitude 5440", 950),
            ("IMP", "HIST-IMP", "HP", "LaserJet Pro", 380),
            ("SRV", "HIST-SRV", "HPE", "ProLiant DL360", 4300),
            ("OND", "HIST-OND", "APC", "Smart-UPS 1500", 640),
            ("SW", "HIST-ROUT", "Cisco", "Catalyst 2960", 1200),
            ("RAD", "HIST-RADIO", "Motorola", "DP4400e", 520),
            ("EXT", "HIST-EXT", "Sicli", "CO2 5kg", 75),
            ("OUT", "HIST-OUTIL", "Stanley", "Kit maintenance", 150),
        ]
        for index in range(1, 181):
            prefix, category_code, brand, model, base_price = random.choice(materiel_templates)
            purchase_date = self._random_date(context["start"], context["today"] - timedelta(days=15))
            warranty_months = random.choice([6, 12, 18, 24, 36])
            code = f"HIST-{prefix}-{index:04d}"
            material, _ = Materiel.objects.update_or_create(
                code_materiel=code,
                defaults={
                    "id_categorie": category_by_code[category_code],
                    "id_magasin": random.choice(context["magasins"]),
                    "id_fournisseur": random.choice(context["fournisseurs"]),
                    "numero_serie": f"SN-HIST-{prefix}-{index:05d}",
                    "marque": brand,
                    "modele": model,
                    "date_achat": purchase_date,
                    "date_mise_en_service": purchase_date + timedelta(days=random.randint(1, 45)),
                    "prix_achat": Decimal(base_price + random.randint(-80, 220)),
                    "devise": "USD",
                    "duree_garantie_mois": warranty_months,
                    "garantie_fin": purchase_date + timedelta(days=30 * warranty_months),
                    "etat": Materiel.EtatMateriel.EN_STOCK,
                    "code_barre": f"BAR-HIST-{index:05d}",
                    "qr_code": f"QR-HIST-{index:05d}",
                    "date_enregistrement": purchase_date,
                    "observation": "HIST-Equipement issu du remplissage historique.",
                },
            )
            context["materiels"].append(material)

        consommable_templates = [
            ("CABLE-25", "Cable cuivre 25mm", "HIST-CABLE", "M", 120, 500),
            ("CABLE-50", "Cable cuivre 50mm", "HIST-CABLE", "M", 80, 350),
            ("TONER-HP", "Toner HP LaserJet", "HIST-TONER", "PCS", 10, 45),
            ("PAPIER-A4", "Ramette papier A4", "HIST-PAP", "PCS", 30, 180),
            ("CASQUE", "Casque de securite", "HIST-CASQ", "PCS", 15, 95),
            ("GANTS", "Gants isolants", "HIST-CASQ", "PCS", 20, 130),
            ("PNEU-4X4", "Pneu vehicule intervention", "HIST-PNEU", "PCS", 8, 36),
            ("BAT-12V", "Batterie 12V", "HIST-BATT", "PCS", 6, 28),
            ("RUBAN", "Ruban isolant", "HIST-OUTIL", "PCS", 25, 220),
            ("BOULON", "Boite boulonnerie", "HIST-OUTIL", "BT", 10, 60),
        ]
        for index, (base_code, name, category_code, unit_code, seuil, stock) in enumerate(consommable_templates, start=1):
            for magasin_index, magasin in enumerate(context["magasins"][:4], start=1):
                code = f"HIST-{base_code}-{magasin_index}"
                item, _ = Consommable.objects.update_or_create(
                    code_consommable=code,
                    defaults={
                        "nom_consommable": f"{name} - {magasin.nom_magasin}",
                        "id_categorie": category_by_code[category_code],
                        "id_unite": context["unites"][unit_code],
                        "id_magasin": magasin,
                        "quantite_stock": Decimal(stock + random.randint(-20, 90)),
                        "seuil_alerte": Decimal(seuil),
                        "statut": True,
                    },
                )
                context["consommables"].append(item)

    def _seed_operations(self, context):
        users = context["users"]

        for index, material in enumerate(context["materiels"], start=1):
            MouvementStock.objects.create(
                id_materiel=material,
                type_mouvement=MouvementStock.TypeMouvement.ENTREE,
                quantite=1,
                magasin_destination=material.id_magasin,
                date_mouvement=material.date_achat,
                fait_par=users["magasin"],
                reference_document=f"HIST-BL-MAT-{index:05d}",
                observation="HIST-Entree initiale de materiel.",
            )

            if random.random() < 0.35:
                destination = random.choice([m for m in context["magasins"] if m != material.id_magasin])
                move_date = min(material.date_achat + timedelta(days=random.randint(20, 420)), context["today"])
                MouvementStock.objects.create(
                    id_materiel=material,
                    type_mouvement=MouvementStock.TypeMouvement.TRANSFERT,
                    quantite=1,
                    magasin_source=material.id_magasin,
                    magasin_destination=destination,
                    date_mouvement=move_date,
                    fait_par=users["magasin"],
                    reference_document=f"HIST-TR-MAT-{index:05d}",
                    observation="HIST-Transfert inter-magasin.",
                )
                material.id_magasin = destination
                material.save(update_fields=["id_magasin"])

        for index, item in enumerate(context["consommables"], start=1):
            entries = random.randint(4, 9)
            exits = random.randint(5, 14)
            for entry_number in range(entries):
                qty = random.randint(20, 160)
                MouvementStock.objects.create(
                    id_consommable=item,
                    type_mouvement=MouvementStock.TypeMouvement.ENTREE,
                    quantite=qty,
                    magasin_destination=item.id_magasin,
                    date_mouvement=self._random_date(context["start"], context["today"]),
                    fait_par=users["magasin"],
                    reference_document=f"HIST-BL-CONS-{index:03d}-{entry_number:02d}",
                    observation="HIST-Reapprovisionnement consommable.",
                )
                item.quantite_stock += Decimal(qty)

            for exit_number in range(exits):
                qty = random.randint(1, 25)
                if item.quantite_stock <= qty:
                    continue
                Consommation.objects.create(
                    id_consommable=item,
                    quantite=qty,
                    date_consommation=self._random_date(context["start"], context["today"]),
                    demandeur=random.choice(context["services"]).nom_service[:100],
                    fait_par=users["magasin"],
                    observation=f"HIST-Consommation reguliere #{exit_number + 1}.",
                )
                item.quantite_stock -= Decimal(qty)

            if random.random() < 0.4:
                qty = random.randint(5, 30)
                MouvementStock.objects.create(
                    id_consommable=item,
                    type_mouvement=MouvementStock.TypeMouvement.SORTIE,
                    quantite=qty,
                    magasin_source=item.id_magasin,
                    date_mouvement=self._random_date(context["start"], context["today"]),
                    fait_par=users["magasin"],
                    reference_document=f"HIST-SORT-CONS-{index:03d}",
                    observation="HIST-Sortie exceptionnelle.",
                )
                item.quantite_stock = max(Decimal(0), item.quantite_stock - Decimal(qty))
            item.save(update_fields=["quantite_stock"])

        active_count = 0
        for index, material in enumerate(context["materiels"], start=1):
            if material.etat in {Materiel.EtatMateriel.HORS_SERVICE, Materiel.EtatMateriel.EN_REPARATION}:
                continue
            if random.random() < 0.45:
                assigned_date = self._random_date(max(material.date_achat, context["start"]), context["today"] - timedelta(days=10))
                is_active = active_count < 55 and random.random() < 0.72
                service = random.choice(context["services"])
                affectation = Affectation.objects.create(
                    id_materiel=material,
                    entite_type=Affectation.EntiteType.SERVICE,
                    entite_id=service.id_service,
                    date_affectation=assigned_date,
                    date_retour=None if is_active else assigned_date + timedelta(days=random.randint(20, 330)),
                    statut=Affectation.StatutAffectation.ACTIVE if is_active else Affectation.StatutAffectation.RETOURNEE,
                    observation=f"HIST-Affectation au service {service.nom_service[:80]}.",
                )
                if affectation.statut == Affectation.StatutAffectation.ACTIVE:
                    material.etat = Materiel.EtatMateriel.AFFECTE
                    active_count += 1
                else:
                    material.etat = Materiel.EtatMateriel.EN_STOCK
                material.save(update_fields=["etat"])

    def _seed_demandes(self, context):
        users = context["users"]
        directions = [direction for direction in context["directions"] if direction.id_departement_id]
        services = context["services"]
        statuses = [
            Demande.StatutDemande.TRAITEE,
            Demande.StatutDemande.TRAITEE,
            Demande.StatutDemande.TRAITEE,
            Demande.StatutDemande.REJETEE,
            Demande.StatutDemande.EN_TRAITEMENT_MAGASIN,
            Demande.StatutDemande.EN_ATTENTE_DEPARTEMENT,
        ]
        for index in range(1, 161):
            direction = random.choice(directions)
            service_choices = [service for service in services if service.id_direction_id == direction.id_direction]
            service = random.choice(service_choices) if service_choices and random.random() < 0.72 else None
            request_date = self._random_date(context["start"], context["today"])
            status = random.choice(statuses)
            validation_dt = None
            finalization_dt = None
            validator = None
            finalizer = None
            motif = None
            if status in {
                Demande.StatutDemande.TRAITEE,
                Demande.StatutDemande.REJETEE,
                Demande.StatutDemande.EN_TRAITEMENT_MAGASIN,
            }:
                validation_dt = timezone.make_aware(datetime.combine(request_date + timedelta(days=random.randint(1, 5)), time(hour=10)))
                validator = users["departement"]
            if status == Demande.StatutDemande.TRAITEE:
                finalization_dt = validation_dt + timedelta(days=random.randint(1, 12))
                finalizer = users["magasin"]
            if status == Demande.StatutDemande.REJETEE:
                motif = random.choice([
                    "Budget non disponible.",
                    "Demande a reformuler avec specification technique.",
                    "Besoin deja couvert par le stock disponible.",
                ])
            request_type = random.choice(list(Demande.TypeDemande.values))
            material = random.choice(context["materiels"]) if request_type == Demande.TypeDemande.REPARATION else None
            consumable = random.choice(context["consommables"]) if request_type == Demande.TypeDemande.REAPPROVISIONNEMENT else None
            requested_quantity = random.randint(2, 40) if consumable else 1
            Demande.objects.create(
                code_demande=f"HIST-DEM-{index:05d}",
                id_departement=direction.id_departement,
                id_direction_demandeuse=direction,
                id_service_destinataire=service,
                id_demandeur=users["direction"],
                origine_type=Demande.OrigineType.DIRECTION,
                origine_id=direction.id_direction,
                type_demande=request_type,
                id_materiel=material,
                id_consommable=consumable,
                quantite_demandee=requested_quantity,
                statut=status,
                date_demande=request_date,
                id_validateur_departement=validator,
                date_validation_departement=validation_dt,
                id_magasinier_finalisateur=finalizer,
                date_finalisation=finalization_dt,
                motif_rejet=motif,
                observation=random.choice([
                    "HIST-Besoin operationnel exprime par la direction.",
                    "HIST-Reapprovisionnement programme.",
                    "HIST-Demande liee a la maintenance du reseau.",
                    "HIST-Dotation de service.",
                ]),
            )

    def _seed_maintenance(self, context):
        materials = random.sample(context["materiels"], 95)
        for index, material in enumerate(materials[:70], start=1):
            date_entretien = self._random_date(max(material.date_achat, context["start"]), context["today"])
            status = random.choice([
                Entretien.StatutEntretien.TERMINE,
                Entretien.StatutEntretien.TERMINE,
                Entretien.StatutEntretien.TERMINE,
                Entretien.StatutEntretien.PLANIFIE,
                Entretien.StatutEntretien.ANNULE,
            ])
            end_real = date_entretien + timedelta(days=random.randint(1, 4)) if status == Entretien.StatutEntretien.TERMINE else None
            Entretien.objects.create(
                id_materiel=material,
                date_entretien=date_entretien,
                date_fin_prevue=date_entretien + timedelta(days=random.randint(1, 5)),
                date_fin_reelle=end_real,
                description=random.choice([
                    "Controle preventif periodique.",
                    "Nettoyage et verification technique.",
                    "Remplacement pieces d'usure.",
                    "Controle apres incident mineur.",
                ]),
                cout_entretien=Decimal(random.randint(0, 450)),
                type_entretien=random.choice(list(Entretien.TypeEntretien.values)),
                type_prestataire=random.choice([
                    Entretien.TypePrestataire.INTERNE,
                    Entretien.TypePrestataire.INTERNE,
                    Entretien.TypePrestataire.PRESTATAIRE,
                ]),
                nom_prestataire=random.choice(["Electro Maintenance Demo", "Equipe interne", "Global Power Services"]),
                garantie_entretien_mois=random.choice([None, 1, 3, 6]),
                prochaine_date=date_entretien + timedelta(days=random.randint(90, 240)),
                statut=status,
                observation=f"HIST-Entretien historique #{index}.",
            )

        for index, material in enumerate(materials[70:], start=1):
            date_reparation = self._random_date(max(material.date_achat, context["start"]), context["today"])
            status = random.choice([
                Reparation.StatutReparation.TERMINEE,
                Reparation.StatutReparation.TERMINEE,
                Reparation.StatutReparation.EN_COURS,
                Reparation.StatutReparation.EN_ATTENTE,
            ])
            end_real = date_reparation + timedelta(days=random.randint(2, 14)) if status == Reparation.StatutReparation.TERMINEE else None
            Reparation.objects.create(
                id_materiel=material,
                date_reparation=date_reparation,
                date_fin_prevue=date_reparation + timedelta(days=random.randint(3, 21)),
                date_fin_reelle=end_real,
                description=random.choice([
                    "Diagnostic panne alimentation.",
                    "Remplacement module defectueux.",
                    "Correction defaut de communication.",
                    "Intervention apres surtension.",
                ]),
                cout_reparation=Decimal(random.randint(80, 1800)),
                type_prestataire=random.choice([
                    Reparation.TypePrestataire.INTERNE,
                    Reparation.TypePrestataire.PRESTATAIRE,
                    Reparation.TypePrestataire.CONSTRUCTEUR,
                ]),
                nom_prestataire=random.choice(["Equipe interne", "Global Power Services", "Constructeur agree"]),
                garantie_reparation_mois=random.choice([1, 3, 6, 12]),
                statut=status,
                observation=f"HIST-Reparation historique #{index}.",
            )
            if status == Reparation.StatutReparation.EN_COURS:
                material.etat = Materiel.EtatMateriel.EN_REPARATION
                material.save(update_fields=["etat"])
            elif status == Reparation.StatutReparation.EN_ATTENTE:
                material.etat = Materiel.EtatMateriel.EN_PANNE
                material.save(update_fields=["etat"])

    def _seed_inventaires(self, context):
        users = context["users"]
        for index in range(1, 25):
            magasin = random.choice(context["magasins"])
            start_date = self._random_date(context["start"], context["today"] - timedelta(days=5))
            status = Inventaire.StatutInventaire.TERMINE if index <= 22 else Inventaire.StatutInventaire.EN_COURS
            inventaire = Inventaire.objects.create(
                code_inventaire=f"HIST-INV-{index:04d}",
                entite_type=Inventaire.EntiteType.MAGASIN,
                entite_id=magasin.id_magasin,
                type_inventaire=random.choice([
                    Inventaire.TypeInventaire.PERIODIQUE,
                    Inventaire.TypeInventaire.PARTIEL,
                    Inventaire.TypeInventaire.GENERAL,
                ]),
                date_debut=start_date,
                date_fin=start_date + timedelta(days=random.randint(1, 4)) if status == Inventaire.StatutInventaire.TERMINE else None,
                statut=status,
                effectue_par=users["magasin"],
                observation="HIST-Inventaire physique magasin.",
            )
            materials = [m for m in context["materiels"] if m.id_magasin_id == magasin.id_magasin][:8]
            consumables = [c for c in context["consommables"] if c.id_magasin_id == magasin.id_magasin][:8]
            for material in random.sample(materials, min(len(materials), random.randint(2, 6))):
                InventaireDetail.objects.create(
                    id_inventaire=inventaire,
                    id_materiel=material,
                    quantite_theorique=1,
                    quantite_reelle=random.choice([1, 1, 1, 0]),
                    observation="HIST-Pointage materiel.",
                )
            for item in random.sample(consumables, min(len(consumables), random.randint(3, 7))):
                theoretical = int(item.quantite_stock)
                real = max(0, theoretical + random.choice([-2, -1, 0, 0, 0, 1, 2]))
                InventaireDetail.objects.create(
                    id_inventaire=inventaire,
                    id_consommable=item,
                    quantite_theorique=theoretical,
                    quantite_reelle=real,
                    observation="HIST-Comptage consommable.",
                )

    def _seed_documents(self, context):
        users = context["users"]
        for index, material in enumerate(random.sample(context["materiels"], 120), start=1):
            document_date = timezone.make_aware(
                datetime.combine(self._random_date(material.date_achat, context["today"]), time(hour=random.randint(8, 16)))
            )
            Document.objects.create(
                id_materiel=material,
                cree_par=users["magasin"],
                type_document=random.choice(list(Document.TypeDocument.values)),
                numero_document=f"HIST-DOC-MAT-{index:05d}",
                titre=f"Document {material.code_materiel}",
                chemin_fichier=f"archives/historique/materiels/{material.code_materiel}.pdf",
                mime_type="application/pdf",
                taille_fichier_octets=random.randint(90_000, 2_500_000),
                date_upload=document_date,
                observation="HIST-Document historique materiel.",
            )
        for index, item in enumerate(random.sample(context["consommables"], min(60, len(context["consommables"]))), start=1):
            Document.objects.create(
                id_consommable=item,
                cree_par=users["magasin"],
                type_document=random.choice([Document.TypeDocument.FACTURE, Document.TypeDocument.BON_LIVRAISON, Document.TypeDocument.AUTRE]),
                numero_document=f"HIST-DOC-CONS-{index:05d}",
                titre=f"Document {item.code_consommable}",
                chemin_fichier=f"archives/historique/consommables/{item.code_consommable}.pdf",
                mime_type="application/pdf",
                taille_fichier_octets=random.randint(70_000, 1_400_000),
                date_upload=timezone.now() - timedelta(days=random.randint(0, 730)),
                observation="HIST-Document historique consommable.",
            )

    def _random_date(self, start, end):
        if end < start:
            return start
        return start + timedelta(days=random.randint(0, (end - start).days))

    def _print_summary(self):
        summary = {
            "Departements actifs": Departement.objects.filter(statut=True).count(),
            "Directions actives": Direction.objects.filter(statut=True).count(),
            "Services actifs": Service.objects.filter(statut=True).count(),
            "Familles": Famille.objects.count(),
            "Categories": Categorie.objects.count(),
            "Fournisseurs": Fournisseur.objects.count(),
            "Magasins": Magasin.objects.count(),
            "Materiels": Materiel.objects.count(),
            "Consommables": Consommable.objects.count(),
            "Mouvements": MouvementStock.objects.count(),
            "Affectations": Affectation.objects.count(),
            "Consommations": Consommation.objects.count(),
            "Demandes": Demande.objects.count(),
            "Entretiens": Entretien.objects.count(),
            "Reparations": Reparation.objects.count(),
            "Inventaires": Inventaire.objects.count(),
            "Details inventaire": InventaireDetail.objects.count(),
            "Documents": Document.objects.count(),
        }
        self.stdout.write(self.style.SUCCESS("Historique operationnel genere."))
        for label, value in summary.items():
            self.stdout.write(f"{label}: {value}")
