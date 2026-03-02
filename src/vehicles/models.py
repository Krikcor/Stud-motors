from django.db import models
from django.utils.text import slugify


class Vehicle(models.Model):

    # TYPE
    PURCHASE = 'purchase'
    RENTAL = 'rental'

    VEHICLE_TYPE_CHOICES = [
        (PURCHASE, 'Achat'),
        (RENTAL, 'Location'),
    ]

    # STATUS
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"

    STATUS_CHOICES = [
        (AVAILABLE, "Disponible"),
        (RESERVED, "Réservé"),
        (SOLD, "Vendu"),
    ]

    # Informations principales
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    engine = models.CharField(max_length=100)

    year = models.PositiveIntegerField(db_index=True)
    color = models.CharField(max_length=50)
    mileage = models.PositiveIntegerField()

    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        db_index=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_index=True
    )

    # SEO
    slug = models.SlugField(unique=True, blank=True)

    # Statut & mise en avant
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=AVAILABLE,
        db_index=True
    )

    is_featured = models.BooleanField(
        default=False,
        help_text="Mettre en avant sur la page d'accueil"
    )

    # Statistiques
    views = models.PositiveIntegerField(default=0)

    # Images
    main_image = models.ImageField(
        upload_to="vehicles/main/",
        null=True,
        blank=True
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # Important pour pagination stable
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["year"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

    def save(self, *args, **kwargs):
        """
        Génération automatique du slug si non défini
        """
        if not self.slug:
            base_slug = slugify(f"{self.brand}-{self.model}-{self.year}")
            slug = base_slug
            counter = 1

            while Vehicle.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class VehicleImage(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="vehicles/secondary/"
    )

    is_main = models.BooleanField(
        default=False,
        help_text="Définir comme image principale"
    )

    def __str__(self):
        return f"Image for {self.vehicle}"