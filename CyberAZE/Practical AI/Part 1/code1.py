import json
import os

import requests

url = "http://172.16.34.35:8089/v1/chat/completions"

headers = {
    "Authorization": "Bearer dummy-key",
    "Content-Type": "application/json",
}

# This dictionary is the JSON request body.
payload = {
    "model": "qwen/qwen3.6-27B",
    "messages": [
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
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "support_ticket",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [
                            "billing",
                            "technical",
                            "shipping",
                            "other",
                        ],
                    },
                    "priority": {
                        "type": "string",
                        "enum": [
                            "low",
                            "medium",
                            "high",
                        ],
                    },
                    "summary": {
                        "type": "string",
                    },
                    "requires_refund": {
                        "type": "boolean",
                    },
                },
                "required": [
                    "category",
                    "priority",
                    "summary",
                    "requires_refund",
                ],
                "additionalProperties": False,
            },
        }
    },
}

session = requests.Session()
# The local environment configures a broken proxy at 127.0.0.1:9. This model
# server is on the local network, so connect to it directly.
session.trust_env = False

response = session.post(
    url,
    headers=headers,
    json=payload,
    timeout=60,
)

response.raise_for_status()
response_data = response.json()

# print(json.dumps(response_data, indent=2))

# Chat Completions returns the generated text here.
structured_text = response_data["choices"][0]["message"]["content"]

# Convert the returned JSON string into a Python dictionary.
ticket = json.loads(structured_text)

print(json.dumps(ticket, indent=2))
