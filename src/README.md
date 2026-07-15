# Farmácia Stock: Sistema de Gestão de Estoque e Vendas de Medicamentos

## Visão Geral do Projeto

O **Farmácia Stock** é um sistema de gestão de estoque e vendas de medicamentos desenvolvido como parte do Projeto Integrador da disciplina de **Engenharia de Software I**. Este projeto visa aplicar e demonstrar o domínio de todo o *processo de engenharia de software*, desde a elicitação de requisitos até a implementação, testes e documentação, focando na criação de uma solução robusta e funcional para o controle de inventário em farmácias.

Nosso objetivo não é apenas entregar um sistema, mas evidenciar a **compreensão e aplicação das melhores práticas** em cada etapa do ciclo de vida do desenvolvimento de software, com especial atenção à gestão de lotes, datas de validade e medicamentos controlados.

### MVP (Produto Mínimo Viável)

O MVP do Farmácia Stock concentra-se nas funcionalidades essenciais para um controle de estoque eficiente e seguro:

*   **Gestão de Medicamentos:** Cadastro, consulta e atualização de informações detalhadas de medicamentos (EAN, princípio ativo, dosagem, fabricante, tarja, estoque mínimo).
*   **Gestão de Lotes:** Registro de lotes com controle rigoroso de datas de validade e quantidades, incluindo bloqueio de lotes vencidos ou com validade retroativa.
*   **Movimentação de Estoque (Kardex):** Registro atômico de entradas e saídas, garantindo a integridade dos dados com rollback em caso de falha. Inclui rastreabilidade por usuário, data, hora, operação e motivo.
*   **Controle de Medicamentos Controlados (SNGPC):** Implementação de validação de receita médica e autenticação de dois fatores (2FA) para farmacêuticos em operações de saída de medicamentos de tarja preta ou vermelha.
*   **Dashboard de Alertas:** Visão consolidada com alertas proativos sobre medicamentos próximos do vencimento e itens com estoque abaixo do mínimo.
*   **Pesquisa Unificada:** Funcionalidade de busca eficiente por nome, princípio ativo ou código de barras para acesso rápido à informação.

## Funcionalidades Principais

*   **Gestão de Medicamentos:** Cadastro, edição e exclusão de medicamentos com detalhes como código de barras, princípio ativo, dosagem, fabricante, tarja e estoque mínimo.
*   **Gestão de Lotes:** Controle de lotes de medicamentos, incluindo data de validade e quantidade.
*   **Movimentações de Estoque:** Registro de entradas e saídas de medicamentos, com histórico detalhado e transações atômicas.
*   **Controle de Medicamentos Controlados:** Implementação de autenticação de dois fatores (2FA) e exigência de receita médica para a saída de medicamentos de tarja preta ou vermelha.
*   **Dashboard:** Visão geral com estatísticas de estoque, medicamentos com baixo estoque e próximos do vencimento.
*   **Consulta Rápida:** Funcionalidade de busca eficiente para localizar medicamentos por nome ou código de barras.
*   **Autenticação Segura:** Sistema de login com JWT (JSON Web Tokens) e suporte a 2FA.

## Arquitetura do Sistema

O projeto segue uma arquitetura baseada em **Camadas (Layered Architecture)**, o que facilita a manutenção, escalabilidade e testes.

| Camada | Responsabilidade |
| :--- | :--- |
| **Frontend (Templates & Static)** | Interface do usuário (HTML/CSS) e lógica de interação no cliente (JavaScript). |
| **Controllers (API Routes)** | Gerencia as requisições HTTP, valida entradas básicas e coordena a resposta. |
| **Services (Business Logic)** | Onde reside a inteligência do negócio (ex: cálculo de estoque, validação de 2FA para controlados). |
| **Repositories (Data Access)** | Abstração da comunicação com o banco de dados (SQLAlchemy). |
| **Models (Database Schema)** | Definição das tabelas e relacionamentos do banco de dados. |
| **Schemas (Pydantic)** | Modelos de dados para validação e serialização da API. |

### Fluxo de Funcionamento

#### Autenticação e Segurança
O sistema utiliza **JWT (JSON Web Tokens)** para autenticação. O usuário faz login e recebe um token, que deve ser enviado no cabeçalho `Authorization: Bearer <token>` em todas as requisições protegidas. Para medicamentos controlados (tarja preta/vermelha), o sistema exige um código **OTP (One-Time Password)** gerado por aplicativos como Google Authenticator.

#### Gestão de Medicamentos e Lotes
Um **Medicamento** pode ter múltiplos **Lotes**. O estoque total de um medicamento é a soma das quantidades de todos os seus lotes ativos. Alertas de **Estoque Baixo** são gerados quando a soma total é inferior ao estoque mínimo definido no cadastro.

#### Movimentações de Estoque
Toda entrada ou saída é registrada como uma **Movimentação**. O sistema garante que, se ocorrer um erro ao salvar a receita médica, a alteração no estoque seja revertida (Rollback), assegurando **Transações Atômicas**.

## Entregáveis do Projeto Integrador

Este projeto foi estruturado em entregáveis que correspondem aos módulos da disciplina, demonstrando a aplicação prática dos conhecimentos adquiridos. Todos os documentos e o código-fonte estão organizados para facilitar a avaliação.

*   **Entregável 01 · Módulo 3: Documento de Requisitos**
    *   **Descrição:** Documento detalhado contendo a elicitação e especificação completa dos requisitos do sistema, incluindo requisitos funcionais (RFs), não-funcionais (RNFs) categorizados por FURPS+, User Stories e glossário. Foca em demonstrar a capacidade de **descobrir e documentar** o que o sistema precisa fazer.
    *   **Arquivo:** `Entregavel_1_Requisitos.pdf` (fornecido pelo usuário)

*   **Entregável 02 · Módulo 4: Modelagem UML**
    *   **Descrição:** Conjunto de diagramas UML que modelam o sistema, garantindo **consistência** entre Casos de Uso, Classes, Sequência e Atividades. Evidencia a habilidade de **representar a estrutura e o comportamento** do sistema de forma visual e padronizada.
    *   **Arquivo:** (Não gerado por este agente, mas esperado no projeto)

*   **Entregável 03 · Módulo 5: Arquitetura do Sistema**
    *   **Descrição:** Detalhamento da arquitetura em camadas do sistema, explicando a separação de responsabilidades entre Frontend, Backend (API), Lógica de Negócio (Services) e Acesso a Dados (Repositories). Aborda a escolha das tecnologias e como elas se integram para formar uma solução coesa.
    *   **Arquivo:** `DOCUMENTACAO.md`

*   **Entregável 04 · Módulo 6: Implementação e Código**
    *   **Descrição:** O código-fonte completo do sistema, implementado em Python com FastAPI para o backend e HTML/CSS/JS para o frontend. A implementação segue as diretrizes de clean code, modularidade e segurança, refletindo a **construção prática** do sistema com base nos requisitos e modelagem.
    *   **Localização:** Diretório `app/`

*   **Entregável 05 · Módulo 6: Testes**
    *   **Descrição:** Evidência rigorosa de testes do sistema, incluindo um plano de testes detalhado, testes unitários e de integração automatizados (Pytest), demonstração de Test-Driven Development (TDD) e um relatório de cobertura de código. Garante a **qualidade e confiabilidade** do software.
    *   **Arquivo:** `PLANO_DE_TESTES.md`

*   **Entregável 06 · Módulo 7: Apresentação Oral**
    *   **Descrição:** Guia de apoio para a apresentação oral do projeto, destacando os pontos que os professores mais valorizam, como atomicidade de transações, separação de responsabilidades e testes automatizados. Prepara a equipe para **comunicar eficazmente** o trabalho desenvolvido.
    *   **Arquivo:** `GUIA_APRESENTACAO.md`

## Tecnologias Utilizadas

*   **Backend:** Python 3.12, FastAPI, SQLAlchemy, Pydantic
*   **Banco de Dados:** PostgreSQL (produção), SQLite (desenvolvimento/testes)
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
*   **Autenticação:** JWT (JSON Web Tokens), 2FA (Two-Factor Authentication com PyOTP)
*   **Testes:** Pytest, Pytest-Cov
*   **Containerização:** Docker, Docker Compose
*   **Servidor Web:** Uvicorn

## Estrutura do Projeto

```
farmacia_stock/
├── app/
│   ├── api/                  # Endpoints da API
│   ├── core/                 # Lógica de negócio principal
│   │   ├── controllers/      # Controladores da aplicação
│   │   ├── database/         # Configuração do banco de dados
│   │   ├── models/           # Modelos de dados (SQLAlchemy)
│   │   ├── repositories/     # Camada de acesso a dados
│   │   ├── schemas/          # Schemas de validação (Pydantic)
│   │   ├── security/         # Funções de segurança (JWT, 2FA)
│   │   ├── services/         # Lógica de negócio (services)
│   │   └── utils/            # Utilitários
│   ├── static/               # Arquivos estáticos (CSS, JS, Imagens)
│   ├── templates/            # Templates HTML
│   └── main.py               # Ponto de entrada da aplicação FastAPI
├── app/tests/                # Testes automatizados (unitários e de integração)
├── .env                      # Variáveis de ambiente
├── docker-compose.yml        # Configuração do Docker Compose
├── Dockerfile                # Dockerfile para a aplicação
├── init_db.py                # Script de inicialização do banco de dados
├── requirements.txt          # Dependências do Python
├── wait-for-db.py            # Script para aguardar o banco de dados
├── DOCUMENTACAO.md           # Documentação técnica detalhada
├── GUIA_APRESENTACAO.md      # Guia para apresentação ao professor
└── README.md                 # Este arquivo
```

## Como Executar o Projeto

### Pré-requisitos

Certifique-se de ter o [Docker](https://www.docker.com/get-started) e [Docker Compose](https://docs.docker.com/compose/install/) instalados em sua máquina.

### 1. Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd farmacia_stock
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto, baseado no `.env.example` (se houver) ou com as seguintes variáveis:

```env
# Para Docker (PostgreSQL):
DATABASE_URL=postgresql://postgres:postgres@db:5432/pharmacy_stock
DATABASE_NAME=pharmacy_stock
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres

SECRET_KEY_JWT="sua_chave_secreta_aqui" # Altere para uma chave segura
ALGORITHM_JWT="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Nota:** Para desenvolvimento local sem Docker, você pode usar SQLite. Altere a linha `DATABASE_URL` para:
`DATABASE_URL=sqlite:///./farmacia_stock.db`

### 3. Para construir as imagens e iniciar todos os serviços (aplicação e banco de dados PostgreSQL, se configurado):

```bash
docker-compose up --build -d
```

*   `--build`: Reconstrói as imagens (útil após alterações no código ou Dockerfile).
*   `-d`: Executa os serviços em segundo plano (detached mode).

### 4. Inicializar o Banco de Dados e Criar Usuário Admin

Após os serviços estarem rodando, execute o script de inicialização do banco de dados para criar as tabelas e um usuário administrador padrão:

```bash
docker-compose exec app python init_db.py
```

*   **Usuário Admin Padrão:** `admin_test`
*   **Senha Admin Padrão:** `admin123`

### 5. Acessar a Aplicação

O frontend estará disponível em `http://localhost:8000` (ou a porta configurada no `docker-compose.yml`).

## Testes Automatizados

O projeto utiliza o framework **Pytest** para garantir a qualidade do código.

### Como os testes funcionam?
Os testes são executados em um banco de dados **SQLite em memória** (`test.db`), garantindo que os testes sejam rápidos e não afetem os dados reais.

### O que é testado?
*   **Sucesso em Entradas/Saídas:** Verifica se o estoque aumenta/diminui corretamente.
*   **Validação de Saldo:** Tenta retirar mais do que existe no estoque e verifica se o sistema impede e reverte a operação.
*   **Medicamentos Controlados:**
    *   Testa se o sistema exige receita médica.
    *   Testa se o código 2FA é validado corretamente.
*   **Integridade de Dados:** Garante que um lote pertença de fato ao medicamento selecionado.

Para rodar a suíte de testes automatizados (unitários e de integração) dentro do contêiner da aplicação:

```bash
docker-compose exec app bash -c "PYTHONPATH=. pytest app/tests/"
```

Para gerar o relatório de cobertura de código (focado na camada de serviços):

```bash
docker-compose exec app bash -c "PYTHONPATH=. pytest --cov=app/core/services --cov-report=term-missing app/tests/"
```

## Guia para Apresentação Acadêmica

Ao explicar para o professor, foque nos seguintes diferenciais técnicos:

1.  **Segurança Avançada:** Implementação de 2FA (TOTP) para operações críticas.
2.  **Robustez de Dados:** Uso de transações atômicas para evitar inconsistências no estoque.
3.  **Clean Code:** Separação clara entre lógica de negócio (Services) e acesso a dados (Repositories).
4.  **UX/UI:** Dashboard dinâmico que consome uma API RESTful de forma assíncrona.

## Comandos Docker Úteis

*   **Verificar logs dos serviços:**
    ```bash
    docker-compose logs -f <nome_do_servico>
    # Ex: docker-compose logs -f app
    ```
*   **Parar os serviços:**
    ```bash
    docker-compose stop
    ```
*   **Parar e remover contêineres, redes e volumes (cuidado: remove dados do banco!):**
    ```bash
    docker-compose down -v
    ```
*   **Acessar o terminal do contêiner da aplicação:**
    ```bash
    docker-compose exec app bash
    ```

## Contribuição

Sinta-se à vontade para contribuir com o projeto. Para isso, siga os passos:

1.  Faça um fork do repositório.
2.  Crie uma nova branch (`git checkout -b feature/sua-feature`).
3.  Implemente suas mudanças e escreva testes.
4.  Faça commit das suas mudanças (`git commit -m 'feat: Adiciona nova funcionalidade X'`).
5.  Envie para o seu fork (`git push origin feature/sua-feature`).
6.  Abra um Pull Request.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
