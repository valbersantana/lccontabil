import streamlit as st
import io

# Teste de import
try:
    from processador import processar_arquivos_em_memoria
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    IMPORT_ERROR = str(e)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Processador de XMLs", page_icon="📁", layout="wide")

if not IMPORT_OK:
    st.error(f"❌ Erro ao importar processador.py: {IMPORT_ERROR}")
    st.stop()

st.title("📁 Processador e Organizador de Arquivos XML")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ 1. Selecione os Arquivos XML")
    arquivos_xml = st.file_uploader(
        "Carregue os arquivos XML para processar",
        type=['xml'],
        accept_multiple_files=True,
        key="uploader_xml"
    )
    # Salva conteúdo dos XMLs no session_state IMEDIATAMENTE após upload
    if arquivos_xml:
        st.session_state['xml_bytes'] = [
            {"nome": f.name, "conteudo": f.read()} for f in arquivos_xml
        ]
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
        type=['xls', 'xlsx'],
        key="uploader_planilha"
    )
    # Salva conteúdo da planilha no session_state IMEDIATAMENTE após upload
    if uploaded_planilha:
        st.session_state['planilha_bytes'] = uploaded_planilha.read()
        st.session_state['planilha_nome'] = uploaded_planilha.name
        st.success(f"✅ Planilha '{uploaded_planilha.name}' carregada.")

st.markdown("---")

xml_ok = 'xml_bytes' in st.session_state and len(st.session_state['xml_bytes']) > 0
planilha_ok = 'planilha_bytes' in st.session_state

if xml_ok and planilha_ok:
    st.subheader("🚀 4. Inicie o Processamento")

    if st.button("⚡ Processar Arquivos Agora!", key="processar_btn", type="primary"):
        st.session_state['log_sucesso'] = []
        st.session_state['log_falha'] = []
        st.session_state['arquivo_zip'] = None

        def acumular_log(status, message):
            if status == 'success':
                st.session_state.log_sucesso.append(message)
            else:
                st.session_state.log_falha.append(message)

        with st.spinner("Processando arquivos... Aguarde."):
            try:
                arquivo_zip = processar_arquivos_em_memoria(
                    st.session_state['xml_bytes'],
                    io.BytesIO(st.session_state['planilha_bytes']),
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
    nome_planilha = st.session_state.get('planilha_nome', 'XMLs_Organizados').rsplit('.', 1)[0].capitalize()
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
        for key in ['log_sucesso', 'log_falha', 'arquivo_zip', 'xml_bytes', 'planilha_bytes', 'planilha_nome']:
            st.session_state.pop(key, None)
        st.rerun()

st.markdown("""
<div style="text-align: center; color: grey; font-size: 12px; margin-top: 40px;">
    <hr>
    <p>Desenvolvido por <strong>Data Mining Solutions IT</strong> | Contato: valbersantana@gmail.com</p>
</div>
""", unsafe_allow_html=True)
