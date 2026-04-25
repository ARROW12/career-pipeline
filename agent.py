import json
import requests

# --- HARD CONSTRAINTS ---
# If a job doesn't have at least ONE of these, it is discarded immediately
CORE_TECH_MUST_HAVE = ["Glue", "Step Functions", "Lake Formation", "PySpark", "Redshift"]

# Senior-level keywords to ensure you aren't seeing entry-level roles
SENIORITY_FILTER = ["Manager", "Senior", "Lead", "Architect", "Principal"]

# Negative filters to prune irrelevant healthcare/non-tech roles
EXCLUDE_KEYWORDS = [
    "Nurse", "Doctor", "Neurologist", "Patient", "Customer Success", 
    "Marketing", "SEO", "Sales", "Intern", "Junior", "Entry Level"
]

def refined_graph_score(job_data):
    title = job_data['title'].lower()
    desc = job_data.get('desc', '').lower()
    text = title + " " + desc
    
    # STAGE 1: The "Kill" Filters
    # 1.1 Remove Blacklisted Industries/Roles
    if any(word.lower() in title for word in EXCLUDE_KEYWORDS):
        return 0
    
    # 1.2 Remove non-Senior/Manager roles (Matches your current title)
    if not any(word.lower() in title for word in SENIORITY_FILTER):
        return 0

    # STAGE 2: The Tech Validation
    # Ensure it's actually an AWS Data Engineering role
    if not any(tech.lower() in text for tech in CORE_TECH_MUST_HAVE):
        return 0

    # STAGE 3: Location/Contract Logic
    is_india = "india" in job_data.get('loc', '').lower() or "inr" in text
    is_contract = any(x in text for x in ["contract", "freelance", "temp", "consultant"])
    
    # Per your instruction: India roles MUST be contract
    if is_india and not is_contract:
        return 0
    
    # STAGE 4: Final Scoring
    score = 50 # Base score for passing all filters
    if "pharma" in text or "clinical" in text or "life sciences" in text:
        score += 30 # Heavy boost for your industry niche (MSD/BMS)
    if "glue" in text and "step functions" in text:
        score += 20 # Bonus for your primary stack
        
    return min(score, 100)
