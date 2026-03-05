import requests
import json
from datetime import datetime, timedelta

url = "https://api.openalex.org/works"

one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

searches = [
    # POWER
    '"small modular reactor"',
    '"nuclear reactor" "military"',
    '"grid resilience" "infrastructure"',
    '"energy storage" "grid"',

    # PROTECTION
    '"unmanned aerial" "defense"',
    '"counter drone"',
    '"autonomous weapon"',
    '"defense technology" "startup"',

    # PRODUCTIVITY
    '"manufacturing" "AI" "defense"',
    '"supply chain" "military" "automation"',
]

all_papers = []
seen_ids = set()

for search_term in searches:
    params = {
        "search": search_term,
        "filter": f"from_publication_date:{one_week_ago}",
        "per-page": 10,
        "mailto": "samayms@umich.edu"
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = data.get("results", [])
    count = data.get("meta", {}).get("count", 0)

    print(f"\nSearch: {search_term}")
    print(f"Total results: {count}")

    valid = 0

    for work in results:
        paper_id = work.get("id")
        if paper_id in seen_ids:
            continue
        seen_ids.add(paper_id)

        title = work.get("title", "") or ""
        abstract_index = work.get("abstract_inverted_index")

        if abstract_index:
            max_pos = max(
                pos
                for positions in abstract_index.values()
                for pos in positions
            )
            words = [""] * (max_pos + 1)
            for word, positions in abstract_index.items():
                for pos in positions:
                    words[pos] = word
            abstract = " ".join(words)
        else:
            abstract = ""

        search_clean = search_term.replace('"', '').lower()
        keywords = [kw.strip() for kw in search_clean.split() if kw.strip()]

        content = (title + " " + abstract).lower()
        if any(kw in content for kw in keywords):
            valid += 1
            all_papers.append({
                "title": title,
                "abstract": abstract[:200],
                "search_term": search_term
            })

    print(f"Valid (keyword in title/abstract): {valid}")

print(f"\n{'='*50}")
print(f"TOTAL VALID PAPERS: {len(all_papers)}")
print(f"\n--- SAMPLE TITLES ---")
for paper in all_papers[:10]:
    print(f"  [{paper['search_term']}]")
    print(f"  {paper['title']}")
    print()