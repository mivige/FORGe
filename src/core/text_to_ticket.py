import json
from datetime import datetime
from typing import Any, Dict, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

text_input = (
        "Hi, this is Sarah Thompson. My policy number is PL-4829. "
        "Yesterday, my car was rear-ended on Main Street in Denver. "
        "The back bumper is pretty damaged, probably around $1,500 in repairs."
    )

def extract_incident_info(text: str) -> Dict[str, Any]:
    """
    Extract incident fields from unstructured text using GPT.
    """
    schema_prompt = f"""
    You are an assistant that extracts structured insurance incident data from text.
    Return ONLY valid JSON following this schema:
    {{
        "policyId": "string",
        "customerName": "string",
        "incidentType": "string",
        "description": "string",
        "location": "string",
        "estimatedDamage": "float (in USD)",
        "incidentDate": "YYYY-MM-DD or null"
    }}
    If a field is not mentioned, use null.
    """

    messages = [
        {"role": "system", "content": schema_prompt},
        {"role": "user", "content": f"Extract data from this text:\n{text}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    content = response.choices[0].message.content.strip()

    try:
        extracted = json.loads(content)
    except json.JSONDecodeError:
        extracted = {"error": "Invalid JSON returned", "raw": content}

    return extracted


def create_incident_payload(
    policy_id: str,
    customer_name: str,
    incident_type: str,
    description: str,
    location: str,
    estimated_damage: float,
    incident_date: Optional[str] = None
) -> Dict[str, Any]:
    if incident_date is None:
        incident_date = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "policyId": policy_id,
        "customerName": customer_name,
        "incidentDate": incident_date,
        "incidentType": incident_type,
        "description": description,
        "location": location,
        "estimatedDamage": estimated_damage
    }


def text_to_incident_ticket(text: str) -> Dict[str, Any]:
    extracted = extract_incident_info(text)
    
    if "error" in extracted:
        return extracted  # handle parsing issues

    payload = create_incident_payload(
        policy_id = extracted.get("policyId") or "UNKNOWN",
        customer_name = extracted.get("customerName") or "UNKNOWN",
        incident_type = extracted.get("incidentType") or "unspecified",
        description = extracted.get("description") or "",
        location = extracted.get("location") or "unspecified",
        estimated_damage = float(extracted.get("estimatedDamage") or 0.0),
        incident_date = extracted.get("incidentDate"),
    )
    
    return payload


if __name__ == "__main__":
    # Simulated caller text
    text = (
        "Hi, this is Sarah Thompson. My policy number is PL-4829. "
        "Yesterday, my car was rear-ended on Main Street in Denver. "
        "The back bumper is pretty damaged, probably around $1,500 in repairs."
    )

    # Generate structured ticket
    ticket = text_to_incident_ticket(text)

    # Print the result nicely formatted
    print("\n--- Generated Ticket ---")
    print(json.dumps(ticket, indent=4))
