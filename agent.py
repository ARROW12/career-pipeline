import json
import requests
from datetime import datetime

# --- ENHANCED LOGIC NODES ---
# Strictly targeting your 4+ years of AWS expertise
CORE_STACK = ["Glue", "Step Functions", "Lake Formation", "Redshift", "PySpark", "EMR"]
AI_STACK = ["LangGraph", "LangChain", "LLM", "Vector DB"]
PHARMA_KEYWORDS = ["Pharma", "Clinical", "Life Sciences", "GxP", "HIPAA"]

# Negative filters to remove irrelevant noise
BLACK-LIST = ["Data Analyst", "Intern", "Junior", "Entry Level", "Marketing", "Recruiter"]

def calculate_graph_score(job_data):
    score = 0
    text = (job_data['title'] + " " + job_data['desc']).lower()
    
    # 0. Immediate Filter: Blacklist
    if any(word.lower() in job_data['title'].lower() for word in BLACK-LIST):
        return 0

    # 1. AWS Mastery (High Weight for your MSD/BMS tech stack)
    for tech in CORE_STACK:
        if tech.lower() in text: score += 25
    
    # 2. Industry Moat (Pharma experience is your differentiator)
    for d in PHARMA_KEYWORDS:
        if d.lower() in text: score += 30
        
    # 3. Location/Contract Intelligence
    is_india = "india" in job_data['loc'].lower() or "inr" in text
    is_contract = any(x in text for x in ["contract", "freelance", "temporary", "day rate"])
    
    if is_india and not is_contract:
        return 0 # Per your request: India roles must be Contractual
    
    return score

def fetch_pipeline():
    leads = []
    
    # Source 1: Hacker News (YC) 'Who is Hiring'
    # High-quality tech roles, usually direct from founders/engineering managers
    try:
        hn_items = requests.get("https://hacker-news.firebaseio.com/v0/jobstories.json").json()
        for item_id in hn_items[:30]:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json").json()
            if item and 'title' in item:
                s = calculate_graph_score({'title': item['title'], 'desc': item.get('text', ''), 'loc': 'Global'})
                if s > 20:
                    leads.append({"title": item['title'], "company": "YC Startup", "url": f"https://news.ycombinator.com/item?id={item_id}", "match": s, "loc": "Remote / US", "type": "Direct Hire"})
    except: pass

    # Source 2: Adzuna (Aggregator - Free Tier)
    # This reaches Indeed, Glassdoor, and 100+ others via one API
    try:
        # Note: Replace with your credentials from developer.adzuna.com
        ADZ_ID = "YOUR_APP_ID" 
        ADZ_KEY = "YOUR_APP_KEY"
        adz_res = requests.get(f"https://api.adzuna.com/v1/api/jobs/us/search/1?app_id={AD_ID}&app_key={AD_KEY}&what=Data%20Engineer%20AWS%20Remote").json()
        for job in adz_res.get('results', []):
            s = calculate_graph_score({'title': job['title'], 'desc': job['description'], 'loc': 'Global'})
            if s > 30:
                leads.append({"title": job['title'], "company": job['company']['display_name'], "url": job['redirect_url'], "match": s, "loc": "Global", "type": "Aggregated"})
    except: pass

    leads.sort(key=lambda x: x['match'], reverse=True)
    with open('jobs.json', 'w') as f:
        json.dump(leads[:40], f, indent=4)

if __name__ == "__main__":
    fetch_pipeline()
