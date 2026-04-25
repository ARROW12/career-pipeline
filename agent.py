import json
import requests
from datetime import datetime

# --- YOUR PERSONAL RECRUITMENT PROTOCOL ---
PROFILE = {
    "tech_stack": ["AWS Glue", "Step Functions", "Lake Formation", "PySpark", "Redshift"],
    "domain": "Pharma / Life Sciences",
    "payment_rule": "If India: Must be Contract/Freelance. If Global: Must NOT be INR."
}

def ai_judge(lead):
    """
    Simulates a LangGraph Node: Evaluates a lead based on your career constraints.
    """
    title = lead.get('title', '').lower()
    desc = lead.get('description', '').lower()
    loc = lead.get('location', '').lower()
    
    # 1. Identity Check
    if not any(x in title for x in ["data engineer", "etl", "analytics engineer"]):
        return None

    # 2. Financial Constraint Logic
    is_india = "india" in loc or "india" in title
    is_contract = any(x in desc or x in title for x in ["contract", "freelance", "day rate", "c2c"])
    
    if is_india and not is_contract:
        return None # Reject India Full-Time roles

    # 3. Stack Alignment (Perfect Match Scoring)
    score = 0
    for tech in PROFILE["tech_stack"]:
        if tech.lower() in desc or tech.lower() in title:
            score += 20
            
    # Pharma Bonus (Your specialized background)
    if any(p in desc for p in ["pharma", "clinical", "msd", "bms"]):
        score += 20

    if score >= 40:
        lead['match_score'] = score
        lead['currency_type'] = "Global/Non-INR" if not is_india else "INR Contract"
        return lead
    return None

def run_pipeline():
    # Placeholder for multi-source search (Reddit, LinkedIn, Indeed, Naukri)
    # We use Google Search Dorks to aggregate these into one stream
    sources = [
        "https://www.google.com/search?q=site:linkedin.com/jobs/ \"Data Engineer\" AWS Glue Contract",
        "https://www.reddit.com/r/dataengineering/search/?q=hiring+remote&sort=new",
        "https://www.google.com/search?q=site:naukri.com \"Data Engineer\" \"Contract\""
    ]
    
    print("Agent: Commencing Multi-Source Sourcing...")
    # Sourcing logic would go here...
    
    leads = [
        # Example of a 'Perfect' result found by the agent
        {
            "title": "AWS Data Engineer (Pharma Project)",
            "company": "Global Health Tech",
            "url": "https://example.com/apply",
            "location": "Remote (Global)",
            "description": "Building ETL pipelines with AWS Glue and Step Functions. Paying in USD."
        }
    ]

    perfect_matches = []
    for l in leads:
        judged_lead = ai_judge(l)
        if judged_lead:
            judged_lead['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            perfect_matches.append(judged_lead)

    with open('jobs.json', 'w') as f:
        json.dump(perfect_matches, f, indent=4)
    print(f"Agent: Successfully validated {len(perfect_matches)} perfect matches.")

if __name__ == "__main__":
    run_pipeline()
