
from supabase import create_client
import sys

SUPABASE_URL = "https://kckawsrcgfzterietkht.supabase.co"
SUPABASE_KEY = "sb_publishable_9yDAvXAM_AoSgB0wUD2_IQ_-af6ODLr"

try:
    print(f"Testing connection to {SUPABASE_URL}...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Try a simple query
    # Note: If the key is invalid, it might still create the client but fail on the first request
    try:
        res = supabase.table("transactions").select("*").limit(1).execute()
        print("Connection successful!")
        print(f"Data: {res.data}")
    except Exception as e:
        print(f"Query failed: {e}")
except Exception as e:
    print(f"Initialization failed: {e}")
