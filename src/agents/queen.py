import asyncio
import json
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
from pydantic import BaseModel
from src.utils.logger import HiveLogger
from src.agents.base import TaskRequest, TaskResponse

class DecomposedTask(BaseModel):
    worker_type: str
    task: str
    priority: int

class QueenAgent:
    """
    Queen Agent: Orquestrador central que decompõe queries e coordena workers.
    Estratégia: recebe query complexa, decompõe em subtarefas, roteia para workers apropriados,
    agrega resultados finais.
    """

    def __init__(self, api_key: str, model: str = "claude-opus-5-5", logger: Optional[HiveLogger] = None):
        self.name = "Queen"
        self.model = model
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key)
        self.logger = logger or HiveLogger()
        self.workers: Dict[str, Any] = {}

    def register_worker(self, worker_type: str, worker):
        """Registra um worker specializado"""
        self.workers[worker_type] = worker

    async def decompose_query(self, query: str) -> List[DecomposedTask]:
        """
        Decompõe uma query complexa em subtarefas específicas para cada worker.
        """
        system_prompt = """Você é o coordenador de um sistema multi-agente (HIVE Queen).
Sua responsabilidade é decompor queries complexas em subtarefas específicas.

Tipos de workers disponíveis:
1. RAG: Busca, pesquisa e síntese de informações
2. Math: Cálculos, análises numéricas e validação matemática
3. Code: Geração, debugging e otimização de código
4. QA: Validação, verificação de qualidade e refinamento

Analise a query e decomponha em subtarefas. Para cada subtarefa, especifique:
- worker_type: qual worker deve executar
- task: descrição clara da subtarefa
- priority: prioridade (1=alta, 2=média, 3=baixa)

Retorne um JSON array com as subtarefas."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Decomponha esta query complexa em subtarefas:\n\n{query}"
                }
            ]
        )

        response_text = None
        if message.content:
            for block in message.content:
                block_type = getattr(block, 'type', None)
                if block_type == 'text' and hasattr(block, 'text') and block.text:
                    response_text = block.text
                    break

        if not response_text:
            print(f"❌ Resposta vazia da API ao decompor (stop_reason: {message.stop_reason})")
            return []

        try:
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1

            if json_start == -1 or json_end == 0:
                print(f"❌ Nenhum JSON encontrado na resposta")
                return []

            json_str = response_text[json_start:json_end]
            tasks_data = json.loads(json_str)

            tasks = [DecomposedTask(**task) for task in tasks_data]
            tasks.sort(key=lambda x: x.priority)

            return tasks
        except Exception as e:
            print(f"❌ Erro ao parsear decomposição: {e}")
            return []

    async def execute_workers_parallel(self, tasks: List[DecomposedTask]) -> Dict[str, TaskResponse]:
        """
        Executa workers em paralelo para as subtarefas.
        """
        worker_tasks = []
        task_mapping = {}

        for i, task in enumerate(tasks):
            worker_type = task.worker_type.lower()
            if worker_type in self.workers:
                self.logger.start_worker(f"{worker_type.upper()}Worker")

                coro = self.workers[worker_type].process(
                    TaskRequest(task=task.task, context={"priority": task.priority})
                )
                worker_tasks.append(coro)
                task_mapping[i] = (worker_type, coro)
            else:
                print(f"⚠️  Worker '{worker_type}' não registrado")

        results = await asyncio.gather(*worker_tasks, return_exceptions=True)

        responses = {}
        for i, (worker_type, _) in task_mapping.items():
            result = results[i]
            if isinstance(result, Exception):
                self.logger.end_worker(f"{worker_type.upper()}Worker", 0, "error", str(result))
                print(f"❌ Erro ao executar {worker_type}: {result}")
            else:
                self.logger.end_worker(
                    f"{worker_type.upper()}Worker",
                    result.tokens_used,
                    "success" if result.success else "error",
                    result.error
                )
                responses[f"{worker_type.upper()}"] = result

        return responses

    async def aggregate_results(self, query: str, worker_results: Dict[str, TaskResponse]) -> str:
        """
        Agrega os resultados de todos os workers em uma resposta final coerente.
        """
        results_context = "\n\n".join([
            f"[{worker_name}]:\n{response.result}"
            for worker_name, response in worker_results.items()
        ])

        system_prompt = """Você é o coordenador final de um sistema multi-agente (HIVE Queen).
Sua responsabilidade é agregar e sintetizar os resultados de múltiplos workers especializados
em uma resposta final coerente, bem estruturada e útil ao usuário.

Integre os insights de cada worker de forma lógica e hierárquica."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"""Query original: {query}

Resultados dos workers:
{results_context}

Sintetize uma resposta final que integre todos esses resultados de forma coerente e útil."""
                }
            ]
        )

        final_result = "Erro ao agregar resultados"
        if message.content:
            for block in message.content:
                block_type = getattr(block, 'type', None)
                if block_type == 'text' and hasattr(block, 'text') and block.text:
                    final_result = block.text
                    break

        total_tokens = message.usage.input_tokens + message.usage.output_tokens

        for response in worker_results.values():
            total_tokens += response.tokens_used

        self.logger.log_final_aggregation(final_result, total_tokens)

        return final_result

    async def process_query(self, query: str) -> str:
        """
        Processa uma query complexa através do pipeline HIVE:
        1. Decompõe em subtarefas
        2. Roteia para workers apropriados
        3. Executa em paralelo
        4. Agrega resultados
        """
        print(f"\n🐝 HIVE Queen iniciando processamento...")
        print(f"📋 Query: {query[:100]}...")

        decomposed_tasks = await self.decompose_query(query)
        self.logger.log_queen_decision(query, [t.task for t in decomposed_tasks])

        print(f"\n✂️  Decomposição em {len(decomposed_tasks)} subtarefas:")
        for i, task in enumerate(decomposed_tasks, 1):
            print(f"   {i}. [{task.worker_type}] {task.task[:60]}...")

        print(f"\n⚙️  Executando workers em paralelo...")
        worker_results = await self.execute_workers_parallel(decomposed_tasks)

        print(f"\n🔄 Agregando resultados...")
        final_result = await self.aggregate_results(query, worker_results)

        return final_result
