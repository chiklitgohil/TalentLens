import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes):
    text = ""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text


def simple_extract_fields(text):
    # VERY basic (we'll upgrade later)
    lines = text.split("\n")

    skills = []
    for line in lines:
        if "python" in line.lower():
            skills.append("Python")
        if "react" in line.lower():
            skills.append("React")
        if "machine learning" in line.lower():
            skills.append("Machine Learning")

    return {
        "name": lines[0] if lines else "Unknown",
        "skills": list(set(skills))
    }