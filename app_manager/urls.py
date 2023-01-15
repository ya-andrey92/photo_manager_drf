from django.urls import path, include
from rest_framework import routers
from .views import PhotoViewSet

router = routers.DefaultRouter()
router.register('photo', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', include(router.urls))
]
