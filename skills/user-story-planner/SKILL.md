---
description: >
  Breaks a ready user story into scoped development tasks with clear done criteria for agent
  execution.
when_to_use: >
  Use whenever a user story is ready and needs to be broken into development tasks. Triggers on
  "quebra essa história em tasks", "quais são as tasks dessa história", "define as tasks para",
  "como implementar essa história", or when a user story exists and the next step is defining
  what the agent should do and in what order. Always use before starting implementation.
allowed-tools: Read Write Edit
---
 
# Story Task Planner
 
Dado uma história de usuário, define as tasks de desenvolvimento necessárias para implementá-la.
Cada task delimita escopo, declara intenção e estabelece o critério de done — o mínimo para que
um agente execute com segurança e o humano possa revisar.
 
---
 
## Protocolo
 
### Fase 1 — Leitura da história
 
Antes de propor qualquer task, confirme que você tem:
 
- O "Como / quero / para que" da história
- Os critérios de aceitação
- O que está fora do escopo
 
Se algum desses estiver ausente, peça antes de continuar.
 
---
 
### Fase 2 — Decomposição
 
Quebre a história em tasks atômicas seguindo estas regras:
 
**O que é uma task:**
- Uma unidade de trabalho que pode ser executada de forma independente
- Tem um resultado verificável ao final
- Não carrega valor de negócio por si só — isso é da história
 
**Regras de decomposição:**
- Declare dependências explicitamente — a ordem importa
- Prefira tasks sem dependências primeiro (mais seguras de executar)
- Se uma task não tiver critério de done claro, ela está grande demais — quebre
- Máximo de 7 tasks por história. Se precisar de mais, a história precisa de split
 
**Sinal de que uma task está errada:**
- Ela entrega valor de negócio sozinha → é uma história, não uma task
- Ela não tem critério de done verificável → está vaga
- Ela depende de outra task que ainda não existe → declare a dependência ou reordene
 
---
 
### Fase 3 — Template por task
 
Para cada task, preencha:
 
```
### Task [N]: [título curto]
 
**Objetivo:** [uma frase — o que essa task faz]
 
**Depende de:** [task anterior / nenhuma]
 
**Escopo:**
- Inclui: [o que será tocado]
- Exclui: [o que NÃO deve ser tocado, mesmo que pareça relacionado]
 
**Pronto quando:**
- [ ] [condição verificável 1]
- [ ] [condição verificável 2]
```
 
Regras do template:
- "Exclui" é obrigatório — ao menos uma linha
- "Pronto quando" deve ser verificável sem ambiguidade
- Máximo de 3 condições em "Pronto quando". Se precisar de mais, quebre a task.
 
---
 
### Fase 4 — Alinhamento
 
Após apresentar todas as tasks, pergunte:
 
> "A decomposição faz sentido? Alguma task está grande demais, fora de ordem ou faltando?"
 
Itere até confirmação. Só então as tasks estão prontas para execução.
 
---
 
## Heurísticas de qualidade
 
**As tasks estão boas quando:**
- A ordem de execução é óbvia
- Cada task pode ser revisada isoladamente
- Nenhuma task depende de decisão que ainda não foi tomada
- Executar todas as tasks em ordem satisfaz todos os critérios de aceitação da história
 
**Sinais de retrabalho iminente:**
- Uma task assume algo que não está declarado em nenhuma outra
- Duas tasks tocam os mesmos arquivos sem coordenação explícita
- A última task é "integrar tudo" — isso indica que as anteriores não eram atômicas
