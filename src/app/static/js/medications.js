document.addEventListener("DOMContentLoaded", () => {
    const medicationsTableBody = document.getElementById("medications-table-body");
    const noMedicationsMessage = document.getElementById("no-medications-message");
    const searchInput = document.getElementById("search-medication");
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
            let errorMessage = errorData.detail || "Erro ao buscar dados";
            if (Array.isArray(errorData.detail)) {
                errorMessage = errorData.detail.map(err => err.msg).join("; ");
            }
            throw new Error(errorMessage);
        }
        return response.json();
    }

    async function loadMedications(query = "") {
        showLoading();
        try {
            let url = "/api/v1/medications/";
            if (query) {
                url = `/api/v1/quick-search/?query=${encodeURIComponent(query)}`;
            }
            const medications = await fetchData(url);
            displayMedications(medications);
        } catch (error) {
            console.error("Erro ao carregar medicamentos:", error);
            showToast(error.message || "Erro ao carregar medicamentos.", "danger");
        } finally {
            hideLoading();
        }
    }

    function displayMedications(medications) {
        if (!medicationsTableBody) return;
        medicationsTableBody.innerHTML = "";
        if (!medications || medications.length === 0) {
            if (noMedicationsMessage) noMedicationsMessage.style.display = "block";
            return;
        }
        if (noMedicationsMessage) noMedicationsMessage.style.display = "none";

        medications.forEach(medication => {
            const row = medicationsTableBody.insertRow();
            row.innerHTML = `
                <td>${medication.barcode}</td>
                <td>${medication.name}</td>
                <td>${medication.active_principle}</td>
                <td>${medication.dosage}</td>
                <td>${medication.manufacturer}</td>
                <td>${medication.tarja}</td>
                <td>R$ ${medication.price.toFixed(2)}</td>
                <td>${medication.min_stock}</td>
                <td class="actions-cell">
                    <button class="btn-icon edit-btn" data-id="${medication.id}">✏️</button>
                    <button class="btn-icon delete-btn" data-id="${medication.id}">🗑️</button>
                </td>
            `;
        });

        document.querySelectorAll(".edit-btn").forEach(button => {
            button.addEventListener("click", (event) => {
                const medicationId = event.target.dataset.id;
                window.location.href = `/edit-medication.html?id=${medicationId}`;
            });
        });

        document.querySelectorAll(".delete-btn").forEach(button => {
            button.addEventListener("click", async (event) => {
                const medicationId = event.target.dataset.id;
                if (confirm("Tem certeza que deseja excluir este medicamento?")) {
                    showLoading();
                    try {
                        await fetchData(`/api/v1/medications/${medicationId}`, "DELETE");
                        showToast("Medicamento excluído com sucesso!", "success");
                        loadMedications(); // Recarregar a lista
                    } catch (error) {
                        console.error("Erro ao excluir medicamento:", error);
                        showToast(error.message || "Erro ao excluir medicamento.", "danger");
                    } finally {
                        hideLoading();
                    }
                }
            });
        });
    }

    searchInput.addEventListener("input", (event) => {
        loadMedications(event.target.value);
    });

    loadMedications();
});
