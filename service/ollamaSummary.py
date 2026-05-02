from pathlib import Path

import ollama
MODEL = "qwen2.5:0.5b"   # 352MB — very fast on low-end PC

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
    return response

# ── Prompt ────────────────────────────────────────────────────────────────────
def build_prompt(job_text: str) -> str:
    return f"""You are an expert IT job description parser for the Indian tech industry.
Extract ALL information from the job posting below and return ONLY a raw JSON object.
No explanation. No markdown. No code fences. Just the JSON.
Never Add extra information, or details which is not mentioned in the job description.

OUTPUT FORMAT:
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

EXTRACTION RULES:

job_title:
- Use directly from input otherwise
- Check both explicit mentions AND indirect clues like "senior", "junior", "entry level" then update job title like that

company:
- Use company name as-is from input

location:
- Always keep the location from input
- Also scan description for additional locations, office names, or city mentions
- Add work mode clues e.g. "Chennai (Hybrid - 2 days onsite)"
- Return as list if multiple locations

work_mode:
- Detect from description: remote / hybrid / onsite / not mentioned
- Look for keywords: "work from home", "hybrid", "in-person", "office", "days a week", "wfo", "wfh"

experience_required:
- Extract as a range e.g. "1-3 years", "3-5 years"
- If only one number mentioned e.g. "3 years" return "3+ years"
- Check both explicit mentions AND indirect clues like "senior", "junior", "entry level"
- Return number/range only, no extra text

salary:
- Extract if mentioned, else empty string
- Normalize to yearly if monthly is  tell in lpa(lakhs per annum)

required_skills:
- List every technology, language, framework, tool, platform explicitly required
- ALSO extract skills indirectly mentioned in responsibilities or "what you'll bring" sections
- For each skill, check if a minimum years of experience is mentioned
- Include: languages, frameworks, databases, cloud platforms, DevOps tools, protocols, methodologies

good_to_have_skills:
- Skills marked as "preferred", "good to have", "nice to have", "plus", "advantage"
- Same format as required_skills add it insie required skills

responsibilities:
- Max 4 bullet points
- Extract the actual work the person will DO, not requirements
- Keep each point under 15 words

job_type:
- full-time / part-time / contract / internship / not mentioned

summary:
- 3 lines: what the company does + what this role does
- Be specific, not generic

link:
- Copy the link from input exactly, do not change

JOB INPUT:
{job_text}
"""

import json

def json_to_text(file: Path):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Plain text — no JSON syntax, saves tokens
    return (
        f"Title: {data.get('title', '')}\n"
        f"Company: {data.get('company', '')}\n"
        f"Location: {data.get('location', '')}\n"
        f"Link: {data.get('link', '')}\n"
        f"Description:\n{data.get('content', '')}"
    )


for file in Path("D:\\working repository\Job-Search-Project\Crawler\jobs").glob("*.json"):
    print(f"\n--- {file.name} ---")
    print("Output: "+str(ollamaSummary(MODEL, json_to_text(file))))
    break
# print(ollamaSummary(MODEL,"Where is Jabalpur located and tell me more about it "))