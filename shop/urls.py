from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register()

urlpatterns = [
    path('', include(router.urls))
]