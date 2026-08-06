from rest_framework.routers import DefaultRouter

from .views import ConsommableViewset, MaterielViewset

router = DefaultRouter()

router.register("materiels", MaterielViewset, basename="materiel")
router.register("consommables", ConsommableViewset, basename="consommable")

urlpatterns = router.urls
