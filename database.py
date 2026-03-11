
import os
import sqlite3
import pandas as pd
from supabase import create_client, Client
from types import SimpleNamespace

# Supabase Credentials
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://kckawsrcgfzterietkht.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtja2F3c3JjZ2Z6dGVyaWV0a2h0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwNjUyMDAsImV4cCI6MjA4NjY0MTIwMH0.cTIYsaq2SHNx8DC-76Tjw8nFncNpkwWuKo5HEtDMv_g")

# SQLite Database Path
LOCAL_DB = "bizsight.db"

# Initialize Supabase Client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    USE_SUPABASE = True
except Exception as e:
    print(f"Supabase init failed, falling back to local: {e}")
    USE_SUPABASE = False

def get_sqlite_conn():
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    
    # Create tables if they don't exist (Local Fallback) - Matching existing bizsight.db schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT,
        business_name TEXT,
        business_type TEXT,
        business_address TEXT,
        aadhar_number TEXT,
        gst_number TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        type TEXT,
        category TEXT,
        amount REAL,
        description TEXT,
        date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        item_name TEXT,
        quantity INTEGER,
        cost_price REAL,
        selling_price REAL,
        category TEXT,
        min_stock_level INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def verify_user(username, password):
    # Try Supabase first if available
    if USE_SUPABASE:
        try:
            response = supabase.auth.sign_in_with_password({"email": username, "password": password})
            return response.user
        except Exception as e:
            print(f"Supabase auth attempt failed: {e}")
            # Fall through to SQLite
    
    # SQLite Fallback
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password))
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            # Create a user object that mimics Supabase user object for app.py compatibility
            user = SimpleNamespace()
            user.id = str(user_row['id'])
            user.email = user_row['username']
            user.user_metadata = {
                'role': user_row['role'],
                'biz_name': user_row['business_name']
            }
            return user
    except Exception as e:
        print(f"Local auth failed: {e}")
    
    return None

def create_user(email, password, role, business_name, business_type, business_address, aadhar, gst):
    # Try Supabase first
    if USE_SUPABASE:
        try:
            auth_resp = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": email,
                        "role": role,
                        "biz_name": business_name,
                        "industry": business_type
                    }
                }
            })
            if auth_resp:
                return True
        except Exception as e:
            print(f"Supabase signup failed: {e}")
            # Fall through to SQLite
            
    # SQLite Fallback
    try:
        print(f"Attempting local signup for {email}")
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, business_name, business_type, business_address, aadhar_number, gst_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (email, password, role, business_name, business_type, business_address, aadhar, gst))
        conn.commit()
        conn.close()
        print(f"Local signup success for {email}")
        return True
    except sqlite3.IntegrityError:
        print(f"Local signup failed: User {email} already exists.")
        return False
    except Exception as e:
        print(f"Local signup failed with error: {e}")
        return False

def add_transaction(user_id, trans_type, category, amount, description, date, receipt_image=None):
    import uuid
    is_uuid = False
    try:
        uuid.UUID(str(user_id))
        is_uuid = True
    except ValueError:
        is_uuid = False

    if USE_SUPABASE and is_uuid:
        try:
            data = {
                "user_id": str(user_id),
                "type": trans_type,
                "category": category,
                "amount": float(amount),
                "description": description,
                "date": str(date)
            }
            # Attempt Supabase insert
            res = supabase.table("transactions").insert(data).execute()
            if hasattr(res, 'error') and res.error:
                 print(f"Supabase transaction error: {res.error}")
                 # continue to local fallback
            else:
                 print(f"Supabase transaction success for user {user_id}")
                 return True
        except Exception as e:
            print(f"Supabase transaction exception: {e}")
            # fall through to SQLite
    else:
        if USE_SUPABASE and not is_uuid:
            print(f"Skipping Supabase for local user ID: {user_id}")
            
    # SQLite Fallback
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, type, category, amount, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(user_id), trans_type, category, float(amount), description, str(date)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Local transaction failed: {e}")
        return False

def get_transactions(user_id):
    import uuid
    is_uuid = False
    try:
        uuid.UUID(str(user_id))
        is_uuid = True
    except ValueError:
        is_uuid = False

    if USE_SUPABASE and is_uuid:
        try:
            response = supabase.table("transactions").select("*").eq("user_id", str(user_id)).execute()
            if hasattr(response, 'data') and response.data:
                return pd.DataFrame(response.data)
        except Exception as e:
            print(f"Supabase fetch transactions failed: {e}")
            
    # SQLite Fallback
    try:
        conn = get_sqlite_conn()
        df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ?", conn, params=(str(user_id),))
        conn.close()
        return df
    except Exception as e:
        print(f"Local fetch transactions failed: {e}")
        return pd.DataFrame()

def add_inventory_item(user_id, item_name, quantity, cost_price, selling_price, category, min_stock):
    import uuid
    is_uuid = False
    try:
        uuid.UUID(str(user_id))
        is_uuid = True
    except ValueError:
        is_uuid = False

    if USE_SUPABASE and is_uuid:
        try:
            data = {
                "user_id": str(user_id),
                "item_name": item_name,
                "quantity": int(quantity),
                "cost_price": float(cost_price),
                "selling_price": float(selling_price),
                "category": category,
                "min_stock_level": int(min_stock)
            }
            res = supabase.table("inventory").insert(data).execute()
            if hasattr(res, 'error') and res.error:
                print(f"Supabase inventory error: {res.error}")
            else:
                print(f"Supabase inventory success for user {user_id}")
                return True
        except Exception as e:
            print(f"Supabase inventory exception: {e}")

    # SQLite Fallback
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (user_id, item_name, quantity, cost_price, selling_price, category, min_stock_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (str(user_id), item_name, int(quantity), float(cost_price), float(selling_price), category, int(min_stock)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Local inventory failed: {e}")
        return False

def get_inventory(user_id):
    import uuid
    is_uuid = False
    try:
        uuid.UUID(str(user_id))
        is_uuid = True
    except ValueError:
        is_uuid = False

    if USE_SUPABASE and is_uuid:
        try:
            response = supabase.table("inventory").select("*").eq("user_id", str(user_id)).execute()
            if hasattr(response, 'data') and response.data:
                return pd.DataFrame(response.data)
        except Exception as e:
            print(f"Supabase fetch inventory failed: {e}")
    # SQLite Fallback
    try:
        conn = get_sqlite_conn()
        df = pd.read_sql_query("SELECT * FROM inventory WHERE user_id = ?", conn, params=(str(user_id),))
        conn.close()
        return df
    except Exception as e:
        print(f"Local fetch inventory failed: {e}")
        return pd.DataFrame()

def test_connection():
    if USE_SUPABASE:
        try:
            supabase.table("transactions").select("id").limit(1).execute()
            return True
        except Exception:
            return False
    return True # Local mode is always "connected"
