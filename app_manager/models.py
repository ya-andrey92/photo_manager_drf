from django.db import models
from django.contrib.auth.models import User


class Photo(models.Model):
    image = models.ImageField(upload_to='photo/%Y/%m/%d')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    geolocation = models.ForeignKey('Geolocation', blank=True, null=True,
                                    on_delete=models.SET_NULL)
    humans = models.ManyToManyField('Human', blank=True)

    class Meta:
        ordering = ['-created_at']


class Geolocation(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return f'{self.pk}: {self.name}'


class Human(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return f'{self.pk}: {self.name}'
