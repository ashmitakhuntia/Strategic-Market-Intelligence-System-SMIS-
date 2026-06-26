"""

Plain utility functions called directly from pipeline.py (not LangChain
@tool-wrapped functions) — your pipeline runs agents in a fixed sequence
rather than letting an LLM decide which tool to call, so keeping these as


- search_web()              -> Market Intelligence Agent  (Tavily)
- extract_page_text()       -> Trend Agent                (scrape + clean)
- retain_insight()
  recall_past_insights()
  reflect_on_findings()      -> Insights & Recommendation Agent (Hindsight)
"""

import requests
from bs4 import BeautifulSoup
from langchain_tavily import TavilySearch

from memory import client, BANK_ID


# Market Intelligence Agent — web search
_tavily = TavilySearch(max_results=5, topic="news")


def search_web(query: str) -> list[dict]:
    """
    Search the web for market/news signals related to `query`.
    Returns: [{"title": ..., "url": ..., "content": ...}, ...]
    """
    response = _tavily.invoke({"query": query})
    results = response.get("results", []) if isinstance(response, dict) else response
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", "")}
        for r in results
    ]


# Trend Agent — page extraction
def extract_page_text(url: str, max_chars: int = 5000) -> str:
    """Fetch a URL and return cleaned, readable text content."""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return " ".join(soup.stripped_strings)[:max_chars]
    except Exception as e:
        return f"[Error fetching {url}: {e}]"


# Insights & Recommendation Agent — Hindsight memory
def retain_insight(content: str, context: str = "research insight", tags: list[str] | None = None) -> None:
    """Store a finalized insight or Critic feedback into persistent memory."""
    client.retain(bank_id=BANK_ID, content=content, context=context, tags=tags)


def recall_past_insights(query: str, budget: str = "mid") -> list[str]:
    """Return plain fact strings relevant to `query`, most relevant first."""
    response = client.recall(bank_id=BANK_ID, query=query, budget=budget)
    return [r.text for r in response.results]


def reflect_on_findings(query: str, budget: str = "mid") -> str:
    """
    Synthesize across accumulated memory to answer a higher-level question,
    e.g. "Has a similar recommendation been flagged or wrong before?"
    """
    response = client.reflect(bank_id=BANK_ID, query=query, budget=budget)
    return response.text