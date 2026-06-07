import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# ==========================================
# TEJAS ANAND - BROADENED STACK MATRIX
# ==========================================
CORE_STACK = ['databricks', 'dbt', 'aws', 'glue', 'unity catalog', 'python', 'sql', 'mcp', 'model context protocol']
SUPPORTING_STACK = ['airflow', 'redshift', 'athena', 'spark', 'pyspark', 'medallion', 'delta lake', 'terraform', 'cloudformation', 'llm']

def calculate_precision_score(title, full_desc):
    title_lower = title.lower()
    desc_lower = full_desc.lower()
    
    # BROADENED: Added 'architect', 'developer', 'senior' to capture more roles
    data_anchors = ['data', 'analytics', 'etl', 'elt', 'dbt', 'databricks', 'pyspark', 'warehouse', 'pipeline', 'bi ', 'intelligence', 'architect', 'developer', 'engineer']
    
    # DEBUG: See what is being processed
    if not any(anchor in title_lower for anchor in data_anchors):
        return 0 
        
    score = 0
    for tech in CORE_STACK:
        if tech in title_lower: score += 35
        elif tech in desc_lower: score += 15
    for tech in SUPPORTING_STACK:
        if tech in title_lower: score += 20
        elif tech in desc_lower: score += 8
            
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
                
                # DEBUG PRINT: Uncomment the next line to see what the script is actually finding
                # for job in jobs_array: print(f"DEBUG: Found Job Title: {job.get('title')}")
                
                for job in jobs_array:
                    title = job.get('title', '')
                    raw_desc = job.get('description', '')
                    loc = job.get('location', '') if 'arbeitnow' in url else job.get('candidate_required_location', '')
                    
                    leads.append({
                        "title": title, "company": job.get('company_name', 'Tech Co'),
                        "url": job.get('url', ''), "loc": loc or "Remote",
                        "full_raw_description": raw_desc,
                        "employment_type": "Full-Time", "workplace_type": "Remote"
                    })
        except Exception as e:
            print(f"API Error: {e}")
    return leads

def run_agent():
    print("Running diagnostic pipeline...")
    raw_jobs = fetch_aggregator_apis()
    
    # FALLBACK: If no jobs found, reduce threshold to 20 to verify connectivity
    threshold = 45 
    
    validated_payloads = []
    for job in raw_jobs:
        score = calculate_precision_score(job['title'], job['full_raw_description'])
        if score >= threshold:
            validated_payloads.append({
                "title": job['title'], "company": job['company'], "url": job['url'],
                "loc": job['loc'], "desc": "Relevant opportunity.",
                "source": "Aggregator", "employment_type": job['employment_type'],
                "workplace_type": job['workplace_type'], "tejas_score": score,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
    with open('jobs.json', 'w') as f:
        json.dump(validated_payloads, f, indent=4)
        
    print(f"Curated {len(validated_payloads)} jobs. (Threshold: {threshold})")

if __name__ == "__main__":
    run_agent()
