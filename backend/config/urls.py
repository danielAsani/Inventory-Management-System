from django.contrib import admin
from django.urls import path, include
from apps.core.views import DashboardStatsView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/dashboard/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("api/organisation/", include("apps.organisation.urls")),
    path("api/catalogue/", include("apps.catalogue.urls")),
    path("api/stock/", include("apps.stock.urls")),
    path("api/auth/", include("apps.comptes.auth_urls")),
    path("api/comptes/", include("apps.comptes.urls")),
    path("api/operations/", include("apps.operations.urls")),
    path("api/inventaires/", include("apps.inventaires.urls")),
    path("api/maintenance/", include("apps.maintenance.urls")),
    path("api/demandes/", include("apps.demandes.urls")),
    path("api/documents/", include("apps.documents.urls")),
]
