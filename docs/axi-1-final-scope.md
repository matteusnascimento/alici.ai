# AXI 1.0 - Escopo Final Congelado

Este documento congela o escopo da plataforma AXI 1.0. A regra para os
proximos ciclos e:

```txt
Este modulo gera valor real para o cliente?
```

Nao devem ser criados novos modulos antes do fechamento dos ciclos
operacionais existentes.

## Modulos oficiais

- Home
- Revenue
- Chats
- AXI Assistant
- Marketing
- Studio
- Integrations
- Account
- Administracao

## Marketing

O Marketing deve fechar o ciclo:

```txt
Planejamento
+
Execucao
+
Publicacao
+
Mensuracao
```

Fluxo definitivo:

```txt
Nova Campanha
-> Objetivo
-> Canal
-> Publico
-> Orcamento
-> Criativo
-> Publicar
-> Metricas
-> Revenue
```

Objetivos oficiais:

- Trafego
- Leads
- Mensagens
- Conversoes
- Reservas
- Reconhecimento
- Remarketing

Canais oficiais:

- Instagram
- Facebook
- Google Ads
- Website
- WhatsApp

O Marketing nao cria arte diretamente. Ele usa o Studio:

```txt
Marketing
-> Criar campanha
-> Selecionar criativo
-> Abrir Studio
-> Criar ou escolher criativo
-> Voltar para campanha
```

## Revenue

Revenue deve responder:

- Quanto vendi?
- De onde veio?
- Quem converteu?
- Qual campanha vendeu?
- Qual cidade gera mais receita?
- Qual canal gera mais reservas?

Dados necessarios:

- Reservas
- Receita
- Leads
- Conversoes
- Campanhas
- Origem

Fontes de dados:

- Website
- WhatsApp
- Instagram
- Meta Ads
- Google Ads
- OmniBees
- PMS

## Chats

Chats e a central unica de atendimento para:

- WhatsApp
- Instagram
- Website Chat

Informacoes do cliente:

- Nome
- Telefone
- Cidade
- Ultimo interesse
- Ultima mensagem
- Origem
- Status
- Tags

Acoes:

- Responder
- Transferir
- Enviar cotacao
- Criar tarefa
- Adicionar tag

## AXI Assistant

O AXI Assistant deve evoluir de chat para assistente operacional da plataforma.

Modos:

- Executivo: analise de receita, relatorios e decisoes.
- Marketing: campanhas, canais, publicos e calendario.
- Studio: posts, criativos, videos e templates.
- Operacional: plano de acao semanal, tarefas e atendimento.

## Studio

Nao criar novas areas. Melhorar as existentes.

Biblioteca central:

- Templates
- Brand Kit
- Logos
- Fotos
- Videos
- Campanhas
- Assets

APIs realmente necessarias:

- Templates: Freepik API ou Envato API
- Remover fundo: Remove.bg
- Voz: ElevenLabs
- Imagem IA: OpenAI Images ou Flux
- Video: Shotstack ou Creatomate

Nao integrar muitas APIs. Integrar apenas as que resolvem lacunas reais.

## Integrations

Fluxo definitivo:

```txt
Conectar
-> OAuth
-> Importar historico
-> Captura em tempo real
```

Integracoes minimas:

- Meta: Instagram, WhatsApp, Meta Ads
- Google: Google Ads, Google Analytics
- Website: AXI Tracker
- Hotelaria: OmniBees, PMS

## Administracao

Usuarios:

- Criar
- Editar
- Desativar
- Convidar

Permissoes:

- Revenue
- Chats
- Assistant
- Marketing
- Studio
- Integrations
- Administracao

Billing deve ser exclusivo para administrador.

Auditoria deve cobrir:

- Logins
- Integracoes
- Campanhas
- Reservas
- IA

## Criterio final de lancamento

Interface:

- 100% das rotas funcionando
- 100% dos botoes funcionando
- 0 telas vazias
- 0 layouts quebrados

Backend:

- 0 endpoints mortos
- 0 mocks em producao
- 0 dados fake

Integracoes minimas operacionais:

- WhatsApp
- Instagram
- Google Ads
- Google Analytics
- Website Tracker

Marketing:

- Criar
- Publicar
- Mensurar

Revenue:

- Receber dados
- Analisar
- Exibir

Studio:

- Criar
- Editar
- Exportar

Assistant:

- Conversar
- Analisar
- Gerar conteudo
- Gerar relatorios

Quando estes itens estiverem fechados, a fase de construcao termina e a fase de
validacao com 2 a 5 pousadas reais pode comecar antes de qualquer expansao
maior do produto.
