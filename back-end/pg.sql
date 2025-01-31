


DROP TABLE IF EXISTS balance_logs CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM user2;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM user2;
REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public FROM user2;
REVOKE ALL PRIVILEGES ON UserAccountView FROM user2;



-- Create the accounts table
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    balance NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the transactions table
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    amount NUMERIC(15, 2) NOT NULL,
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('deposit', 'withdrawal')) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the balance logs table
CREATE TABLE balance_logs (
    log_id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    old_balance NUMERIC(15, 2) NOT NULL,
    new_balance NUMERIC(15, 2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample users
INSERT INTO users (username, password, role) VALUES
('admin', 'hashed_password_here', 'root'),
('user1', 'hashed_password_here', 'user'),
('user2', 'hashed_password_here', 'user');

-- Insert sample accounts
INSERT INTO accounts (customer_name, email, balance) VALUES
('John Doe', 'john@example.com', 1000.00),
('Jane Smith', 'jane@example.com', 1500.50);

-- Insert sample transactions
INSERT INTO transactions (account_id, amount, transaction_type) VALUES
(1, 500.00, 'deposit'),
(1, 200.00, 'withdrawal'),
(2, 1000.00, 'deposit');

-- Insert balance log records
INSERT INTO balance_logs (account_id, old_balance, new_balance) VALUES
(1, 1000.00, 1500.00),
(1, 1500.00, 1300.00),
(2, 1500.50, 2500.50);




-- View balance logs ordered by the most recent changes
SELECT log_id, account_id, old_balance, new_balance, timestamp
FROM balance_logs
ORDER BY timestamp DESC;


-- Create a test user with the role 'user'
INSERT INTO users (username, password, role) VALUES
('test_user', 'hashed_password_here', 'user');

-- Insert an account for test_user
INSERT INTO accounts (customer_name, email, balance) 
VALUES ('Test User', 'test_user@example.com', 1000.00);


INSERT INTO transactions (account_id, amount, transaction_type) 
VALUES 
  ((SELECT account_id FROM accounts WHERE email = 'test_user@example.com'), 500.00, 'deposit'),
  ((SELECT account_id FROM accounts WHERE email = 'test_user@example.com'), 200.00, 'withdrawal'),
  ((SELECT account_id FROM accounts WHERE email = 'test_user@example.com'), 300.00, 'deposit');


INSERT INTO balance_logs (account_id, old_balance, new_balance) 
VALUES 
  ((SELECT account_id FROM accounts WHERE email = 'test_user@example.com'), 1000.00, 1500.00), 
  ((SELECT account_id FROM accounts WHERE email = 'test_user@example.com'), 1500.00, 1300.00), 
  ((SELECT account_id FROM accounts WHERE email = 'test_user@example.com'), 1300.00, 1600.00); 




 DROP VIEW IF EXISTS account_balance_view;


CREATE VIEW account_balance_view AS
SELECT a.account_id, a.customer_name, a.email, a.balance, a.created_at,
       t.transaction_id, t.amount, t.transaction_type, t.timestamp AS transaction_timestamp,
       b.log_id, b.old_balance, b.new_balance, b.timestamp AS log_timestamp
FROM accounts a
LEFT JOIN transactions t ON a.account_id = t.account_id
LEFT JOIN balance_logs b ON a.account_id = b.account_id
WHERE t.transaction_type = 'withdrawal';  


CREATE ROLE test_user WITH LOGIN PASSWORD 'your_password';

GRANT SELECT ON account_balance_view TO test_user;



REVOKE INSERT, UPDATE, DELETE ON account_balance_view FROM test_user;

SELECT * FROM account_balance_view;




CREATE OR REPLACE FUNCTION get_account_balance() 
RETURNS TABLE (
    account_id INT,
    customer_name VARCHAR,
    email VARCHAR,
    balance NUMERIC(15, 2),
    created_at TIMESTAMP,
    transaction_id INT,
    amount NUMERIC(15, 2),
    transaction_type VARCHAR,
    transaction_timestamp TIMESTAMP,
    log_id INT,
    old_balance NUMERIC(15, 2),
    new_balance NUMERIC(15, 2),
    log_timestamp TIMESTAMP
) AS $$
BEGIN
    -- Root user sees all records (both deposit and withdrawal)
    IF EXISTS (SELECT 1 FROM users WHERE username = current_user AND role = 'root') THEN
        RETURN QUERY
        SELECT a.account_id, a.customer_name, a.email, a.balance, a.created_at,
               t.transaction_id, t.amount, t.transaction_type, t.timestamp AS transaction_timestamp,
               b.log_id, b.old_balance, b.new_balance, b.timestamp AS log_timestamp
        FROM accounts a
        LEFT JOIN transactions t ON a.account_id = t.account_id
        LEFT JOIN balance_logs b ON a.account_id = b.account_id;
    ELSE
        -- Regular users (like test_user) see all deposit transactions, but not withdrawals
        RETURN QUERY
        SELECT a.account_id, a.customer_name, a.email, a.balance, a.created_at,
               t.transaction_id, t.amount, t.transaction_type, t.timestamp AS transaction_timestamp,
               b.log_id, b.old_balance, b.new_balance, b.timestamp AS log_timestamp
        FROM accounts a
        LEFT JOIN transactions t ON a.account_id = t.account_id
        LEFT JOIN balance_logs b ON a.account_id = b.account_id
        WHERE t.transaction_type = 'deposit';  -- Only deposit transactions
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Example of using the function for the current user (test role-based data access)
SELECT * FROM get_account_balance();

-- Example of using the view for root users (shows both deposits and withdrawals)
SELECT * FROM account_balance_view;

