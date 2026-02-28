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