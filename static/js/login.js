// Get URL parameters
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');
const userType = urlParams.get('type');

console.log('URL userType:', userType);
console.log('URL token:', token);

// Page initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing page...');

    const userTypeBadge = document.getElementById('userTypeBadge');
    const tokenDisplay = document.getElementById('tokenDisplay');
    const signupSection = document.getElementById('signupSection');
    const signupLink = document.getElementById('signupLink');

    // Debug: Check if elements exist
    console.log('Elements found:', {
        userTypeBadge: userTypeBadge !== null,
        tokenDisplay: tokenDisplay !== null,
        signupSection: signupSection !== null,
        signupLink: signupLink !== null
    });

    // Update user type badge
    if (userTypeBadge) {
        if (userType) {
            userTypeBadge.textContent = userType.charAt(0).toUpperCase() + userType.slice(1) + ' Login';
        } else {
            userTypeBadge.textContent = 'General Login';
        }
    }

    // Update token display
    if (tokenDisplay) {
        if (token) {
            tokenDisplay.textContent = token;
        } else {
            tokenDisplay.textContent = 'No token provided';
        }
    }

    // Handle signup section
    if (signupSection) {
        // FORCE HIDE the signup section first
        signupSection.style.display = 'none';

        // Display user type and handle signup visibility
        if (userType) {
            console.log('Processing userType:', userType);

            // Show sign-up button ONLY for users and couriers
            if (userType === 'users' || userType === 'couriers') {
                console.log('Showing signup for:', userType);
                signupSection.style.display = 'block';
                if (signupLink) {
                    signupLink.href = `signup.html?type=${userType}&token=${token}`;
                }
            } else if (userType === 'managers') {
                console.log('Hiding signup for managers');
                signupSection.style.display = 'none';
            }
        } else {
            signupSection.style.display = 'none';
        }
    } else {
        console.error('signupSection not found!');
    }
});

// Login form submission handler
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const customerId = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Determine which JSON file to use based on token
    let jsonFile;
    let userCategory;

    switch(token) {
        case 'USR_TOKEN':
            jsonFile = '../customers.json';
            userCategory = 'user';
            break;
        case 'CUR_TOKEN':
            jsonFile = '../courier.json';
            userCategory = 'courier';
            break;
        case 'MGR_TOKEN':
            jsonFile = '../managers.json';
            userCategory = 'manager';
            break;
        default:
        showErrorHeader('Invalid access token. Please start from the main page.', 'info');
        return;
    }

    console.log(`Loading ${jsonFile} for ${userCategory} authentication`);

    try {
        // Load the appropriate JSON file
        const response = await fetch(jsonFile);
        if (!response.ok) {
            throw new Error(`Could not load ${userCategory} data`);
        }

        const userData = await response.json();
        console.log(`Loaded ${userData.length} ${userCategory} records`);

        // Find matching user based on user type
        let authenticatedUser;

        if (userCategory === 'user') {
            // For users, check customer_id and password
            authenticatedUser = userData.find(user =>
                user.customer_id === customerId && user.password === password
            );
        } else if (userCategory === 'courier') {
            // For couriers, check courier_id and password
            authenticatedUser = userData.find(user =>
                user.courier_id === parseInt(customerId) && user.password === password
            );
        } else if (userCategory === 'manager') {
            // For managers, check manager_id and password
            authenticatedUser = userData.find(user =>
                user.manager_id === customerId && user.password === password
            );
        }

        if (authenticatedUser) {
            // Login successful
            console.log(`${userCategory} login successful for:`, authenticatedUser.name);

            // Store user info for next page
            sessionStorage.setItem('currentUser', JSON.stringify(authenticatedUser));
            sessionStorage.setItem('userType', userType);
            sessionStorage.setItem('userCategory', userCategory);
            sessionStorage.setItem('authToken', token);

            // Redirect to appropriate dashboard
            window.location.href = `dashboard.html?type=${userType}&category=${userCategory}&id=${customerId}`;

        } else {
            // Login failed
            showErrorHeader('Wrong credentials. Please try again.');
            document.getElementById('password').value = ''; // Clear password field
        }

    } catch (error) {
        console.error(`${userCategory} login error:`, error);
        showErrorHeader(`${userCategory} login system temporarily unavailable. Please try again later.`);
    }
});

// Function to show error header
function showErrorHeader(message, type = 'error') {
    const errorHeader = document.getElementById('errorHeader');
    const errorText = document.getElementById('errorText');

    if (errorHeader && errorText) {
        errorText.textContent = message;

        // Reset classes
        errorHeader.className = 'error-header';

        // Add type class
        if (type === 'success') {
            errorHeader.classList.add('success');
        } else if (type === 'info') {
            errorHeader.classList.add('info');
        }

        errorHeader.style.display = 'block';

    }
}

// Function to hide error header
function hideErrorHeader() {
    const errorHeader = document.getElementById('errorHeader');
    if (errorHeader) {
        errorHeader.style.display = 'none';
    }
}

// Function to show success header
function showSuccessHeader(message) {
    showErrorHeader(message, 'success');
}
