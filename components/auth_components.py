"""
Componentes de Autenticação - Interface
"""
import streamlit as st
from services.auth_service import register_user, login_user, get_pending_users, approve_user

def show_login_page():
    """Exibe página de login"""
    st.title("🔐 Login - Decisum")
    
    # Criar duas colunas: Login e Registro
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Fazer Login")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            login_button = st.form_submit_button("Entrar")
            
            if login_button:
                if email and password:
                    success, message, user_data = login_user(email, password)
                    
                    if success:
                        # Salvar dados do usuário na sessão
                        st.session_state.user_logged_in = True
                        st.session_state.user_data = user_data
                        st.success(message)
                        st.rerun()  # Atualiza a página
                    else:
                        st.error(message)
                else:
                    st.error("Preencha email e senha!")
    
    with col2:
        st.subheader("Criar Conta")
        
        with st.form("register_form"):
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Senha", type="password", key="reg_password")
            reg_password_confirm = st.text_input("Confirmar Senha", type="password")
            register_button = st.form_submit_button("Registrar")
            
            if register_button:
                if reg_email and reg_password and reg_password_confirm:
                    if reg_password != reg_password_confirm:
                        st.error("Senhas não conferem!")
                    elif len(reg_password) < 6:
                        st.error("Senha deve ter pelo menos 6 caracteres!")
                    else:
                        success, message = register_user(reg_email, reg_password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                else:
                    st.error("Preencha todos os campos!")

def show_admin_panel():
    """Painel administrativo"""
    st.title("👨‍💼 Painel Administrativo")
    
    st.subheader("Usuários Pendentes de Aprovação")
    
    pending_users = get_pending_users()
    
    if not pending_users:
        st.info("Nenhum usuário pendente de aprovação.")
    else:
        for user in pending_users:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"📧 **{user['email']}**")
                st.write(f"📅 Cadastrado em: {user['created_at'][:10]}")
            
            with col2:
                if st.button("✅ Aprovar", key=f"approve_{user['id']}"):
                    if approve_user(user['id']):
                        st.success(f"Usuário {user['email']} aprovado!")
                        st.rerun()
            
            with col3:
                if st.button("❌ Rejeitar", key=f"reject_{user['id']}"):
                    st.error("Função de rejeição será implementada!")
            
            st.divider()

def show_logout_button():
    """Botão de logout no sidebar"""
    with st.sidebar:
        st.divider()
        if st.button("🚪 Logout"):
            # Limpar sessão
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

def check_authentication():
    """
    Verifica se o usuário está logado
    Returns: True se logado, False caso contrário
    """
    return st.session_state.get("user_logged_in", False)

def get_current_user():
    """Retorna dados do usuário atual"""
    return st.session_state.get("user_data", {})

def is_admin():
    """Verifica se o usuário atual é admin"""
    user_data = get_current_user()
    return user_data.get("role") == "admin"