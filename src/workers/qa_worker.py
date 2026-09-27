from anthropic import Anthropic
from src.agents.base import BaseAgent, TaskRequest, TaskResponse

class QAWorker(BaseAgent):
    """
    QA Agent: Validação, verificação e refinamento de qualidade.
    Especializado em testes, validação e garantia de qualidade.
    """

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        super().__init__("QAWorker", model, api_key)
        self.client = Anthropic(api_key=api_key)

    async def process(self, request: TaskRequest) -> TaskResponse:
        try:
            system_prompt = """Você é um especialista em garantia de qualidade e validação.
Sua tarefa é revisar, validar e melhorar o conteúdo fornecido.
Identifique potenciais problemas, erros ou áreas de melhoria.
Forneça feedback construtivo e sugestões de refinamento.
Verifique completude, precisão e coerência."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Valide e revise: {request.task}"
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
