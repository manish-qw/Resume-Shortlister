import streamlit as st
import asyncio
from models import JobDescription
from parser.pdf_extractor import extract_text
from parser.resume_parser import parse_resume, parse_job_description
from scoring.orchestrator import evaluate
import tempfile
import os

st.set_page_config(page_title="AI Resume Shortlister", layout="wide")

st.title("AI Resume Shortlister & Interview Assistant")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Job Description")
    jd_text = st.text_area("Paste the Job Description here", height=300)

with col2:
    st.subheader("Candidate Resume")
    uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

if st.button("Evaluate Candidate", type="primary"):
    if not jd_text or not uploaded_file:
        st.warning("Please provide both a JD and a Resume.")
    else:
        with st.spinner("Analyzing candidate profile across 4 dimensions..."):
            try:
                # Save PDF temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                resume_raw = extract_text(tmp_path)
                os.remove(tmp_path)

                if not resume_raw:
                    st.error("Failed to extract text from PDF.")
                    st.stop()

                jd = parse_job_description(jd_text)
                resume = parse_resume(resume_raw)

                result = asyncio.run(evaluate(resume, jd))

                st.success("Evaluation Complete!")

                # Tier Badge
                tier_colors = {"A": "green", "B": "orange", "C": "red"}
                st.markdown(f"### Classification: :**{tier_colors[result.tier]}[Tier {result.tier}]** (Composite Score: {result.composite})")
                st.write(result.overall_reasoning)

                st.divider()

                # Detailed Scores
                st.subheader("Dimensional Analysis")
                cols = st.columns(len(result.scores))
                
                for idx, (scorer_name, score_result) in enumerate(result.scores.items()):
                    with cols[idx]:
                        st.metric(label=scorer_name.replace("_", " ").title(), value=f"{score_result.score:.1f}/100")
                        with st.expander("View Evidence"):
                            st.write("**Reasoning:**", score_result.reasoning)
                            st.write("**Evidence:**")
                            for ev in score_result.evidence:
                                st.write(f"- {ev}")
                            if score_result.gaps:
                                st.write("**Gaps:**")
                                for gap in score_result.gaps:
                                    st.write(f"- {gap}")
                            if score_result.analogous_pairs:
                                st.write("**Analogous Skills:**")
                                for pair in score_result.analogous_pairs:
                                    st.write(f"- {pair.resume_skill} ≈ {pair.jd_skill} ({pair.similarity*100:.0f}%)")

                st.divider()

                # Interview Questions
                st.subheader("Tailored Interview Questions")
                for q in result.questions:
                    st.markdown(f"- {q}")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
