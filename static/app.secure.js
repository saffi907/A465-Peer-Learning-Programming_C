/**
 * Bypass -- Frontend Utilities
 * Internal portal script (production)
 */

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
