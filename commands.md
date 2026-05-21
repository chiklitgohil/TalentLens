# commands.md

## Install Required Packages

```bash
pip install sentence-transformers chromadb numpy python-dotenv google-genai PyMuPDF python-docx google-generativeai fastapi uvicorn pydantic sqlalchemy
```

## Run testing files

```bash
python -m testing.test_parser.py
python -m testing.test_normalizer.py
python -m testing.test_matcher.py
```

## Run FastAPI Server in main.py

```bash
uvicorn backend.main:app --reload
```

## Open API in browser

```text
http://127.0.0.1:8000
```
