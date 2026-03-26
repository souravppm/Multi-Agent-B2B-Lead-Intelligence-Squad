from typing import TypedDict, Optional
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END

# ==========================================
# 1. Define the Graph State
# Eta holo amader system-er memory ba pipeline data.
# ==========================================
class LeadGraphState(TypedDict):
    company_name: str
    company_url: str
    research_data: Optional[str]
    pain_points: Optional[str]
    email_draft: Optional[str]

# ==========================================
# 2. Initialize the Local LLM (RTX 4060 Optimized)
# ==========================================
# Temperature 0.2 rakhchi jate model basi banie kotha na bole (hallucinate na kore).
llm = ChatOllama(model="llama3", temperature=0.2) 

print("LLM and State Initialized successfully.")

from langchain_core.messages import SystemMessage, HumanMessage
# Nicher import gulo tomar folder structure onujayi asbe
from src.agents.prompts import RESEARCHER_PROMPT, ANALYST_PROMPT, COPYWRITER_PROMPT
from src.tools.search_tools import search_company_news, scrape_website

# ==========================================
# 3. Define the Nodes (Agent Functions)
# ==========================================

def researcher_node(state: LeadGraphState):
    """Researcher Agent: Scrapes web and summarizes company data."""
    print("--- [AGENT] Researcher is working... ---")
    company = state["company_name"]
    url = state["company_url"]
    
    # 1. Use Tools (Error handling rakha valo, but MVP er jonno simple rakhchi)
    try:
        search_results = search_company_news(company)
        website_data = scrape_website(url)
    except Exception as e:
        print(f"Tool Error: {e}")
        search_results = "Could not fetch news."
        website_data = "Could not fetch website."

    # 2. Combine data and ask LLM to extract key info
    raw_data = f"Company: {company}\nURL: {url}\n\nSearch Data:\n{search_results}\n\nWebsite Data:\n{website_data}"
    
    messages = [
        SystemMessage(content=RESEARCHER_PROMPT),
        HumanMessage(content=raw_data)
    ]
    
    response = llm.invoke(messages)
    return {"research_data": response.content} # Update State


def analyst_node(state: LeadGraphState):
    """Analyst Agent: Finds pain points from research data."""
    print("--- [AGENT] Analyst is analyzing pain points... ---")
    research_data = state["research_data"]
    
    messages = [
        SystemMessage(content=ANALYST_PROMPT),
        HumanMessage(content=f"Here is the structured research data:\n{research_data}")
    ]
    
    response = llm.invoke(messages)
    return {"pain_points": response.content} # Update State


def copywriter_node(state: LeadGraphState):
    """Copywriter Agent: Drafts the final email."""
    print("--- [AGENT] Copywriter is drafting the email... ---")
    company = state["company_name"]
    pain_points = state["pain_points"]
    
    messages = [
        SystemMessage(content=COPYWRITER_PROMPT),
        HumanMessage(content=f"Target Company: {company}\nIdentified Pain Points:\n{pain_points}")
    ]
    
    response = llm.invoke(messages)
    return {"email_draft": response.content} # Update State

# ==========================================
# 4. Build and Compile the Graph
# ==========================================

workflow = StateGraph(LeadGraphState)

# Add nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("copywriter", copywriter_node)

# Add edges (Set the flow)
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "analyst")
workflow.add_edge("analyst", "copywriter")
workflow.add_edge("copywriter", END)

# Compile the pipeline
app = workflow.compile()
print("Graph compiled successfully!")
