const API_BASE_URL = 'http://127.0.0.1:5000';

const messageDiv = document.getElementById('message');
const formsSection = document.getElementById('formsSection');
const registerFormDiv = document.getElementById('registerForm');
const loginFormDiv = document.getElementById('loginForm');
const createAdFormDiv = document.getElementById('createAdForm');

// Search forms and containers
const advancedSearchFormDiv = document.getElementById('advancedSearchForm');
const carSearchForm = document.getElementById('carSearchForm');
const searchResultsSection = document.getElementById('searchResultsSection');
const searchResultsContainer = document.getElementById('searchResultsContainer');
const clearSearchResultsBtn = document.getElementById('clearSearchResultsBtn');
const relatedCarsSection = document.getElementById('relatedCarsSection');
const relatedCarsContainer = document.getElementById('relatedCarsContainer');
const clearRelatedCarsBtn = document.getElementById('clearRelatedCarsBtn');

const adsContainer = document.getElementById('adsContainer');

const showRegisterFormBtn = document.getElementById('showRegisterFormBtn');
const showLoginFormBtn = document.getElementById('showLoginFormBtn');
const showCreateAdFormBtn = document.getElementById('showCreateAdFormBtn');
const showAdvancedSearchFormBtn = document.getElementById('showAdvancedSearchFormBtn');
const logoutBtn = document.getElementById('logoutBtn');
const loggedInUserSpan = document.getElementById('loggedInUser');
const userMobileSpan = document.getElementById('userMobile');

const registrationForm = document.getElementById('registrationForm');
const loginUserForm = document.getElementById('loginUserForm');
const newAdvertisementForm = document.getElementById('newAdvertisementForm');

// NEW: Role-specific UI elements
const showUserManagementBtn = document.getElementById('showUserManagementBtn');
const userManagementSection = document.getElementById('userManagementSection');
const userListContainer = document.getElementById('userListContainer');

const showAllTransactionsBtn = document.getElementById('showAllTransactionsBtn');
const allTransactionsSection = document.getElementById('allTransactionsSection');
const transactionListContainer = document.getElementById('transactionListContainer');


let currentUserMobile = null;
let currentUserRoles = []; // NEW: Store user roles

function showMessage(msg, type = 'success') {
    messageDiv.textContent = msg;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
    setTimeout(() => {
        messageDiv.style.display = 'none';
        messageDiv.textContent = '';
    }, 5000);
}

function hideAllForms() {
    registerFormDiv.style.display = 'none';
    loginFormDiv.style.display = 'none';
    createAdFormDiv.style.display = 'none';
    advancedSearchFormDiv.style.display = 'none';
    userManagementSection.style.display = 'none'; // NEW
    allTransactionsSection.style.display = 'none'; // NEW
}

function hideAllSearchSections() {
    searchResultsSection.style.display = 'none';
    relatedCarsSection.style.display = 'none';
    document.getElementById('advertisementListing').style.display = 'block'; // Ensure advertisement listing is visible when searches are cleared
}

// NEW: Helper to check if current user has a specific role
function hasRole(roleName) {
    return currentUserRoles.includes(roleName);
}

function updateAuthUI() {
    const token = localStorage.getItem('authToken');
    currentUserMobile = localStorage.getItem('userMobile');
    const rolesString = localStorage.getItem('userRoles'); // NEW: Get roles from localStorage
    currentUserRoles = rolesString ? JSON.parse(rolesString) : []; // Parse roles array

    if (token && currentUserMobile) {
        showRegisterFormBtn.style.display = 'none';
        showLoginFormBtn.style.display = 'none';
        loggedInUserSpan.style.display = 'inline';
        userMobileSpan.textContent = currentUserMobile;
        logoutBtn.style.display = 'inline';
        showCreateAdFormBtn.style.display = 'inline';
        showAdvancedSearchFormBtn.style.display = 'inline'; // Search always visible for logged in

        // NEW: Show/hide role-specific buttons
        if (hasRole('Admin') || hasRole('Senior')) {
            showUserManagementBtn.style.display = 'inline';
            showAllTransactionsBtn.style.display = 'inline'; // Admins/Seniors can see all transactions
        } else if (hasRole('Seller') || hasRole('User')) {
            showAllTransactionsBtn.style.display = 'inline'; // Other users/sellers can see their own transactions
            showUserManagementBtn.style.display = 'none';
        } else {
            showUserManagementBtn.style.display = 'none';
            showAllTransactionsBtn.style.display = 'none';
        }

        hideAllForms();
    } else {
        showRegisterFormBtn.style.display = 'inline';
        showLoginFormBtn.style.display = 'inline';
        loggedInUserSpan.style.display = 'none';
        userMobileSpan.textContent = '';
        logoutBtn.style.display = 'none';
        showCreateAdFormBtn.style.display = 'none';
        showAdvancedSearchFormBtn.style.display = 'inline'; // Search always visible for guests
        showUserManagementBtn.style.display = 'none'; // NEW: Hide for guests
        showAllTransactionsBtn.style.display = 'none'; // NEW: Hide for guests
        currentUserRoles = []; // Clear roles for guests
    }
}

showRegisterFormBtn.addEventListener('click', () => {
    hideAllForms();
    hideAllSearchSections();
    registerFormDiv.style.display = 'block';
});

showLoginFormBtn.addEventListener('click', () => {
    hideAllForms();
    hideAllSearchSections();
    loginFormDiv.style.display = 'block';
});

showCreateAdFormBtn.addEventListener('click', () => {
    hideAllForms();
    hideAllSearchSections();
    createAdFormDiv.style.display = 'block';
});

showAdvancedSearchFormBtn.addEventListener('click', () => {
    hideAllForms();
    hideAllSearchSections();
    advancedSearchFormDiv.style.display = 'block';
    document.getElementById('advertisementListing').style.display = 'none';
});

// NEW: Event listener for User Management button
showUserManagementBtn.addEventListener('click', () => {
    hideAllForms();
    hideAllSearchSections();
    userManagementSection.style.display = 'block';
    document.getElementById('advertisementListing').style.display = 'none';
    fetchAllUsers(); // Fetch users when the section is shown
});

// NEW: Event listener for All Transactions button
showAllTransactionsBtn.addEventListener('click', () => {
    hideAllForms();
    hideAllSearchSections();
    allTransactionsSection.style.display = 'block';
    document.getElementById('advertisementListing').style.display = 'none';
    fetchAllTransactions(); // Fetch transactions when the section is shown
});


logoutBtn.addEventListener('click', async () => {
    const token = localStorage.getItem('authToken');
    if (!token) {
        showMessage('You are not logged in.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userMobile');
            localStorage.removeItem('userRoles'); // NEW: Clear roles on logout
            showMessage(data.message, 'success');
            updateAuthUI();
            fetchAllAdvertisements();
            hideAllSearchSections();
        } else {
            showMessage(data.message || 'Logout failed.', 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showMessage('An error occurred during logout.', 'error');
    }
});

registrationForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const mobile_number = document.getElementById('regMobile').value;
    const password = document.getElementById('regPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mobile_number, password })
        });

        const data = await response.json();
        if (response.ok) {
            showMessage(data.message, 'success');
            registrationForm.reset();
            hideAllForms();
            showLoginFormBtn.click();
        } else {
            showMessage(data.description || data.message || 'Registration failed.', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showMessage('An error occurred during registration.', 'error');
    }
});

loginUserForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const mobile_number = document.getElementById('loginMobile').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/login_api`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mobile_number, password })
        });

        const data = await response.json();
        if (response.ok) {
            // NOTE: Your /login_api currently doesn't return roles.
            // You MUST modify your Flask /login_api to return user.roles
            // For example: return jsonify({'message': 'Login successful', 'user_id': user.id, 'mobile_number': user.mobile_number, 'roles': [role.name for role in user.roles]}), 200
            localStorage.setItem('authToken', 'true'); // Placeholder for a real token
            localStorage.setItem('userMobile', mobile_number);
            localStorage.setItem('userRoles', JSON.stringify(data.roles || ['User'])); // NEW: Store roles, default to 'User' if not provided
            showMessage(data.message, 'success');
            loginUserForm.reset();
            updateAuthUI();
            fetchAllAdvertisements();
            hideAllSearchSections();
        } else {
            showMessage(data.message || 'Login failed.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('An error occurred during login.', 'error');
    }
});

newAdvertisementForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const token = localStorage.getItem('authToken');
    if (!token) {
        showMessage('You must be logged in to create an advertisement.', 'error');
        return;
    }

    const adData = {
        car: {
            make: document.getElementById('adMake').value,
            model: document.getElementById('adModel').value,
            year: parseInt(document.getElementById('adYear').value),
            color: document.getElementById('adColor').value,
            status: document.getElementById('adStatus').value
        },
        title: document.getElementById('adTitle').value,
        description: document.getElementById('adDescription').value,
        price: parseFloat(document.getElementById('adPrice').value)
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/advertisements`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // 'Authorization': `Bearer ${token}` // Add if your create ad endpoint requires token
            },
            body: JSON.stringify(adData)
        });

        const data = await response.json();
        if (response.ok) {
            showMessage('Advertisement created successfully!', 'success');
            newAdvertisementForm.reset();
            hideAllForms();
            fetchAllAdvertisements();
        } else {
            showMessage(data.description || data.message || 'Failed to create advertisement.', 'error');
        }
    } catch (error) {
        console.error('Create advertisement error:', error);
        showMessage('An error occurred while creating the advertisement.', 'error');
    }
});

// Advanced Car Search Logic
carSearchForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    performAdvancedSearch();
});

async function performAdvancedSearch() {
    const minPrice = document.getElementById('searchMinPrice').value;
    const maxPrice = document.getElementById('searchMaxPrice').value;
    const brand = document.getElementById('searchBrand').value;
    const color = document.getElementById('searchColor').value;
    const status = document.getElementById('searchStatus').value;

    const queryParams = new URLSearchParams();
    if (minPrice) queryParams.append('min_price', minPrice);
    if (maxPrice) queryParams.append('max_price', maxPrice);
    if (brand) queryParams.append('brand', brand);
    if (color) queryParams.append('color', color);
    if (status) queryParams.append('status', status);

    searchResultsContainer.innerHTML = 'Searching for cars...';
    searchResultsSection.style.display = 'block';
    document.getElementById('advertisementListing').style.display = 'none';
    hideAllForms();
    clearSearchResultsBtn.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/api/search/cars?${queryParams.toString()}`);
        const cars = await response.json();

        if (response.ok) {
            if (cars.length === 0) {
                searchResultsContainer.innerHTML = '<p>No cars found matching your criteria.</p>';
                return;
            }

            searchResultsContainer.innerHTML = '';
            cars.forEach(car => {
                const carCard = document.createElement('div');
                carCard.className = 'ad-card';
                carCard.innerHTML = `
                    <h3>${car.make} ${car.model}</h3>
                    <p><strong>Year:</strong> ${car.year}</p>
                    <p><strong>Color:</strong> ${car.color}</p>
                    <p><strong>Status:</strong> ${car.status}</p>
                `;
                searchResultsContainer.appendChild(carCard);
            });
        } else {
            searchResultsContainer.innerHTML = `<p class="error">Error during search: ${cars.message || 'Unknown error'}</p>`;
        }
    } catch (error) {
        console.error('Advanced search error:', error);
        searchResultsContainer.innerHTML = '<p class="error">Failed to perform search. Please check server connection.</p>';
    }
}

// Clear Search Results
clearSearchResultsBtn.addEventListener('click', () => {
    searchResultsSection.style.display = 'none';
    searchResultsContainer.innerHTML = '';
    clearSearchResultsBtn.style.display = 'none';
    document.getElementById('advertisementListing').style.display = 'block';
    fetchAllAdvertisements();
});


// Fetch Related Cars Logic
async function fetchRelatedCars(carId) {
    relatedCarsContainer.innerHTML = 'Loading related cars...';
    relatedCarsSection.style.display = 'block';
    document.getElementById('advertisementListing').style.display = 'none';
    searchResultsSection.style.display = 'none';
    hideAllForms();

    try {
        const response = await fetch(`${API_BASE_URL}/api/cars/${carId}/related`);
        const relatedCars = await response.json();

        if (response.ok) {
            if (relatedCars.length === 0) {
                relatedCarsContainer.innerHTML = '<p>No related cars found.</p>';
                return;
            }

            relatedCarsContainer.innerHTML = '';
            relatedCars.forEach(car => {
                const carCard = document.createElement('div');
                carCard.className = 'ad-card';
                carCard.innerHTML = `
                    <h3>${car.make} ${car.model}</h3>
                    <p><strong>Year:</strong> ${car.year}</p>
                    <p><strong>Color:</strong> ${car.color}</p>
                    <p><strong>Status:</strong> ${car.status}</p>
                `;
                relatedCarsContainer.appendChild(carCard);
            });
        } else {
            relatedCarsContainer.innerHTML = `<p class="error">Error loading related cars: ${relatedCars.message || 'Unknown error'}</p>`;
        }
    } catch (error) {
        console.error('Error fetching related cars:', error);
        relatedCarsContainer.innerHTML = '<p class="error">Failed to load related cars. Please check server connection.</p>';
    }
}

// Back to All Ads (from related cars)
clearRelatedCarsBtn.addEventListener('click', () => {
    relatedCarsSection.style.display = 'none';
    relatedCarsContainer.innerHTML = '';
    document.getElementById('advertisementListing').style.display = 'block';
    fetchAllAdvertisements();
});


async function fetchAllAdvertisements() {
    adsContainer.innerHTML = 'Loading advertisements...';
    try {
        const response = await fetch(`${API_BASE_URL}/api/advertisements`);
        const ads = await response.json();

        if (response.ok) {
            if (ads.length === 0) {
                adsContainer.innerHTML = '<p>No advertisements found.</p>';
                return;
            }

            adsContainer.innerHTML = '';
            ads.forEach(ad => {
                const adCard = document.createElement('div');
                adCard.className = 'ad-card';
                adCard.setAttribute('data-ad-id', ad.id); // Store ad ID for potential actions
                adCard.setAttribute('data-car-id', ad.car_details ? ad.car_details.id : ''); // Store car ID
                adCard.setAttribute('data-publisher-id', ad.user_id); // Store publisher ID

                adCard.innerHTML = `
                    <h3>${ad.title}</h3>
                    <p><strong>Car:</strong> ${ad.car_details ? ad.car_details.make + ' ' + ad.car_details.model : 'N/A'}</p>
                    <p><strong>Year:</strong> ${ad.car_details ? ad.car_details.year : 'N/A'}</p>
                    <p><strong>Color:</strong> ${ad.car_details ? ad.car_details.color : 'N/A'}</p>
                    <p><strong>Status:</strong> ${ad.status}</p>
                    <p>${ad.description || 'No description provided.'}</p>
                    <p class="price">Price: $${parseFloat(ad.price).toLocaleString()}</p>
                    <p><strong>Published by:</strong> ${ad.publisher_mobile || 'Unknown'}</p>
                    <p><small>Created: ${new Date(ad.created_at).toLocaleString()}</small></p>
                    ${ad.car_details && ad.car_details.id ? `<button class="view-related-btn" data-car-id="${ad.car_details.id}">View Related Cars</button>` : ''}
                    <div class="ad-actions" style="margin-top: 10px;">
                        ${(hasRole('Admin') || hasRole('Senior') || (localStorage.getItem('userMobile') === ad.publisher_mobile)) ?
                            `<button class="edit-ad-btn" data-ad-id="${ad.id}" style="background-color: #ffc107; margin-right: 5px;">Edit</button>
                             <button class="delete-ad-btn" data-ad-id="${ad.id}" style="background-color: #dc3545;">Delete</button>`
                            : ''
                        }
                        ${hasRole('User') && (localStorage.getItem('userMobile') !== ad.publisher_mobile) ?
                            `<button class="initiate-transaction-btn" data-car-id="${ad.car_details.id}" data-ad-id="${ad.id}" data-ad-price="${ad.price}" style="background-color: #28a745;">Buy Now</button>`
                            : ''
                        }
                    </div>
                `;
                adsContainer.appendChild(adCard);
            });

            // Attach event listeners to newly created buttons
            document.querySelectorAll('.view-related-btn').forEach(button => {
                button.addEventListener('click', (event) => {
                    const carId = event.target.dataset.carId;
                    if (carId) {
                        fetchRelatedCars(carId);
                    }
                });
            });

            // NEW: Edit Ad Button Event Listener (example - you'd need a separate edit form)
            document.querySelectorAll('.edit-ad-btn').forEach(button => {
                button.addEventListener('click', (event) => {
                    const adId = event.target.dataset.adId;
                    showMessage(`Editing advertisement ID: ${adId} (Functionality not fully implemented yet)`, 'info');
                    // TODO: Implement actual edit form and PUT request
                });
            });

            // NEW: Delete Ad Button Event Listener
            document.querySelectorAll('.delete-ad-btn').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const adId = event.target.dataset.adId;
                    if (confirm(`Are you sure you want to delete advertisement ID: ${adId}?`)) {
                        await deleteAdvertisement(adId);
                    }
                });
            });

            // NEW: Initiate Transaction Button Event Listener
            document.querySelectorAll('.initiate-transaction-btn').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const carId = event.target.dataset.carId;
                    const adId = event.target.dataset.adId;
                    const adPrice = event.target.dataset.adPrice;
                    if (confirm(`Initiate transaction for Car ID: ${carId} at price $${adPrice}?`)) {
                        await initiateTransaction(carId, adPrice);
                    }
                });
            });


        } else {
            adsContainer.innerHTML = `<p class="error">Error loading advertisements: ${ads.message || 'Unknown error'}</p>`;
        }
    } catch (error) {
        console.error('Error fetching advertisements:', error);
        adsContainer.innerHTML = '<p class="error">Failed to load advertisements. Please check server connection.</p>';
    }
}

// NEW: Function to handle deleting an advertisement
async function deleteAdvertisement(adId) {
    const token = localStorage.getItem('authToken');
    if (!token) {
        showMessage('You must be logged in to delete an advertisement.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/advertisements/${adId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}` // Assuming your delete endpoint requires token
            }
        });

        if (response.ok) {
            showMessage(`Advertisement ${adId} deleted successfully!`, 'success');
            fetchAllAdvertisements(); // Refresh the list
        } else {
            const data = await response.json();
            showMessage(data.description || data.message || `Failed to delete advertisement ${adId}.`, 'error');
        }
    } catch (error) {
        console.error('Delete advertisement error:', error);
        showMessage('An error occurred while deleting the advertisement.', 'error');
    }
}

// NEW: Function to handle initiating a transaction
async function initiateTransaction(carId, agreedPrice) {
    const token = localStorage.getItem('authToken');
    if (!token) {
        showMessage('You must be logged in to initiate a transaction.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/transactions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ car_id: carId, agreed_price: agreedPrice })
        });

        const data = await response.json();
        if (response.ok) {
            showMessage(data.message, 'success');
            // Optionally, refresh ads or update the specific ad's status if transaction initiated
        } else {
            showMessage(data.description || data.message || 'Failed to initiate transaction.', 'error');
        }
    } catch (error) {
        console.error('Initiate transaction error:', error);
        showMessage('An error occurred while initiating the transaction.', 'error');
    }
}


// NEW: Fetch All Users (Admin/Senior)
async function fetchAllUsers() {
    userListContainer.innerHTML = 'Loading users...';
    const token = localStorage.getItem('authToken');
    if (!token) {
        userListContainer.innerHTML = '<p class="error">Not authorized to view users.</p>';
        showMessage('Not authorized to view users.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/users`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const users = await response.json();

        if (response.ok) {
            if (users.length === 0) {
                userListContainer.innerHTML = '<p>No users found.</p>';
                return;
            }

            userListContainer.innerHTML = '';
            users.forEach(user => {
                const userCard = document.createElement('div');
                userCard.className = 'ad-card'; // Reusing card styling
                userCard.innerHTML = `
                    <h3>User: ${user.mobile_number}</h3>
                    <p>ID: ${user.id}</p>
                    <p>Active: ${user.active ? 'Yes' : 'No'}</p>
                    <p>Roles: ${user.roles.join(', ')}</p>
                    ${user.active && user.mobile_number !== currentUserMobile ?
                        `<button class="deactivate-user-btn" data-user-id="${user.id}" style="background-color: #dc3545;">Deactivate</button>` : ''
                    }
                `;
                userListContainer.appendChild(userCard);
            });

            // Attach event listeners for deactivate buttons
            document.querySelectorAll('.deactivate-user-btn').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const userId = event.target.dataset.userId;
                    if (confirm(`Are you sure you want to deactivate user ID: ${userId}?`)) {
                        await deactivateUser(userId);
                    }
                });
            });

        } else {
            userListContainer.innerHTML = `<p class="error">Error loading users: ${users.message || 'Unknown error'}</p>`;
            showMessage(users.message || 'Failed to load users.', 'error');
        }
    } catch (error) {
        console.error('Error fetching users:', error);
        userListContainer.innerHTML = '<p class="error">Failed to load users. Please check server connection.</p>';
        showMessage('Failed to load users.', 'error');
    }
}

// NEW: Deactivate User Functionality
async function deactivateUser(userId) {
    const token = localStorage.getItem('authToken');
    if (!token) {
        showMessage('Not authorized to deactivate users.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/users/${userId}/deactivate`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            showMessage(`User ${userId} deactivated successfully!`, 'success');
            fetchAllUsers(); // Refresh the user list
        } else {
            const data = await response.json();
            showMessage(data.description || data.message || `Failed to deactivate user ${userId}.`, 'error');
        }
    } catch (error) {
        console.error('Deactivate user error:', error);
        showMessage('An error occurred while deactivating the user.', 'error');
    }
}

// NEW: Fetch All Transactions (Admin/Senior/Seller/User)
async function fetchAllTransactions() {
    transactionListContainer.innerHTML = 'Loading transactions...';
    const token = localStorage.getItem('authToken');
    if (!token) {
        transactionListContainer.innerHTML = '<p class="error">Not authorized to view transactions.</p>';
        showMessage('Not authorized to view transactions.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/transactions`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const transactions = await response.json();

        if (response.ok) {
            if (transactions.length === 0) {
                transactionListContainer.innerHTML = '<p>No transactions found.</p>';
                return;
            }

            transactionListContainer.innerHTML = '';
            transactions.forEach(t => {
                const transactionCard = document.createElement('div');
                transactionCard.className = 'ad-card'; // Reusing card styling
                transactionCard.innerHTML = `
                    <h3>Transaction ID: ${t.id}</h3>
                    <p>Car: ${t.car_make || 'N/A'} (ID: ${t.car_id})</p>
                    <p>Buyer: ${t.buyer_mobile} (ID: ${t.buyer_id})</p>
                    <p>Seller: ${t.seller_mobile} (ID: ${t.seller_id})</p>
                    <p>Agreed Price: $${parseFloat(t.agreed_price).toLocaleString()}</p>
                    <p>Status: <strong>${t.status}</strong></p>
                    <p>Date: ${new Date(t.transaction_date).toLocaleString()}</p>
                    <div class="transaction-actions" style="margin-top: 10px;">
                        ${(hasRole('Admin') || hasRole('Senior') || (t.seller_mobile === currentUserMobile)) && t.status === 'pending' ?
                            `<button class="update-transaction-status-btn" data-transaction-id="${t.id}" data-status="accepted" style="background-color: #28a745; margin-right: 5px;">Accept</button>
                             <button class="update-transaction-status-btn" data-transaction-id="${t.id}" data-status="rejected" style="background-color: #dc3545;">Reject</button>`
                            : ''
                        }
                        ${(hasRole('Admin') || hasRole('Senior') || (t.seller_mobile === currentUserMobile)) && (t.status === 'accepted' || t.status === 'rejected') ?
                            `<button class="update-transaction-status-btn" data-transaction-id="${t.id}" data-status="completed" style="background-color: #007bff;">Mark as Completed</button>`
                            : ''
                        }
                    </div>
                `;
                transactionListContainer.appendChild(transactionCard);
            });

            // Attach event listeners for transaction status update buttons
            document.querySelectorAll('.update-transaction-status-btn').forEach(button => {
                button.addEventListener('click', async (event) => {
                    const transactionId = event.target.dataset.transactionId;
                    const newStatus = event.target.dataset.status;
                    if (confirm(`Change transaction ${transactionId} status to ${newStatus}?`)) {
                        await updateTransactionStatus(transactionId, newStatus);
                    }
                });
            });

        } else {
            transactionListContainer.innerHTML = `<p class="error">Error loading transactions: ${transactions.message || 'Unknown error'}</p>`;
            showMessage(transactions.message || 'Failed to load transactions.', 'error');
        }
    } catch (error) {
        console.error('Error fetching transactions:', error);
        transactionListContainer.innerHTML = '<p class="error">Failed to load transactions. Please check server connection.</p>';
        showMessage('Failed to load transactions.', 'error');
    }
}

// NEW: Update Transaction Status Functionality
async function updateTransactionStatus(transactionId, newStatus) {
    const token = localStorage.getItem('authToken');
    if (!token) {
        showMessage('Not authorized to update transaction status.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/transactions/${transactionId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            showMessage(`Transaction ${transactionId} status updated to ${newStatus}!`, 'success');
            fetchAllTransactions(); // Refresh the transaction list
        } else {
            const data = await response.json();
            showMessage(data.description || data.message || `Failed to update transaction ${transactionId}.`, 'error');
        }
    } catch (error) {
        console.error('Update transaction status error:', error);
        showMessage('An error occurred while updating transaction status.', 'error');
    }
}


document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI();
    fetchAllAdvertisements();
});