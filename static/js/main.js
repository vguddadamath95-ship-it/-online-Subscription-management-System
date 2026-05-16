/* ============================================
   Online Subscription Management System
   Custom JavaScript - Enhanced UX
   ============================================ */

// ---------- Initialize on DOM Load ----------
document.addEventListener('DOMContentLoaded', function () {
    // Initialize Bootstrap tooltips
    initializeTooltips();
    
    // Auto-dismiss flash messages
    autoDismissFlashMessages();
    
    // Add smooth scroll behavior
    addSmoothScroll();
    
    // Initialize form enhancements
    initializeFormEnhancements();
});

// ---------- Tooltip Initialization ----------
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ---------- Form Validation ----------

/**
 * Validate the registration form before submission
 */
function validateRegisterForm() {
    var name = document.getElementById('name').value.trim();
    var email = document.getElementById('email').value.trim();
    var password = document.getElementById('password').value;
    var confirmPassword = document.getElementById('confirm_password').value;

    // Check if all fields are filled
    if (!name || !email || !password || !confirmPassword) {
        showAlert('Please fill in all fields.', 'warning');
        return false;
    }

    // Check name length
    if (name.length < 2) {
        showAlert('Name must be at least 2 characters long.', 'warning');
        return false;
    }

    // Validate email format
    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        showAlert('Please enter a valid email address.', 'warning');
        return false;
    }

    // Check password length
    if (password.length < 6) {
        showAlert('Password must be at least 6 characters long.', 'warning');
        return false;
    }

    // Check if passwords match
    if (password !== confirmPassword) {
        showAlert('Passwords do not match!', 'warning');
        return false;
    }

    return true;
}

/**
 * Validate the login form before submission
 */
function validateLoginForm() {
    var email = document.getElementById('email').value.trim();
    var password = document.getElementById('password').value;

    if (!email || !password) {
        showAlert('Please fill in all fields.', 'warning');
        return false;
    }

    return true;
}

/**
 * Validate the admin plan form (add/edit)
 */
function validatePlanForm() {
    var planName = document.getElementById('plan_name').value.trim();
    var price = document.getElementById('price').value;
    var duration = document.getElementById('duration').value;
    var features = document.getElementById('features').value.trim();

    if (!planName || !price || !duration || !features) {
        showAlert('Please fill in all plan details.', 'warning');
        return false;
    }

    if (parseFloat(price) < 0) {
        showAlert('Price cannot be negative.', 'warning');
        return false;
    }

    if (parseInt(duration) < 1) {
        showAlert('Duration must be at least 1 day.', 'warning');
        return false;
    }

    return true;
}

// ---------- Alert Helper ----------

/**
 * Display a custom alert message with Bootstrap styling
 * @param {string} message - The alert message
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type) {
    // Remove any existing custom alerts
    var existingAlerts = document.querySelectorAll('.js-custom-alert');
    existingAlerts.forEach(function (alert) {
        alert.remove();
    });

    // Create alert element with enhanced styling
    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-' + type + ' alert-dismissible fade show js-custom-alert';
    alertDiv.setAttribute('role', 'alert');
    alertDiv.style.marginTop = '1rem';
    alertDiv.style.borderLeft = '4px solid';
    
    var icon = 'bi-info-circle';
    if (type === 'success') icon = 'bi-check-circle';
    if (type === 'danger') icon = 'bi-exclamation-triangle';
    if (type === 'warning') icon = 'bi-exclamation-circle';
    
    alertDiv.innerHTML = '<i class="bi ' + icon + ' me-2"></i>' + message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';

    // Insert alert at the top of the form or page
    var form = document.querySelector('form');
    if (form) {
        form.insertBefore(alertDiv, form.firstChild);
    } else {
        var container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
    }

    // Auto-dismiss after 5 seconds
    setTimeout(function () {
        if (alertDiv.parentNode) {
            var bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, 5000);
}

// ---------- Confirm Actions ----------

/**
 * Ask for confirmation before cancelling a subscription
 */
function confirmCancel() {
    return confirm('⚠️ Are you sure you want to cancel your subscription? This action cannot be undone.');
}

/**
 * Ask for confirmation before deleting a plan (admin)
 */
function confirmDelete() {
    return confirm('⚠️ Are you sure you want to delete this plan? This will affect existing subscribers.');
}

// ---------- Auto-dismiss Flash Messages ----------
function autoDismissFlashMessages() {
    var flashMessages = document.querySelectorAll('.alert:not(.js-custom-alert):not(.js-alert)');
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            var bsAlert = new bootstrap.Alert(msg);
            bsAlert.close();
        }, 5000);
    });
}

// ---------- Smooth Scroll Behavior ----------
function addSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

// ---------- Form Enhancements ----------
function initializeFormEnhancements() {
    // Add visual feedback to form inputs on focus
    var inputs = document.querySelectorAll('.form-control, .form-check-input');
    
    inputs.forEach(function (input) {
        input.addEventListener('focus', function () {
            this.style.borderColor = '#808000';
        });
        
        input.addEventListener('blur', function () {
            this.style.borderColor = '';
        });
    });

    // Add character counter for textarea
    var textareas = document.querySelectorAll('textarea.form-control');
    textareas.forEach(function (textarea) {
        var maxChars = textarea.getAttribute('maxlength') || 500;
        var counter = document.createElement('small');
        counter.className = 'form-text';
        counter.style.color = '#6b7280';
        counter.style.display = 'block';
        counter.style.marginTop = '0.25rem';
        counter.innerHTML = '0 / ' + maxChars + ' characters';
        
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', function () {
            counter.innerHTML = this.value.length + ' / ' + maxChars + ' characters';
        });
    });
}

// ---------- Format Currency Input ----------
function formatCurrency(value) {
    return parseFloat(value).toLocaleString('en-IN', {
        style: 'currency',
        currency: 'INR'
    });
}

// ---------- Date Formatting ----------
function formatDate(dateString) {
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-IN', options);
}

// ---------- Loading State Management ----------
function setLoadingState(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...';
    } else {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text') || 'Submit';
    }
}

// ---------- Notification Toast Function ----------
function showNotification(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    
    const icon = {
        'success': 'bi-check-circle-fill',
        'danger': 'bi-exclamation-triangle-fill',
        'warning': 'bi-exclamation-circle-fill',
        'info': 'bi-info-circle-fill'
    }[type] || 'bi-info-circle-fill';
    
    toast.innerHTML = `
        <i class="bi ${icon} me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after duration
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(toast);
        bsAlert.close();
    }, duration);
}

// ---------- Keyboard Shortcuts ----------
document.addEventListener('keydown', function (e) {
    // Ctrl/Cmd + Enter to submit form (if form is focused)
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        var form = document.querySelector('form');
        if (form) form.submit();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        var modals = document.querySelectorAll('.modal.show');
        modals.forEach(function (modal) {
            new bootstrap.Modal(modal).hide();
        });
    }
});

// ---------- Page Visibility Detection ----------
document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
        // Page is hidden - pause animations if needed
    } else {
        // Page is visible - resume animations if needed
    }
});

// ---------- Deprecation: Old Alert Function ----------
// Kept for backward compatibility
function showAlertOld(message, type) {
    var existingAlerts = document.querySelectorAll('.js-alert');
    existingAlerts.forEach(function (alert) {
        alert.remove();
    });

    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-' + type + ' alert-dismissible fade show js-alert';
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = '<i class="bi bi-exclamation-circle me-2"></i>' + message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';

    var form = document.querySelector('form');
    if (form) {
        form.insertBefore(alertDiv, form.firstChild);
    }

    setTimeout(function () {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}
