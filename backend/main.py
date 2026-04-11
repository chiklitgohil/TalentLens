from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import sys
import os
import uuid

# Safely resolve the absolute path to ai_pipeline and prioritize it in the module search path
ai_pipeline_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai_pipeline"))
sys.path.insert(0, ai_pipeline_dir)

from pipeline import run_pipeline, parse_resume_text, match_pipeline
from parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from normalizer import NormalizationAgent

app = FastAPI()

# ✅ Keep CORS (good)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

normalizer = NormalizationAgent()

# --- Database Configuration ---
# Use SQLite for local development (creates a local file automatically instead of needing a full server)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./talentlens.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(String, primary_key=True, index=True)
    profile = Column(JSON)

# Create tables automatically on startup
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MatchRequest(BaseModel):
    candidate_id: str
    job_description: str

@app.get("/api/v1/skills/taxonomy")
async def get_taxonomy():
    return {"taxonomy": normalizer.taxonomy}

@app.post("/api/v1/parse")
async def parse_resume(resume: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_bytes = await resume.read()

        # ✅ safer file type check
        filename = resume.filename.lower()

        if filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_bytes)
        elif filename.endswith(".docx"):
            resume_text = extract_text_from_docx(file_bytes)
        elif filename.endswith(".txt"):
            resume_text = extract_text_from_txt(file_bytes)
        else:
            return {"error": "Only PDF, DOCX, and TXT supported"}

        parsed_data = parse_resume_text(resume_text)
        
        # Save to PostgreSQL database and assign ID
        candidate_id = str(uuid.uuid4())
        db_candidate = Candidate(id=candidate_id, profile=parsed_data)
        db.add(db_candidate)
        db.commit()
        
        return {
            "message": "Resume successfully parsed",
            "candidate_id": candidate_id,
            "profile": parsed_data
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/api/v1/match")
async def match_job(request: MatchRequest, db: Session = Depends(get_db)):
    try:
        db_candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
        if not db_candidate:
            return {"error": "Candidate ID not found"}
            
        parsed_data = db_candidate.profile
        result = match_pipeline(parsed_data, request.job_description)
        return result
    except Exception as e:
        return {"error": str(e)}

# Mount the frontend directory to serve the UI at the root (http://localhost:8000/)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
