"""
Debug detalhado da resposta da API
"""

import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

print("🔍 Testando estrutura completa da resposta...\n")

message = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=500,
    system="Você é um assistente que retorna JSON.",
    messages=[
        {
            "role": "user",
            "content": 'Retorne um JSON simples: {"test": "value"}'
        }
    ]
)

print("📋 Estrutura completa:")
print(f"Type: {type(message)}")
print(f"Stop reason: {message.stop_reason}")
print(f"Content length: {len(message.content)}")
print(f"Content type: {type(message.content)}")
print()

print("📦 Content[0]:")
if message.content:
    content_0 = message.content[0]
    print(f"  Type: {type(content_0)}")
    print(f"  Dir: {[x for x in dir(content_0) if not x.startswith('_')]}")
    print(f"  Text attr exists: {hasattr(content_0, 'text')}")
    if hasattr(content_0, 'text'):
        print(f"  Text value: {repr(content_0.text)}")
        print(f"  Text is None: {content_0.text is None}")
        print(f"  Text length: {len(content_0.text) if content_0.text else 0}")
    print()

    # Tenta acessar como dict
    print("  Como dict:")
    try:
        print(f"    {dict(content_0)}")
    except:
        print(f"    Não é dict")

    # Tenta conversão JSON
    print()
    print(f"  JSON str: {json.dumps(content_0.__dict__)}")
else:
    print("  ⚠️  Content está VAZIO!")

print()
print("📊 Tokens:")
print(f"  Input: {message.usage.input_tokens}")
print(f"  Output: {message.usage.output_tokens}")
print(f"  Total: {message.usage.input_tokens + message.usage.output_tokens}")
