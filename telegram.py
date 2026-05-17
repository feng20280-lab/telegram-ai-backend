import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

# In-memory store for active clients { account_id: TelegramClient }
active_clients: dict = {}


async def create_client(session_string: str = None) -> TelegramClient:
    session = StringSession(session_string) if session_string else StringSession()
    client = TelegramClient(session, API_ID, API_HASH)
    await client.connect()
    return client


async def get_client(account_id: str, session_string: str) -> TelegramClient:
    if account_id in active_clients:
        client = active_clients[account_id]
        if await client.is_user_authorized():
            return client

    client = await create_client(session_string)
    active_clients[account_id] = client
    return client


async def send_otp(phone: str) -> dict:
    """Step 1: Send OTP to phone number"""
    client = await create_client()
    result = await client.send_code_request(phone)
    # Save temp client keyed by phone
    active_clients[f"temp_{phone}"] = client
    return {
        "phone_code_hash": result.phone_code_hash,
        "session": client.session.save()
    }


async def verify_otp(phone: str, code: str, phone_code_hash: str, temp_session: str) -> dict:
    """Step 2: Verify OTP and get session string"""
    client = await create_client(temp_session)
    await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
    me = await client.get_me()
    session_string = client.session.save()

    account_id = str(me.id)
    active_clients[account_id] = client

    return {
        "account_id": account_id,
        "phone": phone,
        "username": me.username or "",
        "first_name": me.first_name or "",
        "last_name": me.last_name or "",
        "session_string": session_string  # Store this encrypted in Supabase
    }


async def get_dialogs(account_id: str, session_string: str) -> list:
    """Get list of all chats/contacts for an account"""
    client = await get_client(account_id, session_string)
    dialogs = await client.get_dialogs(limit=50)
    result = []
    for d in dialogs:
        result.append({
            "id": str(d.id),
            "name": d.name,
            "is_group": d.is_group,
            "is_channel": d.is_channel,
            "unread_count": d.unread_count,
        })
    return result


async def get_messages(account_id: str, session_string: str, dialog_id: int, limit: int = 50) -> list:
    """Fetch chat history for a specific dialog"""
    client = await get_client(account_id, session_string)
    messages = []
    async for msg in client.iter_messages(dialog_id, limit=limit):
        if msg.text:
            messages.append({
                "id": msg.id,
                "sender_id": str(msg.sender_id),
                "text": msg.text,
                "date": msg.date.isoformat(),
                "out": msg.out  # True = sent by this account, False = received
            })
    return list(reversed(messages))  # Oldest first
