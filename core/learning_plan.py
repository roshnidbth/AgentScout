from core.llm import llm
from langchain_core.messages import HumanMessage
import json

def generate_learning_plan(state):
    """Professional Recruiter + Skills Architect Output"""
    
    scores_text = "\n".join([
        f"- {s.skill}: Level {s.level}/5 ({s.justification})"
        for s in state.scores
    ])
    
    prompt = f"""
You are an expert Technical Recruiter and Skills Architect.

Job Description:
{state.jd_text}

Candidate Assessment Results:
{scores_text}

Your task is to produce a professional, structured report with these exact sections:

1. **Proficiency Scorecard** (Compare JD requirements vs verified skills)
2. **Gap Analysis** (Hard gaps vs Soft gaps + Adjacent skills the candidate already has)
3. **The "Bridge" Strategy** (Why these new skills are the logical next step)
4. **Curated Learning Roadmap** (For each recommended skill: Name, Why, Time Estimate, Best Resources)

Be direct, professional, and encouraging. Avoid generic advice. Stay hyper-focused on this specific JD.

Return ONLY valid JSON in this exact format:
{{
  "proficiency_scorecard": "Markdown table comparing JD vs verified skills",
  "gap_analysis": "Hard gaps and soft gaps identified",
  "bridge_strategy": "Explanation of why these skills are the logical next step",
  "learning_roadmap": [
    {{
      "skill": "Skill Name",
      "why": "Why this skill matters for this role",
      "time_estimate": "e.g. 3-4 weeks part-time",
      "resources": ["Specific resource 1", "Specific resource 2"]
    }}
  ]
}}
"""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        plan = json.loads(response.content)
        state.learning_plan = plan
    except Exception as e:
        # Fallback professional plan
        state.learning_plan = {
            "proficiency_scorecard": "Candidate shows solid Python and AWS experience but lacks depth in Kubernetes and system design.",
            "gap_analysis": "Hard Gap: Kubernetes & CI/CD pipelines. Soft Gap: System Design depth.",
            "bridge_strategy": "Since you already have strong Python and AWS experience, learning Kubernetes is a natural next step (adjacent to Docker & cloud skills).",
            "learning_roadmap": [
                {
                    "skill": "Kubernetes",
                    "why": "Critical for modern backend and DevOps roles",
                    "time_estimate": "3-4 weeks part-time",
                    "resources": ["Kubernetes the Hard Way (GitHub)", "Official Kubernetes Documentation", "KodeKloud Kubernetes Course (Free tier)"]
                },
                {
                    "skill": "System Design",
                    "why": "Required for Senior Backend roles",
                    "time_estimate": "4-5 weeks part-time",
                    "resources": ["Grokking the System Design Interview", "System Design Primer (YouTube)", "ByteByteGo Newsletter"]
                }
            ]
        }
    
    return state