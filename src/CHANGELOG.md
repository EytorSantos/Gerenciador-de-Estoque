# Histórico de Mudanças

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [0.1.0] - 2026-07-14

### Adicionado

*   Estrutura inicial do projeto com Clean Architecture.
*   Configuração de ambiente com Docker e Docker Compose.
*   Backend com FastAPI, SQLAlchemy e PostgreSQL.
*   Frontend com HTML5, CSS3 puro e JavaScript Vanilla.
*   Implementação dos requisitos funcionais RF01, RF02, RF06, RF07, RF10 (MVP).
*   Implementação dos requisitos não-funcionais RNF01, RNF02, RNF04.
*   Autenticação JWT e 2FA simulada.
*   Modelagem inicial do banco de dados.
*   Testes automatizados com Pytest.
*   Documentação inicial (README, LICENSE, CONTRIBUTING).

## [0.2.0] - 2026-07-14

### Melhorado

*   **Tratamento de Erros no Frontend:** Refinado o tratamento de erros em todos os arquivos JavaScript (`profile.js`, `new-medication.js`, `quick-search.js`, `dashboard.js`, `edit-medication.js`, `medications.js`, `movements.js`) para exibir mensagens detalhadas da API, facilitando a depuração e melhorando a UX.
*   **Feedback Visual de Validação:** Adicionado suporte visual para estados `:invalid` nos formulários via CSS (`forms.css`), fornecendo feedback imediato ao usuário antes do envio.
*   **Documentação da API (Swagger):** 
    *   Enriquecidos os modelos Pydantic (`schemas.py`) com descrições detalhadas para cada campo.
    *   Adicionadas docstrings informativas a todas as rotas nos controladores (`user_controller.py`, `medication_controller.py`, `batch_controller.py`, `movement_controller.py`, `prescription_controller.py`, `quick_search_controller.py`, `dashboard_controller.py`).
    *   Atualizada a rota de Consulta Rápida para retornar `QuickSearchResponse`, incluindo informações de estoque e lotes.
*   **Estabilidade do Ambiente:** Configurado o arquivo `.env` padrão e inicializado o banco de dados para testes imediatos.
