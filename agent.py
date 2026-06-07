import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import urllib.parse

def clean_text(text):
    if not text:
        return ""
    # Strip HTML tags and normalize whitespace
    clean = BeautifulSoup(text, "html.parser").get_text()
    return re.sub(r'\s+', ' ', clean).strip()

def classify_job_attributes(title, desc, loc):
    """
    Evaluates text context to dynamically tag employment setups.
    """
    combined = f"{title} {desc} {loc}".lower()
    
    # Identify Contract/Freelance vs Full-Time
    is_contract = any(k in combined for k in ["contract", "freelance", "temp", "c2c", "day rate", "consultant", "gig"])
    employment_type = "Freelance/Contract" if is_contract else "Full-Time"
    
    # Identify Workplace Setup
    if "hybrid" in combined:
        workplace_type = "Hybrid"
    elif any(k in combined for k in ["remote", "work from home", "wfh", "anywhere", "wfa"]):
        workplace_type = "Remote"
    else:
        workplace_type = "On-site"
        
    return employment_type, workplace_type

def fetch_arbeitnow_jobs():
    """
    Dynamically queries live tech targets via open board APIs.
    """
    leads = []
    api_url = "https://www.arbeitnow.com/api/job-board-api"
    try:
        response = requests.get(api_url, timeout=12)
        if response.status_code == 200:
            data = response.json()
            for job in data.get('data', []):
                title = job.get('title', '')
                desc = job.get('description', '')
                tags = [t.lower() for t in job.get('tags', [])]
                
                # Dynamic Filter: Ensure it targets data engineering or core cloud infrastructure
                is_de = any(k in title.lower() for k in ["data", "etl", "analytics engineer", "pyspark", "bi"])
                if is_de:
                    emp_type, work_type = classify_job_attributes(title, desc, "Remote")
                    # Force remote if tagged implicitly by API
                    if job.get('remote', False):
                        work_type = "Remote"
                        
                    leads.append({
                        "title": title,
                        "company": job.get('company_name', 'Tech Enterprise'),
                        "url": job.get('url', ''),
                        "loc": job.get('location', 'Remote / Global'),
                        "desc": clean_text(desc)[:300] + "...",
                        "source": "Arbeitnow Index",
                        "employment_type": emp_type,
                        "workplace_type": work_type
                    })
    except Exception as e:
        print(f"Error executing API call to Arbeitnow: {e}")
    return leads

def fetch_rss_aggregators():
    """
    Scrapes high-frequency global job streams and engineering communities.
    """
    leads = []
    streams = [
        {"url": "https://www.reddit.com/r/dataengineering/new/.rss", "source": "Reddit Community"},
        {"url": "https://remotive.com/api/remote-jobs?category=data", "source": "Remotive API Feed"}
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AssetPipeline/3.0"}
    
    for stream in streams:
        try:
            res = requests.get(stream["url"], headers=headers, timeout=12)
            if res.status_code != 200:
                continue
                
            # Handle JSON API vs XML RSS standard responses
            if "json" in res.headers.get("Content-Type", "").lower():
                data = res.json()
                for job in data.get("jobs", []):
                    title = job.get("title", "")
                    desc = job.get("description", "")
                    emp_type, work_type = classify_job_attributes(title, desc, job.get("candidate_required_location", ""))
                    leads.append({
                        "title": title,
                        "company": job.get("company_name", "Global Startup"),
                        "url": job.get("url", ""),
                        "loc": job.get("candidate_required_location", "Remote / Global"),
                        "desc": clean_text(desc)[:300] + "...",
                        "source": stream["source"],
                        "employment_type": emp_type,
                        "workplace_type": work_type
                    })
            else:
                # Parse XML standard RSS
                soup = BeautifulSoup(res.content, "xml")
                for entry in soup.find_all("entry"):
                    title = entry.find("title").text if entry.find("title") else ""
                    content = entry.find("content").text if entry.find("content") else ""
                    link = entry.find("link")["href"] if entry.find("link") else ""
                    
                    # Filtering criteria context rules
                    if any(k in title.lower() for k in ["hiring", "job", "contract", "remote", "engineer"]):
                        emp_type, work_type = classify_job_attributes(title, content, "Global")
                        leads.append({
                            "title": clean_text(title),
                            "company": "Network Lead",
                            "url": link,
                            "loc": "Remote / Global",
                            "desc": clean_text(content)[:300] + "...",
                            "source": stream["source"],
                            "employment_type": emp_type,
                            "workplace_type": work_type
                        })
        except Exception as e:
            print(f"Failed processing stream source {stream['url']}: {e}")
    return leads

def run_agent():
    print("Agent Core Status: Launching dynamic collection routine...")
    
    # Execute lookups concurrently across dynamic public endpoints
    all_live_opportunities = fetch_arbeitnow_jobs() + fetch_rss_aggregators()
    
    validated_payloads = []
    unique_signatures = set()
    
    for job in all_live_opportunities:
        # Generate a fingerprint signature to prevent duplicate results across indexes
        signature = f"{job['title']}-{job['company']}".lower()
        if signature in unique_signatures:
            continue
        unique_signatures.add(signature)
        
        # Enforce baseline quality filter (must contain data-centric infrastructure references)
        lexicon_pool = (job['title'] + " " + job['desc']).lower()
        core_tech = ["data", "aws", "pyspark", "glue", "redshift", "athena", "dbt", "databricks", "python", "sql", "etl"]
        
        if any(tech in lexicon_pool for tech in core_tech):
            job['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            validated_payloads.append(job)
            
    # Commit true real-time dataset straight to your repository matrix file
    with open('jobs.json', 'w') as f:
        json.dump(validated_payloads, f, indent=4)
        
    print(f"Pipeline Update Complete: Successfully harvested {len(validated_payloads)} active opportunities.")

if __name__ == "__main__":
    run_agent()
