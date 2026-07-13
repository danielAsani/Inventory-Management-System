from rest_framework.routers import DefaultRouter

from .views import AffectationViewSet, ConsommationViewSet, MouvementStockViewSet

router = DefaultRouter()

router.register("mouvements", MouvementStockViewSet, basename="mouvement")
router.register("affectations", AffectationViewSet, basename="affectation")
router.register("consommations", ConsommationViewSet, basename="consommation")

urlpatterns = router.urls
