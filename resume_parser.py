import PyPDF2

def extract_resume(file_content):
    """
    Extracts text from the uploaded file content.
    """
    try:
        reader = PyPDF2.PdfReader(file_content)
        resume_text = ""
        for page in reader.pages:
            resume_text += page.extract_text()
        return resume_text
    except Exception as e:
        return f"Error reading file: {e}"