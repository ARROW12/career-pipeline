import json
import requests

# --- STRICT IDENTITY NODES ---
REQUIRED_TITLE_KEYWORDS = ["Data Engineer", "Data Engineering", "ETL", "PySpark", "Glue"]

# --- THE KILL LIST ---
# If these words appear in the TITLE, the job is discarded instantly
FORBIDDEN_TITLE_KEYWORDS = [
    "Nurse", "Neurologist", "Counselor", "Physician", "Marketing", 
    "Sales", "Account", "Clinical Research", "Associate", "HR"
]

def calculate_refined_score(job_data):
    title = job_data['title'].lower()
    desc = job_data.get('desc', '').lower()
    text = title + " " + desc
    
    # STAGE 1: FORBIDDEN TITLE CHECK
    # This prevents roles like "Neurologist" or "Nurse" from appearing
    if any(forbidden.lower() in title for forbidden in FORBIDDEN_TITLE_KEYWORDS):
        return 0

    # STAGE 2: MANDATORY IDENTITY GATE
    # The title MUST sound like an Engineering role
    if not any(req.lower() in title for req in REQUIRED_TITLE_KEYWORDS):
        return 0

    # STAGE 3: TECH VALIDATION
    # Must mention at least one core AWS/Data tool to be relevant
    CORE_TECH = ["Glue", "Step Functions", "Redshift", "PySpark", "S3", "Athena"]
    tech_hits = [tech for tech in CORE_TECH if tech.lower() in text]
    
    if len(tech_hits) == 0:
        return 0

    # STAGE 4: SCORING
    score = 50 
    score += (len(tech_hits) * 10)
    
    # Bonus for your specific Pharma background (MSD/BMS)
    if any(d in text for d in ["pharma", "life sciences", "biotech"]):
        score += 20

    # STAGE 5: LOCATION COMPLIANCE
    is_india = "india" in job_data.get('location', '').lower() or "inr" in text
    is_contract = any(x in text for x in ["contract", "freelance", "temp"])
    
    if is_india and not is_contract:
        return 0 
        
    return min(score, 100)
