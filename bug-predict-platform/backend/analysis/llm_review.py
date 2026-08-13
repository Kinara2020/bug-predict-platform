import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

PROMPT = """You are a senior code reviewer. For the file below, identify:
1. Code smells (long functions, duplication, poor naming, tight coupling)
2. Potential bugs static analysis wouldn't catch
3. One concrete improvement

Respond as strict JSON: {{"smells": [{{"type": "", "description": "", "suggestion": ""}}], "notes": ""}}

File: {file_path}
Code:
{code}
"""

def review_file(file_path, content):
    content = content[:6000]
    try:
        resp = model.generate_content(PROMPT.format(file_path=file_path, code=content))
        return resp.text
    except Exception as e:
        return f'{{"smells": [], "notes": "review failed: {e}"}}'