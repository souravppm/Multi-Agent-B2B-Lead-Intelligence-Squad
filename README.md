# Multi-Agent B2B Lead Intelligence Squad 🤖🏢

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)

## Project Overview

**Multi-Agent B2B Lead Intelligence Squad** is an autonomous AI agent pipeline designed to streamline and automate B2B outbound sales efforts. Powered by **LangGraph**, it orchestrates a team of specialized AI agents to research a target company, analyze its strategic pain points, and draft a highly personalized, context-aware cold email. 

By utilizing local LLMs and autonomous web scraping, the system delivers high-quality, actionable sales intelligence with zero hallucination and robust privacy.

## System Architecture

The pipeline leverages a directed State Graph, enabling seamless intelligence transfer between three autonomous nodes:

1. **🕵️‍♂️ Researcher Node:** Given a company name and URL, it uses the Tavily Search API and Firecrawl to scrape recent news (last 6-12 months) and technology stack data. It processes and structures the raw data into actionable intelligence.
2. **🧠 Analyst Node:** Ingests the Researcher's formatted data to identify three distinct, strategic "Pain Points" the target company is currently facing, explaining exactly *why* these pose a friction or business risk.
3. **✍️ Copywriter Node:** Receives the strategic analysis and drafts a hyper-personalized, high-converting cold email. It mentions a specific recent news item and addresses an identified pain point with a subtle solution—strictly avoiding generic templates or buzzwords perfectly suited for enterprise decision-makers.

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
