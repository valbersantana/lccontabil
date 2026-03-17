import streamlit as st
import io

# Teste de import com mensagem clara de erro
try:
    from processador import processar_arquivos_em_memoria
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    IMPORT_ERROR = str(e)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Processador de XMLs", page_icon="📁", layout="wide")

# --- Verificação de Import ---
if not IMPORT_OK:
    st.error(f"❌ Erro ao importar processador.py: {IMPORT_ERROR}")
    st.info("Verifique se o arquivo processador.py no GitHub contém a função 'processar_arquivos_em_memoria'")
    st.stop()

# --- Título e Descrição ---
st.title("📁 Processador e Organizador de Arquivos XML")
st.markdown("---")

# --- Interface Principal ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ 1. Selecione os Arquivos XML")
    arquivos_xml = st.file_uploader(
        "Carregue os arquivos XML para processar",
        type=['xml'],
        accept_multiple_files=True
    )
    if arquivos_xml:
        st.success(f"✅ {len(arquivos_xml)} arquivo(s) XML carregado(s).")

    st.subheader("🏷️ 2. Tag do CPF no XML")
    tag_cpf = st.selectbox(
        "Selecione a tag que contém o CPF nos arquivos XML:",
        options=["cpfTrab", "cpfBenef"],
        help="Use 'cpfBenef' para arquivos XML5002, e 'cpfTrab' para os demais."
    )

with col2:
    st.subheader("📄 3. Carregue a Planilha")
    uploaded_planilha = st.file_uploader(
        "Selecione a planilha de funcionários (.xls ou .xlsx)",
        type=['xls', 'xlsx']
    )
    if uploaded_planilha:
        st.success(f"✅ Planilha '{uploaded_planilha.name}' carregada.")

# --- Lógica de Execução ---
st.markdown("---")
tudo_pronto = arquivos_xml and uploaded_planilha

if tudo_pronto:
    st.subheader("🚀 4. Inicie o Processamento")

    if st.button("⚡ Processar Arquivos Agora!", key="processar_btn", type="primary"):
        st.session_state['log_sucesso'] = []
        st.session_state['log_falha'] = []
        st.session_state['arquivo_zip'] = None

        st.write(f"🔍 Debug: {len(arquivos_xml)} XML(s) recebido(s) | Planilha: {uploaded_planilha.name}")

        def acumular_log(status, message):
            if status == 'success':
                st.session_state.log_sucesso.append(message)
            else:
                st.session_state.log_falha.append(message)

        with st.spinner("Processando arquivos... Aguarde."):
            try:
                arquivo_zip = processar_arquivos_em_memoria(
                    arquivos_xml,
                    uploaded_planilha,
                    acumular_log,
                    tag_cpf=tag_cpf
                )
                st.session_state['arquivo_zip'] = arquivo_zip
                if arquivo_zip:
                    st.success("🎉 Processo finalizado com sucesso!")
                else:
                    st.warning("⚠️ Nenhum arquivo gerado. Verifique os logs de falha.")
            except Exception as e:
                import traceback
                st.error(f"Erro fatal: {e}")
                st.code(traceback.format_exc())
else:
    st.info("⬆️ Carregue os arquivos XML e a planilha para habilitar o processamento.")

# --- Botão de Download ---
if st.session_state.get('arquivo_zip'):
    nome_planilha = uploaded_planilha.name.rsplit('.', 1)[0].capitalize() if uploaded_planilha else "XMLs_Organizados"
    st.download_button(
        label="📥 Baixar XMLs Organizados (.zip)",
        data=st.session_state['arquivo_zip'],
        file_name=f"{nome_planilha}_organizado.zip",
        mime="application/zip",
        type="primary"
    )

# --- Exibição do Log ---
if 'log_sucesso' in st.session_state and (st.session_state.get('log_sucesso') or st.session_state.get('log_falha')):
    st.markdown("---")
    st.subheader("📋 Log de Processamento")
    tab_sucesso, tab_falha = st.tabs(["✅ Sucesso", "⚠️ Falhas e Avisos"])

    with tab_sucesso:
        st.metric("Arquivos com Sucesso", len(st.session_state.log_sucesso))
        if st.session_state.log_sucesso:
            st.text_area("Detalhes:", value="\n".join(st.session_state.log_sucesso), height=300)

    with tab_falha:
        st.metric("Avisos/Erros", len(st.session_state.log_falha))
        if st.session_state.log_falha:
            st.text_area("Detalhes:", value="\n".join(st.session_state.log_falha), height=300)

    if st.button("🧹 Limpar Logs"):
        st.session_state['log_sucesso'] = []
        st.session_state['log_falha'] = []
        st.session_state['arquivo_zip'] = None
        st.rerun()

# --- Rodapé ---
st.markdown("""
<div style="text-align: center; color: grey; font-size: 12px; margin-top: 40px;">
    <hr>
    <p>Desenvolvido por <strong>Data Mining Solutions IT</strong> | Contato: valbersantana@gmail.com</p>
</div>
""", unsafe_allow_html=True)
