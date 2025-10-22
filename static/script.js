'use strict';

document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================================
    // LOGIN/SIGNUP POPUP LOGIC
    // ==========================================================
    const loginBtn = document.getElementById('login-btn');
    const popup = document.getElementById('login-popup');
    const closeBtn = document.getElementById('close-login');
    const showLogin = document.getElementById('show-login');
    const showSignup = document.getElementById('show-signup');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    // Open popup
    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            popup.style.display = 'flex';
            // Default to login tab
            showLogin.classList.add('active');
            showSignup.classList.remove('active');
            loginForm.style.display = 'flex';
            signupForm.style.display = 'none';
        });
    }

    // Close popup with 'X' button
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            popup.style.display = 'none';
        });
    }

    // Switch to login tab
    if (showLogin) {
        showLogin.addEventListener('click', function() {
            showLogin.classList.add('active');
            showSignup.classList.remove('active');
            loginForm.style.display = 'flex';
            signupForm.style.display = 'none';
        });
    }

    // Switch to signup tab
    if (showSignup) {
        showSignup.addEventListener('click', function() {
            showSignup.classList.add('active');
            showLogin.classList.remove('active');
            loginForm.style.display = 'none';
            signupForm.style.display = 'flex';
        });
    }

    // Close popup by clicking background
    if (popup) {
        popup.addEventListener('click', function(e) {
            if (e.target === popup) {
                popup.style.display = 'none';
            }
        });
    }

    // ==========================================================
    // FORM SUBMISSION LOGIC
    // ==========================================================
    
    // --- Handle Login Form Submission ---
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission
            const formData = new FormData(loginForm);

            fetch('/login', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message); // Show success/error message
                if (data.status === 'success') {
                    window.location.reload(); // Reload the page on successful login
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // --- Handle Signup Form Submission ---
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(signupForm);
            const password = formData.get('signup_password');
            const confirmPassword = formData.get('signup_confirm_password'); // Make sure your input has name="confirm_password"

            if (password !== confirmPassword) {
                alert("Passwords do not match!");
                return;
            }

            fetch('/signup', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if (data.status === 'success') {
                    window.location.reload(); // Reload the page on successful signup
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }
});

// ==========================================================
    // ORDERING LOGIC
    // ==========================================================

document.addEventListener('DOMContentLoaded', function() {
    // Cart logic with localStorage
    const cartCountSpan = document.getElementById('cart-count');
    const cartLink = document.getElementById('cart-link');
    const orderButtons = document.querySelectorAll('.order-btn');

    // Load cart items from localStorage
    let cartList = JSON.parse(localStorage.getItem('cartList')) || [];

    // --- Function to update the cart UI (count and icon state) ---
    function updateCartUI() {
        let cartCount = cartList.length;
        if (cartCountSpan) {
            cartCountSpan.textContent = cartCount;
        }
        if (cartLink) {
            if (cartCount > 0) {
                cartLink.classList.add('cart-active');
            } else {
                cartLink.classList.remove('cart-active');
            }
        }
    }

    // Add listener to all "Order" buttons
    orderButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const menuItem = btn.closest('.menu-item'); // Safer way to get parent
            const itemName = menuItem.querySelector('h3').textContent;
            const itemPriceText = menuItem.querySelector('.menu-price').textContent;
            const itemPrice = parseFloat(itemPriceText.replace(/[^0-9.]/g, ''));
            
            cartList.push({ name: itemName, price: itemPrice });
            localStorage.setItem('cartList', JSON.stringify(cartList));
            
            updateCartUI(); // Update display
        });
    });

    // --- Update cart on page load ---
    updateCartUI();
});

    // ==========================================================
    // CART LOGIC
    // ==========================================================
document.addEventListener('DOMContentLoaded', function() {
    const cartItemsDiv = document.getElementById('cart-items');
    const cartEmptyDiv = document.getElementById('cart-empty');
    const cartTotalSpan = document.getElementById('cart-total');
    const purchaseBtn = document.getElementById('purchase-btn');
    let cart = JSON.parse(localStorage.getItem('cartList')) || [];

    // --- Function to render all items in the cart ---
    function renderCart() {
        cartItemsDiv.innerHTML = '';
        let total = 0;
        if (cart.length === 0) {
            cartEmptyDiv.style.display = 'block';
            cartTotalSpan.textContent = '$0.00';
            purchaseBtn.style.display = 'none';
            return;
        }

        cartEmptyDiv.style.display = 'none';
        purchaseBtn.style.display = 'inline-block';

        cart.forEach((item, idx) => {
            let name, price;
            if (typeof item === 'object' && item !== null && 'price' in item) {
                name = item.name;
                price = item.price;
            } else {
                name = item;
                price = 0; // Fallback for old/bad data
            }
            total += price;
            const div = document.createElement('div');
            div.className = 'cart-item';
            div.innerHTML = `
                <span class="cart-item-name">${name}</span>
                <span class="cart-item-price">${price ? `$${price.toFixed(2)}` : ''}</span>
                <button class="remove-btn" data-idx="${idx}">Remove</button>
            `;
            cartItemsDiv.appendChild(div);
        });
        cartTotalSpan.textContent = `$${total.toFixed(2)}`;
    }

    // --- Handle removing items from the cart ---
    if (cartItemsDiv) {
        cartItemsDiv.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-btn')) {
                const idx = parseInt(e.target.getAttribute('data-idx'));
                cart.splice(idx, 1);
                localStorage.setItem('cartList', JSON.stringify(cart));
                renderCart(); // Re-render the cart
                
                // Update the main cart count in the header
                const cartCountSpan = document.getElementById('cart-count');
                if (cartCountSpan) cartCountSpan.textContent = cart.length;
            }
        });
    }

    // --- Handle the "Purchase" button click ---
    if (purchaseBtn) {
        purchaseBtn.addEventListener('click', function() {
            if (cart.length === 0) return;

            // Send cart data to the backend
            fetch('/purchase', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(cart)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // SUCCESS: Clear the cart and update UI
                    alert('Thank you for your purchase!');
                    cart = [];
                    localStorage.setItem('cartList', JSON.stringify(cart));
                    
                    renderCart();
                    const cartCountSpan = document.getElementById('cart-count');
                    if (cartCountSpan) cartCountSpan.textContent = '0';
                } else {
                    alert('Purchase failed: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    }

    // --- Initial render of the cart on page load ---
    renderCart();
});