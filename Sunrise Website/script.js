'use strict';


document.addEventListener('DOMContentLoaded', () => {
    
    console.log('Script loaded and DOM is ready.');
});

document.addEventListener('DOMContentLoaded', function() {
    const loginBtn = document.getElementById('login-btn');
    const popup = document.getElementById('login-popup');
    const closeBtn = document.getElementById('close-login');

    loginBtn.addEventListener('click', function() {
        popup.style.display = 'flex';
    });

    closeBtn.addEventListener('click', function() {
        popup.style.display = 'none';
    });

    
    popup.addEventListener('click', function(e) {
        if (e.target === popup) {
            popup.style.display = 'none';
        }
    });
});