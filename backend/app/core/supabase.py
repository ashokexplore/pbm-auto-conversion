"""
Supabase client configuration
"""
from supabase import create_client, Client
from app.core.config import settings


def get_supabase_client() -> Client:
    """
    Get Supabase client instance
    
    Returns:
        Client: Supabase client
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("Supabase credentials are not configured")
    
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_supabase_admin_client() -> Client:
    """
    Get Supabase admin client with service role key
    Use this for server-side operations that bypass RLS
    
    Returns:
        Client: Supabase admin client
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise ValueError("Supabase admin credentials are not configured")
    
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


# Global client instance
supabase: Client = get_supabase_client()
supabase_admin: Client = get_supabase_admin_client()

