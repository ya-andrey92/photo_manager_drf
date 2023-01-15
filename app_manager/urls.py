from django.urls import path, include
from rest_framework import routers
from .views import api_root, PhotoViewSet, AutocompleteApiView

router = routers.SimpleRouter()
router.register('photo', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', api_root),
    path('', include(router.urls)),
    path('autocomplete/', AutocompleteApiView.as_view(), name='autocomplete'),
]
