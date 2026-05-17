from fastapi import APIRouter, HTTPException
import telegram as tg_service
from database import supabase

router = APIRouter()


def get_account(account_id: str) -> dict:
    result = supabase.table("accounts").select("*").eq("account_id", account_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Account not found")
    return result.data[0]


@router.get("/{account_id}/dialogs")
async def get_dialogs(account_id: str):
    """Get all chats/contacts for a Telegram account"""
    try:
        account = get_account(account_id)
        dialogs = await tg_service.get_dialogs(account_id, account["session_string"])
        return {"dialogs": dialogs}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}/messages/{dialog_id}")
async def get_messages(account_id: str, dialog_id: int, limit: int = 50):
    """Get message history for a specific chat"""
    try:
        account = get_account(account_id)
        messages = await tg_service.get_messages(
            account_id, account["session_string"], dialog_id, limit
        )
        return {
            "account_id": account_id,
            "dialog_id": dialog_id,
            "messages": messages,
            "count": len(messages)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
