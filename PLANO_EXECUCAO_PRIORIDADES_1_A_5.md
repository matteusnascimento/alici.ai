# Plano de Execucao - Prioridades 1 a 5 (ALICI)

Data: 2026-03-08

## Status atual
- [x] 1) Memoria do usuario (persistente)
- [x] 2) Busca na web (fallback automatico)
- [x] 3) Conversar com documentos (RAG)
- [ ] 4) Sistema de agentes
- [ ] 5) Integracoes (incluindo WhatsApp)

## 1) Memoria do usuario - entregue
Implementado:
- Modelo: `app/models/user_memory.py`
- Tabela (migracao): `migrations/versions/20260308_0002_add_user_memory_table.py`
- Servico: `app/services/user_memory_service.py`
- Captura automatica no chat: `app/api/routes/chat.py`
- Consumo no contexto de resposta: `app/services/ai_orchestrator.py`
- API para consultar e editar memoria:
  - `GET /api/user/memory`
  - `POST /api/user/memory`
- Testes: `tests/test_user_memory_persistence.py`

## 2) Busca na web - proxima entrega
Objetivo:
- Se o modelo nao tiver confianca/contexto, acionar web search e responder com resumo.

Implementacao proposta:
- Entregue em:
  - `app/services/web_search_service.py`
  - `app/services/ai_orchestrator.py`
- Comportamento atual:
  - fallback automatico quando provider de IA indisponivel/sem resposta
  - heuristica para perguntas de web (hoje, atual, noticias, cotacao, etc.)
  - resposta inclui fonte
- Controle por configuracao:
  - `settings.web_search_enabled`
  - `settings.web_search_timeout_seconds`
- Teste de regressao:
  - `tests/test_web_search_fallback.py`

Criterio de aceite:
- [x] Perguntas de atualidades retornam resposta com base externa quando o provider principal nao responde.

## 3) Conversar com documentos (RAG) - fase seguinte
Objetivo:
- Upload de PDF/DOCX/TXT/CSV e resposta contextual baseada nos arquivos.

Implementacao proposta:
- Entregue em:
  - Modelos: `app/models/knowledge.py`
  - Servico: `app/services/knowledge_service.py`
  - Rotas: `app/api/routes/knowledge.py`
  - Migracao: `migrations/versions/20260308_0003_add_knowledge_tables.py`
- Endpoints ativos:
  - `POST /api/knowledge/upload`
  - `POST /api/knowledge/query`
- Pipeline atual:
  - upload -> extracao texto -> chunking -> indexacao SQL -> retrieval por relevancia lexical
- Formatos:
  - TXT e CSV totalmente operacionais
  - PDF e DOCX com suporte condicional (requer pacotes `pypdf` e `python-docx`)
- Testes:
  - `tests/test_knowledge_rag_flow.py`

Criterio de aceite:
- [x] Resposta retorna trechos relevantes e referencias dos documentos indexados.

## 4) Sistema de agentes
Objetivo:
- Usuario criar agentes personalizados por prompt, ferramentas e memoria.

Implementacao proposta:
- Evoluir `platform_agents` com campos de ferramentas/memoria habilitada.
- Endpoints de lifecycle:
  - criar, editar, publicar, ativar/desativar
- Runner com politicas de timeout/retry.

Criterio de aceite:
- Um usuario consegue criar agente de atendimento e usá-lo em conversa real.

## 5) Integracoes (WhatsApp primeiro)
Objetivo:
- Receber mensagem de canal externo e responder com ALICI.

Implementacao proposta:
- WhatsApp Cloud API:
  - webhook inbound
  - dispatcher outbound
- Mapeamento tenant por credencial/integracao ativa.

Criterio de aceite:
- Mensagem recebida no WhatsApp dispara resposta automatica em menos de 3s em ambiente piloto.

## Ordem de entrega recomendada (sprints curtos)
1. Agentes (runtime + UX)
2. Integracao WhatsApp

## Riscos tecnicos
- Custo de inferencia e busca externa sem limites de quota.
- Qualidade de parsing em PDF complexo.
- Isolamento multi-tenant em webhooks de canais externos.

## Mitigacoes
- Feature flags + limites por plano.
- Observabilidade com `request_id` e `organization_id`.
- Testes de contrato por endpoint critico.
