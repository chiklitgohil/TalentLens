pip install google-generativeai
pip install fastapi uvicorn python-multipart pymupdf sentence-transformers python-dotenv python-docx
export GOOGLE_API_KEY="your_api_key_here"
uvicorn main:app --reload
