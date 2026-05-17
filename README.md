# Telegram AI Reply Assistant — Backend

A FastAPI backend that connects multiple Telegram accounts, reads chat history, and uses DeepSeek AI to suggest context-aware reply messages.

---

## Tech Stack
- **Backend:** Python + FastAPI
- **Telegram:** Telethon (MTProto user API)
- **AI:** DeepSeek API (OpenAI-compatible)
- **Database:** Supabase
- **Hosting:** Railway

---

## Setup Guide (Step by Step)

### Step 1 — Get Telegram API credentials
1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Create a new app (any name/platform is fine)
4. Copy your **API ID** and **API Hash**

### Step 2 — Get DeepSeek API key
1. Go to https://platform.deepseek.com
2. Sign up and go to API Keys
3. Create a new key and copy it

### Step 3 — Set up Supabase
1. Go to https://supabase.com and create a free project
2. Go to **SQL Editor** and paste the contents of `supabase_schema.sql` and run it
3. Go to **Project Settings → API** and copy:
   - Project URL
   - `anon` public key

### Step 4 — Configure environment variables
```bash
cp .env.example .env
```
Fill in all values in `.env`:
```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your_anon_key
DEEPSEEK_API_KEY=sk-xxxx
SESSION_SECRET=any_random_32_char_string
```

### Step 5 — Run locally (optional test)
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Visit http://localhost:8000/docs to see all API endpoints.

### Step 6 — Deploy to Railway
1. Go to https://railway.app and create a free account
2. Click **New Project → Deploy from GitHub repo**
3. Push this folder to a GitHub repo first, then connect it
4. In Railway, go to **Variables** and add all your `.env` values
5. Railway auto-deploys. Copy your public URL (e.g. `https://your-app.railway.app`)

---

## API Endpoints

### Accounts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/accounts/send-otp` | Send OTP to phone number |
| POST | `/accounts/verify-otp` | Verify OTP and save account |
| GET | `/accounts/` | List all saved accounts |
| DELETE | `/accounts/{account_id}` | Remove an account |

### Chats
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/chats/{account_id}/dialogs` | Get all chats for an account |
| GET | `/chats/{account_id}/messages/{dialog_id}` | Get message history |

### AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ai/{account_id}/persona` | Get AI persona analysis |
| POST | `/ai/suggest-reply` | Get 3 reply suggestions |
| DELETE | `/ai/{account_id}/persona` | Reset persona cache |

---

## How to Connect to Lovable (Frontend)

In your Lovable app, set the backend URL as an environment variable:
```
VITE_BACKEND_URL=https://your-app.railway.app
```

Then call the API like this in your Lovable React code:
```javascript
const BACKEND = import.meta.env.VITE_BACKEND_URL;

// Send OTP
const res = await fetch(`${BACKEND}/accounts/send-otp`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ phone: "+6591234567" })
});

// Get reply suggestions
const res = await fetch(`${BACKEND}/ai/suggest-reply`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    account_id: "123456789",
    dialog_id: -1001234567890,
    incoming_message: "Hi, what are your operating hours?"
  })
});
```

---

## Lovable Prompt (copy this into Lovable)

> Build a Telegram AI Reply Assistant web app. It has 3 main pages:
>
> 1. **Accounts Page** — Shows all connected Telegram accounts as cards. Each card shows name, phone, username. Has an "Add Account" button that opens a modal with 2 steps: enter phone number → enter OTP code. Has a remove button on each card.
>
> 2. **Chats Page** — Left sidebar shows accounts. Clicking an account loads their dialogs (chats). Clicking a dialog shows the message history on the right in a chat bubble UI (blue = sent, grey = received).
>
> 3. **AI Reply Page** — Select account and dialog from dropdowns. Shows a text box to paste/type the incoming message. Click "Suggest Replies" button. Shows 3 reply cards: Short, Detailed, Friendly — each with a Copy button. Also shows the account's persona analysis in a collapsible section.
>
> Backend URL is stored in env variable VITE_BACKEND_URL. Use fetch() to call the API. Dark theme, modern and clean design.

---

## File Structure
```
telegram-ai-backend/
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Python dependencies
├── railway.toml             # Railway deployment config
├── .env.example             # Environment variables template
├── supabase_schema.sql      # Database tables
├── routers/
│   ├── accounts.py          # Login / account management
│   ├── chats.py             # Fetch dialogs and messages
│   └── ai.py                # Persona analysis + reply suggestions
└── services/
    ├── database.py          # Supabase client
    ├── telegram.py          # Telethon multi-account handler
    └── ai.py                # DeepSeek AI logic
```
