import json
import requests
from datetime import datetime

# --- TARGET PROFILE NODES ---
CORE_STACK = ["Glue", "Step Functions", "Lake Formation", "Redshift", "PySpark"]
AI_STACK = ["LangGraph", "LangChain", "LLM"]
DOMAIN = ["Pharma", "Clinical", "Life Sciences", "Healthcare"]

def calculate_graph_score(job_data):
    score = 0
    text = (job_data['title'] + " " + job_data['desc']).lower()
    
    # 1. Tech Affinity (Edge Weight)
    for tech in CORE_STACK:
        if tech.lower() in text: score += 20
    for tech in AI_STACK:
        if tech.lower() in text: score += 15
        
    # 2. Domain Affinity (High Priority for MSD/BMS background)
    for d in DOMAIN:
        if d.lower() in text: score += 25
        
    # 3. Location/Contract Logic
    is_india = "india" in job_data['loc'].lower() or "inr" in text
    is_contract = "contract" in text or "freelance" in text or "temporary" in text
    
    # If India, strictly require Contract
    if is_india and not is_contract:
        return 0
    
    return score

def fetch_pipeline():
    leads = []
    
    # Tier 1: Specialized Remote APIs
    try:
        # RemoteOK for high-end Global roles
        rok = requests.get("https://remoteok.com/api", headers={'User-Agent': 'Mozilla/5.0'}).json()
        for job in rok[1:]:
            s = calculate_graph_score({'title': job.get('position'), 'desc': job.get('description'), 'loc': 'Remote'})
            if s > 35:
                leads.append({"title": job.get('position'), "company": job.get('company'), "url": job.get('url'), "match": min(s, 100), "loc": "Remote Global", "type": "Remote/Contract"})
    except: pass

    # Tier 2: Reddit Scraping (r/dataengineering, r/remotework, r/forhire)
    subreddits = ["dataengineering", "forhire", "remotework"]
    for sub in subreddits:
        try:
            res = requests.get(f"https://www.reddit.com/r/{sub}/new.json?limit=25", headers={'User-Agent': 'CareerPipelineAgent/1.0'}).json()
            for post in res['data']['children']:
                p = post['data']
                if "hiring" in p['title'].lower() or "[hiring]" in p['title'].lower():
                    s = calculate_graph_score({'title': p['title'], 'desc': p['selftext'], 'loc': 'Reddit/Remote'})
                    if s > 30:
                        leads.append({"title": p['title'][:60]+"...", "company": "Reddit User", "url": f"https://reddit.com{p['permalink']}", "match": s, "loc": f"r/{sub}", "type": "Community Lead"})
        except: pass

    # Deduplicate and prioritize
    leads.sort(key=lambda x: x['match'], reverse=True)
    with open('jobs.json', 'w') as f:
        json.dump(leads[:50], f, indent=4)

if __name__ == "__main__":
    fetch_pipeline()
