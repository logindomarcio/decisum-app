"""
Serviço de Autenticação
"""
import hashlib
import streamlit as st
from config.supabase_config import get_supabase_client

def hash_password(password: str) -> str:
    """Gera hash da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verifica se a senha está correta"""
    return hash_password(password) == hashed

def register_user(email: str, password: str) -> tuple[bool, str]:
    """
    Registra novo usuário
    Returns: (sucesso, mensagem)
    """
    try:
        supabase = get_supabase_client()
        
        # Verificar se email já existe
        result = supabase.table("users").select("email").eq("email", email).execute()
        if result.data:
            return False, "Email já cadastrado!"
        
        # Criar usuário
        password_hash = hash_password(password)
        result = supabase.table("users").insert({
            "email": email,
            "password_hash": password_hash,
            "role": "user",
            "approved": False  # Precisa aprovação do admin
        }).execute()
        
        return True, "Usuário registrado! Aguarde aprovação do administrador."
    
    except Exception as e:
        return False, f"Erro ao registrar: {e}"

def login_user(email: str, password: str) -> tuple[bool, str, dict]:
    """
    Faz login do usuário
    Returns: (sucesso, mensagem, dados_usuario)
    """
    try:
        supabase = get_supabase_client()
        
        # Buscar usuário
        result = supabase.table("users").select("*").eq("email", email).execute()
        
        if not result.data:
            return False, "Email não encontrado!", {}
        
        user = result.data[0]
        
        # Verificar senha
        if not verify_password(password, user["password_hash"]):
            return False, "Senha incorreta!", {}
        
        # Verificar se está aprovado
        if not user["approved"]:
            return False, "Usuário ainda não foi aprovado pelo administrador!", {}
        
        return True, "Login realizado com sucesso!", user
    
    except Exception as e:
        return False, f"Erro no login: {e}", {}

def get_pending_users():
    """Retorna usuários pendentes de aprovação"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("users").select("*").eq("approved", False).execute()
        return result.data
    except Exception as e:
        st.error(f"Erro ao buscar usuários: {e}")
        return []

def approve_user(user_id: str) -> bool:
    """Aprova um usuário"""
    try:
        supabase = get_supabase_client()
        supabase.table("users").update({"approved": True}).eq("id", user_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao aprovar usuário: {e}")
        return False