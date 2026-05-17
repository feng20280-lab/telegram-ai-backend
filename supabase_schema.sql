-- Run this in your Supabase SQL Editor

-- Table: accounts (stores logged-in Telegram accounts)
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    phone TEXT NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    session_string TEXT NOT NULL,  -- Telegram session (treat as sensitive)
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: personas (cached AI persona analysis per account)
CREATE TABLE IF NOT EXISTS personas (
    account_id TEXT PRIMARY KEY REFERENCES accounts(account_id) ON DELETE CASCADE,
    persona TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security (recommended)
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE personas ENABLE ROW LEVEL SECURITY;

-- Simple policy: allow all operations from service role (your backend)
CREATE POLICY "Allow all for service role" ON accounts
    FOR ALL USING (true);

CREATE POLICY "Allow all for service role" ON personas
    FOR ALL USING (true);
