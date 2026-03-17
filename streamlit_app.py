import streamlit as st
import os
from processador import processar_arquivos_com_planilha
import tkinter as tk
from tkinter import filedialog

# --- CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA LINHA DO CÓDIGO) ---
st.set_page_config(page_title="Processador de XMLs", page_icon="app_icon.ico", layout="wide")

# --- Função Auxiliar para Seleção de Pasta ---
def selecionar_pasta(label, key):
    st.write(label)
    col1, col2 = st.columns([4, 1])
    
    if key not in st.session_state:
        st.session_state[key] = 'C:/' # Caminho inicial padrão

    caminho_selecionado = col1.text_input("Caminho", label_visibility="collapsed", key=f"text_{key}", value=st.session_state[key])
    
    if col2.button("🔍 Procurar...", key=f"browse_{key}", use_container_width=True):
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True) # Garante que a janela apareça na frente
            caminho = filedialog.askdirectory(initialdir=st.session_state[key])
            root.destroy()
            if caminho:
                st.session_state[key] = os.path.normpath(caminho)
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao abrir seletor de pastas: {e}")
            
    return st.session_state[key]

# --- Título e Descrição ---
st.title("📁 Processador e Organizador de Arquivos XML")
st.markdown("---")

# --- Interface Principal ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("⚙️ 1. Selecione as Pastas")
    pasta_origem_final = selecionar_pasta("Pasta com os XMLs Originais:", "pasta_origem")
    pasta_base_destino = selecionar_pasta("Pasta Base para Salvar os Arquivos:", "pasta_destino")
with col2:
    st.subheader("📄 2. Carregue a Planilha")
    uploaded_file = st.file_uploader("Selecione a planilha de funcionários (.xls ou .xlsx)", type=['xls', 'xlsx'])

# --- Lógica de Execução ---
if uploaded_file is not None and pasta_origem_final and pasta_base_destino:
    st.success(f"Tudo pronto!")
    st.markdown("---")
    st.subheader("🚀 3. Inicie o Processamento")
    
    if st.button("Processar Arquivos Agora!", key="processar_btn"):
        nome_pasta_origem = os.path.basename(os.path.normpath(pasta_origem_final))
        tag_cpf_a_usar = 'cpfBenef' if nome_pasta_origem == 'XML5002' else 'cpfTrab'
        
        identificador = os.path.splitext(uploaded_file.name)[0]
        pasta_destino_final = os.path.join(pasta_base_destino, identificador.capitalize())
        
        with st.spinner(f"Processando..."):
            st.session_state['log_sucesso'] = []
            st.session_state['log_falha'] = []

            def acumular_log(status, message):
                if status == 'success':
                    st.session_state.log_sucesso.append(message)
                else:
                    st.session_state.log_falha.append(message)
            
            try:
                processar_arquivos_com_planilha(
                    pasta_origem_final, pasta_destino_final, uploaded_file,
                    acumular_log, tag_cpf=tag_cpf_a_usar
                )
                st.success("🎉 Processo finalizado com sucesso!")
            except Exception as e:
                st.error(f"Ocorreu um erro fatal: {e}")

# --- Exibição do Log ---
if 'log_sucesso' in st.session_state and (st.session_state.log_sucesso or st.session_state.log_falha):
    st.subheader("📋 Log de Processamento")
    tab_sucesso, tab_falha = st.tabs(["✅ Sucesso", "⚠️ Falhas e Avisos"])

    with tab_sucesso:
        st.metric("Arquivos com Sucesso", len(st.session_state.log_sucesso))
        if st.session_state.log_sucesso:
            st.text_area("Detalhes Sucesso:", value="\n".join(st.session_state.log_sucesso), height=300)

    with tab_falha:
        st.metric("Avisos/Erros", len(st.session_state.log_falha))
        if st.session_state.log_falha:
            st.text_area("Detalhes Falhas:", value="\n".join(st.session_state.log_falha), height=300)

    # Botão para limpar logs
    if st.button("🧹 Limpar Logs", key="limpar_logs"):
        st.session_state['log_sucesso'] = []
        st.session_state['log_falha'] = []
        st.success("🔄 Logs limpos com sucesso!")
        
# --- Rodapé ---
footer_html = """
<div style="text-align: center; color: grey; font-size: 12px;">
    <hr>
    <p>Desenvolvido por <strong>Data Mining Solutions IT</strong> | Contato: valbersantana@gmail.com</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
