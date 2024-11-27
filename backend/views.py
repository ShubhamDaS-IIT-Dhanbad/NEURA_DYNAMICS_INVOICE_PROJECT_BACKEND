import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import InvoiceSerializer
from .utils import read_invoices_from_file, write_invoices_to_file  # Utility functions for file handling
import os

INVOICE_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'invoices.json')

def read_invoices_from_file():
    """Read invoices from the file synchronously."""
    try:
        with open(INVOICE_FILE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Return an empty list if the file does not exist

def write_invoices_to_file(invoices):
    """Write invoices to the file synchronously."""
    with open(INVOICE_FILE_PATH, 'w') as f:
        json.dump(invoices, f, indent=4)


# GET method to list all invoices
def get_invoices(request):
    try:
        invoices = read_invoices_from_file()  # Synchronously read invoices from file
        return JsonResponse({
            'status': 'success',
            'message': 'Invoices retrieved successfully.',
            'data': invoices
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# POST method to create a new invoice
@csrf_exempt
def create_invoice(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON request data
            data = json.loads(request.body)
            # Serialize the incoming data
            serializer = InvoiceSerializer(data=data)

            # Read the current invoices from the file
            invoices = read_invoices_from_file()

            # Check if the data is valid
            if serializer.is_valid():
                invoice = serializer.data

                # Prepare unique IDs for details
                details_with_ids = [
                    {**detail, 'id': idx + 1} for idx, detail in enumerate(invoice["details"])
                ]

                # Prepare the new invoice to append to the invoices list
                new_invoice = {
                    'id': len(invoices) + 1,  # Generate a new unique ID
                    'invoice_number': invoice['invoice_number'],  
                    'customer_name': invoice['customer_name'],
                    'date': invoice['date'],
                    'details': details_with_ids
                }

                # Append the new invoice to the existing list
                invoices.append(new_invoice)

                # Write the updated invoices list back to the file
                write_invoices_to_file(invoices)

                # Return a successful response
                return JsonResponse({
                    'status': 'success',
                    'message': 'Invoice created successfully.',
                    'data': new_invoice
                })

            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invoice creation failed.',
                    'errors': serializer.errors
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data.'
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Only POST requests are allowed.'
    }, status=405)


# PUT method to update an existing invoice
@csrf_exempt  # If you need to disable CSRF for testing
def update_invoice(request):
    try:
        if request.method != 'PUT':
            return JsonResponse({
                'status': 'error',
                'message': 'Only PUT requests are allowed.'
            }, status=405)

        # Parse the incoming JSON request data
        data = json.loads(request.body)

        # Read the existing invoices from the file
        invoices = read_invoices_from_file()

        # Find the invoice with the given ID
        invoice = next((inv for inv in invoices if inv['id'] == data['id']), None)
        if not invoice:
            return JsonResponse({
                'status': 'error',
                'message': 'Invoice not found.'
            }, status=404)

        # Update or add fields from the incoming data
        for key, value in data.items():
            if key == "details":
                # Handle details specifically
                existing_details = invoice.get("details", [])
                max_existing_id = max((detail["id"] for detail in existing_details if "id" in detail), default=0)

                updated_details = []
                for new_detail in value:
                    if "id" in new_detail:
                        # Update existing detail
                        existing_detail = next((det for det in existing_details if det["id"] == new_detail["id"]), None)
                        if existing_detail:
                            existing_detail.update(new_detail)
                            updated_details.append(existing_detail)
                        else:
                            # If the id is not in existing details, add it as a new entry
                            updated_details.append(new_detail)
                    else:
                        # New detail, assign unique id
                        new_detail["id"] = max_existing_id + 1
                        max_existing_id += 1
                        updated_details.append(new_detail)

                # Update the invoice details
                invoice["details"] = updated_details
            else:
                # Update other fields
                invoice[key] = value

        # Write the updated invoices list back to the file
        write_invoices_to_file(invoices)

        return JsonResponse({
            'status': 'success',
            'message': 'Invoice updated successfully.',
            'data': invoice
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data.'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# DELETE method to delete an invoice
@csrf_exempt  # If you need to disable CSRF for testing
def delete_invoice(request):
    try:
        if request.method != 'DELETE':
            return JsonResponse({
                'status': 'error',
                'message': 'Only DELETE requests are allowed.'
            }, status=405)

        # Parse the incoming JSON request data
        data = json.loads(request.body)

        # Read the existing invoices from the file
        invoices = read_invoices_from_file()

        # Extract necessary fields from the request
        invoice_id = data.get('invoice_id')
        detail_id = data.get('detail_id')

        # Find the invoice with the given ID
        invoice = next((inv for inv in invoices if inv['id'] == invoice_id), None)
        if not invoice:
            return JsonResponse({
                'status': 'error',
                'message': 'Invoice not found.'
            }, status=404)

        if detail_id is None:
            # If detail_id is not provided, delete the entire invoice
            invoices.remove(invoice)
            message = 'Invoice deleted successfully.'
        else:
            # If detail_id is provided, delete the specific detail
            details = invoice.get('details', [])
            updated_details = [d for d in details if d.get('id') != detail_id]
            if len(details) == len(updated_details):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Detail not found in the invoice.'
                }, status=404)
            invoice['details'] = updated_details
            message = 'Detail deleted successfully.'

        # Write the updated invoices list back to the file
        write_invoices_to_file(invoices)

        return JsonResponse({
            'status': 'success',
            'message': message
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data.'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
