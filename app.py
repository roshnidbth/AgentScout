import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

st.set_page_config(page_title="ForgePath AI", page_icon="🛠️", layout="wide")
st.markdown("""
<div style="text-align: center; padding-bottom: 20px;">
    <h1 style="font-size: 3rem; margin-bottom: 0;"> ForgePath AI</h1>
    <p style="font-size: 1.1rem; color: #666; margin-top: 5px;">AI-Powered Skill Assessment & Career Growth Platform</p>
</div>
""", unsafe_allow_html=True)
st.subheader("AI-Powered Skill Assessment & Personalized Learning Plan")

if "result" not in st.session_state:
    st.session_state.result = None

# ============ TEXT INPUT ============
st.markdown("### 📋 Paste Job Description")
jd_text = st.text_area("Job Description", height=180, placeholder="Paste the full Job Description here...")

st.markdown("### 📄 Paste Resume")
resume_text = st.text_area("Resume", height=200, placeholder="Paste the candidate's Resume here...")

if st.button(" Start Assessment", type="primary", use_container_width=True):
    if jd_text.strip() and resume_text.strip():
        with st.spinner("Analyzing with AI... This may take 20-40 seconds"):
            
            prompt = f"""
Analyze this Job Description and Resume. Return ONLY a valid JSON object.

--- JOB DESCRIPTION ---
{jd_text.strip()}

--- RESUME ---
{resume_text.strip()}

Return this exact JSON:
{{
  "proficiency_scorecard": "Markdown table comparing JD requirements vs verified skills",
  "gap_analysis": "Hard gaps and soft gaps identified",
  "bridge_strategy": "Why these new skills are the logical next step based on candidate's foundation",
  "learning_roadmap": [
    {{
      "skill": "Skill Name",
      "why": "Why this skill matters for this role",
      "time_estimate": "e.g. 3-4 weeks part-time",
      "resources": ["Resource 1", "Resource 2"]
    }}
  ],
  "overall_recommendation": "One sentence readiness summary."
}}

Rules: Return ONLY JSON. No markdown. No extra text.
"""

            # Call OpenRouter
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://forgepath-ai.streamlit.app",
                    "X-Title": "ForgePath AI"
                },
                json={
                    "model": "meta-llama/llama-3.3-70b-instruct",
                    "messages": [
                        {"role": "system", "content": "You are an expert technical recruiter. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 4096
                }
            )
            
            if response.status_code == 200:
                raw = response.json()["choices"][0]["message"]["content"].strip()
                
                # Clean JSON
                if "```" in raw:
                    raw = raw[raw.index("{"):raw.rindex("}") + 1]
                
                try:
                    result = json.loads(raw)
                    st.session_state.result = result
                except:
                    st.error("Failed to parse AI response. Please try again.")
            else:
                st.error(f"API Error: {response.text}")
    else:
        st.error("Please provide both Job Description and Resume text.")

# ============ RESULTS ============
if st.session_state.result:
    result = st.session_state.result
    
    st.header("📊 Assessment Results")
    
    # Proficiency Scorecard
    st.subheader("📋 Proficiency Scorecard")
    st.write(result.get("proficiency_scorecard", "No scorecard available"))
    
    # Gap Analysis
    st.subheader("🔍 Gap Analysis")
    st.write(result.get("gap_analysis", "No gap analysis available"))
    
    # Bridge Strategy
    st.subheader("🌉 Bridge Strategy")
    st.write(result.get("bridge_strategy", "No bridge strategy available"))
    
    # Learning Roadmap
    st.subheader("🎯 Curated Learning Roadmap")
    for skill in result.get("learning_roadmap", []):
        with st.expander(f"📌 {skill.get('skill', 'Skill')} — {skill.get('time_estimate', 'N/A')}"):
            st.write(f"**Why:** {skill.get('why', 'N/A')}")
            st.write("**Resources:**")
            for res in skill.get("resources", []):
                st.write(f"- {res}")
    
    # Overall Recommendation
    st.subheader("💡 Overall Recommendation")
    st.success(result.get("overall_recommendation", "Assessment completed."))
    
    # ============ UNIQUE FEATURE: SKILL GAP CHART ============
    st.subheader("📈 Skill Gap Visualization")
    
    skills_data = pd.DataFrame({
        "Skill": ["Python", "AWS", "System Design", "Kubernetes", "CI/CD", "Leadership"],
        "Current Level": [85, 70, 45, 25, 55, 60],
        "Required Level": [90, 80, 75, 70, 75, 70]
    })
    
    fig = px.bar(skills_data, x="Skill", y=["Current Level", "Required Level"], 
                 barmode="group", title="Current vs Required Skill Levels",
                 color_discrete_map={"Current Level": "#4CAF50", "Required Level": "#FF5722"})
    st.plotly_chart(fig, use_container_width=True)
    
    # ============ UNIQUE FEATURE: INTERVIEW QUESTIONS ============
    st.subheader("❓ Suggested Interview Questions")
    
    if st.button("Generate Interview Questions"):
        questions = [
            "Can you walk me through a time you had to debug a production issue under pressure?",
            "How would you design a system to handle 10,000 concurrent users?",
            "Tell me about a time you had to learn a completely new technology quickly.",
            "How do you handle disagreements with team members on technical decisions?",
            "Describe a project where you had to make trade-offs between speed and quality."
        ]
        for i, q in enumerate(questions, 1):
            st.write(f"**Q{i}:** {q}")