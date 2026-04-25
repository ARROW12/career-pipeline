import json
import re
import requests
from datetime import datetime

TARGET_SKILLS = ["AWS", "Glue", "PySpark", "LangGraph", "LangChain", "Airflow", 
                 "Redshift", "Python", "SQL", "Data", "ETL", "Cloud", "Step Functions"]
CURRENCY_SYMBOLS = [r'\$', r'€', r'£', r'AED', r'₹', r'USD', r'EUR', r'GBP']

def fetch_and_filter_jobs():
    url = "https://www.arbeitnow.com/api/job-board-api"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    jobs_data = response.json().get('data', [])
    processed_jobs = []

    for job in jobs_data:
        description = job.get('description', '').lower()
        title = job.get('title', '')
        location = job.get('location', '')
        is_remote = job.get('remote', True) or "remote" in location.lower()

        if not is_remote:
            continue

        found_tags = [skill for skill in TARGET_SKILLS if skill.lower() in description or skill.lower() in title.lower()]
        if len(found_tags) >= 1:
            match_score = int((len(found_tags) / len(TARGET_SKILLS)) * 100)
            has_currency = any(re.search(curr, description, re.IGNORECASE) for curr in CURRENCY_SYMBOLS)

            processed_jobs.append({
                "title": title,
                "company": job.get('company_name', 'Unknown'),
                "url": job.get('url', '#'),
                "match": min(match_score + 20, 100),
                "tags": found_tags[:5],
                "location": "Remote",
                "salary": "Multi-currency listing" if has_currency else "Competitive",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

    processed_jobs.sort(key=lambda x: x['match'], reverse=True)
    with open('jobs.json', 'w') as f:
        json.dump(processed_jobs[:40], f, indent=4) 

if __name__ == "__main__":
    fetch_and_filter_jobs()