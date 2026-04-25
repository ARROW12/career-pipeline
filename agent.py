import json
import requests
from datetime import datetime

# --- CORE AGENT CONSTRAINTS ---
TECH_STACK = ["Glue", "Step Functions", "Lake Formation", "PySpark", "Redshift", "Athena"]
DOMAIN = ["Pharma", "Life Sciences", "Clinical"]

def llm_as_judge(job):
    """
    Evaluates job relevance against Data Engineering stack and Financial Rules.
    """
    title = job.get('title', '').lower()
    desc = job.get('desc', '').lower()
    loc = job.get('loc', '').lower()
    text = title + " " + desc

    # 1. IDENTITY GATE: Must be Data Engineering (at any seniority level)
    DE_KEYWORDS = ["data engineer", "data engineering", "etl", "analytics engineer", "big data"]
    if not any(k in title for k in DE_KEYWORDS):
        return False, 0

    # 2. FINANCIAL GATE:
    # If India, must be Contract/Freelance. If Global, must be non-INR.
    is_india = "india" in loc or "india" in title
    is_contract = any(c in text for c in ["contract", "freelance", "temp", "c2c", "day rate"])
    
    if is_india and not is_contract:
        return False, 0

    # 3. TECHNICAL ALIGNMENT
    score = 40 # Base score for passing Identity Gate
    hits = [t for t in TECH_STACK if t.lower() in text]
    score += (len(hits) * 10)
    
    # Pharma/Healthcare Domain Bonus
    if any(d.lower() in text for d in DOMAIN):
        score += 20

    return (score >= 50), score

def get_job_leads():
    """
    Placeholder for Multi-Source Fetcher (Reddit RSS, Adzuna, etc.)
    Constructs search payloads for LinkedIn, Indeed, and Naukri.
    """
    # This list would be populated by your scraping/API logic
    raw_results = [
        {
            "title": "AWS Data Engineer (Pharma Contract)",
            "company": "LifeScience Solutions",
            "url": "https://example.com/apply-pharma",
            "loc": "Remote / India",
            "desc": "Looking for AWS Glue and Step Functions experts. 6-month freelance contract.",
            "source": "Reddit"
        },
        {
            "title": "Senior Data Engineer (Global)",
            "company": "TechStream Global",
            "url": "https://example.com/global-de",
            "loc": "Remote (EMEA/US)",
            "desc": "Build scalable ETL with Redshift and Athena. Paid in USD.",
            "source": "LinkedIn"
        }
    ]
    return raw_results

def run_agent():
    print("Agent: Commencing Global Sourcing...")
    leads = get_job_leads()
    validated_jobs = []

    for job in leads:
        is_perfect, final_score = llm_as_judge(job)
        if is_perfect:
            job['match'] = final_score
            job['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            job['type'] = "USD/Global" if "india" not in job['loc'].lower() else "INR Contract"
            validated_jobs.append(job)

    # Sort by match quality
    validated_jobs.sort(key=lambda x: x['match'], reverse=True)

    with open('jobs.json', 'w') as f:
        json.dump(validated_jobs, f, indent=4)
    print(f"Agent: Sync complete. Found {len(validated_jobs)} perfect matches.")

if __name__ == "__main__":
    run_agent()
