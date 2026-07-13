from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.catalogue.models import Categorie, Famille, UniteMesure
from apps.comptes.models import Role, Users
from apps.demandes.models import Demande
from apps.organisation.models import Departement, Direction, Service
from apps.operations.models import Affectation
from apps.stock.models import Consommable, Magasin, Materiel


class AuthDashboardIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role, _ = Role.objects.get_or_create(
            code_role="ADMIN",
            defaults={"nom_role": "Administrateur", "statut": True},
        )
        self.gestionnaire_role, _ = Role.objects.get_or_create(
            code_role="GESTION",
            defaults={"nom_role": "GESTION", "statut": True},
        )
        self.magasin_role, _ = Role.objects.get_or_create(
            code_role="MAGASIN",
            defaults={"nom_role": "MAGASIN", "statut": True},
        )
        self.user = Users.objects.create(
            email="admin.integration@example.com",
            nom_users="Admin Integration",
            matricule="ADMINIT",
            telephone="000000000",
            password_hash=make_password("Integration@2026!"),
            statut=True,
            id_role=self.role,
            scope_type="GENERAL",
        )
        self.gestionnaire = Users.objects.create(
            email="gestion.integration@example.com",
            nom_users="Gestion Integration",
            matricule="GESTIT",
            telephone="000000000",
            password_hash=make_password("Integration@2026!"),
            statut=True,
            id_role=self.gestionnaire_role,
            scope_type="GENERAL",
        )

        self.departement = Departement.objects.create(
            code_departement="INT-DPT",
            nom_departement="Departement Integration",
            statut=True,
        )
        self.direction = Direction.objects.create(
            code_direction="INT-DIR",
            nom_direction="Direction Integration",
            id_departement=self.departement,
            statut=True,
        )
        self.service = Service.objects.create(
            code_service="INT-SRV",
            nom_service="Service Integration",
            id_direction=self.direction,
            statut=True,
        )
        self.magasin = Magasin.objects.create(
            code_magasin="INT-MAG",
            nom_magasin="Magasin Integration",
            id_service=self.service,
            statut=True,
        )
        famille = Famille.objects.create(
            code_famille="INT-FAM",
            nom_famille="Famille Integration",
            statut=True,
        )
        self.categorie = Categorie.objects.create(
            code_categorie="INT-CAT",
            nom_categorie="Categorie Integration",
            id_famille=famille,
            statut=True,
        )
        self.unite = UniteMesure.objects.create(
            code_unite="INT",
            nom_unite="Unite Integration",
            symbole="int",
        )
        self.consommable = Consommable.objects.create(
            code_consommable="INT-CONS",
            nom_consommable="Consommable Integration",
            id_categorie=self.categorie,
            id_unite=self.unite,
            id_magasin=self.magasin,
            quantite_stock=7,
            seuil_alerte=10,
            statut=True,
        )
        self.materiel = Materiel.objects.create(
            code_materiel="INT-MAT",
            id_categorie=self.categorie,
            id_magasin=self.magasin,
            numero_serie="INT-SERIAL",
            marque="Integration",
            modele="Model",
            date_achat=timezone.localdate(),
            prix_achat=100,
            code_barre="INT-BAR",
            qr_code="INT-QR",
            etat=Materiel.EtatMateriel.EN_STOCK,
        )

        self.direction_user = Users.objects.create(
            email="direction.integration@example.com",
            nom_users="Direction Integration",
            matricule="DIRIT",
            telephone="000000000",
            password_hash=make_password("Integration@2026!"),
            statut=True,
            id_role=self.gestionnaire_role,
            scope_type="DIRECTION",
            id_direction=self.direction,
        )
        self.department_user = Users.objects.create(
            email="departement.integration@example.com",
            nom_users="Departement Integration",
            matricule="DPTIT",
            telephone="000000000",
            password_hash=make_password("Integration@2026!"),
            statut=True,
            id_role=self.gestionnaire_role,
            scope_type="DEPARTEMENT",
            id_departement=self.departement,
        )
        self.storekeeper = Users.objects.create(
            email="magasin.integration@example.com",
            nom_users="Magasin Integration",
            matricule="MAGIT",
            telephone="000000000",
            password_hash=make_password("Integration@2026!"),
            statut=True,
            id_role=self.magasin_role,
            scope_type="GENERAL",
        )

    def test_login_me_dashboard_and_protected_list(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {"matricule": "ADMINIT", "password": "Integration@2026!"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data)
        self.assertEqual(login_response.data["user"]["role"], "ADMIN")

        token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        me_response = self.client.get("/api/auth/me/")
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data["matricule"], "ADMINIT")

        dashboard_response = self.client.get("/api/dashboard/")
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(dashboard_response.data["metrics"]["materiels_total"], 1)
        self.assertEqual(dashboard_response.data["metrics"]["consommables_total"], 1)
        self.assertEqual(dashboard_response.data["metrics"]["stock_faible"], 1)

        materiels_response = self.client.get("/api/stock/materiels/")
        self.assertEqual(materiels_response.status_code, 200)
        self.assertEqual(materiels_response.data["count"], 1)

    def test_protected_endpoint_without_token_is_rejected(self):
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Token manquant.")

    def test_gestionnaire_has_operational_permissions_but_not_admin_ui_permissions(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {"matricule": "GESTIT", "password": "Integration@2026!"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.data["user"]["role"], "GESTION")

        token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        movement_response = self.client.post(
            "/api/operations/mouvements/",
            {
                "id_consommable": self.consommable.id_consommable,
                "type_mouvement": "ENTREE",
                "quantite": 1,
                "magasin_destination": self.magasin.id_magasin,
            },
            format="json",
        )
        self.assertEqual(movement_response.status_code, 201)

        users_response = self.client.get("/api/comptes/users/")
        self.assertEqual(users_response.status_code, 403)

        catalogue_write_response = self.client.post(
            "/api/catalogue/familles/",
            {
                "code_famille": "GEST-CAT",
                "nom_famille": "Catalogue Gestionnaire",
                "statut": True,
            },
            format="json",
        )
        self.assertEqual(catalogue_write_response.status_code, 403)

    def test_stock_movements_and_consumptions_update_quantity(self):
        token = self._login_as_gestionnaire()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        movement_response = self.client.post(
            "/api/operations/mouvements/",
            {
                "id_consommable": self.consommable.id_consommable,
                "type_mouvement": "SORTIE",
                "quantite": 2,
                "magasin_source": self.magasin.id_magasin,
            },
            format="json",
        )
        self.assertEqual(movement_response.status_code, 201)
        self.consommable.refresh_from_db()
        self.assertEqual(self.consommable.quantite_stock, 5)

        consumption_response = self.client.post(
            "/api/operations/consommations/",
            {
                "id_consommable": self.consommable.id_consommable,
                "quantite": 3,
                "demandeur": "Service Integration",
            },
            format="json",
        )
        self.assertEqual(consumption_response.status_code, 201)
        self.consommable.refresh_from_db()
        self.assertEqual(self.consommable.quantite_stock, 2)

        over_stock_response = self.client.post(
            "/api/operations/consommations/",
            {
                "id_consommable": self.consommable.id_consommable,
                "quantite": 3,
                "demandeur": "Service Integration",
            },
            format="json",
        )
        self.assertEqual(over_stock_response.status_code, 400)
        self.consommable.refresh_from_db()
        self.assertEqual(self.consommable.quantite_stock, 2)

    def test_affectation_updates_material_state_and_blocks_duplicates(self):
        token = self._login_as_gestionnaire()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        affectation_response = self.client.post(
            "/api/operations/affectations/",
            {
                "id_materiel": self.materiel.id_materiel,
                "entite_type": "SERVICE",
                "entite_id": self.service.id_service,
                "statut": "ACTIVE",
            },
            format="json",
        )
        self.assertEqual(affectation_response.status_code, 201)
        self.materiel.refresh_from_db()
        self.assertEqual(self.materiel.etat, Materiel.EtatMateriel.AFFECTE)

        duplicate_response = self.client.post(
            "/api/operations/affectations/",
            {
                "id_materiel": self.materiel.id_materiel,
                "entite_type": "SERVICE",
                "entite_id": self.service.id_service,
                "statut": "ACTIVE",
            },
            format="json",
        )
        self.assertEqual(duplicate_response.status_code, 400)

        affectation_id = affectation_response.data["id_affectation"]
        return_response = self.client.patch(
            f"/api/operations/affectations/{affectation_id}/",
            {
                "statut": Affectation.StatutAffectation.RETOURNEE,
                "date_retour": timezone.localdate(),
            },
            format="json",
        )
        self.assertEqual(return_response.status_code, 200)
        self.materiel.refresh_from_db()
        self.assertEqual(self.materiel.etat, Materiel.EtatMateriel.EN_STOCK)

    def test_direction_department_store_request_workflow(self):
        token = self._login("DIRIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        create_response = self.client.post(
            "/api/demandes/",
            {
                "code_demande": "DEM-INT-001",
                "id_service_destinataire": self.service.id_service,
                "type_demande": "ACHAT",
                "observation": "Besoin direction",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.data["statut"], Demande.StatutDemande.EN_ATTENTE_DEPARTEMENT)
        self.assertEqual(create_response.data["id_direction_demandeuse"], self.direction.id_direction)
        self.assertEqual(create_response.data["id_departement"], self.departement.id_departement)

        demande_id = create_response.data["id_demande"]

        token = self._login("DPTIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        validate_response = self.client.post(
            f"/api/demandes/{demande_id}/valider-departement/",
            {},
            format="json",
        )
        self.assertEqual(validate_response.status_code, 200)
        self.assertEqual(validate_response.data["statut"], Demande.StatutDemande.EN_TRAITEMENT_MAGASIN)

        token = self._login("MAGIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        finalize_response = self.client.post(
            f"/api/demandes/{demande_id}/finaliser-magasin/",
            {},
            format="json",
        )
        self.assertEqual(finalize_response.status_code, 200)
        self.assertEqual(finalize_response.data["statut"], Demande.StatutDemande.TRAITEE)

    def test_department_user_cannot_create_request(self):
        token = self._login("DPTIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(
            "/api/demandes/",
            {
                "code_demande": "DEM-INT-002",
                "id_service_destinataire": self.service.id_service,
                "type_demande": "ACHAT",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_direction_can_create_request_without_target_service(self):
        token = self._login("DIRIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(
            "/api/demandes/",
            {
                "code_demande": "DEM-INT-003",
                "type_demande": "ACHAT",
                "observation": "Besoin sans service precis",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.data["id_service_destinataire"])
        self.assertEqual(response.data["id_direction_demandeuse"], self.direction.id_direction)
        self.assertEqual(response.data["id_departement"], self.departement.id_departement)

    def test_simple_request_can_use_observation_only(self):
        token = self._login("DIRIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(
            "/api/demandes/",
            {
                "code_demande": "DEM-INT-SIMPLE",
                "type_demande": "AUTRE",
                "observation": "Besoin simple a analyser par le departement.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.data["id_materiel"])
        self.assertIsNone(response.data["id_consommable"])

    def test_repair_and_restock_requests_must_identify_target_item(self):
        token = self._login("DIRIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        repair_without_material = self.client.post(
            "/api/demandes/",
            {
                "code_demande": "DEM-INT-REP-FAIL",
                "type_demande": "REPARATION",
                "observation": "Materiel en panne.",
            },
            format="json",
        )
        self.assertEqual(repair_without_material.status_code, 400)

        repair_with_material = self.client.post(
            "/api/demandes/",
            {
                "code_demande": "DEM-INT-REP-OK",
                "type_demande": "REPARATION",
                "id_materiel": self.materiel.id_materiel,
                "observation": "Materiel en panne.",
            },
            format="json",
        )
        self.assertEqual(repair_with_material.status_code, 201)
        self.assertEqual(repair_with_material.data["id_materiel"], self.materiel.id_materiel)

        restock_without_consumable = self.client.post(
            "/api/demandes/",
            {
                "code_demande": "DEM-INT-REA-FAIL",
                "type_demande": "REAPPROVISIONNEMENT",
                "quantite_demandee": 5,
                "observation": "Stock faible.",
            },
            format="json",
        )
        self.assertEqual(restock_without_consumable.status_code, 400)

        restock_with_consumable = self.client.post(
            "/api/demandes/",
            {
                "code_demande": "DEM-INT-REA-OK",
                "type_demande": "REAPPROVISIONNEMENT",
                "id_consommable": self.consommable.id_consommable,
                "quantite_demandee": 5,
                "observation": "Stock faible.",
            },
            format="json",
        )
        self.assertEqual(restock_with_consumable.status_code, 201)
        self.assertEqual(restock_with_consumable.data["id_consommable"], self.consommable.id_consommable)
        self.assertEqual(restock_with_consumable.data["quantite_demandee"], 5)

    def test_request_list_is_scoped_by_user_perimeter(self):
        sibling_direction = Direction.objects.create(
            code_direction="INT-DIR-2",
            nom_direction="Direction Integration 2",
            id_departement=self.departement,
            statut=True,
        )
        other_department = Departement.objects.create(
            code_departement="INT-DPT-2",
            nom_departement="Departement Integration 2",
            statut=True,
        )
        other_direction = Direction.objects.create(
            code_direction="INT-DIR-3",
            nom_direction="Direction Integration 3",
            id_departement=other_department,
            statut=True,
        )
        own_request = Demande.objects.create(
            code_demande="DEM-SCOPE-OWN",
            id_departement=self.departement,
            id_direction_demandeuse=self.direction,
            origine_type=Demande.OrigineType.DIRECTION,
            origine_id=self.direction.id_direction,
            type_demande=Demande.TypeDemande.ACHAT,
            id_demandeur=self.direction_user,
        )
        sibling_request = Demande.objects.create(
            code_demande="DEM-SCOPE-SIBLING",
            id_departement=self.departement,
            id_direction_demandeuse=sibling_direction,
            origine_type=Demande.OrigineType.DIRECTION,
            origine_id=sibling_direction.id_direction,
            type_demande=Demande.TypeDemande.REAPPROVISIONNEMENT,
            id_demandeur=self.user,
        )
        other_request = Demande.objects.create(
            code_demande="DEM-SCOPE-OTHER",
            id_departement=other_department,
            id_direction_demandeuse=other_direction,
            origine_type=Demande.OrigineType.DIRECTION,
            origine_id=other_direction.id_direction,
            type_demande=Demande.TypeDemande.AUTRE,
            id_demandeur=self.user,
        )

        token = self._login("DIRIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        direction_response = self.client.get("/api/demandes/")
        self.assertEqual(direction_response.status_code, 200)
        direction_ids = {item["id_demande"] for item in direction_response.data["results"]}
        self.assertEqual(direction_ids, {own_request.id_demande})

        token = self._login("DPTIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        department_response = self.client.get("/api/demandes/")
        self.assertEqual(department_response.status_code, 200)
        department_ids = {item["id_demande"] for item in department_response.data["results"]}
        self.assertEqual(department_ids, {own_request.id_demande, sibling_request.id_demande})
        self.assertNotIn(other_request.id_demande, department_ids)

        token = self._login("MAGIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        store_response = self.client.get("/api/demandes/")
        self.assertEqual(store_response.status_code, 200)
        self.assertEqual(store_response.data["count"], 3)

    def test_stock_lists_are_scoped_by_gestionnaire_perimeter(self):
        other_department = Departement.objects.create(
            code_departement="INT-STK-DPT",
            nom_departement="Departement Stock Autre",
            statut=True,
        )
        other_direction = Direction.objects.create(
            code_direction="INT-STK-DIR",
            nom_direction="Direction Stock Autre",
            id_departement=other_department,
            statut=True,
        )
        other_service = Service.objects.create(
            code_service="INT-STK-SRV",
            nom_service="Service Stock Autre",
            id_direction=other_direction,
            statut=True,
        )
        other_magasin = Magasin.objects.create(
            code_magasin="INT-STK-MAG",
            nom_magasin="Magasin Stock Autre",
            id_service=other_service,
            statut=True,
        )
        other_materiel = Materiel.objects.create(
            code_materiel="INT-MAT-OTHER",
            id_categorie=self.categorie,
            id_magasin=other_magasin,
            numero_serie="INT-SERIAL-OTHER",
            marque="Autre",
            modele="Model",
            date_achat=timezone.localdate(),
            prix_achat=100,
            code_barre="INT-BAR-OTHER",
            qr_code="INT-QR-OTHER",
            etat=Materiel.EtatMateriel.EN_STOCK,
        )
        other_consommable = Consommable.objects.create(
            code_consommable="INT-CONS-OTHER",
            nom_consommable="Consommable Autre",
            id_categorie=self.categorie,
            id_unite=self.unite,
            id_magasin=other_magasin,
            quantite_stock=12,
            seuil_alerte=3,
            statut=True,
        )
        assigned_materiel = Materiel.objects.create(
            code_materiel="INT-MAT-AFFECTE",
            id_categorie=self.categorie,
            id_magasin=None,
            numero_serie="INT-SERIAL-AFFECTE",
            marque="Affecte",
            modele="Service",
            date_achat=timezone.localdate(),
            prix_achat=120,
            code_barre="INT-BAR-AFFECTE",
            qr_code="INT-QR-AFFECTE",
            etat=Materiel.EtatMateriel.AFFECTE,
        )
        Affectation.objects.create(
            id_materiel=assigned_materiel,
            entite_type=Affectation.EntiteType.SERVICE,
            entite_id=self.service.id_service,
            statut=Affectation.StatutAffectation.ACTIVE,
        )

        token = self._login("DIRIT")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        materiels_response = self.client.get("/api/stock/materiels/")
        self.assertEqual(materiels_response.status_code, 200)
        materiel_ids = {item["id_materiel"] for item in materiels_response.data["results"]}
        self.assertIn(self.materiel.id_materiel, materiel_ids)
        self.assertIn(assigned_materiel.id_materiel, materiel_ids)
        self.assertNotIn(other_materiel.id_materiel, materiel_ids)

        consommables_response = self.client.get("/api/stock/consommables/")
        self.assertEqual(consommables_response.status_code, 200)
        consommable_ids = {item["id_consommable"] for item in consommables_response.data["results"]}
        self.assertIn(self.consommable.id_consommable, consommable_ids)
        self.assertNotIn(other_consommable.id_consommable, consommable_ids)

        magasins_response = self.client.get("/api/stock/magasins/")
        self.assertEqual(magasins_response.status_code, 200)
        magasin_ids = {item["id_magasin"] for item in magasins_response.data["results"]}
        self.assertIn(self.magasin.id_magasin, magasin_ids)
        self.assertNotIn(other_magasin.id_magasin, magasin_ids)

        dashboard_response = self.client.get("/api/dashboard/")
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(dashboard_response.data["metrics"]["materiels_total"], 2)
        self.assertEqual(dashboard_response.data["metrics"]["consommables_total"], 1)
        self.assertEqual(dashboard_response.data["metrics"]["stock_disponible"], 7)

    def _login_as_gestionnaire(self):
        return self._login("GESTIT")

    def _login(self, matricule):
        login_response = self.client.post(
            "/api/auth/login/",
            {"matricule": matricule, "password": "Integration@2026!"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        return login_response.data["access"]
