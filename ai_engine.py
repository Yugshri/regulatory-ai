from google import genai
from config import GEMINI_API_KEY, AI_MODEL, BANK_DEPARTMENTS
import json

# Client initialize karo
client = genai.Client(api_key=GEMINI_API_KEY)

def extract_maps(circular_text):
    """
    Circular text se Measurable Action Points nikalta hai
    Returns: list of MAP dictionaries
    """
    try:
        prompt = f"""
You are a senior regulatory compliance expert for Indian banks.

Analyze this RBI/SEBI circular and extract Measurable Action Points (MAPs).

Rules:
- Each MAP must be specific and measurable
- Assign to exactly one department from this list: {BANK_DEPARTMENTS}
- Extract deadline exactly as mentioned in circular
- Priority: High (immediate/critical), Medium (within 3 months), Low (advisory)

Return ONLY a valid JSON array, no explanation, no markdown.

Format:
[
  {{
    "id": 1,
    "action": "specific action to be taken",
    "department": "exact department name from list",
    "deadline": "deadline as mentioned in circular",
    "priority": "High/Medium/Low",
    "status": "Pending",
    "compliance_risk": "what happens if not done",
    "estimated_effort": "Low/Medium/High"
  }}
]

Circular:
{circular_text}
"""

        response = client.models.generate_content(
            model=AI_MODEL,
            contents=prompt
        )

        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        maps = json.loads(raw)
        return maps

    except json.JSONDecodeError:
        raise Exception("AI response parse nahi hua - dobara try karo")
    except Exception as e:
        raise Exception(f"AI error: {str(e)}")


def validate_completion(map_item):
    """
    Ek MAP ki completion validate karta hai
    Returns: (is_valid, feedback) tuple
    """
    try:
        prompt = f"""
You are a bank compliance auditor.

This action was marked as completed:
Action: {map_item['action']}
Department: {map_item['department']}
Deadline: {map_item['deadline']}

Ask 2 specific questions a compliance officer must answer to prove this is truly complete.
Keep it short and practical.

Return as JSON:
{{
  "validation_questions": ["question 1", "question 2"],
  "completion_criteria": "one line criteria"
}}
"""
        response = client.models.generate_content(
            model=AI_MODEL,
            contents=prompt
        )

        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return True, result

    except Exception as e:
        return False, {"validation_questions": [], "completion_criteria": "Validation failed"}