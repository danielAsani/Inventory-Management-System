from django.core.management.base import BaseCommand
from django.db import transaction

from apps.organisation.models import Departement, Direction, Service


DATA = [
    {
        "code": "DAD",
        "name": "Departement Administration et Pilotage",
        "directions": [
            {
                "code": "DGO",
                "name": "Direction Gouvernance Operationnelle",
                "services": [
                    ("SGO", "Service coordination generale"),
                    ("SPF", "Service planification fonctionnelle"),
                    ("SQR", "Service qualite et referentiels"),
                    ("SCD", "Service courrier et documentation"),
                ],
            },
            {
                "code": "DJA",
                "name": "Direction Juridique et Assurances",
                "services": [
                    ("SJC", "Service conseil juridique"),
                    ("SCT", "Service contrats et conventions"),
                    ("SLI", "Service litiges internes"),
                    ("SAR", "Service assurances et risques"),
                ],
            },
            {
                "code": "DCM",
                "name": "Direction Communication Institutionnelle",
                "services": [
                    ("SRI", "Service relations internes"),
                    ("SPE", "Service presse et edition"),
                    ("SEN", "Service evenements"),
                ],
            },
        ],
    },
    {
        "code": "DRH",
        "name": "Departement Capital Humain",
        "directions": [
            {
                "code": "DPA",
                "name": "Direction Personnel et Administration",
                "services": [
                    ("SGP", "Service gestion du personnel"),
                    ("SPA", "Service paie et avantages"),
                    ("SPR", "Service presence et rapports"),
                    ("SMD", "Service dossiers administratifs"),
                ],
            },
            {
                "code": "DFC",
                "name": "Direction Formation et Competences",
                "services": [
                    ("SFP", "Service formation professionnelle"),
                    ("SEC", "Service evaluation des competences"),
                    ("SST", "Service stages et tutorat"),
                ],
            },
            {
                "code": "DBS",
                "name": "Direction Bien-etre et Sante au Travail",
                "services": [
                    ("SMS", "Service medico-social"),
                    ("SPS", "Service prevention et securite"),
                    ("SQS", "Service qualite de vie au travail"),
                ],
            },
        ],
    },
    {
        "code": "DFN",
        "name": "Departement Finances et Budget",
        "directions": [
            {
                "code": "DCF",
                "name": "Direction Comptabilite et Fiscalite",
                "services": [
                    ("SCG", "Service comptabilite generale"),
                    ("SCA", "Service comptabilite analytique"),
                    ("SFI", "Service fiscalite"),
                    ("SCL", "Service cloture et reporting"),
                ],
            },
            {
                "code": "DBU",
                "name": "Direction Budget et Controle",
                "services": [
                    ("SBI", "Service budget investissement"),
                    ("SBE", "Service budget exploitation"),
                    ("SCE", "Service controle engagements"),
                ],
            },
            {
                "code": "DTR",
                "name": "Direction Tresorerie",
                "services": [
                    ("SEN", "Service encaissements"),
                    ("SDP", "Service decaissements"),
                    ("SBC", "Service banques et caisse"),
                ],
            },
        ],
    },
    {
        "code": "DLO",
        "name": "Departement Logistique et Approvisionnements",
        "directions": [
            {
                "code": "DAC",
                "name": "Direction Achats et Contrats",
                "services": [
                    ("SAS", "Service achats standards"),
                    ("SAT", "Service achats techniques"),
                    ("SMP", "Service marches et prestataires"),
                    ("SRE", "Service reception documentaire"),
                ],
            },
            {
                "code": "DST",
                "name": "Direction Stocks et Magasins",
                "services": [
                    ("SGS", "Service gestion des stocks"),
                    ("SMC", "Service magasin central"),
                    ("SMR", "Service magasins regionaux"),
                    ("SIN", "Service inventaires"),
                ],
            },
            {
                "code": "DPT",
                "name": "Direction Patrimoine et Transport",
                "services": [
                    ("SPM", "Service patrimoine mobilier"),
                    ("SGV", "Service gestion vehicules"),
                    ("SLV", "Service logistique voyages"),
                ],
            },
        ],
    },
    {
        "code": "DOP",
        "name": "Departement Operations Techniques",
        "directions": [
            {
                "code": "DEX",
                "name": "Direction Exploitation",
                "services": [
                    ("SCO", "Service conduite des operations"),
                    ("SSR", "Service supervision reseau"),
                    ("SPI", "Service preparation interventions"),
                    ("SQC", "Service qualite continuite"),
                ],
            },
            {
                "code": "DMT",
                "name": "Direction Maintenance Technique",
                "services": [
                    ("SMP", "Service maintenance preventive"),
                    ("SMC", "Service maintenance corrective"),
                    ("SAT", "Service ateliers techniques"),
                    ("SPI", "Service pieces critiques"),
                ],
            },
            {
                "code": "DIR",
                "name": "Direction Interventions Regionales",
                "services": [
                    ("SRN", "Service region Nord"),
                    ("SRS", "Service region Sud"),
                    ("SRE", "Service region Est"),
                    ("SRO", "Service region Ouest"),
                    ("SRC", "Service region Centre"),
                ],
            },
        ],
    },
    {
        "code": "DSI",
        "name": "Departement Systemes Numeriques",
        "directions": [
            {
                "code": "DIN",
                "name": "Direction Infrastructure Numerique",
                "services": [
                    ("SRE", "Service reseaux et connectivite"),
                    ("SDC", "Service data center"),
                    ("SPO", "Service postes et outils"),
                    ("SSU", "Service support utilisateurs"),
                ],
            },
            {
                "code": "DAM",
                "name": "Direction Applications Metier",
                "services": [
                    ("SGA", "Service gestion applicative"),
                    ("SIA", "Service integration API"),
                    ("SQA", "Service tests et qualite"),
                    ("SDV", "Service developpement"),
                ],
            },
            {
                "code": "DDS",
                "name": "Direction Donnees et Securite",
                "services": [
                    ("SAN", "Service analyse des donnees"),
                    ("SRP", "Service reporting et pilotage"),
                    ("SSI", "Service securite informatique"),
                    ("SCO", "Service conformite numerique"),
                ],
            },
        ],
    },
    {
        "code": "DCL",
        "name": "Departement Commercial et Relation Client",
        "directions": [
            {
                "code": "DVC",
                "name": "Direction Ventes et Contrats",
                "services": [
                    ("SCO", "Service contrats clients"),
                    ("SVT", "Service ventes terrain"),
                    ("SGC", "Service grands comptes"),
                    ("SOT", "Service offres et tarifs"),
                ],
            },
            {
                "code": "DRC",
                "name": "Direction Relation Client",
                "services": [
                    ("SAC", "Service accueil client"),
                    ("SRC", "Service reclamations"),
                    ("SSF", "Service suivi factures"),
                    ("SEN", "Service enquete satisfaction"),
                ],
            },
            {
                "code": "DRE",
                "name": "Direction Recouvrement",
                "services": [
                    ("SRA", "Service recouvrement amiable"),
                    ("SRC", "Service recouvrement contentieux"),
                    ("SCA", "Service comptes actifs"),
                ],
            },
        ],
    },
    {
        "code": "DPR",
        "name": "Departement Projets et Ingenierie",
        "directions": [
            {
                "code": "DBP",
                "name": "Direction Bureau Projets",
                "services": [
                    ("SPO", "Service portefeuille projets"),
                    ("SPL", "Service planification projets"),
                    ("SBG", "Service budget projets"),
                    ("SRC", "Service risques projets"),
                ],
            },
            {
                "code": "DIN",
                "name": "Direction Ingenierie",
                "services": [
                    ("SET", "Service etudes techniques"),
                    ("SCP", "Service conception plans"),
                    ("SQS", "Service qualite sites"),
                ],
            },
            {
                "code": "DSX",
                "name": "Direction Suivi Execution",
                "services": [
                    ("SCT", "Service controle travaux"),
                    ("SRL", "Service reception livrables"),
                    ("SRA", "Service rapports avancement"),
                ],
            },
        ],
    },
    {
        "code": "DAU",
        "name": "Departement Audit et Maitrise des Risques",
        "directions": [
            {
                "code": "DAI",
                "name": "Direction Audit Interne",
                "services": [
                    ("SOP", "Service audit operations"),
                    ("SAF", "Service audit financier"),
                    ("SAI", "Service audit informatique"),
                ],
            },
            {
                "code": "DRQ",
                "name": "Direction Risques et Qualite",
                "services": [
                    ("SRM", "Service cartographie risques"),
                    ("SCI", "Service controle interne"),
                    ("SQA", "Service qualite processus"),
                ],
            },
            {
                "code": "DCO",
                "name": "Direction Conformite",
                "services": [
                    ("SCR", "Service conformite reglementaire"),
                    ("SET", "Service ethique et transparence"),
                    ("SVE", "Service veille et exigences"),
                ],
            },
        ],
    },
    {
        "code": "DSG",
        "name": "Departement Services Generaux",
        "directions": [
            {
                "code": "DIM",
                "name": "Direction Immobilier et Moyens",
                "services": [
                    ("SIM", "Service immobilier"),
                    ("SEN", "Service entretien bureaux"),
                    ("SFO", "Service fournitures ordinaires"),
                    ("SAC", "Service archives centrales"),
                ],
            },
            {
                "code": "DSU",
                "name": "Direction Surete et Acces",
                "services": [
                    ("SAC", "Service controle acces"),
                    ("SSR", "Service surete des sites"),
                    ("SVI", "Service visiteurs"),
                ],
            },
            {
                "code": "DPS",
                "name": "Direction Protocoles et Support",
                "services": [
                    ("SPC", "Service protocole"),
                    ("SRE", "Service reprographie"),
                    ("SAS", "Service assistance siege"),
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Charge une organisation fictive et neutralise les anciennes entites si demande."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Desactive les departements, directions et services existants avant de charger les donnees fictives.",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options["replace"]:
                Service.objects.update(statut=False)
                Direction.objects.update(statut=False)
                Departement.objects.update(statut=False)

            counts = {"departements": 0, "directions": 0, "services": 0}
            for item in DATA:
                departement, _ = Departement.objects.update_or_create(
                    code_departement=item["code"],
                    defaults={
                        "nom_departement": item["name"],
                        "abreviation": item["code"],
                        "statut": True,
                    },
                )
                counts["departements"] += 1

                for direction_item in item["directions"]:
                    direction, _ = Direction.objects.update_or_create(
                        id_departement=departement,
                        code_direction=direction_item["code"],
                        defaults={
                            "nom_direction": direction_item["name"],
                            "abreviation": direction_item["code"],
                            "statut": True,
                        },
                    )
                    counts["directions"] += 1

                    for service_code, service_name in direction_item["services"]:
                        Service.objects.update_or_create(
                            id_direction=direction,
                            code_service=service_code,
                            defaults={
                                "nom_service": service_name,
                                "abreviation": service_code[:10],
                                "statut": True,
                            },
                        )
                        counts["services"] += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Organisation fictive chargee: "
                f"{counts['departements']} departements, "
                f"{counts['directions']} directions, "
                f"{counts['services']} services."
            )
        )
