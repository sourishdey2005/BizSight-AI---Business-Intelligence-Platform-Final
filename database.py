import os
from supabase import create_client, Client
import pandas as pd

# Supabase Credentials (from user)
SUPABASE_URL = "https://kckawsrcgfzterietkht.supabase.co"
SUPABASE_KEY = "sb_publishable_9yDAvXAM_AoSgB0wUD2_IQ_-af6ODLr"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    # Tables are created in Supabase via SQL Editor using SCHEMA.sql
    pass

def verify_user(username, password):
    # This is now handled by Supabase Auth in the HTML frontend
    # But for Streamlit continuity, we can fetch from a custom users table if needed
    # Better: Use Supabase Auth directly if possible
    try:
        response = supabase.auth.sign_in_with_password({"email": username, "password": password})
        return response.user
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def create_user(email, password, role, business_name, business_type, business_address, aadhar, gst):
    try:
        # 1. Create Auth User
        auth_resp = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": email, # Fallback
                    "role": role,
                    "biz_name": business_name,
                    "industry": business_type
                }
            }
        })
        return True
    except Exception as e:
        print(f"Signup error: {e}")
        return False

def add_transaction(user_id, trans_type, category, amount, description, date, receipt_image=None):
    try:
        data = {
            "user_id": user_id,
            "type": trans_type,
            "category": category,
            "amount": float(amount),
            "description": description,
            "date": str(date)
        }
        response = supabase.table("transactions").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error adding transaction: {e}")
        return False

def get_transactions(user_id):
    try:
        response = supabase.table("transactions").select("*").eq("user_id", user_id).execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return pd.DataFrame()

def add_inventory_item(user_id, item_name, quantity, cost_price, selling_price, category, min_stock):
    try:
        data = {
            "user_id": user_id,
            "item_name": item_name,
            "quantity": int(quantity),
            "cost_price": float(cost_price),
            "selling_price": float(selling_price),
            "category": category,
            "min_stock_level": int(min_stock)
        }
        response = supabase.table("inventory").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error adding inventory: {e}")
        return False

def get_inventory(user_id):
    try:
        response = supabase.table("inventory").select("*").eq("user_id", user_id).execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return pd.DataFrame()

def test_connection():
    """Test if Supabase connection is working"""
    try:
        response = supabase.table("transactions").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False
