from fastapi import APIRouter
from pydantic import BaseModel
import os
import json
import re
from openai import OpenAI

router = APIRouter()


class SankalpRequest(BaseModel):
    intent: str


@router.post("/sankalp")
def generate_contract(request: SankalpRequest):

   client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    prompt = f"""
Convert the following intent into a structured decision contract.

Intent:
{request.intent}

STRICT RULES:
- Use ONLY variable name: amount
- Conditions must be valid Python expressions
- Use operators: <=, >=, <, >, ==
- Actions must be lowercase strings like: auto_approve, require_manager
- Do NOT invent new variable names

Output ONLY valid JSON.

Format:
{{
  "contract": {{
    "rules": [
      {{
        "condition": "amount <= 5000",
        "action": "auto_approve"
      }}
    ]
  }}
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You MUST convert intent into deterministic rule-based contracts using only the variable 'amount'."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        json_str = re.search(r'\{.*\}', content, re.DOTALL).group()
        parsed = json.loads(json_str)

        return parsed

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }