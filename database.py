
import os
import sqlite3
import pandas as pd
from supabase import create_client, Client
from types import SimpleNamespace

# Supabase Credentials
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://kckawsrcgfzterietkht.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtja2F3c3JjZ2Z6dGVyaWV0a2h0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwNjUyMDAsImV4cCI6MjA4NjY0MTIwMH0.cTIYsaq2SHNx8DC-76Tjw8nFncNpkwWuKo5HEtDMv_g")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# SQLite Database Path
LOCAL_DB = "bizsight.db"

# Initialize Supabase Client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    USE_SUPABASE = True
    admin_supabase = None
    if SUPABASE_SERVICE_ROLE_KEY:
        admin_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
except Exception as e:
    print(f"Supabase init failed, falling back to local: {e}")
    USE_SUPABASE = False
    admin_supabase = None

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
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        logout_time TIMESTAMP
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
                print("Supabase signup successful. Proceeding to replicate locally.")
                # We do not return True here; we let it fall through to dual-write to SQLite.
        except Exception as e:
            print(f"Supabase signup failed: {e}")
            # Fall through to SQLite
            
    # SQLite Fallback & Dual-Write
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

from datetime import datetime

def log_user_login(email):
    log_ids = {'local': None, 'sb': None}
    
    if USE_SUPABASE:
        try:
            data = {"user_email": email}
            res = supabase.table("login_logs").insert(data).execute()
            if hasattr(res, 'data') and len(res.data) > 0:
                log_ids['sb'] = res.data[0]['id']
        except Exception as e:
            print(f"Supabase login log failed: {e}")
            
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO login_logs (user_email) VALUES (?)", (email,))
        log_ids['local'] = cursor.lastrowid
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Local login log failed: {e}")
        
    return log_ids

def update_user_activity(log_ids):
    if not isinstance(log_ids, dict):
        log_ids = {'local': log_ids, 'sb': None}
        
    if USE_SUPABASE and log_ids.get('sb') is not None:
        try:
            supabase.table("login_logs").update({"last_active": datetime.utcnow().isoformat()}).eq("id", log_ids['sb']).execute()
        except:
            pass

    try:
        if log_ids.get('local') is not None:
            conn = get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("UPDATE login_logs SET last_active = CURRENT_TIMESTAMP WHERE id = ?", (log_ids['local'],))
            conn.commit()
            conn.close()
    except:
        pass

def log_user_logout(log_ids):
    if not isinstance(log_ids, dict):
        log_ids = {'local': log_ids, 'sb': None}
        
    if USE_SUPABASE and log_ids.get('sb') is not None:
        try:
            supabase.table("login_logs").update({"logout_time": datetime.utcnow().isoformat()}).eq("id", log_ids['sb']).execute()
        except:
            pass

    try:
        if log_ids.get('local') is not None:
            conn = get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("UPDATE login_logs SET logout_time = CURRENT_TIMESTAMP WHERE id = ?", (log_ids['local'],))
            conn.commit()
            conn.close()
    except:
        pass

def get_all_login_logs():
    if USE_SUPABASE:
        try:
            response = supabase.table("login_logs").select("*").execute()
            if hasattr(response, 'data') and response.data:
                return pd.DataFrame(response.data)
        except Exception as e:
            print(f"Supabase fetch login logs failed: {e}")

    try:
        conn = get_sqlite_conn()
        df = pd.read_sql_query("SELECT * FROM login_logs", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def get_all_users():
    if USE_SUPABASE:
        try:
            # When admin key is available, use it to get exact list from auth
            if admin_supabase:
                auth_users = admin_supabase.auth.admin.list_users()
                if hasattr(auth_users, 'users'):
                    users_list = []
                    for user in auth_users.users:
                        users_list.append({
                            'id': user.id,
                            'username': user.email,
                            'role': user.user_metadata.get('role', 'Owner') if hasattr(user, 'user_metadata') and user.user_metadata else 'Owner',
                            'business_name': user.user_metadata.get('biz_name', 'Unknown') if hasattr(user, 'user_metadata') and user.user_metadata else 'Unknown',
                            'created_at': user.created_at
                        })
                    if users_list:
                        return pd.DataFrame(users_list)
                    
            # Fallback to profiles table if no admin key
            response = supabase.table("profiles").select("*").execute()
            if hasattr(response, 'data') and response.data:
                df = pd.DataFrame(response.data)
                # handle renaming based on what's available
                if 'full_name' in df.columns:
                    df = df.rename(columns={'full_name': 'username'})
                return df
        except Exception as e:
            print(f"Supabase fetch users failed: {e}")

    try:
        conn = get_sqlite_conn()
        df = pd.read_sql_query("SELECT id, username, role, business_name, created_at FROM users", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def update_user_password(username, new_password):
    if USE_SUPABASE:
        if admin_supabase:
            try:
                # 1. First get the user's ID using their email
                auth_users = admin_supabase.auth.admin.list_users()
                user_id = None
                if hasattr(auth_users, 'users'):
                    for user in auth_users.users:
                        # Assuming 'username' is actually an email since that's what we collect
                        if user.email == username:
                            user_id = user.id
                            break
                            
                # 2. Update their password using admin client
                if user_id:
                    admin_supabase.auth.admin.update_user_by_id(user_id, {"password": new_password})
                    print(f"Successfully updated Supabase password for {username}")
                    return True
                else:
                    print(f"Could not find user in Supabase Auth to update password: {username}")
            except Exception as e:
                print(f"Failed to update password via Supabase Admin: {e}")
        else:
            print("Note: Password reset via Supabase requires SUPABASE_SERVICE_ROLE_KEY environment variable. Cannot update cloud user.")

    # Always attempt local fallback
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_password, username))
        conn.commit()
        conn.close()
        return True
    except:
        return False
