from django.db import models


class Vehicle(models.Model):

    PURCHASE = 'purchase'
    RENTAL = 'rental'

    VEHICLE_TYPE_CHOICES = [
        (PURCHASE, 'Achat'),
        (RENTAL, 'Location'),
    ]

    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    engine = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=50)
    mileage = models.PositiveIntegerField()

    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    main_image = models.ImageField(
        upload_to="vehicles/main/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


class VehicleImage(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="vehicles/secondary/"
    )

    def __str__(self):
        return f"Image for {self.vehicle}"
