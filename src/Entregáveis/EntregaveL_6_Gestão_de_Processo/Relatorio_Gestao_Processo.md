# Relatório de Gestão do Processo - Projeto Integrador Farmácia Stock

## 1. Metodologia Adotada (Justificativa)

Para o desenvolvimento do sistema de gestão de estoque da farmácia, a equipe adotou uma abordagem híbrida, combinando os princípios do **Kanban** com práticas do **Extreme Programming (XP)**. A escolha do Kanban foi motivada pela necessidade de manter uma **visibilidade contínua do fluxo de trabalho**, essencial para uma equipe de cinco desenvolvedores. O controle rigoroso do **WIP (Work In Progress)** permitiu que a equipe focasse na conclusão de tarefas antes de iniciar novas, otimizando a entrega e evitando gargalos. A flexibilidade inerente ao Kanban foi crucial para absorver as mudanças e refinamentos nos requisitos do sistema de estoque e na implementação de funcionalidades de segurança, como a autenticação de dois fatores (2FA), sem a rigidez de ciclos de sprint fixos.

Complementarmente, as práticas de XP, como **Code Review** e **Integração Contínua**, foram incorporadas para garantir a qualidade do código e a colaboração efetiva. O Code Review promoveu o compartilhamento de conhecimento e a detecção precoce de defeitos, enquanto a integração contínua, facilitada pelo uso de **Docker**, assegurou que o sistema estivesse sempre em um estado funcional e testável, mitigando problemas de compatibilidade e ambiente ("funciona na minha máquina"). Essa combinação permitiu à equipe responder rapidamente às demandas, manter a qualidade do software e gerenciar eficientemente o projeto.

## 2. Product Backlog (User Stories Priorizadas)

Com base na engenharia reversa do código-fonte e artefatos do projeto, o Product Backlog foi construído com as seguintes User Stories, priorizadas e categorizadas por status:

| Prioridade | User Story | Status |
|---|---|---|
| 1 | Como **usuário**, eu quero **me autenticar no sistema com usuário e senha** para que eu possa acessar as funcionalidades restritas. | Feito |
| 2 | Como **farmacêutico**, eu quero **habilitar a autenticação de dois fatores (2FA)** para que minhas operações críticas sejam mais seguras. | Feito |
| 3 | Como **farmacêutico**, eu quero **registrar uma saída de medicamento controlado com 2FA e receita** para que a conformidade regulatória seja garantida. | Feito |
| 4 | Como **gerente de estoque**, eu quero **adicionar um novo medicamento ao catálogo** para que ele possa ser gerenciado no sistema. | Feito |
| 5 | Como **gerente de estoque**, eu quero **registrar a entrada de um lote de medicamentos** para que o estoque seja atualizado. | Feito |
| 6 | Como **gerente de estoque**, eu quero **visualizar o histórico de movimentações de estoque** para auditar as operações. | Em Progresso |
| 7 | Como **usuário**, eu quero **visualizar meu perfil e minhas informações** para que eu possa gerenciá-las. | Em Progresso |
| 8 | Como **gerente de estoque**, eu quero **pesquisar medicamentos por nome, princípio ativo ou código de barras** para encontrar rapidamente um item. | A Fazer |
| 9 | Como **gerente de estoque**, eu quero **visualizar medicamentos com estoque baixo** para que eu possa planejar novas compras. | A Fazer |
| 10 | Como **gerente de estoque**, eu quero **visualizar medicamentos próximos do vencimento** para que eu possa tomar ações preventivas. | A Fazer |
| 11 | Como **usuário**, eu quero **atualizar minhas informações de perfil** para manter meus dados corretos. | A Fazer |
| 12 | Como **gerente de estoque**, eu quero **editar os detalhes de um medicamento existente** para corrigir informações. | A Fazer |

## 3. Evidência de Processo e Fluxo (Quadro Kanban Visual)

A seguir, uma representação visual do quadro Kanban do projeto, refletindo o estado atual das User Stories e a alocação da equipe:

| Backlog | Ready for Dev | In Progress (WIP) | Code Review | Done |
|---|---|---|---|---|
| US 8: Pesquisar medicamentos | US 9: Visualizar estoque baixo | US 6: Visualizar histórico de movimentações (Gabriel) | US 7: Visualizar perfil (Maria) | US 1: Autenticação de usuário |
| US 10: Visualizar vencimentos | US 11: Atualizar perfil | | | US 2: Habilitar 2FA |
| US 12: Editar medicamento | | | | US 3: Saída de controlado com 2FA |
| | | | | US 4: Adicionar medicamento |
| | | | | US 5: Registrar entrada de lote |

### Ata de Uma Reunião de Sprint Review 

**Data:** 10 de Julho de 2026
**Horário:** 14:00 - 15:00
**Local:** Sala de Reuniões Virtual (meet)
**Participantes:** Eytor Santos Assunção, Cristovam Augusto dos Santos Barreiros, Diule Monteiro Pereira Junior, Maria Yasmin Oliveira de Souza , Gabriel de Jesus Santiago Cardoso   
**Pauta:** Validação das entregas de autenticação e movimentação de estoque.

**Discussões e Decisões:**

1.  **Autenticação de Usuário (US 1):** A funcionalidade de login com usuário e senha foi demonstrada e validada. Os testes de integração confirmaram o funcionamento esperado.
2.  **Habilitação de 2FA (US 2):** A configuração e habilitação da autenticação de dois fatores para usuários foi apresentada. A geração do segredo TOTP e a verificação do OTP foram testadas com sucesso. A equipe confirmou a robustez da implementação.
3.  **Saída de Medicamento Controlado com 2FA e Receita (US 3):** A funcionalidade crítica de saída de medicamentos controlados, exigindo 2FA do farmacêutico e dados de receita, foi demonstrada. A validação de permissões e a integração com o módulo 2FA foram verificadas. Pequenos ajustes na mensagem de erro para OTP inválido foram sugeridos e aceitos pela equipe para serem implementados em breve.
4.  **Adição de Medicamento (US 4):** A funcionalidade de cadastro de novos medicamentos foi validada, incluindo campos essenciais e validações básicas.
5.  **Registro de Entrada de Lote (US 5):** A entrada de novos lotes de medicamentos, com validação de data de vencimento, foi demonstrada e aprovada.

**Próximos Passos:** A equipe continuará o desenvolvimento das funcionalidades de visualização de histórico de movimentações e perfil do usuário, com foco na conclusão dessas histórias para a próxima revisão. O backlog será refinado com base no feedback recebido.

**Status Geral:** As entregas de segurança e as funcionalidades básicas de estoque estão em um bom caminho, com a equipe demonstrando capacidade de entregar valor de forma incremental.

## 4. Lições Aprendidas (Retrospectiva)

O projeto Farmácia Stock, desde sua concepção até a implementação atual, proporcionou uma rica experiência de aprendizado para a equipe. **O que deu certo** foi a clara separação de responsabilidades nas camadas (controllers, services, repositories), o que facilitou a manutenção, a testabilidade e a escalabilidade do sistema. O uso de **Docker** para conteinerização foi um ponto forte, eliminando o clássico problema de "na minha máquina funciona", garantindo um ambiente de desenvolvimento e execução consistente. A implementação da segurança com JWT para autenticação e 2FA para autorização de operações críticas demonstrou um alto nível de preocupação com a integridade do sistema.

No entanto, enfrentamos **dificuldades** que serviram como importantes aprendizados. A curva de aprendizado inicial com o mapeamento objeto-relacional do SQLAlchemy, especialmente em relacionamentos mais complexos, exigiu um esforço adicional da equipe. A configuração de testes unitários, embora presente, poderia ter sido mais abrangente desde o início, cobrindo um maior percentual do código.

Para **o que faríamos diferente** em projetos futuros, a principal melhoria seria a adoção de um pipeline de CI/CD automatizado desde o Sprint 1. Isso teria agilizado a detecção de problemas de integração e a entrega contínua. Além disso, aumentar a granularidade das User Stories, dividindo tarefas maiores em subtarefas menores, poderia ter evitado que alguns cards ficassem parados por muito tempo na coluna 'In Progress', melhorando o fluxo e a visibilidade do Kanban. Aumentar a frequência de sessões de pair programming também seria benéfico para mitigar a curva de aprendizado e os conflitos de merge.
