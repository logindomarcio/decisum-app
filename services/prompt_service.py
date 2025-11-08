"""
Serviço de Prompts - Versão 2
Gerenciamento de prompts colaborativos
"""
import streamlit as st
from config.supabase_config import get_supabase_client
from components.auth_components import get_current_user

def get_prompts_by_area_and_type(legal_area: str, decision_type: str):
    """
    Busca prompts por área jurídica e tipo de decisão
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("prompts").select("*").eq("legal_area", legal_area).eq("decision_type", decision_type).eq("is_public", True).execute()
        
        return result.data
    except Exception as e:
        st.error(f"Erro ao buscar prompts: {e}")
        return []

def get_all_prompts():
    """
    Retorna todos os prompts públicos
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("prompts").select("*").eq("is_public", True).order("created_at", desc=True).execute()
        
        return result.data
    except Exception as e:
        st.error(f"Erro ao buscar prompts: {e}")
        return []

def create_prompt(title: str, legal_area: str, decision_type: str, description: str, instruction: str, paradigm_block: str = ""):
    """
    Cria um novo prompt
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        result = supabase.table("prompts").insert({
            "title": title,
            "legal_area": legal_area,
            "decision_type": decision_type,
            "description": description,
            "instruction": instruction,
            "paradigm_block": paradigm_block,
            "created_by": user_data["id"],
            "is_public": True
        }).execute()
        
        return True, "Prompt criado com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao criar prompt: {e}"

def get_user_prompts():
    """
    Retorna prompts criados pelo usuário atual
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        result = supabase.table("prompts").select("*").eq("created_by", user_data["id"]).order("created_at", desc=True).execute()
        
        return result.data
    except Exception as e:
        st.error(f"Erro ao buscar seus prompts: {e}")
        return []

def delete_prompt(prompt_id: str):
    """
    Deleta um prompt (apenas o criador ou admin)
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        # Verificar se é o criador ou admin
        if user_data.get("role") == "admin":
            result = supabase.table("prompts").delete().eq("id", prompt_id).execute()
        else:
            result = supabase.table("prompts").delete().eq("id", prompt_id).eq("created_by", user_data["id"]).execute()
        
        return True, "Prompt deletado com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao deletar prompt: {e}"

def update_prompt(prompt_id: str, title: str, description: str, instruction: str, paradigm_block: str):
    """
    Atualiza um prompt existente
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        # Verificar se é o criador ou admin
        if user_data.get("role") == "admin":
            result = supabase.table("prompts").update({
                "title": title,
                "description": description,
                "instruction": instruction,
                "paradigm_block": paradigm_block
            }).eq("id", prompt_id).execute()
        else:
            result = supabase.table("prompts").update({
                "title": title,
                "description": description,
                "instruction": instruction,
                "paradigm_block": paradigm_block
            }).eq("id", prompt_id).eq("created_by", user_data["id"]).execute()
        
        return True, "Prompt atualizado com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao atualizar prompt: {e}"

# Mapeamento das áreas jurídicas
LEGAL_AREAS = {
    "Direito Civil": "Direito Civil",
    "Direito de Família": "Direito de Família", 
    "Direito Penal": "Direito Penal",
    "Fazenda Pública": "Fazenda Pública",
    "Justiça da Infância e da Juventude": "Justiça da Infância e da Juventude",
    "Contratos Bancários": "Contratos Bancários",
    "Competência Delegada e Acidentes de Trabalho": "Competência Delegada e Acidentes de Trabalho",
    "Outros": "Outros"
}

DECISION_TYPES = {
    "Despacho": "Despacho",
    "Decisão": "Decisão", 
    "Sentença": "Sentença"
}