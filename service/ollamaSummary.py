import os
from pathlib import Path

import ollama
MODEL = "qwen2.5:0.5b"   # 352MB — very fast on low-end PC
import re

def sanitize_filename(name: str) -> str:
    # Replace invalid characters with "_"
    safe = re.sub(r'[^a-zA-Z0-9_-]', "_", name)
    # Limit length to avoid Windows path issues
    return safe[:150]
def save_file(job_json: str,link:str):
    try:
        # Convert JSON string → dict
        job = json.loads(job_json)
    except json.JSONDecodeError as e:
        print("⚠️ Model did not return valid JSON:", e)
        return
    # ✅ Keep the original link inside the JSON
    job["link"] = link

    # ✅ Create a safe filename from the link
    safe_name = sanitize_filename(link)
    filename = f"jobs/{safe_name}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(job, f, indent=2, ensure_ascii=False)

def ollamaSummary(model, job_text):
    print("Input :"+build_prompt(job_text))
    response = ollama.chat(
        model,
        messages=[{"role": "user", "content": build_prompt(job_text)}],
        options={
            "num_ctx":     2048,   # qwen2 0.5b works well with small context
            "temperature": 0.1,
            "num_thread":  4,
        }
    )
    return response["message"]["content"]

# ── Prompt ────────────────────────────────────────────────────────────────────
def build_prompt(job_text: str) -> str:
    return f"""You Have to Extract values from content and Dont have to invent any lines or numbers. If Not enough information then leave that value. Return ONLY raw JSON, no explanation, no markdown.
STRICT: Only use information explicitly written below. Empty string if not found.

INPUT:
{job_text}

OUTPUT JSON:
{{
  "job_title": "",        
  "company": "",          
  "location": [],         
  "work_mode": "",        
  "experience_required": "",
  "salary": "",           
  "required_skills": [],  
  "responsibilities": [], 
  "job_type": "",         
  "summary": "",          
  "link": ""              
}}

RULES:
- job_title: from title field. Add Senior/Junior/Lead only if explicitly written
- location: list. Include all cities found anywhere in description
- work_mode: remote/hybrid/onsite — scan for wfh/wfo/hybrid/in-person/days a week. else ""
- experience_required: numbers only e.g. "2-4 years". Check experience, years, senior/junior clues
- salary: INR/LPA only. Convert monthly to yearly LPA. else ""
- required_skills: every tool/language/framework/platform found anywhere in description
- responsibilities: max 3 points. What the person DOES. Under 10 words each
- job_type: full-time/part-time/contract/internship. else ""
- summary: 2 lines. Company purpose + role purpose. Facts only, no fluff
- link: copy exactly as given, do not modify"""

import json

def json_to_text(file: Path):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Plain text — no JSON syntax, saves tokens
    text = (
        f"Title: {data.get('title', '')}\n"
        f"Company: {data.get('company', '')}\n"
        f"Location: {data.get('location', '')}\n"
        f"Description:\n{data.get('content', '')}"
    )
    return text,data.get('link')


for file in Path("D:\\working repository\Job-Search-Project\Crawler\jobs").glob("*.json"):
    print(f"\n--- {file.name} ---")
    raw_json,link = json_to_text(file)
    response = ollamaSummary(MODEL, raw_json)
    print(response)
    save_file(response,link)
    os.remove(file)
# print(ollamaSummary(MODEL,"Where is Jabalpur located and tell me more about it "))





