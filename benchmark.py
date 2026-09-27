"""
Benchmark: Comparar HIVE vs Abordagem Tradicional
Demonstra ganhos em tempo, tokens e custo
"""

import asyncio
import os
import time
from dotenv import load_dotenv
from src.agents.queen import QueenAgent
from src.workers import RAGWorker, MathWorker, CodeWorker, QAWorker
from src.utils.logger import HiveLogger
from anthropic import Anthropic

load_dotenv()

async def benchmark_hive():
    """Executa uma query através do HIVE"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY não configurada")
        return None

    logger = HiveLogger()
    queen = QueenAgent(api_key=api_key, logger=logger)

    queen.register_worker("rag", RAGWorker(api_key))
    queen.register_worker("math", MathWorker(api_key))
    queen.register_worker("code", CodeWorker(api_key))
    queen.register_worker("qa", QAWorker(api_key))

    query = "Crie um script Python que calcula juros compostos, " \
            "faça uma busca sobre histórico de taxas de juros, " \
            "e valide se o código está correto."

    start = time.time()
    result = await queen.process_query(query)
    hive_duration = time.time() - start

    metrics = logger.get_metrics()
    hive_tokens = metrics['total_tokens']

    return {
        "method": "HIVE",
        "duration": hive_duration,
        "tokens": hive_tokens,
        "result_preview": result[:100]
    }

async def benchmark_traditional():
    """Simula a abordagem tradicional (Opus sequencial)"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY não configurada")
        return None

    client = Anthropic(api_key=api_key)

    tasks = [
        "Pesquise e resuma o histórico de taxas de juros",
        "Crie um script Python que calcula juros compostos",
        "Valide a fórmula matemática de juros compostos",
        "Revise a qualidade do código fornecido"
    ]

    start = time.time()
    total_tokens = 0

    for task in tasks:
        message = client.messages.create(
            model="claude-opus-5-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": task}]
        )
        tokens = message.usage.input_tokens + message.usage.output_tokens
        total_tokens += tokens

    traditional_duration = time.time() - start

    return {
        "method": "Tradicional",
        "duration": traditional_duration,
        "tokens": total_tokens,
        "result_preview": "Execução sequencial de 4 chamadas Opus"
    }

def calculate_metrics(hive_result, traditional_result):
    """Calcula e compara métricas"""

    time_savings = (1 - hive_result['duration'] / traditional_result['duration']) * 100
    token_savings = (1 - hive_result['tokens'] / traditional_result['tokens']) * 100

    cost_per_1k_opus = 0.015  # Opus: $15 por 1M tokens
    cost_per_1k_haiku = 0.002  # Haiku: $0.80 por 1M tokens

    traditional_cost = traditional_result['tokens'] * (cost_per_1k_opus / 1000)
    hive_cost = hive_result['tokens'] * (cost_per_1k_haiku / 1000)
    cost_savings = (1 - hive_cost / traditional_cost) * 100

    return {
        "time_savings": time_savings,
        "token_savings": token_savings,
        "cost_savings": cost_savings,
        "traditional_cost": traditional_cost,
        "hive_cost": hive_cost,
        "cost_per_query": hive_cost
    }

async def main():
    print("\n" + "="*80)
    print("🐝 HIVE BENCHMARK - Comparação de Performance".center(80))
    print("="*80)

    print("\n⏱️  Executando benchmark...\n")

    print("1️⃣  Testando HIVE (paralelo)...")
    hive_result = await benchmark_hive()

    if not hive_result:
        return

    print("✓ HIVE concluído")
    print(f"   Tempo: {hive_result['duration']:.2f}s")
    print(f"   Tokens: {hive_result['tokens']}")

    print("\n2️⃣  Testando Abordagem Tradicional (sequencial)...")
    traditional_result = await benchmark_traditional()

    if not traditional_result:
        return

    print("✓ Tradicional concluído")
    print(f"   Tempo: {traditional_result['duration']:.2f}s")
    print(f"   Tokens: {traditional_result['tokens']}")

    metrics = calculate_metrics(hive_result, traditional_result)

    print("\n" + "="*80)
    print("📊 RESULTADOS".center(80))
    print("="*80)

    print("\n┌─────────────────────┬──────────────┬──────────────┬──────────┐")
    print("│ Métrica             │ Tradicional  │ HIVE         │ Ganho    │")
    print("├─────────────────────┼──────────────┼──────────────┼──────────┤")
    print(f"│ Tempo (s)           │ {traditional_result['duration']:11.2f} │ {hive_result['duration']:12.2f} │ {metrics['time_savings']:6.1f}% ⚡ │")
    print(f"│ Tokens              │ {traditional_result['tokens']:11} │ {hive_result['tokens']:12} │ {metrics['token_savings']:6.1f}% 📉 │")
    print(f"│ Custo (USD)         │ ${metrics['traditional_cost']:10.4f} │ ${metrics['hive_cost']:11.4f} │ {metrics['cost_savings']:6.1f}% 💰 │")
    print("└─────────────────────┴──────────────┴──────────────┴──────────┘")

    print("\n💡 Insights:")
    print(f"   • HIVE é {metrics['time_savings']:.0f}% mais rápido (paralelo vs sequencial)")
    print(f"   • HIVE usa {metrics['token_savings']:.0f}% menos tokens (Haiku vs Opus)")
    print(f"   • HIVE economiza {metrics['cost_savings']:.0f}% em custo por query")
    print(f"   • Custo HIVE: ${metrics['hive_cost']:.4f} vs Tradicional: ${metrics['traditional_cost']:.4f}")

    print("\n🎯 Break-even:")
    queries_needed = 100  # Exemplo
    traditional_cost_total = metrics['traditional_cost'] * queries_needed
    hive_cost_total = metrics['hive_cost'] * queries_needed
    savings = traditional_cost_total - hive_cost_total
    print(f"   • {queries_needed} queries: Economia de ${savings:.2f}")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
