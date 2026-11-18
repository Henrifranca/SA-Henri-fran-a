
# Devolutiva formativa — Atividade 01 da SA

**Estudante:** Henri França  
**Turma:** Rio Negrinho — Tarde  
**Unidade Curricular:** Programação de Aplicativos  
**Projeto:** Sistema Hospitalar  
**Código analisado:** `codigo/app.py`  
**Referência:** Situação de Aprendizagem nº 1 — *Da Ideia ao Código*

## O que você já conseguiu desenvolver

Henri, parabéns pelo desenvolvimento do seu sistema hospitalar! Você apresentou uma aplicação com diferentes funcionalidades e uma estrutura que demonstra conhecimento de programação orientada a objetos, manipulação de dados e organização de regras de negócio.

Pontos positivos identificados:

- Criou classes específicas, como `Paciente`, `Medico`, `Exame`, `RegistroAjuda` e `SistemaHospitalar`, separando entidades e responsabilidades.
- Implementou cadastro e consulta de pacientes, médicos e exames.
- Desenvolveu mecanismos de busca, associação entre pacientes e médicos, estatísticas e uma fila de atendimento organizada por prioridade.
- Utilizou **JSON para salvar e recuperar informações**, permitindo que os dados permaneçam disponíveis após o encerramento do programa.
- Aplicou **listas, dicionários, funções, classes, laços de repetição e condicionais** de maneira consistente.
- Criou identificadores sequenciais para os registros.
- Utilizou tratamento de exceções em entradas numéricas e operações de leitura e gravação.
- Incluiu comentários que ajudam a compreender os blocos mais importantes.

## O que precisa ser corrigido

### 1. Preservar a integridade dos registros ao dar alta

O método `dar_alta()` remove o paciente da lista principal. Entretanto, podem existir exames vinculados ao objeto desse paciente.

Quando o sistema salva e carrega novamente os dados, os exames que não encontram o paciente correspondente deixam de ser reconstruídos pela rotina de carregamento.

**Como melhorar:** diferenciar a alta hospitalar da exclusão do cadastro. Considere manter o paciente no sistema com um atributo de situação, como `ativo`, `internado` ou `alta`, preservando o histórico de exames.

### 2. Validar os dados do cadastro

No método `cadastrar_paciente()`, nome, idade e sintoma são recebidos diretamente. A idade é armazenada como texto, sem validação numérica. Também é possível prosseguir com campos vazios.

**Como melhorar:** validar os campos obrigatórios, converter a idade para inteiro e verificar se está em uma faixa coerente. Faça o mesmo com o nome e a especialidade dos médicos e com as informações dos exames.

### 3. Corrigir a identificação da turma no README

O README identifica Henri como estudante do período da manhã, mas ele está relacionado à turma de **Rio Negrinho — tarde**.

**Como melhorar:** atualizar a identificação do estudante e incluir uma descrição das funcionalidades específicas do Sistema Hospitalar.

## Oportunidades de melhoria

### 4. Separar as responsabilidades da classe principal

A classe `SistemaHospitalar` concentra cadastros, regras, consultas, persistência, mensagens e apresentação dos menus.

**Como melhorar:** considerar módulos separados para entidades, armazenamento, regras de negócio e interação com o usuário. Essa divisão facilitará alterações e testes.

### 5. Proteger as informações cadastradas

O arquivo JSON contém informações de pacientes, exames e outros registros. Como o programa trabalha com dados de caráter sensível, é importante não utilizar informações reais em demonstrações ou publicar arquivos preenchidos no GitHub.

**Como melhorar:** utilizar dados inteiramente fictícios nos testes, manter os arquivos de dados fora do versionamento e planejar controles de acesso para futuras versões.

### 6. Delimitar as funcionalidades de orientação de saúde

O programa apresenta informações de referência para doenças e situações de saúde. Em uma aplicação real, esses conteúdos exigiriam validação por profissionais habilitados.

**Como melhorar:** identificar essas telas como **simulações educacionais** e evitar apresentar sugestões automáticas como diagnóstico ou prescrição individual.

### 7. Organizar testes específicos

O projeto apresenta validações, mas é importante demonstrar como as operações se comportam em diferentes situações.

**Testes recomendados:**

1. Cadastrar um paciente com dados válidos e inválidos.
2. Cadastrar um médico e vinculá-lo a um paciente.
3. Registrar um exame e verificar sua associação.
4. Salvar os dados, encerrar e reiniciar o sistema.
5. Dar alta a um paciente que possui exames e verificar se o histórico é preservado.
6. Conferir a ordenação da fila por prioridade.
7. Verificar as respostas a opções de menu inexistentes.

## Prioridades para a próxima versão

1. **Corrigir o tratamento da alta para preservar o histórico do paciente.**
2. **Validar idade, nomes e demais campos obrigatórios.**
3. **Revisar a documentação e a identificação da turma.**
4. **Separar gradualmente as responsabilidades da classe principal.**
5. **Documentar os testes e proteger os dados usados nas demonstrações.**

## Mensagem final

Henri, seu projeto demonstra iniciativa e conhecimento de conceitos importantes de programação. A utilização de classes, relacionamentos entre objetos, persistência em JSON e diferentes operações de gerenciamento é um avanço significativo.

Seu próximo desafio é garantir que essas funcionalidades continuem corretas mesmo quando os registros são alterados ou removidos. **Continue desenvolvendo o sistema com atenção à integridade dos dados, à validação e à organização do código.** Esses cuidados tornarão sua aplicação cada vez mais confiável e fácil de manter.
