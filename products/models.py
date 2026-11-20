from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    class Currency(models.TextChoices):
        USD = "USD", "US Dollar"
        INR = "INR", "Indian Rupee"

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.INR,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
