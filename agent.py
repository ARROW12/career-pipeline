import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# ==========================================
# TEJAS ANAND - SPECIFIC CORE STACK MATRIX
# ==========================================
CORE_STACK = ['databricks', 'dbt', 'aws', 'glue', 'unity catalog', 'python', 'sql', 'mcp', 'model context protocol']
SUPPORTING_STACK = ['airflow', 'redshift', 'athena', 'lake formation', 'spark', 'pyspark', 'medallion', 'delta lake', 'terraform', 'cloudformation', 'langchain', 'langgraph', 'llm']

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
    """Realistic evaluation matrix checking for alignment with Tejas's specific senior stack."""
    title_lower = title.lower()
    desc_lower = full_desc.lower()
    
    # GUARDRAIL 1: Title-Gate Filter. Must be data/analytics architecture focused.
    data_anchors = ['data', 'analytics', 'etl', 'elt', 'dbt', 'databricks', 'pyspark', 'warehouse', 'pipeline', 'bi ', 'intelligence']
    if not any(anchor in title_lower for anchor in data_anchors):
        return 0  # Instantly drops generic software engineering noise
        
    score = 0
    
    # Score Primary Tech Stack (Increased weights to reflect real-world JD length)
    for tech in CORE_STACK:
        if tech in title_lower: 
            score += 35
        elif tech in desc_lower: 
            score += 15
            
    # Score Secondary/Supporting Tech Stack
    for tech in SUPPORTING_STACK:
        if tech in title_lower: 
            score += 20
        elif tech in desc_lower: 
            score += 8
            
    return min(score, 100)

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
                        "full_raw_description": raw_desc,
                        "source": "Global Network Stream",
                        "employment_type": emp_type,
                        "workplace_type": work_type
                    })
        except Exception as e:
            print(f"Network reading skip on endpoint ({url}): {e}")
    return leads

def run_agent():
    print("Awakening specialized high-relevance pipeline engine...")
    raw_jobs = fetch_aggregator_apis()
    
    validated_payloads = []
    unique_signatures = set()
    
    for job in raw_jobs:
        signature = f"{job['title']}-{job['company']}".lower()
        if signature in unique_signatures:
            continue
        unique_signatures.add(signature)
        
        # Compute exact engineering stack fit
        score = calculate_precision_score(job['title'], job['full_raw_description'])
        
        # GUARDRAIL 2: Enforce Realistic 45 Point Relevance Drop-off
        # Example Pass: AWS (15) + Python (15) + SQL (15) = 45 points
        if score < 45:
            continue
            
        loc_lower = job['loc'].lower()
        desc_lower = job['full_raw_description'].lower()
        
        is_india = any(city in loc_lower or city in desc_lower for city in ['india', 'hyderabad', 'bangalore', 'bengaluru', 'pune', 'mumbai', 'noida', 'gurgaon', 'delhi', 'chennai'])
        is_global_wfa = any(term in loc_lower for term in ['global', 'anywhere', 'worldwide', 'wfa'])
        
        # GUARDRAIL 3: Anti-Leak Geofencing
        is_foreign_locked = any(country in loc_lower or f"located in {country}" in desc_lower for country in ['brazil', 'united states', 'usa', 'uk', 'united kingdom', 'canada', 'germany', 'berlin']) and not is_india

        keep_job = False
        
        if job['employment_type'] == "Full-Time":
            if (is_india or job['workplace_type'] == "Remote") and not is_foreign_locked:
                keep_job = True
        elif job['employment_type'] == "Freelance/Contract":
            if job['workplace_type'] == "Remote" or is_global_wfa:
                keep_job = True

        if keep_job:
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
            
    # Sort with pristine top matches first
    validated_payloads.sort(key=lambda x: x['tejas_score'], reverse=True)
    
    with open('jobs.json', 'w') as f:
        json.dump(validated_payloads, f, indent=4)
        
    print(f"Data pipeline processing complete. Curated {len(validated_payloads)} high-precision opportunities at >= 45% alignment.")

if __name__ == "__main__":
    run_agent()
