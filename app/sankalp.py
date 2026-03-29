from fastapi import APIRouter
from pydantic import BaseModel
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================
# INPUT MODEL
# =========================

class SankalpRequest(BaseModel):
    intent: str


# =========================
# SANKALP API
# =========================

@router.post("/sankalp")
def generate_contract(request: SankalpRequest):

    prompt = f"""
Convert the following intent into a structured decision contract.

Intent:
{request.intent}

Output ONLY valid JSON.

Format:
{{
  "contract": {{
    "rules": [
      {{
        "condition": "expression",
        "action": "action_name"
      }}
    ]
  }}
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You convert intent into deterministic rule-based contracts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(content)
        return parsed
    except Exception:
        return {
            "error": "Failed to parse contract",
            "raw": content
        }