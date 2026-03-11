
from supabase import create_client
import uuid

SUPABASE_URL = "https://kckawsrcgfzterietkht.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtja2F3c3JjZ2Z6dGVyaWV0a2h0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwNjUyMDAsImV4cCI6MjA4NjY0MTIwMH0.cTIYsaq2SHNx8DC-76Tjw8nFncNpkwWuKo5HEtDMv_g"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Note: This might fail if RLS is on and we are not authenticated.
# In SCHEMA.sql, I enabled RLS.
try:
    print("Attempting to insert a test transaction...")
    # Using a fake but valid UUID for testing
    test_user_id = str(uuid.uuid4()) 
    data = {
        "user_id": test_user_id,
        "type": "Sale",
        "category": "Test",
        "amount": 100.0,
        "description": "Test Insert",
        "date": "2024-03-11"
    }
    res = supabase.table("transactions").insert(data).execute()
    print("Insert success!")
    print(res.data)
except Exception as e:
    print(f"Insert failed: {e}")
