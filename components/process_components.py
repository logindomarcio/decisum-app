"""
Componentes para Gerenciamento de Processos
"""
import streamlit as st
from services.process_service import (
    extract_text_from_pdf, save_process_to_db, get_user_processes, 
    get_process_by_id, delete_process, search_processes
)

def show_process_upload():
    """Interface para upload de processos"""
    st.subheader("📄 Upload de Processo")
    
    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "Selecione o arquivo PDF do processo:",
        type="pdf",
        help="Faça upload do processo judicial em formato PDF"
    )
    
    if uploaded_file is not None:
        # Mostrar informações do arquivo
        st.info(f"📄 Arquivo: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔍 Processar PDF", type="primary"):
                with st.spinner("Extraindo texto do PDF..."):
                    # Extrair texto
                    text_content = extract_text_from_pdf(uploaded_file)
                    
                    if text_content:
                        # Mostrar preview do texto
                        st.success("✅ Texto extraído com sucesso!")
                        
                        with st.expander("👁️ Visualizar texto extraído (primeiras 500 palavras)"):
                            preview_text = " ".join(text_content.split()[:500])
                            st.text_area("", value=preview_text, height=300, disabled=True)
                        
                        # Salvar no banco
                        if save_process_to_db(uploaded_file.name, text_content):
                            st.success("💾 Processo salvo no banco de dados!")
                            st.balloons()
                            
                            # Limpar cache para atualizar lista
                            if 'processes_cache' in st.session_state:
                                del st.session_state.processes_cache
                        else:
                            st.error("❌ Erro ao salvar processo!")
                    else:
                        st.error("❌ Não foi possível extrair texto do PDF!")
        
        with col2:
            st.info("💡 **Dicas:**\n- PDFs devem estar em formato texto\n- Evite PDFs escaneados\n- Tamanho máximo: 200MB")

def show_process_list():
    """Lista dos processos do usuário"""
    st.subheader("📋 Meus Processos")
    
    # Busca
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Buscar processos:", placeholder="Digite o nome do arquivo...")
    with col2:
        st.write("")  # Espaçamento
        refresh_button = st.button("🔄 Atualizar")
    
    # Carregar processos
    if search_query:
        processes = search_processes(search_query)
    else:
        if refresh_button or 'processes_cache' not in st.session_state:
            st.session_state.processes_cache = get_user_processes()
        processes = st.session_state.processes_cache
    
    if not processes:
        st.info("📂 Nenhum processo encontrado. Faça upload do primeiro processo!")
        return
    
    # Lista de processos
    for process in processes:
        with st.expander(f"📄 {process['filename']} - {process['created_at'][:10]}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**ID:** {process['id'][:8]}...")
                st.write(f"**Criado em:** {process['created_at'][:19].replace('T', ' ')}")
                
                # Preview do conteúdo
                if len(process['txt_content']) > 200:
                    preview = process['txt_content'][:200] + "..."
                else:
                    preview = process['txt_content']
                st.write(f"**Preview:** {preview}")
            
            with col2:
                if st.button("👁️ Ver Completo", key=f"view_{process['id']}"):
                    st.session_state.selected_process = process['id']
                    st.rerun()
                
                if st.button("⚖️ Gerar Decisão", key=f"generate_{process['id']}"):
                    st.session_state.selected_process_for_decision = process['id']
                    st.session_state.page = "Gerar Decisões"
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Deletar", key=f"delete_{process['id']}", type="secondary"):
                    if delete_process(process['id']):
                        st.success("Processo deletado!")
                        if 'processes_cache' in st.session_state:
                            del st.session_state.processes_cache
                        st.rerun()

def show_process_viewer():
    """Visualizador completo de processo"""
    if 'selected_process' not in st.session_state:
        st.info("Selecione um processo para visualizar.")
        return
    
    process = get_process_by_id(st.session_state.selected_process)
    
    if not process:
        st.error("Processo não encontrado!")
        return
    
    st.subheader(f"📄 {process['filename']}")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**Criado em:** {process['created_at'][:19].replace('T', ' ')}")
        st.write(f"**Tamanho:** {len(process['txt_content'])} caracteres")
    
    with col2:
        if st.button("⬅️ Voltar"):
            if 'selected_process' in st.session_state:
                del st.session_state.selected_process
            st.rerun()
    
    st.divider()
    
    # Conteúdo completo
    st.text_area(
        "Conteúdo completo do processo:",
        value=process['txt_content'],
        height=400,
        disabled=True
    )