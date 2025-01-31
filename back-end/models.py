from extensions import db

class Account(db.Model):
    __tablename__ = 'accounts'
    account_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    balance = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

   
    transactions = db.relationship('Transaction', backref='account', lazy=True)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    transaction_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_type = db.Column(db.Enum('deposit', 'withdrawal', name='transaction_type_enum'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")  # Role-based access control
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class BalanceLog(db.Model):
    __tablename__ = 'balance_logs'
    log_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)
    old_balance = db.Column(db.Numeric(15, 2), nullable=False)
    new_balance = db.Column(db.Numeric(15, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())