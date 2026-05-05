---
description: >
  Turns a raw problem or idea into a well-structured user story with acceptance criteria.
when_to_use: >
  Use whenever the user describes a problem, feature request, or task they want to implement
  and needs to turn it into a user story. Triggers on "quero implementar", "preciso de uma
  história de usuário", "monta uma story para", "tenho um problema que", or any raw idea that
  needs formalization before development begins. Always use before writing acceptance criteria,
  defining scope, or initiating a development session.
allowed-tools: Read Write Edit
---
 
# User Story Builder
 
Transforma um problema ou ideia bruta em uma user story bem definida, com critérios de aceitação claros,
garantindo alinhamento completo entre o agente e o usuário antes de qualquer trabalho de desenvolvimento.
 
---
 
## Protocolo
 
### Fase 1 — Entendimento do problema
 
Ao receber um problema ou ideia, **não** escreva a story imediatamente.
 
Primeiro, faça perguntas cirúrgicas para eliminar ambiguidade. O objetivo é chegar em:
 
1. **Quem** é o usuário real que se beneficia (papel/persona, não "o sistema")
2. **O que** precisa ser feito — a ação concreta, não o mecanismo técnico
3. **Por que** — o valor de negócio ou técnico que justifica o esforço
4. **Quando está pronto** — o critério observável que indica conclusão
 
Regras para as perguntas:
- Máximo 3 perguntas por rodada
- Priorize as que desbloqueiam as outras
- Se o "para que" (o porquê) não estiver claro, essa é sempre a primeira pergunta
- Se o escopo parecer grande, pergunte sobre o menor slice que entrega valor
 
Exemplo de perguntas úteis:
- "Qual é o resultado observável quando isso estiver funcionando?"
- "Quem sofre hoje sem essa funcionalidade?"
- "Existe uma versão menor disso que já entregaria valor?"
- "O que está fora do escopo dessa story?"
 
Continue perguntando até ter clareza suficiente para escrever uma story que passe no critério INVEST
(Independent, Negotiable, Valuable, Estimatable, Small, Testable).
 
---
 
### Fase 2 — Draft da story
 
Com as respostas em mãos, escreva a story no template:
 
```
Como [tipo de usuário],
quero [ação concreta e pequena],
para que [resultado de negócio ou técnico mensurável].
```
 
Seguido dos critérios de aceitação:
 
```
Critérios de aceitação:
- [ ] [condição observável 1]
- [ ] [condição observável 2]
- [ ] [condição observável 3]
```
 
Regras para os critérios:
- Cada critério deve ser verificável sem ambiguidade
- Sem critérios de implementação (como, não o quê)
- Incluir explicitamente o que está **fora** do escopo se houver risco de expansão
- Máximo de 5 critérios. Se precisar de mais, a story está grande demais — proponha split.
 
---
 
### Fase 3 — Alinhamento
 
Após apresentar o draft, pergunte explicitamente:
 
> "Essa story captura o que você quer? Algum critério está errado, faltando ou além do escopo?"
 
Itere até o usuário confirmar que está alinhado. Só então a story está pronta.
 
---
 
### Fase 4 — Saída final
 
Apresente a story confirmada em bloco formatado:
 
```
## História: [título curto]
 
Como [tipo de usuário],
quero [ação],
para que [valor].
 
### Critérios de aceitação
- [ ] ...
- [ ] ...
 
### Fora do escopo
- ...
```
 
---
 
## Heurísticas de qualidade
 
**A história está boa quando:**
- O "para que" expressa valor real, não consequência técnica óbvia
- Qualquer desenvolvedor lendo entende o que está pronto sem perguntar
- Pode ser desenvolvida e entregue em uma sessão ou iteração curta
- Os critérios de aceitação são testáveis manualmente ou com testes automatizados
 
**Sinais de que a história precisa de split:**
- O "quero" contém "e" ou "ou"
- Tem mais de 5 critérios de aceitação
- O usuário hesita ao dizer se cabe em uma iteração
- Há dependência implícita de outra história não escrita
 
**Sinais de que o "para que" está fraco:**
- É uma consequência técnica ("para que o código fique mais limpo")
- Repete o "quero" com outras palavras
- Não mudaria nada se fosse removido
