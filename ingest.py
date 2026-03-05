import requests
import json
from datetime import datetime, timedelta
from config import SEARCH_TERMS, RESULTS_PER_SEARCH, DAYS_BACK, EMAIL

def find_abstract(inverted_index):
    if not inverted_index:
        return None
    max_position = max(
        pos
        for positions in inverted_index.values()
        for pos in positions
    )
    words = [""] * (max_position + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words)

def get_papers():
    print("Fetching papers from OpenAlex...")

    one_week_ago = (datetime.now() - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%d")

    all_papers = []
    seen_titles = set()
    seen_ids = set()

    for search_term in SEARCH_TERMS:
        params = {
            "search": search_term,
            "filter": f"from_publication_date:{one_week_ago}",
            "per-page": RESULTS_PER_SEARCH,
            # Courtesy request from OpenAlex API
            "mailto": EMAIL
        }

        response = requests.get("https://api.openalex.org/works", params=params)
        data = response.json()

        for work in data.get("results", []):
            paper_id = work.get("id")
            title = work.get("title", "") or ""
            if title in seen_titles:
                continue
            seen_titles.add(title)
            abstract = find_abstract(work.get("abstract_inverted_index"))

            if not abstract:
                continue

            search_clean = search_term.replace('"', '').lower()
            keywords = [kw.strip() for kw in search_clean.split() if kw.strip()]
            content = (title + " " + abstract).lower()
            if not any(kw in content for kw in keywords):
                continue

            authors = []
            institutions = []
            for authorship in work.get("authorships", []):
                name = authorship.get("author", {}).get("display_name")
                if name:
                    authors.append(name)
                for inst in authorship.get("institutions", []):
                    inst_name = inst.get("display_name")
                    if inst_name:
                        institutions.append(inst_name)

            topics = []
            for topic in work.get("topics", []):
                topic_name = topic.get("display_name")
                if topic_name:
                    topics.append(topic_name)

            all_papers.append({
                "paper_id": paper_id,
                "title": title,
                "authors": ", ".join(authors[:3]),
                "institutions": ", ".join(list(set(institutions))[:3]),
                "topics": ", ".join(topics[:3]),
                "abstract": abstract,
                "publication_date": work.get("publication_date"),
                "citation_count": work.get("cited_by_count", 0),
                "source_url": work.get("doi") or paper_id,
                "search_term": search_term
            })

    print(f"Fetched {len(all_papers)} valid papers")
    return all_papers

if __name__ == "__main__":
    papers = get_papers()
    if papers:
        print(json.dumps(papers[0], indent=2))