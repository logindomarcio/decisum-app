"""
Configuração do Supabase
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_supabase_client() -> Client:
    """
    Cria e retorna cliente do Supabase
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("Credenciais do Supabase não encontradas no arquivo .env")
    
    return create_client(url, key)

def test_connection():
    """
    Testa a conexão com o Supabase
    """
    try:
        supabase = get_supabase_client()
        # Tenta fazer uma consulta simples na tabela users
        result = supabase.table("users").select("*").limit(1).execute()
        print("✅ Conexão com Supabase funcionando!")
        print(f"✅ Encontrados {len(result.data)} registros na tabela users")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    test_connection()