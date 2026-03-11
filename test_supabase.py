
from supabase import create_client
import sys

SUPABASE_URL = "https://kckawsrcgfzterietkht.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtja2F3c3JjZ2Z6dGVyaWV0a2h0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwNjUyMDAsImV4cCI6MjA4NjY0MTIwMH0.cTIYsaq2SHNx8DC-76Tjw8nFncNpkwWuKo5HEtDMv_g"

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
