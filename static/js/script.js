// static/js/script.js
const API_BASE_URL = 'http://127.0.0.1:5000'; // Your Flask app base URL

const messageDiv = document.getElementById('message');
const formsSection = document.getElementById('formsSection');
const registerFormDiv = document.getElementById('registerForm');
const loginFormDiv = document.getElementById('loginForm');
const createAdFormDiv = document.getElementById('createAdForm');
const adsContainer = document.getElementById('adsContainer');

const showRegisterFormBtn = document.getElementById('showRegisterFormBtn');
const showLoginFormBtn = document.getElementById('showLoginFormBtn');
const showCreateAdFormBtn = document.getElementById('showCreateAdFormBtn');
const logoutBtn = document.getElementById('logoutBtn');
const loggedInUserSpan = document.getElementById('loggedInUser');
const userMobileSpan = document.getElementById('userMobile');

const registrationForm = document.getElementById('registrationForm');
const loginUserForm = document.getElementById('loginUserForm');
const newAdvertisementForm = document.getElementById('newAdvertisementForm');

let currentUserMobile = null; // To store the mobile number of the logged-in user

// --- UI Utility Functions ---

function showMessage(msg, type = 'success') {
    messageDiv.textContent = msg;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
    setTimeout(() => {
        messageDiv.style.display = 'none';
        messageDiv.textContent = '';
    }, 5000); // Hide after 5 seconds
}

function hideAllForms() {
    registerFormDiv.style.display = 'none';
    loginFormDiv.style.display = 'none';
    createAdFormDiv.style.display = 'none';
}

function updateAuthUI() {
    const token = localStorage.getItem('authToken');
    currentUserMobile = localStorage.getItem('userMobile'); // Retrieve stored mobile number

    if (token && currentUserMobile) {
        showRegisterFormBtn.style.display = 'none';
        showLoginFormBtn.style.display = 'none';
        loggedInUserSpan.style.display = 'inline';
        userMobileSpan.textContent = currentUserMobile;
        logoutBtn.style.display = 'inline';
        showCreateAdFormBtn.style.display = 'inline';
        hideAllForms(); // Hide forms after successful login
    } else {
        showRegisterFormBtn.style.display = 'inline';
        showLoginFormBtn.style.display = 'inline';
        loggedInUserSpan.style.display = 'none';
        userMobileSpan.textContent = '';
        logoutBtn.style.display = 'none';
        showCreateAdFormBtn.style.display = 'none';
        // Do not hide forms automatically to allow user to register/login
    }
}

// --- Event Listeners for UI Buttons ---

showRegisterFormBtn.addEventListener('click', () => {
    hideAllForms();
    registerFormDiv.style.display = 'block';
});

showLoginFormBtn.addEventListener('click', () => {
    hideAllForms();
    loginFormDiv.style.display = 'block';
});

showCreateAdFormBtn.addEventListener('click', () => {
    hideAllForms();
    createAdFormDiv.style.display = 'block';
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
                'Authorization': `Bearer ${token}`, // Flask session-based, but good practice for API
                'Content-Type': 'application/json' // Logout usually doesn't need body, but good to include
            }
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userMobile');
            showMessage(data.message, 'success');
            updateAuthUI();
            fetchAllAdvertisements(); // Refresh ads, though logout usually doesn't affect public view
        } else {
            showMessage(data.message || 'Logout failed.', 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showMessage('An error occurred during logout.', 'error');
    }
});

// --- Form Submission Handlers ---

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
            showLoginFormBtn.click(); // Redirect to login form
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
        // IMPORTANT: Your login_api route is directly on the app, not under /api/
        const response = await fetch(`${API_BASE_URL}/login_api`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mobile_number, password })
        });

        const data = await response.json();
        if (response.ok) {
            // In your Flask app, you're not sending a token, but setting a session.
            // For a real SPA, you'd usually get a JWT here.
            // For now, we'll simulate 'logged in' state using the user ID and mobile.
            // A production app would handle session cookies automatically or use JWT.
            localStorage.setItem('authToken', 'true'); // Simple indicator for UI state
            localStorage.setItem('userMobile', mobile_number); // Store mobile for display
            showMessage(data.message, 'success');
            loginUserForm.reset();
            updateAuthUI();
            fetchAllAdvertisements(); // Refresh advertisements to show new options (e.g., create ad button)
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
                // Flask session handles authentication, so no explicit 'Authorization' header needed for this simple setup.
                // If using JWT, this is where you'd add: 'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(adData)
        });

        const data = await response.json();
        if (response.ok) {
            showMessage('Advertisement created successfully!', 'success');
            newAdvertisementForm.reset();
            hideAllForms();
            fetchAllAdvertisements(); // Refresh the list of ads
        } else {
            showMessage(data.description || data.message || 'Failed to create advertisement.', 'error');
        }
    } catch (error) {
        console.error('Create advertisement error:', error);
        showMessage('An error occurred while creating the advertisement.', 'error');
    }
});


// --- Fetch Advertisements Function ---

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

            adsContainer.innerHTML = ''; // Clear previous ads
            ads.forEach(ad => {
                const adCard = document.createElement('div');
                adCard.className = 'ad-card';
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
                `;
                adsContainer.appendChild(adCard);
            });
        } else {
            adsContainer.innerHTML = `<p class="error">Error loading advertisements: ${ads.message || 'Unknown error'}</p>`;
        }
    } catch (error) {
        console.error('Error fetching advertisements:', error);
        adsContainer.innerHTML = '<p class="error">Failed to load advertisements. Please check server connection.</p>';
    }
}

// --- Initial Load ---
document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI(); // Check authentication status on page load
    fetchAllAdvertisements(); // Load all ads when the page loads
});