"""
Decisum - App Principal
Sistema de Decisões Judiciais com Autenticação
"""
import streamlit as st
import sys
import os
from datetime import datetime

# Adicionar pastas ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))

from config.supabase_config import test_connection
from components.auth_components import (
    show_login_page, check_authentication, get_current_user, 
    is_admin, show_admin_panel, show_logout_button
)
from components.process_components import (
    show_process_upload, show_process_list, show_process_viewer
)
from components.decision_generator_v2 import show_decision_generator_v3
from components.prompt_manager import show_prompt_manager

def main():
    st.set_page_config(
        page_title="Decisum",
        page_icon="⚖️",
        layout="wide"
    )
    
    # Executar limpeza automática silenciosa
    from services.cleanup_service import run_auto_cleanup
    run_auto_cleanup()
    
    # Verificar se usuário está logado
    if not check_authentication():
        show_login_page()
        return
    
    # Usuário logado - mostrar aplicação principal
    user_data = get_current_user()
    
    # Sidebar com info do usuário
    with st.sidebar:
        st.title("⚖️ Decisum")
        st.write(f"Bem-vindo, **{user_data.get('email')}**")
        st.write(f"Perfil: **{user_data.get('role').title()}**")
        
        # Menu principal
        st.divider()
        
        if is_admin():
            page = st.selectbox(
                "Navegação",
                ["Dashboard", "Painel Admin", "Upload Processo", "Meus Processos", "Gerar Decisões", "Gerenciar Prompts", "Configurações"]
            )
        else:
            page = st.selectbox(
                "Navegação", 
                ["Dashboard", "Upload Processo", "Meus Processos", "Gerenciar Prompts", "Gerar Decisões", "Configurações"]
            )
        
        show_logout_button()
    
    # Conteúdo principal baseado na página selecionada
    if page == "Dashboard":
        show_dashboard()
    elif page == "Painel Admin" and is_admin():
        show_admin_panel()
    elif page == "Upload Processo":
        show_upload_page()
    elif page == "Meus Processos":
        show_my_processes_page()
    elif page == "Gerenciar Prompts":
        show_prompt_manager()
    elif page == "Gerar Decisões":
        show_decision_generator()
    elif page == "Configurações":
        show_settings()
    else:
        st.info(f"Página '{page}' em desenvolvimento...")

def show_dashboard():
    """Página principal do dashboard com estatísticas colaborativas"""
    st.title("📊 Dashboard - Decisum")
    
    from services.stats_service import (
        get_system_overview, get_decision_stats, get_top_legal_areas, 
        get_recent_prompts, get_top_prompt_contributors, format_time_ago
    )
    
    user_data = get_current_user()
    
    # Boas vindas personalizada
    st.markdown(f"### Bem-vindo, **{user_data.get('email').split('@')[0].title()}**! 👋")
    st.markdown("*Visão colaborativa de toda a comunidade Decisum*")
    
    # Seção 1: Visão Geral do Sistema
    st.markdown("### 🌐 Visão Geral da Comunidade")
    
    overview = get_system_overview()
    if overview["success"]:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "👥 Usuários Totais", 
                overview["total_users"], 
                f"{overview['active_users']} ativos"
            )
        
        with col2:
            st.metric(
                "🎯 Prompts Públicos", 
                overview["total_prompts"],
                "Colaborativos"
            )
        
        with col3:
            st.metric(
                "📄 Processos Ativos", 
                overview["total_processes"],
                "Sendo analisados"
            )
        
        with col4:
            st.metric(
                "⚖️ Sistema", 
                "Online",
                "🟢 Estável"
            )
    
    st.divider()
    
    # Seção 2: Estatísticas de Decisões Geradas
    st.markdown("### ⚖️ Decisões Geradas pela Comunidade")
    
    decision_stats = get_decision_stats()
    if decision_stats["success"] and decision_stats["total_decisions"] > 0:
        col_stats, col_chart = st.columns([1, 2])
        
        with col_stats:
            st.metric(
                "Total de Decisões",
                decision_stats["total_decisions"],
                f"+{decision_stats['recent_count']} esta semana"
            )
            
            st.markdown("**Por Tipo:**")
            for tipo, count in decision_stats["by_type"].items():
                percentage = (count / decision_stats["total_decisions"]) * 100 if decision_stats["total_decisions"] > 0 else 0
                st.write(f"• **{tipo}**: {count} ({percentage:.1f}%)")
        
        with col_chart:
            # Dados para gráfico
            chart_data = {
                "Tipo de Decisão": list(decision_stats["by_type"].keys()),
                "Quantidade": list(decision_stats["by_type"].values())
            }
            
            if any(chart_data["Quantidade"]):  # Se há dados para mostrar
                st.bar_chart(data=chart_data, x="Tipo de Decisão", y="Quantidade", color="#1f77b4")
            else:
                st.info("Aguardando primeiras decisões geradas...")
    
    else:
        st.info("🚀 **Primeiras decisões em breve!** Quando a comunidade começar a gerar decisões, as estatísticas aparecerão aqui.")
    
    st.divider()
    
    # Seção 3: Top 5 Áreas Jurídicas
    col_areas, col_contributors = st.columns(2)
    
    with col_areas:
        st.markdown("### 🏛️ Top 5 Áreas Jurídicas")
        
        top_areas = get_top_legal_areas()
        if top_areas["success"] and top_areas["areas"]:
            for i, area_data in enumerate(top_areas["areas"], 1):
                # Emoji baseado na posição
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
                
                st.markdown(f"""
                **{emoji} {area_data['area']}**  
                `{area_data['count']} prompt{'s' if area_data['count'] != 1 else ''}`
                """)
        else:
            st.info("📋 Áreas aparecerão conforme prompts forem criados.")
    
    with col_contributors:
        st.markdown("### 🏆 Top Contribuidores de Prompts")
        
        top_contributors = get_top_prompt_contributors()
        if top_contributors["success"] and top_contributors["contributors"]:
            for i, contributor in enumerate(top_contributors["contributors"][:5], 1):
                # Emoji baseado na posição
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
                
                st.markdown(f"""
                **{emoji} {contributor['user']}**  
                `{contributor['count']} prompt{'s' if contributor['count'] != 1 else ''} criado{'s' if contributor['count'] != 1 else ''}`
                """)
        else:
            st.info("🏆 Ranking aparecerá conforme usuários contribuírem.")
    
    st.divider()
    
    # Seção 4: Últimos Prompts Adicionados
    st.markdown("### 🆕 Últimos Prompts da Comunidade")
    
    recent_prompts = get_recent_prompts()
    if recent_prompts["success"] and recent_prompts["prompts"]:
        # Mostrar últimos 5 prompts em cards
        for prompt in recent_prompts["prompts"][:5]:
            time_ago = format_time_ago(prompt["created_at"])
            
            with st.container():
                col_info, col_meta = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"""
                    **📝 {prompt['title']}**  
                    `{prompt['area']} → {prompt['type']}`  
                    Por: {prompt['creator']}
                    """)
                
                with col_meta:
                    st.markdown(f"""
                    <div style="text-align: right; color: #666; font-size: 0.8em;">
                    {time_ago}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
        
        # Link para ver todos
        if len(recent_prompts["prompts"]) > 5:
            st.markdown("*💡 Veja mais prompts em 'Gerenciar Prompts' → 'Biblioteca Pública'*")
    
    else:
        st.info("📝 Últimos prompts aparecerão aqui conforme forem criados pela comunidade.")
    
    st.divider()
    
    # Seção final: Teste de Conexão (mantido para desenvolvimento)
    with st.expander("🔧 Testes de Sistema (Desenvolvimento)"):
        if st.button("Testar Conexão Supabase"):
            with st.spinner("Testando..."):
                if test_connection():
                    st.success("✅ Conexão funcionando!")
                else:
                    st.error("❌ Erro na conexão")
        
        # Mostrar detalhes técnicos para debug
        st.markdown("**Debug Info:**")
        st.json({
            "user_id": user_data.get("id", "N/A"),
            "role": user_data.get("role", "user"),
            "timestamp": datetime.now().isoformat()
        })

def show_decision_generator():
    """Página de geração de decisões - Versão 3.1 MELHORADA"""
    from components.decision_generator_v3_improved import show_decision_generator_v3_improved
    show_decision_generator_v3_improved()

def show_settings():
    """Página de configurações com limpeza automática"""
    st.title("⚙️ Configurações")
    
    from services.gemini_service import get_user_gemini_key, save_user_gemini_key, validate_gemini_key
    from services.cleanup_service import get_system_stats, manual_cleanup_user_data, admin_cleanup_system, check_storage_usage
    
    # Seção 1: Chave API Gemini
    st.subheader("🔑 Chave API Gemini")
    st.markdown("""
    **Para usar o sistema de geração de decisões, você precisa de uma chave API do Google Gemini.**
    
    **Como obter:**
    1. Acesse: https://ai.google.dev/
    2. Faça login com sua conta Google
    3. Vá em "Get API Key"
    4. Crie uma nova chave API gratuita
    5. Cole a chave no campo abaixo
    """)
    
    # Verificar se já tem chave salva
    current_key = get_user_gemini_key()
    key_status = "✅ Configurada" if current_key else "❌ Não configurada"
    
    st.info(f"**Status atual:** {key_status}")
    
    # Campo para inserir/atualizar chave
    with st.form("gemini_config_form"):
        gemini_key = st.text_input(
            "Cole sua chave API do Google Gemini:",
            type="password",
            value=current_key,
            help="Sua chave será armazenada de forma segura e criptografada"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            test_button = st.form_submit_button("🧪 Testar Chave", use_container_width=True)
        
        with col2:
            save_button = st.form_submit_button("💾 Salvar Chave", type="primary", use_container_width=True)
        
        if test_button and gemini_key:
            with st.spinner("Testando conexão com Gemini..."):
                if validate_gemini_key(gemini_key):
                    st.success("✅ Chave API válida e funcionando!")
                else:
                    st.error("❌ Chave API inválida ou com problema de conexão!")
        
        if save_button:
            if gemini_key:
                if save_user_gemini_key(gemini_key):
                    st.success("✅ Chave API salva com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar chave!")
            else:
                st.error("❌ Digite uma chave válida!")
    
    st.divider()
    
    # Seção 2: Gerenciamento de Dados e Limpeza
    st.subheader("🧹 Gerenciamento de Dados")
    st.markdown("*O sistema automaticamente remove dados antigos para manter a performance.*")
    
    # Estatísticas do sistema
    stats = get_system_stats()
    if stats["success"]:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Seus Processos", stats["user_processes"], help="Máximo: 5 processos")
        
        with col2:
            st.metric("Total Processos", stats["total_processes"])
        
        with col3:
            st.metric("Total Usuários", stats["total_users"])
        
        with col4:
            storage_usage = check_storage_usage()
            st.metric("Uso Estimado", storage_usage)
        
        # Indicadores de sustentabilidade
        if stats["user_processes"] >= 5:
            st.warning("⚠️ Você atingiu o limite de 5 processos. Os mais antigos serão removidos automaticamente.")
        elif stats["user_processes"] >= 3:
            st.info(f"ℹ️ Você tem {stats['user_processes']}/5 processos. Espaço restante: {5 - stats['user_processes']}")
        else:
            st.success(f"✅ Você tem {stats['user_processes']}/5 processos. Sistema otimizado!")
    
    # Regras de limpeza automática
    with st.expander("📋 Regras de Limpeza Automática"):
        st.markdown("""
        **O sistema automaticamente remove:**
        
        - 🕰️ **Processos** com mais de **6 horas**
        - 📝 **Decisões geradas** com mais de **24 horas**  
        - 📊 **Limite por usuário:** máximo **5 processos** simultâneos
        - 🔄 **Execução:** a cada acesso ao sistema
        
        **Por que fazemos isso?**
        - ⚡ Manter sistema rápido e responsivo
        - 💾 Evitar sobrecarga do banco de dados
        - 🔒 Proteger dados sensíveis (não ficam armazenados)
        - 🌱 Sustentabilidade para todos os usuários
        """)
    
    # Ações manuais de limpeza
    st.markdown("### 🗑️ Limpeza Manual")
    
    col_user, col_admin = st.columns(2)
    
    with col_user:
        st.markdown("**Limpar Seus Dados**")
        if st.button("🗑️ Limpar Meus Processos", type="secondary", use_container_width=True):
            with st.spinner("Limpando seus dados..."):
                success, processes_removed, decisions_removed = manual_cleanup_user_data()
                if success:
                    st.success(f"✅ Removidos: {processes_removed} processos e {decisions_removed} decisões")
                    st.rerun()
                else:
                    st.error("❌ Erro na limpeza manual")
    
    with col_admin:
        if is_admin():
            st.markdown("**Limpeza Administrativa**")
            if st.button("⚠️ Limpar Todo Sistema", type="secondary", use_container_width=True):
                with st.spinner("Executando limpeza completa..."):
                    success, message = admin_cleanup_system()
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        else:
            st.markdown("**Apenas Administradores**")
            st.button("⚠️ Limpar Todo Sistema", disabled=True, use_container_width=True, help="Acesso restrito a administradores")
    
    st.divider()
    
    # Seção 3: Informações do Sistema
    st.subheader("📊 Informações do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Prompts Disponíveis", stats.get("total_prompts", "N/A"), "Crescendo")
        st.metric("Decisões Geradas", stats.get("total_decisions", "N/A"), "Histórico 24h")
    
    with col2:
        st.metric("Versão Sistema", "3.1", "Limpeza Auto")
        st.metric("Status", "🟢 Ativo", "Sustentável")
    
    # Ajuda e suporte
    st.divider()
    
    st.subheader("❓ Precisa de Ajuda?")
    
    with st.expander("🔧 Solução de Problemas"):
        st.markdown("""
        **Problemas comuns:**
        
        - **Processo sumiu**: Sistema remove automaticamente após 6h
        - **Limite atingido**: Máximo 5 processos por usuário
        - **Erro de chave API**: Verifique se a chave foi copiada corretamente
        - **Geração lenta**: Normal para decisões complexas (até 2-3 minutos)
        - **PDF não processado**: Certifique-se que é um PDF com texto (não imagem)
        
        **Dicas de uso:**
        - Baixe decisões importantes antes das 24h
        - Use instruções claras e específicas
        - Mantenha apenas processos ativos necessários
        """)
    
    with st.expander("📋 Limites e Políticas"):
        st.markdown("""
        **Limites por usuário:**
        - Processos simultâneos: 5 máximo
        - Tamanho PDF: até 200MB  
        - Retenção processos: 6 horas
        - Retenção decisões: 24 horas
        
        **Política de uso:**
        - Sistema para uso profissional ético
        - Dados são temporários e não persistentes
        - Usuário responsável pelo conteúdo gerado
        - Sempre revisar decisões antes do uso
        """)
    
    st.divider()
    
    # Ações avançadas
    col_cache, col_stats = st.columns(2)
    
    with col_cache:
        if st.button("🔄 Limpar Cache Sistema"):
            # Limpar session_state
            keys_to_clear = ['generated_decision', 'generation_data', 'selected_legal_area', 
                            'selected_decision_type', 'selected_prompt', 'depoimentos_processados',
                            'processes_cache', 'viewing_prompt', 'editing_prompt', 'auto_cleanup_done']
            cleared_count = 0
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
                    cleared_count += 1
            
            if cleared_count > 0:
                st.success(f"✅ Cache limpo! {cleared_count} itens removidos.")
            else:
                st.info("ℹ️ Cache já estava limpo.")
    
    with col_stats:
        if st.button("📊 Atualizar Estatísticas"):
            st.rerun()

def show_upload_page():
    """Página de upload de processos"""
    st.title("📤 Upload de Processo")
    show_process_upload()

def show_my_processes_page():
    """Página de gerenciamento de processos"""
    st.title("📁 Meus Processos")
    
    # Verificar se está visualizando um processo específico
    if 'selected_process' in st.session_state:
        show_process_viewer()
    else:
        show_process_list()

if __name__ == "__main__":
    main()