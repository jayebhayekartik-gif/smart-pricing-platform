# dashboard/utils/supabase_client.py
from supabase import create_client
import os

# You can switch later to env variables for deployment.
SUPABASE_URL = "https://qfpqrkvovdjzxshfbyuq.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFmcHFya3ZvdmRqenhzaGZieXVxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTkxNjk2MCwiZXhwIjoyMDc3NDkyOTYwfQ."
    "Gl2LCeRFNLtiQS8UanuF15r6Iso50czuqBfoOv1JkNY"
)

def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

