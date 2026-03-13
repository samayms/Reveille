from concurrent.futures import ThreadPoolExecutor, as_completed
from ingest import fetch_openalex_papers, fetch_nsf_sbir_awards, fetch_sbir_gov
from score import score_items
from database import upsert_leads, fetch_existing_ids
from config import ENABLE_OPENALEX, ENABLE_NSF_SBIR, ENABLE_SBIR_GOV

def run_pipeline():
    print("=" * 50)
    print("Fetch pipeline starting...")

    existing_ids = fetch_existing_ids()
    print(f"Skipping {len(existing_ids)} existing records in database")

    # Fetch all enabled sources in parallel
    fetch_tasks = {}
    if ENABLE_OPENALEX:
        fetch_tasks["openalex"] = fetch_openalex_papers
    if ENABLE_NSF_SBIR:
        fetch_tasks["nsf"] = fetch_nsf_sbir_awards
    if ENABLE_SBIR_GOV:
        fetch_tasks["sbir_gov"] = fetch_sbir_gov

    fetched = {}
    with ThreadPoolExecutor(max_workers=len(fetch_tasks) or 1) as executor:
        futures = {executor.submit(fn): name for name, fn in fetch_tasks.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                fetched[name] = future.result()
            except Exception as e:
                print(f"  Fetch error [{name}]: {e}")
                fetched[name] = []

    all_leads = []

    if "openalex" in fetched:
        openalex_papers = fetched["openalex"]
        new_oa = [p for p in openalex_papers if p["paper_id"] not in existing_ids]
        print(f"OpenAlex: {len(openalex_papers)} fetched, {len(new_oa)} new")
        scored_oa = score_items(new_oa)
        upsert_leads(scored_oa)
        print(f"Scored {len(scored_oa)} OpenAlex papers: {sum(1 for l in scored_oa if l.get('relevance_score', 0) >= 7)} scored 7+")
        all_leads.extend(scored_oa)

    if "nsf" in fetched:
        nsf_leads = fetched["nsf"]
        new_nsf = [p for p in nsf_leads if p["paper_id"] not in existing_ids]
        print(f"NSF SBIR: {len(nsf_leads)} fetched, {len(new_nsf)} new")
        scored_nsf = score_items(new_nsf)
        upsert_leads(scored_nsf)
        print(f"Scored {len(scored_nsf)} NSF leads: {sum(1 for l in scored_nsf if l.get('relevance_score', 0) >= 7)} scored 7+")
        all_leads.extend(scored_nsf)

    if "sbir_gov" in fetched:
        sbir_gov_leads = fetched["sbir_gov"]
        new_sbir = [p for p in sbir_gov_leads if p["paper_id"] not in existing_ids]
        print(f"SBIR.gov: {len(sbir_gov_leads)} fetched, {len(new_sbir)} new")
        scored_sbir_gov = score_items(new_sbir)
        upsert_leads(scored_sbir_gov)
        print(f"Scored {len(scored_sbir_gov)} SBIR.gov leads: {sum(1 for l in scored_sbir_gov if l.get('relevance_score', 0) >= 7)} scored 7+")
        all_leads.extend(scored_sbir_gov)

    high_signal = sorted(
        [l for l in all_leads if l.get("relevance_score", 0) >= 7],
        key=lambda x: x["relevance_score"],
        reverse=True,
    )

    print("\n" + "=" * 50)
    print("Pipeline complete")
    print(f"Total scored: {len(all_leads)}")
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
