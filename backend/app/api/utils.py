from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader
from io import BytesIO

router = APIRouter()

@router.post("/extract-text")
async def extract_text_from_file(file: UploadFile = File(...)):
    """
    Extrae texto plano de archivos PDF o de texto.
    Soporta: .pdf, .txt, .md, .csv, .json, .log
    """
    try:
        content_type = file.content_type
        filename = file.filename.lower()
        
        # 1. Procesamiento de PDF
        if filename.endswith(".pdf") or content_type == "application/pdf":
            try:
                content = await file.read()
                pdf_file = BytesIO(content)
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return {"text": text, "filename": file.filename, "type": "pdf"}
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error leyendo PDF: {str(e)}")

        # 2. Procesamiento de Texto Plano
        else:
            try:
                content = await file.read()
                # Intentar decodificar como utf-8
                text = content.decode("utf-8")
                return {"text": text, "filename": file.filename, "type": "text"}
            except UnicodeDecodeError:
                # Fallback a latin-1 si utf-8 falla
                text = content.decode("latin-1")
                return {"text": text, "filename": file.filename, "type": "text"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")
