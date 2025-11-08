"""
Componentes para Gerenciamento de Prompts
CRUD completo com interface colaborativa
"""
import streamlit as st
from services.prompt_service import (
    get_all_prompts, create_prompt, get_user_prompts, 
    delete_prompt, update_prompt, LEGAL_AREAS, DECISION_TYPES
)
from components.auth_components import get_current_user, is_admin

def show_prompt_manager():
    """
    Interface principal para gerenciamento de prompts
    """
    st.title("🎯 Gerenciar Prompts")
    
    # Tabs principais
    tab_biblioteca, tab_meus_prompts, tab_criar_novo = st.tabs([
        "📚 Biblioteca Pública", 
        "👤 Meus Prompts", 
        "➕ Criar Novo"
    ])
    
    with tab_biblioteca:
        show_public_prompts_library()
    
    with tab_meus_prompts:
        show_user_prompts()
    
    with tab_criar_novo:
        show_create_prompt_form()

def show_public_prompts_library():
    """
    Biblioteca pública de prompts compartilhados
    """
    st.subheader("📚 Biblioteca Pública de Prompts")
    st.markdown("*Prompts criados pela comunidade e disponíveis para todos os usuários.*")
    
    # Filtros
    col_filter1, col_filter2, col_search = st.columns([1, 1, 2])
    
    with col_filter1:
        filter_area = st.selectbox(
            "Filtrar por área:",
            ["Todas"] + list(LEGAL_AREAS.keys()),
            key="filter_area_public"
        )
    
    with col_filter2:
        filter_type = st.selectbox(
            "Filtrar por tipo:",
            ["Todos"] + list(DECISION_TYPES.keys()),
            key="filter_type_public"
        )
    
    with col_search:
        search_query = st.text_input(
            "🔍 Buscar prompts:",
            placeholder="Digite o título ou descrição...",
            key="search_public"
        )
    
    # Carregar e filtrar prompts
    all_prompts = get_all_prompts()
    
    if filter_area != "Todas":
        all_prompts = [p for p in all_prompts if p['legal_area'] == filter_area]
    
    if filter_type != "Todos":
        all_prompts = [p for p in all_prompts if p['decision_type'] == filter_type]
    
    if search_query:
        all_prompts = [p for p in all_prompts if 
                      search_query.lower() in p['title'].lower() or 
                      search_query.lower() in p.get('description', '').lower()]
    
    st.divider()
    
    if not all_prompts:
        st.info("📂 Nenhum prompt encontrado com os filtros aplicados.")
        return
    
    # Mostrar prompts
    for prompt in all_prompts:
        with st.expander(f"📝 **{prompt['title']}** ({prompt['legal_area']} → {prompt['decision_type']})"):
            col_info, col_actions = st.columns([3, 1])
            
            with col_info:
                st.write(f"**Descrição:** {prompt.get('description', 'Sem descrição')}")
                st.write(f"**Criado em:** {prompt['created_at'][:10]}")
                
                # Preview da instrução
                instruction_preview = prompt['instruction'][:200] + "..." if len(prompt['instruction']) > 200 else prompt['instruction']
                st.write(f"**Instrução:** {instruction_preview}")
                
                if st.button(f"👁️ Ver Completo", key=f"view_full_{prompt['id']}"):
                    st.session_state.viewing_prompt = prompt['id']
                    st.rerun()
            
            with col_actions:
                # Botão copiar (para usar em geração)
                if st.button("📋 Copiar ID", key=f"copy_{prompt['id']}"):
                    st.info(f"ID: `{prompt['id']}`")
                
                # Apenas admin ou criador pode deletar
                user_data = get_current_user()
                can_delete = (is_admin() or prompt.get('created_by') == user_data.get('id'))
                
                if can_delete:
                    if st.button("🗑️ Deletar", key=f"delete_public_{prompt['id']}", type="secondary"):
                        success, message = delete_prompt(prompt['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
    
    # Modal para visualização completa
    if 'viewing_prompt' in st.session_state:
        show_prompt_detail_modal()

def show_user_prompts():
    """
    Prompts criados pelo usuário atual
    """
    st.subheader("👤 Meus Prompts")
    st.markdown("*Prompts que você criou. Você pode editar ou deletar seus próprios prompts.*")
    
    user_prompts = get_user_prompts()
    
    if not user_prompts:
        st.info("📝 Você ainda não criou nenhum prompt. Use a aba 'Criar Novo' para começar!")
        return
    
    for prompt in user_prompts:
        with st.expander(f"📝 **{prompt['title']}** ({prompt['legal_area']} → {prompt['decision_type']})"):
            col_info, col_actions = st.columns([2, 1])
            
            with col_info:
                st.write(f"**Descrição:** {prompt.get('description', 'Sem descrição')}")
                st.write(f"**Criado em:** {prompt['created_at'][:10]}")
                st.write(f"**Público:** {'✅ Sim' if prompt['is_public'] else '❌ Não'}")
                
                # Preview da instrução
                instruction_preview = prompt['instruction'][:150] + "..." if len(prompt['instruction']) > 150 else prompt['instruction']
                st.write(f"**Instrução:** {instruction_preview}")
            
            with col_actions:
                if st.button("✏️ Editar", key=f"edit_{prompt['id']}", use_container_width=True):
                    st.session_state.editing_prompt = prompt
                    st.rerun()
                
                if st.button("🗑️ Deletar", key=f"delete_{prompt['id']}", type="secondary", use_container_width=True):
                    success, message = delete_prompt(prompt['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    # Modal para edição
    if 'editing_prompt' in st.session_state:
        show_edit_prompt_modal()

def show_create_prompt_form():
    """
    Formulário para criar novo prompt
    """
    st.subheader("➕ Criar Novo Prompt")
    st.markdown("*Crie um prompt personalizado que ficará disponível para toda a comunidade.*")
    
    with st.form("create_prompt_form"):
        # Informações básicas
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "📝 Título do Prompt *",
                placeholder="Ex: Sentença de Procedência em Ação de Cobrança",
                help="Nome que aparecerá na lista de prompts"
            )
            
            legal_area = st.selectbox(
                "⚖️ Área Jurídica *",
                list(LEGAL_AREAS.keys()),
                help="Ramo do direito ao qual se aplica"
            )
        
        with col2:
            decision_type = st.selectbox(
                "📋 Tipo de Decisão *",
                list(DECISION_TYPES.keys()),
                help="Tipo de ato judicial"
            )
            
            description = st.text_input(
                "📄 Descrição",
                placeholder="Ex: Modelo para sentenças de procedência em ações de cobrança",
                help="Breve descrição do que o prompt faz"
            )
        
        # Instrução principal
        st.markdown("### ✏️ Instrução para a IA")
        instruction = st.text_area(
            "Instrução Principal *",
            placeholder="Ex: Elabore uma sentença julgando procedente o pedido de cobrança, considerando os fatos e provas apresentados. Use fundamentação baseada no inadimplemento contratual e liquidez do débito...",
            height=150,
            help="Instrução detalhada que será enviada à IA junto com o processo e contexto"
        )
        
        # Bloco paradigma (opcional)
        st.markdown("### 📋 Bloco de Decisão Paradigma (Opcional)")
        paradigm_block = st.text_area(
            "Modelo de Texto",
            placeholder="Ex: DISPOSITIVO: Julgo PROCEDENTE o pedido inicial para CONDENAR o réu ao pagamento de...",
            height=120,
            help="Texto modelo que serve de inspiração para a formatação da decisão"
        )
        
        # Botões de ação
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submit_button = st.form_submit_button(
                "✨ Criar Prompt",
                use_container_width=True,
                type="primary"
            )
        
        with col_cancel:
            if st.form_submit_button("🔄 Limpar Campos", use_container_width=True):
                st.rerun()
        
        # Processar criação
        if submit_button:
            if not title or not legal_area or not decision_type or not instruction:
                st.error("❌ Preencha todos os campos obrigatórios (*)!")
            else:
                success, message = create_prompt(
                    title=title,
                    legal_area=legal_area,
                    decision_type=decision_type,
                    description=description or "Sem descrição",
                    instruction=instruction,
                    paradigm_block=paradigm_block
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    # Limpar formulário
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

def show_prompt_detail_modal():
    """
    Modal para visualização detalhada do prompt
    """
    if 'viewing_prompt' not in st.session_state:
        return
    
    # Buscar prompt específico
    all_prompts = get_all_prompts()
    prompt = next((p for p in all_prompts if p['id'] == st.session_state.viewing_prompt), None)
    
    if not prompt:
        del st.session_state.viewing_prompt
        return
    
    # Modal usando container
    st.markdown("---")
    st.markdown(f"### 👁️ Visualizando: {prompt['title']}")
    
    col_content, col_close = st.columns([4, 1])
    
    with col_close:
        if st.button("❌ Fechar", key="close_detail"):
            del st.session_state.viewing_prompt
            st.rerun()
    
    with col_content:
        st.write(f"**Área:** {prompt['legal_area']}")
        st.write(f"**Tipo:** {prompt['decision_type']}")
        st.write(f"**Descrição:** {prompt.get('description', 'Sem descrição')}")
        
        st.markdown("**Instrução Completa:**")
        st.text_area("", value=prompt['instruction'], height=200, disabled=True, key="full_instruction")
        
        if prompt.get('paradigm_block'):
            st.markdown("**Bloco Paradigma:**")
            st.text_area("", value=prompt['paradigm_block'], height=150, disabled=True, key="full_paradigm")

def show_edit_prompt_modal():
    """
    Modal para edição de prompt
    """
    if 'editing_prompt' not in st.session_state:
        return
    
    prompt = st.session_state.editing_prompt
    
    st.markdown("---")
    st.markdown(f"### ✏️ Editando: {prompt['title']}")
    
    with st.form("edit_prompt_form"):
        col1, col2 = st.columns([4, 1])
        
        with col2:
            if st.form_submit_button("❌ Cancelar"):
                del st.session_state.editing_prompt
                st.rerun()
        
        with col1:
            # Campos editáveis
            new_title = st.text_input("Título:", value=prompt['title'])
            new_description = st.text_input("Descrição:", value=prompt.get('description', ''))
            new_instruction = st.text_area("Instrução:", value=prompt['instruction'], height=150)
            new_paradigm = st.text_area("Bloco Paradigma:", value=prompt.get('paradigm_block', ''), height=100)
            
            # Botão salvar
            save_button = st.form_submit_button("💾 Salvar Alterações", type="primary")
            
            if save_button:
                success, message = update_prompt(
                    prompt['id'], new_title, new_description, new_instruction, new_paradigm
                )
                
                if success:
                    st.success(message)
                    del st.session_state.editing_prompt
                    st.rerun()
                else:
                    st.error(message)