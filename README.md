Banking Application
A full-stack banking application built with Flask (backend) and HTML/CSS/JavaScript (frontend). The application allows users to register, log in, manage accounts, and perform transactions. Root users have additional privileges, such as creating, updating, and deleting accounts, as well as creating transactions.


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




