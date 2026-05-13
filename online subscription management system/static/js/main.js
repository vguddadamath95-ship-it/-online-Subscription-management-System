/* ============================================
   Online Subscription Management System
   Custom JavaScript
   ============================================ */

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
        showAlert('Please fill in all fields.', 'danger');
        return false;
    }

    // Check name length
    if (name.length < 2) {
        showAlert('Name must be at least 2 characters long.', 'danger');
        return false;
    }

    // Validate email format
    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        showAlert('Please enter a valid email address.', 'danger');
        return false;
    }

    // Check password length
    if (password.length < 6) {
        showAlert('Password must be at least 6 characters long.', 'danger');
        return false;
    }

    // Check if passwords match
    if (password !== confirmPassword) {
        showAlert('Passwords do not match!', 'danger');
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
        showAlert('Please fill in all fields.', 'danger');
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
        showAlert('Please fill in all plan details.', 'danger');
        return false;
    }

    if (parseFloat(price) < 0) {
        showAlert('Price cannot be negative.', 'danger');
        return false;
    }

    if (parseInt(duration) < 1) {
        showAlert('Duration must be at least 1 day.', 'danger');
        return false;
    }

    return true;
}

// ---------- Alert Helper ----------

/**
 * Display a Bootstrap alert message at the top of the form
 * @param {string} message - The alert message
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type) {
    // Remove any existing alerts
    var existingAlerts = document.querySelectorAll('.js-alert');
    existingAlerts.forEach(function (alert) {
        alert.remove();
    });

    // Create alert element
    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-' + type + ' alert-dismissible fade show js-alert';
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = '<i class="bi bi-exclamation-circle me-2"></i>' + message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';

    // Insert alert at the top of the form
    var form = document.querySelector('form');
    if (form) {
        form.insertBefore(alertDiv, form.firstChild);
    }

    // Auto-dismiss after 5 seconds
    setTimeout(function () {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// ---------- Confirm Actions ----------

/**
 * Ask for confirmation before cancelling a subscription
 */
function confirmCancel() {
    return confirm('Are you sure you want to cancel your subscription? This action cannot be undone.');
}

/**
 * Ask for confirmation before deleting a plan (admin)
 */
function confirmDelete() {
    return confirm('Are you sure you want to delete this plan? This will also affect existing subscribers.');
}

// ---------- Auto-dismiss Flash Messages ----------

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss flash messages after 5 seconds
    var flashMessages = document.querySelectorAll('.alert:not(.js-alert)');
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            var bsAlert = new bootstrap.Alert(msg);
            bsAlert.close();
        }, 5000);
    });
});
