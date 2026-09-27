"""
Teste da função decompose_query
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

query = "Crie um script Python que calcula juros compostos, faça uma busca sobre histórico de taxas de juros, e valide se o código está correto."

print("🔍 Testando decompose_query...\n")

system_prompt = """Você é o coordenador de um sistema multi-agente (HIVE Queen).
Sua responsabilidade é decompor queries complexas em subtarefas específicas.

Tipos de workers disponíveis:
1. RAG: Busca, pesquisa e síntese de informações
2. Math: Cálculos, análises numéricas e validação matemática
3. Code: Geração, debugging e otimização de código
4. QA: Validação, verificação de qualidade e refinement

Analise a query e decomponha em subtarefas. Para cada subtarefa, especifique:
- worker_type: qual worker deve executar
- task: descrição clara da subtarefa
- priority: prioridade (1=alta, 2=média, 3=baixa)

Retorne um JSON array com as subtarefas."""

message = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=2048,
    system=system_prompt,
    messages=[
        {
            "role": "user",
            "content": f"Decomponha esta query complexa em subtarefas:\n\n{query}"
        }
    ]
)

print("📊 Resposta recebida:")
print(f"  Stop reason: {message.stop_reason}")
print(f"  Content length: {len(message.content)}")
print(f"  Tokens: {message.usage.input_tokens + message.usage.output_tokens}")
print()

print("📝 Tipos de conteúdo:")
for i, block in enumerate(message.content):
    print(f"  [{i}] {type(block).__name__}")
print()

text = None
if message.content:
    for i, block in enumerate(message.content):
        if hasattr(block, 'text'):
            text = block.text
            print(f"✅ TextBlock encontrado no index {i}")
            break

if text:
    print(f"  Length: {len(text)} chars")
    print()
    print("📄 Conteúdo:")
    print("  " + "="*70)
    print(text[:800])
    print("  " + "="*70)
else:
    print("❌ Nenhum TextBlock encontrado!")
    print()
    print("Conteúdo bruto:")
    for block in message.content:
        print(f"  {block}")
