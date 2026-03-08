# Diagrama da Arquitetura de Escala - ALICI

```mermaid
flowchart TB
    U1[Web App Next.js]
    U2[Mobile Flutter]
    U3[Dev API Clients]

    CDN[CDN + WAF + API Gateway]
    AUTH[Auth + Rate Limit + Tenant Guard]
    API[Core API FastAPI]

    ORCH[AI Router ai_router.py]
    AGENT[Agent Engine\nPlanner Executor Memory Knowledge Tools]
    RAG[RAG Service\nIngest Retrieval Re-rank]
    TOOL[Tool Runtime\nweb_search db_query email calendar http_request]
    INTEG[Integration Hub\nWhatsApp Slack Telegram Shopify WordPress]
    BILL[Billing Service\nStripe + Webhooks]
    PUB[Public API v1\nchat agents embeddings]

    Q[Queue Bus\nKafka RabbitMQ SQS]
    WK[Worker Fleet\nAsync jobs and automations]

    PG[(PostgreSQL OLTP)]
    RD[(Redis)]
    VDB[(Vector DB\npgvector Qdrant Weaviate)]
    OBJ[(Object Storage\nS3 R2)]
    AN[(Analytics Store)]

    OBS[Observability\nLogs Metrics Tracing Alerts]
    SEC[Security\nVault KMS RBAC Audit]

    U1 --> CDN
    U2 --> CDN
    U3 --> CDN
    CDN --> AUTH --> API

    API --> ORCH
    ORCH --> AGENT
    ORCH --> RAG
    ORCH --> TOOL
    ORCH --> INTEG
    API --> BILL
    API --> PUB

    AGENT --> Q
    RAG --> Q
    INTEG --> Q
    BILL --> Q
    Q --> WK

    API --> PG
    API --> RD
    RAG --> VDB
    RAG --> OBJ
    WK --> PG
    WK --> VDB
    WK --> OBJ
    API --> AN
    WK --> AN

    API --> OBS
    WK --> OBS
    API --> SEC
    WK --> SEC

    BILL -.webhooks.-> API
    INTEG -.external events.-> API
```

## Leitura rapida
- Camada de entrada protegida por WAF + gateway.
- API stateless para scale horizontal.
- Jobs pesados e integrações rodam em workers via fila.
- Dados separados por funcao: transacional, cache, vetorial e objetos.
- Observabilidade e seguranca sao transversais a toda a plataforma.
