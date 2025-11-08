"""
Serviço de Estatísticas Colaborativas
Dashboard com métricas compartilhadas entre todos os usuários
"""
import streamlit as st
from config.supabase_config import get_supabase_client
from datetime import datetime, timedelta

def get_decision_stats():
    """
    Retorna estatísticas de decisões geradas por tipo
    """
    try:
        supabase = get_supabase_client()
        
        # Buscar todas as decisões com informações dos prompts
        result = supabase.table("decisions").select("""
            id,
            created_at,
            prompts!inner(decision_type, legal_area, title)
        """).execute()
        
        if not result.data:
            return {
                "total_decisions": 0,
                "by_type": {"Despacho": 0, "Decisão": 0, "Sentença": 0},
                "recent_count": 0,
                "success": True
            }
        
        # Contar por tipo
        type_counts = {"Despacho": 0, "Decisão": 0, "Sentença": 0}
        recent_count = 0
        
        # Data de 7 dias atrás para contar decisões recentes
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        for decision in result.data:
            decision_type = decision["prompts"]["decision_type"]
            if decision_type in type_counts:
                type_counts[decision_type] += 1
            
            # Contar decisões recentes
            created_date = datetime.fromisoformat(decision["created_at"].replace('Z', '+00:00'))
            if created_date >= seven_days_ago:
                recent_count += 1
        
        return {
            "total_decisions": len(result.data),
            "by_type": type_counts,
            "recent_count": recent_count,
            "success": True
        }
    
    except Exception as e:
        return {
            "total_decisions": 0,
            "by_type": {"Despacho": 0, "Decisão": 0, "Sentença": 0},
            "recent_count": 0,
            "error": str(e),
            "success": False
        }

def get_top_legal_areas():
    """
    Retorna as 5 principais áreas jurídicas dos prompts
    """
    try:
        supabase = get_supabase_client()
        
        # Buscar todos os prompts públicos com contagem por área
        result = supabase.table("prompts").select("legal_area").eq("is_public", True).execute()
        
        if not result.data:
            return {"areas": [], "success": True}
        
        # Contar por área jurídica
        area_counts = {}
        for prompt in result.data:
            area = prompt["legal_area"]
            area_counts[area] = area_counts.get(area, 0) + 1
        
        # Ordenar e pegar top 5
        top_areas = sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "areas": [{"area": area, "count": count} for area, count in top_areas],
            "success": True
        }
    
    except Exception as e:
        return {
            "areas": [],
            "error": str(e),
            "success": False
        }

def get_recent_prompts():
    """
    Retorna os últimos prompts adicionados (públicos)
    """
    try:
        supabase = get_supabase_client()
        
        # Buscar últimos 10 prompts públicos com dados do criador
        result = supabase.table("prompts").select("""
            id,
            title,
            legal_area,
            decision_type,
            created_at,
            users!inner(email)
        """).eq("is_public", True).order("created_at", desc=True).limit(10).execute()
        
        if not result.data:
            return {"prompts": [], "success": True}
        
        # Formatar dados
        formatted_prompts = []
        for prompt in result.data:
            # Mascarar email para privacidade (mostrar só primeiro nome)
            email = prompt["users"]["email"]
            masked_email = email.split("@")[0][:3] + "***" if email else "Usuário"
            
            formatted_prompts.append({
                "title": prompt["title"],
                "area": prompt["legal_area"],
                "type": prompt["decision_type"], 
                "created_at": prompt["created_at"],
                "creator": masked_email
            })
        
        return {
            "prompts": formatted_prompts,
            "success": True
        }
    
    except Exception as e:
        return {
            "prompts": [],
            "error": str(e),
            "success": False
        }

def get_top_prompt_contributors():
    """
    Retorna top 10 usuários que mais contribuíram com prompts
    """
    try:
        supabase = get_supabase_client()
        
        # Buscar prompts com dados dos criadores
        result = supabase.table("prompts").select("""
            created_by,
            users!inner(email)
        """).eq("is_public", True).execute()
        
        if not result.data:
            return {"contributors": [], "success": True}
        
        # Contar prompts por usuário
        user_counts = {}
        for prompt in result.data:
            email = prompt["users"]["email"]
            # Mascarar email para privacidade
            masked_email = email.split("@")[0][:4] + "***" if email else "Usuário"
            user_counts[masked_email] = user_counts.get(masked_email, 0) + 1
        
        # Ordenar e pegar top 10
        top_contributors = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "contributors": [{"user": user, "count": count} for user, count in top_contributors],
            "success": True
        }
    
    except Exception as e:
        return {
            "contributors": [],
            "error": str(e),
            "success": False
        }

def get_system_overview():
    """
    Retorna visão geral do sistema para o dashboard
    """
    try:
        supabase = get_supabase_client()
        
        # Contar totais
        total_users = supabase.table("users").select("id", count="exact").execute().count or 0
        total_prompts = supabase.table("prompts").select("id", count="exact").eq("is_public", True).execute().count or 0
        total_processes = supabase.table("processes").select("id", count="exact").execute().count or 0
        
        # Usuários ativos (que fizeram login nas últimas 24h ou têm processos)
        active_users = supabase.table("processes").select("user_id").execute()
        unique_active_users = len(set(p["user_id"] for p in active_users.data)) if active_users.data else 0
        
        return {
            "total_users": total_users,
            "active_users": unique_active_users,
            "total_prompts": total_prompts,
            "total_processes": total_processes,
            "success": True
        }
    
    except Exception as e:
        return {
            "total_users": 0,
            "active_users": 0,
            "total_prompts": 0,
            "total_processes": 0,
            "error": str(e),
            "success": False
        }

def format_time_ago(created_at):
    """
    Formata data para 'X tempo atrás'
    """
    try:
        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now(created_date.tzinfo)
        diff = now - created_date
        
        if diff.days > 0:
            return f"{diff.days}d atrás"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h atrás"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}min atrás"
        else:
            return "Agora"
    except:
        return "Recente"