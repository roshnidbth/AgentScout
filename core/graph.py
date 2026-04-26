from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from core.models import AssessmentState, ProficiencyScore
from core.llm import llm
from langchain_core.messages import HumanMessage, SystemMessage
from core.learning_plan import generate_learning_plan
import json

def parse_inputs(state: AssessmentState):
    state.skills_to_assess = ["Python", "Machine Learning", "System Design", "SQL", "Leadership"]
    state.current_skill_index = 0
    return state

def assess_skill(state: AssessmentState):
    skill = state.skills_to_assess[state.current_skill_index]
    
    system_prompt = f"""You are an expert technical interviewer.
    Current skill: {skill}
    Ask ONE probing question to assess real depth. Be strict but fair."""
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content="Generate the next question.")
    ])
    
    state.chat_history.append({"role": "assistant", "content": response.content})
    return state

def evaluate_response(state: AssessmentState):
    last_user_msg = state.chat_history[-1]["content"] if state.chat_history else ""
    
    eval_prompt = f"""Evaluate this answer for the skill '{state.skills_to_assess[state.current_skill_index]}'.
    Answer: {last_user_msg}
    
    Return ONLY valid JSON:
    {{"level": 0-5, "justification": "short explanation", "evidence_quote": "exact quote", "confidence": 0.7}}
    """
    
    response = llm.invoke([HumanMessage(content=eval_prompt)])
    
    try:
        data = json.loads(response.content)
        score = ProficiencyScore(
            skill=state.skills_to_assess[state.current_skill_index],
            **data
        )
        state.scores.append(score)
    except:
        state.status = "degraded"
    
    state.current_skill_index += 1
    
    if state.current_skill_index >= len(state.skills_to_assess):
        state.status = "complete"
    
    return state

# Build Graph
graph = StateGraph(AssessmentState)

graph.add_node("parse", parse_inputs)
graph.add_node("assess_skill", assess_skill)
graph.add_node("evaluate", evaluate_response)
graph.add_node("generate_plan", generate_learning_plan)

graph.set_entry_point("parse")
graph.add_edge("parse", "assess_skill")
graph.add_edge("assess_skill", "evaluate")

graph.add_conditional_edges(
    "evaluate",
    lambda state: "generate_plan" if state.status == "complete" else "assess_skill"
)

graph.add_edge("generate_plan", END)

# Compile the graph
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)