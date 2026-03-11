import requests
import json
from datetime import datetime, timedelta
from config import (
    SEARCH_TERMS,
    RESULTS_PER_SEARCH,
    OPEN_ALEX_DAYS_BACK,
    NSF_DAYS_BACK,
    NSF_FILTER_KEYWORDS,
    SBIR_GOV_DAYS_BACK,
    SBIR_GOV_FILTER_KEYWORDS,
    ENABLE_OPENALEX,
    ENABLE_NSF_SBIR,
    ENABLE_SBIR_GOV,
    EMAIL,
)

def decode_openalex_abstract(inverted_index):
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

def fetch_openalex_papers():
    if not ENABLE_OPENALEX:
        print("OpenAlex: disabled (ENABLE_OPENALEX=False)")
        return []
    print("Fetching papers from OpenAlex...")

    one_week_ago = (datetime.now() - timedelta(days=OPEN_ALEX_DAYS_BACK)).strftime("%Y-%m-%d")

    all_papers = []
    seen_titles = set()
    seen_ids = set()

    for search_term in SEARCH_TERMS:
        params = {
            "search": " ".join(f'"{p}"' for p in search_term),
            "filter": f"from_publication_date:{one_week_ago}",
            "per-page": RESULTS_PER_SEARCH,
            # Courtesy request from OpenAlex API
            "mailto": EMAIL
        }

        response = requests.get("https://api.openalex.org/works", params=params)
        data = response.json()

        for work in data.get("results", []):
            paper_id = f"oa_{work.get('id')}"
            title = work.get("title", "") or ""
            if title in seen_titles:
                continue
            seen_titles.add(title)
            abstract = decode_openalex_abstract(work.get("abstract_inverted_index"))

            if not abstract:
                continue

            phrases = [p.lower() for p in search_term]
            content = (title + " " + abstract).lower()
            if not all(phrase in content for phrase in phrases):
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

            funding_source = ", ".join(
                g.get("funder_display_name", "")
                for g in work.get("grants", [])
                if g.get("funder_display_name")
            )

            keywords = ", ".join(
                k.get("keyword", "")
                for k in work.get("keywords", [])
                if k.get("keyword")
            )

            publication_venue = (
                (work.get("primary_location") or {})
                .get("source") or {}
            ).get("display_name", "") or ""

            all_papers.append({
                "paper_id": paper_id,
                "title": title,
                "authors": ", ".join(authors[:3]),
                "institutions": ", ".join(list(set(institutions))[:3]),
                "keywords": keywords,
                "funding_source": funding_source,
                "publication_venue": publication_venue,
                "record_type": work.get("type", ""),
                "abstract": abstract,
                "publication_date": work.get("publication_date"),
                "citation_count": work.get("cited_by_count", 0),
                "source_url": work.get("doi") or paper_id,
                "search_term": " ".join(f'"{p}"' for p in search_term),
                "source": "OpenAlex"
            })

    print(f"Fetched {len(all_papers)} valid papers")
    return all_papers

def fetch_nsf_sbir_awards():
    if not ENABLE_NSF_SBIR:
        print("NSF SBIR: disabled (ENABLE_NSF_SBIR=False)")
        return []
    print("Fetching NSF SBIR grants...")
    url = "http://api.nsf.gov/services/v1/awards.json"
    one_month_ago = (datetime.now() - timedelta(days=NSF_DAYS_BACK)).strftime("%m/%d/%Y")
    companies = []
    seen_ids = set()

    for keyword in NSF_FILTER_KEYWORDS:
        params = {
            "keyword": keyword,
            "fundProgramName": "SBIR Phase I",
            "dateStart": one_month_ago,
            "printFields": "id,title,abstractText,awardeeName,piEmail,pdPIName,estimatedTotalAmt,startDate,awardeeCity,awardeeStateCode,expDate,awardeePhone,transType",
            "rpp": 25
        }

        response = requests.get(url, params=params)
        data = response.json()

        awards = data.get("response", {}).get("award", [])
        total = data.get("response", {}).get("metadata", {}).get("totalCount", 0)
        print(f"NSF '{keyword}': {total} total grants, processing {len(awards)}")

        for award in awards:
            award_id = f"nsf_{award.get('id')}"

            if award_id in seen_ids:
                continue
            seen_ids.add(award_id)

            abstract = award.get("abstractText", "") or ""
            title = award.get("title", "") or ""

            if len(abstract.split()) < 100:
                continue

            content = (title + " " + abstract).lower()
            if not any(kw in content for kw in NSF_FILTER_KEYWORDS):
                continue

            companies.append({
                "paper_id": award_id,
                "title": title,
                "authors": award.get("pdPIName", ""),
                "institutions": award.get("awardeeName", ""),
                "abstract": abstract,
                "publication_date": award.get("startDate", ""),
                "citation_count": 0,
                "source_url": f"https://www.nsf.gov/awardsearch/showAward?AWD_ID={award.get('id')}",
                "search_term": "NSF SBIR Phase I",
                "source": "NSF",
                "pi_email": award.get("piEmail", ""),
                "award_amount": award.get("estimatedTotalAmt", ""),
                "company_city": award.get("awardeeCity", ""),
                "company_state": award.get("awardeeStateCode", ""),
                "grant_expiry": award.get("expDate", ""),
                "company_phone": award.get("awardeePhone", ""),
                "grant_type": award.get("transType", "")
            })
    
    print(f"Fetched {len(companies)} relevant NSF SBIR grants")
    return companies

def fetch_sbir_gov():
    if not ENABLE_SBIR_GOV:
        print("SBIR.gov: disabled (ENABLE_SBIR_GOV=False)")
        return []
    print("Fetching SBIR.gov awards...")

    # NOTE: sbir.gov API has been offline intermittently.
    # Set ENABLE_SBIR_GOV=True in config.py when the API is restored.
    # Docs: https://www.sbir.gov/sites/default/files/sbir_gov_api_documentation_v3.pdf
    url = "https://api.sbir.gov/public/api/awards"
    cutoff_year = (datetime.now() - timedelta(days=SBIR_GOV_DAYS_BACK)).year
    companies = []
    seen_ids = set()

    for keyword in SBIR_GOV_FILTER_KEYWORDS:
        params = {
            "keyword": keyword,
            "award_year": cutoff_year,
            "rows": 25,
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"SBIR.gov '{keyword}': request failed — {e}")
            continue

        awards = data if isinstance(data, list) else data.get("data", [])
        print(f"SBIR.gov '{keyword}': {len(awards)} awards returned")

        for award in awards:
            award_id = f"sbir_{award.get('award_number') or award.get('id')}"
            if award_id in seen_ids:
                continue
            seen_ids.add(award_id)

            abstract = award.get("abstract", "") or ""
            title = award.get("title", "") or award.get("project_title", "") or ""

            if len(abstract.split()) < 50:
                continue

            content = (title + " " + abstract).lower()
            if not any(kw in content for kw in SBIR_GOV_FILTER_KEYWORDS):
                continue

            companies.append({
                "paper_id": award_id,
                "title": title,
                "authors": award.get("pi_name", ""),
                "institutions": award.get("firm", "") or award.get("company", ""),
                "abstract": abstract,
                "publication_date": award.get("award_date", "") or str(award.get("award_year", "")),
                "citation_count": 0,
                "source_url": award.get("solicitation_url", "") or f"https://www.sbir.gov/sbirsearch/detail/{award.get('award_number', '')}",
                "search_term": "SBIR.gov",
                "source": "SBIR.gov",
                "pi_email": award.get("pi_email", ""),
                "award_amount": award.get("award_amount", ""),
                "company_city": award.get("city", ""),
                "company_state": award.get("state_code", ""),
                "agency": award.get("agency", ""),
                "phase": award.get("phase", ""),
            })

    print(f"Fetched {len(companies)} relevant SBIR.gov awards")
    return companies


if __name__ == "__main__":
    papers = fetch_openalex_papers()
    if papers:
        print(json.dumps(papers[0], indent=2))