'use strict';

//listener for all code
document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================================
    // GLOBAL LOGIC (Runs on EVERY page)
    // ==========================================================
    
    // --- Login/Signup Popup ---
    const loginBtn = document.getElementById('login-btn');
    const popup = document.getElementById('login-popup');
    const closeBtn = document.getElementById('close-login');
    const showLogin = document.getElementById('show-login');
    const showSignup = document.getElementById('show-signup');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            popup.style.display = 'flex';
            showLogin.classList.add('active');
            showSignup.classList.remove('active');
            loginForm.style.display = 'flex';
            signupForm.style.display = 'none';
        });
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            popup.style.display = 'none';
        });
    }
    if (showLogin) {
        showLogin.addEventListener('click', function() {
            showLogin.classList.add('active');
            showSignup.classList.remove('active');
            loginForm.style.display = 'flex';
            signupForm.style.display = 'none';
        });
    }
    if (showSignup) {
        showSignup.addEventListener('click', function() {
            showSignup.classList.add('active');
            showLogin.classList.remove('active');
            loginForm.style.display = 'none';
            signupForm.style.display = 'flex';
        });
    }
    if (popup) {
        popup.addEventListener('click', function(e) {
            if (e.target === popup) {
                popup.style.display = 'none';
            }
        });
    }

    // --- Login Form Submission ---
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault(); 
            const formData = new FormData(loginForm);
            fetch('/login', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message); 
                if (data.status === 'success') {
                    window.location.reload(); 
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // --- Signup Form Submission ---
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(signupForm);
            const password = formData.get('signup_password');
            const confirmPassword = formData.get('signup_confirm_password'); 
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
                    window.location.reload();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // --- Global Cart UI Update ---
    const cartCountSpan = document.getElementById('cart-count');
    const cartLink = document.getElementById('cart-link');
    let cartList = JSON.parse(localStorage.getItem('cartList')) || [];

    function updateCartUI() {
        let currentCart = JSON.parse(localStorage.getItem('cartList')) || [];
        let cartCount = currentCart.length;
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
    // Update cart on every page load
    updateCartUI();


    // ==========================================================
    // PAGE-SPECIFIC LOGIC
    // ==========================================================

    // --- ORDERING PAGE LOGIC ---
    // Check if '.order-btn' exists before trying to use it
    const orderButtons = document.querySelectorAll('.order-btn');
    if (orderButtons.length > 0) {
        orderButtons.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const menuItem = btn.closest('.menu-item');
                const itemName = menuItem.querySelector('h3').textContent;
                const itemPriceText = menuItem.querySelector('.menu-price').textContent;
                const itemPrice = parseFloat(itemPriceText.replace(/[^0-9.]/g, ''));
                
                // Add item to cart
                cartList = JSON.parse(localStorage.getItem('cartList')) || [];
                cartList.push({ name: itemName, price: itemPrice });
                localStorage.setItem('cartList', JSON.stringify(cartList));
                
                updateCartUI(); // Update display
            });
        });
    }

    // --- CART PAGE LOGIC ---
    // Check if '#cart-item' exists before trying to use it
    const cartItemsDiv = document.getElementById('cart-items');
    if (cartItemsDiv) {
        const cartEmptyDiv = document.getElementById('cart-empty');
        const cartTotalSpan = document.getElementById('cart-total');
        const purchaseBtn = document.getElementById('purchase-btn');
        let cart = JSON.parse(localStorage.getItem('cartList')) || []; // Use 'cart' for this page

        // --- Get Toast Elements ---
        const toastElement = document.getElementById('toast-notification');
        const toastMessage = document.getElementById('toast-message');
        let toastTimer;

        // --- Toast functions ---
        function showToast(message, type = 'processing') {
            clearTimeout(toastTimer);
            if (!toastElement || !toastMessage) return; // Safety check
            toastMessage.textContent = message;
            toastElement.className = 'toast show';
            if (type === 'success') {
                toastElement.classList.add('success');
                toastTimer = setTimeout(() => {
                    toastElement.className = 'toast';
                }, 3000);
            } else {
                toastElement.classList.remove('success');
            }
        }
        function hideToast() {
            clearTimeout(toastTimer);
            if (toastElement) toastElement.className = 'toast';
        }

        // --- Render cart function ---
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
                    name = item; price = 0;
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

        // --- Handle removing items ---
        cartItemsDiv.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-btn')) {
                const idx = parseInt(e.target.getAttribute('data-idx'));
                cart.splice(idx, 1);
                localStorage.setItem('cartList', JSON.stringify(cart));
                renderCart();
                updateCartUI(); // Update header count
            }
        });

        // --- Handle purchasing ---
        purchaseBtn.addEventListener('click', function() {
            if (cart.length === 0) return;
            showToast('Processing your order...', 'processing');
            fetch('/purchase', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(cart)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showToast('Thank you for your purchase!', 'success');
                    cart = [];
                    localStorage.setItem('cartList', JSON.stringify(cart));
                    renderCart();
                    updateCartUI(); // Update header count
                } else {
                    hideToast();
                    alert('Purchase failed: ' + data.message);
                }
            })
            .catch(error => {
                hideToast();
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });

        // --- Initial render of the cart on page load ---
        renderCart();
    }
});
