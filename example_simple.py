"""
Exemplo simples de uso do HIVE - Teste rápido
"""

import asyncio
import os
from dotenv import load_dotenv
from src.agents.queen import QueenAgent
from src.workers import RAGWorker, MathWorker, CodeWorker, QAWorker
from src.utils.logger import HiveLogger

load_dotenv()

async def simple_example():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY não configurada")
        return

    logger = HiveLogger()
    queen = QueenAgent(api_key=api_key, logger=logger)

    queen.register_worker("rag", RAGWorker(api_key))
    queen.register_worker("math", MathWorker(api_key))
    queen.register_worker("code", CodeWorker(api_key))
    queen.register_worker("qa", QAWorker(api_key))

    query = "Crie um script Python que calcula juros compostos, faça uma busca sobre histórico de taxas de juros, e valide se o código está correto."

    print("\n🐝 Iniciando HIVE...\n")
    result = await queen.process_query(query)

    print("\n" + "="*80)
    print("RESULTADO:")
    print("="*80 + "\n")
    print(result)

    logger.print_summary()

if __name__ == "__main__":
    asyncio.run(simple_example())
