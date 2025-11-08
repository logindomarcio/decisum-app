"""
Serviço de Limpeza Automática
Gerencia a sustentabilidade do sistema removendo dados antigos
"""
import streamlit as st
from datetime import datetime, timedelta
from config.supabase_config import get_supabase_client
from components.auth_components import get_current_user, is_admin

def auto_cleanup_old_processes():
    """
    Remove processos com mais de 6 horas automaticamente
    Executa automaticamente quando o usuário acessa o sistema
    """
    try:
        supabase = get_supabase_client()
        
        # Calcular 6 horas atrás
        six_hours_ago = datetime.now() - timedelta(hours=6)
        cutoff_time = six_hours_ago.isoformat()
        
        # Buscar processos antigos
        old_processes = supabase.table("processes").select("id, filename, created_at").lt("created_at", cutoff_time).execute()
        
        if old_processes.data:
            # Deletar processos antigos
            for process in old_processes.data:
                supabase.table("processes").delete().eq("id", process["id"]).execute()
            
            return True, len(old_processes.data)
        
        return True, 0
    
    except Exception as e:
        return False, str(e)

def cleanup_old_decisions():
    """
    Remove decisões geradas com mais de 24 horas
    """
    try:
        supabase = get_supabase_client()
        
        # Calcular 24 horas atrás
        twentyfour_hours_ago = datetime.now() - timedelta(hours=24)
        cutoff_time = twentyfour_hours_ago.isoformat()
        
        # Buscar decisões antigas
        old_decisions = supabase.table("decisions").select("id").lt("created_at", cutoff_time).execute()
        
        if old_decisions.data:
            # Deletar decisões antigas
            for decision in old_decisions.data:
                supabase.table("decisions").delete().eq("id", decision["id"]).execute()
            
            return True, len(old_decisions.data)
        
        return True, 0
    
    except Exception as e:
        return False, str(e)

def enforce_user_limits():
    """
    Garante que cada usuário tenha no máximo 5 processos ativos
    Remove os mais antigos se exceder o limite
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        # Buscar processos do usuário ordenados por data (mais recente primeiro)
        user_processes = supabase.table("processes").select("id, filename, created_at").eq("user_id", user_data["id"]).order("created_at", desc=True).execute()
        
        if len(user_processes.data) > 5:
            # Remover processos além do limite (manter apenas os 5 mais recentes)
            processes_to_remove = user_processes.data[5:]  # Pega do 6º em diante
            
            for process in processes_to_remove:
                supabase.table("processes").delete().eq("id", process["id"]).execute()
            
            return True, len(processes_to_remove)
        
        return True, 0
    
    except Exception as e:
        return False, str(e)

def get_system_stats():
    """
    Retorna estatísticas do sistema para monitoramento
    """
    try:
        supabase = get_supabase_client()
        
        # Contar total de registros
        processes_count = supabase.table("processes").select("id", count="exact").execute()
        prompts_count = supabase.table("prompts").select("id", count="exact").execute()
        decisions_count = supabase.table("decisions").select("id", count="exact").execute()
        users_count = supabase.table("users").select("id", count="exact").execute()
        
        # Processos por usuário
        user_data = get_current_user()
        user_processes = supabase.table("processes").select("id", count="exact").eq("user_id", user_data["id"]).execute()
        
        # Calcular tamanho aproximado dos dados
        recent_processes = supabase.table("processes").select("txt_content").limit(10).execute()
        avg_size = 0
        if recent_processes.data:
            total_chars = sum(len(p.get("txt_content", "")) for p in recent_processes.data)
            avg_size = total_chars / len(recent_processes.data) if recent_processes.data else 0
        
        return {
            "total_processes": processes_count.count or 0,
            "total_prompts": prompts_count.count or 0, 
            "total_decisions": decisions_count.count or 0,
            "total_users": users_count.count or 0,
            "user_processes": user_processes.count or 0,
            "avg_process_size": avg_size,
            "success": True
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def manual_cleanup_user_data():
    """
    Permite ao usuário limpar seus próprios dados manualmente
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        # Contar dados do usuário antes da limpeza
        user_processes = supabase.table("processes").select("id", count="exact").eq("user_id", user_data["id"]).execute()
        user_decisions = supabase.table("decisions").select("id", count="exact").eq("user_id", user_data["id"]).execute()
        
        processes_count = user_processes.count or 0
        decisions_count = user_decisions.count or 0
        
        # Deletar processos do usuário
        if processes_count > 0:
            supabase.table("processes").delete().eq("user_id", user_data["id"]).execute()
        
        # Deletar decisões do usuário  
        if decisions_count > 0:
            supabase.table("decisions").delete().eq("user_id", user_data["id"]).execute()
        
        return True, processes_count, decisions_count
    
    except Exception as e:
        return False, 0, 0

def admin_cleanup_system():
    """
    Limpeza completa do sistema (apenas para admins)
    """
    try:
        if not is_admin():
            return False, "Acesso negado: apenas administradores podem executar limpeza completa"
        
        supabase = get_supabase_client()
        
        # Contar registros antes da limpeza
        processes_count = supabase.table("processes").select("id", count="exact").execute().count or 0
        decisions_count = supabase.table("decisions").select("id", count="exact").execute().count or 0
        
        # Deletar todos os processos
        if processes_count > 0:
            supabase.table("processes").delete().neq("id", "").execute()  # Delete all
        
        # Deletar todas as decisões
        if decisions_count > 0:
            supabase.table("decisions").delete().neq("id", "").execute()  # Delete all
        
        return True, f"Removidos: {processes_count} processos e {decisions_count} decisões"
    
    except Exception as e:
        return False, str(e)

def check_storage_usage():
    """
    Verifica uso aproximado de armazenamento
    """
    try:
        stats = get_system_stats()
        if not stats["success"]:
            return "Erro ao calcular uso de armazenamento"
        
        # Estimativa aproximada
        total_processes = stats["total_processes"]
        avg_size = stats["avg_process_size"]
        estimated_mb = (total_processes * avg_size) / (1024 * 1024)  # Converter para MB
        
        if estimated_mb < 1:
            return f"~{estimated_mb*1000:.0f} KB"
        elif estimated_mb < 1024:
            return f"~{estimated_mb:.1f} MB"
        else:
            return f"~{estimated_mb/1024:.1f} GB"
    
    except:
        return "Cálculo indisponível"

# Função para executar limpeza automática no início da sessão
def run_auto_cleanup():
    """
    Executa limpeza automática silenciosa quando necessário
    """
    if 'auto_cleanup_done' not in st.session_state:
        try:
            # Executar limpezas automáticas
            auto_cleanup_old_processes()
            cleanup_old_decisions()
            enforce_user_limits()
            
            # Marcar como executado nesta sessão
            st.session_state.auto_cleanup_done = True
        except:
            pass  # Falha silenciosa para não interromper o fluxo do usuário