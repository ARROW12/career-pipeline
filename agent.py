import json
import requests
from datetime import datetime

# --- HIGH-PRECISION CONFIGURATION ---
# Core skills from your MSD/BMS experience
CORE_TECH = ["AWS", "Glue", "PySpark", "Step Functions", "Lake Formation", "Redshift"]
AI_TECH = ["LangGraph", "LangChain", "LLM", "Prompt Engineering"]
GENERAL_TECH = ["Python", "SQL", "Airflow", "ETL", "Databricks"]

def get_match_score(text):
    text = text.lower()
    score = 0
    # Core AWS/Data skills are worth 15 points each
    for tech in CORE_TECH:
        if tech.lower() in text: score += 15
    # AI skills are worth 20 points (high priority for you)
    for tech in AI_TECH:
        if tech.lower() in text: score += 20
    # General skills worth 5 points
    for tech in GENERAL_TECH:
        if tech.lower() in text: score += 5
    return score

def fetch_jobs():
    processed_jobs = []
    
    # Source A: Remote OK (High-end tech roles)
    try:
        rok_url = "https://remoteok.com/api"
        # RemoteOK requires a User-Agent header
        rok_res = requests.get(rok_url, headers={'User-Agent': 'Mozilla/5.0'})
        rok_data = rok_res.json()
        for job in rok_data[1:]: # Skip the first legal item
            desc = job.get('description', '') + job.get('position', '')
            score = get_match_score(desc)
            if score >= 30: # Only keep high-match engineering roles
                processed_jobs.append({
                    "title": job.get('position'),
                    "company": job.get('company'),
                    "url": job.get('url'),
                    "match": min(score, 100),
                    "tags": [t for t in (CORE_TECH + AI_TECH) if t.lower() in desc.lower()][:4],
                    "location": "Remote (RemoteOK)",
                    "salary": f"${job.get('salary_min', 'Check listing')}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    except: print("RemoteOK Sync Failed")

    # Source B: Adzuna (Broad market aggregator)
    # Note: Using Adzuna requires a free API key from developer.adzuna.com
    # Replace YOUR_ID and YOUR_KEY if you get them, otherwise this block skips
    ADZUNA_ID = "OPTIONAL_ID"
    ADZUNA_KEY = "OPTIONAL_KEY"
    if ADZUNA_ID != "OPTIONAL_ID":
        try:
            adz_url = f"https://api.adzuna.com/v1/api/jobs/us/search/1?app_id={ADZUNA_ID}&app_key={ADZUNA_KEY}&what=Data%20Engineer%20AWS&content-type=application/json"
            adz_res = requests.get(adz_url).json()
            for job in adz_res.get('results', []):
                score = get_match_score(job.get('description'))
                if score >= 25:
                    processed_jobs.append({
                        "title": job.get('title'),
                        "company": job.get('company', {}).get('display_name'),
                        "url": job.get('redirect_url'),
                        "match": min(score, 100),
                        "tags": ["AWS", "Remote"],
                        "location": "Global / US",
                        "salary": "Market Rate",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
        except: print("Adzuna Sync Failed")

    # Final Filter: Deduplicate and Sort
    processed_jobs.sort(key=lambda x: x['match'], reverse=True)
    
    with open('jobs.json', 'w') as f:
        json.dump(processed_jobs[:30], f, indent=4)

if __name__ == "__main__":
    fetch_jobs()
