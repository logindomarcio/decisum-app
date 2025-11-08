"""
Serviço de Processamento de PDFs
"""
import PyPDF2
import io
import streamlit as st
from config.supabase_config import get_supabase_client
from components.auth_components import get_current_user

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extrai texto de um arquivo PDF
    """
    try:
        # Ler o arquivo PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        st.error(f"Erro ao processar PDF: {e}")
        return ""

def save_process_to_db(filename: str, txt_content: str) -> bool:
    """
    Salva o processo no banco de dados
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        result = supabase.table("processes").insert({
            "filename": filename,
            "txt_content": txt_content,
            "user_id": user_data["id"]
        }).execute()
        
        return True
    
    except Exception as e:
        st.error(f"Erro ao salvar processo: {e}")
        return False

def get_user_processes():
    """
    Retorna todos os processos do usuário atual
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        result = supabase.table("processes").select("*").eq("user_id", user_data["id"]).order("created_at", desc=True).execute()
        
        return result.data
    
    except Exception as e:
        st.error(f"Erro ao buscar processos: {e}")
        return []

def get_process_by_id(process_id: str):
    """
    Retorna um processo específico pelo ID
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("processes").select("*").eq("id", process_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    except Exception as e:
        st.error(f"Erro ao buscar processo: {e}")
        return None

def delete_process(process_id: str) -> bool:
    """
    Deleta um processo
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        # Verificar se o processo pertence ao usuário
        result = supabase.table("processes").delete().eq("id", process_id).eq("user_id", user_data["id"]).execute()
        
        return True
    
    except Exception as e:
        st.error(f"Erro ao deletar processo: {e}")
        return False

def search_processes(query: str):
    """
    Busca processos por nome ou conteúdo
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        # Buscar por nome do arquivo
        result = supabase.table("processes").select("*").eq("user_id", user_data["id"]).ilike("filename", f"%{query}%").execute()
        
        return result.data
    
    except Exception as e:
        st.error(f"Erro na busca: {e}")
        return []