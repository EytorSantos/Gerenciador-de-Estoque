document.addEventListener("DOMContentLoaded", () => {
    const generateSecretBtn = document.getElementById("generate-2fa-secret-btn");
    const qrcodeDisplay = document.getElementById("qrcode-display");
    const qrcodeImg = document.getElementById("qrcode-img");
    const secretText = document.getElementById("2fa-secret-text");
    const enable2faForm = document.getElementById("enable-2fa-form");
    const otpCodeInput = document.getElementById("otp-code");
    const disable2faForm = document.getElementById("disable-2fa-form");
    const disableOtpCodeInput = document.getElementById("disable-otp-code");
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
            throw new Error(errorData.detail || "Erro na requisição");
        }
        return response.json();
    }

    // Função para verificar o status 2FA do usuário e exibir as seções corretas
    async function check2FAStatus() {
        showLoading();
        try {
            const user = await fetchData("/api/v1/users/me/");
            if (user.is_2fa_enabled) {
                document.getElementById("2fa-generate-section").style.display = "none";
                document.getElementById("2fa-verify-section").style.display = "none";
                document.getElementById("2fa-disable-section").style.display = "block";
            } else {
                document.getElementById("2fa-generate-section").style.display = "block";
                document.getElementById("2fa-verify-section").style.display = "none";
                document.getElementById("2fa-disable-section").style.display = "none";
                // Se o segredo já foi gerado mas não ativado, mostrar QR Code
                if (user.two_factor_secret) {
                    const qrcode_uri = `otpauth://totp/FarmaciaStock:${user.email}?secret=${user.two_factor_secret}&issuer=FarmaciaStock`;
                    qrcodeImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrcode_uri)}`;
                    secretText.textContent = user.two_factor_secret;
                    qrcodeDisplay.style.display = "block";
                    document.getElementById("2fa-verify-section").style.display = "block";
                }
            }
        } catch (error) {
            console.error("Erro ao verificar status 2FA:", error);
            showToast(error.message || "Erro ao verificar status 2FA.", "danger");
        } finally {
            hideLoading();
        }
    }

    generateSecretBtn.addEventListener("click", async () => {
        showLoading();
        try {
            const response = await fetchData("/api/v1/users/me/2fa/generate-secret", "POST");
            qrcodeImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(response.qrcode_uri)}`;
            secretText.textContent = response.secret;
            qrcodeDisplay.style.display = "block";
            document.getElementById("2fa-verify-section").style.display = "block";
            showToast("Segredo 2FA gerado! Escaneie o QR Code e ative.", "info");
        } catch (error) {
            console.error("Erro ao gerar segredo 2FA:", error);
            showToast(error.message || "Erro ao gerar segredo 2FA.", "danger");
        } finally {
            hideLoading();
        }
    });

    enable2faForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const otp = otpCodeInput.value;
        showLoading();
        try {
            await fetchData("/api/v1/users/me/2fa/enable", "POST", { otp: otp });
            showToast("2FA ativado com sucesso!", "success");
            check2FAStatus(); // Atualiza a UI
        } catch (error) {
            console.error("Erro ao ativar 2FA:", error);
            let msg = error.message;
            if (msg.includes("OTP")) msg = "Código OTP inválido. Tente novamente.";
            showToast(msg, "danger");
        } finally {
            hideLoading();
        }
    });

    disable2faForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const otp = disableOtpCodeInput.value;
        showLoading();
        try {
            await fetchData("/api/v1/users/me/2fa/disable", "POST", { otp: otp });
            showToast("2FA desativado com sucesso!", "success");
            check2FAStatus(); // Atualiza a UI
        } catch (error) {
            console.error("Erro ao desativar 2FA:", error);
            let msg = error.message;
            if (msg.includes("OTP")) msg = "Código OTP inválido. Tente novamente.";
            showToast(msg, "danger");
        } finally {
            hideLoading();
        }
    });

    check2FAStatus(); // Verifica o status 2FA ao carregar a página
});
