import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# ==========================================
# TEJAS ANAND - CORE PROFESSIONAL TARGET MATRIX
# ==========================================
TEJAS_LEXICON = [
    "aws", "glue", "lake formation", "athena", "step functions", "cloudformation",
    "databricks", "unity catalog", "dbt", "medallion", "delta lake", "pyspark",
    "python", "sql", "mcp", "model context protocol", "langchain", "langgraph",
    "airflow", "redshift", "terraform", "llm", "etl", "analytics engineer", "data engineer"
]

def clean_text(text):
    if not text:
        return ""
    clean = BeautifulSoup(text, "html.parser").get_text()
    return re.sub(r'\s+', ' ', clean).strip()

def classify_job_attributes(title, desc, loc):
    combined = f"{title} {desc} {loc}".lower()
    
    is_contract = any(k in combined for k in ["contract", "freelance", "temp", "c2c", "consultant", "b2b"])
    employment_type = "Freelance/Contract" if is_contract else "Full-Time"
    
    if "hybrid" in combined:
        workplace_type = "Hybrid"
    elif any(k in combined for k in ["remote", "work from home", "wfh", "anywhere", "wfa", "global"]):
        workplace_type = "Remote"
    else:
        workplace_type = "On-site"
        
    return employment_type, workplace_type

def calculate_precision_score(title, full_desc):
    """Evaluates text weights against your stack prior to string trimming."""
    match_points = 0
    t_blob = title.lower()
    d_blob = full_desc.lower()
    
    for token in TEJAS_LEXICON:
        if token in t_blob: 
            match_points += 5
        if token in d_blob: 
            match_points += 1
            
    if match_points == 0:
        return 0
        
    # Scale scoring curve organically
    score_percentage = min(round((match_points / 15) * 100), 100)
    return score_percentage

def fetch_aggregator_apis():
    leads = []
    urls = [
        "https://www.arbeitnow.com/api/job-board-api",
        "https://remotive.com/api/remote-jobs?category=data"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, timeout=12)
            if res.status_code == 200:
                data = res.json()
                jobs_array = data.get('data', []) if 'arbeitnow' in url else data.get('jobs', [])
                
                for job in jobs_array:
                    title = job.get('title', '')
                    raw_desc = job.get('description', '')
                    loc = job.get('location', '') if 'arbeitnow' in url else job.get('candidate_required_location', '')
                    
                    emp_type, work_type = classify_job_attributes(title, raw_desc, loc)
                    
                    leads.append({
                        "title": title,
                        "company": job.get('company_name', 'Tech Enterprise'),
                        "url": job.get('url', ''),
                        "loc": loc if loc else "India / Remote",
                        "full_raw_description": raw_desc, # Saved for context matching
                        "source": "Global Network Stream",
                        "employment_type": emp_type,
                        "workplace_type": work_type
                    })
        except Exception as e:
            print(f"Network reading skip on endpoint ({url}): {e}")
    return leads

def run_agent():
    print("Awakening specialized pipeline engine...")
    raw_jobs = fetch_aggregator_apis()
    
    validated_payloads = []
    unique_signatures = set()
    
    for job in raw_jobs:
        signature = f"{job['title']}-{job['company']}".lower()
        if signature in unique_signatures:
            continue
        unique_signatures.add(signature)
        
        # 1. Score against full un-truncated text block
        score = calculate_precision_score(job['title'], job['full_raw_description'])
        
        # 2. Extract and assign location filters
        loc_lower = job['loc'].lower()
        is_india = any(city in loc_lower for city in ['india', 'hyderabad', 'bangalore', 'bengaluru', 'pune', 'mumbai', 'noida', 'gurgaon', 'delhi', 'chennai'])
        is_global_wfa = any(term in loc_lower for term in ['global', 'anywhere', 'worldwide', 'wfa'])
        
        keep_job = False
        
        # Full-Time Rule: Strictly India-located or explicit remote
        if job['employment_type'] == "Full-Time":
            if is_india or job['workplace_type'] == "Remote":
                keep_job = True
                
        # Freelance Rule: Boundaryless remote contracts
        elif job['employment_type'] == "Freelance/Contract":
            if job['workplace_type'] == "Remote" or is_global_wfa:
                keep_job = True

        if keep_job and score > 0:
            # Drop structural overhead now that validation is complete
            clean_summary = clean_text(job['full_raw_description'])
            
            validated_payloads.append({
                "title": job['title'],
                "company": job['company'],
                "url": job['url'],
                "loc": job['loc'],
                "desc": clean_summary[:350] + "..." if len(clean_summary) > 350 else clean_summary,
                "source": job['source'],
                "employment_type": job['employment_type'],
                "workplace_type": job['workplace_type'],
                "tejas_score": score,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
    # Re-rank by best architectural fit
    validated_payloads.sort(key=lambda x: x['tejas_score'], reverse=True)
    
    with open('jobs.json', 'w') as f:
        json.dump(validated_payloads, f, indent=4)
        
    print(f"Data pipeline compilation completely synced. Outfitted {len(validated_payloads)} accurate targets.")

if __name__ == "__main__":
    run_agent()
