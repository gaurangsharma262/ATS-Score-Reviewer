import PyPDF2
import pdfplumber
import docx

def extract_text_from_pdf(file) -> str:
    """Extract text from a PDF file"""
    text = ""
    try:
        # Using pdfplumber for better formatting extraction
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e_plumber:
        try:
            # Fallback to PyPDF2
            file.seek(0)
            reader = PyPDF2.PdfReader(file, strict=False)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e_pypdf:
            raise ValueError(f"Could not extract text from this PDF. Please try using the 'Paste Text' option instead.")
    return text

def extract_text_from_docx(file) -> str:
    """Extract text from a DOCX file"""
    text = ""
    try:
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        pass
    return text

def extract_text(file) -> str:
    """Main extraction function mapping based on file type"""
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    elif file.name.endswith(".txt"):
        return file.getvalue().decode("utf-8")
    else:
        raise ValueError("Unsupported file format")
