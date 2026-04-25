import json
import requests

# --- CORE IDENTITY NODES ---
# A job MUST contain at least one of these to even be considered
REQUIRED_IDENTITY = ["Data Engineer", "Data Engineering", "Analytics Engineer", "ETL Engineer"]

# HIGH-WEIGHT TECH STACK
CORE_TECH = ["Glue", "Step Functions", "Lake Formation", "Redshift", "PySpark", "EMR", "Athena"]

def calculate_refined_score(job_data):
    title = job_data['title'].lower()
    desc = job_data.get('desc', '').lower()
    text = title + " " + desc
    
    # STAGE 1: HARD IDENTITY GATE
    # If the title doesn't sound like a Data Engineer role, it's 0.
    if not any(role.lower() in title for role in REQUIRED_IDENTITY):
        return 0

    # STAGE 2: NEGATIVE KEYWORD GATE
    # Kill common irrelevant roles that might slip through
    IRRELEVANT = ["Marketing", "Nurse", "Counselor", "Doctor", "Sales", "Neurologist", "Recruiter"]
    if any(word.lower() in title for word in IRRELEVANT):
        return 0

    # STAGE 3: TECH WEIGHTING
    score = 40  # Base score for passing identity gate
    tech_hits = [tech for tech in CORE_TECH if tech.lower() in text]
    score += (len(tech_hits) * 15)
    
    # Bonus for Pharma/Life Sciences (Your MSD/BMS background)
    if any(d in text for d in ["pharma", "clinical", "life sciences"]):
        score += 20

    # STAGE 4: LOCATION & CONTRACT RULE
    is_india = "india" in job_data.get('loc', '').lower() or "inr" in text
    is_contract = any(x in text for x in ["contract", "freelance", "temp", "consultant"])
    
    if is_india and not is_contract:
        return 0 # Per instruction: India roles MUST be contract
        
    return min(score, 100)
