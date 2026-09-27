"""
HIVE Multi-Agent System - Exemplo de Uso
Demonstra o padrão Queen & Workers com 3 queries complexas
"""

import asyncio
import os
from src.config import config
from src.agents.queen import QueenAgent
from src.workers import RAGWorker, MathWorker, CodeWorker, QAWorker
from src.utils.logger import HiveLogger

async def run_hive_query(queen: QueenAgent, query: str) -> str:
    """Executa uma query através do HIVE"""
    result = await queen.process_query(query)
    return result

async def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY não configurada. Use: export ANTHROPIC_API_KEY='your-key'")
        return

    logger = HiveLogger()

    print("\n" + "="*80)
    print("🐝 HIVE MULTI-AGENT SYSTEM - DEMO".center(80))
    print("="*80)
    print("\nArquitetura:")
    print("  • Queen: Claude Opus 5.5 (Orquestrador)")
    print("  • RAG Worker: Busca e síntese de informações")
    print("  • Math Worker: Cálculos e análises numéricas")
    print("  • Code Worker: Geração e debugging de código")
    print("  • QA Worker: Validação e refinement")
    print("="*80 + "\n")

    queen = QueenAgent(api_key=api_key, logger=logger)

    queen.register_worker("rag", RAGWorker(api_key))
    queen.register_worker("math", MathWorker(api_key))
    queen.register_worker("code", CodeWorker(api_key))
    queen.register_worker("qa", QAWorker(api_key))

    queries = [
        "Crie um script Python que calcula juros compostos, faça uma busca sobre histórico de taxas de juros, e valide se o código está correto.",

        "Analise o impacto do machine learning em processamento de linguagem natural, genere código exemplo para um classificador de texto simples, e valide a qualidade da implementação.",

        "Pesquise sobre a evolução das arquiteturas de rede neural, calcule a complexidade computacional de um transformer simples, implemente um exemplo básico de attention mechanism, e revise a qualidade do código."
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"QUERY #{i}".ljust(80))
        print(f"{'='*80}")
        print(f"\n{query}\n")

        result = await run_hive_query(queen, query)

        print(f"\n{'─'*80}")
        print("📊 RESULTADO FINAL:")
        print(f"{'─'*80}\n")
        print(result)
        print()

    logger.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
