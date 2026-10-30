# Uso de ferramentas de IA

Este arquivo registra o apoio de IA ao projeto, conforme a especificação da disciplina. O grupo deve complementar o registro sempre que usar outras ferramentas ou prompts.

| Ferramenta | Pedido principal | Aproveitado / adaptado / descartado | Verificação humana |
| --- | --- | --- | --- |
| Codex (OpenAI), 30/10/2026 | “Estudo da tecnologia e design da POC; primeira comunicação entre dois processos. Entrega 1: roteiro preliminar da POC, divisão de tarefas e repositório GitHub criado. Sou o grupo 2.” | Gerou a proposta inicial de arquitetura SOAP, divisão de tarefas, README e protótipo de servidor/cliente. A divisão é proposta e deve ser confirmada pelo grupo. | Conferir contrato WSDL, executar a comunicação, revisar requisitos com a especificação e validar conclusões na documentação oficial. |

## Registro crítico inicial

- A IA sugeriu trabalhar com centavos inteiros em vez de ponto flutuante para os lances; a escolha foi adotada para manter comparações determinísticas.
- A formulação “notificação” pode sugerir push. Para o grupo SOAP, a especificação pede consulta periódica. O README descreve polling e não atribui push ao protótipo.
- **Caso de erro da IA para o slide obrigatório:** ainda não foi observado um erro concreto. Registrar aqui um caso real durante o desenvolvimento, com a sugestão incorreta, a evidência usada para detectá-la e a correção feita. Não inventar um exemplo.

## Fontes de conferência

- WSDL 1.1: https://www.w3.org/TR/wsdl.html
- SOAP 1.1: https://www.w3.org/TR/2000/NOTE-SOAP-20000508/
- Spyne: https://spyne.io/docs/
- Zeep: https://docs.python-zeep.org/en/master/client.html
