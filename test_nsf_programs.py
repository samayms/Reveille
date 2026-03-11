"""
Quick test: check how many results each NSF program type returns
for a sample of our filter keywords.
Run: python3 test_nsf_programs.py
"""

import requests
from datetime import datetime, timedelta

URL = "http://api.nsf.gov/services/v1/awards.json"
DAYS_BACK = 90  # wider window to get a meaningful sample
DATE_START = (datetime.now() - timedelta(days=DAYS_BACK)).strftime("%m/%d/%Y")

# Representative sample — not all keywords, just enough to gauge yield
SAMPLE_KEYWORDS = ["nuclear", "defense", "autonomous", "manufacturing", "drone"]

PROGRAMS = [
    "SBIR Phase I",
    "SBIR Phase II",
    "STTR Phase I",
    "STTR Phase II",
]


def check_program(program_name):
    total_raw = 0
    total_passing = 0
    sample_titles = []

    for keyword in SAMPLE_KEYWORDS:
        params = {
            "keyword": keyword,
            "fundProgramName": program_name,
            "dateStart": DATE_START,
            "printFields": "id,title,abstractText,awardeeName,estimatedTotalAmt,startDate",
            "rpp": 25,
        }
        try:
            resp = requests.get(URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [{keyword}] request failed: {e}")
            continue

        awards = data.get("response", {}).get("award", [])
        api_total = data.get("response", {}).get("metadata", {}).get("totalCount", 0)
        total_raw += int(api_total)

        for award in awards:
            abstract = award.get("abstractText", "") or ""
            title = award.get("title", "") or ""
            # Apply the same 100-word abstract filter used in ingest.py
            if len(abstract.split()) >= 100:
                total_passing += 1
                if len(sample_titles) < 3:
                    amt = award.get("estimatedTotalAmt", "?")
                    sample_titles.append(f"  ${amt:>10}  {title[:70]}")

    return total_raw, total_passing, sample_titles


def main():
    print(f"NSF program yield test — {DAYS_BACK}-day window, {len(SAMPLE_KEYWORDS)} keywords")
    print(f"Date range: {DATE_START} → today\n")
    print(f"{'Program':<20} {'API total':>10} {'Passing filter':>16}")
    print("-" * 50)

    for program in PROGRAMS:
        raw, passing, titles = check_program(program)
        print(f"{program:<20} {raw:>10,} {passing:>16,}")
        for t in titles:
            print(t)
        if titles:
            print()


if __name__ == "__main__":
    main()
