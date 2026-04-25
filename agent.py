import json
import os
import requests
from datetime import datetime

# --- YOUR VIRTUAL RECRUITER PROFILE ---
USER_PROFILE = {
    "role": "Data Engineer / Manager",
    "must_have": ["AWS Glue", "Step Functions", "PySpark", "Lake Formation"],
    "domain_bonus": ["Pharma", "Life Sciences", "Clinical"],
    "payment_logic": "If Location == India, MUST be Contract/Freelance. If Global, any currency except INR."
}

def llm_judge(job_title, job_desc, location):
    """
    Simulates the 'LLM as Judge' logic. 
    In a full LangGraph setup, this would be an API call to Gemini/GPT-4.
    """
    title = job_title.lower()
    desc = job_desc.lower()
    
    # 1. HARD FILTER: Role Identity
    if not any(x in title for x in ["data engineer", "etl", "analytics engineer"]):
        return False, 0

    # 2. HARD FILTER: Payment/Contract Logic
    is_india = "india" in location.lower() or "india" in title
    is_contract = any(x in desc or x in title for x in ["contract", "freelance", "temp", "c2c"])
    
    if is_india and not is_contract:
        return False, 0

    # 3. AI SCORING: Stack Alignment
    score = 0
    weights = {"glue": 25, "step functions": 25, "pyspark": 15, "pharma": 20}
    for tech, points in weights.items():
        if tech in desc or tech in title:
            score += points
            
    return (score >= 40), score

def fetch_and_process():
    # Source: Combined Scraper (Placeholder for Reddit/LinkedIn/Indeed APIs)
    raw_leads = [
        {"title": "Data Engineer (Contract)", "desc": "AWS Glue, Step Functions...", "loc": "Bangalore", "url": "..."},
        {"title": "Senior Data Engineer", "desc": "Global Remote, paid in USD...", "loc": "Remote", "url": "..."}
    ]
    
    perfect_matches = []
    for lead in raw_leads:
        is_match, final_score = llm_judge(lead['title'], lead['desc'], lead['loc'])
        if is_match:
            lead['match'] = final_score
            lead['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            perfect_matches.append(lead)

    with open('jobs.json', 'w') as f:
        json.dump(perfect_matches, f, indent=4)

if __name__ == "__main__":
    fetch_and_process()
