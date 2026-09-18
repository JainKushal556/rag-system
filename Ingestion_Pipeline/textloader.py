from importlib.resources import path
from pypdf import PdfReader
from pathlib import Path



def filetotext(PATH : Path):
    PATH = Path(PATH)
    
    output_dir = Path("TextConvertedData")
    output_dir.mkdir(exist_ok=True)
    
    if PATH.suffix == ".pdf":
        pdf = PdfReader(PATH)
        path = output_dir / "extracted_text.txt"
        with open(path,'w',encoding="utf-8")as txtfile:
            for page in pdf.pages:
                txtfile.write(page.extract_text())
        return True
    elif PATH.suffix == ".txt":
        with open(PATH,'r',encoding="utf-8") as sourcefile:
            path = output_dir / "extracted_text.txt"
            with open(path,'w',encoding="utf-8") as destinationfile:
                destinationfile.write(sourcefile.read())
            return True
            
    