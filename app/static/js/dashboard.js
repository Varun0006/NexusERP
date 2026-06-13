// Dashboard utility functions
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}
function showNotification(title, message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    document.querySelector('main').insertBefore(alertDiv, document.querySelector('main').firstChild);
}
