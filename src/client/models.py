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

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)


    # Documents
    driver_license = models.FileField(upload_to="reservations/license/")

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