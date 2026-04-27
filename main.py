from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import ValidationError
import uuid

from models import EvaluationResponse, JobDescription
from parser.pdf_extractor import extract_text
from parser.resume_parser import parse_resume, parse_job_description
from scoring.orchestrator import evaluate

app = FastAPI(title="AI Resume Shortlister API")

# In-memory cache for simplicity
job_cache = {}

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_resume(
    pdf_file: UploadFile = File(...),
    jd_text: str = Form(...)
):
    try:
        # 1. Parse JD
        jd = parse_job_description(jd_text)
        
        # 2. Extract and Parse Resume
        pdf_path = f"temp_{uuid.uuid4().hex}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(await pdf_file.read())
            
        resume_raw = extract_text(pdf_path)
        import os
        os.remove(pdf_path) # Clean up
        
        if not resume_raw:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
            
        resume = parse_resume(resume_raw)
        
        # 3. Orchestrate Evaluation
        result = await evaluate(resume, jd)
        
        # 4. Cache and Return
        job_id = uuid.uuid4().hex
        job_cache[job_id] = result
        
        return EvaluationResponse(
            job_id=job_id,
            status="completed",
            result=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results/{job_id}", response_model=EvaluationResponse)
async def get_results(job_id: str):
    if job_id not in job_cache:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return EvaluationResponse(
        job_id=job_id,
        status="completed",
        result=job_cache[job_id]
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}
