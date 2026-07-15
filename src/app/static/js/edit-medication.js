document.addEventListener("DOMContentLoaded", () => {
    const editMedicationForm = document.getElementById("edit-medication-form");
    const medicationIdInput = document.getElementById("medication-id");
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

    // Função para obter o ID do medicamento da URL
    function getMedicationIdFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get("id");
    }

    async function loadMedicationData(medicationId) {
        showLoading();
        try {
            const medication = await fetchData(`/api/v1/medications/${medicationId}`);
            medicationIdInput.value = medication.id;
            document.getElementById("barcode").value = medication.barcode;
            document.getElementById("name").value = medication.name;
            document.getElementById("active_principle").value = medication.active_principle;
            document.getElementById("dosage").value = medication.dosage;
            document.getElementById("manufacturer").value = medication.manufacturer;
            document.getElementById("tarja").value = medication.tarja;
            document.getElementById("price").value = medication.price;
            document.getElementById("min_stock").value = medication.min_stock;
        } catch (error) {
            console.error("Erro ao carregar dados do medicamento:", error);
            showToast(error.message || "Erro ao carregar dados do medicamento.", "danger");
        } finally {
            hideLoading();
        }
    }

    if (editMedicationForm) {
        const medicationId = getMedicationIdFromUrl();
        if (medicationId) {
            loadMedicationData(medicationId);
        } else {
            showToast("ID do medicamento não encontrado na URL.", "danger");
            // Opcional: redirecionar de volta para a lista de medicamentos
            // window.location.href = "/medications.html";
        }

        editMedicationForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const updatedMedicationData = {
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
                await fetchData(`/api/v1/medications/${medicationIdInput.value}`, "PUT", updatedMedicationData);
                showToast("Medicamento atualizado com sucesso!", "success");
                setTimeout(() => {
                    window.location.href = "/medications.html";
                }, 1500);
            } catch (error) {
                console.error("Erro ao atualizar medicamento:", error);
                showToast(error.message || "Erro ao atualizar medicamento.", "danger");
            } finally {
                hideLoading();
            }
        });
    }
});
