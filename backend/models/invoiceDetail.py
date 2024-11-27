from django.db import models
from django.core.validators import MinValueValidator
from .invoice import Invoice  # Import the Invoice model

class InvoiceDetail(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='details', on_delete=models.CASCADE)  # ForeignKey to the Invoice model
    description = models.CharField(max_length=255)  # Description of the product
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])  # Quantity of the product
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Unit price of the product
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Line total, calculated as quantity * unit_price

    def save(self, *args, **kwargs):
        # Automatically calculate line_total before saving the detail
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
