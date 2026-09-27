from anthropic import Anthropic
from src.agents.base import BaseAgent, TaskRequest, TaskResponse

class RAGWorker(BaseAgent):
    """
    RAG Agent: Busca, síntese e recuperação de informações.
    Especializado em pesquisa e compilação de conhecimento.
    """

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        super().__init__("RAGWorker", model, api_key)
        self.client = Anthropic(api_key=api_key)

    async def process(self, request: TaskRequest) -> TaskResponse:
        try:
            system_prompt = """Você é um especialista em busca e síntese de informações (RAG).
Sua tarefa é pesquisar, compilar e resumir informações relevantes sobre o tópico solicitado.
Forneça informações precisas, estruturadas e bem organizadas.
Cite fontes quando apropriado."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Pesquise e resuma informações sobre: {request.task}"
                    }
                ]
            )

            result = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens

            return TaskResponse(
                result=result,
                tokens_used=tokens_used,
                worker_name=self.name,
                success=True
            )
        except Exception as e:
            return TaskResponse(
                result="",
                tokens_used=0,
                worker_name=self.name,
                success=False,
                error=str(e)
            )
