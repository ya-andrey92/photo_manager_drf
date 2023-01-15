from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient, override_settings
from rest_framework import status
from django.conf import settings

from PIL import Image
import tempfile
import shutil

from .models import Photo, Geolocation, Human


@override_settings(MEDIA_ROOT=tempfile.mktemp())
class AuthAPITestCase(APITestCase):
    _username = 'test_{}'
    _password = 'test1234qwe'
    _geolocation = 'City'
    _human = 'Andrey_{}'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    def _authorization(self, username: str) -> APIClient:
        url = reverse('jwt-create')
        data = {'username': username, 'password': self._password}
        response = self.client.post(url, data)
        access_token = response.data.get('access')

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        return client

    @classmethod
    def _create_users(cls) -> None:
        for i in range(1, 4):
            User.objects.create_user(username=cls._username.format(i), password=cls._password)

    @classmethod
    def _create_date_manager(cls):
        geolocation = Geolocation.objects.create(name=cls._geolocation)

        humans = []
        for i in range(1, 4):
            humans.append(Human(name=cls._human.format(i)))
        Human.objects.bulk_create(humans)

        for i in range(2, 4):
            for _ in range(3):
                photo = Photo.objects.create(
                    image=cls._create_image().name,
                    user_id=i,
                    description='Test',
                    geolocation=geolocation
                )
                photo.humans.set(humans)

    @staticmethod
    def _create_image():
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)
        return tmp_file


class ManagerTest(AuthAPITestCase):
    __url_photo = reverse('photo-list')
    __name_url_photo_detail = 'photo-detail'

    @classmethod
    def setUpTestData(cls):
        cls._create_users()
        cls._create_date_manager()

    def _data_generation(self):
        data = {
            'image': self._create_image(),
            'description': 'Test text',
            'geolocation_name': "Geo",
            'humans_name': ["human1", "human2"]
        }
        return data

    def test_get_endpoints_photo_if_logout(self):
        response = self.client.get(self.__url_photo)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_endpoints_photo_detail_if_logout(self):
        url = reverse(self.__name_url_photo_detail, kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_photo_with_full_data(self):
        client = self._authorization(self._username.format(1))
        data = self._data_generation()
        response = client.post(self.__url_photo, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_photo_without_metadata(self):
        client = self._authorization(self._username.format(1))
        data = self._data_generation()
        data.pop('geolocation_name')
        data.pop('humans_name')
        data.pop('description')
        response = client.post(self.__url_photo, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_photo_without_image(self):
        client = self._authorization(self._username.format(1))
        data = self._data_generation()
        data.pop('image')
        response = client.post(self.__url_photo, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_list(self):
        client = self._authorization(self._username.format(2))
        count_photo = Photo.objects.filter(user_id=2).count()
        response = client.get(self.__url_photo)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(count_photo, response.json().get('count'))

    def test_get_detail(self):
        client = self._authorization(self._username.format(2))
        photo = Photo.objects.filter(user_id=2).first()
        url = reverse(self.__name_url_photo_detail, kwargs={'pk': photo.id})
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_to_other_people_photo(self):
        client = self._authorization(self._username.format(2))
        photo = Photo.objects.filter(user_id=3).first()
        url = reverse(self.__name_url_photo_detail, kwargs={'pk': photo.id})
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
