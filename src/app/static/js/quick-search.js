document.addEventListener("DOMContentLoaded", () => {
    const quickSearchInput = document.getElementById("quick-search-input");
    const searchResultsBody = document.getElementById("quick-search-results-body");
    const noResultsMessage = document.getElementById("no-results-message");
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

    async function performQuickSearch(query) {
        showLoading();
        try {
            const medications = await fetchData(`/api/v1/quick-search/?query=${encodeURIComponent(query)}`);
            displaySearchResults(medications);
        } catch (error) {
            console.error("Erro ao realizar consulta rápida:", error);
            showToast(error.message || "Erro ao realizar consulta rápida.", "danger");
        } finally {
            hideLoading();
        }
    }

    function displaySearchResults(medications) {
        if (!searchResultsBody) return;
        searchResultsBody.innerHTML = "";
        if (!medications || medications.length === 0) {
            if (noResultsMessage) noResultsMessage.style.display = "block";
            return;
        }
        if (noResultsMessage) noResultsMessage.style.display = "none";

        medications.forEach(medication => {
            const row = searchResultsBody.insertRow();
            row.innerHTML = `
                <td>${medication.barcode}</td>
                <td>${medication.name}</td>
                <td>${medication.active_principle}</td>
                <td>${medication.dosage}</td>
                <td>${medication.tarja}</td>
                <td>R$ ${medication.price.toFixed(2)}</td>
                <td>${medication.current_stock}</td>
            `;
        });
    }

    quickSearchInput.addEventListener("input", (event) => {
        const query = event.target.value;
        if (query.length > 2) { // Realiza a busca após 3 caracteres para evitar muitas requisições
            performQuickSearch(query);
        } else if (query.length === 0) {
            displaySearchResults([]); // Limpa os resultados se a busca estiver vazia
        }
    });

    // Carregar resultados iniciais (opcional, pode ser vazio)
    // performQuickSearch("");
});
