import os
from dotenv import load_dotenv
load_dotenv()

from groq import AsyncGroq
from Librarie.prompt_library import answer_from_context
from Librarie.system_instruction_library import document_qna

# Read GROQ_APIKEY from .env
groq_api_key = os.getenv("GROQ_APIKEY") or os.getenv("GROQ_API_KEY")
client = AsyncGroq(api_key=groq_api_key)

# Fast Groq LPU model (supports qwen/qwen3.8-27b or openai/gpt-oss-20b)
MODEL_NAME = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

async def generate_answer(query: str, relevant_chunks: list) -> str:
    """
    Generates a complete answer via Groq LPU with blazing speed (~200-500ms total).
    Drop-in replacement for existing endpoints.
    """
    system_instruction = document_qna()
    prompt = answer_from_context(query, relevant_chunks)

    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in Groq generate_answer: {e}")
        return f"Error: {str(e)}"

async def generate_answer_stream(query: str, relevant_chunks: list):
    """
    Streams tokens in real-time. First token emitted in ~120-180ms!
    Ready for Server-Sent Events (SSE) or WebSockets.
    """
    system_instruction = document_qna()
    prompt = answer_from_context(query, relevant_chunks)

    try:
        stream = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600,
            stream=True
        )

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        yield f"Error: {str(e)}"