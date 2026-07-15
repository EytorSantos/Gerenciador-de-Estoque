# Guia de Contribuição

Bem-vindo(a) ao guia de contribuição do Sistema de Gestão de Estoque para Farmácias! Agradecemos o seu interesse em melhorar este projeto.

Para garantir um processo de colaboração eficiente e de alta qualidade, por favor, siga as diretrizes abaixo:

## Como Contribuir

1.  **Fork o Repositório:** Comece fazendo um fork do repositório principal para a sua conta GitHub.
2.  **Clone o Repositório:** Clone o seu fork para a sua máquina local:
    ```bash
    git clone https://github.com/seu-usuario/nome-do-repositorio.git
    cd nome-do-repositorio
    ```
3.  **Crie uma Nova Branch:** Crie uma branch para a sua feature ou correção de bug. Use nomes descritivos, como `feature/nova-funcionalidade` ou `bugfix/correcao-de-login`.
    ```bash
    git checkout -b feature/nome-da-feature
    ```
4.  **Desenvolva:** Implemente suas mudanças, seguindo as diretrizes de código e arquitetura do projeto.
5.  **Testes:** Certifique-se de que todos os testes existentes continuam passando e adicione novos testes para cobrir suas mudanças. Execute os testes com `pytest`.
6.  **Commits:** Faça commits claros e concisos, descrevendo o que foi alterado e por quê. Use a convenção de commits, se houver.
7.  **Atualize a Documentação:** Se suas mudanças afetarem a funcionalidade ou a forma de uso, atualize a documentação relevante (README.md, CHANGELOG.md, etc.).
8.  **Push para o seu Fork:** Envie suas mudanças para o seu fork no GitHub.
    ```bash
    git push origin feature/nome-da-feature
    ```
9.  **Abra um Pull Request (PR):** Abra um Pull Request do seu fork para a branch `main` do repositório original. Descreva detalhadamente as suas mudanças, os problemas que resolve e como foi testado.

## Boas Práticas de Código

*   **Qualidade do Código:** Mantenha o código limpo, legível e bem organizado.
*   **Tipagem:** Utilize tipagem completa em Python para garantir a robustez do código.
*   **Docstrings:** Adicione docstrings para funções, classes e métodos, explicando seu propósito, parâmetros e retornos.
*   **Comentários:** Use comentários apenas quando o código não for autoexplicativo.
*   **Nomenclatura:** Utilize nomes de variáveis, funções e classes em inglês, seguindo padrões claros e consistentes.
*   **PEP8:** Siga as diretrizes de estilo do PEP8 para o código Python.
*   **Testes:** Escreva testes unitários e de integração para garantir a funcionalidade e prevenir regressões.

## Estrutura do Projeto

Familiarize-se com a estrutura de diretórios e a Clean Architecture adotada no projeto para garantir que suas contribuições se encaixem no design existente.

## Dúvidas?

Se tiver alguma dúvida ou precisar de ajuda, não hesite em abrir uma issue no repositório.
