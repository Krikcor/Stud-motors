# AJOUTS POUR LES TESTS D’IMAGES
from io import BytesIO
from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import Profile
from vehicles.models import Vehicle
from client.models import Reservation



def generate_test_image():
    file = BytesIO()
    image = Image.new("RGB", (100, 100), "white")
    image.save(file, "JPEG")
    file.seek(0)
    return SimpleUploadedFile(
        "test.jpg",
        file.read(),
        content_type="image/jpeg"
    )


#TEST LOGOUT

def test_logout(self):
    self.client.login(username="pro", password="testpass123")
    response = self.client.post(reverse("logout"))
    self.assertEqual(response.status_code, 302)

#CLASSE TEST CREATION VEHICULES

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


# NOUVELLE CLASSE POUR LES TESTS D’UPLOAD D IMAGES
class VehicleImageUploadTests(CreateVehicleTests):

    def test_upload_main_image(self):
        self.client.login(username="pro_user", password="Testpassword123")

        main_image = generate_test_image()

        data = self.valid_data.copy()
        data["main_image"] = main_image

        response = self.client.post(self.url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vehicle.objects.count(), 1)

        vehicle = Vehicle.objects.first()
        self.assertTrue(vehicle.main_image.name.endswith(".jpg"))

    def test_upload_secondary_images(self):
        self.client.login(username="pro_user", password="Testpassword123")

        sec1 = generate_test_image()
        sec2 = generate_test_image()

        data = self.valid_data.copy()
        data["secondary_images"] = [sec1, sec2]

        response = self.client.post(self.url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vehicle.objects.count(), 1)

        vehicle = Vehicle.objects.first()
        self.assertEqual(vehicle.images.count(), 2)


# CLASSE POUR TESTS SUPPRESSION
class DeleteVehicleTests(TestCase):

    def setUp(self):
        self.url = reverse("delete_vehicle")

        # PRO
        self.pro_user = User.objects.create_user(
            username="pro_user_del",
            password="Testpassword123"
        )
        Profile.objects.create(user=self.pro_user, role="pro")

        # CLIENT
        self.client_user = User.objects.create_user(
            username="client_user_del",
            password="Testpassword123"
        )
        Profile.objects.create(user=self.client_user, role="client")

        # Véhicule existant
        self.vehicle = Vehicle.objects.create(
            brand="Audi",
            model="A3",
            engine="2.0 TDI",
            year=2021,
            color="Blanc",
            mileage=20000,
            vehicle_type="purchase",
            price=22000.00
        )

    # Un pro peut supprimer
    def test_pro_can_delete_vehicle(self):
        self.client.login(username="pro_user_del", password="Testpassword123")

        # Étape 1 : soumission de l'id
        response = self.client.post(self.url, {
            "vehicle_id": self.vehicle.id
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirmer la suppression")

        # Étape 2 : confirmation
        response = self.client.post(self.url, {
            "confirm_delete": self.vehicle.id
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vehicle.objects.count(), 0)

    # Un client ne peut pas supprimer
    def test_client_cannot_delete_vehicle(self):
        self.client.login(username="client_user_del", password="Testpassword123")

        response = self.client.post(self.url, {
            "vehicle_id": self.vehicle.id
        })

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Vehicle.objects.count(), 1)

    # Un utilisateur non connecté est redirigé
    def test_anonymous_user_redirected(self):
        response = self.client.post(self.url, {
            "vehicle_id": self.vehicle.id
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vehicle.objects.count(), 1)

    # ID invalide
    def test_invalid_vehicle_id(self):
        self.client.login(username="pro_user_del", password="Testpassword123")

        response = self.client.post(self.url, {
            "vehicle_id": 9999
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Véhicule introuvable.")
        self.assertEqual(Vehicle.objects.count(), 1)

#CLASSE TESTS MODIFICATIONS
class ModifyVehicleTests(TestCase):

    def setUp(self):
        # Création d’un utilisateur pro
        self.pro_user = User.objects.create_user(
            username="pro",
            password="testpass123"
        )
        Profile.objects.create(user=self.pro_user, role="pro")

        # Création d’un client
        self.client_user = User.objects.create_user(
            username="client",
            password="testpass123"
        )
        Profile.objects.create(user=self.client_user, role="client")

        # Création d’un véhicule
        self.vehicle = Vehicle.objects.create(
            brand="BMW",
            model="M3",
            engine="3.0L",
            year=2020,
            color="Noir",
            mileage=20000,
            vehicle_type="purchase",
            price=55000
        )

    # Un pro peut accéder
    def test_pro_can_access_modify_page(self):
        self.client.login(username="pro", password="testpass123")
        response = self.client.get(reverse("modify_vehicle"))
        self.assertEqual(response.status_code, 200)

    # Un client ne peut pas accéder
    def test_client_cannot_access_modify_page(self):
        self.client.login(username="client", password="testpass123")
        response = self.client.get(reverse("modify_vehicle"))
        self.assertEqual(response.status_code, 403)

    #Utilisateur non connecté
    def test_anonymous_user_redirected(self):
        response = self.client.get(reverse("modify_vehicle"))
        self.assertEqual(response.status_code, 302)  # redirection login

    #Recherche d’un véhicule existant
    def test_search_existing_vehicle(self):
        self.client.login(username="pro", password="testpass123")

        response = self.client.post(reverse("modify_vehicle"), {
            "vehicle_id": self.vehicle.id
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BMW")

    # Recherche d’un ID inexistant
    def test_search_non_existing_vehicle(self):
        self.client.login(username="pro", password="testpass123")

        response = self.client.post(reverse("modify_vehicle"), {
            "vehicle_id": 9999
        })

        self.assertContains(response, "Véhicule introuvable")

    # Modification réussie
    def test_modify_vehicle_success(self):
        self.client.login(username="pro", password="testpass123")

        response = self.client.post(reverse("modify_vehicle"), {
            "save_modifications": self.vehicle.id,
            "brand": "Audi",
            "model": "RS5",
            "engine": "2.9L",
            "year": 2022,
            "color": "Rouge",
            "mileage": 10000,
            "vehicle_type": "purchase",
            "price": 65000
        })

        self.vehicle.refresh_from_db()

        self.assertEqual(self.vehicle.brand, "Audi")
        self.assertEqual(self.vehicle.model, "RS5")
        self.assertEqual(self.vehicle.price, 65000)
        self.assertEqual(response.status_code, 302)

#CLASSE TESTS TABLEAU

class ListVehicleTests(TestCase):

    def setUp(self):
        # Création utilisateur pro
        self.pro_user = User.objects.create_user(
            username="pro_list",
            password="testpass123"
        )
        Profile.objects.create(user=self.pro_user, role="pro")

        # Création utilisateur client
        self.client_user = User.objects.create_user(
            username="client_list",
            password="testpass123"
        )
        Profile.objects.create(user=self.client_user, role="client")

        # Création de 2 véhicules
        Vehicle.objects.create(
            brand="BMW",
            model="X5",
            engine="3.0L",
            year=2021,
            color="Noir",
            mileage=15000,
            vehicle_type="purchase",
            price=60000
        )

        Vehicle.objects.create(
            brand="Audi",
            model="A3",
            engine="2.0L",
            year=2019,
            color="Blanc",
            mileage=30000,
            vehicle_type="rental",
            price=25000
        )

    def test_pro_can_access_list(self):
        self.client.login(username="pro_list", password="testpass123")
        response = self.client.get(reverse("list_vehicle"))
        self.assertEqual(response.status_code, 200)

    def test_client_cannot_access_list(self):
        self.client.login(username="client_list", password="testpass123")
        response = self.client.get(reverse("list_vehicle"))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_redirected(self):
        response = self.client.get(reverse("list_vehicle"))
        self.assertEqual(response.status_code, 302)

    def test_vehicles_in_context(self):
        self.client.login(username="pro_list", password="testpass123")
        response = self.client.get(reverse("list_vehicle"))

        self.assertEqual(len(response.context["vehicles"]), 2)

    def test_vehicle_data_displayed(self):
        self.client.login(username="pro_list", password="testpass123")
        response = self.client.get(reverse("list_vehicle"))

        self.assertContains(response, "BMW")
        self.assertContains(response, "Audi")
        self.assertContains(response, "X5")
        self.assertContains(response, "A3")



class ReservationDashboardTests(TestCase):

    def setUp(self):

        # PRO USER
        self.pro_user = User.objects.create_user(
            username="pro",
            password="testpass123"
        )
        Profile.objects.create(user=self.pro_user, role="pro")

        # CLIENT USER
        self.client_user = User.objects.create_user(
            username="client",
            password="testpass123"
        )
        Profile.objects.create(user=self.client_user, role="client")

        # VEHICLE
        self.vehicle = Vehicle.objects.create(
            brand="BMW",
            model="X5",
            engine="3.0",
            year=2022,
            color="Noir",
            mileage=10000,
            vehicle_type="purchase",
            price=50000,
            status="available"
        )

        # DRIVER LICENSE
        self.license = SimpleUploadedFile(
            "license.pdf",
            b"filecontent",
            content_type="application/pdf"
        )

        # RESERVATION
        self.reservation = Reservation.objects.create(
            user=self.client_user,
            vehicle=self.vehicle,
            phone="0600000000",
            address="1 rue test",
            city="Paris",
            postal_code="75000",
            country="France",
            driver_license=self.license,
            accepted_terms=True,
            accepted_gdpr=True
        )

    # LISTE RESERVATIONS

    def test_pro_can_access_reservations(self):
        self.client.login(username="pro", password="testpass123")

        response = self.client.get(reverse("pro_reservations"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BMW")

    def test_client_cannot_access_reservations(self):
        self.client.login(username="client", password="testpass123")

        response = self.client.get(reverse("pro_reservations"))

        self.assertEqual(response.status_code, 403)

    # DETAIL

    def test_pro_can_view_reservation_detail(self):
        self.client.login(username="pro", password="testpass123")

        response = self.client.get(
            reverse("reservation_detail", args=[self.reservation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0600000000")

    # APPROVE

    def test_pro_can_approve_reservation(self):
        self.client.login(username="pro", password="testpass123")

        response = self.client.get(
            reverse(
                "reservation_decision",
                args=[self.reservation.id, "approve"]
            )
        )

        self.reservation.refresh_from_db()
        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.reservation.status,
            Reservation.STATUS_APPROVED
        )

        self.assertEqual(self.vehicle.status, "sold")

        self.assertEqual(response.status_code, 302)

    # REFUSE

    def test_pro_can_refuse_reservation(self):
        self.client.login(username="pro", password="testpass123")

        response = self.client.get(
            reverse(
                "reservation_decision",
                args=[self.reservation.id, "refuse"]
            )
        )

        self.reservation.refresh_from_db()

        self.assertEqual(
            self.reservation.status,
            Reservation.STATUS_REFUSED
        )

        self.assertEqual(response.status_code, 302)

    # SECURITY

    def test_client_cannot_decide(self):
        self.client.login(username="client", password="testpass123")

        response = self.client.get(
            reverse(
                "reservation_decision",
                args=[self.reservation.id, "approve"]
            )
        )

        self.assertEqual(response.status_code, 403)

    # VALIDATED_BY FIELD TESTS

    def test_validated_by_set_on_approve(self):
        self.client.login(username="pro", password="testpass123")

        self.client.get(
            reverse(
                "reservation_decision",
                args=[self.reservation.id, "approve"]
            )
        )

        self.reservation.refresh_from_db()

        self.assertEqual(
            self.reservation.validated_by,
            self.pro_user
        )
        self.assertIsNotNone(self.reservation.validated_at)

    def test_validated_by_set_on_refuse(self):
        self.client.login(username="pro", password="testpass123")

        self.client.get(
            reverse(
                "reservation_decision",
                args=[self.reservation.id, "refuse"]
            )
        )

        self.reservation.refresh_from_db()

        self.assertEqual(
            self.reservation.validated_by,
            self.pro_user
        )
        self.assertIsNotNone(self.reservation.validated_at)

    def test_pro_username_displayed_in_dashboard(self):
        self.client.login(username="pro", password="testpass123")

        # Approve first
        self.client.get(
            reverse(
                "reservation_decision",
                args=[self.reservation.id, "approve"]
            )
        )

        response = self.client.get(reverse("pro_reservations"))

        self.assertContains(response, "pro")


class ChangeVehicleTypeTests(TestCase):

    def setUp(self):

        self.url = reverse("change_vehicle_type")

        # PRO USER
        self.pro_user = User.objects.create_user(
            username="pro_change",
            password="testpass123"
        )
        Profile.objects.create(user=self.pro_user, role="pro")

        # CLIENT USER
        self.client_user = User.objects.create_user(
            username="client_change",
            password="testpass123"
        )
        Profile.objects.create(user=self.client_user, role="client")

        # VEHICLE AVAILABLE
        self.available_vehicle = Vehicle.objects.create(
            brand="BMW",
            model="X1",
            engine="2.0",
            year=2021,
            color="Noir",
            mileage=15000,
            vehicle_type=Vehicle.PURCHASE,
            price=25000,
            status=Vehicle.AVAILABLE
        )

        # VEHICLE RESERVED
        self.reserved_vehicle = Vehicle.objects.create(
            brand="Audi",
            model="A4",
            engine="2.0",
            year=2020,
            color="Blanc",
            mileage=20000,
            vehicle_type=Vehicle.PURCHASE,
            price=22000,
            status=Vehicle.RESERVED
        )

    # Sécurité accès

    def test_pro_can_access_page(self):
        self.client.login(username="pro_change", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_client_cannot_access_page(self):
        self.client.login(username="client_change", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    # Recherche véhicule existant

    def test_search_existing_vehicle(self):
        self.client.login(username="pro_change", password="testpass123")

        response = self.client.post(self.url, {
            "vehicle_id": self.available_vehicle.id
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BMW")

    def test_search_non_existing_vehicle(self):
        self.client.login(username="pro_change", password="testpass123")

        response = self.client.post(self.url, {
            "vehicle_id": 9999
        })

        self.assertContains(response, "Véhicule introuvable")

    # Modification réussie (AVAILABLE)

    def test_change_type_success(self):
        self.client.login(username="pro_change", password="testpass123")

        response = self.client.post(self.url, {
            "save_type": self.available_vehicle.id,
            "vehicle_type": Vehicle.RENTAL
        })

        self.available_vehicle.refresh_from_db()

        self.assertEqual(
            self.available_vehicle.vehicle_type,
            Vehicle.RENTAL
        )

        self.assertEqual(response.status_code, 302)

    # Refus si véhicule réservé

    def test_cannot_change_if_reserved(self):
        self.client.login(username="pro_change", password="testpass123")

        response = self.client.post(self.url, {
            "save_type": self.reserved_vehicle.id,
            "vehicle_type": Vehicle.RENTAL
        })

        self.reserved_vehicle.refresh_from_db()

        # Le type ne change pas
        self.assertEqual(
            self.reserved_vehicle.vehicle_type,
            Vehicle.PURCHASE
        )

        self.assertContains(
            response,
            "Impossible de modifier un véhicule réservé ou vendu."
        )