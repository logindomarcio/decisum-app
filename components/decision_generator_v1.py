"""
Componentes para Geração de Decisões - Versão 1
Interface baseada no Google AI Studio
"""
import streamlit as st

def show_decision_generator_v1():
    """
    Interface de geração de decisões - Versão 1 (Layout básico)
    """
    st.title("⚖️ Gerar Decisão Judicial")
    
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
        
        # Primeira linha de botões
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            direito_civil = st.button("Direito Civil", use_container_width=True)
        with col2:
            direito_familia = st.button("Direito de Família", use_container_width=True)
        with col3:
            # Botão destacado (laranja) para Direito Penal
            direito_penal = st.button("🔥 **Direito Penal**", use_container_width=True, type="primary")
        with col4:
            fazenda_publica = st.button("Fazenda Pública", use_container_width=True)
        
        # Segunda linha de botões
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            infancia_juventude = st.button("Justiça da Infância e da Juventude", use_container_width=True)
        with col6:
            contratos_bancarios = st.button("Contratos Bancários", use_container_width=True)
        with col7:
            competencia_delegada = st.button("Competência Delegada e Acidentes de Trabalho", use_container_width=True)
        with col8:
            outros = st.button("Outros", use_container_width=True)
        
        st.markdown("*Selecione o tipo de ato judicial:*")
        
        # Tipos de decisão
        col_despacho, col_decisao, col_sentenca = st.columns(3)
        with col_despacho:
            tipo_despacho = st.button("Despacho", use_container_width=True)
        with col_decisao:
            tipo_decisao = st.button("Decisão", use_container_width=True)  
        with col_sentenca:
            # Botão destacado para Sentença
            tipo_sentenca = st.button("🔥 **Sentença**", use_container_width=True, type="primary")
        
        # Preview do prompt selecionado
        st.markdown("*Selecione o prompt desejado:*")
        
        # Caixa com prompt selecionado (mockup)
        st.markdown("""
        <div style="border-left: 4px solid #ff6b35; padding-left: 15px; margin: 10px 0; background-color: #2b2b2b; padding: 15px; border-radius: 5px;">
        <strong style="color: #ff6b35;">Sentença Penal</strong><br>
        <span style="color: #cccccc;">Sentença Penal Condenatória - Padrão</span>
        </div>
        """, unsafe_allow_html=True)
        
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
        
        if st.button("➕ Adicionar Depoimento", key="add_depoimento"):
            st.info("Funcionalidade será implementada na próxima versão")
        
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
        gerar_button = st.button(
            "📝 Gerar Minuta de Decisão",
            use_container_width=True,
            type="primary"
        )
        
        if gerar_button:
            st.success("🚧 Funcionalidade de geração será implementada na próxima versão!")
    
    with col_output:
        # Área de saída - Minuta Gerada
        st.markdown("### 📋 Minuta Gerada")
        
        # Container com fundo branco para a minuta
        st.markdown("""
        <div style="background-color: white; padding: 20px; border-radius: 10px; min-height: 600px; color: black;">
        <p style="color: #666; text-align: center; margin-top: 200px;">
        ⏳ A minuta da sua decisão aparecerá aqui...
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