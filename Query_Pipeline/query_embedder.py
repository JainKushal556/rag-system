
from google import genai
from google.genai import types
import os
import asyncio


async def generate_query_embeddings(query : str):
    client= genai.Client(api_key=os.getenv("GEMINIAPI_KEY"))
    try:
        result = await client.aio.models.embed_content(
            model="gemini-embedding-001",
            contents=[query],
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY",output_dimensionality=1536)
        )
        return result.embeddings[0].values
    except Exception as e:
        print(f"Error generating embeddings for query: {e}")
        raise e
