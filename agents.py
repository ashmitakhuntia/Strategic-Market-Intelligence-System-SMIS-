"""


Defines what each agent in the pipeline actually does.
Each agent: takes input, optionally calls tools.py, prompts the LLM via
Groq, and returns output for the next agent in the chain.

Pipeline order (called from pipeline.py):
    market_intelligence_agent -> trend_agent -> insights_recommendation_agent -> critic_agent
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from tools import (
    search_web,
    extract_page_text,
    retain_insight,
    recall_past_insights,
    reflect_on_findings,
)

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0.3,
    api_key=os.environ["GROQ_API_KEY"],
)


# 1. Market Intelligence Agent
def market_intelligence_agent(query: str) -> dict:
    """Searches the web and summarizes raw market/news signals for `query`."""
    results = search_web(query)
    sources_text = "\n\n".join(
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content']}" for r in results
    )

    messages = [
        SystemMessage(content=(
            "You are a Market Intelligence Agent. Summarize the raw search "
            "results into a short briefing of the most relevant market signals, "
            "news, or competitor activity. Be factual, no speculation."
        )),
        HumanMessage(content=f"Query: {query}\n\nRaw results:\n{sources_text}"),
    ]
    summary = llm.invoke(messages).content
    return {"query": query, "raw_results": results, "summary": summary}


# 2. Trend Agent
def trend_agent(market_intel: dict) -> dict:
    """Reads full source pages and extracts recurring trend patterns."""
    urls = [r["url"] for r in market_intel["raw_results"][:3]]  # cap to top 3, saves tokens
    full_texts = [extract_page_text(url) for url in urls]
    combined = "\n\n---\n\n".join(full_texts)

    messages = [
        SystemMessage(content=(
            "You are a Trend Agent. Given full-text content from multiple sources, "
            "identify recurring patterns, emerging trends, and notable shifts. "
            "Output 3-5 concise, source-grounded bullet points."
        )),
        HumanMessage(content=combined),
    ]
    trends = llm.invoke(messages).content
    return {**market_intel, "trends": trends}


# 3. Insights & Recommendation Agent — memory-aware
def insights_recommendation_agent(trend_data: dict) -> dict:
    """Synthesizes trends into a recommendation, informed by past Hindsight memory."""
    query = trend_data["query"]
    past_insights = recall_past_insights(f"recommendations or critiques about {query}")
    caution = reflect_on_findings(f"Has a similar recommendation about {query} been flagged or wrong before?")
    past_context = "\n".join(f"- {p}" for p in past_insights) or "No prior memory on this topic."

    messages = [
        SystemMessage(content=(
            "You are an Insights & Recommendation Agent. Given trend analysis, "
            "produce one clear, actionable recommendation. Take into account past "
            "insights and cautionary notes from memory — avoid repeating mistakes "
            "that were previously flagged."
        )),
        HumanMessage(content=(
            f"Trends:\n{trend_data['trends']}\n\n"
            f"Past memory on this topic:\n{past_context}\n\n"
            f"Cautionary reflection:\n{caution}"
        )),
    ]
    recommendation = llm.invoke(messages).content
    return {**trend_data, "recommendation": recommendation}


# 4. Critic Agent — validates + writes feedback back to memory
def critic_agent(insight_data: dict) -> dict:
    """Critiques the recommendation, then stores it + the verdict in memory."""
    messages = [
        SystemMessage(content=(
            "You are a Critic Agent. Evaluate the recommendation for logical "
            "soundness, evidence support, and risk of overstatement. Give a "
            "verdict: APPROVED, NEEDS REVISION, or REJECTED, with a one-line justification."
        )),
        HumanMessage(content=insight_data["recommendation"]),
    ]
    critique = llm.invoke(messages).content

    retain_insight(
        content=(
            f"Topic: {insight_data['query']}\n"
            f"Recommendation: {insight_data['recommendation']}\n"
            f"Critic verdict: {critique}"
        ),
        context="critic feedback",
        tags=[f"topic:{insight_data['query'].lower().replace(' ', '-')}"],
    )
    return {**insight_data, "critique": critique}