from rest_framework.routers import DefaultRouter
from .views import (
    DepartementViewSet,
    DirectionViewSet,
    ServiceViewSet,
)

router = DefaultRouter()

router.register("departements", DepartementViewSet, basename="departement")
router.register("directions", DirectionViewSet, basename="direction")
router.register("services", ServiceViewSet, basename="service")

urlpatterns = router.urls