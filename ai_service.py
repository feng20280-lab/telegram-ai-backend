import os
from openai import OpenAI  # DeepSeek uses OpenAI-compatible API
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def analyze_persona(account_info: dict, messages: list) -> str:
    """Analyze the account's communication style/persona from chat history"""
    history_text = "\n".join([
        f"{'[SENT]' if m['out'] else '[RECEIVED]'} {m['text']}"
        for m in messages[-100:]  # Use last 100 messages for persona
    ])

    prompt = f"""Analyze this Telegram account's communication style based on their sent messages.

Account Name: {account_info.get('first_name', '')} {account_info.get('last_name', '')}
Username: @{account_info.get('username', 'unknown')}

Chat History (SENT = messages they wrote, RECEIVED = messages from others):
{history_text}

Provide a concise persona summary covering:
1. Role/profession (e.g. receptionist, sales, customer support, personal)
2. Tone (formal, casual, friendly, professional)
3. Common phrases or greetings they use
4. Response style (short/long, emoji usage, punctuation style)
5. Key topics they handle

Keep it under 200 words."""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    return response.choices[0].message.content


def suggest_reply(
    account_info: dict,
    persona: str,
    conversation_history: list,
    incoming_message: str
) -> dict:
    """Generate AI reply suggestion based on persona and conversation history"""

    # Format conversation history
    history_text = "\n".join([
        f"{'You' if m['out'] else 'Them'}: {m['text']}"
        for m in conversation_history[-30:]  # Last 30 messages for context
    ])

    prompt = f"""You are assisting {account_info.get('first_name', 'this user')} to reply to a Telegram message.

ACCOUNT PERSONA:
{persona}

RECENT CONVERSATION:
{history_text}

NEW INCOMING MESSAGE:
"{incoming_message}"

Based on the persona and conversation context, suggest 3 different reply options:
1. A short/quick reply
2. A detailed/professional reply  
3. A friendly/warm reply

Format your response as JSON like this:
{{
  "short": "...",
  "detailed": "...",
  "friendly": "...",
  "context_note": "Brief note about what this message is asking/about"
}}

Match the account's natural writing style. Do not add any text outside the JSON."""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )

    import json
    try:
        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())
    except Exception:
        return {
            "short": response.choices[0].message.content,
            "detailed": "",
            "friendly": "",
            "context_note": ""
        }
