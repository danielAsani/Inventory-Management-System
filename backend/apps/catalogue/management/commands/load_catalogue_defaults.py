from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalogue.models import Categorie, Famille, Fournisseur, UniteMesure


FAMILIES = [
    ("FAM-INFO", "Materiel informatique", "Ordinateurs, imprimantes et accessoires IT"),
    ("FAM-RESEAU", "Reseaux et telecom", "Equipements reseau, connectivite et communication"),
    ("FAM-ELEC", "Equipements electriques", "Materiels et accessoires electriques"),
    ("FAM-BUR", "Fournitures de bureau", "Papeterie et consommables administratifs"),
    ("FAM-EPI", "Equipements de protection", "Equipements de protection individuelle"),
]

CATEGORIES = [
    ("CAT-PC", "Ordinateurs", "FAM-INFO"),
    ("CAT-IMP", "Imprimantes et scanners", "FAM-INFO"),
    ("CAT-ACC-IT", "Accessoires informatiques", "FAM-INFO"),
    ("CAT-SWITCH", "Switches et routeurs", "FAM-RESEAU"),
    ("CAT-CABLE-RJ", "Cables reseau", "FAM-RESEAU"),
    ("CAT-OND", "Onduleurs", "FAM-ELEC"),
    ("CAT-CABLE-ELEC", "Cables electriques", "FAM-ELEC"),
    ("CAT-PAP", "Papeterie", "FAM-BUR"),
    ("CAT-TONER", "Toners et cartouches", "FAM-BUR"),
    ("CAT-CASQUE", "Casques et gants", "FAM-EPI"),
]

UNITS = [
    ("PCS", "Piece", "PCS"),
    ("BT", "Boite", "BT"),
    ("PAQ", "Paquet", "PAQ"),
    ("M", "Metre", "M"),
    ("RLX", "Rouleau", "RLX"),
    ("KG", "Kilogramme", "KG"),
    ("L", "Litre", "L"),
]

SUPPLIERS = [
    ("Congo Tech Supply", "contact@congotechsupply.example.com", "Kinshasa Gombe", "RCCM-CD-001", "NIF-CD-001"),
    ("Kin Equipements", "vente@kinequipements.example.com", "Kinshasa Limete", "RCCM-CD-002", "NIF-CD-002"),
    ("Africa Office Plus", "contact@africaofficeplus.example.com", "Kinshasa Ngaliema", "RCCM-CD-003", "NIF-CD-003"),
    ("Electro Services RDC", "support@electroservicesrdc.example.com", "Kinshasa Barumbu", "RCCM-CD-004", "NIF-CD-004"),
    ("Safety Pro Distribution", "info@safetypro.example.com", "Kinshasa Lingwala", "RCCM-CD-005", "NIF-CD-005"),
]


class Command(BaseCommand):
    help = "Ajoute quelques donnees de base pour le catalogue."

    def handle(self, *args, **options):
        with transaction.atomic():
            families_by_code = {}
            for code, name, description in FAMILIES:
                family, _ = Famille.objects.update_or_create(
                    code_famille=code,
                    defaults={"nom_famille": name, "description": description, "statut": True},
                )
                families_by_code[code] = family

            for code, name, family_code in CATEGORIES:
                Categorie.objects.update_or_create(
                    code_categorie=code,
                    defaults={
                        "nom_categorie": name,
                        "description": f"Articles de type {name.lower()}",
                        "id_famille": families_by_code[family_code],
                        "statut": True,
                    },
                )

            for code, name, symbol in UNITS:
                UniteMesure.objects.update_or_create(
                    code_unite=code,
                    defaults={"nom_unite": name, "symbole": symbol},
                )

            for name, email, address, rccm, nif in SUPPLIERS:
                Fournisseur.objects.update_or_create(
                    rccm=rccm,
                    defaults={
                        "nom_fournisseur": name,
                        "email": email,
                        "adresse": address,
                        "nif": nif,
                        "statut": True,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Catalogue par defaut charge: "
                f"{len(FAMILIES)} familles, {len(CATEGORIES)} categories, "
                f"{len(UNITS)} unites, {len(SUPPLIERS)} fournisseurs."
            )
        )
