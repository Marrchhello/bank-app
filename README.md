Banking Application
A full-stack banking application built with Flask (backend) and HTML/CSS/JavaScript (frontend). The application allows users to register, log in, manage accounts, and perform transactions. Root users have additional privileges, such as creating, updating, and deleting accounts, as well as creating transactions.

Features
User Features
Register: Create a new user account.

Login: Authenticate and log in as a user.

View Account: View account details and transaction history.

Root User Features
Create Account: Create a new bank account.

Update Account: Update account details (e.g., customer name, email, balance).

Delete Account: Delete an existing account.

Create Transaction: Perform deposit or withdrawal transactions.

Technologies Used
Backend
Flask: A lightweight Python web framework.

Flask-CORS: Handles Cross-Origin Resource Sharing (CORS) for frontend-backend communication.

Flask-JWT-Extended: Manages JSON Web Tokens (JWT) for user authentication.

SQLAlchemy: An ORM for database interactions.

PostgreSQL: The database used to store user, account, and transaction data.

Frontend
HTML: Structure of the web pages.

CSS: Styling for the user interface.

JavaScript: Handles user interactions and API calls.

Setup Instructions
Prerequisites
Python 3.x: Install Python from python.org.

PostgreSQL: Install PostgreSQL from postgresql.org.

Node.js (Optional): Required if you want to use a live server for the frontend.

Backend Setup
Clone the repository:

bash
Copy
git clone <repository-url>
cd banking-app
Create a virtual environment and activate it:

bash
Copy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install the required Python packages:

bash
Copy
pip install -r requirements.txt
Set up the PostgreSQL database:

Create a database named bank.

Update the SQLALCHEMY_DATABASE_URI in app.py with your PostgreSQL credentials:

python
Copy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/bank'
Run the Flask application:

bash
Copy
python app.py
The backend will be available at http://127.0.0.1:5000.

Frontend Setup
Open the frontend folder:

bash
Copy
cd frontend
Serve the frontend using a live server:

If you have Node.js installed, you can use http-server:

bash
Copy
npx http-server
Alternatively, open index.html directly in your browser.

The frontend will be available at http://127.0.0.1:5500 (or another port depending on your setup).

API Endpoints
Authentication
POST /register: Register a new user.

json
Copy
{
  "username": "testuser",
  "password": "testpass"
}
POST /login: Log in as a user.

json
Copy
{
  "username": "testuser",
  "password": "testpass"
}
Account Management
POST /accounts: Create a new bank account (root only).

json
Copy
{
  "customer_name": "John Doe",
  "email": "john@example.com",
  "balance": 1000.00
}
GET /accounts/<int:account_id>: View account details and transactions.

PUT /accounts/<int:account_id>: Update account details (root only).

DELETE /accounts/<int:account_id>: Delete an account (root only).

Transaction Management
POST /transactions: Create a new transaction (root only).

json
Copy
{
  "account_id": 1,
  "amount": 100.00,
  "transaction_type": "deposit"
}
GET /transactions/<int:account_id>: View transaction history for an account.

Usage
Register a User:

Open the registration form and fill in the details.

Submit the form to create a new user.

Log In:

Enter your username and password to log in.

If you log in as a root user, additional features will be available.

Manage Accounts:

Create Account: Fill in the form to create a new bank account.

View Account: Enter an account ID to view its details and transactions.

Update Account: Update account details (root only).

Delete Account: Delete an account (root only).

Create Transactions:

Perform deposit or withdrawal transactions for an account (root only).




