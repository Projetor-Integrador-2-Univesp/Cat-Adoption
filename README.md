# pet-adoption

Este projeto foi desenvolvido como parte de uma iniciativa acadêmica com o objetivo de apoiar organizações e protetores independentes que atuam no resgate, cuidado e adoção de animais em situação de vulnerabilidade.

A solução foi idealizada a partir de uma visita técnica e entrevista realizada com a responsável pelo Lar Bastet, um projeto familiar localizado na região de Jundiaí/SP, que desde 2018 acolhe, trata e encaminha gatos para adoção.

Durante a entrevista, foram identificadas demandas relacionadas à:

- falta de um sistema estruturado para registro e controle dos animais atendidos;

- dificuldade de localizar informações armazenadas apenas no celular (fotos e conversas de WhatsApp);

- necessidade de otimizar o tempo gasto com comunicações e gestão de processos;

- ausência de um canal formal para divulgação de animais disponíveis e recebimento de doações.

Com base nessas necessidades, foi desenvolvido um modelo de banco de dados relacional que serve como base para uma futura aplicação web/mobile, permitindo à equipe do Lar Bastet gerenciar de forma mais eficiente todo o fluxo de trabalho.

🗄️ Estrutura do Banco de Dados
O banco de dados foi projetado para armazenar informações sobre:

- animais acolhidos;

- pessoas envolvidas (adotantes, responsáveis);

- adoções realizadas;

- usuários do sistema (colaboradores que acessam a plataforma).

📌 Principais Entidades

*adotante*
Armazena os dados dos responsáveis que adotam os animais.

- cpf (chave primária)

- nome, email, telefone, endereço

*usuario_sistema*
Registra os colaboradores que têm acesso ao sistema (atualmente Katiana e Brigid).

- id_usuario (chave primária)

- nome, email, telefone, senha

*pet*
Cadastro completo dos animais atendidos pelo projeto.

- id_pet (chave primária)

- data_entrada, idade, sexo, cor, descrição, status

- fk_usuario_sistema_id_usuario (quem registrou o animal)

*adocao*
Registro do processo de adoção, com vínculo entre o animal e o adotante.

- id_adocao (chave primária)

- data_adocao, obs, termo_compromisso

- relacionamentos com pet, adotante e usuario_sistema

🔗 Relacionamentos e Integridade
As chaves estrangeiras garantem a consistência dos dados:

- pet → usuario_sistema: cada animal é vinculado ao usuário que o cadastrou.

- adocao → pet: uma adoção pertence a um único animal (exclusividade no momento da adoção).

- adocao → adotante: uma adoção está associada a um único adotante.

- adocao → usuario_sistema: registro de quem concluiu o processo de adoção.

Regras de integridade:

ON DELETE RESTRICT: impede a exclusão de registros que estejam referenciados (ex: um adotante não pode ser removido se tiver uma adoção ativa).

ON DELETE CASCADE: na tabela adocao, se um animal for excluído, suas adoções também são removidas (adequado para casos de testes ou exclusão controlada).



🛠️ Tecnologias Utilizadas
MySQL — Sistema de gerenciamento de banco de dados relacional

Modelagem — Diagrama Entidade-Relacionamento (conceitual, lógico e físico)

Ferramentas de apoio — brModelo 3.3.3, MySQL Workbench

Módulo: Cadastro e Gerenciamento de Gatos (Backend)
Desenvolvido como parte fundamental do sistema para automatizar a entrada de novos animais para adoção, substituindo processos manuais.

### Funcionalidades:
- **Cadastro de Felinos:** Registro estruturado com nome, idade e características.
- **Banco de Dados Relacional:** Implementação em SQLite para persistência dos dados de adoção.
- **Painel Administrativo:** Interface Django para gerenciamento rápido pela equipe da clínica.