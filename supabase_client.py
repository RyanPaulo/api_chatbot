from supabase import create_client, Client
from config import settings

# Inicializa o cliente Supabase
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY )
