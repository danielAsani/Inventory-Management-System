from django.db.models import F, Q, Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalogue.models import Categorie, Famille, Fournisseur, UniteMesure
from apps.core.permissions import READ_ALL_ROLES, RoleBasedPermission
from apps.organisation.models import Departement, Direction
from apps.operations.models import MouvementStock
from apps.operations.serializers import MouvementStockSerializer
from apps.stock.models import Consommable, Materiel
from apps.stock.views import scoped_stock_queryset


class DashboardStatsView(APIView):
    permission_classes = [RoleBasedPermission]
    role_permissions = {"read": READ_ALL_ROLES}

    def get(self, request):
        materiels = scoped_stock_queryset(
            Materiel.objects.all(),
            request.user,
            include_affectations=True,
        )
        consommables = scoped_stock_queryset(Consommable.objects.all(), request.user)

        stock_total = consommables.aggregate(total=Sum("quantite_stock"))["total"] or 0
        recent_movements = MouvementStock.objects.select_related(
            "id_materiel",
            "id_consommable",
            "fait_par",
        ).filter(
            Q(id_materiel__in=materiels)
            | Q(id_consommable__in=consommables)
        ).order_by("-date_mouvement", "-id_mouvement")[:8]

        stock_alerts = consommables.filter(
            seuil_alerte__isnull=False,
            quantite_stock__lte=F("seuil_alerte"),
        )

        return Response(
            {
                "metrics": {
                    "familles_total": Famille.objects.count(),
                    "categories_total": Categorie.objects.count(),
                    "unites_total": UniteMesure.objects.count(),
                    "fournisseurs_total": Fournisseur.objects.count(),
                    "departements_total": Departement.objects.count(),
                    "directions_total": Direction.objects.count(),
                    "materiels_total": materiels.count(),
                    "consommables_total": consommables.count(),
                    "references_total": materiels.count() + consommables.count(),
                    "stock_disponible": stock_total,
                    "stock_faible": stock_alerts.count(),
                    "materiels_affectes": materiels.filter(statut_stock=Materiel.StatutStock.AFFECTE).count(),
                    "materiels_en_reparation": materiels.filter(
                        etat=Materiel.EtatMateriel.EN_REPARATION
                    ).count(),
                },
                "recent_movements": MouvementStockSerializer(recent_movements, many=True).data,
                "stock_alerts": list(
                    stock_alerts.order_by("quantite_stock")[:8].values(
                        "id_consommable",
                        "code_consommable",
                        "nom_consommable",
                        "quantite_stock",
                        "seuil_alerte",
                    )
                ),
            }
        )
