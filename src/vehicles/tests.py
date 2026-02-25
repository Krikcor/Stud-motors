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


from django.test import TestCase
from django.urls import reverse
from .models import Vehicle


class VehicleFilterTests(TestCase):

    def setUp(self):
        # Véhicules
        self.v1 = Vehicle.objects.create(
            brand="BMW",
            model="Serie 1",
            year=2020,
            mileage=50000,
            price=20000,
            vehicle_type="purchase"
        )

        self.v2 = Vehicle.objects.create(
            brand="Yamaha",
            model="MT-07",
            year=2022,
            mileage=10000,
            price=7500,
            vehicle_type="rental"
        )

        self.v3 = Vehicle.objects.create(
            brand="Audi",
            model="A4",
            year=2018,
            mileage=80000,
            price=15000,
            vehicle_type="purchase"
        )

    # Test filtre par type

    def test_filter_by_vehicle_type(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"vehicle_type": "purchase"}  # valeur correcte du model
        )

        self.assertEqual(response.status_code, 200)

        # Doit apparaître (purchase)
        self.assertContains(response, "BMW")
        self.assertContains(response, "Audi")

        # Ne doit pas apparaître (rental)
        self.assertNotContains(response, "Yamaha")

    # Test filtre par année

    def test_filter_by_year(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"year": 2022}
        )

        self.assertContains(response, "Yamaha")
        self.assertNotContains(response, "BMW")
        self.assertNotContains(response, "Audi")

    # Test prix minimum

    def test_filter_by_min_price(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"min_price": 16000}
        )

        self.assertContains(response, "BMW")
        self.assertNotContains(response, "Audi")
        self.assertNotContains(response, "Yamaha")

    # Test prix maximum

    def test_filter_by_max_price(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"max_price": 16000}
        )

        self.assertContains(response, "Audi")
        self.assertContains(response, "Yamaha")
        self.assertNotContains(response, "BMW")

    # Test combinaison filtres
    def test_filter_combination(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {
                "vehicle_type": "car",
                "min_price": 18000
            }
        )

        self.assertContains(response, "BMW")
        self.assertNotContains(response, "Audi")
        self.assertNotContains(response, "Yamaha")