import asyncio
import time
import sys
from dotenv import load_dotenv
load_dotenv()

from Query_Pipeline.query_embedder import generate_query_embeddings
from Query_Pipeline.chunk_retriver import chunk_retriver
from Query_Pipeline.llm_answer import generate_answer_stream

async def main():
    query = input("\n💬 Enter your query: ").strip()
    if not query:
        print("Query cannot be empty!")
        return

    print("\n🔍 Generating embedding & searching database...")
    t_start = time.time()
    
    # 1. Generate query embedding
    query_embedding = await generate_query_embeddings(query)
    
    # 2. Retrieve relevant chunks from PostgreSQL pgvector
    retrieved_chunks = chunk_retriver(query_embedding)
    t_retrieved = time.time()
    
    print(f"✅ Context retrieved in {round((t_retrieved - t_start) * 1000)}ms.")
    print("=" * 60)
    print("⚡ [Live Groq Streaming Answer]:\n")

    # 3. Stream Groq LPU response live to terminal
    ttft = 0
    first_token = True
    async for token in generate_answer_stream(query, retrieved_chunks):
        if first_token:
            ttft = round((time.time() - t_start) * 1000)
            first_token = False
        sys.stdout.write(token)
        sys.stdout.flush()

    print("\n" + "=" * 60)
    total_time = round((time.time() - t_start), 3)
    print(f"⏱️ Time To First Token (TTFT): {ttft}ms | Total Pipeline Time: {total_time}s\n")

if __name__ == "__main__":
    asyncio.run(main())