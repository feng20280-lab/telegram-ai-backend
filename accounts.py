from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import telegram as tg_service
from database import supabase

router = APIRouter()


class SendOTPRequest(BaseModel):
    phone: str  # e.g. "+6591234567"


class VerifyOTPRequest(BaseModel):
    phone: str
    code: str
    phone_code_hash: str
    temp_session: str


class AccountResponse(BaseModel):
    account_id: str
    phone: str
    username: str
    first_name: str
    last_name: str


@router.post("/send-otp")
async def send_otp(req: SendOTPRequest):
    """Step 1: Send OTP to the phone number"""
    try:
        result = await tg_service.send_otp(req.phone)
        return {
            "success": True,
            "phone_code_hash": result["phone_code_hash"],
            "temp_session": result["session"],
            "message": f"OTP sent to {req.phone}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-otp")
async def verify_otp(req: VerifyOTPRequest):
    """Step 2: Verify OTP and save account to Supabase"""
    try:
        account = await tg_service.verify_otp(
            req.phone, req.code, req.phone_code_hash, req.temp_session
        )

        # Save account to Supabase (session_string stored for reconnecting)
        supabase.table("accounts").upsert({
            "account_id": account["account_id"],
            "phone": account["phone"],
            "username": account["username"],
            "first_name": account["first_name"],
            "last_name": account["last_name"],
            "session_string": account["session_string"],  # Encrypt this in production!
        }).execute()

        return {
            "success": True,
            "account": {
                "account_id": account["account_id"],
                "phone": account["phone"],
                "username": account["username"],
                "first_name": account["first_name"],
                "last_name": account["last_name"],
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def list_accounts():
    """Get all saved Telegram accounts"""
    try:
        result = supabase.table("accounts").select(
            "account_id, phone, username, first_name, last_name"
        ).execute()
        return {"accounts": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{account_id}")
async def remove_account(account_id: str):
    """Remove a Telegram account"""
    try:
        supabase.table("accounts").delete().eq("account_id", account_id).execute()
        # Disconnect active client if exists
        if account_id in tg_service.active_clients:
            await tg_service.active_clients[account_id].disconnect()
            del tg_service.active_clients[account_id]
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
