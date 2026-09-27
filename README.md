# 🐝 HIVE Multi-Agent System

Sistema de orquestração multi-agente seguindo o padrão **Queen & Workers** do HIVE. Ideal para resolver problemas complexos que requerem múltiplos domínios de expertise.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────┐
│         User Query (Complexa)               │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │    Queen Agent       │
        │  (Claude Opus 5.5)   │
        │  Orquestrador        │
        └──────────┬───────────┘
                   │
        ┌──────────┼──────────┬──────────┬──────────┐
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
     ┌─────┐  ┌─────────┐ ┌─────────┐ ┌─────────┐
     │RAG  │  │  Math   │ │  Code   │ │   QA    │
     │W.   │  │  Worker │ │ Worker  │ │ Worker  │
     └─────┘  └─────────┘ └─────────┘ └─────────┘
        │          │          │          │
        └──────────┼──────────┼──────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Agregador (Queen)  │
        │  Síntese Final       │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Resposta Final      │
        │  Estruturada         │
        └──────────────────────┘
```

## 📋 Componentes

### Queen Agent (Orquestrador)
- **Modelo**: Claude Opus 5.5
- **Responsabilidades**:
  - Decompõe queries complexas em subtarefas
  - Roteia subtarefas para workers apropriados
  - Executa workers em paralelo (asyncio)
  - Agrega e sintetiza resultados

### Worker Agents (Especializados)
Todos usam **Claude Haiku 4.5** para otimização de custo:

1. **RAG Worker** 📚
   - Busca, pesquisa e síntese de informações
   - Compilação de conhecimento estruturado

2. **Math Worker** 🔢
   - Cálculos e análises numéricas
   - Validação de operações matemáticas

3. **Code Worker** 💻
   - Geração, otimização e debugging de código
   - Suporta múltiplas linguagens

4. **QA Worker** ✓
   - Validação e verificação de qualidade
   - Revisão e refinement de resultados

## 🚀 Quick Start

### 1. Instalação

```bash
pip install -r requirements.txt
```

### 2. Configurar API Key

```bash
export ANTHROPIC_API_KEY='seu-api-key'
```

### 3. Rodar Exemplo Simples

```bash
python example_simple.py
```

### 4. Rodar Exemplo Completo

```bash
python main.py
```

## 📊 Exemplo de Uso

```python
import asyncio
from src.agents.queen import QueenAgent
from src.workers import RAGWorker, MathWorker, CodeWorker, QAWorker
from src.utils.logger import HiveLogger

async def main():
    api_key = "your-api-key"
    logger = HiveLogger()
    queen = QueenAgent(api_key=api_key, logger=logger)
    
    # Registrar workers
    queen.register_worker("rag", RAGWorker(api_key))
    queen.register_worker("math", MathWorker(api_key))
    queen.register_worker("code", CodeWorker(api_key))
    queen.register_worker("qa", QAWorker(api_key))
    
    # Processar query complexa
    query = "Crie um script Python que calcula juros compostos, " \
            "faça uma busca sobre histórico de taxas de juros, " \
            "e valide se o código está correto."
    
    result = await queen.process_query(query)
    print(result)
    
    logger.print_summary()

asyncio.run(main())
```

## 🔍 Test Cases Inclusos

### Query 1: Juros Compostos
```
Crie um script Python que calcula juros compostos,
faça uma busca sobre histórico de taxas de juros,
e valide se o código está correto.
```

**Decomposição esperada:**
- RAG: Pesquisa histórico de taxas de juros
- Code: Gera script Python
- Math: Valida cálculos de juros
- QA: Revisão final do código

### Query 2: Machine Learning em NLP
```
Analise o impacto do machine learning em processamento de
linguagem natural, genere código exemplo para um classificador
de texto simples, e valide a qualidade da implementação.
```

### Query 3: Redes Neurais
```
Pesquise sobre a evolução das arquiteturas de rede neural,
calcule a complexidade computacional de um transformer simples,
implemente um exemplo básico de attention mechanism,
e revise a qualidade do código.
```

## 📈 Métricas e Logging

### Estrutura de Logs

Cada execução gera um arquivo JSONL em `logs/hive_session_YYYYMMDD_HHMMSS.jsonl`:

```json
{
  "timestamp": "2024-09-27T10:30:45",
  "type": "queen_decision",
  "query": "...",
  "decomposition": ["task1", "task2", ...]
}

{
  "timestamp": "2024-09-27T10:30:50",
  "type": "worker_complete",
  "worker": "CodeWorker",
  "duration": 5.23,
  "tokens": 1024,
  "status": "success"
}
```

### Resumo de Execução

```
======================================================================
HIVE EXECUTION SUMMARY
======================================================================
Session ID: 20240927_103045
Total Duration: 15.42s
Total Tokens: 5234

Worker Breakdown:
  RAGWorker       -   3.21s |  1024 tokens | success
  MathWorker      -   2.15s |   512 tokens | success
  CodeWorker      -   7.89s |  2048 tokens | success
  QAWorker        -   2.17s |  1650 tokens | success

Log file: logs/hive_session_20240927_103045.jsonl
======================================================================
```

## 🛠️ Desenvolvimento

### Executar Testes

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

### Estrutura de Arquivos

```
hive-multi-agent/
├── src/
│   ├── agents/
│   │   ├── base.py          # Classes base
│   │   ├── queen.py         # Orquestrador
│   │   └── __init__.py
│   ├── workers/
│   │   ├── rag_worker.py    # Pesquisa
│   │   ├── math_worker.py   # Cálculos
│   │   ├── code_worker.py   # Programação
│   │   ├── qa_worker.py     # Validação
│   │   └── __init__.py
│   ├── utils/
│   │   ├── logger.py        # Sistema de logging
│   │   └── __init__.py
│   ├── config.py            # Configurações
│   └── __init__.py
├── tests/
│   ├── test_workers.py      # Testes dos workers
│   └── __init__.py
├── logs/                    # Logs de execução
├── main.py                  # Exemplo completo
├── example_simple.py        # Exemplo simples
├── requirements.txt
└── README.md
```

## 💡 Insights para Blog Post

### Eficiência de Custo
- **Queen**: Claude Opus 5.5 (mais inteligente)
- **Workers**: Claude Haiku 4.5 (mais econômico)
- Economia: ~70% em tokens vs usar Opus para tudo

### Paralelização
- Execução asyncio reduz tempo total em ~50%
- Exemplo: 3 workers paralelos ≈ 5-7 segundos vs 15-20 sequencial

### Qualidade de Resultados
- Decomposição inteligente garante contexto apropriado
- Agregação sintetiza respostas coerentes
- QA worker valida completude e qualidade

### Escalabilidade
- Adicionar novo worker é trivial (herdar de BaseAgent)
- Logging estruturado permite análise detalhada
- Async permite milhares de queries simultâneas

## 🔑 Pontos-Chave para Documentação

1. **Como funciona a decomposição**: Queen analisa query e cria subtarefas
2. **Por que funciona**: Cada worker é especialista, execução paralela, agregação inteligente
3. **Resultados reais**: Mostrar logs, métricas de tempo e tokens
4. **Screenshots**: Incluir output de execução no blog
5. **Código comentado**: Mostrar snippets principais comentados

## 📝 Licença

MIT
