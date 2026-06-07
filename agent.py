import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# ==========================================
# TEJAS ANAND - PROFESSIONAL DNA MATRIX
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

def calculate_tejas_match_score(title, desc):
    """Scores opportunities strictly against Tejas's resume keywords."""
    match_points = 0
    title_blob = title.lower()
    desc_blob = desc.lower()
    
    for token in TEJAS_LEXICON:
        if token in title_blob: match_points += 4
        if token in desc_blob: match_points += 1
        
    if match_points == 0:
        return 0
    
    # Normalize score based on lexicon size
    score_percent = Math.min(round((match_points / (len(TEJAS_LEXICON) * 1.2)) * 100), 100)
    return score_percent

# --- SCRAPER MODULES ---

def fetch_aggregator_apis():
    """Pulls from open boards that aggregate Indeed and smaller tech boards."""
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
                    desc = job.get('description', '')
                    loc = job.get('location', '') if 'arbeitnow' in url else job.get('candidate_required_location', '')
                    
                    emp_type, work_type = classify_job_attributes(title, desc, loc)
                    
                    leads.append({
                        "title": title,
                        "company": job.get('company_name', 'Tech Co'),
                        "url": job.get('url', ''),
                        "loc": loc if loc else "Remote",
                        "desc": clean_text(desc)[:400] + "...",
                        "source": "Aggregator API",
                        "employment_type": emp_type,
                        "workplace_type": work_type
                    })
        except Exception as e:
            print(f"API Error ({url}): {e}")
    return leads

def fetch_rss_streams():
    """Pulls tech-specific feeds including Reddit and RSS bridges for LinkedIn/Naukri."""
    leads = []
    streams = [
        {"url": "https://www.reddit.com/r/dataengineering/new/.rss", "source": "Reddit Data Eng"}
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TejasPipeline/8.0"}
    
    for stream in streams:
        try:
            res = requests.get(stream["url"], headers=headers, timeout=12)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "xml")
                for entry in soup.find_all("entry"):
                    title = entry.find("title").text if entry.find("title") else ""
                    content = entry.find("content").text if entry.find("content") else ""
                    link = entry.find("link")["href"] if entry.find("link") else ""
                    
                    if "hiring" in title.lower() or "job" in title.lower():
                        emp_type, work_type = classify_job_attributes(title, content, "Global")
                        leads.append({
                            "title": clean_text(title),
                            "company": "Network Direct",
                            "url": link,
                            "loc": "Global / Remote",
                            "desc": clean_text(content)[:400] + "...",
                            "source": stream["source"],
                            "employment_type": emp_type,
                            "workplace_type": work_type
                        })
        except Exception as e:
            print(f"RSS Error: {e}")
    return leads

def run_agent():
    print("Initiating pipeline for Tejas Anand...")
    raw_jobs = fetch_aggregator_apis() + fetch_rss_streams()
    
    validated_payloads = []
    unique_signatures = set()
    
    for job in raw_jobs:
        signature = f"{job['title']}-{job['company']}".lower()
        if signature in unique_signatures:
            continue
        unique_signatures.add(signature)
        
        # 1. Calculate Tejas Match Score
        # Native Python implementation of the scoring logic
        match_points = 0
        title_blob = job['title'].lower()
        desc_blob = job['desc'].lower()
        
        for token in TEJAS_LEXICON:
            if token in title_blob: match_points += 4
            if token in desc_blob: match_points += 1
            
        score = min(round((match_points / (len(TEJAS_LEXICON) * 1.5)) * 100), 100) if match_points > 0 else 0
        job['tejas_score'] = score
        
        # 2. Enforce Tejas Strict Location & Contract Rules
        is_india = any(loc in job['loc'].lower() for loc in ['india', 'hyderabad', 'bangalore', 'pune', 'mumbai', 'ncr', 'gurgaon'])
        is_wfa = any(term in job['loc'].lower() for term in ['global', 'anywhere', 'worldwide', 'wfa', 'remote'])
        
        keep_job = False
        
        # Full-Time Rule: Must be in India OR fully Remote
        if job['employment_type'] == "Full-Time" and (is_india or job['workplace_type'] == "Remote"):
            keep_job = True
            
        # Freelance Rule: Must be explicitly Global/Remote
        if job['employment_type'] == "Freelance/Contract" and job['workplace_type'] == "Remote" and is_wfa:
            keep_job = True

        # Must have at least some relevance to your resume
        if keep_job and score > 0:
            job['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            validated_payloads.append(job)
            
    # Sort by highest relevance to your specific resume
    validated_payloads.sort(key=lambda x: x['tejas_score'], reverse=True)
    
    with open('jobs.json', 'w') as f:
        json.dump(validated_payloads, f, indent=4)
        
    print(f"Sync complete. Curated {len(validated_payloads)} high-precision opportunities.")

if __name__ == "__main__":
    run_agent()
