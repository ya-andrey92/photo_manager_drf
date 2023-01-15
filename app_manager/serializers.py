from rest_framework import serializers

from .models import Photo


class PhotoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'image')


class PhotoSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Photo
        fields = '__all__'
        depth = 1
