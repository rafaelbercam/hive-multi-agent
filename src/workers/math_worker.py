from anthropic import Anthropic
from src.agents.base import BaseAgent, TaskRequest, TaskResponse

class MathWorker(BaseAgent):
    """
    Math Agent: Cálculos, análises numéricas e validação matemática.
    Especializado em operações matemáticas complexas e verificação de precisão.
    """

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        super().__init__("MathWorker", model, api_key)
        self.client = Anthropic(api_key=api_key)

    async def process(self, request: TaskRequest) -> TaskResponse:
        try:
            system_prompt = """Você é um especialista em matemática e análise numérica.
Sua tarefa é realizar cálculos, validar operações matemáticas e fornecer análises numéricas detalhadas.
Mostre todos os passos do cálculo de forma clara.
Use notação matemática apropriada quando necessário."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Realize a análise matemática: {request.task}"
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
