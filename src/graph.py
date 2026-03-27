import logging
from typing import TypedDict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.utils.schemas import ResearchOutput, AnalysisOutput, EmailOutput

# ==========================================
# 0. Configure Logging
# ==========================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 1. Define the Graph State
# Eta holo amader system-er memory ba pipeline data.
# ==========================================
class LeadGraphState(TypedDict):
    company_name: str
    company_url: str
    research_data: Optional[ResearchOutput]
    pain_points: Optional[AnalysisOutput]
    email_draft: Optional[EmailOutput]
    evaluation: Optional[EvaluationOutput]
    feedback: Optional[str]
    revision_count: int


# ==========================================
# 2. Initialize the Local LLM (RTX 4060 Optimized)
# ==========================================
# Temperature 0.2 rakhchi jate model basi banie kotha na bole (hallucinate na kore).
llm = ChatOllama(model="llama3", temperature=0.2) 

logger.info("LLM and State Initialized successfully.")

from langchain_core.messages import SystemMessage, HumanMessage
# Nicher import gulo tomar folder structure onujayi asbe
from src.agents.prompts import RESEARCHER_PROMPT, ANALYST_PROMPT, COPYWRITER_PROMPT, EVALUATOR_PROMPT
from src.tools.search_tools import search_company_news, scrape_website

# ==========================================
# 3. Define the Nodes (Agent Functions)
# ==========================================

def researcher_node(state: LeadGraphState):
    """Researcher Agent: Scrapes web and summarizes company data concurrently."""
    logger.info("--- [AGENT] Researcher is working... ---")
    company = state["company_name"]
    url = state["company_url"]
    
    # Concurrent execution for Search and Scrape
    search_results = ""
    website_data = ""
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(search_company_news, company): "search",
            executor.submit(scrape_website, url): "scrape"
        }
        
        for future in as_completed(futures):
            task_name = futures[future]
            try:
                result = future.result()
                if task_name == "search":
                    search_results = result
                else:
                    website_data = result
            except Exception as e:
                logger.error(f"Error in {task_name} task: {e}")
                if task_name == "search": search_results = "Search failed."
                else: website_data = "Scrape failed."

    # 2. Combine data and ask LLM to extract key info
    raw_data = f"Company: {company}\nURL: {url}\n\nSearch Data:\n{search_results}\n\nWebsite Data:\n{website_data}"
    
    messages = [
        SystemMessage(content=RESEARCHER_PROMPT),
        HumanMessage(content=raw_data)
    ]
    
    # Use Structured Output via Pydantic
    structured_llm = llm.with_structured_output(ResearchOutput)
    response = structured_llm.invoke(messages)
    return {"research_data": response} # Update State


def analyst_node(state: LeadGraphState):
    """Analyst Agent: Finds pain points from research data."""
    logger.info("--- [AGENT] Analyst is analyzing pain points... ---")
    research_data = state["research_data"]
    
    # Convert Pydantic object to string context for next LLM
    context = research_data.model_dump_json() if research_data else "No data"
    
    messages = [
        SystemMessage(content=ANALYST_PROMPT),
        HumanMessage(content=f"Here is the structured research data:\n{context}")
    ]
    
    # Use Structured Output via Pydantic
    structured_llm = llm.with_structured_output(AnalysisOutput)
    response = structured_llm.invoke(messages)
    return {"pain_points": response} # Update State


def copywriter_node(state: LeadGraphState):
    """Copywriter Agent: Drafts/Refines the email draft."""
    logger.info("--- [AGENT] Copywriter is drafting/refining the email... ---")
    company = state["company_name"]
    pain_points = state["pain_points"]
    feedback = state.get("feedback")
    old_draft = state.get("email_draft")
    
    # Context
    context = pain_points.model_dump_json() if pain_points else "No pain points"
    
    # Branching logic for initial draft vs revision
    if feedback and old_draft:
        user_msg = f"""
        Target Company: {company}
        Pain Points: {context}
        
        --- PREVIOUS DRAFT ---
        Subject: {old_draft.subject_line}
        Body: {old_draft.email_body}
        
        --- JUDGE FEEDBACK ---
        {feedback}
        
        Please revise the previous draft completely following the feedback above.
        """
    else:
        user_msg = f"Target Company: {company}\nIdentified Pain Points:\n{context}"
    
    messages = [
        SystemMessage(content=COPYWRITER_PROMPT),
        HumanMessage(content=user_msg)
    ]
    
    # Use Structured Output via Pydantic
    structured_llm = llm.with_structured_output(EmailOutput)
    response = structured_llm.invoke(messages)
    
    # Increment Revision Count
    new_rev_count = state.get("revision_count", 0) + 1
    
    return {"email_draft": response, "revision_count": new_rev_count} # Update State


def evaluator_node(state: LeadGraphState):
    """Evaluator Agent: Judges the quality of the email draft (LLM-as-a-Judge)."""
    logger.info("--- [AGENT] AI Judge (Sales Director) is reviewing the draft... ---")
    email_draft = state["email_draft"]
    pain_points = state["pain_points"]
    
    # Context for judgment
    context = pain_points.model_dump_json() if pain_points else "No pain points"
    
    messages = [
        SystemMessage(content=EVALUATOR_PROMPT),
        HumanMessage(content=f"Original Pain Points:\n{context}\n\nDraft Subject: {email_draft.subject_line}\n\nDraft Body: {email_draft.email_body}")
    ]
    
    # Use Structured Output for Evaluation
    structured_llm = llm.with_structured_output(EvaluationOutput)
    response = structured_llm.invoke(messages)
    
    return {"evaluation": response, "feedback": response.feedback}


# ==========================================
# 4. Define Conditional Logic (The Loop)
# ==========================================

def route_evaluation(state: LeadGraphState):
    """Router to decide if we need more reflection or if we are done."""
    evaluation = state["evaluation"]
    rev_count = state.get("revision_count", 0)
    
    # Logic: Approve if score is 8+ OR if we've reached max revisions (2)
    if evaluation and evaluation.score >= 8:
        logger.info(f"--- [ROUTER] Score: {evaluation.score}/10 (Approved) ---")
        return "end"
    elif rev_count >= 2:
        logger.info(f"--- [ROUTER] Max revisions reached ({rev_count}). Stopping. ---")
        return "end"
    else:
        logger.info(f"--- [ROUTER] Score: {evaluation.score}/10. Refining... ---")
        return "refine"

# ==========================================
# 5. Build and Compile the Graph (with Reflection Loop)
# ==========================================

workflow = StateGraph(LeadGraphState)

# Add nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("copywriter", copywriter_node)
workflow.add_node("evaluator", evaluator_node)

# Add edges
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "analyst")
workflow.add_edge("analyst", "copywriter")
workflow.add_edge("copywriter", "evaluator") # Direct edge to judge

# Conditional Loop
workflow.add_conditional_edges(
    "evaluator",
    route_evaluation,
    {
        "end": END,
        "refine": "copywriter"
    }
)


# Initialize Memory Checkpointer
memory = MemorySaver()

# Compile the pipeline with Human-in-the-Loop interrupt
# Note: interrupt_before stays on copywriter so the HUMAN can approve the final reflection result if needed
app = workflow.compile(checkpointer=memory, interrupt_before=["copywriter"])
logger.info("Graph compiled successfully with Reflection Loop and HITL.")

