import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

# Persistent Gemini client (connection pooled)
client = genai.Client(api_key=os.getenv("GEMINIAPI_KEY"))

# IN-MEMORY VECTOR CACHE (RAM)
# Key: normalized lower-case query -> Value: 1536-dimensional vector list
EMBEDDING_CACHE = {}

async def generate_query_embeddings(query: str):
    clean_query = query.strip().lower()

    # 1. Instant Cache Check (RAM retrieval in 0.001 ms)
    if clean_query in EMBEDDING_CACHE:
        return EMBEDDING_CACHE[clean_query]

    # 2. If not cached, fetch from Gemini API
    try:
        result = await client.aio.models.embed_content(
            model="gemini-embedding-001",
            contents=[query],
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY", output_dimensionality=1536)
        )
        vector = result.embeddings[0].values
        
        # 3. Store in RAM for instant future lookups
        EMBEDDING_CACHE[clean_query] = vector
        return vector

    except Exception as e:
        print(f"Error generating embeddings for query: {e}")
        raise e
