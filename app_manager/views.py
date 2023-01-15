from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django_filters.rest_framework import DjangoFilterBackend

from .models import Photo, Human
from .serializers import PhotoSerializer, PhotoListSerializer, AutocompleteSerializer
from .paginations import CustomPagination
from .filters import PhotoFilter


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'photo': reverse('photo-list', request=request, format=format),
        'autocomplete': reverse('autocomplete', request=request, format=format)
    })


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


class AutocompleteApiView(APIView):
    def post(self, request):
        serialiser = AutocompleteSerializer(data=request.data)
        serialiser.is_valid(raise_exception=True)
        name = serialiser.data.get('name').strip()
        humans = Human.objects.filter(name__istartswith=name)
        return Response({'name': [human.name for human in humans]})
