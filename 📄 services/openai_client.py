from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def gerar_resposta(mensagem_usuario):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
Você é a Alici — Artificial Extreme Intelligence.
Uma IA futurista, extremamente inteligente, rápida e estratégica.
Responda de forma clara, útil e profissional.
"""
            },
            {
                "role": "user",
                "content": mensagem_usuario
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content
