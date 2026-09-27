# 🚀 Guia de Deployment - HIVE Multi-Agent

Instruções para deploy em produção, serverless, e ambientes corporativos.

## 1. Deploy Local / Desenvolvimento

### 1.1 Setup Local
```bash
# Clone e setup
git clone <repo>
cd hive-multi-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure API key
export ANTHROPIC_API_KEY='your-key'

# Teste
python example_simple.py
```

### 1.2 Modo Servidor (Flask)
```bash
pip install flask
```

```python
# server.py
from flask import Flask, request, jsonify
from src.agents.queen import QueenAgent
from src.workers import *
import asyncio

app = Flask(__name__)
queen = None

@app.before_first_request
def init():
    global queen
    api_key = os.getenv("ANTHROPIC_API_KEY")
    queen = QueenAgent(api_key=api_key)
    queen.register_worker("rag", RAGWorker(api_key))
    queen.register_worker("math", MathWorker(api_key))
    queen.register_worker("code", CodeWorker(api_key))
    queen.register_worker("qa", QAWorker(api_key))

@app.route("/query", methods=["POST"])
async def process_query():
    data = request.json
    query = data.get("query")
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    result = await queen.process_query(query)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=False, port=5000)
```

## 2. Deploy Serverless

### 2.1 AWS Lambda
```bash
pip install awslambdaric
```

```python
# lambda_function.py
import json
import asyncio
import os
from src.agents.queen import QueenAgent
from src.workers import *

queen = None

def lambda_handler(event, context):
    global queen
    
    if queen is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        queen = QueenAgent(api_key=api_key)
        queen.register_worker("rag", RAGWorker(api_key))
        queen.register_worker("math", MathWorker(api_key))
        queen.register_worker("code", CodeWorker(api_key))
        queen.register_worker("qa", QAWorker(api_key))
    
    query = event.get("query")
    
    try:
        result = asyncio.run(queen.process_query(query))
        return {
            "statusCode": 200,
            "body": json.dumps({"result": result})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
```

**Deploy:**
```bash
# Zip dependencies
pip install -r requirements.txt -t package/
cp -r src package/
cd package
zip -r function.zip .
cd ..

# Upload to Lambda
aws lambda create-function \
    --function-name hive-processor \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://package/function.zip \
    --environment Variables={ANTHROPIC_API_KEY=your-key}
```

### 2.2 Google Cloud Functions
```bash
pip install functions-framework
```

```python
# main.py
import functions_framework
import asyncio
import os
from src.agents.queen import QueenAgent
from src.workers import *

queen = None

@functions_framework.http
def process_hive_query(request):
    global queen
    
    if queen is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        queen = QueenAgent(api_key=api_key)
        queen.register_worker("rag", RAGWorker(api_key))
        queen.register_worker("math", MathWorker(api_key))
        queen.register_worker("code", CodeWorker(api_key))
        queen.register_worker("qa", QAWorker(api_key))
    
    request_json = request.get_json()
    query = request_json.get("query")
    
    try:
        result = asyncio.run(queen.process_query(query))
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}, 500
```

**Deploy:**
```bash
gcloud functions deploy process-hive-query \
    --runtime python311 \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars ANTHROPIC_API_KEY=your-key \
    --entry-point process_hive_query
```

## 3. Docker Deployment

### 3.1 Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "server.py"]
```

### 3.2 Docker Compose
```yaml
version: '3.8'

services:
  hive-processor:
    build: .
    ports:
      - "5000:5000"
    environment:
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      LOG_DIR: /app/logs
    volumes:
      - ./logs:/app/logs
    restart: always

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**Run:**
```bash
export ANTHROPIC_API_KEY='your-key'
docker-compose up
```

## 4. Performance Optimization

### 4.1 Caching de Decomposições
```python
# Adicionar ao QueenAgent
from functools import lru_cache

@lru_cache(maxsize=128)
async def decompose_query_cached(self, query_hash: str):
    # Reutiliza decomposição de queries similares
    return await self.decompose_query(query_hash)
```

### 4.2 Connection Pooling
```python
# Usar aiohttp session para reutilizar conexões
import aiohttp

class QueenAgent:
    def __init__(self, api_key: str):
        self.session = aiohttp.ClientSession()
        # ...
    
    async def cleanup(self):
        await self.session.close()
```

### 4.3 Rate Limiting
```python
from asyncio import Semaphore

class QueenAgent:
    def __init__(self, api_key: str, max_concurrent=5):
        self.semaphore = Semaphore(max_concurrent)
    
    async def execute_workers_parallel(self, tasks):
        async def bounded_worker(task):
            async with self.semaphore:
                return await self.workers[task.worker_type].process(...)
        
        # Usar bounded_worker em vez de direto
```

## 5. Monitoring & Observability

### 5.1 Logging Estruturado
```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()
logger.info("query_processed", 
            duration=7.1, 
            tokens=1850,
            query_id="abc123")
```

### 5.2 Métricas Prometheus
```python
from prometheus_client import Counter, Histogram

query_counter = Counter('hive_queries_total', 'Total queries')
query_duration = Histogram('hive_query_duration_seconds', 'Query duration')
tokens_used = Histogram('hive_tokens_used', 'Tokens per query')

@query_duration.time()
async def process_query(self, query):
    try:
        result = await ...
        query_counter.inc()
        tokens_used.observe(result_tokens)
        return result
    except Exception as e:
        logger.error("query_failed", error=str(e))
        raise
```

### 5.3 Alertas
```python
# Exemplo: alerta se latência > 30s
if query_duration > 30:
    send_alert("HIVE latência alta", 
              f"Query demorou {query_duration}s")

# Exemplo: alerta se tokens > orçamento
if total_tokens > daily_token_budget:
    send_alert("HIVE budget excessivo",
              f"Tokens: {total_tokens}/{daily_token_budget}")
```

## 6. Segurança

### 6.1 API Key Management
```python
# ❌ Não fazer
API_KEY = "sk-..."  # Hardcoded!

# ✅ Correto
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ✅ Melhor: AWS Secrets Manager
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='anthropic-api-key')
API_KEY = secret['SecretString']
```

### 6.2 Rate Limiting por User
```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_queries_per_hour=100):
        self.max_queries = max_queries_per_hour
        self.user_queries = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        # Limpar queries antigas
        self.user_queries[user_id] = [
            t for t in self.user_queries[user_id]
            if t > one_hour_ago
        ]
        
        if len(self.user_queries[user_id]) >= self.max_queries:
            return False
        
        self.user_queries[user_id].append(now)
        return True
```

### 6.3 Input Validation
```python
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    query: str
    user_id: str
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        if len(v) > 5000:
            raise ValueError('Query too long (max 5000 chars)')
        return v
```

## 7. Testing em Produção

### 7.1 Health Checks
```python
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "queen_loaded": queen is not None,
        "workers": list(queen.workers.keys()) if queen else []
    })
```

### 7.2 Smoke Tests
```bash
#!/bin/bash
# test_production.sh

API_URL="https://api.example.com"

# Test 1: Query simples
response=$(curl -X POST $API_URL/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Calcule 2+2"}')

if [[ $response == *"success"* ]]; then
  echo "✓ Test 1 passed"
else
  echo "❌ Test 1 failed: $response"
  exit 1
fi

# Test 2: Health check
health=$(curl $API_URL/health)
if [[ $health == *"healthy"* ]]; then
  echo "✓ Health check passed"
else
  echo "❌ Health check failed"
  exit 1
fi
```

## 8. Escalabilidade

### 8.1 Load Balancing
```yaml
# nginx.conf
upstream hive_backend {
    least_conn;
    server hive-1:5000;
    server hive-2:5000;
    server hive-3:5000;
}

server {
    listen 80;
    
    location /query {
        proxy_pass http://hive_backend;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}
```

### 8.2 Queue de Processamento
```python
# Com Celery para processamento assíncrono
from celery import Celery

app = Celery('hive')

@app.task
def process_query_async(query):
    asyncio.run(queen.process_query(query))
```

## Checklist de Deployment

- [ ] API key em variável de ambiente (não hardcoded)
- [ ] Logging estruturado (JSON)
- [ ] Health check endpoint
- [ ] Rate limiting implementado
- [ ] Error handling completo
- [ ] Timeouts configurados
- [ ] Monitoring (Prometheus/CloudWatch)
- [ ] Alertas em place
- [ ] Testes de carga
- [ ] Backup de logs
- [ ] Documentação atualizada
- [ ] Security review completo
