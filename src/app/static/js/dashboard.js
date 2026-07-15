document.addEventListener("DOMContentLoaded", () => {
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
                window.location.href = "/login.html"; // Redirecionar para login se não autorizado
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

    async function loadDashboardData() {
        showLoading();
        try {
            const stats = await fetchData("/api/v1/dashboard/stats");
            
            if (document.getElementById("total-medications")) document.getElementById("total-medications").textContent = stats.total_medications;
            if (document.getElementById("total-batches")) document.getElementById("total-batches").textContent = stats.total_batches;
            if (document.getElementById("controlled-medications")) document.getElementById("controlled-medications").textContent = stats.controlled_medications;
            if (document.getElementById("low-stock-count")) document.getElementById("low-stock-count").textContent = stats.low_stock_count;
            // O ID 'expiring-soon-count' não existe no novo HTML, removido para evitar erro.

            const movementsList = document.getElementById("recent-movements-list");
            if (movementsList) {
                movementsList.innerHTML = "";
                if (!stats.recent_movements || stats.recent_movements.length === 0) {
                    movementsList.innerHTML = "<p class='text-muted'>Nenhuma movimentação recente.</p>";
                } else {
                    stats.recent_movements.forEach(m => {
                        const div = document.createElement("div");
                        div.className = "movement-item";
                        const date = new Date(m.timestamp).toLocaleString();
                        const typeClass = m.type === "entry" ? "text-success" : (m.type === "exit" ? "text-danger" : "text-warning");
                        const typeLabel = m.type === "entry" ? "Entrada" : (m.type === "exit" ? "Saída" : "Ajuste/Perda");
                        
                        div.className = "list-item";
                        div.innerHTML = `
                            <div>
                                <div style="font-weight: 600;">${m.medication_name}</div>
                                <div style="font-size: 0.75rem; color: var(--text-muted);">Lote: ${m.batch_number} • ${date}</div>
                            </div>
                            <div style="text-align: right;">
                                <div class="${typeClass}" style="font-weight: 700;">${m.type === "entry" ? "+" : "-"}${m.quantity}</div>
                                <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">${typeLabel}</div>
                            </div>
                        `;
                        movementsList.appendChild(div);
                    });
                }
            }

            const expiringList = document.getElementById("expiring-medications-list");
            if (expiringList) {
                expiringList.innerHTML = "";
                if (!stats.expiring_medications || stats.expiring_medications.length === 0) {
                    expiringList.innerHTML = "<p style='padding: 1rem; color: var(--text-muted); text-align: center;'>Nenhum alerta crítico.</p>";
                } else {
                    stats.expiring_medications.forEach(item => {
                        const div = document.createElement("div");
                        div.className = "list-item";
                        const expiryDate = new Date(item.expiry_date).toLocaleDateString();
                        div.innerHTML = `
                            <div>
                                <div style="font-weight: 600;">${item.medication_name}</div>
                                <div style="font-size: 0.75rem; color: var(--text-muted);">Lote: ${item.batch_number}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: var(--danger); font-weight: 700;">${expiryDate}</div>
                                <div style="font-size: 0.7rem; color: var(--text-muted);">VENCIMENTO</div>
                            </div>
                        `;
                        expiringList.appendChild(div);
                    });
                }
            }

        } catch (error) {
            console.error("Erro ao carregar dados do dashboard:", error);
            showToast(error.message || "Erro ao carregar dados do dashboard.", "danger");
        } finally {
            hideLoading();
        }
    }

    // Carregar dados ao entrar no dashboard
    loadDashboardData();
});
