# Credit Approval

## Overview

Brief overview of the project and its purpose.

## Setup

### Prerequisites

- Python (version 3.9.12)
- Django (version 4.2.10)
- PostgreSQL (version 15.6)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/rajasekhar161819/credit_approvel.git
   ```

2. Navigate to the project directory:

   ```bash
   cd credit_approvel
   ```


### Database Setup

1. Run migrations to create customer and loan tables:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Perform any other database-related operations needed to reflect the changes made.

### Loading Data

To load CSV files into the customer and loan tables, run:

```bash
python credit_approvel/load_data.py
```

### Running the Server

Start the Django development server:

```bash
python manage.py runserver
```

The server will be running at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).


