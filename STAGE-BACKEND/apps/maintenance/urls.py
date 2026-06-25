from rest_framework.routers import DefaultRouter

from .views import EntretienViewSet, ReparationViewSet

router = DefaultRouter()

router.register("entretiens", EntretienViewSet, basename="entretien")
router.register("reparations", ReparationViewSet, basename="reparation")

urlpatterns = router.urls
