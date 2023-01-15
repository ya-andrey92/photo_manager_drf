from django_filters import filters, FilterSet

from .models import Photo


class PhotoFilter(FilterSet):
    created_at = filters.DateFromToRangeFilter(field_name='created_at', label='created_at')

    class Meta:
        model = Photo
        fields = {
            'geolocation__name': ['iexact', 'in', 'isnull'],
            'humans__name': ['iexact', 'in', 'isnull']
        }
