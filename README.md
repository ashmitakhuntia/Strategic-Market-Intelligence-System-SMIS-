# Strategic Market Intelligence System

> A memory-aware, four-agent crew that researches a market topic, extracts trends, generates a recommendation, and critiques itself — learning from its own past critiques over time.

## Overview

This project automates tech market research through a sequential pipeline of four LLM-powered agents. Given a query, the crew searches the web, reads the most relevant sources in full, synthesizes trends, produces an actionable recommendation, and then has a Critic agent validate that recommendation.

What sets this crew apart is **persistent memory**: the Critic Agent's verdicts aren't thrown away after each run — they're stored via **Hindsight** and recalled by the Insights & Recommendation Agent on future queries about the same topic. This closes a feedback loop where the crew avoids repeating recommendations that were previously flagged as weak or wrong.

## Agent Crew

| Agent | Function | Responsibility |
|---|---|---|
| **Market Intelligence Agent** | `market_intelligence_agent()` | Searches the web for the query and summarizes raw market/news signals into a factual briefing |
| **Trend Agent** | `trend_agent()` | Reads the full text of the top sources and extracts 3–5 concise, source-grounded trend bullet points |
| **Insights & Recommendation Agent** | `insights_recommendation_agent()` | Recalls past insights and cautionary reflections from memory, then synthesizes trends into one actionable recommendation |
| **Critic Agent** | `critic_agent()` | Evaluates the recommendation (APPROVED / NEEDS REVISION / REJECTED + justification), then writes the recommendation and verdict back into memory |

All four agents are powered by **Groq's `llama-3.3-70b-versatile`** via LangChain.

## Pipeline Flow

```
query
  │
  ▼
[1] Market Intelligence Agent  ──► search_web()
  │   summarizes raw search results
  ▼
[2] Trend Agent  ──► extract_page_text()
  │   reads top 3 sources in full, extracts trend patterns
  ▼
[3] Insights & Recommendation Agent  ──► recall_past_insights() + reflect_on_findings()
  │   generates a recommendation, informed by memory
  ▼
[4] Critic Agent  ──► retain_insight()
  │   validates the recommendation, stores verdict back into memory
  ▼
final report (query, summary, trends, recommendation, critique, status)
```

The whole pipeline runs through a single entry point — `run_research_pipeline(query)` — which is called by the Streamlit UI (`app.py`) and prints live progress to stdout for the UI to capture.

## Tech Stack

- **Python 3.10+**
- **LangChain** (`langchain_groq`, `langchain_core`) — LLM orchestration
- **Groq API** — `llama-3.3-70b-versatile` inference
- **Hindsight** — persistent agent memory (insight storage + recall + reflection)
- **Streamlit** — UI layer (`app.py`)
- **python-dotenv** — environment configuration

## Project Structure

```
Strategic-Market-Intelligence-System-SMIS/
├── agents.py          # Market Intelligence, Trend, Insights & Recommendation, and Critic agents
├── tools.py           # Web search, page scraping, and Hindsight memory tools
├── pipeline.py        # Orchestrates the 4-agent pipeline (run_research_pipeline)
├── app.py             # Streamlit UI
├── requirements.txt
└── .env               # GROQ_API_KEY and Hindsight config
```

## Installation

```bash
git clone https://github.com/ashmitakhuntia/Strategic-Market-Intelligence-System-SMIS-.git
cd strategic-market-intelligence-system

python -m venv .venv
# On Windows: venv\Scripts\activate    #on macOs: source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file with:

```
GROQ_API_KEY=your_groq_api_key
```

(plus any Hindsight configuration your `tools.py` setup requires)

## Usage

**Via Streamlit UI:**

```bash
streamlit run app.py
```

**Via CLI (quick test, no UI):**

```bash
python pipeline.py
# Enter your query when prompted
```

## Output

`run_research_pipeline(query)` returns a dict containing:

- `query` — the original research query
- `raw_results` — search results from the Market Intelligence Agent
- `summary` — factual market/news briefing
- `trends` — 3–5 source-grounded trend bullet points
- `recommendation` — actionable recommendation, informed by memory
- `critique` — Critic Agent's verdict and justification
- `status` — `success` or `error`
- `started_at` / `finished_at` — UTC timestamps

## Memory Loop (Hindsight)

1. After every run, the Critic Agent calls `retain_insight()` to store the topic, recommendation, and verdict, tagged by topic.
2. On a future query about the same topic, the Insights & Recommendation Agent calls `recall_past_insights()` and `reflect_on_findings()` to check whether a similar recommendation was previously flagged — and adjusts accordingly.

This means the crew's recommendations get more reliable the more it's used on overlapping topics, instead of starting from zero every run.



