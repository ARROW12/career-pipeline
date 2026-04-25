import json
import re
import requests
from datetime import datetime

# --- CONFIGURATION ---
TARGET_SKILLS = ["AWS", "Glue", "PySpark", "LangGraph", "LangChain", "Airflow", "Redshift", "Python", "SQL"]
CURRENCY_SYMBOLS = [r'\$', r'€', r'£', r'AED', r'₹', r'USD', r'EUR', r'GBP']

def fetch_and_filter_jobs():
    # Using Arbeitnow Free API for demonstration (No API Key needed)
    url = "https://www.arbeitnow.com/api/job-board-api"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to fetch jobs.")
        return

    jobs_data = response.json().get('data', [])
    processed_jobs = []

    for job in jobs_data:
        description = job.get('description', '').lower()
        title = job.get('title', '')
        location = job.get('location', '')
        remote = job.get('remote', False)

        # 1. Filter: Must be Remote
        if not remote and "remote" not in location.lower() and "anywhere" not in location.lower():
            continue

        # 2. Tech Match Engine
        match_count = sum(1 for skill in TARGET_SKILLS if skill.lower() in description or skill.lower() in title.lower())
        match_score = int((match_count / len(TARGET_SKILLS)) * 100)

        # 3. Currency Check
        has_currency = any(re.search(curr, description, re.IGNORECASE) for curr in CURRENCY_SYMBOLS)

        # Only save jobs with at least a 20% match to your stack
        if match_score >= 20:
            processed_jobs.append({
                "title": title,
                "company": job.get('company_name', 'Unknown'),
                "url": job.get('url', '#'),
                "match": match_score,
                "tags": [skill for skill in TARGET_SKILLS if skill.lower() in description or skill.lower() in title.lower()][:4],
                "location": "Remote Anywhere",
                "salary": "Check Listing for $, €, £" if has_currency else "Unlisted",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    # Sort by highest match score
    processed_jobs.sort(key=lambda x: x['match'], reverse=True)

    # Save to file
    with open('jobs.json', 'w') as f:
        json.dump(processed_jobs[:30], f, indent=4) # Keep top 30 leads
    
    print(f"Successfully processed {len(processed_jobs)} matching roles.")

if __name__ == "__main__":
    fetch_and_filter_jobs()
