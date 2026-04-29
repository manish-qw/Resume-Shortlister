# AI Resume Shortlisting & Interview Assistant

**Live Application:** [https://resume-shortlister-gkx8dboehlm8qwkftrstrq.streamlit.app/](https://resume-shortlister-gkx8dboehlm8qwkftrstrq.streamlit.app/)

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
# Edit .env and add your API keys
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
| **Achievement** | Gemini LLM reasoning | API call |
| **Ownership** | Gemini verb-subject analysis | API call |

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
- **LLM API** for structured parsing + LLM scoring
- **sentence-transformers** for embedding-based similarity
- **rank-bm25** for keyword matching
- **Pydantic v2** for data validation + explainability enforcement

---

## Further Scope & Roadmap

- **Claim Verification Engine**: Verify public claims to dynamically adjust scores based on real-world evidence.
  - *GitHub*: Use the REST API to check commit frequency, language breakdown, and repository authenticity.
  - *LinkedIn*: Scrape public profiles (via `httpx` + BeautifulSoup) to cross-reference claimed job titles and durations.
- **Intelligent Question Generation**: Use identified evaluation gaps to construct highly personalized interview questions.
  - *Example*: If a candidate knows RabbitMQ but the JD needs Kafka, ask them how they would migrate between the two.
  - *Strategy*: Tailor question types by Tier (e.g., architecture questions for Tier A, foundational gap probes for Tier C).
- **Batch Processing at Scale**: Process thousands of resumes concurrently without hitting LLM rate limits.
  - *Architecture*: Implement a Celery/Redis task queue where FastAPI returns a `job_id` for frontend polling.
  - *Cost Savings*: Add a fast-path local pre-filter (Exact Match) to auto-reject fundamentally unqualified resumes before they trigger expensive LLM API calls.
- **Persistent Storage & Analytics**: 
  - *Database*: Swap the in-memory dictionary for a PostgreSQL database using SQLAlchemy.
  - *Dashboard*: Add Streamlit/Plotly visualizations for recruiters to track score distributions, JD realism, and hiring pipeline health.
- **Self-Calibrating Feedback Loop**: 
  - *Process*: Collect recruiter interview outcomes (Hired/Rejected) to create a labeled dataset.
  - *Optimization*: Use this data to automatically recalibrate composite scorer weights and tier thresholds, turning the system into a self-learning pipeline.

---

<p align="center">
  Built with ❤️ for better hiring.
</p>
