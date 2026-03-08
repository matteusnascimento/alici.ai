# Checklist de Hardening - Producao ALICI

## Identidade e acesso
- [ ] Habilitar MFA para todas as contas administrativas (AWS, GitHub, Stripe, provedor de DNS).
- [ ] Remover credenciais de longo prazo e usar IAM Role/OIDC no CI.
- [ ] Aplicar principio do menor privilegio para roles de API, workers e CI/CD.
- [ ] Rotacionar segredos criticos (JWT, Stripe, OpenAI, DB) com periodicidade definida.

## Rede e perimetro
- [ ] Isolar RDS e Redis em subnets privadas sem IP publico.
- [ ] Restringir Security Groups por origem/destino especifica (sem 0.0.0.0/0 desnecessario).
- [ ] Colocar API atras de ALB + WAF com regras para SQLi/XSS e rate limiting.
- [ ] Habilitar TLS 1.2+ ponta a ponta e HSTS no ingress.

## Kubernetes
- [ ] Definir `securityContext` (runAsNonRoot, readOnlyRootFilesystem, drop ALL capabilities).
- [ ] Definir `resources` requests/limits em todos os pods (incluindo jobs/cronjobs).
- [ ] Configurar `PodDisruptionBudget` para API e workers.
- [ ] Ativar NetworkPolicies para bloquear trafego lateral indevido.
- [ ] Mover segredos para External Secrets + AWS Secrets Manager/KMS.

## Aplicacao e API
- [ ] Desativar CORS amplo em producao (`allow_origins` explicito por ambiente).
- [ ] Garantir endpoint de health dedicado e barato (`/healthz`) para probes e Docker.
- [ ] Implementar trilha de auditoria para acoes sensiveis (billing, API keys, auth).
- [ ] Cobrir endpoints criticos com testes de autorizacao por tenant.

## Dados
- [ ] Garantir migracoes versionadas Alembic antes de cada deploy de schema.
- [ ] Habilitar backup automatico e teste de restore de RDS com RPO/RTO definidos.
- [ ] Criptografar dados sensiveis em repouso (KMS) e em transito.
- [ ] Aplicar politica de retencao e descarte para logs e historico de conversas.

## Observabilidade e resposta
- [ ] Padronizar logs estruturados com `request_id` e `organization_id`.
- [ ] Habilitar tracing distribuido (OpenTelemetry) e correlacao com logs.
- [ ] Criar alertas para erro 5xx, latencia p95, fila pendente e falha de webhook.
- [ ] Definir runbooks para incidente de indisponibilidade, vazamento de segredo e regressao de deploy.

## CI/CD e supply chain
- [ ] Bloquear merge em `main` sem testes e sem `terraform plan` limpo.
- [ ] Adicionar scan SAST e dependencia (pip-audit, trivy, codeql).
- [ ] Assinar imagens de container e validar proveniencia (cosign/slsa).
- [ ] Promover deploy com aprovacao manual para producao.

## Governanca
- [ ] Manter matriz de ownership por modulo (backend, frontend, infra, billing).
- [ ] Revisar checklist a cada sprint e registrar evidencias.
- [ ] Realizar game day trimestral para DR e incidentes de seguranca.
