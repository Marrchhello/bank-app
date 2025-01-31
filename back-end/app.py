from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, event
from extensions import db
from models import Account, Transaction, User, BalanceLog
from decimal import Decimal
import logging
from sqlalchemy.orm.attributes import LoaderCallableStatus

app = Flask(__name__)


CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:3107@localhost:5432/bank'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  

jwt = JWTManager(app)


db.init_app(app)


with app.app_context():
    db.create_all()

# Trigger to log balance changes whenever there's a change in the account balance
@event.listens_for(Account.balance, 'set')
def log_balance_change(target, value, oldvalue, initiator):
    try:
        # Ensure account_id is set
        if target.account_id is None:
            return

        # Handle LoaderCallableStatus.NO_VALUE
        if oldvalue is LoaderCallableStatus.NO_VALUE:
            oldvalue = Decimal('0.00')  # Default to 0.00 for new accounts

        # Only log if the balance has changed
        if value != oldvalue:
            log = BalanceLog(
                account_id=target.account_id,
                old_balance=oldvalue,
                new_balance=value
            )
            db.session.add(log)
    except Exception as e:
        logging.error(f"Error logging balance change: {str(e)}")



# Test DB connection
@app.route('/test-db')
def test_db():
    try:
        result = db.session.execute(text('SELECT 1'))
        return jsonify({"message": "Database connection successful"}), 200
    except Exception as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

# Register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        
        if 'username' not in data or 'password' not in data:
            return jsonify({"error": "Username and password are required"}), 400

        # Hash the password before saving it to the database
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        # Create a new user instance
        new_user = User(
            username=data['username'],
            password=hashed_password,
            role=data.get('role', 'user')  # Default role is 'user'
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Return success response
        return jsonify({"message": "User registered successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username already exists"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Login user (generate access token)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        user = User.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=str(user.user_id))
            return jsonify({"access_token": access_token}), 200
        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

# Create a new bank account
@app.route('/accounts', methods=['POST'])
@jwt_required()
def create_account():
    data = request.json
    try:
        # Create the new account with proper values
        new_account = Account(
            customer_name=data['customer_name'],
            email=data['email'],
            balance=Decimal(str(data.get('balance', 0.00)))  
        )
        
        # Add the new account to the session
        db.session.add(new_account)
        db.session.commit()  # Commit to generate the account_id

        # Ensure the account_id is set
        if new_account.account_id is None:
            return jsonify({"error": "Account creation failed, account_id is None"}), 500

        # Debugging: Log the account_id and balance
        logging.info(f"Account created: account_id={new_account.account_id}, balance={new_account.balance}")

        # Create the first balance log
        first_log = BalanceLog(
            account_id=new_account.account_id, 
            old_balance=Decimal('0.00'),  # Explicitly set old_balance to 0.00
            new_balance=new_account.balance  # Use the new account's balance
        )

        # Debugging: Log the balance log details
        logging.info(f"Creating BalanceLog: account_id={first_log.account_id}, old_balance={first_log.old_balance}, new_balance={first_log.new_balance}")

        # Add the balance log to the session and commit
        db.session.add(first_log)
        db.session.commit()

        return jsonify({"message": "Account created successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 400
    except Exception as e:
        logging.error(f"Error creating account: {str(e)}")
        db.session.rollback()  # Rollback in case of any other errors
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Retrieve an account with its transactions
@app.route('/accounts/<int:account_id>', methods=['GET'])
@jwt_required()
def get_account(account_id):
    try:
        account = db.session.query(Account).outerjoin(Transaction).filter(Account.account_id == account_id).first()
        if not account:
            return jsonify({"error": "Account not found"}), 404

        account_data = {
            "account_id": account.account_id,
            "customer_name": account.customer_name,
            "email": account.email,
            "balance": float(account.balance), 
            "transactions": [{
                "transaction_id": t.transaction_id,
                "amount": float(t.amount),  
                "transaction_type": t.transaction_type,
                "timestamp": t.timestamp
            } for t in account.transactions]
        }
        return jsonify(account_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Create a new transaction (deposit or withdrawal)
@app.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    data = request.json
    try:
        # Get the current user's identity (ID from the JWT token)
        current_user_id = get_jwt_identity()

        # Fetch the current user from the database
        current_user = User.query.get(current_user_id)

        # Check if the user has the "root" role
        if current_user.role != 'root':
            return jsonify({"error": "Unauthorized: Only root users can create transactions"}), 403

        # Convert the amount to Decimal to avoid compatibility issues with float
        amount = Decimal(str(data['amount']))  

        transaction = Transaction(
            account_id=data['account_id'],
            amount=amount,
            transaction_type=data['transaction_type']
        )
        db.session.add(transaction)

        account = db.session.get(Account, data['account_id'])
        
        # Ensure account balance is a Decimal type
        if data['transaction_type'] == 'deposit':
            account.balance += amount  
        elif data['transaction_type'] == 'withdrawal':
            account.balance -= amount  

        db.session.commit()
        return jsonify({"message": "Transaction successful"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    

@app.route('/transactions/<int:account_id>', methods=['GET'])
@jwt_required()
def get_transaction_history(account_id):
    try:
        # Get the current user's identity (ID from the JWT token)
        current_user_id = get_jwt_identity()

        # Fetch the current user from the database (optional, based on role check)
        current_user = User.query.get(current_user_id)

        # Fetch the account to verify it exists
        account = Account.query.filter_by(account_id=account_id).first()

        if not account:
            return jsonify({"error": "Account not found"}), 404

       

        # Get all transactions for the account
        transactions = Transaction.query.filter_by(account_id=account_id).all()

        # Prepare the transaction history data to return
        transaction_history = [{
            "transaction_id": t.transaction_id,
            "amount": float(t.amount),
            "transaction_type": t.transaction_type,
            "timestamp": t.timestamp
        } for t in transactions]

        if not transaction_history:
            return jsonify({"message": "No transactions found for this account"}), 200

        return jsonify({"account_id": account.account_id, "transactions": transaction_history}), 200

    except Exception as e:
        return jsonify({"error": f"Error retrieving transaction history: {str(e)}"}), 500
    


# Delete an account (only for root users)
@app.route('/accounts/<int:account_id>', methods=['DELETE'])
@jwt_required()
def delete_account(account_id):
    try:
        # Get the current user's identity (ID from the JWT token)
        current_user_id = get_jwt_identity()

        # Fetch the current user from the database
        current_user = User.query.get(current_user_id)

        # Check if the user has the "root" role
        if current_user.role != 'root':
            return jsonify({"error": "Unauthorized: Only root users can delete accounts"}), 403

        # Fetch the account to be deleted
        account = Account.query.filter_by(account_id=account_id).first()

        if not account:
            return jsonify({"error": "Account not found"}), 404

        # Delete the associated transactions and balance logs
        Transaction.query.filter_by(account_id=account_id).delete()
        BalanceLog.query.filter_by(account_id=account_id).delete()

        # Delete the account
        db.session.delete(account)
        db.session.commit()

        return jsonify({"message": "Account deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Update an account (only for root users)
@app.route('/accounts/<int:account_id>', methods=['PUT'])
@jwt_required()
def update_account(account_id):
    data = request.json
    try:
        # Get the current user's identity (ID from the JWT token)
        current_user_id = get_jwt_identity()

        # Fetch the current user from the database
        current_user = User.query.get(current_user_id)

        # Check if the user has the "root" role
        if current_user.role != 'root':
            return jsonify({"error": "Unauthorized: Only root users can update accounts"}), 403

        # Fetch the account to be updated
        account = Account.query.filter_by(account_id=account_id).first()

        if not account:
            return jsonify({"error": "Account not found"}), 404

        # Update account details (name, email, balance, etc.)
        if 'customer_name' in data:
            account.customer_name = data['customer_name']
        if 'email' in data:
            account.email = data['email']
        if 'balance' in data:
            account.balance = Decimal(str(data['balance']))

        db.session.commit()

        return jsonify({"message": "Account updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True) 