from django.db import transaction
from rest_framework import serializers

from .models import Photo, Geolocation, Human


class PhotoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'image')


class PhotoSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    geolocation_name = serializers.CharField(max_length=255, required=False,
                                             write_only=True)
    humans_name = serializers.ListField(child=serializers.CharField(max_length=100),
                                        required=False, write_only=True)

    class Meta:
        model = Photo
        fields = ('id', 'image', 'created_at', 'description', 'user', 'geolocation',
                  'geolocation_name', 'humans', 'humans_name')
        read_only_fields = ('geolocation', 'humans')
        depth = 1

    @transaction.atomic
    def create(self, validated_data):
        geolocation = validated_data.pop('geolocation_name', None)
        humans = validated_data.pop('humans_name', None)

        if geolocation:
            geolocation_name = geolocation.strip().capitalize()
            geolocation, _ = Geolocation.objects.get_or_create(name=geolocation_name)
            validated_data['geolocation'] = geolocation

        if humans:
            humans_obj = []
            for human in humans:
                name = human.strip().capitalize()
                human_obj, _ = Human.objects.get_or_create(name=name)
                humans_obj.append(human_obj)
            validated_data['humans'] = humans_obj

        return super().create(validated_data)
