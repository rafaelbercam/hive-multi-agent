from anthropic import Anthropic
from src.agents.base import BaseAgent, TaskRequest, TaskResponse

class CodeWorker(BaseAgent):
    """
    Code Agent: Geração, otimização e debugging de código.
    Especializado em programação em múltiplas linguagens.
    """

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        super().__init__("CodeWorker", model, api_key)
        self.client = Anthropic(api_key=api_key)

    async def process(self, request: TaskRequest) -> TaskResponse:
        try:
            system_prompt = """Você é um especialista em desenvolvimento de software.
Sua tarefa é gerar, otimizar, debugar e melhorar código.
Forneça código limpo, bem estruturado e comentado quando necessário.
Considere performance, legibilidade e boas práticas de programação.
Sempre inclua exemplos de uso quando apropriado."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Trabalhe com código: {request.task}"
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
