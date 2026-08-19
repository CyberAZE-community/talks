from typing import Literal

import httpx
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI( base_url="http://172.16.34.35:8089/v1", api_key="dummy")

class ActionArguments(BaseModel):
    email_id: str
    reason: str
    quarantine_days: int | None
    soc_queue: str | None


class SecurityCommand(BaseModel):
    action: Literal[
        "allow_email",
        "quarantine_email",
        "escalate_to_soc",
    ]
    severity: Literal["low", "medium", "high"]
    arguments: ActionArguments


response = client.chat.completions.parse(
    model="qwen/qwen3.6-27B",
    messages=[
        {
            "role": "developer",
            "content": """
You are a phishing email triage system.

Choose one action:
- allow_email
- quarantine_email
- escalate_to_soc

For quarantine_email, provide quarantine_days.
For escalate_to_soc, provide soc_queue.
Use null for arguments that are not needed.
""",
        },
        {
            "role": "user",
            "content": """
Email ID: email-4821
From: Barrister John Okafor <inheritance@royal-bank.example>
Subject: CONFIDENTIAL INHERITANCE NOTIFICATION

Dear Friend,

My late client, Prince Alexander Johnson, left $18,500,000
in an unclaimed Nigerian bank account.

Because you have the same surname, Johnson, you may be presented
as his legal relative.

Please send your passport, bank details, home address, and a
small processing fee. You will receive 40% of the inheritance.

This matter is urgent and strictly confidential.
""",
        },
    ],
    response_format=SecurityCommand,
)

command : SecurityCommand = response.choices[0].message.parsed
print(command)
print(command.model_dump_json(indent=2))

def allow_email(email_id: str):
    print(f"Allowing email: {email_id}")

def quarantine_email(email_id: str, days: int, reason: str):
    print(f"Quarantining {email_id} for {days} days")
    print(f"Reason: {reason}")

def escalate_to_soc(email_id: str, queue: str, reason: str):
    print(f"Sending {email_id} to SOC queue: {queue}")
    print(f"Reason: {reason}")

args = command.arguments

if command.action == "allow_email":
    allow_email(args.email_id)

elif command.action == "quarantine_email":
    quarantine_email(
        email_id=args.email_id,
        days=args.quarantine_days or 30,
        reason=args.reason,
    )

elif command.action == "escalate_to_soc":
    escalate_to_soc(
        email_id=args.email_id,
        queue=args.soc_queue or "phishing-investigation",
        reason=args.reason,
    )
