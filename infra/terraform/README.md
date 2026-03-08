# ALICI Infra as Code (Terraform)

Base de infraestrutura para escala de milhoes de usuarios.

## Provisiona
- VPC e subnets publica/privada
- EKS cluster + node group
- RDS PostgreSQL
- ElastiCache Redis
- S3 para artifacts
- CloudWatch log groups

## Uso rapido
```bash
cd infra/terraform
terraform init
terraform plan -var="environment=prod"
terraform apply -var="environment=prod"
```

## Variaveis chave
- `aws_region`
- `environment`
- `db_instance_class`
- `redis_node_type`
- `k8s_desired_nodes`

## Proximos hardenings recomendados
- Security groups restritivos por servico
- KMS para RDS/S3/Secrets
- WAF + ALB + Route53
- Remote state (S3 + DynamoDB lock)
- Multi-region DR
