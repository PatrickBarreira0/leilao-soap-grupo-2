# Uso de ferramentas de IA

Este arquivo registra o apoio de IA ao projeto, conforme a especificação da disciplina. O grupo deve complementar o registro sempre que usar outras ferramentas ou prompts. A coluna de pedidos apresenta **paráfrases consolidadas dos objetivos**, revisadas para facilitar a leitura; não são transcrições literais das mensagens enviadas.

| Ferramenta | Objetivo do pedido (paráfrase) | Aproveitado / adaptado / descartado | Verificação humana |
| --- | --- | --- | --- |
| Codex (OpenAI), 30/10/2026 | Analisar a especificação do projeto para o grupo 2, responsável por SOA/SOAP, e propor uma arquitetura simples para o leilão distribuído. Preparar o roteiro preliminar da POC, distribuir as frentes de trabalho entre os integrantes, criar o repositório GitHub e implementar uma primeira troca de lance entre Leiloeiro e Participante em processos distintos. | Gerou a proposta inicial de arquitetura SOAP, divisão de tarefas, README e protótipo de servidor/cliente. A divisão é proposta e deve ser confirmada pelo grupo. | Conferir contrato WSDL, executar a comunicação, revisar requisitos com a especificação e validar conclusões na documentação oficial. |
| Codex (OpenAI), 06/11/2026 | Dar continuidade ao protótipo de SOAP para cobrir os requisitos da POC: consulta periódica das atualizações, decisão sobre lances, encerramento do leilão e observação de falha e concorrência. Atualizar o README com instruções e resultados verificados, preparar os slides para o seminário e publicar a Entrega 2 no mesmo repositório. | Acrescentou polling, anúncio do vencedor, tratamento da indisponibilidade, testes de integração, README e slides. | Três experimentos locais foram executados. O teste entre duas máquinas ainda depende dos notebooks do grupo. |

## Registro crítico inicial

- A IA sugeriu trabalhar com centavos inteiros em vez de ponto flutuante para os lances; a escolha foi adotada para manter comparações determinísticas.
- A formulação “notificação” pode sugerir push. Para o grupo SOAP, a especificação pede consulta periódica. O README descreve polling e não atribui push ao protótipo.
- **Sugestão inadequada identificada:** o primeiro protótipo gerado pela IA em 30/10 tinha `darLance` e `consultarLeilao`, mas o cliente apenas fazia chamadas pontuais. Isso não atendia RF4 (todos saberem de cada novo maior lance) nem RF5 (anunciar o vencedor). A comparação do código com esses requisitos revelou a lacuna; em 06/11 foi criado o modo de consulta periódica que imprime as mudanças e o encerramento. O teste com dois observadores confirmou o resultado.
- Os resultados de falha e concorrência apresentados no README e nos slides vieram de execução local; não representam ainda a execução em duas máquinas exigida em RE1.

## Fontes de conferência

- WSDL 1.1: https://www.w3.org/TR/wsdl.html
- SOAP 1.1: https://www.w3.org/TR/2000/NOTE-SOAP-20000508/
- Spyne: https://spyne.io/docs/
- Zeep: https://docs.python-zeep.org/en/master/client.html
- Exemplo empresarial verificado, Salesforce SOAP API: https://developer.salesforce.com/docs/platform/api/guide/sforce-api-partner.html
