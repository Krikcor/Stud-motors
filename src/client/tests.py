from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from vehicles.models import Vehicle
from accounts.models import Profile
from client.models import Reservation


class ReservationTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            password="password123"
        )

        Profile.objects.create(
            user=self.user,
            role="client"
        )

        self.vehicle = Vehicle.objects.create(
            brand="TestBrand",
            model="TestModel",
            engine="V8",
            year=2020,
            color="Black",
            mileage=10000,
            vehicle_type=Vehicle.RENTAL,
            price=10000,
            status=Vehicle.AVAILABLE,
        )

        self.url = reverse(
            "reservation_form",
            kwargs={"slug": self.vehicle.slug}
        )

        self.client.login(
            username="testuser",
            password="password123"
        )

        self.valid_file = SimpleUploadedFile(
            "license.pdf",
            b"file_content",
            content_type="application/pdf"
        )

        self.valid_data = {
            "phone": "0600000000",
            "address": "1 rue test",
            "city": "Paris",
            "postal_code": "75000",
            "country": "France",
            "accepted_terms": True,
            "accepted_gdpr": True,
            "driver_license": self.valid_file,
        }

    # LOGIN

    def test_reservation_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    # DISPLAY

    def test_reservation_form_display(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # SUCCESS

    def test_create_reservation(self):
        response = self.client.post(self.url, self.valid_data, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Reservation.objects.filter(
                user=self.user,
                vehicle=self.vehicle
            ).exists()
        )

    # VEHICLE STATUS

    def test_vehicle_becomes_reserved(self):
        self.client.post(self.url, self.valid_data)

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            Vehicle.RESERVED
        )

    # BLOCK RESERVED

    def test_reservation_blocked_if_vehicle_reserved(self):
        self.vehicle.status = Vehicle.RESERVED
        self.vehicle.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    # REQUIRED FIELD
    def test_missing_required_field(self):
        data = self.valid_data.copy()
        data.pop("phone")

        response = self.client.post(self.url, data)

        form = response.context["form"]

        self.assertIn("phone", form.errors)

    # WRONG FILE

    def test_reject_wrong_file_type(self):
        wrong_file = SimpleUploadedFile(
            "license.txt",
            b"fake",
            content_type="text/plain"
        )

        data = self.valid_data.copy()
        data["driver_license"] = wrong_file

        response = self.client.post(self.url, data)

        form = response.context["form"]

        self.assertIn("driver_license", form.errors)

    # FILE TOO LARGE

    def test_reject_file_too_large(self):
        big_file = SimpleUploadedFile(
            "license.pdf",
            b"x" * (6 * 1024 * 1024),
            content_type="application/pdf"
        )

        data = self.valid_data.copy()
        data["driver_license"] = big_file

        response = self.client.post(self.url, data)

        form = response.context["form"]

        self.assertIn("driver_license", form.errors)

    # TERMS

    def test_terms_must_be_accepted(self):
        data = self.valid_data.copy()
        data["accepted_terms"] = False

        response = self.client.post(self.url, data)

        form = response.context["form"]

        self.assertIn("accepted_terms", form.errors)

    # DOUBLE RESERVATION

    def test_user_cannot_reserve_twice(self):

        Reservation.objects.create(
            user=self.user,
            vehicle=self.vehicle,
            phone="0600000000",
            address="1 rue test",
            city="Paris",
            postal_code="75000",
            country="France",
            accepted_terms=True,
            accepted_gdpr=True,
            driver_license=self.valid_file,
        )

        self.client.post(self.url, self.valid_data)

        self.assertEqual(
            Reservation.objects.filter(
                user=self.user,
                vehicle=self.vehicle
            ).count(),
            1
        )

# PRO CANNOT RESERVE

    def test_pro_cannot_reserve_vehicle(self):

        # Création d’un utilisateur pro
        pro_user = User.objects.create_user(
            username="pro_user",
            password="password123"
        )

        Profile.objects.create(
            user=pro_user,
            role="pro"
        )

        self.client.logout()

        self.client.login(
            username="pro_user",
            password="password123"
        )

        response = self.client.post(self.url, self.valid_data)

        # Accès interdit
        self.assertEqual(response.status_code, 403)

        # Aucune réservation créée
        self.assertFalse(
            Reservation.objects.filter(
                user=pro_user,
                vehicle=self.vehicle
            ).exists()
        )

        # Véhicule toujours disponible
        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            Vehicle.AVAILABLE
        )

class ClientDashboardTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="client1",
            password="password123"
        )

        Profile.objects.create(
            user=self.user,
            role="client"
        )

        self.vehicle = Vehicle.objects.create(
            brand="BMW",
            model="M3",
            engine="V6",
            year=2022,
            color="Blue",
            mileage=5000,
            vehicle_type=Vehicle.RENTAL,
            price=20000,
            status=Vehicle.AVAILABLE,
        )

        self.client.login(
            username="client1",
            password="password123"
        )

        self.dashboard_url = reverse("client_dashboard")


    # LOGIN REQUIRED


    def test_dashboard_requires_login(self):

        self.client.logout()

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 302)


    # CLIENT SEES RESERVATION

    def test_client_sees_his_reservation(self):

        Reservation.objects.create(
            user=self.user,
            vehicle=self.vehicle,
            phone="0600000000",
            address="1 rue test",
            city="Paris",
            postal_code="75000",
            country="France",
            accepted_terms=True,
            accepted_gdpr=True,
            driver_license="licenses/test.pdf",
        )

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)

        reservations = response.context["reservations"]

        self.assertEqual(reservations.count(), 1)

    # ONLY OWN RESERVATIONS

    def test_client_cannot_see_other_users_reservations(self):

        other = User.objects.create_user(
            username="other",
            password="password123"
        )

        Profile.objects.create(
            user=other,
            role="client"
        )

        Reservation.objects.create(
            user=other,
            vehicle=self.vehicle,
            phone="0600000000",
            address="Other",
            city="Lyon",
            postal_code="69000",
            country="France",
            accepted_terms=True,
            accepted_gdpr=True,
            driver_license="licenses/test.pdf",
        )

        response = self.client.get(self.dashboard_url)

        reservations = response.context["reservations"]

        self.assertEqual(reservations.count(), 0)

class DeleteAccountTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="deleteuser",
            password="password123"
        )

        Profile.objects.create(
            user=self.user,
            role="client"
        )

        self.vehicle = Vehicle.objects.create(
            brand="Audi",
            model="RS6",
            engine="V8",
            year=2021,
            color="Grey",
            mileage=8000,
            vehicle_type=Vehicle.RENTAL,
            price=50000,
            status=Vehicle.AVAILABLE,
        )

        self.client.login(
            username="deleteuser",
            password="password123"
        )

        self.delete_url = reverse("delete_account")

    def create_reservation(self, status):
        return Reservation.objects.create(
            user=self.user,
            vehicle=self.vehicle,
            phone="0600000000",
            address="1 rue test",
            city="Paris",
            postal_code="75000",
            country="France",
            accepted_terms=True,
            accepted_gdpr=True,
            driver_license="licenses/test.pdf",
            status=status
        )

    # TEST GLOBAL DELETE LOGIC

    def test_delete_account_behavior(self):

        # Création des 3 types de réservation
        pending = self.create_reservation(Reservation.STATUS_PENDING)
        refused = self.create_reservation(Reservation.STATUS_REFUSED)
        approved = self.create_reservation(Reservation.STATUS_APPROVED)

        response = self.client.post(self.delete_url, follow=True)

        self.assertEqual(response.status_code, 200)

        # User supprimé
        self.assertFalse(
            User.objects.filter(username="deleteuser").exists()
        )

        # Pending supprimée
        self.assertFalse(
            Reservation.objects.filter(id=pending.id).exists()
        )

        # Refused supprimée
        self.assertFalse(
            Reservation.objects.filter(id=refused.id).exists()
        )

        # Approved conservée
        self.assertTrue(
            Reservation.objects.filter(id=approved.id).exists()
        )

        approved.refresh_from_db()

        # User détaché
        self.assertIsNone(approved.user)

    def test_vehicle_becomes_available_when_pending_deleted(self):

        pending = self.create_reservation(Reservation.STATUS_PENDING)

        # Simule le statut réservé du véhicule
        self.vehicle.status = Vehicle.RESERVED
        self.vehicle.save()

        self.client.post(self.delete_url)

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            Vehicle.AVAILABLE
        )

class EditProfileTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="edituser",
            password="password123",
            first_name="Old",
            last_name="Name",
            email="old@email.com"
        )

        Profile.objects.create(
            user=self.user,
            role="client"
        )

        self.client.login(
            username="edituser",
            password="password123"
        )

        self.url = reverse("edit_profile")


    # LOGIN REQUIRED

    def test_edit_profile_requires_login(self):

        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)


    # DISPLAY

    def test_edit_profile_display(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


    # UPDATE PERSONAL INFO ONLY

    def test_update_profile_without_password_change(self):

        response = self.client.post(self.url, {
            "first_name": "New",
            "last_name": "Lastname",
            "email": "new@email.com",
            "new_password1": "",
            "new_password2": "",
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "New")
        self.assertEqual(self.user.last_name, "Lastname")
        self.assertEqual(self.user.email, "new@email.com")

        # Mot de passe inchangé
        self.assertTrue(self.user.check_password("password123"))


    # PASSWORD CHANGE SUCCESS

    def test_update_profile_with_password_change(self):

        response = self.client.post(self.url, {
            "first_name": "Old",
            "last_name": "Name",
            "email": "old@email.com",
            "new_password1": "NewStrongPass123!",
            "new_password2": "NewStrongPass123!",
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("NewStrongPass123!"))


    # PASSWORD MISMATCH

    def test_password_mismatch(self):

        response = self.client.post(self.url, {
            "first_name": "Old",
            "last_name": "Name",
            "email": "old@email.com",
            "new_password1": "Password123!",
            "new_password2": "Different123!",
        })

        self.assertEqual(response.status_code, 200)

        form = response.context["password_form"]

        self.assertFalse(form.is_valid())

        # Mot de passe inchangé
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("password123"))


    # REQUIRED FIELDS CANNOT BE EMPTY

    def test_required_fields_cannot_be_empty(self):

        response = self.client.post(self.url, {
            "first_name": "",
            "last_name": "",
            "email": "",
        })

        self.assertEqual(response.status_code, 200)

        form = response.context["form"]

        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("email", form.errors)


    # USERNAME CANNOT BE MODIFIED

    def test_username_cannot_be_modified(self):

        response = self.client.post(self.url, {
            "first_name": "Old",
            "last_name": "Name",
            "email": "old@email.com",
            "username": "hacker_attempt",  # tentative injection
        }, follow=True)

        self.user.refresh_from_db()

        # Username doit rester inchangé
        self.assertEqual(self.user.username, "edituser")