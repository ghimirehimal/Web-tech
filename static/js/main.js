/**
 * JUTTA LAGANI - Main JavaScript
 * Interactive functionality for the e-commerce website
 */

$(document).ready(function() {
    // Initialize
    console.log('JUTTA LAGANI - Website Loaded');
    
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Navbar scroll effect
    $(window).scroll(function() {
        if ($(this).scrollTop() > 50) {
            $('.navbar').addClass('scrolled');
        } else {
            $('.navbar').removeClass('scrolled');
        }
    });
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Product quantity buttons
    initQuantityButtons();
    
    // Smooth scroll for anchor links
    smoothScroll();
    
    // Image lazy loading
    lazyLoadImages();
    
    // Search functionality
    initSearch();
});

/**
 * Initialize quantity +/- buttons
 */
function initQuantityButtons() {
    $('.qty-btn').on('click', function() {
        const $input = $(this).siblings('.qty-input');
        let value = parseInt($input.val());
        const min = parseInt($input.attr('min')) || 1;
        const max = parseInt($input.attr('max')) || 999;
        
        if ($(this).text() === '+' && value < max) {
            $input.val(value + 1);
        } else if ($(this).text() === '-' && value > min) {
            $input.val(value - 1);
        }
        
        // Trigger change event
        $input.trigger('change');
    });
}

/**
 * Smooth scroll functionality
 */
function smoothScroll() {
    $('a[href^="#"]').on('click', function(event) {
        const target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 500);
        }
    });
}

/**
 * Lazy load images
 */
function lazyLoadImages() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(function(img) {
            imageObserver.observe(img);
        });
    }
}

/**
 * Search functionality
 */
function initSearch() {
    const searchForm = $('.search-form');
    const searchInput = searchForm.find('input[type="search"]');
    
    searchInput.on('keypress', function(e) {
        if (e.which === 13) {
            const query = $(this).val().trim();
            if (query.length > 0) {
                searchForm.submit();
            }
        }
    });
}

/**
 * Add to cart with AJAX
 */
function addToCart(productId, quantity = 1) {
    $.ajax({
        url: '/add_to_cart/' + productId,
        method: 'POST',
        data: { quantity: quantity },
        success: function(response) {
            // Update cart count in navbar
            updateCartCount();
            
            // Show success message
            showAlert('Product added to cart!', 'success');
        },
        error: function() {
            showAlert('Error adding product to cart', 'danger');
        }
    });
}

/**
 * Update cart count in navbar
 */
function updateCartCount() {
    $.get('/cart/count', function(data) {
        $('.cart-btn .badge').text(data.count);
    });
}

/**
 * Show alert message
 */
function showAlert(message, type) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    $('.flash-messages').append(alertHtml);
    
    // Auto hide after 3 seconds
    setTimeout(function() {
        $('.alert').last().fadeOut('slow', function() {
            $(this).remove();
        });
    }, 3000);
}

/**
 * Quick view product
 */
function quickView(productId) {
    window.location.href = '/product/' + productId;
}

/**
 * Add to wishlist
 */
function addToWishlist(productId) {
    // For now, just show an alert
    // Can be enhanced with AJAX
    showAlert('Added to wishlist!', 'success');
}

/**
 * Update cart item quantity
 */
function updateCartItem(cartItemId, quantity) {
    $.ajax({
        url: '/update_cart/' + cartItemId,
        method: 'POST',
        data: { quantity: quantity },
        success: function() {
            location.reload();
        },
        error: function() {
            showAlert('Error updating cart', 'danger');
        }
    });
}

/**
 * Remove from cart
 */
function removeFromCart(cartItemId) {
    if (confirm('Remove this item from cart?')) {
        window.location.href = '/remove_from_cart/' + cartItemId;
    }
}

/**
 * Apply coupon code
 */
function applyCoupon() {
    const couponCode = $('#couponCode').val().trim();
    if (couponCode) {
        // AJAX call to validate coupon
        showAlert('Coupon applied!', 'success');
    } else {
        showAlert('Please enter a coupon code', 'warning');
    }
}

/**
 * Newsletter subscription
 */
function subscribeNewsletter() {
    const email = $('#newsletterEmail').val().trim();
    if (email && validateEmail(email)) {
        // AJAX call to subscribe
        showAlert('Thank you for subscribing!', 'success');
        $('#newsletterEmail').val('');
    } else {
        showAlert('Please enter a valid email', 'danger');
    }
}

/**
 * Email validation
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Price range filter
 */
function filterByPrice(min, max) {
    const url = new URL(window.location.href);
    url.searchParams.set('price_min', min);
    url.searchParams.set('price_max', max);
    window.location.href = url.toString();
}

/**
 * Sort products
 */
function sortProducts(sortBy) {
    const url = new URL(window.location.href);
    url.searchParams.set('sort', sortBy);
    window.location.href = url.toString();
}

/**
 * Category filter
 */
function filterByCategory(category) {
    if (category) {
        window.location.href = '/shop/' + category;
    } else {
        window.location.href = '/shop';
    }
}

/**
 * Product image gallery
 */
function changeImage(src) {
    $('#mainImage').attr('src', src);
    $('.thumbnail').removeClass('active');
    $(event.target).addClass('active');
}

/**
 * Mobile menu toggle
 */
$('.navbar-toggler').on('click', function() {
    $('#navbarNav').toggleClass('show');
});

/**
 * Dropdown hover effect for desktop
 */
if ($(window).width() > 991) {
    $('.nav-item.dropdown').hover(
        function() {
            $(this).find('.dropdown-menu').addClass('show');
        },
        function() {
            $(this).find('.dropdown-menu').removeClass('show');
        }
    );
}

/**
 * Back to top button
 */
$(window).scroll(function() {
    if ($(this).scrollTop() > 300) {
        $('#backToTop').fadeIn();
    } else {
        $('#backToTop').fadeOut();
    }
});

$('#backToTop').click(function() {
    $('html, body').animate({ scrollTop: 0 }, 500);
    return false;
});
