import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def clean_text(text):
    if not text:
        return ""
    clean = BeautifulSoup(text, "html.parser").get_text()
    return re.sub(r'\s+', ' ', clean).strip()

def classify_job_attributes(title, desc, loc):
    combined = f"{title} {desc} {loc}".lower()
    
    is_contract = any(k in combined for k in ["contract", "freelance", "temp", "c2c", "day rate", "consultant", "gig"])
    employment_type = "Freelance/Contract" if is_contract else "Full-Time"
    
    if "hybrid" in combined:
        workplace_type = "Hybrid"
    elif any(k in combined for k in ["remote", "work from home", "wfh", "anywhere", "wfa", "worldwide", "global"]):
        workplace_type = "Remote"
    else:
        workplace_type = "On-site"
        
    return employment_type, workplace_type

def fetch_arbeitnow_jobs():
    leads = []
    api_url = "https://www.arbeitnow.com/api/job-board-api"
    try:
        response = requests.get(api_url, timeout=12)
        if response.status_code == 200:
            data = response.json()
            for job in data.get('data', []):
                title = job.get('title', '')
                desc = job.get('description', '')
                emp_type, work_type = classify_job_attributes(title, desc, job.get('location', ''))
                
                if job.get('remote', False):
                    work_type = "Remote"
                    
                leads.append({
                    "title": title,
                    "company": job.get('company_name', 'Tech Enterprise'),
                    "url": job.get('url', ''),
                    "loc": job.get('location', 'Global / Remote'),
                    "desc": clean_text(desc)[:400] + "...",
                    "source": "Arbeitnow Index",
                    "employment_type": emp_type,
                    "workplace_type": work_type
                })
    except Exception as e:
        print(f"Error fetching from Arbeitnow: {e}")
    return leads

def fetch_rss_aggregators():
    leads = []
    # Removed the specific '?category=data' to pull the full global tech stream
    streams = [
        {"url": "https://remotive.com/api/remote-jobs", "source": "Remotive Global"},
        {"url": "https://www.reddit.com/r/cscareerquestions/new/.rss", "source": "Reddit Tech Network"}
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AssetPipeline/3.0"}
    
    for stream in streams:
        try:
            res = requests.get(stream["url"], headers=headers, timeout=12)
            if res.status_code != 200:
                continue
                
            if "json" in res.headers.get("Content-Type", "").lower():
                data = res.json()
                for job in data.get("jobs", []):
                    title = job.get("title", "")
                    desc = job.get("description", "")
                    emp_type, work_type = classify_job_attributes(title, desc, job.get("candidate_required_location", ""))
                    leads.append({
                        "title": title,
                        "company": job.get("company_name", "Global Operation"),
                        "url": job.get("url", ""),
                        "loc": job.get("candidate_required_location", "Remote / Global"),
                        "desc": clean_text(desc)[:400] + "...",
                        "source": stream["source"],
                        "employment_type": emp_type,
                        "workplace_type": work_type
                    })
            else:
                soup = BeautifulSoup(res.content, "xml")
                for entry in soup.find_all("entry"):
                    title = entry.find("title").text if entry.find("title") else ""
                    content = entry.find("content").text if entry.find("content") else ""
                    link = entry.find("link")["href"] if entry.find("link") else ""
                    
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
            print(f"Failed processing source {stream['url']}: {e}")
    return leads

def run_agent():
    print("Agent Active: Executing generalized tech industry sweep...")
    all_live_opportunities = fetch_arbeitnow_jobs() + fetch_rss_aggregators()
    
    validated_payloads = []
    unique_signatures = set()
    
    # Generalized anchor check to confirm it's an engineering/tech/corporate role
    tech_anchors = ["engineer", "developer", "analyst", "data", "software", "architect", "consultant", "manager", "lead", "programmer", "tech"]
    
    for job in all_live_opportunities:
        signature = f"{job['title']}-{job['company']}".lower()
        if signature in unique_signatures:
            continue
        unique_signatures.add(signature)
        
        combined_text = f"{job['title']} {job['desc']}".lower()
        if any(anchor in combined_text for anchor in tech_anchors):
            job['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            validated_payloads.append(job)
            
    with open('jobs.json', 'w') as f:
        json.dump(validated_payloads, f, indent=4)
        
    print(f"Sync complete. Compiled {len(validated_payloads)} total active tech opportunities.")

if __name__ == "__main__":
    run_agent()
