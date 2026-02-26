from django.db import models
from django.contrib.auth.models import User
from vehicles.models import Vehicle


class Reservation(models.Model):

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REFUSED = "refused"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En cours de traitement"),
        (STATUS_APPROVED, "Validée"),
        (STATUS_REFUSED, "Refusée"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    # Infos personnelles
    phone = models.CharField(max_length=20)
    birth_date = models.DateField()

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    # Situation
    employment_status = models.CharField(max_length=100)
    monthly_income = models.DecimalField(max_digits=8, decimal_places=2)

    # Documents
    id_document = models.FileField(upload_to="reservations/id/")
    driver_license = models.FileField(upload_to="reservations/license/")
    proof_of_address = models.FileField(upload_to="reservations/address/")
    income_proof = models.FileField(upload_to="reservations/income/")

    # RGPD
    accepted_terms = models.BooleanField()
    accepted_gdpr = models.BooleanField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.vehicle}"