from rest_framework.routers import DefaultRouter

from .views import RoleViewSet, UsersViewSet

router = DefaultRouter()

router.register("users", UsersViewSet, basename="user")
router.register("roles", RoleViewSet, basename="role")

urlpatterns = router.urls
