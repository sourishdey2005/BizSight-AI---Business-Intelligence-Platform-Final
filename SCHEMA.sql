-- SCHEMA FOR BIZSIGHT AI (INFOSYS POWERED)
-- Paste this into the Supabase SQL Editor (https://supabase.com/dashboard/project/kckawsrcgfzterietkht/sql)

-- 1. Create Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('Sale', 'Expense')),
  category TEXT,
  amount NUMERIC NOT NULL DEFAULT 0,
  description TEXT,
  date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create Inventory Table
CREATE TABLE IF NOT EXISTS inventory (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  item_name TEXT NOT NULL,
  quantity INTEGER DEFAULT 0,
  cost_price NUMERIC DEFAULT 0,
  selling_price NUMERIC DEFAULT 0,
  min_stock_level INTEGER DEFAULT 10,
  category TEXT,
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Enable Row Level Security (RLS)
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;

-- 4. Create Policies
-- Users can only see/edit their own data
CREATE POLICY "Handle Transactions" ON transactions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Handle Inventory" ON inventory
    FOR ALL USING (auth.uid() = user_id);

-- Note: In the Supabase Dashboard, also ensure "Realtime" is enabled 
-- for these tables if you want live updates!
