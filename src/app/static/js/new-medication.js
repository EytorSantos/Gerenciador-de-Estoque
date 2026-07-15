document.addEventListener("DOMContentLoaded", () => {
    const newMedicationForm = document.getElementById("new-medication-form");
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

    if (newMedicationForm) {
        newMedicationForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const medicationData = {
                barcode: document.getElementById("barcode").value,
                name: document.getElementById("name").value,
                active_principle: document.getElementById("active_principle").value,
                dosage: document.getElementById("dosage").value,
                manufacturer: document.getElementById("manufacturer").value,
                tarja: document.getElementById("tarja").value,
                price: parseFloat(document.getElementById("price").value),
                min_stock: parseInt(document.getElementById("min_stock").value),
            };

            showLoading();

            try {
                await fetchData("/api/v1/medications/", "POST", medicationData);
                showToast("Medicamento cadastrado com sucesso!", "success");
                setTimeout(() => {
                    window.location.href = "/medications.html";
                }, 1500);
            } catch (error) {
                console.error("Erro ao cadastrar medicamento:", error);
                showToast(error.message || "Erro ao cadastrar medicamento.", "danger");
            } finally {
                hideLoading();
            }
        });
    }
});
