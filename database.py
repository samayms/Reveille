from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upsert_leads(leads):
    if not leads:
        print("No leads to insert")
        return

    rows = []
    for lead in leads:
        row = {
            "paper_id": lead.get("paper_id"),
            "source": lead.get("source"),
            "search_term": lead.get("search_term"),
            "title": lead.get("title"),
            "authors": lead.get("authors"),
            "institutions": lead.get("institutions"),
            "abstract": lead.get("abstract"),
            "publication_date": lead.get("publication_date"),
            "citation_count": lead.get("citation_count", 0),
            "source_url": lead.get("source_url"),
            "keywords": lead.get("keywords"),
            "funding_source": lead.get("funding_source"),
            "publication_venue": lead.get("publication_venue"),
            "record_type": lead.get("record_type"),
            "pi_email": lead.get("pi_email"),
            "award_amount": lead.get("award_amount"),
            "company_city": lead.get("company_city"),
            "company_state": lead.get("company_state"),
            "grant_expiry": lead.get("grant_expiry"),
            "company_phone": lead.get("company_phone"),
            "grant_type": lead.get("grant_type"),
            "fund_program_name": lead.get("fund_program_name"),
            "relevance_score": lead.get("relevance_score"),
            "why_this_matters": lead.get("why_this_matters"),
        }
        rows.append(row)

    result = client.table("items").upsert(rows, on_conflict="paper_id").execute()
    print(f"Upserted {len(rows)} leads to Supabase")
    return result


def fetch_leads(min_score=None, status=None, source=None):
    query = client.table("items").select("*")

    if min_score is not None:
        query = query.gte("relevance_score", min_score)
    if status is not None:
        query = query.eq("status", status)
    if source is not None:
        query = query.eq("source", source)

    query = query.order("relevance_score", desc=True)
    result = query.execute()
    return result.data


def update_status(paper_id, new_status):
    result = (
        client.table("items")
        .update({"status": new_status})
        .eq("paper_id", paper_id)
        .execute()
    )
    return result


if __name__ == "__main__":
    leads = fetch_leads(min_score=7)
    print(f"Leads with score >= 6: {len(leads)}")
    if leads:
        print(f"Top lead: {leads[0]['title']} — {leads[0]['relevance_score']}/10")