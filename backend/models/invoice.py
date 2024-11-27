from django.db import models
from django.core.validators import MinValueValidator

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)  # Unique invoice number
    customer_name = models.CharField(max_length=100)  # Customer name
    date = models.DateField()  # Date of the invoice
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total amount of the invoice

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        # Calculate total amount by summing the line_total of each related InvoiceDetail
        self.total_amount = sum(detail.line_total for detail in self.details.all())
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'invoice'  # Explicitly set the table name to 'invoice'
