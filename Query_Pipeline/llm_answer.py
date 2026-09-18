from Librarie.prompt_library import answer_from_context
from Librarie.system_instruction_library import document_qna
from google import genai
import os


client = genai.Client(api_key=os.getenv("GEMINIAPI_KEY"))
model_name = "gemini-3.5-flash-lite"
previous_id = None

# It Keeps Track Of Previous Chats 
async def generate_answer(query, relevant_chunks):
    global previous_id
    global model_name
    systemInstruction = document_qna()
    prompt = answer_from_context(query, relevant_chunks)
    print(f"Prompt:\n {prompt}")
    if previous_id is None:
        try:
            response1 =await client.aio.interactions.create(
                model=model_name,
                input=prompt,
                generation_config={
                    "temperature" : 0.6
                },
                system_instruction = systemInstruction
            )
        except Exception as e:
            return {"Error": str(e)}
        else:
            previous_id = response1.id
            return response1.output_text
    else:
        try:
            response2 = await client.aio.interactions.create(
                model=model_name,
                input=prompt,
                generation_config={
                    "temperature" : 0.6
                },
                system_instruction=systemInstruction,          
                previous_interaction_id= previous_id
            )
        except Exception as e:
            return {"Error": str(e)}
        else:
            previous_id = response2.id
            return response2.output_text