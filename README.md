# Invoice Management Backend - Django[backend not deployed.... working on it...and also integrating to frontend]

This is the backend server built with Django, specifically for managing invoices. The application supports operations to **Create, Read, Update, and Delete (CRUD)** invoices. Unlike traditional relational databases, this system uses a **JSON file** (`invoices.json`) to store and manage invoice data.

### Features:
- **CRUD Operations**: Endpoints to create, retrieve, update, and delete invoices.
- **JSON-based Storage**: Invoice data is stored in a JSON file (`invoices.json`), making it easy to manage without the need for complex database setups.
- **Invoice Validation**: Ensures that each invoice contains necessary details like customer name, invoice date, and product details.
- **Security**: Basic error handling and validation for secure data transactions.

### Tech Stack:
- **Backend**: Django
- **Data Storage**: JSON file (`invoices.json`) for storing invoice data
- **API**: Django Rest Framework (DRF)

---

### Setup

#### Prerequisites:
- Python 3.8 or later
- Django 3.x or later
- Django Rest Framework (DRF)
- pip (Python package manager)

#### Installation Steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/invoice-management-backend.git
   cd invoice-management-backend
API Endpoints
1. POST /invoices - Create a new invoice
Request body (JSON):
json
Copy code
{
  "customer_name": "John Doe",
  "date": "2024-11-28",
  "details": [
    {
      "product_name": "Product A",
      "quantity": 2,
      "unit_price": 50
    },
    {
      "product_name": "Product B",
      "quantity": 1,
      "unit_price": 100
    }
  ]
}
Response (JSON):
json
Copy code
{
  "status": "success",
  "message": "Invoice created successfully.",
  "data": {
    "id": 1,
    "customer_name": "John Doe",
    "date": "2024-11-28",
    "details": [
      {
        "product_name": "Product A",
        "quantity": 2,
        "unit_price": 50
      },
      {
        "product_name": "Product B",
        "quantity": 1,
        "unit_price": 100
      }
    ],
    "total_amount": 200
  }
}
2. GET /invoices - Retrieve a list of all invoices
Response (JSON):
json
Copy code
[
  {
    "id": 1,
    "customer_name": "John Doe",
    "date": "2024-11-28",
    "details": [
      {
        "product_name": "Product A",
        "quantity": 2,
        "unit_price": 50
      },
      {
        "product_name": "Product B",
        "quantity": 1,
        "unit_price": 100
      }
    ],
    "total_amount": 200
  }
]
3. GET /invoices/{id} - Retrieve a specific invoice by its ID
Response (JSON):
json
Copy code
{
  "id": 1,
  "customer_name": "John Doe",
  "date": "2024-11-28",
  "details": [
    {
      "product_name": "Product A",
      "quantity": 2,
      "unit_price": 50
    },
    {
      "product_name": "Product B",
      "quantity": 1,
      "unit_price": 100
    }
  ],
  "total_amount": 200
}
4. PUT /invoices/{id} - Update an existing invoice by its ID
Request body (JSON):
json
Copy code
{
  "customer_name": "John Doe Updated",
  "date": "2024-12-01",
  "details": [
    {
      "product_name": "Product A Updated",
      "quantity": 3,
      "unit_price": 60
    },
    {
      "product_name": "Product B Updated",
      "quantity": 2,
      "unit_price": 110
    }
  ]
}
Response (JSON):
json
Copy code
{
  "status": "success",
  "message": "Invoice updated successfully.",
  "data": {
    "id": 1,
    "customer_name": "John Doe Updated",
    "date": "2024-12-01",
    "details": [
      {
        "product_name": "Product A Updated",
        "quantity": 3,
        "unit_price": 60
      },
      {
        "product_name": "Product B Updated",
        "quantity": 2,
        "unit_price": 110
      }
    ],
    "total_amount": 380
  }
}
5. DELETE /invoices/{id} - Delete an invoice by its ID
Response (JSON):
json
Copy code
{
  "status": "success",
  "message": "Invoice deleted successfully."
}
Data Storage
The invoice data is stored in a JSON file located in the root directory of the project, called invoices.json. The JSON file contains an array of invoice objects, each representing an invoice with details like id, customer_name, date, details (list of products), and total_amount.

Notes:
This backend is lightweight and simple, using a JSON file for storage. It is ideal for small-scale applications, but for larger projects or production, it is recommended to use a full-fledged database.
The total_amount for each invoice is automatically calculated based on the quantity and unit price of the products in the details array.
