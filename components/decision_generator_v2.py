"""
Componentes para Geração de Decisões - Versão 3
Interface com integração Gemini AI completa
"""
import streamlit as st
from services.prompt_service import get_prompts_by_area_and_type, LEGAL_AREAS, DECISION_TYPES
from services.gemini_service import generate_decision, refine_decision, save_generated_decision, clean_markdown_for_download
import io

def show_decision_generator_v3():
    """
    Interface de geração de decisões - Versão 3 (Com Gemini AI)
    """
    st.title("⚖️ Gerar Decisão Judicial")
    
    # Inicializar estado da sessão
    if 'selected_legal_area' not in st.session_state:
        st.session_state.selected_legal_area = None
    if 'selected_decision_type' not in st.session_state:
        st.session_state.selected_decision_type = None
    if 'selected_prompt' not in st.session_state:
        st.session_state.selected_prompt = None
    if 'generated_decision' not in st.session_state:
        st.session_state.generated_decision = None
    if 'generation_data' not in st.session_state:
        st.session_state.generation_data = None
    
    # Layout em duas colunas principais
    col_input, col_output = st.columns([1, 1])
    
    with col_input:
        # Seção 1: Upload de Processo
        st.markdown("### 📄 1. Processo Judicial (.pdf)")
        st.markdown("*Faça o upload do processo judicial em formato PDF. O sistema converterá o arquivo para texto automaticamente.*")
        
        uploaded_file = st.file_uploader(
            "Selecionar Arquivo PDF",
            type="pdf",
            key="decision_pdf_upload"
        )
        
        if uploaded_file:
            st.success(f"✅ **{uploaded_file.name}** ({uploaded_file.size/1024:.1f} KB)")
        
        st.divider()
        
        # Seção 2: Modelo de Decisão (Prompts)
        st.markdown("### 🎯 2. Modelo de Decisão (Prompt)")
        st.markdown("*Selecione o ramo do direito:*")
        
        # Primeira linha de botões - Áreas Jurídicas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Direito Civil", use_container_width=True, 
                        type="primary" if st.session_state.selected_legal_area == "Direito Civil" else "secondary"):
                st.session_state.selected_legal_area = "Direito Civil"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col2:
            if st.button("Direito de Família", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Direito de Família" else "secondary"):
                st.session_state.selected_legal_area = "Direito de Família"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col3:
            if st.button("🔥 Direito Penal", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Direito Penal" else "secondary"):
                st.session_state.selected_legal_area = "Direito Penal"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col4:
            if st.button("Fazenda Pública", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Fazenda Pública" else "secondary"):
                st.session_state.selected_legal_area = "Fazenda Pública"
                st.session_state.selected_prompt = None
                st.rerun()
        
        # Segunda linha de botões
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            if st.button("Justiça Infância", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Justiça da Infância e da Juventude" else "secondary"):
                st.session_state.selected_legal_area = "Justiça da Infância e da Juventude"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col6:
            if st.button("Contratos Bancários", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Contratos Bancários" else "secondary"):
                st.session_state.selected_legal_area = "Contratos Bancários"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col7:
            if st.button("Competência Delegada", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Competência Delegada e Acidentes de Trabalho" else "secondary"):
                st.session_state.selected_legal_area = "Competência Delegada e Acidentes de Trabalho"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col8:
            if st.button("Outros", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Outros" else "secondary"):
                st.session_state.selected_legal_area = "Outros"
                st.session_state.selected_prompt = None
                st.rerun()
        
        # Mostrar área selecionada
        if st.session_state.selected_legal_area:
            st.info(f"📂 **Área selecionada:** {st.session_state.selected_legal_area}")
        
        st.markdown("*Selecione o tipo de ato judicial:*")
        
        # Tipos de decisão
        col_despacho, col_decisao, col_sentenca = st.columns(3)
        with col_despacho:
            if st.button("Despacho", use_container_width=True,
                        type="primary" if st.session_state.selected_decision_type == "Despacho" else "secondary"):
                st.session_state.selected_decision_type = "Despacho"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col_decisao:
            if st.button("Decisão", use_container_width=True,
                        type="primary" if st.session_state.selected_decision_type == "Decisão" else "secondary"):
                st.session_state.selected_decision_type = "Decisão"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col_sentenca:
            if st.button("🔥 Sentença", use_container_width=True,
                        type="primary" if st.session_state.selected_decision_type == "Sentença" else "secondary"):
                st.session_state.selected_decision_type = "Sentença"
                st.session_state.selected_prompt = None
                st.rerun()
        
        # Mostrar prompts disponíveis
        if st.session_state.selected_legal_area and st.session_state.selected_decision_type:
            st.markdown("*Selecione o prompt desejado:*")
            
            prompts = get_prompts_by_area_and_type(
                st.session_state.selected_legal_area, 
                st.session_state.selected_decision_type
            )
            
            if prompts:
                for prompt in prompts:
                    is_selected = st.session_state.selected_prompt and st.session_state.selected_prompt['id'] == prompt['id']
                    
                    # Container clicável
                    with st.container():
                        if st.button(
                            f"📝 {prompt['title']}",
                            key=f"prompt_{prompt['id']}",
                            use_container_width=True,
                            type="primary" if is_selected else "secondary"
                        ):
                            st.session_state.selected_prompt = prompt
                            st.rerun()
                        
                        if is_selected:
                            st.markdown(f"**Descrição:** {prompt['description']}")
                            with st.expander("👁️ Ver instrução completa"):
                                st.text_area("Instrução:", value=prompt['instruction'], height=100, disabled=True)
                                if prompt.get('paradigm_block'):
                                    st.text_area("Bloco paradigma:", value=prompt['paradigm_block'], height=100, disabled=True)
            else:
                st.warning(f"Nenhum prompt encontrado para **{st.session_state.selected_legal_area}** → **{st.session_state.selected_decision_type}**")
                st.info("💡 Você pode criar novos prompts na seção 'Gerenciar Prompts'!")
        
        st.divider()
        
        # Seção 3: Instrução Principal
        st.markdown("### ✏️ 3. Instrução Principal")
        st.markdown("*Descreva o resultado esperado da decisão. A IA utilizará esta instrução como a diretriz principal, aplicando o modelo selecionado e os contextos abaixo.*")
        
        instrucao_principal = st.text_area(
            "",
            placeholder="Ex: 'Julgue o pedido procedente para condenar o réu ao pagamento de R$ 5.000,00 a título de danos morais, utilizando o fundamento da falha na prestação do serviço...'",
            height=120,
            key="instrucao_principal"
        )
        
        st.divider()
        
        # Seção 4: Depoimentos
        st.markdown("### 👥 4. Depoimentos (Opcional)")
        st.markdown("*Adicione o conteúdo de depoimentos e oitivas, seja colando o texto ou fazendo upload do termo em .pdf ou .txt.*")
        
        # Tabs para organizar as opções
        tab_texto, tab_upload = st.tabs(["✏️ Colar Texto", "📁 Upload Arquivos"])
        
        with tab_texto:
            depoimentos_text = st.text_area(
                "Digite ou cole os depoimentos:",
                placeholder="Ex: 'Testemunha João Silva: Confirmo que presenciei o acidente...'",
                height=100,
                key="depoimentos_text"
            )
        
        with tab_upload:
            uploaded_depoimentos = st.file_uploader(
                "Selecione arquivos de depoimentos:",
                type=["txt", "pdf"],
                accept_multiple_files=True,
                key="depoimentos_upload",
                help="Você pode selecionar múltiplos arquivos .txt ou .pdf"
            )
            
            if uploaded_depoimentos:
                st.success(f"✅ {len(uploaded_depoimentos)} arquivo(s) selecionado(s):")
                for file in uploaded_depoimentos:
                    st.write(f"📄 {file.name} ({file.size/1024:.1f} KB)")
                
                # Botão para processar arquivos
                if st.button("🔄 Processar Depoimentos", key="process_depoimentos"):
                    depoimentos_processados = []
                    
                    for file in uploaded_depoimentos:
                        try:
                            if file.type == "text/plain":
                                # Arquivo .txt
                                content = file.read().decode("utf-8")
                                depoimentos_processados.append(f"**{file.name}:**\n{content}")
                            elif file.type == "application/pdf":
                                # Arquivo .pdf (vamos usar a função que já temos)
                                from services.process_service import extract_text_from_pdf
                                content = extract_text_from_pdf(file)
                                if content:
                                    depoimentos_processados.append(f"**{file.name}:**\n{content}")
                        except Exception as e:
                            st.error(f"Erro ao processar {file.name}: {e}")
                    
                    if depoimentos_processados:
                        # Salvar no session_state para uso posterior
                        st.session_state.depoimentos_processados = "\n\n".join(depoimentos_processados)
                        st.success("✅ Depoimentos processados com sucesso!")
                        
                        with st.expander("👁️ Visualizar depoimentos processados"):
                            st.text_area(
                                "Conteúdo extraído:",
                                value=st.session_state.depoimentos_processados,
                                height=200,
                                disabled=True
                            )
        
        st.divider()
        
        # Seção 5: Doutrina e Jurisprudência  
        st.markdown("### 📚 5. Doutrina e Jurisprudência (Opcional)")
        st.markdown("*Cole aqui outros fundamentos que devam ser considerados na decisão.*")
        
        doutrina_jurisprudencia = st.text_area(
            "",
            placeholder="Ex: 'Conforme entendimento do STJ no REsp 1.234.567...'",
            height=120,
            key="doutrina_jurisprudencia"
        )
        
        st.divider()
        
        # Botão principal de geração
        can_generate = (
            uploaded_file is not None and 
            st.session_state.selected_prompt is not None and
            instrucao_principal.strip() != ""
        )
        
        # Reunir todos os dados para geração
        if can_generate:
            # Combinar depoimentos de texto e upload
            all_depoimentos = []
            if depoimentos_text and depoimentos_text.strip():
                all_depoimentos.append(depoimentos_text)
            if 'depoimentos_processados' in st.session_state:
                all_depoimentos.append(st.session_state.depoimentos_processados)
            
            combined_depoimentos = "\n\n".join(all_depoimentos) if all_depoimentos else ""
            
            gerar_button = st.button(
                "🚀 Gerar Minuta de Decisão",
                use_container_width=True,
                type="primary"
            )
            
            if gerar_button:
                # Gerar decisão real com Gemini
                success, result = generate_decision(
                    pdf_file=uploaded_file,
                    prompt_data=st.session_state.selected_prompt,
                    instrucao_principal=instrucao_principal,
                    depoimentos=combined_depoimentos,
                    doutrina=doutrina_jurisprudencia
                )
                
                if success:
                    st.session_state.generated_decision = result
                    st.session_state.generation_data = {
                        "pdf_file": uploaded_file,
                        "prompt": st.session_state.selected_prompt,
                        "instrucao": instrucao_principal,
                        "depoimentos": combined_depoimentos,
                        "doutrina": doutrina_jurisprudencia
                    }
                    
                    # Salvar no banco de dados
                    save_generated_decision(
                        uploaded_file.name,
                        st.session_state.selected_prompt['id'],
                        result,
                        instrucao_principal,
                        doutrina_jurisprudencia
                    )
                    
                    st.success("✅ Decisão gerada com sucesso!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {result}")
        else:
            st.button(
                "🚀 Gerar Minuta de Decisão",
                use_container_width=True,
                disabled=True,
                help="Necessário: PDF + Prompt + Instrução Principal"
            )
            
            # Mostrar o que está faltando
            missing = []
            if not uploaded_file:
                missing.append("📄 Upload do PDF")
            if not st.session_state.selected_prompt:
                missing.append("🎯 Seleção do prompt")  
            if not instrucao_principal.strip():
                missing.append("✏️ Instrução principal")
            
            if missing:
                st.warning(f"**Faltando:** {' • '.join(missing)}")
    
    with col_output:
        show_output_area()

def show_output_area():
    """
    Área de saída com minuta gerada
    """
    st.markdown("### 📋 Minuta Gerada")
    
    if st.session_state.generated_decision:
        # Container com fundo branco para a minuta
        st.markdown("""
        <div style="background-color: white; padding: 20px; border-radius: 10px; color: black; border: 1px solid #ddd;">
        """, unsafe_allow_html=True)
        
        # Mostrar decisão formatada
        st.markdown(st.session_state.generated_decision)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Botões de ação
        st.divider()
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("✏️ Editar Texto", use_container_width=True):
                st.session_state.editing_decision = True
                st.rerun()
        
        with col_btn2:
            if st.button("📋 Copiar", use_container_width=True):
                st.code(st.session_state.generated_decision, language=None)
                st.success("Texto exibido acima - use Ctrl+A e Ctrl+C para copiar!")
        
        with col_btn3:
            # Download como arquivo
            clean_text = clean_markdown_for_download(st.session_state.generated_decision)
            st.download_button(
                "💾 Download .txt",
                data=clean_text,
                file_name="decisao_judicial.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        st.divider()
        
        # Seção Refinar Minuta
        st.markdown("### 🔄 Refinar Minuta")
        st.markdown("*Dê uma instrução para a IA ajustar a minuta gerada. Você pode pedir para deixar um parágrafo mais conciso, alterar o tom ou adicionar uma fundamentação.*")
        
        refinar_instrucao = st.text_area(
            "",
            placeholder="Ex: 'Torne o terceiro parágrafo mais conciso e direto.'",
            height=80,
            key="refinar_instrucao"
        )
        
        if st.button("🔄 Refinar Texto", use_container_width=True):
            if refinar_instrucao.strip():
                success, refined_decision = refine_decision(
                    st.session_state.generated_decision, 
                    refinar_instrucao
                )
                
                if success:
                    st.session_state.generated_decision = refined_decision
                    st.success("✅ Decisão refinada!")
                    st.rerun()
                else:
                    st.error(f"❌ {refined_decision}")
            else:
                st.warning("Digite uma instrução para refinamento!")
        
        # Botão Nova Minuta
        st.divider()
        if st.button("🆕 Nova Minuta", use_container_width=True, type="secondary"):
            # Limpar todos os dados
            keys_to_clear = ['generated_decision', 'generation_data', 'selected_legal_area', 
                           'selected_decision_type', 'selected_prompt', 'depoimentos_processados']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
    else:
        # Container com fundo branco para aguardar geração
        st.markdown("""
        <div style="background-color: white; padding: 20px; border-radius: 10px; min-height: 600px; color: black; border: 1px solid #ddd;">
        <p style="color: #666; text-align: center; margin-top: 200px;">
        ⏳ A minuta da sua decisão aparecerá aqui...<br><br>
        <small>Configure sua chave API Gemini nas Configurações e siga os passos ao lado</small>
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botões desabilitados
        st.divider()
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            st.button("✏️ Editar", disabled=True, use_container_width=True)
        with col_btn2:
            st.button("📋 Copiar", disabled=True, use_container_width=True)
        with col_btn3:
            st.button("💾 Download", disabled=True, use_container_width=True)
        
        st.divider()
        st.markdown("### 🔄 Refinar Minuta")
        st.text_area("", disabled=True, placeholder="Aguardando geração da decisão...")
        st.button("🔄 Refinar Texto", disabled=True, use_container_width=True)
    
    # Modal de edição
    if st.session_state.get('editing_decision'):
        show_edit_decision_modal()

def show_edit_decision_modal():
    """
    Modal para edição direta da decisão
    """
    st.markdown("---")
    st.markdown("### ✏️ Editando Decisão")
    
    with st.form("edit_decision_form"):
        edited_text = st.text_area(
            "Edite o texto da decisão:",
            value=st.session_state.generated_decision,
            height=400
        )
        
        col_save, col_cancel = st.columns([1, 1])
        
        with col_save:
            save_button = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
        
        with col_cancel:
            cancel_button = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if save_button:
            st.session_state.generated_decision = edited_text
            st.session_state.editing_decision = False
            st.success("Decisão atualizada!")
            st.rerun()
        
        if cancel_button:
            st.session_state.editing_decision = False
            st.rerun()
    """
    Interface de geração de decisões - Versão 2 (Prompts funcionais)
    """
    st.title("⚖️ Gerar Decisão Judicial")
    
    # Inicializar estado da sessão
    if 'selected_legal_area' not in st.session_state:
        st.session_state.selected_legal_area = None
    if 'selected_decision_type' not in st.session_state:
        st.session_state.selected_decision_type = None
    if 'selected_prompt' not in st.session_state:
        st.session_state.selected_prompt = None
    
    # Layout em duas colunas principais
    col_input, col_output = st.columns([1, 1])
    
    with col_input:
        # Seção 1: Upload de Processo
        st.markdown("### 📄 1. Processo Judicial (.pdf)")
        st.markdown("*Faça o upload do processo judicial em formato PDF. O sistema converterá o arquivo para texto automaticamente.*")
        
        uploaded_file = st.file_uploader(
            "Selecionar Arquivo PDF",
            type="pdf",
            key="decision_pdf_upload"
        )
        
        if uploaded_file:
            st.success(f"✅ **{uploaded_file.name}** ({uploaded_file.size/1024:.1f} KB)")
        
        st.divider()
        
        # Seção 2: Modelo de Decisão (Prompts)
        st.markdown("### 🎯 2. Modelo de Decisão (Prompt)")
        st.markdown("*Selecione o ramo do direito:*")
        
        # Primeira linha de botões - Áreas Jurídicas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Direito Civil", use_container_width=True, 
                        type="primary" if st.session_state.selected_legal_area == "Direito Civil" else "secondary"):
                st.session_state.selected_legal_area = "Direito Civil"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col2:
            if st.button("Direito de Família", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Direito de Família" else "secondary"):
                st.session_state.selected_legal_area = "Direito de Família"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col3:
            if st.button("🔥 Direito Penal", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Direito Penal" else "secondary"):
                st.session_state.selected_legal_area = "Direito Penal"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col4:
            if st.button("Fazenda Pública", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Fazenda Pública" else "secondary"):
                st.session_state.selected_legal_area = "Fazenda Pública"
                st.session_state.selected_prompt = None
                st.rerun()
        
        # Segunda linha de botões
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            if st.button("Justiça Infância", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Justiça da Infância e da Juventude" else "secondary"):
                st.session_state.selected_legal_area = "Justiça da Infância e da Juventude"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col6:
            if st.button("Contratos Bancários", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Contratos Bancários" else "secondary"):
                st.session_state.selected_legal_area = "Contratos Bancários"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col7:
            if st.button("Competência Delegada", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Competência Delegada e Acidentes de Trabalho" else "secondary"):
                st.session_state.selected_legal_area = "Competência Delegada e Acidentes de Trabalho"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col8:
            if st.button("Outros", use_container_width=True,
                        type="primary" if st.session_state.selected_legal_area == "Outros" else "secondary"):
                st.session_state.selected_legal_area = "Outros"
                st.session_state.selected_prompt = None
                st.rerun()
        
        # Mostrar área selecionada
        if st.session_state.selected_legal_area:
            st.info(f"📂 **Área selecionada:** {st.session_state.selected_legal_area}")
        
        st.markdown("*Selecione o tipo de ato judicial:*")
        
        # Tipos de decisão
        col_despacho, col_decisao, col_sentenca = st.columns(3)
        with col_despacho:
            if st.button("Despacho", use_container_width=True,
                        type="primary" if st.session_state.selected_decision_type == "Despacho" else "secondary"):
                st.session_state.selected_decision_type = "Despacho"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col_decisao:
            if st.button("Decisão", use_container_width=True,
                        type="primary" if st.session_state.selected_decision_type == "Decisão" else "secondary"):
                st.session_state.selected_decision_type = "Decisão"
                st.session_state.selected_prompt = None
                st.rerun()
        
        with col_sentenca:
            if st.button("🔥 Sentença", use_container_width=True,
                        type="primary" if st.session_state.selected_decision_type == "Sentença" else "secondary"):
                st.session_state.selected_decision_type = "Sentença"
                st.session_state.selected_prompt = None
                st.rerun()
        
        # Mostrar prompts disponíveis
        if st.session_state.selected_legal_area and st.session_state.selected_decision_type:
            st.markdown("*Selecione o prompt desejado:*")
            
            prompts = get_prompts_by_area_and_type(
                st.session_state.selected_legal_area, 
                st.session_state.selected_decision_type
            )
            
            if prompts:
                for prompt in prompts:
                    is_selected = st.session_state.selected_prompt and st.session_state.selected_prompt['id'] == prompt['id']
                    
                    # Container clicável
                    with st.container():
                        if st.button(
                            f"📝 {prompt['title']}",
                            key=f"prompt_{prompt['id']}",
                            use_container_width=True,
                            type="primary" if is_selected else "secondary"
                        ):
                            st.session_state.selected_prompt = prompt
                            st.rerun()
                        
                        if is_selected:
                            st.markdown(f"**Descrição:** {prompt['description']}")
                            with st.expander("👁️ Ver instrução completa"):
                                st.text_area("Instrução:", value=prompt['instruction'], height=100, disabled=True)
                                if prompt.get('paradigm_block'):
                                    st.text_area("Bloco paradigma:", value=prompt['paradigm_block'], height=100, disabled=True)
            else:
                st.warning(f"Nenhum prompt encontrado para **{st.session_state.selected_legal_area}** → **{st.session_state.selected_decision_type}**")
                st.info("💡 Você pode criar novos prompts na seção 'Gerenciar Prompts'!")
        
        st.divider()
        
        # Seção 3: Instrução Principal
        st.markdown("### ✏️ 3. Instrução Principal")
        st.markdown("*Descreva o resultado esperado da decisão. A IA utilizará esta instrução como a diretriz principal, aplicando o modelo selecionado e os contextos abaixo.*")
        
        instrucao_principal = st.text_area(
            "",
            placeholder="Ex: 'Julgue o pedido procedente para condenar o réu ao pagamento de R$ 5.000,00 a título de danos morais, utilizando o fundamento da falha na prestação do serviço...'",
            height=120,
            key="instrucao_principal"
        )
        
        st.divider()
        
        # Seção 4: Depoimentos
        st.markdown("### 👥 4. Depoimentos (Opcional)")
        st.markdown("*Adicione o conteúdo de depoimentos e oitivas, seja colando o texto ou fazendo upload do termo em .pdf ou .txt.*")
        
        # Tabs para organizar as opções
        tab_texto, tab_upload = st.tabs(["✏️ Colar Texto", "📁 Upload Arquivos"])
        
        with tab_texto:
            depoimentos_text = st.text_area(
                "Digite ou cole os depoimentos:",
                placeholder="Ex: 'Testemunha João Silva: Confirmo que presenciei o acidente...'",
                height=100,
                key="depoimentos_text"
            )
        
        with tab_upload:
            uploaded_depoimentos = st.file_uploader(
                "Selecione arquivos de depoimentos:",
                type=["txt", "pdf"],
                accept_multiple_files=True,
                key="depoimentos_upload",
                help="Você pode selecionar múltiplos arquivos .txt ou .pdf"
            )
            
            if uploaded_depoimentos:
                st.success(f"✅ {len(uploaded_depoimentos)} arquivo(s) selecionado(s):")
                for file in uploaded_depoimentos:
                    st.write(f"📄 {file.name} ({file.size/1024:.1f} KB)")
                
                # Botão para processar arquivos
                if st.button("🔄 Processar Depoimentos", key="process_depoimentos"):
                    depoimentos_processados = []
                    
                    for file in uploaded_depoimentos:
                        try:
                            if file.type == "text/plain":
                                # Arquivo .txt
                                content = file.read().decode("utf-8")
                                depoimentos_processados.append(f"**{file.name}:**\n{content}")
                            elif file.type == "application/pdf":
                                # Arquivo .pdf (vamos usar a função que já temos)
                                from services.process_service import extract_text_from_pdf
                                content = extract_text_from_pdf(file)
                                if content:
                                    depoimentos_processados.append(f"**{file.name}:**\n{content}")
                        except Exception as e:
                            st.error(f"Erro ao processar {file.name}: {e}")
                    
                    if depoimentos_processados:
                        # Salvar no session_state para uso posterior
                        st.session_state.depoimentos_processados = "\n\n".join(depoimentos_processados)
                        st.success("✅ Depoimentos processados com sucesso!")
                        
                        with st.expander("👁️ Visualizar depoimentos processados"):
                            st.text_area(
                                "Conteúdo extraído:",
                                value=st.session_state.depoimentos_processados,
                                height=200,
                                disabled=True
                            )
        
        st.divider()
        
        # Seção 5: Doutrina e Jurisprudência  
        st.markdown("### 📚 5. Doutrina e Jurisprudência (Opcional)")
        st.markdown("*Cole aqui outros fundamentos que devam ser considerados na decisão.*")
        
        doutrina_jurisprudencia = st.text_area(
            "",
            placeholder="Ex: 'Conforme entendimento do STJ no REsp 1.234.567...'",
            height=120,
            key="doutrina_jurisprudencia"
        )
        
        st.divider()
        
        # Botão principal de geração
        can_generate = (
            uploaded_file is not None and 
            st.session_state.selected_prompt is not None and
            instrucao_principal.strip() != ""
        )
        
        # Reunir todos os dados para geração
        if can_generate:
            # Combinar depoimentos de texto e upload
            all_depoimentos = []
            if depoimentos_text and depoimentos_text.strip():
                all_depoimentos.append(depoimentos_text)
            if 'depoimentos_processados' in st.session_state:
                all_depoimentos.append(st.session_state.depoimentos_processados)
            
            combined_depoimentos = "\n\n".join(all_depoimentos) if all_depoimentos else ""
            
            gerar_button = st.button(
                "📝 Gerar Minuta de Decisão",
                use_container_width=True,
                type="primary"
            )
            
            if gerar_button:
                # Preparar dados para envio à IA (Versão 3)
                generation_data = {
                    "pdf_file": uploaded_file,
                    "prompt": st.session_state.selected_prompt,
                    "instrucao_principal": instrucao_principal,
                    "depoimentos": combined_depoimentos,
                    "doutrina_jurisprudencia": doutrina_jurisprudencia
                }
                
                st.success("🚧 Geração será implementada na Versão 3 - Integração Gemini!")
                st.info("Todos os dados estão capturados e prontos para serem enviados à IA!")
                
                # Preview dos dados capturados
                with st.expander("👁️ Dados capturados para geração"):
                    st.write("**PDF:**", uploaded_file.name)
                    st.write("**Prompt:**", st.session_state.selected_prompt['title'])
                    st.write("**Instrução:**", instrucao_principal[:100] + "...")
                    if combined_depoimentos:
                        st.write("**Depoimentos:**", f"{len(combined_depoimentos)} caracteres")
                    if doutrina_jurisprudencia:
                        st.write("**Doutrina:**", f"{len(doutrina_jurisprudencia)} caracteres")
        else:
            st.button(
                "📝 Gerar Minuta de Decisão",
                use_container_width=True,
                disabled=True,
                help="Necessário: PDF + Prompt + Instrução Principal"
            )
            
            # Mostrar o que está faltando
            missing = []
            if not uploaded_file:
                missing.append("📄 Upload do PDF")
            if not st.session_state.selected_prompt:
                missing.append("🎯 Seleção do prompt")  
            if not instrucao_principal.strip():
                missing.append("✏️ Instrução principal")
            
            if missing:
                st.warning(f"**Faltando:** {' • '.join(missing)}")
    
    with col_output:
        # Área de saída - Minuta Gerada
        st.markdown("### 📋 Minuta Gerada")
        
        # Container com fundo branco para a minuta
        st.markdown("""
        <div style="background-color: white; padding: 20px; border-radius: 10px; min-height: 600px; color: black;">
        <p style="color: #666; text-align: center; margin-top: 200px;">
        ⏳ A minuta da sua decisão aparecerá aqui...<br><br>
        <small>Versão 3 implementará a geração com Gemini AI</small>
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botões de ação (desabilitados por enquanto)
        st.divider()
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            st.button("✏️ Editar", disabled=True, use_container_width=True)
        with col_btn2:
            st.button("📋 Copiar", disabled=True, use_container_width=True)
        with col_btn3:
            st.button("💾 Download", disabled=True, use_container_width=True)
        
        st.divider()
        
        # Seção Refinar Minuta
        st.markdown("### 🔄 Refinar Minuta")
        st.markdown("*Dê uma instrução para a IA ajustar a minuta gerada. Você pode pedir para deixar um parágrafo mais conciso, alterar o tom ou adicionar uma fundamentação.*")
        
        refinar_instrucao = st.text_area(
            "",
            placeholder="Ex: 'Torne o terceiro parágrafo mais conciso e direto.'",
            height=80,
            disabled=True,
            key="refinar_instrucao"
        )
        
        st.button("🔄 Refinar Texto", disabled=True, use_container_width=True)