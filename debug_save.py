
from supabase import create_client
import sys

SUPABASE_URL = "https://kckawsrcgfzterietkht.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtja2F3c3JjZ2Z6dGVyaWV0a2h0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwNjUyMDAsImV4cCI6MjA4NjY0MTIwMH0.cTIYsaq2SHNx8DC-76Tjw8nFncNpkwWuKo5HEtDMv_g"

def debug_save():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Try to login first (use valid credentials if you know them, or test with a user you created)
    # Since I don't have the user's password, I'll try to insert without auth first (should fail if RLS is on)
    # Then I'll try to disable RLS for a moment if I had admin access (but I don't).
    
    # Wait! If the user says data is not getting stored, 
    # and my previous test_insert.py failed with RLS error,
    # then the app is definitely hitting RLS errors if it's not properly authenticated.
    
    # Let's check if there is an 'service_role' key available? 
    # Usually it's not provided in the source code for security reasons.
    
    print("Testing insert with explicit auth...")
    # I'll create a test user first or use the one I saw in code?
    # I saw 'admin@gmail.com' in the list of users in SQLite.
    # If the user also exists in Supabase Auth...
    
    try:
        # This will likely fail if the user doesn't exist in Supabase Auth
        # But maybe the user only exists in SQLite!
        # If the user only exists in SQLite, then database.USE_SUPABASE will be True
        # but supabase.auth.sign_in_with_password will fail.
        # Then verify_user falls back to SQLite.
        # BUT then add_transaction sees USE_SUPABASE is True and tries to save to Supabase.
        # AND it fails because it's not authenticated!
        
        email = "admin@gmail.com"
        password = "admin" # Guessing from common dev patterns, or maybe I saw it?
        
        # Let's try to sign up a new test user in Supabase to verify the flow
        import uuid
        test_email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        test_password = "TestPassword123!"
        
        print(f"Signing up test user: {test_email}")
        auth_resp = client.auth.sign_up({
            "email": test_email,
            "password": test_password
        })
        
        if auth_resp.user:
            print(f"Signup success! User ID: {auth_resp.user.id}")
            # Now try to insert
            data = {
                "user_id": auth_resp.user.id,
                "type": "Sale",
                "category": "Test",
                "amount": 50.0,
                "description": "Auth Test Insert",
                "date": "2024-03-11"
            }
            res = client.table("transactions").insert(data).execute()
            print("Insert with auth success!")
            print(res.data)
        else:
            print("Signup failed (no user returned)")
            
    except Exception as e:
        print(f"Debug save failed: {e}")

if __name__ == "__main__":
    debug_save()
