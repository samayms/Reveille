from ingest import get_papers, fetch_nsf_sbir
from filter import filter_papers
from score import score_items
from database import upsert_leads

def run_pipeline():
    print("=" * 50)
    print("Fetch pipeline starting...")

    openalex_papers = filter_papers(get_papers())
    nsf_leads = fetch_nsf_sbir()
    print(f"Total ingested: {len(openalex_papers) + len(nsf_leads)} ({len(openalex_papers)} OpenAlex, {len(nsf_leads)} NSF)")

    scored_oa = score_items(openalex_papers)
    scored_nsf = score_items(nsf_leads)

    high_signal_oa = [l for l in scored_oa if l.get("relevance_score", 0) >= 7]
    high_signal_nsf = [l for l in scored_nsf if l.get("relevance_score", 0) >= 7]
    high_signal = sorted(high_signal_oa + high_signal_nsf, key=lambda x: x["relevance_score"], reverse=True)

    print(f"Scored {len(scored_oa)} OpenAlex papers: {len(high_signal_oa)} scored 7+")
    print(f"Scored {len(scored_nsf)} NSF leads: {len(high_signal_nsf)} scored 7+")

    upsert_leads(scored_oa)
    upsert_leads(scored_nsf)

    print("\n" + "=" * 50)
    print("Pipeline complete")
    print(f"Total ingested: {len(openalex_papers) + len(nsf_leads)}")
    print(f"After scoring: {len(scored_oa) + len(scored_nsf)}")
    print(f"High signal (7+): {len(high_signal)}")
    print("=" * 50)

    if high_signal:
        print("\nTOP LEADS:")
        for lead in high_signal[:5]:
            print(f"[{lead['relevance_score']}/10] [{lead['source']}] {lead['title'][:70]}")
            print(f"{lead['why_this_matters'][:120]}...")
            print()

if __name__ == "__main__":
    run_pipeline()