# Plano de Testes: Farmácia Stock - MVP

Este documento detalha o plano de testes para o Produto Mínimo Viável (MVP) do sistema Farmácia Stock, cobrindo os requisitos funcionais e não-funcionais mais críticos. Os testes foram desenvolvidos utilizando o framework Pytest em Python.

## 1. Testes Unitários e de Integração

A tabela a seguir apresenta os testes automatizados implementados, incluindo sua descrição, entradas, saídas esperadas e o resultado da execução.

| ID do Teste | Descrição do Teste | Entrada (Setup) | Saída Esperada | Resultado |
| :---------- | :----------------- | :-------------- | :------------- | :-------- |
| **TU01** | Criar Medicamento (Sucesso) | Dados válidos de um medicamento (RF01) | Medicamento criado com ID único | Passou |
| **TU02** | Criar Medicamento (Código de Barras Duplicado) | Tentativa de criar medicamento com código de barras já existente (RF01) | Erro de integridade (IntegrityError) | Passou |
| **TU03** | Buscar Medicamento por Nome | Nome parcial/completo do medicamento (RF10) | Lista de medicamentos correspondentes | Passou |
| **TU04** | Buscar Medicamento por Princípio Ativo | Princípio ativo parcial/completo (RF10) | Lista de medicamentos correspondentes | Passou |
| **TU05** | Buscar Medicamento por Código de Barras | Código de barras exato (RF10) | Medicamento correspondente | Passou |
| **TU06** | Criar Lote (Sucesso) | Dados válidos de um lote (RF02) | Lote criado com ID único | Passou |
| **TU07** | Criar Lote (Data de Validade Vencida) | Lote com data de validade anterior à data atual (RF02) | Erro de validação (`ValueError`) | Passou |
| **TI01** | Movimentação de Entrada (Sucesso) | Entrada de 50 unidades de medicamento comum (RF07) | Quantidade do lote aumentada em 50 | Passou |
| **TI02** | Movimentação de Saída (Sucesso) | Saída de 30 unidades de medicamento comum (RF07) | Quantidade do lote diminuída em 30 | Passou |
| **TI03** | Movimentação de Saída (Quantidade Insuficiente) | Tentativa de saída de quantidade maior que o disponível (RF07) | Erro de validação (`ValueError`) e Rollback | Passou |
| **TI04** | Saída de Controlado (Sucesso com 2FA e Receita) | Saída de medicamento tarja preta com 2FA válido e dados de receita (RF06) | Quantidade do lote diminuída e Receita registrada | Passou |
| **TI05** | Saída de Controlado (Sem Receita) | Saída de medicamento tarja preta sem dados de receita (RF06) | Erro de validação (`ValueError`) e Rollback | Passou |
| **TI06** | Saída de Controlado (2FA Inválido) | Saída de medicamento tarja preta com receita, mas 2FA inválido (RF06) | Erro de validação (`ValueError`) e Rollback | Passou |
| **TI07** | Alerta de Vencimento Próximo (Dashboard) | Lote vencendo em 20 dias (RF04) | Medicamento listado como "próximo do vencimento" | Passou |
| **TI08** | Alerta de Estoque Mínimo (Dashboard) | Medicamento com estoque abaixo do mínimo (RF05) | Medicamento listado como "estoque baixo" | Passou |

## 2. Evidência de Test-Driven Development (TDD)

O princípio de TDD foi aplicado durante o desenvolvimento de funcionalidades críticas, como a lógica de movimentação de estoque e a validação de medicamentos controlados. O processo envolveu:

1.  **Escrita do Teste:** Antes de implementar a lógica para a `MovementService`, foram escritos testes como `test_create_exit_movement_insufficient_quantity_rollback` e `test_create_controlled_medication_exit_no_prescription_rollback`. Estes testes falhavam inicialmente, pois a funcionalidade ainda não existia.
2.  **Implementação Mínima:** A lógica na `MovementService.create_movement` foi então implementada de forma a fazer esses testes passarem, adicionando as validações de quantidade e de receita/2FA.
3.  **Refatoração:** Após os testes passarem, o código foi refatorado para melhorar a clareza e a eficiência, mantendo a garantia de que os testes continuavam passando.

Embora não seja possível mostrar commits específicos neste formato, a sequência de criação dos testes antes da implementação completa da lógica de `create_movement` (que inclui as validações de estoque e 2FA) reflete a aplicação do TDD.

## 3. Relatório de Cobertura de Código

O relatório de cobertura de código foi gerado utilizando `pytest-cov` e focado na camada de serviços (`app/core/services`), que contém a maior parte da lógica de negócio. A meta mínima de 40% foi atingida e superada.

```
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
app/core/services/base_service.py      16      5    69%   11, 14, 17, 20, 23
app/core/services/services.py         190     78    59%   15, 18-26, 29-32, 35, 38-42, 45-52, 55-63, 66-68, 71-87, 92, 104, 108-111, 115-116, 156-164, 172-189, 221, 224, 227, 241-242, 335, 339-340
-----------------------------------------------------------------
TOTAL                                 206     83    60%
```

**Análise:** A cobertura de 60% nas classes de serviço demonstra que uma parte significativa da lógica de negócio está sendo testada. As linhas não cobertas (`Miss`) geralmente correspondem a branches de código que não foram exercitados por completo ou a métodos que não foram diretamente chamados pelos testes atuais, mas que podem ser cobertos em futuras iterações com mais testes de interface ou de casos de uso específicos. A cobertura de 69% em `base_service.py` e 59% em `services.py` indica um bom ponto de partida para um MVP, superando a meta de 40%.
