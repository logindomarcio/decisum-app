"""
Serviço de Integração com Gemini AI
Geração real de decisões judiciais
"""
import streamlit as st
import google.generativeai as genai
from config.supabase_config import get_supabase_client
from components.auth_components import get_current_user
from services.process_service import extract_text_from_pdf
import os
import re

def get_user_gemini_key():
    """
    Retorna a chave API Gemini do usuário
    """
    try:
        user_data = get_current_user()
        return user_data.get('gemini_api_key', '')
    except:
        return ''

def save_user_gemini_key(api_key: str) -> bool:
    """
    Salva a chave API Gemini do usuário no banco
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        result = supabase.table("users").update({
            "gemini_api_key": api_key
        }).eq("id", user_data["id"]).execute()
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar chave API: {e}")
        return False

def validate_gemini_key(api_key: str) -> bool:
    """
    Valida se a chave API Gemini está funcionando
    """
    try:
        temp_genai = genai 
        temp_genai.configure(api_key=api_key)
        temp_model = temp_genai.GenerativeModel('gemini-pro-latest')
        
        # Teste simples
        response = temp_model.generate_content("Teste")
        return True
    except Exception as e:
        st.error(f"Chave API inválida: {e}")
        return False

def generate_decision(pdf_file, prompt_data, instrucao_principal, depoimentos="", doutrina=""):
    """
    Gera uma decisão judicial usando Gemini AI
    """
    try:
        # Obter chave API do usuário
        api_key = get_user_gemini_key()
        if not api_key:
            return False, "Você precisa configurar sua chave API do Gemini nas Configurações!"
        
        # Configurar Gemini
        temp_genai = genai 
        temp_genai.configure(api_key=api_key)
        model = temp_genai.GenerativeModel('gemini-pro-latest')
        
        # Extrair texto do PDF
        with st.spinner("Extraindo texto do processo..."):
            processo_text = extract_text_from_pdf(pdf_file)
            if not processo_text:
                return False, "Erro ao extrair texto do PDF!"
        
        # Construir prompt completo
        prompt_completo = build_complete_prompt(
            prompt_data, instrucao_principal, processo_text, depoimentos, doutrina
        )
        
        # Gerar decisão
        with st.spinner("Gerando decisão judicial... Isso pode levar alguns momentos."):
            response = model.generate_content(prompt_completo)
            decisao_gerada = response.text
        
        return True, decisao_gerada
    
    except Exception as e:
        return False, f"Erro na geração: {str(e)}"

def build_complete_prompt(prompt_data, instrucao_principal, processo_text, depoimentos, doutrina):
    """
    Constrói o prompt completo para envio ao Gemini
    """
    
    prompt_completo = f"""
SISTEMA ESPECIALISTA EM DECISÕES JUDICIAIS

Você é um assistente especializado em elaboração de decisões judiciais brasileiras. 
Analise cuidadosamente o processo judicial e elabore uma decisão conforme as instruções.

=== MODELO DE DECISÃO SELECIONADO ===
Título: {prompt_data['title']}
Área: {prompt_data['legal_area']}
Tipo: {prompt_data['decision_type']}
Descrição: {prompt_data.get('description', 'Não informado')}

=== INSTRUÇÃO ESPECÍFICA ===
{prompt_data['instruction']}

=== DIRETRIZ PRINCIPAL PARA ESTA DECISÃO ===
{instrucao_principal}

=== CONTEÚDO DO PROCESSO JUDICIAL ===
{processo_text[:15000]}  # Limitando para não exceder tokens

"""

    # Adicionar depoimentos se fornecidos
    if depoimentos and depoimentos.strip():
        prompt_completo += f"""
=== DEPOIMENTOS E OITIVAS ===
{depoimentos[:5000]}

"""

    # Adicionar doutrina se fornecida
    if doutrina and doutrina.strip():
        prompt_completo += f"""
=== DOUTRINA E JURISPRUDÊNCIA ===
{doutrina[:3000]}

"""

    # Adicionar bloco paradigma se existir
    if prompt_data.get('paradigm_block'):
        prompt_completo += f"""
=== MODELO DE FORMATAÇÃO ===
Use este texto como inspiração para a estrutura da decisão:
{prompt_data['paradigm_block']}

"""

    # Instruções finais
    prompt_completo += """
=== INSTRUÇÕES PARA ELABORAÇÃO ===

1. ANALISE cuidadosamente todos os fatos e provas apresentados no processo
2. APLIQUE a legislação brasileira pertinente à área jurídica especificada
3. SIGA a instrução específica do modelo e a diretriz principal fornecida
4. UTILIZE os depoimentos e doutrina como fundamentos adicionais quando relevantes
5. ESTRUTURE a decisão de forma clara e profissional
6. USE formatação em markdown para destacar seções importantes
7. INCLUA fundamentação jurídica sólida e referências legais quando apropriado
8. MANTENHA linguagem técnica-jurídica adequada ao tipo de decisão

=== IMPORTANTE ===
- Responda APENAS com a decisão judicial elaborada
- NÃO inclua comentários ou explicações sobre o processo de elaboração
- USE formatação markdown para organizar o texto (## para títulos, **negrito**, etc.)
- A decisão deve estar completa e pronta para uso

ELABORE A DECISÃO AGORA:
"""
    
    return prompt_completo

def refine_decision(original_decision, refinement_instruction):
    """
    Refina uma decisão já gerada baseada em nova instrução
    """
    try:
        api_key = get_user_gemini_key()
        if not api_key:
            return False, "Chave API não configurada!"
        
        temp_genai = genai 
        temp_genai.configure(api_key=api_key)
        model = temp_genai.GenerativeModel('gemini-pro-latest')
        
        refinement_prompt = f"""
Você é um assistente especializado em aprimoramento de decisões judiciais.

=== DECISÃO ORIGINAL ===
{original_decision}

=== INSTRUÇÃO PARA REFINAMENTO ===
{refinement_instruction}

=== INSTRUÇÕES ===
1. Analise a decisão original e a instrução de refinamento
2. Faça APENAS as alterações solicitadas na instrução
3. Mantenha toda a estrutura e conteúdo não afetado pela instrução
4. Preserve a formatação markdown
5. Responda APENAS com a decisão refinada, sem comentários

DECISÃO REFINADA:
"""
        
        with st.spinner("Refinando decisão..."):
            response = model.generate_content(refinement_prompt)
            decisao_refinada = response.text
        
        return True, decisao_refinada
    
    except Exception as e:
        return False, f"Erro no refinamento: {str(e)}"

def save_generated_decision(pdf_filename, prompt_id, generated_text, additional_context="", doctrine=""):
    """
    Salva a decisão gerada no banco de dados
    """
    try:
        user_data = get_current_user()
        supabase = get_supabase_client()
        
        # Buscar o processo pelo nome do arquivo
        process_result = supabase.table("processes").select("id").eq("filename", pdf_filename).eq("user_id", user_data["id"]).execute()
        
        process_id = None
        if process_result.data:
            process_id = process_result.data[0]["id"]
        
        # Salvar decisão
        result = supabase.table("decisions").insert({
            "process_id": process_id,
            "prompt_id": prompt_id,
            "additional_context": additional_context,
            "doctrine_jurisprudence": doctrine,
            "generated_decision": generated_text,
            "user_id": user_data["id"]
        }).execute()
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar decisão: {e}")
        return False

def clean_markdown_for_download(text):
    """
    Limpa formatação markdown para download em .txt
    """
    # Remove marcações markdown básicas
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove **negrito**
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove *itálico*
    text = re.sub(r'#{1,6}\s*(.*)', r'\1', text)  # Remove headers
    text = re.sub(r'`(.*?)`', r'\1', text)        # Remove código inline
    
    return text.strip()