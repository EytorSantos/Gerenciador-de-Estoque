document.addEventListener("DOMContentLoaded", async () => {
    const movementForm = document.getElementById("movement-form");
    const medicationSelect = document.getElementById("medication_id");
    const batchSelect = document.getElementById("batch_id");
    const typeSelect = document.getElementById("type");
    const controlledSection = document.getElementById("controlled-section");
    const twoFaSection = document.getElementById("2fa-section");
    
    let medications = [];
    let currentMedication = null;

    async function fetchData(url, method = "GET", body = null) {
        const token = localStorage.getItem("access_token");
        const headers = {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        };

        const options = { method, headers };
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(url, options);
        if (!response.ok) {
            if (response.status === 401) window.location.href = "/login.html";
            const errorData = await response.json();
            throw new Error(errorData.detail || "Erro na requisição");
        }
        return response.json();
    }

    // Carregar medicamentos
    try {
        medications = await fetchData("/api/v1/medications/");
        if (Array.isArray(medications) && medicationSelect) {
            medications.forEach(med => {
                const option = document.createElement("option");
                option.value = med.id;
                option.textContent = `${med.name} (${med.active_principle})`;
                medicationSelect.appendChild(option);
            });
        }
    } catch (error) {
        showToast(error.message, "danger");
    }

    medicationSelect.addEventListener("change", async (e) => {
        const medId = e.target.value;
        batchSelect.innerHTML = '<option value="">Selecione um lote...</option>';
        
        if (!medId) {
            batchSelect.disabled = true;
            controlledSection.style.display = "none";
            return;
        }

        currentMedication = medications.find(m => m.id == medId);
        batchSelect.disabled = false;

        // Verificar se é controlado
        checkControlled();

        try {
            const batches = await fetchData(`/api/v1/batches/medication/${medId}`);
            if (Array.isArray(batches) && batchSelect) {
                batches.forEach(batch => {
                    const option = document.createElement("option");
                    option.value = batch.id;
                    option.textContent = `Lote: ${batch.batch_number} (Qtd: ${batch.quantity}, Venc: ${new Date(batch.expiration_date).toLocaleDateString()})`;
                    batchSelect.appendChild(option);
                });
            }
        } catch (error) {
            showToast(error.message, "danger");
        }
    });

    typeSelect.addEventListener("change", checkControlled);

    function checkControlled() {
        if (currentMedication && typeSelect.value === "exit" && 
            (currentMedication.tarja === "vermelha" || currentMedication.tarja === "preta")) {
            controlledSection.style.display = "block";
            twoFaSection.style.display = "block";
            
            // Tornar campos obrigatórios
            document.getElementById("prescription_number").required = true;
            document.getElementById("doctor_name").required = true;
            document.getElementById("doctor_crm").required = true;
            document.getElementById("buyer_name").required = true;
            document.getElementById("buyer_cpf").required = true;
            document.getElementById("pharmacist_otp").required = true;
        } else {
            controlledSection.style.display = "none";
            twoFaSection.style.display = "none";
            
            // Remover obrigatoriedade
            document.getElementById("prescription_number").required = false;
            document.getElementById("doctor_name").required = false;
            document.getElementById("doctor_crm").required = false;
            document.getElementById("buyer_name").required = false;
            document.getElementById("buyer_cpf").required = false;
            document.getElementById("pharmacist_otp").required = false;
        }
    }

    movementForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        showLoading();

        const formData = new FormData(movementForm);
        
        const payload = {
            user_id: 0, // Backend deve ignorar ou usar do token, mas o schema pede
            medication_id: parseInt(formData.get("medication_id")),
            batch_id: parseInt(formData.get("batch_id")),
            type: formData.get("type"),
            quantity: parseInt(formData.get("quantity")),
            reason: formData.get("reason")
        };

        if (controlledSection.style.display === "block") {
            payload.prescription = {
                prescription_number: formData.get("prescription_number"),
                doctor_name: formData.get("doctor_name"),
                doctor_crm: formData.get("doctor_crm"),
                buyer_name: formData.get("buyer_name"),
                buyer_cpf: formData.get("buyer_cpf")
            };
            payload.pharmacist_otp = formData.get("pharmacist_otp");
        }

        try {
            await fetchData("/api/v1/movements/", "POST", payload);
            showToast("Movimentação registrada com sucesso!", "success");
            setTimeout(() => window.location.href = "/movements.html", 1500);
        } catch (error) {
            console.error("Erro ao registrar movimentação:", error);
            let msg = error.message;
            if (msg.includes("OTP")) msg = "Código 2FA do farmacêutico inválido ou expirado.";
            if (msg.includes("quantity")) msg = "Quantidade insuficiente no lote selecionado.";
            showToast(msg, "danger");
        } finally {
            hideLoading();
        }
    });
});
