from dotenv import load_dotenv
load_dotenv() 
from pathlib import Path
from Ingestion_Pipeline.textloader import filetotext
from Ingestion_Pipeline.chunking import chunker




if __name__ == "__main__":


    pdf = Path("Resources/RAG_Intern_Learning_Plan_Updated.pdf")
    # pdf = Path("DataSet.pdf")
    filetotext(pdf)



    with open("TextConvertedData/pdftext.txt", 'r') as f:
        text_content = f.read()
        chunker(text_content)



    # with open("splitedtext.json", 'r') as f:
    #     data = json.load(f)
    #     print(len(data[0]["embedding"]))


# python -m Ingestion_Pipeline.main