"""
One-time script to strip HTML from why_this_matters fields that were
accidentally stored as HTML card fragments instead of plain text.
"""
import re
import html
from database import client


def strip_html(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    result = client.table("items").select("paper_id, why_this_matters").execute()
    rows = result.data

    to_update = []
    for row in rows:
        val = row.get("why_this_matters") or ""
        if "<" in val and ">" in val:
            to_update.append((row["paper_id"], strip_html(val)))

    print(f"Found {len(to_update)} rows with HTML in why_this_matters")

    for paper_id, clean_text in to_update:
        print(f"  Cleaning {paper_id[:40]}…")
        client.table("items").update({"why_this_matters": clean_text}).eq("paper_id", paper_id).execute()

    print("Done.")


if __name__ == "__main__":
    main()
