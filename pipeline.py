"""

Orchestrates the full research pipeline:
    Market Intelligence -> Trend -> Insights & Recommendation -> Critic

Entry point: run_research_pipeline(query)
Called by app.py (Streamlit UI).
"""

from datetime import datetime, timezone

from agents import (
    market_intelligence_agent,
    trend_agent,
    insights_recommendation_agent,
    critic_agent,
)


def run_research_pipeline(query: str) -> dict:
    """
    Runs the full four-agent pipeline for a given research query.
    Returns a dict with results from every stage, plus metadata.

    print() statements below are intentional — they give your Streamlit
    UI's live stdout capture something to show as progress.
    """
    started_at = datetime.now(timezone.utc).isoformat()
    state: dict = {"query": query, "started_at": started_at}

    try:
        print(f"[1/4] Market Intelligence Agent: searching for '{query}'...")
        state = market_intelligence_agent(query)
        print(f"  -> found {len(state.get('raw_results', []))} sources.")

        print("[2/4] Trend Agent: extracting and analyzing trends...")
        state = trend_agent(state)
        print("  -> trend analysis complete.")

        print("[3/4] Insights & Recommendation Agent: checking memory + generating recommendation...")
        state = insights_recommendation_agent(state)
        print("  -> recommendation generated.")

        print("[4/4] Critic Agent: validating recommendation + updating memory...")
        state = critic_agent(state)
        print("  -> critique complete, insight stored in memory.")

        state["status"] = "success"

    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}")
        state["status"] = "error"
        state["error_message"] = str(e)

    state["finished_at"] = datetime.now(timezone.utc).isoformat()
    return state


# Optional: quick manual test without Streamlit
if __name__ == "__main__":
    topic = input("Enter your query: ").strip()
    if not topic:
        print("No query entered - exiting.")
    else:
        result = run_research_pipeline(topic)
        print("\n--- FINAL STATE ---")
        for key, value in result.items():
            if key not in ("raw_results",):  # skip the noisy raw list in console output
                print(f"\n{key.upper()}:\n{value}")