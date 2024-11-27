import json
import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import InvoiceSerializer, read_invoices_from_file, write_invoices_to_file
from asgiref.sync import sync_to_async  # Import for async compatibility with sync functions
import os

INVOICE_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'invoices.json')

# Async function to serialize JSON data
async def async_json_dumps(data, indent=4):
    """Offload the blocking JSON serialization to a separate thread."""
    return await asyncio.to_thread(json.dumps, data, indent=indent)

# Async function to handle reading invoices from file
async def async_read_invoices():
    return await asyncio.to_thread(read_invoices_from_file)










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
async def get_invoices(request):
    try:
        invoices = await async_read_invoices()
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
            print("shubham")

            # Parse the incoming JSON request data
            data = json.loads(request.body)

            # Validate the data manually
            customer_name = data.get('customer_name')
            details = data.get('details')

            if not customer_name:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Customer name is required.'
                }, status=400)

            if not details or not isinstance(details, list) or len(details) == 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Details are required and must be a non-empty list.'
                }, status=400)

            # Read the current invoices from the file
            if os.path.exists(INVOICE_FILE_PATH):
                with open(INVOICE_FILE_PATH, 'r') as f:
                    invoices = json.load(f)
            else:
                invoices = []

            # Calculate total amount by multiplying count with price for each product in the details
            total_amount = 0
            details_with_ids = []

            print(data)
            for idx, detail in enumerate(details):
                # Ensure 'count' and 'price' are present
                count = detail.get('quantity', 0)
                price = detail.get('unit_price', 0)

                # Convert 'count' to an integer and 'price' to a float
                try:
                    count = int(count) if count != '' else 0  # Convert count to integer (default to 0 if empty)
                    price = float(price) if price != '' else 0.0  # Convert price to float (default to 0.0 if empty)
                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid value for count or price. Must be numeric.'
                    }, status=400)

                print(detail, count, price)

                # Calculate the amount for this particular detail
                detail_amount = count * price
                total_amount += detail_amount

                # Add an ID to the detail (for example, a unique index)
                details_with_ids.append({**detail, 'id': idx + 1})

            # Prepare the new invoice to append to the invoices list
            new_invoice = {
                'id': len(invoices) + 1,  # Generate a new unique ID
                'invoice_number': len(invoices) + 1,
                'customer_name': customer_name,
                'date': data.get('date'),  # Use provided date or handle default
                'details': details_with_ids,
                'total_amount': total_amount  # Add the total amount to the invoice
            }

            # Append the new invoice to the existing list
            invoices.append(new_invoice)

            # Write the updated invoices list back to the file
            with open(INVOICE_FILE_PATH, 'w') as f:
                json.dump(invoices, f, indent=4)

            # Return a successful response
            return JsonResponse({
                'status': 'success',
                'message': 'Invoice created successfully.',
                'data': new_invoice
            })

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

        # Handle string-to-JSON conversion for specific keys
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    # Attempt to parse strings as JSON
                    data[key] = json.loads(value)
                except json.JSONDecodeError:
                    # Leave the value as-is if it's not a JSON string
                    pass

        print("update", data)

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
        details = data.get("details", [])
        total_amount = 0
        details_with_ids = []

        for idx, detail in enumerate(details):
            # Ensure 'count' and 'price' are present
            count = detail.get('quantity', 0)
            price = detail.get('unit_price', 0)

            # Convert 'count' to an integer and 'price' to a float
            try:
                count = int(count) if count != '' else 0  # Convert count to integer (default to 0 if empty)
                price = float(price) if price != '' else 0.0  # Convert price to float (default to 0.0 if empty)
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid value for count or price. Must be numeric.'
                }, status=400)

            print(detail, count, price)

            # Calculate the amount for this particular detail
            detail_amount = count * price
            total_amount += detail_amount

            # Add an ID to the detail (for example, a unique index)
            details_with_ids.append({**detail, 'id': idx + 1})

        # Update the invoice's details with the new data
        if "details" in data:
            existing_details = invoice.get("details", [])
            max_existing_id = max((detail["id"] for detail in existing_details if "id" in detail), default=0)

            updated_details = []
            for new_detail in details_with_ids:
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

        # Update other fields from the incoming data (excluding "details")
        for key, value in data.items():
            if key != "details":
                invoice[key] = value

        # Update the total amount of the invoice
        invoice['total_amount'] = total_amount

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