from dotenv import load_dotenv
load_dotenv() 
import asyncio
from pathlib import Path
from Ingestion_Pipeline.textloader import filetotext
from Ingestion_Pipeline.chunking import chunker




if __name__ == "__main__":


    pdf = Path("AI_Receptionist_Doctor_Clinic_Data.pdf")
    # pdf = Path("DataSet.pdf")
    filetotext(pdf)




    asyncio.run(chunker())



    # with open("splitedtext.json", 'r') as f:
    #     data = json.load(f)
    #     print(len(data[0]["embedding"]))


# python -m Ingestion_Pipeline.main