# Multi-Agent B2B Lead Intelligence Squad

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)

## Project Overview

**Multi-Agent B2B Lead Intelligence Squad** is an autonomous AI agent pipeline designed to streamline and automate B2B outbound sales efforts. Powered by **LangGraph**, it orchestrates a team of specialized AI agents to research a target company, analyze its strategic pain points, and draft a highly personalized, context-aware cold email. 

By utilizing local LLMs, autonomous web scraping, and **Human-in-the-Loop (HITL)** oversight, the system delivers high-quality, actionable sales intelligence with zero hallucination and robust privacy.

### Key Features 🚀
- **⚖️ LLM-as-a-Judge (Reflection Loop):** Every email draft is evaluated by a "Judge" LLM. If the score is below 8/10, the system triggers an automatic re-draft with specific feedback for refinement (Max 2 iterations).
- **⚡ Concurrency Optimization:** Uses `ThreadPoolExecutor` to execute I/O-bound tasks (Search & Scraping) in parallel, drastically reducing overall latency.
- **🙋‍♂️ Human-in-the-Loop (HITL):** A manual approval step after analysis ensures 100% quality and alignment before the final draft is verified.
- **🔄 State Persistence:** Built-in `MemorySaver` checkpointer for session-based autonomous workflows and state recovery.
- **🎯 Strictly Typed Structured Outputs:** Pydantic-validated data exchange between all agents using `.with_structured_output()`.
- **📜 Structured Logging:** Production-ready traceability using Python's standard logging module (INFO level).

## System Architecture

The pipeline leverages a directed **StateGraph** with conditional loops, enabling autonomous reflection and manual interrupts:

1. **🕵️‍♂️ Researcher Node:** Concurrently fetches market news (Tavily) and technology stack (Firecrawl).
2. **🧠 Analyst Node:** Identifies three strategic "Pain Points" and business risks based on the research.
3. **✍️ Copywriter Node:** Drafts a hyper-personalized cold email and incorporates feedback if a revision is needed.
4. **⚖️ Evaluator Node:** Judges the email draft's quality and assigns a score and feedback, deciding whether to route back for refinement or proceed to completion.


## Tech Stack

This project is built using bleeding-edge AI and data engineering technologies:

- **Orchestration:** [LangGraph](https://python.langchain.com/docs/langgraph) (Stateful multi-agent pipelines)
- **Local Inference:** `Llama-3` via [Ollama](https://ollama.com/) — *Uses the dedicated `langchain-ollama` library for enhanced performance and stability on an NVIDIA RTX 4060.*
- **Search Engine:** [Tavily API](https://tavily.com/) (AI-optimized advanced web search)
- **Web Scraping:** [Firecrawl API](https://www.firecrawl.dev/) — *Compatible with Firecrawl SDK v4+ for robust markdown extraction.*
- **Frontend / UI:** [Streamlit](https://streamlit.io/) (Interactive, real-time tracking interface)

## Installation & Setup

Follow these steps to set up the B2B Lead Intelligence Squad on your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/souravppm/Multi-Agent-B2B-Lead-Intelligence-Squad.git
cd Multi-Agent-B2B-Lead-Intelligence-Squad
```

### 2. Create the Virtual Environment

Ensure you have Python 3.10+ installed. Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Requirements

Install the necessary dependencies to run the backend agents and the Streamlit frontend:

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

The system relies on external APIs to fetch live market data. Create a `.env` file at the root of the project:

```bash
touch .env
```

Add your API keys to the `.env` file:

```env
TAVILY_API_KEY=your_tavily_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### 5. Pull the Local Model

Since the pipeline runs `Llama-3` locally to ensure privacy, you must pull the model using Ollama. Make sure the Ollama server is running in your background, then execute:

```bash
ollama pull llama3
```

## Usage

Once everything is set up, you can launch the beautiful interactive UI to execute the pipeline. Run the following command in your terminal using the activated environment:

```bash
streamlit run ui/app.py
```

This will automatically open the web application in your browser. From the sidebar, input the target **Company Name** and **Company URL**, then click **Generate Intel** to watch the agents execute their tasks in real-time.

---

## Future Roadmap

The intelligence pipeline is continuously evolving. Planned enhancements include:

- **📊 Evaluation Metrics:** Integrating LangSmith to trace agent latency, token usage, and pipeline accuracy over time.
- **🗄️ Vector Database (ChromaDB):** Establishing a permanent leads database utilizing ChromaDB to store, index, and retrieve historical lead intelligence preventing duplicate efforts.
- **🔄 Multi-Model Support:** Extending support beyond Ollama to include GPT-4o, Claude 3.5 Sonnet, and Gemini Pro for dynamic model-switching based on task complexity.
