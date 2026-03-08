# Infra e Operacao - ALICI

Este diretorio contem os artefatos iniciais para implantacao em escala:

- `infra/terraform`: provisionamento de infraestrutura cloud.
- `infra/k8s`: manifests base de runtime (API, workers, HPA, ingress).

## Ordem recomendada
1. Provisionar infraestrutura com Terraform.
2. Configurar segredos e registries de imagem.
3. Aplicar manifests Kubernetes.
4. Validar health checks e autoscaling.
5. Executar testes de carga e tunning.

## Comandos
```bash
# Terraform
cd infra/terraform
terraform init
terraform plan
terraform apply

# Kubernetes
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/api-deployment.yaml
kubectl apply -f infra/k8s/worker-deployment.yaml
kubectl apply -f infra/k8s/hpa.yaml
kubectl apply -f infra/k8s/ingress.yaml
```
