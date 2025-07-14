from utils.supabase_client import supabase

data = supabase.table("Hiring Intel").select("*").limit(1).execute()
print(data)
