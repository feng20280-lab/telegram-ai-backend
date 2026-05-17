from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import telegram as tg_service
import ai_service
from database import supabase

router = APIRouter()

def get_account(account_id: str) -> dict:
    result = supabase.table("accounts").select("*").eq("account_id", account_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Account not found")
    return result.data[0]

class SuggestReplyRequest(BaseModel):
    account_id: str
    dialog_id: int
    incoming_message: str
    history_limit: int = 50

@router.get("/{account_id}/persona")
async def get_persona(account_id: str, dialog_id: int = None):
    try:
        account = get_account(account_id)
        cached = supabase.table("personas").select("*").eq("account_id", account_id).execute()
        if cached.data:
            return {"account_id": account_id, "persona": cached.data[0]["persona"]}
        if dialog_id:
            messages = await tg_service.get_messages(account_id, account["session_string"], dialog_id, limit=100)
        else:
            dialogs = await tg_service.get_dialogs(account_id, account["session_string"])
            if not dialogs:
                raise HTTPException(status_code=404, detail="No dialogs found")
            messages = await tg_service.get_messages(account_id, account["session_string"], int(dialogs[0]["id"]), limit=100)
        persona = ai_service.analyze_persona(account, messages)
        supabase.table("personas").upsert({"account_id": account_id, "persona": persona}).execute()
        return {"account_id": account_id, "persona": persona}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-reply")
async def suggest_reply(req: SuggestReplyRequest):
    try:
        account = get_account(req.account_id)
        messages = await tg_service.get_messages(req.account_id, account["session_string"], req.dialog_id, req.history_limit)
        cached = supabase.table("personas").select("*").eq("account_id", req.account_id).execute()
        if cached.data:
            persona = cached.data[0]["persona"]
        else:
            persona = ai_service.analyze_persona(account, messages)
            supabase.table("personas").upsert({"account_id": req.account_id, "persona": persona}).execute()
        suggestions = ai_service.suggest_reply(
            account_info=account,
            persona=persona,
            conversation_history=messages,
            incoming_message=req.incoming_message
        )
        return {
            "account_id": req.account_id,
            "incoming_message": req.incoming_message,
            "suggestions": suggestions,
            "persona_used": persona
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{account_id}/persona")
async def reset_persona(account_id: str):
    supabase.table("personas").delete().eq("account_id", account_id).execute()
    return {"success": True, "message": "Persona cache cleared"}
