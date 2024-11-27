from rest_framework import serializers
import json
import os
from decimal import Decimal

# Path to the JSON file where invoices will be stored
INVOICE_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'invoices.json')


def read_invoices_from_file():
    """Read invoices from the JSON file."""
    try:
        with open(INVOICE_FILE_PATH, 'r') as f:
            contents = f.read()
            return json.loads(contents) if contents else []  # Return an empty list if file is empty
    except FileNotFoundError:
        return []  # Return empty list if the file doesn't exist


def write_invoices_to_file(invoices):
    """Write the list of invoices back to the JSON file."""
    with open(INVOICE_FILE_PATH, 'w') as f:
        json.dump(invoices, f, indent=4)


class InvoiceSerializer(serializers.Serializer):
    invoice_number = serializers.CharField(max_length=100)
    customer_name = serializers.CharField(max_length=255)
    date = serializers.DateField()
    details = serializers.ListField(child=serializers.DictField(), required=True)  # Assuming details is a list of items

    def calculate_total_amount(self, details):
        """Calculate total amount based on details (unit_price * quantity)."""
        total_amount = Decimal(0)
        for item in details:
            unit_price = item.get('unit_price', 0)
            quantity = item.get('quantity', 0)
            total_amount += Decimal(unit_price) * Decimal(quantity)
        return total_amount

    def create(self, validated_data):
        """Custom method to create an invoice."""
        details = validated_data.get('details', [])
        total_amount = self.calculate_total_amount(details)
        validated_data['total_amount'] = total_amount  # Set the calculated total amount

        # Generate a new invoice with a unique ID (based on the existing number of invoices)
        invoices = read_invoices_from_file()
        new_invoice = {
            'id': len(invoices) + 1,
            **validated_data  # Add other validated fields like invoice_number, customer_name, etc.
        }

        # Save the new invoice
        invoices.append(new_invoice)
        write_invoices_to_file(invoices)

        return new_invoice

    def update(self, instance, validated_data):
        """Custom method to update an existing invoice."""
        details = validated_data.get('details', instance.get('details', []))
        total_amount = self.calculate_total_amount(details)
        validated_data['total_amount'] = total_amount  # Set the calculated total amount

        # Update the instance with validated data
        instance.update(validated_data)
        return instance
