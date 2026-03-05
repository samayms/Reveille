def filter_papers(papers):
    print(f"Filtering {len(papers)} papers...")

    filtered = []

    for paper in papers:
        abstract = paper.get("abstract", "")
        title = paper.get("title", "") or ""

        if len(abstract.split()) < 100:
            continue

        filtered.append(paper)

    print(f"{len(filtered)} papers passed filter")
    return filtered


if __name__ == "__main__":
    from ingest import get_papers
    papers = get_papers()
    filtered = filter_papers(papers)

    print(f"\nDropped {len(papers) - len(filtered)} papers")
    print(f"\n--- FILTERED TITLES ---")
    for paper in filtered:
        print(f"  {paper['title']}")