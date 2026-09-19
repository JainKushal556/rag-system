import asyncio
import time
import sys
from dotenv import load_dotenv
load_dotenv()

from Query_Pipeline.query_embedder import generate_query_embeddings
from Query_Pipeline.chunk_retriver import chunk_retriver
from Query_Pipeline.llm_answer import generate_answer_stream

async def main():
    print("📞 [Call Connected: CarePlus Multispeciality Clinic]")
    print("Type 'exit' or 'quit' to end the call.\n")
    
    # Stores the back-and-forth dialogue history of the call
    chat_history = []

    while True:
        try:
            query = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n[Call Disconnected]")
            break

        if not query:
            continue
        if query.lower() in ["exit", "quit", "bye"]:
            print("\nAssistant: Thank you for calling CarePlus. Have a wonderful day!")
            print("[Call Ended]")
            break

        t_start = time.time()

        # 1. Retrieval
        query_embedding = await generate_query_embeddings(query)
        retrieved_chunks = chunk_retriver(query_embedding)

        # 2. Streaming Response
        sys.stdout.write("Receptionist: ")
        sys.stdout.flush()

        full_response = ""
        ttft = 0
        first_token = True

        async for token in generate_answer_stream(query, retrieved_chunks, chat_history):
            if first_token:
                ttft = round((time.time() - t_start) * 1000)
                first_token = False
            sys.stdout.write(token)
            sys.stdout.flush()
            full_response += token

        total_time = round((time.time() - t_start), 2)
        print(f"\n({total_time}s | First word: {ttft}ms)\n")

        # 3. Save to Conversation History (remembers previous questions)
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": full_response})

        # Keep history within reasonable window (last 8 turns) to save tokens
        if len(chat_history) > 8:
            chat_history = chat_history[-8:]

if __name__ == "__main__":
    asyncio.run(main())

# python -m Query_Pipeline.main
