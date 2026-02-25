from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Vehicle


class VehicleViewsTests(TestCase):

    def setUp(self):
        # Création d’un véhicule
        self.vehicle = Vehicle.objects.create(
            brand="BMW",
            model="M4",
            engine="3.0L",
            year=2022,
            color="Noir",
            mileage=10000,
            vehicle_type="purchase",
            price=70000
        )

        # Création utilisateur
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

    # LIST VIEW

    def test_vehicle_list_page_status(self):
        response = self.client.get(reverse("vehicle_list"))
        self.assertEqual(response.status_code, 200)

    def test_vehicle_in_context(self):
        response = self.client.get(reverse("vehicle_list"))
        self.assertEqual(len(response.context["vehicles"]), 1)

    def test_vehicle_list_contains_vehicle_data(self):
        response = self.client.get(reverse("vehicle_list"))
        self.assertContains(response, "BMW")
        self.assertContains(response, "M4")

    # DETAIL VIEW

    def test_vehicle_detail_page_status(self):
        response = self.client.get(
            reverse("vehicle_detail", args=[self.vehicle.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_vehicle_detail_404(self):
        response = self.client.get(
            reverse("vehicle_detail", args=[999])
        )
        self.assertEqual(response.status_code, 404)

    def test_vehicle_detail_contains_data(self):
        response = self.client.get(
            reverse("vehicle_detail", args=[self.vehicle.id])
        )
        self.assertContains(response, "BMW")
        self.assertContains(response, "M4")
        self.assertContains(response, "70000")

    # RESERVE BUTTON

    def test_reserve_button_redirects_to_login_if_not_authenticated(self):
        response = self.client.get(
            reverse("vehicle_detail", args=[self.vehicle.id])
        )

        self.assertContains(response, "login")

    def test_reserve_button_visible_if_authenticated(self):
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(
            reverse("vehicle_detail", args=[self.vehicle.id])
        )

        self.assertContains(response, "Réserver")