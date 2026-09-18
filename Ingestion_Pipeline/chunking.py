from pydantic import BaseModel , Field
from Ingestion_Pipeline.embeddings import generate_embeddings
from Ingestion_Pipeline.vectore_store import insert_inpgvector
import asyncio
from pathlib import Path


# class chunk(BaseModel):
#     content: str = Field(max_length=30)

chunk_size = 600
overlap = 100
async def chunker():

    with open("TextConvertedData/extracted_text.txt", 'r', encoding="utf-8") as f:
        text = f.read()
    text_structure = []
    text_content= chunk_generate(text)

    for i,texts in enumerate(text_content):
        dic = {
            "No." : i+1,
            "content" : texts
        }
        text_structure.append(dic)

    all_embeddings =await generate_embeddings(text_content)

    for i, embedding in enumerate(all_embeddings):
        text_structure[i]["embedding"] = embedding.values
    insert_inpgvector(text_structure)
    # with open("splitedtext(1536).json",'w') as f:
    #     json.dump(text_structure, f, indent=4, ensure_ascii=False)


def chunk_generate(text: str):
    chunck = []
    i = 0
    
    while i < len(text):
        
        if i + chunk_size >= len(text):
            chunck.append(text[i:])
            break

        trimed_chunk = text[i : i + chunk_size]
        endline = trimed_chunk.rfind('.')

        
        if endline != -1 and endline > overlap:   
            trimed_chunk = trimed_chunk[:endline + 1]
            chunck.append(trimed_chunk)
            i += (endline + 1) - overlap
        else:
            chunck.append(trimed_chunk)
            i += chunk_size - overlap

    return chunck





    # def chunk_generate(text:str):
#     chunck = []
#     i=0
#     while i < len(text):
#         trimed_chunk=  text[i:i + chunk_size]
#         endline = trimed_chunk.rfind('.')
#         if endline != -1:   
#             trimed_chunk = trimed_chunk[:endline+1]
#             chunck.append(trimed_chunk)
#             i += endline+1-50
#         else:
#             chunck.append(trimed_chunk)
#             i += chunk_size-50
#     return chunck