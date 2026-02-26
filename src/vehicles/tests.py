from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Vehicle


class VehicleViewsTests(TestCase):

    def setUp(self):
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
            reverse("vehicle_detail", args=[self.vehicle.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_vehicle_detail_404(self):
        response = self.client.get(
            reverse("vehicle_detail", args=[999])
        )
        self.assertEqual(response.status_code, 404)

    def test_vehicle_detail_contains_data(self):
        response = self.client.get(
            reverse("vehicle_detail", args=[self.vehicle.slug])
        )
        self.assertContains(response, "BMW")
        self.assertContains(response, "M4")
        self.assertContains(response, "70000")

    # RESERVE BUTTON

    def test_reserve_button_redirects_to_login_if_not_authenticated(self):
        response = self.client.get(
            reverse("vehicle_detail", args=[self.vehicle.slug])
        )
        self.assertContains(response, "login")

    def test_reserve_button_visible_if_authenticated(self):
        # On se connecte avec l'utilisateur client
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(
            reverse("vehicle_detail", args=[self.vehicle.slug])
        )

        # Vérifie que le bouton contient bien le lien vers le formulaire client
        expected_url = reverse("reservation_form", args=[self.vehicle.slug])
        self.assertContains(response, f'href="{expected_url}"')
        self.assertContains(response, "Réserver")


class VehicleFilterTests(TestCase):

    def setUp(self):
        self.v1 = Vehicle.objects.create(
            brand="BMW",
            model="Serie 1",
            engine="2.0",
            year=2020,
            color="Noir",
            mileage=50000,
            price=20000,
            vehicle_type="purchase"
        )

        self.v2 = Vehicle.objects.create(
            brand="Yamaha",
            model="MT-07",
            engine="700cc",
            year=2022,
            color="Bleu",
            mileage=10000,
            price=7500,
            vehicle_type="rental"
        )

        self.v3 = Vehicle.objects.create(
            brand="Audi",
            model="A4",
            engine="2.0",
            year=2018,
            color="Gris",
            mileage=80000,
            price=15000,
            vehicle_type="purchase"
        )

    # Filtre par type

    def test_filter_by_vehicle_type(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"vehicle_type": "purchase"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BMW")
        self.assertContains(response, "Audi")
        self.assertNotContains(response, "Yamaha")


    # Prix minimum

    def test_filter_by_min_price(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"min_price": 16000}
        )

        self.assertContains(response, "BMW")
        self.assertNotContains(response, "Audi")
        self.assertNotContains(response, "Yamaha")

    # Prix maximum

    def test_filter_by_max_price(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"max_price": 16000}
        )

        self.assertContains(response, "Audi")
        self.assertContains(response, "Yamaha")
        self.assertNotContains(response, "BMW")

    # Combinaison filtres

    def test_filter_combination(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {
                "vehicle_type": "purchase",
                "min_price": 18000
            }
        )

        self.assertContains(response, "BMW")
        self.assertNotContains(response, "Audi")
        self.assertNotContains(response, "Yamaha")

    # Tri croissant

    def test_order_by_price_ascending(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"order_by": "price"}
        )

        page = response.context["vehicles"]
        prices = [v.price for v in page]

        self.assertEqual(prices, sorted(prices))

    # Tri décroissant

    def test_order_by_price_descending(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"order_by": "-price"}
        )

        page = response.context["vehicles"]
        prices = [v.price for v in page]

        self.assertEqual(prices, sorted(prices, reverse=True))

    # Dans VehicleFilterTests

    def test_filter_by_min_year(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"min_year": 2021}
        )
        for v in response.context["vehicles"]:
            self.assertGreaterEqual(v.year, 2021)

    def test_filter_by_max_mileage(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"max_mileage": 50000}
        )
        for v in response.context["vehicles"]:
            self.assertLessEqual(v.mileage, 50000)

    def test_filter_hide_reserved(self):
        # Crée un véhicule réservé
        reserved_vehicle = Vehicle.objects.create(
            brand="TestBrand",
            model="TestModel",
            engine="2.0",
            year=2022,
            color="Noir",
            mileage=10000,
            vehicle_type=Vehicle.PURCHASE,
            price=30000,
            status=Vehicle.RESERVED
        )
        response = self.client.get(
            reverse("vehicle_list"),
            {"hide_reserved": True}
        )
        # Le véhicule réservé ne doit pas apparaître
        self.assertNotIn(reserved_vehicle, response.context["vehicles"])


class VehicleOrderingTests(TestCase):

    def setUp(self):
        self.v1 = Vehicle.objects.create(
            brand="BMW",
            model="X1",
            engine="2.0",
            year=2020,
            color="Noir",
            mileage=20000,
            vehicle_type=Vehicle.PURCHASE,
            price=Decimal("20000.00")
        )

        self.v2 = Vehicle.objects.create(
            brand="Audi",
            model="A3",
            engine="1.8",
            year=2019,
            color="Blanc",
            mileage=30000,
            vehicle_type=Vehicle.PURCHASE,
            price=Decimal("15000.00")
        )

        self.v3 = Vehicle.objects.create(
            brand="Mercedes",
            model="A180",
            engine="1.6",
            year=2021,
            color="Gris",
            mileage=10000,
            vehicle_type=Vehicle.PURCHASE,
            price=Decimal("25000.00")
        )

    def test_order_by_price_ascending(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"order_by": "price"}
        )

        self.assertEqual(response.status_code, 200)

        page = response.context["vehicles"]
        prices = [vehicle.price for vehicle in page]

        self.assertEqual(prices, sorted(prices))

    def test_order_by_price_descending(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"order_by": "-price"}
        )

        self.assertEqual(response.status_code, 200)

        page = response.context["vehicles"]
        prices = [vehicle.price for vehicle in page]

        self.assertEqual(prices, sorted(prices, reverse=True))


class VehicleSlugTests(TestCase):

    def test_slug_is_created_on_save(self):
        vehicle = Vehicle.objects.create(
            brand="BMW",
            model="M3",
            engine="3.0",
            year=2023,
            color="Noir",
            mileage=5000,
            vehicle_type="purchase",
            price=80000
        )

        self.assertIsNotNone(vehicle.slug)
        self.assertNotEqual(vehicle.slug, "")

    def test_vehicle_detail_accessible_with_slug(self):
        vehicle = Vehicle.objects.create(
            brand="Audi",
            model="RS3",
            engine="2.5",
            year=2022,
            color="Rouge",
            mileage=10000,
            vehicle_type="purchase",
            price=60000
        )

        response = self.client.get(
            reverse("vehicle_detail", args=[vehicle.slug])
        )

        self.assertEqual(response.status_code, 200)

    class VehicleStatusTests(TestCase):

        def test_sold_vehicle_not_visible_in_list(self):
            Vehicle.objects.create(
                brand="BMW",
                model="X5",
                engine="3.0",
                year=2020,
                color="Noir",
                mileage=40000,
                vehicle_type="purchase",
                price=30000,
                status=Vehicle.SOLD
            )

            response = self.client.get(reverse("vehicle_list"))

            self.assertNotContains(response, "X5")

    def test_sold_vehicle_returns_404_on_detail(self):
        vehicle = Vehicle.objects.create(
            brand="Audi",
            model="A6",
            engine="2.0",
            year=2019,
            color="Gris",
            mileage=60000,
            vehicle_type="purchase",
            price=25000,
            status=Vehicle.SOLD
        )

        response = self.client.get(
            reverse("vehicle_detail", args=[vehicle.slug])
        )

        self.assertEqual(response.status_code, 404)

class VehicleViewsCounterTests(TestCase):

    def test_vehicle_views_increment(self):
        vehicle = Vehicle.objects.create(
            brand="Mercedes",
            model="C63",
            engine="4.0",
            year=2021,
            color="Noir",
            mileage=15000,
            vehicle_type="purchase",
            price=70000
        )

        initial_views = vehicle.views

        self.client.get(
            reverse("vehicle_detail", args=[vehicle.slug])
        )

        vehicle.refresh_from_db()

        self.assertEqual(vehicle.views, initial_views + 1)

class VehicleContextTests(TestCase):

    def test_reserved_flag_in_context(self):
        vehicle = Vehicle.objects.create(
            brand="BMW",
            model="M2",
            engine="3.0",
            year=2022,
            color="Bleu",
            mileage=8000,
            vehicle_type="purchase",
            price=55000,
            status=Vehicle.RESERVED
        )

        response = self.client.get(
            reverse("vehicle_detail", args=[vehicle.slug])
        )

        self.assertTrue(response.context["is_reserved"])
        self.assertFalse(response.context["is_available"])