from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Photo
from .serializers import PhotoSerializer, PhotoListSerializer
from .paginations import CustomPagination
from .filters import PhotoFilter


class PhotoViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PhotoFilter

    def get_queryset(self):
        queryset = Photo.objects.filter(user=self.request.user)
        if self.action in ('retrieve', 'create'):
            queryset = queryset.select_related('geolocation')
            queryset = queryset.prefetch_related('humans')
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return PhotoListSerializer
        return PhotoSerializer
