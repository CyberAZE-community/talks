import json
import httpx
from openai import OpenAI

client = OpenAI(
    base_url="http://172.16.34.35:8089/v1",
    api_key="dummy",
    http_client=httpx.Client(trust_env=False),
)

def check_ip_reputation(ip_address):
    return {
        "ip_address": ip_address,
        "risk": "high",
        "reports": 47,
        "category": "credential phishing",
    }


def quarantine_email(email_id, reason):
    return {
        "status": "quarantined",
        "email_id": email_id,
        "reason": reason,
    }


def create_incident(title, severity):
    return {
        "incident_id": "INC-1042",
        "title": title,
        "severity": severity,
        "status": "open",
    }

tools = [
    {
        "type": "function",
        "name": "check_ip_reputation",
        "description": "Check whether an IP address is malicious.",
        "parameters": {
            "type": "object",
            "properties": {
                "ip_address": {"type": "string"}
            },
            "required": ["ip_address"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "quarantine_email",
        "description": "Quarantine a suspicious email.",
        "parameters": {
            "type": "object",
            "properties": {
                "email_id": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["email_id", "reason"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "create_incident",
        "description": "Create a cybersecurity incident.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                },
            },
            "required": ["title", "severity"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


functions = {
    "check_ip_reputation": check_ip_reputation,
    "quarantine_email": quarantine_email,
    "create_incident": create_incident,
}

messages = [
    {
        "role": "system",
        "content": """
You are a SOC analyst assistant.

Use tools when necessary.
Do not invent tool results.
Ask before performing destructive actions.
""",
    },
    {
        "role": "user",
        "content": """
We received a login alert from IP address 203.0.113.42.
Check its reputation and explain the risk.
""",
    },
]

# llama.cpp's Chat Completions API expects function definitions under `function`.
chat_tools = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"],
        },
    }
    for tool in tools
]

response = client.chat.completions.create(
    model="qwen/qwen3.6-27B",
    messages=messages,
    tools=chat_tools,
)

message = response.choices[0].message

if message.tool_calls:
    messages.append({
        "role": "assistant",
        "content": message.content,
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }
            for call in message.tool_calls
        ],
    })

    for call in message.tool_calls:
        arguments = json.loads(call.function.arguments)
        print("Tool selected:", call.function.name)
        print("Arguments:", arguments)
        print("Call ID:", call.id)

        result = functions[call.function.name](**arguments)
        print("Tool result:", result)

        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": json.dumps(result),
        })

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27B",
        messages=messages,
        tools=chat_tools,
    )
    message = response.choices[0].message

print("\nFinal answer:")
print(message.content)
