"""
Testes unitários para os workers
"""

import pytest
import asyncio
import os
from src.agents.base import TaskRequest
from src.workers import RAGWorker, MathWorker, CodeWorker, QAWorker

@pytest.fixture
def api_key():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY não configurada")
    return key

@pytest.mark.asyncio
async def test_rag_worker(api_key):
    worker = RAGWorker(api_key)
    request = TaskRequest(task="Qual é a história dos juros compostos?")
    response = await worker.process(request)

    assert response.success
    assert len(response.result) > 0
    assert response.tokens_used > 0
    assert response.worker_name == "RAGWorker"

@pytest.mark.asyncio
async def test_math_worker(api_key):
    worker = MathWorker(api_key)
    request = TaskRequest(task="Calcule o valor futuro de R$ 1000 com juros de 5% ao ano por 10 anos")
    response = await worker.process(request)

    assert response.success
    assert len(response.result) > 0
    assert response.tokens_used > 0
    assert response.worker_name == "MathWorker"

@pytest.mark.asyncio
async def test_code_worker(api_key):
    worker = CodeWorker(api_key)
    request = TaskRequest(task="Crie uma função Python para calcular juros compostos")
    response = await worker.process(request)

    assert response.success
    assert "def " in response.result or "python" in response.result.lower()
    assert response.tokens_used > 0
    assert response.worker_name == "CodeWorker"

@pytest.mark.asyncio
async def test_qa_worker(api_key):
    worker = QAWorker(api_key)
    request = TaskRequest(task="Revise este código: def calc(p, r, t): return p * (1 + r)**t")
    response = await worker.process(request)

    assert response.success
    assert len(response.result) > 0
    assert response.tokens_used > 0
    assert response.worker_name == "QAWorker"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
