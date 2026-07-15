document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const twoFaForm = document.getElementById("2fa-form");
    const otpInput = document.getElementById("otp");
    const username2faInput = document.getElementById("username-2fa");
    const password2faInput = document.getElementById("password-2fa");

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            showLoading();

            try {
                const loginBody = new URLSearchParams({
                    username: username,
                    password: password
                });
                console.log("Login Request Body:", loginBody.toString());

                const response = await fetch("/token", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    body: loginBody,
                });

                hideLoading();

                if (response.ok) {
                    const data = await response.json();
                    if (data.message === "2FA necessário") {
                        showToast("2FA necessário. Insira o código OTP.", "info");
                        document.getElementById("login-form").style.display = "none";
                        document.getElementById("otp-section").style.display = "block";
                        username2faInput.value = username;
                        password2faInput.value = password;
                        document.getElementById("otp").focus();
                    } else {
                        localStorage.setItem("access_token", data.access_token);
                        localStorage.setItem("token_type", data.token_type);
                        showToast("Login realizado com sucesso!", "success");
                        window.location.href = "/dashboard.html"; // Redirecionar para o dashboard
                    }
                } else {
                    const errorData = await response.json();
                    let msg = errorData.detail || "Erro ao fazer login.";
                    if (response.status === 401) msg = "Usuário ou senha inválidos.";
                    showToast(msg, "danger");
                }
            } catch (error) {
                hideLoading();
                console.error("Erro de rede:", error);
                showToast("Erro de conexão. Tente novamente.", "danger");
            }
        });
    }

    if (twoFaForm) {
        twoFaForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const username = username2faInput.value;
            const password = password2faInput.value;
            const otp = otpInput.value;

            showLoading();

            try {
                const twoFaBody = new URLSearchParams({
                    username: username,
                    password: password,
                    otp: otp
                });
                console.log("2FA Request Body:", twoFaBody.toString());

                const response = await fetch("/token/2fa", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    body: twoFaBody,
                });

                hideLoading();

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem("access_token", data.access_token);
                    localStorage.setItem("token_type", data.token_type);
                    showToast("Login 2FA realizado com sucesso!", "success");
                    window.location.href = "/dashboard.html";
                } else {
                    const errorData = await response.json();
                    let msg = errorData.detail || "Erro na verificação 2FA.";
                    if (response.status === 401) msg = "Código OTP inválido ou expirado.";
                    showToast(msg, "danger");
                }
            } catch (error) {
                hideLoading();
                console.error("Erro de rede durante 2FA:", error);
                showToast("Erro de conexão. Tente novamente.", "danger");
            }
        });
    }
});
