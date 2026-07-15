// main.js - Global helper functions and UI management

// Global helper functions
window.showToast = function(message, type = "info") {
    const toastContainer = document.getElementById("toast-container");
    if (!toastContainer) {
        const container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }
    
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    const icon = document.createElement("i");
    switch(type) {
        case 'success': icon.className = 'fas fa-check-circle'; break;
        case 'danger': icon.className = 'fas fa-exclamation-circle'; break;
        case 'warning': icon.className = 'fas fa-exclamation-triangle'; break;
        default: icon.className = 'fas fa-info-circle';
    }
    
    const text = document.createElement("span");
    text.textContent = message;
    
    toast.appendChild(icon);
    toast.appendChild(text);
    
    document.getElementById("toast-container").appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
};

window.showLoading = function() {
    let loadingOverlay = document.getElementById("loading-overlay");
    if (!loadingOverlay) {
        loadingOverlay = document.createElement("div");
        loadingOverlay.id = "loading-overlay";
        loadingOverlay.className = "loading-overlay";
        loadingOverlay.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(loadingOverlay);
    }
    loadingOverlay.style.display = "flex";
};

window.hideLoading = function() {
    const loadingOverlay = document.getElementById("loading-overlay");
    if (loadingOverlay) loadingOverlay.style.display = "none";
};

document.addEventListener("DOMContentLoaded", () => {
    console.log("Frontend JavaScript carregado!");

    // Theme Toggle
    const themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            document.body.classList.toggle("light-mode");
            localStorage.setItem("theme", document.body.classList.contains("light-mode") ? "light" : "dark");
        });
    }

    // Load theme preference
    if (localStorage.getItem("theme") === "light") {
        document.body.classList.add("light-mode");
    }

    // Modal Handling
    const modal = document.getElementById("modal");
    const closeModalBtn = document.getElementById("close-modal");
    if (modal && closeModalBtn) {
        closeModalBtn.addEventListener("click", () => {
            modal.style.display = "none";
        });
        window.addEventListener("click", (event) => {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        });
    }

    // Logout handling
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", (e) => {
            e.preventDefault();
            localStorage.removeItem("access_token");
            localStorage.removeItem("token_type");
            window.location.href = "/login.html";
        });
    }
});
