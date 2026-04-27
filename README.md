# AI Resume Shortlisting & Interview Assistant

An AI-powered evaluation engine that scores resumes against job descriptions across **4 dimensions** — Exact Match, Semantic Similarity, Achievement/Impact, and Ownership — with full explainability.

## Architecture

```
PDF → pdfplumber (raw text) → Claude (structured JSON) → ResumeData
                                                              ↓
                                              ┌── Exact Match (BM25)
                                              ├── Similarity (SBERT)
                           Orchestrator ──────┤
                                              ├── Achievement (Claude)
                                              └── Ownership (Claude)
                                                              ↓
                                              Composite Score → Tier → Questions
```

## Quick Start

### 1. Setup
```bash
cd resume_shortlister
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Run API Server
```bash
uvicorn main:app --reload --port 8000
```

### 4. Run Streamlit UI
```bash
streamlit run app.py
```

### 5. Run Tests
```bash
pytest tests/ -v
```

## Scoring Dimensions

| Scorer | Strategy | Cost |
|--------|----------|------|
| **Exact Match** | BM25 + token set overlap | Free (local) |
| **Semantic Similarity** | sentence-transformers cosine sim | Free (local, ~50ms) |
| **Achievement** | Claude LLM reasoning | API call |
| **Ownership** | Claude verb-subject analysis | API call |

## Composite Score

```
composite = 0.30 × Exact + 0.25 × Similarity + 0.25 × Achievement + 0.20 × Ownership
```

## Tier Classification

- **Tier A** (≥75): Fast-track to interview
- **Tier B** (50–74): Technical screening required  
- **Tier C** (<50): Needs further evaluation

## Tech Stack

- **Python 3.11+** / FastAPI / Streamlit
- **Anthropic Claude** for structured parsing + LLM scoring
- **sentence-transformers** for embedding-based similarity
- **rank-bm25** for keyword matching
- **Pydantic v2** for data validation + explainability enforcement
