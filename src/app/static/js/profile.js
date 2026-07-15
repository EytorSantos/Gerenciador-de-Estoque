document.addEventListener("DOMContentLoaded", () => {
    const profileForm = document.getElementById("profile-form");
    const logoutBtn = document.getElementById("logout-btn");

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("access_token");
            localStorage.removeItem("token_type");
            window.location.href = "/login.html";
        });
    }

    async function fetchData(url, method = "GET", body = null) {
        const token = localStorage.getItem("access_token");
        const headers = {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        };

        const options = {
            method,
            headers,
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = "/login.html";
            }
            const errorData = await response.json();
            let errorMessage = errorData.detail || "Erro na requisição";
            if (Array.isArray(errorData.detail)) {
                errorMessage = errorData.detail.map(err => err.msg).join("; ");
            }
            throw new Error(errorMessage);
        }
        return response.json();
    }

    async function loadUserProfile() {
        showLoading();
        try {
            const user = await fetchData("/api/v1/users/me/");
            if (document.getElementById("username")) document.getElementById("username").value = user.username;
            if (document.getElementById("email")) document.getElementById("email").value = user.email;
            
            const roleEl = document.getElementById("display-role");
            if (roleEl) {
                roleEl.textContent = user.role === "pharmacist" ? "Farmacêutico" : (user.role === "admin" ? "Administrador" : "Auxiliar");
            }
            
            if (user.role === "pharmacist" && document.getElementById("crm-group")) {
                document.getElementById("crm-group").style.display = "block";
            }

            const initialsEl = document.getElementById("avatar-initials");
            if (initialsEl && user.username) {
                initialsEl.textContent = user.username.substring(0, 1).toUpperCase();
            }

            const nameEl = document.getElementById("display-name");
            if (nameEl) nameEl.textContent = user.username;

            // O backend retorna o profile aninhado
            if (user.profile) {
                if (document.getElementById("full_name")) {
                    document.getElementById("full_name").value = user.profile.full_name || "";
                    if (nameEl && user.profile.full_name) nameEl.textContent = user.profile.full_name;
                }
                if (document.getElementById("cpf")) document.getElementById("cpf").value = user.profile.cpf || "";
                if (document.getElementById("crm")) document.getElementById("crm").value = user.profile.crm || "";
            }
        } catch (error) {
            console.error("Erro ao carregar perfil do usuário:", error);
            showToast(error.message || "Erro ao carregar perfil do usuário.", "danger");
        } finally {
            hideLoading();
        }
    }

    if (profileForm) {
        loadUserProfile();

        profileForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const updatedProfileData = {
                full_name: document.getElementById("full_name").value,
                cpf: document.getElementById("cpf").value,
                crm: document.getElementById("crm").value,
            };

            showLoading();

            try {
                // Precisamos garantir que o backend suporte atualização de perfil via user controller ou criar um profile controller
                const user = await fetchData("/api/v1/users/me/");
                await fetchData(`/api/v1/users/${user.id}`, "PUT", { profile: updatedProfileData });
                showToast("Perfil atualizado com sucesso!", "success");
            } catch (error) {
                console.error("Erro ao atualizar perfil:", error);
                showToast(error.message || "Erro ao atualizar perfil.", "danger");
            } finally {
                hideLoading();
            }
        });
    }
});
