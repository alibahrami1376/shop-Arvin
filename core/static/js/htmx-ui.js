(function () {
    document.body.addEventListener("showToast", function (event) {
        if (typeof Toastify === "undefined") {
            return;
        }
        var detail = event.detail || {};
        Toastify({
            text: detail.text || "",
            className: detail.className || "info",
            duration: detail.duration || 2500,
            gravity: "top",
            position: "left",
            style: {
                background: detail.background || "#2e7d32",
            },
        }).showToast();
    });
})();
