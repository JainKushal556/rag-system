from dotenv import load_dotenv
load_dotenv()
from Query_Pipeline.query_embedder import generate_query_embeddings
from Query_Pipeline.chunk_retriver import chunk_retriver
from Query_Pipeline.llm_answer import generate_answer
import asyncio


query = input("Enter your query: ")
generated_query_embedding = generate_query_embeddings(query)
retrived_chunks = chunk_retriver(generated_query_embedding)
generated_answer = asyncio.run(generate_answer(query, retrived_chunks))
print(f"Answer: {generated_answer}")


#  python -m Query_Pipeline.main