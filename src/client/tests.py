from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date

from vehicles.models import Vehicle
from accounts.models import Profile
from client.models import Reservation


class ReservationTests(TestCase):

    def setUp(self):
        # USER
        self.user = User.objects.create_user(
            username="testuser",
            password="password123"
        )

        Profile.objects.create(
            user=self.user,
            role="client"
        )

        # VEHICLE (TOUS LES CHAMPS REQUIS)
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

        # FAUX FICHIER
        self.fake_file = SimpleUploadedFile(
            "license.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        # DATA COMPLETE (TOUS LES NOT NULL)
        self.valid_data = {
            "phone": "0600000000",
            "address": "1 rue test",
            "city": "Paris",
            "postal_code": "75000",
            "country": "France",
            "accepted_terms": True,
            "accepted_gdpr": True,
            "driver_license": self.fake_file,
        }

    # -------------------------

    def test_reservation_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    # -------------------------

    def test_reservation_form_display(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # -------------------------

    def test_create_reservation(self):
        response = self.client.post(
            self.url,
            self.valid_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Reservation.objects.filter(
                user=self.user,
                vehicle=self.vehicle
            ).exists()
        )

    # -------------------------

    def test_vehicle_becomes_reserved(self):
        self.client.post(self.url, self.valid_data)

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            Vehicle.RESERVED
        )

    # -------------------------

    def test_reservation_blocked_if_vehicle_reserved(self):

        Reservation.objects.create(
            user=self.user,
            vehicle=self.vehicle,
            phone="0600000000",
            address="test",
            city="Paris",
            postal_code="75000",
            country="France",
            accepted_terms=True,
            accepted_gdpr=True,
            driver_license=self.fake_file,
        )

        self.vehicle.status = Vehicle.RESERVED
        self.vehicle.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)