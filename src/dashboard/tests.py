from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from vehicles.models import Vehicle
from accounts.models import Profile


class CreateVehicleTests(TestCase):

    def setUp(self):
        self.url = reverse("create_vehicle")

        # Utilisateur PRO
        self.pro_user = User.objects.create_user(
            username="pro_user",
            password="Testpassword123"
        )
        Profile.objects.create(user=self.pro_user, role="pro")

        # Utilisateur CLIENT
        self.client_user = User.objects.create_user(
            username="client_user",
            password="Testpassword123"
        )
        Profile.objects.create(user=self.client_user, role="client")

        self.valid_data = {
            "brand": "BMW",
            "model": "Série 3",
            "engine": "2.0 Diesel",
            "year": 2022,
            "color": "Noir",
            "mileage": 15000,
            "vehicle_type": "purchase",
            "price": 25000.00,
        }

    # Un pro peut créer un véhicule
    def test_pro_can_create_vehicle(self):
        self.client.login(username="pro_user", password="Testpassword123")

        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vehicle.objects.count(), 1)

        vehicle = Vehicle.objects.first()
        self.assertEqual(vehicle.brand, "BMW")
        self.assertEqual(vehicle.vehicle_type, "purchase")

    # Un client ne peut pas créer de véhicule
    def test_client_cannot_create_vehicle(self):
        self.client.login(username="client_user", password="Testpassword123")

        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Vehicle.objects.count(), 0)

    # Un utilisateur non connecté est redirigé
    def test_anonymous_user_redirected(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vehicle.objects.count(), 0)

    # Données invalides → pas de création
    def test_invalid_data_does_not_create_vehicle(self):
        self.client.login(username="pro_user", password="Testpassword123")

        invalid_data = self.valid_data.copy()
        invalid_data["year"] = ""  # champ requis vide

        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vehicle.objects.count(), 0)
