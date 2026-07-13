from rest_framework.routers import DefaultRouter
from .views import MagasinViewset,MaterielViewset, ConsommableViewset

router = DefaultRouter()

router.register("magasins", MagasinViewset, basename="magasin")
router.register("materiels", MaterielViewset, basename="materiel")
router.register("consommables", ConsommableViewset, basename="consommable" )

urlpatterns = router.urls