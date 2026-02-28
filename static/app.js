/**
 * Bypass: Frontend Utilities
 * Internal portal script
 */

document.addEventListener("DOMContentLoaded", function () {
    // left in by a developer during testing
    console.log("[DEBUG] Health check: /api/debug, remove before production");

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
