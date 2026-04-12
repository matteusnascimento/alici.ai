# Deploy Frontend no Render

## Estrategia atual

O projeto hoje usa um unico servico no Render:

- o frontend e buildado a partir de frontend/dist
- os arquivos gerados sao copiados para backend/frontend_dist
- o backend FastAPI serve esse frontend compilado no mesmo dominio

Em outras palavras: a aparencia de producao depende do build do frontend embutido no deploy do backend.

## Fonte de verdade

A configuracao real de deploy esta em render.yaml.

Fluxo atual:

1. Instala dependencias Python do backend
2. Entra em frontend
3. Executa npm install
4. Executa npm run build
5. Copia frontend/dist para backend/frontend_dist
6. Roda migracoes
7. Sobe o backend, que tambem entrega os arquivos do frontend

## URL esperada em producao

- App: https://alici-ai.onrender.com
- API: https://alici-ai.onrender.com/api
- Docs: https://alici-ai.onrender.com/docs
- Health: https://alici-ai.onrender.com/health

## Por que o visual pode diferir do VS Code

1. Local usa Vite em modo dev
2. Render usa build de producao compilado
3. Se o deploy falhar, o Render pode continuar servindo arquivos antigos
4. Se o navegador/CDN estiver com cache, a UI pode parecer desatualizada

## Checklist exato para validar a mesma versao

### 1. GitHub

Confirme que o commit desejado esta no main.

### 2. Build local

Rode:

```bash
cd frontend
npm run build
```

Se o build falhar, o Render nao vai publicar a mesma UI do local.

### 3. Sync local de comparacao

Para simular o comportamento do Render localmente:

```bash
cd ..
Remove-Item backend/frontend_dist/* -Recurse -Force
Copy-Item frontend/dist/* backend/frontend_dist -Recurse -Force
```

### 4. Render

No painel do Render:

1. Abra o servico axi-backend
2. Clique em Manual Deploy
3. Escolha Deploy latest commit
4. Aguarde o build terminar sem erro

### 5. Browser

Depois do deploy:

1. Abra https://alici-ai.onrender.com
2. Faça hard refresh com Ctrl + F5
3. Se ainda aparecer a UI antiga, abra janela anonima
4. Verifique se os assets JS/CSS carregados sao os mais recentes

### 6. Validacao rapida de assets

O nome dos arquivos em producao deve mudar quando o build muda.

Exemplo local atual:

- index-BbrIrmU4.css
- index-D8w_4kVi.js

Se o Render estiver servindo outros nomes, ele ainda esta com build antigo.

## Configuracao recomendada

### CORS

Como frontend e backend estao no mesmo dominio em producao, o CORS principal deve apontar para:

```env
CORS_ALLOWED_ORIGINS=https://alici-ai.onrender.com
```

### API URL

No frontend, a API pode continuar relativa:

```ts
const API_URL = import.meta.env.VITE_API_URL || '/api';
```

Isso evita diferencas entre dev e producao quando o frontend e servido pelo backend.

## Diagnostico rapido quando Render estiver diferente

Se a aparencia do Render estiver diferente da do VS Code, cheque nesta ordem:

1. O commit correto esta no GitHub?
2. npm run build passa localmente?
3. O deploy mais recente do Render terminou com sucesso?
4. Os nomes dos assets em producao batem com o build novo?
5. O navegador ainda esta usando cache?

## Observacao importante

Este repositorio nao esta configurado hoje para um Static Site separado como estrategia principal. A documentacao anterior estava ambigua nesse ponto. O modelo atual e:

- backend web service
- frontend buildado dentro do deploy do backend
- frontend servido pelo FastAPI
