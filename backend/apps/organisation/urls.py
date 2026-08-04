from rest_framework.routers import DefaultRouter
from .views import (
    DepartementViewSet,
    DirectionViewSet,
)

router = DefaultRouter()

router.register("departements", DepartementViewSet, basename="departement")
router.register("directions", DirectionViewSet, basename="direction")

urlpatterns = router.urls
