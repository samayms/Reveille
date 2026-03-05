import anthropic
import json
from config import ANTHROPIC_API_KEY, PROMPT

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def score_paper(paper):
    prompt = PROMPT.format(
        title=paper.get("title", "") or "",
        authors=paper.get("authors", "") or "",
        institutions=paper.get("institutions", "") or "",
        topics=paper.get("topics", "") or "",
        abstract=paper.get("abstract", "") or "",
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    response_text = response_text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
    response_text = response_text.strip()

    result = json.loads(response_text)
    return {
        **paper,
        "relevance_score": result["relevance_score"],
        "why_this_matters": result["why_this_matters"]
    }


def score_papers(papers):
    print(f"Scoring {len(papers)} papers with Claude...")

    scored = []

    for i, paper in enumerate(papers):
        print(f"  Scoring {i+1}/{len(papers)}: {paper['title'][:60]}...")
        try:
            scored_paper = score_paper(paper)
            scored.append(scored_paper)
        except Exception as e:
            print(f"  Error scoring paper: {e}")
            continue

    print(f"Successfully scored {len(scored)} papers")
    return scored


if __name__ == "__main__":
    from ingest import get_papers
    from filter import filter_papers

    papers = get_papers()
    filtered = filter_papers(papers)
    scored = score_papers(filtered)

    scored.sort(key=lambda x: x["relevance_score"], reverse=True)

    print(f"\n--- TOP SCORED PAPERS ---")
    for paper in scored[:5]:
        print(f"\nScore: {paper['relevance_score']}/10")
        print(f"Title: {paper['title']}")
        print(f"Why: {paper['why_this_matters']}")

ThreadPoolExecutor(max_workers = 3)