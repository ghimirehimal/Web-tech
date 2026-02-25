/**
 * JUTTA LAGANI - Form Validation
 * Client-side form validation for all forms
 */

$(document).ready(function() {
    // Initialize validation
    validateForms();
    
    // Real-time validation
    realTimeValidation();
    
    // Password strength checker
    passwordStrength();
});

/**
 * Main validation function
 */
function validateForms() {
    // Registration Form Validation
    $('#registerForm').on('submit', function(e) {
        let isValid = true;
        
        // Username validation
        const username = $('#username').val();
        if (username.length < 3) {
            showError('username', 'Username must be at least 3 characters');
            isValid = false;
        }
        
        // Email validation
        const email = $('#email').val();
        if (!validateEmail(email)) {
            showError('email', 'Please enter a valid email address');
            isValid = false;
        }
        
        // Password validation
        const password = $('#password').val();
        if (password.length < 6) {
            showError('password', 'Password must be at least 6 characters');
            isValid = false;
        }
        
        // Confirm password
        const confirmPassword = $('#confirm_password').val();
        if (password !== confirmPassword) {
            showError('confirm_password', 'Passwords do not match');
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
    
    // Login Form Validation
    $('#loginForm').on('submit', function(e) {
        let isValid = true;
        
        const email = $('#email').val();
        if (!validateEmail(email)) {
            showError('email', 'Please enter a valid email address');
            isValid = false;
        }
        
        const password = $('#password').val();
        if (!password) {
            showError('password', 'Please enter your password');
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
    
    // Checkout Form Validation
    $('#checkoutForm').on('submit', function(e) {
        let isValid = true;
        
        // Shipping name
        const shippingName = $('#shipping_name').val();
        if (!shippingName.trim()) {
            showError('shipping_name', 'Please enter your full name');
            isValid = false;
        }
        
        // Shipping address
        const shippingAddress = $('#shipping_address').val();
        if (!shippingAddress.trim()) {
            showError('shipping_address', 'Please enter your address');
            isValid = false;
        }
        
        // City
        const shippingCity = $('#shipping_city').val();
        if (!shippingCity.trim()) {
            showError('shipping_city', 'Please enter your city');
            isValid = false;
        }
        
        // Phone
        const shippingPhone = $('#shipping_phone').val();
        if (!shippingPhone.trim() || !validatePhone(shippingPhone)) {
            showError('shipping_phone', 'Please enter a valid phone number');
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
    
    // Contact Form Validation
    $('#contactForm').on('submit', function(e) {
        let isValid = true;
        
        const name = $('#name').val();
        if (!name.trim()) {
            showError('name', 'Please enter your name');
            isValid = false;
        }
        
        const email = $('#email').val();
        if (!validateEmail(email)) {
            showError('email', 'Please enter a valid email address');
            isValid = false;
        }
        
        const message = $('#message').val();
        if (!message.trim()) {
            showError('message', 'Please enter your message');
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
}

/**
 * Real-time validation on blur
 */
function realTimeValidation() {
    // Email validation
    $('input[type="email"]').on('blur', function() {
        const value = $(this).val();
        if (value && !validateEmail(value)) {
            showError($(this).attr('id'), 'Please enter a valid email address');
        } else {
            clearError($(this).attr('id'));
        }
    });
    
    // Phone validation
    $('input[type="tel"], input[name="phone"], input[name="shipping_phone"]').on('blur', function() {
        const value = $(this).val();
        if (value && !validatePhone(value)) {
            showError($(this).attr('id'), 'Please enter a valid phone number');
        } else {
            clearError($(this).attr('id'));
        }
    });
    
    // Password match validation
    $('input[name="confirm_password"], input[id="confirm_password"]').on('blur', function() {
        const password = $('input[name="password"], input[id="password"]').val();
        const confirm = $(this).val();
        if (confirm && password !== confirm) {
            showError($(this).attr('id'), 'Passwords do not match');
        } else {
            clearError($(this).attr('id'));
        }
    });
    
    // Required field validation
    $('input[required], textarea[required], select[required]').on('blur', function() {
        const value = $(this).val();
        if (!value || !value.trim()) {
            showError($(this).attr('id'), 'This field is required');
        } else {
            clearError($(this).attr('id'));
        }
    });
}

/**
 * Password strength checker
 */
function passwordStrength() {
    $('input[name="password"], input[id="password"]').on('keyup', function() {
        const password = $(this).val();
        const strength = calculatePasswordStrength(password);
        
        // Update strength indicator
        const indicator = $('#passwordStrength');
        if (indicator.length) {
            indicator.removeClass('weak medium strong very-strong');
            indicator.addClass(strength.class);
            indicator.text(strength.text);
        }
    });
}

/**
 * Calculate password strength
 */
function calculatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 6) score++;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    if (score <= 2) {
        return { class: 'weak', text: 'Weak' };
    } else if (score <= 4) {
        return { class: 'medium', text: 'Medium' };
    } else if (score <= 5) {
        return { class: 'strong', text: 'Strong' };
    } else {
        return { class: 'very-strong', text: 'Very Strong' };
    }
}

/**
 * Email validation helper
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Phone validation helper
 */
function validatePhone(phone) {
    // Indian phone number format (10 digits)
    const re = /^[6-9]\d{9}$/;
    return re.test(phone.replace(/\s/g, ''));
}

/**
 * Show error message
 */
function showError(fieldId, message) {
    const field = $('#' + fieldId);
    field.addClass('is-invalid');
    
    // Remove existing error
    field.siblings('.invalid-feedback').remove();
    
    // Add error message
    field.after('<div class="invalid-feedback">' + message + '</div>');
}

/**
 * Clear error message
 */
function clearError(fieldId) {
    const field = $('#' + fieldId);
    field.removeClass('is-invalid');
    field.siblings('.invalid-feedback').remove();
}

/**
 * Validate product form
 */
function validateProductForm() {
    let isValid = true;
    
    // Name
    if (!$('#name').val().trim()) {
        showError('name', 'Product name is required');
        isValid = false;
    }
    
    // Description
    if (!$('#description').val().trim()) {
        showError('description', 'Description is required');
        isValid = false;
    }
    
    // Price
    const price = parseFloat($('#price').val());
    if (!price || price <= 0) {
        showError('price', 'Please enter a valid price');
        isValid = false;
    }
    
    // Stock
    const stock = parseInt($('#stock').val());
    if (isNaN(stock) || stock < 0) {
        showError('stock', 'Please enter valid stock quantity');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Cart quantity validation
 */
function validateQuantity(input) {
    const value = parseInt($(input).val());
    const min = parseInt($(input).attr('min')) || 1;
    const max = parseInt($(input).attr('max')) || 999;
    
    if (value < min) {
        $(input).val(min);
    } else if (value > max) {
        $(input).val(max);
    }
}
