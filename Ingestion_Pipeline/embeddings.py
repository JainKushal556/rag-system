from google import genai
from google.genai import types
import os
import time
import asyncio


client= genai.Client(api_key=os.getenv("GEMINIAPI_KEY"))

async def generate_embeddings(text : list):
    print("Entered..")
    st = time.time()
    all_embeddings = []
    for i in range(0, len(text), 100):
            try:
                start = i
                end = min(i+100, len(text))
                batch = text[start:end]
                result = await client.aio.models.embed_content(
                    model="gemini-embedding-001",
                    contents=batch,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT",output_dimensionality=1536)
                )
                # result = await client.aio.models.embed_content(
                #     model="gemini-embedding-001",
                #     contents=batch[0],
                #     config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT",output_dimensionality=1536)
                # )
                # print(result)
                # return 
            except Exception as e:
                print(f"Error generating embeddings for chunk {i//100 + 1}: {e}")
                raise e
            else:
                all_embeddings.extend(result.embeddings)
                if i + 100 < len(text): 
                    await asyncio.sleep(60)
    end = time.time()
    print(f"Time taken to generate embeddings: {end - st} seconds")
    print("Embedding Done...")
    return all_embeddings

# [10,20,120]