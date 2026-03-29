# 🚀 Multi-Agent B2B Lead Intelligence Squad

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

## 📌 Project Overview

**Multi-Agent B2B Lead Intelligence Squad** is an autonomous, production-ready AI pipeline designed to streamline B2B outbound sales efforts. Powered by **LangGraph**, it orchestrates a team of specialized AI agents to autonomously research target companies, analyze strategic pain points, and draft hyper-personalized cold emails.

Built with a focus on data privacy, zero-hallucination, and deployment readiness, this system utilizes local LLMs (Llama-3 via Ollama), SQLite for state persistence, and Docker for seamless cross-platform execution.

### ✨ Key Features (The "Tech Flex")
- **⚖️ LLM-as-a-Judge (Reflection Loop):** Every email draft is evaluated by an AI "Judge". If the score is below 8/10, the system triggers an automatic re-draft with specific feedback.
- **🐳 Dockerized Architecture:** Fully containerized environment ensuring seamless deployment across any OS or Cloud provider (No more "It works on my machine" issues).
- **🗄️ Local Database Persistence:** Integrated `SQLite` database automatically saves historical leads, AI evaluations, and email drafts with localized timestamps for easy retrieval.
- **🔄 Failsafe State Regeneration:** Built-in UI controls allowing users to manually force-regenerate emails using cached research data, saving costly I/O scraping time.
- **⚡ Concurrency Optimization:** Uses `ThreadPoolExecutor` to execute I/O-bound tasks (Web Search & Scraping) in parallel, drastically reducing overall latency.
- **🎯 Strictly Typed Structured Outputs:** Pydantic-validated data exchange between all agents using `.with_structured_output()`.

## 🧠 System Architecture

The pipeline leverages a directed **StateGraph** with conditional loops, enabling autonomous reflection and manual interrupts:

1. **🕵️‍♂️ Researcher Node:** Concurrently fetches market news (Tavily) and technology stack (Firecrawl).
2. **🔬 Analyst Node:** Identifies three strategic "Pain Points" and business risks based on the research.
3. **✍️ Copywriter Node:** Drafts a hyper-personalized cold email.
4. **⚖️ Evaluator Node:** Judges the email draft's quality and assigns a score and feedback, routing back for refinement or proceeding to completion.
5. **💾 Persistence Layer:** Validated outputs are automatically committed to the local SQLite database for historical access.

## 🛠️ Tech Stack

- **Orchestration:** [LangGraph](https://python.langchain.com/docs/langgraph) (Stateful multi-agent pipelines)
- **Local Inference:** `Llama-3` via [Ollama](https://ollama.com/) 
- **Search & Scraping:** [Tavily API](https://tavily.com/) & [Firecrawl API](https://www.firecrawl.dev/)
- **Frontend / UI:** [Streamlit](https://streamlit.io/)
- **Database:** `SQLite3`
- **DevOps:** `Docker`

---

## 🚀 Installation & Deployment

You can run this project either using **Docker (Recommended)** or via a traditional Local Virtual Environment.

### Prerequisites
1. Clone the Repository:
   ```bash
   git clone https://github.com/yourusername/Multi-Agent-B2B-Lead-Intelligence-Squad.git
   cd Multi-Agent-B2B-Lead-Intelligence-Squad
2. Create a .env file at the root of the project:
   ```bash
   TAVILY_API_KEY=your_tavily_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
3. Ensure Ollama is installed and the model is pulled on your host machine:
   ```bash
   ollama pull llama3


## 🐳 Option A: Run with Docker (Production Way)

If you have Docker Desktop installed, you can launch the entire isolated environment in just two commands.

> **Note:** To allow the Docker container to communicate with your host machine's Ollama instance, add this line to your `.env` file:

```
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### 1. Build the Image

```bash
docker build -t b2b-lead-app .
```

### 2. Run the Container

```bash
docker run -p 8501:8501 --env-file .env b2b-lead-app
```

Now open your browser and go to:

```
http://localhost:8501
```

---

## 💻 Option B: Run Locally (Development Way)

### 1. Create and Activate Virtual Environment

#### Windows

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Launch the App

```bash
streamlit run ui/app.py
```

---

## 🛣️ Future Roadmap

* 📊 **Evaluation Metrics**
  Integrating LangSmith to trace agent latency, token usage, and pipeline accuracy over time.

* 🧠 **Vector Search (ChromaDB)**
  Establishing a RAG-based database to query past leads semantically.

* 🔄 **Multi-Model Support**
  Extending support to include GPT-4o and Claude 3.5 Sonnet for dynamic model-switching based on task complexity.

  
