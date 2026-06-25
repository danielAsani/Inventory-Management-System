from rest_framework.routers import DefaultRouter

from .views import InventaireDetailViewSet, InventaireViewSet

router = DefaultRouter()

router.register("details", InventaireDetailViewSet, basename="inventaire-detail")
router.register("", InventaireViewSet, basename="inventaire")

urlpatterns = router.urls
