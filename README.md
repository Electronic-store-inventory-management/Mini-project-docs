# Electronics Store Inventory Management System

## Overview

The Electronics Store Inventory Management System is a Django-based web application for managing electronic components and monitoring inventory levels. It provides functionality for viewing component details, adding new components, validating component information, and tracking stock availability.

## Features

- **User Authentication:** Login-protected access to inventory functionality.
- **View Components:** Display component details and current quantities.
- **Add Components:** Add new components through a form.
- **Input Validation:** Validate component details, including quantity, minimum stock level, and unit price.
- **Availability Tracking:** Identify components as available, low stock, or out of stock.
- **Low Stock Monitoring:** View components that require restocking.
- **Out-of-Stock Management:** View components whose quantity has reached zero.
- **Component Deletion:** Delete components through a confirmation page.

## Technology Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, Django Templates
- **Database:** Django-supported database configuration
- **Version Control:** Git and GitHub

## Screen Recording / Demo

Watch the project demonstration and screen recording here:

[**View the Screen Recording on Google Drive**](https://drive.google.com/file/d/1iX7vPZvKeql2OzC-kMbkmyKdl8p8j4to/view?usp=sharing)

Ensure that the recording's sharing permissions allow the intended reviewers to access it.

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Electronic-store-inventory-management/Mini-project-docs.git
   cd Mini-project-docs
   ```

2. Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the required environment variables using `.env.example`. Set an appropriate secret key and database configuration for your environment.

5. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

6. Create an administrator account if required:

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

8. Open the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Running Tests

Run the Django test suite with:

```bash
python manage.py test
```

Check the project configuration with:

```bash
python manage.py check
```

## Repository

[GitHub Repository](https://github.com/Electronic-store-inventory-management/Mini-project-docs)
