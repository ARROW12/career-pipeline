import json
import requests

# --- UPDATED LOGIC NODES ---
CORE_TECH = ["Glue", "Step Functions", "Lake Formation", "Redshift", "PySpark", "EMR", "Athena"]
DOMAIN = ["Pharma", "Clinical", "Life Sciences", "Healthcare"]

def calculate_refined_score(job_data):
    title = job_data['title'].lower()
    desc = job_data.get('desc', '').lower()
    text = title + " " + desc
    
    # 1. Broaden Role Check: Accept any DE role, but exclude non-tech noise
    TECH_ROLES = ["data engineer", "data engineering", "analytics engineer", "cloud data engineer"]
    if not any(role in title for role in TECH_ROLES):
        return 0

    # 2. Tech Affinity: This is now the primary weight
    score = 30 # Base score for being a DE role
    tech_matches = [tech for tech in CORE_TECH if tech.lower() in text]
    score += (len(tech_matches) * 15) # +15 for every core tool found

    # 3. Industry Weighting (Pharma/Clinical expertise)
    if any(d.lower() in text for d in DOMAIN):
        score += 25

    # 4. Location/Contract Rule: Still mandatory for India
    is_india = "india" in job_data.get('loc', '').lower() or "inr" in text
    is_contract = any(x in text for x in ["contract", "freelance", "temp", "consultant", "inside ir35"])
    
    if is_india and not is_contract:
        return 0
    
    # 5. Seniority Bonus: (Optional points, but doesn't block "normal" roles)
    if any(word in title for word in ["senior", "lead", "manager", "principal"]):
        score += 10
        
    return min(score, 100)
