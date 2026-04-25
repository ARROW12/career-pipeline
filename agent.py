import json
import requests
from datetime import datetime

# --- PROFILE-BASED PRIORITIZATION ---
# [span_8](start_span)[span_9](start_span)[span_10](start_span)Extracted from your resume: AWS native, Clinical/Pharma background[span_8](end_span)[span_9](end_span)[span_10](end_span)
RESUME_KEYWORDS = {
    "CRITICAL": ["Glue", "Step Functions", "PySpark", "Lake Formation", "Redshift"],
    "ADVANCED": ["LangGraph", "LangChain", "Airflow", "Infrastructure-as-Code", "Terraform"],
    "DOMAIN": ["Clinical", "Pharma", "HIPAA", "Life Sciences", "GxP"]
}

def calculate_priority(title, desc):
    score = 0
    text = (title + " " + desc).lower()
    # [span_11](start_span)Prioritize your core AWS stack[span_11](end_span)
    for word in RESUME_KEYWORDS["CRITICAL"]:
        if word.lower() in text: score += 20
    # [span_12](start_span)Add points for your new LLM interests[span_12](end_span)
    for word in RESUME_KEYWORDS["ADVANCED"]:
        if word.lower() in text: score += 15
    # [span_13](start_span)[span_14](start_span)Boost roles in Pharma/Clinical (your specialized domain)[span_13](end_span)[span_14](end_span)
    for word in RESUME_KEYWORDS["DOMAIN"]:
        if word.lower() in text: score += 25
    return score

def fetch_mega_pipeline():
    all_leads = []
    
    # 1. Adzuna API (Aggregates thousands of sites like Indeed/LinkedIn)
    # Get a free API Key at developer.adzuna.com
    ADZUNA_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": "YOUR_ADZUNA_ID", 
        "app_key": "YOUR_ADZUNA_KEY",
        "what": "Data Engineer AWS Glue Remote",
        "content-type": "application/json"
    }
    
    try:
        res = requests.get(ADZUNA_URL, params=params).json()
        for job in res.get('results', []):
            desc = job.get('description', '')
            score = calculate_priority(job.get('title'), desc)
            if score > 30: # Strict relevance filter
                all_leads.append({
                    "title": job.get('title'),
                    "company": job.get('company', {}).get('display_name'),
                    "url": job.get('redirect_url'),
                    "match": min(score, 100),
                    "tags": ["Aggregated", "High Match"],
                    "location": "Remote / Hybrid",
                    "salary": "Market Rate",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    except: print("Adzuna tier failed")

    # 2. RemoteOK API (Niche tech focus)
    try:
        rok = requests.get("https://remoteok.com/api", headers={'User-Agent': 'Mozilla/5.0'}).json()
        for job in rok[1:]:
            score = calculate_priority(job.get('position'), job.get('description'))
            if score > 25:
                all_leads.append({
                    "title": job.get('position'),
                    "company": job.get('company'),
                    "url": job.get('url'),
                    "match": min(score, 100),
                    "tags": job.get('tags', [])[:3],
                    "location": "Remote",
                    "salary": f"${job.get('salary_min', 'Check listing')}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    except: print("RemoteOK tier failed")

    # Sort and save top 50 matches
    all_leads.sort(key=lambda x: x['match'], reverse=True)
    with open('jobs.json', 'w') as f:
        json.dump(all_leads[:50], f, indent=4)

if __name__ == "__main__":
    fetch_mega_pipeline()
