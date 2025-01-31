document.addEventListener('DOMContentLoaded', () => {
    const BASE_URL = 'http://127.0.0.1:5000'; 
    const loginSection = document.getElementById('login-section');
    const registerSection = document.getElementById('register-section');
    const accountSection = document.getElementById('account-section');
    const createAccountForm = document.getElementById('create-account-form');
    const viewAccountDetails = document.getElementById('view-account-details');
    const updateAccountForm = document.getElementById('update-account-form');
    const deleteAccountForm = document.getElementById('delete-account-form');
    const createTransactionForm = document.getElementById('create-transaction-form');
    const accountInfo = document.getElementById('account-info');

    let token = null;
    let currentUser = null;

    // Toggle between login and registration forms
    document.getElementById('register-link').addEventListener('click', () => {
        loginSection.style.display = 'none';
        registerSection.style.display = 'block';
    });

    document.getElementById('login-link').addEventListener('click', () => {
        registerSection.style.display = 'none';
        loginSection.style.display = 'block';
    });

    // Login Form Submission
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch(`${BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();
            if (response.ok) {
                token = data.access_token;
                currentUser = await fetchCurrentUser(token); 
                loginSection.style.display = 'none';
                accountSection.style.display = 'block';
                toggleRootFeatures(currentUser.role === 'root'); 
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Fetch current user details
    async function fetchCurrentUser(token) {
        try {
            const response = await fetch(`${BASE_URL}/current-user`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to fetch user details');
            }

            return await response.json();
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Toggle root features based on role
    function toggleRootFeatures(isRoot) {
        document.getElementById('update-account-btn').style.display = isRoot ? 'block' : 'none';
        document.getElementById('delete-account-btn').style.display = isRoot ? 'block' : 'none';
        document.getElementById('create-transaction-btn').style.display = isRoot ? 'block' : 'none';
    }

    // Logout Button
    document.getElementById('logout-btn').addEventListener('click', () => {
        token = null;
        currentUser = null;
        accountSection.style.display = 'none';
        loginSection.style.display = 'block';
    });

    // Create Account Button
    document.getElementById('create-account-btn').addEventListener('click', () => {
        createAccountForm.style.display = 'block';
        viewAccountDetails.style.display = 'none';
        updateAccountForm.style.display = 'none';
        deleteAccountForm.style.display = 'none';
        createTransactionForm.style.display = 'none';
    });

    // View Account Button
    document.getElementById('view-account-btn').addEventListener('click', () => {
        viewAccountDetails.style.display = 'block';
        createAccountForm.style.display = 'none';
        updateAccountForm.style.display = 'none';
        deleteAccountForm.style.display = 'none';
        createTransactionForm.style.display = 'none';
    });

    // Update Account Button
    document.getElementById('update-account-btn').addEventListener('click', () => {
        updateAccountForm.style.display = 'block';
        createAccountForm.style.display = 'none';
        viewAccountDetails.style.display = 'none';
        deleteAccountForm.style.display = 'none';
        createTransactionForm.style.display = 'none';
    });

    // Delete Account Button
    document.getElementById('delete-account-btn').addEventListener('click', () => {
        deleteAccountForm.style.display = 'block';
        createAccountForm.style.display = 'none';
        viewAccountDetails.style.display = 'none';
        updateAccountForm.style.display = 'none';
        createTransactionForm.style.display = 'none';
    });

    // Create Transaction Button
    document.getElementById('create-transaction-btn').addEventListener('click', () => {
        createTransactionForm.style.display = 'block';
        createAccountForm.style.display = 'none';
        viewAccountDetails.style.display = 'none';
        updateAccountForm.style.display = 'none';
        deleteAccountForm.style.display = 'none';
    });

    // Registration Form Submission
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;

        try {
            const response = await fetch(`${BASE_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();
            if (response.ok) {
                alert('Registration successful. Please login.');
                registerSection.style.display = 'none';
                loginSection.style.display = 'block';
            } else {
                alert(data.error || 'Registration failed');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Create Account Form Submission
    document.getElementById('create-account-form-inner').addEventListener('submit', async (e) => {
        e.preventDefault();
        const customerName = document.getElementById('customer-name').value;
        const email = document.getElementById('email').value;
        const initialBalance = document.getElementById('initial-balance').value;

        try {
            const response = await fetch(`${BASE_URL}/accounts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    customer_name: customerName,
                    email: email,
                    balance: initialBalance,
                }),
            });

            const data = await response.json();
            if (response.ok) {
                alert('Account created successfully');
                createAccountForm.style.display = 'none';
            } else {
                alert(data.error || 'Failed to create account');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Fetch Account Details
    document.getElementById('fetch-account-btn').addEventListener('click', async () => {
        const accountId = document.getElementById('account-id').value;

        try {
            const response = await fetch(`${BASE_URL}/accounts/${accountId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            const data = await response.json();
            if (response.ok) {
                accountInfo.innerHTML = `
                    <p><strong>Account ID:</strong> ${data.account_id}</p>
                    <p><strong>Customer Name:</strong> ${data.customer_name}</p>
                    <p><strong>Email:</strong> ${data.email}</p>
                    <p><strong>Balance:</strong> $${data.balance}</p>
                    <h4>Transactions:</h4>
                    <ul>
                        ${data.transactions.map(t => `
                            <li>
                                <strong>Amount:</strong> $${t.amount} (${t.transaction_type})<br>
                                <strong>Timestamp:</strong> ${t.timestamp}
                            </li>
                        `).join('')}
                    </ul>
                `;
            } else {
                alert(data.error || 'Failed to fetch account details');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Update Account Form Submission
    document.getElementById('update-account-form-inner').addEventListener('submit', async (e) => {
        e.preventDefault();
        const accountId = document.getElementById('update-account-id').value;
        const customerName = document.getElementById('update-customer-name').value;
        const email = document.getElementById('update-email').value;
        const balance = document.getElementById('update-balance').value;

        try {
            const response = await fetch(`${BASE_URL}/accounts/${accountId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    customer_name: customerName,
                    email: email,
                    balance: balance,
                }),
            });

            const data = await response.json();
            if (response.ok) {
                alert('Account updated successfully');
            } else {
                alert(data.error || 'Failed to update account');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Delete Account Form Submission
    document.getElementById('delete-account-form-inner').addEventListener('submit', async (e) => {
        e.preventDefault();
        const accountId = document.getElementById('delete-account-id').value;

        try {
            const response = await fetch(`${BASE_URL}/accounts/${accountId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            const data = await response.json();
            if (response.ok) {
                alert('Account deleted successfully');
            } else {
                alert(data.error || 'Failed to delete account');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Create Transaction Form Submission
    document.getElementById('create-transaction-form-inner').addEventListener('submit', async (e) => {
        e.preventDefault();
        const accountId = document.getElementById('transaction-account-id').value;
        const amount = document.getElementById('transaction-amount').value;
        const transactionType = document.getElementById('transaction-type').value;

        try {
            const response = await fetch(`${BASE_URL}/transactions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    account_id: accountId,
                    amount: amount,
                    transaction_type: transactionType,
                }),
            });

            const data = await response.json();
            if (response.ok) {
                alert('Transaction created successfully');
            } else {
                alert(data.error || 'Failed to create transaction');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
