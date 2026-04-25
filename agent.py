import json
import requests
from datetime import datetime

# --- CONFIGURATION ---
# Titles must contain one of these
REQUIRED_TITLES = ["Data Engineer", "Data Engineering", "ETL", "PySpark", "Glue", "Big Data"]

# Titles containing these are deleted immediately
FORBIDDEN_TITLES = ["Nurse", "Neurologist", "Counselor", "Physician", "Marketing", "Sales", "HR", "Recruiter"]

def calculate_refined_score(job_data):
    title = job_data.get('title', '').lower()
    desc = job_data.get('desc', '').lower()
    text = title + " " + desc
    
    # STAGE 1: FORBIDDEN GATE (Prevents irrelevant roles from screenshots)
    if any(word.lower() in title for word in FORBIDDEN_TITLES):
        return 0

    # STAGE 2: IDENTITY GATE (Ensures it's an engineering role)
    if not any(word.lower() in title for word in REQUIRED_TITLES):
        return 0

    # STAGE 3: TECH VALIDATION (Must have at least one core tool)
    CORE_TECH = ["Glue", "Step Functions", "Lake Formation", "Redshift", "PySpark", "S3", "Athena"]
    found_tech = [t for t in CORE_TECH if t.lower() in text]
    if not found_tech:
        return 0

    # STAGE 4: SCORING
    score = 50
    score += (len(found_tech) * 10)
    if any(d in text for d in ["pharma", "life sciences", "clinical"]):
        score += 20
        
    return min(score, 100), found_tech

def fetch_jobs():
    # Example using Adzuna (You will need to use your actual sourcing logic here)
    # This is a placeholder for the logic that populates 'all_leads'
    all_leads = [] 
    processed = []
    
    for lead in all_leads:
        score, tags = calculate_refined_score(lead)
        if score >= 40:
            lead['match'] = score
            lead['tags'] = tags
            lead['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            processed.append(lead)
            
    processed.sort(key=lambda x: x['match'], reverse=True)
    
    with open('jobs.json', 'w') as f:
        json.dump(processed[:30], f, indent=4)

if __name__ == "__main__":
    fetch_jobs()
