import requests
import json

url = "http://api.nsf.gov/services/v1/awards.json"

params = {
    "keyword": "energy defense autonomous nuclear grid",
    "fundProgramName": "SBIR Phase I",
    "dateStart": "01/01/2025",
    "printFields": "id,title,abstractText,awardeeName,piEmail,pdPIName,estimatedTotalAmt,startDate",
    "rpp": 10
}

response = requests.get(url, params=params)
data = response.json()

awards = data.get("response", {}).get("award", [])
print(f"Total results: {data['response']['metadata']['totalCount']}")
print()

for award in awards:
    print(f"Title: {award.get('title')}")
    print(f"Awardee: {award.get('awardeeName')}")
    print(f"Amount: ${award.get('estimatedTotalAmt')}")
    print(f"Abstract: {award.get('abstractText', '')[:200]}...")
    print()