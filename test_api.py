"""
Script de teste para validar API key e resposta
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ API KEY não encontrada")
    exit(1)

print(f"✅ API Key encontrada: {api_key[:20]}...")

client = Anthropic(api_key=api_key)

print("\n🧪 Testando chamada simples...")

try:
    message = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Responda com: FUNCIONANDO"
            }
        ]
    )

    print(f"✅ Status: {message.stop_reason}")
    print(f"✅ Conteúdo: {message.content}")
    print(f"✅ Texto: {message.content[0].text if message.content else 'VAZIO'}")
    print(f"✅ Tokens: {message.usage.input_tokens + message.usage.output_tokens}")

except Exception as e:
    print(f"❌ Erro: {type(e).__name__}: {e}")
    print(f"\nDicas:")
    print("1. API key é válida?")
    print("2. Conexão de internet ativa?")
    print("3. Rate limit não foi atingido?")
    print("4. Modelo 'claude-opus-5-5' está disponível?")
