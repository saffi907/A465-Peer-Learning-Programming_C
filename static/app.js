/**
 * Bypass -- Frontend Utilities
 * Internal portal script
 */

// TODO: remove before production
// Debug API endpoint: /api/debug
// Contains sensitive configuration data -- for dev use only

document.addEventListener("DOMContentLoaded", function () {
    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll(".flash-message");
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.opacity = "0";
            msg.style.transform = "translateY(-10px)";
            setTimeout(function () { msg.remove(); }, 400);
        }, 4000);
    });
});
