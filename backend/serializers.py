from rest_framework import serializers
import json
import os
import aiofiles  # For asynchronous file handling
import asyncio

# Path to the JSON file where invoices will be stored
INVOICE_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'invoices.json')


async def read_invoices_from_file():
    """Read invoices from the JSON file asynchronously."""
    try:
        async with aiofiles.open(INVOICE_FILE_PATH, 'r') as f:
            contents = await f.read()
            return json.loads(contents) if contents else []  # Return an empty list if file is empty
    except FileNotFoundError:
        return []  # Return empty list if the file doesn't exist



async def write_invoices_to_file(invoices):
    """Write the list of invoices back to the JSON file asynchronously."""
    async with aiofiles.open(INVOICE_FILE_PATH, 'w') as f:
        await f.write(json.dumps(invoices, indent=4))


# Example InvoiceSerializer - adjust fields according to your model
class InvoiceSerializer(serializers.Serializer):
    invoice_number = serializers.CharField(max_length=100)
    customer_name = serializers.CharField(max_length=255)
    date = serializers.DateField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Make this read-only
    details = serializers.ListField(child=serializers.DictField(), required=False)  # Assuming details is a list of items

    def calculate_total_amount(self, details):
        """Calculate total amount based on details (unit_price * quantity)."""
        total_amount = 0
        for item in details:
            unit_price = item.get('unit_price', 0)
            quantity = item.get('quantity', 0)
            total_amount += unit_price * quantity
        return total_amount

    async def create(self, validated_data):
        """Custom method to create an invoice asynchronously."""
        details = validated_data.get('details', [])
        total_amount = self.calculate_total_amount(details)
        validated_data['total_amount'] = total_amount  # Set the calculated total amount

        # Create the invoice instance (returning data for simplicity)
        return validated_data

    async def update(self, instance, validated_data):
        """Custom method to update an existing invoice asynchronously."""
        details = validated_data.get('details', instance.get('details', []))
        total_amount = self.calculate_total_amount(details)
        validated_data['total_amount'] = total_amount  # Set the calculated total amount

        # Update the instance with validated data
        instance.update(validated_data)
        return instance

    async def save_invoice(self, new_invoice):
        """Method to save the new invoice into the file asynchronously."""
        invoices = await read_invoices_from_file()  # Read existing invoices asynchronously
        invoices.append(new_invoice)  # Add the new invoice to the list
        await write_invoices_to_file(invoices)  # Save the updated invoices list back to the file asynchronously
