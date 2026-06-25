from rest_framework.routers import DefaultRouter
from .views import (
    FamilleViewSet,
    CategorieViewSet,
    UniteMesureViewSet,
    FournisseurViewSet,
)

router = DefaultRouter()

router.register("familles", FamilleViewSet, basename="famille")
router.register("categories", CategorieViewSet, basename="categorie")
router.register("unites", UniteMesureViewSet, basename="unite")
router.register("fournisseurs", FournisseurViewSet, basename="fournisseur")

urlpatterns = router.urls