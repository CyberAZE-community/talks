from typing import Literal

import httpx
from openai import OpenAI
from pydantic import BaseModel, ConfigDict

class SupportTicket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Literal[
        "billing",
        "technical",
        "shipping",
        "other",
    ]
    priority: Literal[
        "low",
        "medium",
        "high",
    ]
    summary: str
    requires_refund: bool


client = OpenAI(
    base_url="http://172.16.34.35:8089/v1",
    api_key="dummy",
    # Bypass the broken HTTP_PROXY / HTTPS_PROXY environment settings.
    http_client=httpx.Client(trust_env=False),
)

response = client.chat.completions.parse(
    model= "qwen/qwen3.6-27B",
    messages=[
        {
            "role": "system",
            "content": "Convert the customer message into a support ticket.",
        },
        {
            "role": "user",
            "content": (
                "I was charged twice for order 4821. Please refund the duplicate payment."
            ),
        },
    ],
    response_format=SupportTicket,
)

ticket = response.choices[0].message.parsed

if ticket is None:
    raise RuntimeError("The response did not contain a parsed support ticket.")

print(ticket.model_dump_json(indent=2))
