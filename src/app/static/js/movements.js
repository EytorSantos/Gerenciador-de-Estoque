document.addEventListener("DOMContentLoaded", () => {
    const movementsTableBody = document.getElementById("movements-table-body");
    const noMovementsMessage = document.getElementById("no-movements-message");
    const searchInput = document.getElementById("search-movement");
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

    async function loadMovements(query = "") {
        showLoading();
        try {
            const movements = await fetchData("/api/v1/movements/");
            
            // Para exibir nomes em vez de IDs, precisamos buscar meds, lotes e users ou ter um endpoint que já traga isso.
            // Para o MVP, vamos buscar os dados básicos e exibir o que temos.
            // Idealmente, o backend deveria retornar esses nomes no MovementResponse.
            
            const filteredMovements = movements.filter(m => 
                (m.medication_name && m.medication_name.toLowerCase().includes(query.toLowerCase())) ||
                (m.batch_number && m.batch_number.toLowerCase().includes(query.toLowerCase())) ||
                (m.username && m.username.toLowerCase().includes(query.toLowerCase())) ||
                m.type.toLowerCase().includes(query.toLowerCase()) ||
                m.reason.toLowerCase().includes(query.toLowerCase())
            );

            displayMovements(filteredMovements);
        } catch (error) {
            console.error("Erro ao carregar movimentações:", error);
            showToast(error.message || "Erro ao carregar movimentações.", "danger");
        } finally {
            hideLoading();
        }
    }

    function displayMovements(movements) {
        if (!movementsTableBody) return;
        movementsTableBody.innerHTML = "";
        if (!movements || movements.length === 0) {
            if (noMovementsMessage) noMovementsMessage.style.display = "block";
            return;
        }
        if (noMovementsMessage) noMovementsMessage.style.display = "none";

        movements.forEach(movement => {
            const row = movementsTableBody.insertRow();
            row.innerHTML = `
                <td>${movement.id}</td>
                <td>${movement.medication_name}</td>
                <td>${movement.batch_number}</td>
                <td>${movement.type}</td>
                <td>${movement.quantity}</td>
                <td>${new Date(movement.timestamp).toLocaleString()}</td>
                <td>${movement.username}</td>
            `;
        });
    }

    searchInput.addEventListener("input", (event) => {
        loadMovements(event.target.value);
    });

    loadMovements();
});
