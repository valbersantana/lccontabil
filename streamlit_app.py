import streamlit as st
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando Streamlit) ---
st.set_page_config(page_title="Processador de XMLs", page_icon="📁", layout="wide") [cite: 5]

# --- 2. FUNÇÕES DE AUTENTICAÇÃO E SESSÃO ---
def check_password():
    """Gerencia a tela de login e validação de usuários via Secrets."""
    
    def login_form():
        """Renderiza a interface de login."""
        # Centralizando o formulário na tela
        _, col_central, _ = st.columns([1, 1, 1])
        
        with col_central:
            st.markdown("### 🔐 Acesso Restrito")
            with st.form("login_form"):
                user_input = st.text_input("Usuário")
                password_input = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar", type="primary", use_container_width=True)
                
                if submit:
                    # Busca a lista de usuários configurada nos Secrets do Streamlit Cloud
                    users = st.secrets.get("users", {})
                    if user_input in users and str(users[user_input]) == password_input:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user_input
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos")

    if not st.session_state.get("authenticated"):
        login_form()
        st.stop() # Impede a execução do restante do código se não estiver logado
        return False
    return True

def logout():
    """Limpa todos os dados da sessão e desloga o usuário."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- 3. VERIFICAÇÃO DE ACESSO ---
check_password()

# --- 4. ÁREA LOGADA - SISTEMA ORIGINAL ---

# Teste de importação do processador
try:
    from processador import processar_arquivos_em_memoria
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    IMPORT_ERROR = str(e) [cite: 5]

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.image("https://via.placeholder.com/150?text=NexusPS", width=100) # Opcional: Seu Logo
    st.title("Painel de Controle")
    st.write(f"👤 Usuário: **{st.session_state.get('username')}**")
    
    if st.button("Sair / Logout", use_container_width=True):
        logout()
    
    st.divider()
    st.info("Versão v2.1")
    st.caption("NexusPS - Data Mining Solutions IT")

# --- CONTEÚDO PRINCIPAL ---
if not IMPORT_OK:
    st.error(f"❌ Erro crítico ao carregar o motor de processamento: {IMPORT_ERROR}")
    st.stop()

st.title("📁 Processador e Organizador de Arquivos XML")
st.markdown("---")

col1, col2 = st.columns(2) [cite: 5]

with col1:
    st.subheader("⚙️ 1. Selecione os Arquivos XML")
    arquivos_xml = st.file_uploader(
        "Carregue os arquivos XML para processar",
        type=['xml'],
        accept_multiple_files=True,
        key="uploader_xml"
    ) [cite: 5]
    
    if arquivos_xml:
        st.session_state['xml_bytes'] = [
            {"nome": f.name, "conteudo": f.read()} for f in arquivos_xml
        ] [cite: 5]
        st.success(f"✅ {len(arquivos_xml)} arquivo(s) XML carregado(s).") [cite: 5]

    st.subheader("🏷️ 2. Tag do CPF no XML")
    tag_cpf = st.selectbox(
        "Selecione a tag que contém o CPF nos arquivos XML:",
        options=["cpfTrab", "cpfBenef"],
        help="Use 'cpfBenef' para arquivos XML5002, e 'cpfTrab' para os demais."
    ) [cite: 5]

with col2:
    st.subheader("📄 3. Carregue a Planilha")
    uploaded_planilha = st.file_uploader(
        "Selecione a planilha de funcionários (.xls ou .xlsx)",
        type=['xls', 'xlsx'],
        key="uploader_planilha"
    ) [cite: 5]
    
    if uploaded_planilha:
        st.session_state['planilha_bytes'] = uploaded_planilha.read() [cite: 5]
        st.session_state['planilha_nome'] = uploaded_planilha.name [cite: 5]
        st.success(f"✅ Planilha '{uploaded_planilha.name}' carregada.") [cite: 5]

st.markdown("---")

# Verificação para habilitar botão de processamento
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

        with st.spinner("Processando e organizando arquivos..."):
            try:
                arquivo_zip = processar_arquivos_em_memoria(
                    st.session_state['xml_bytes'],
                    io.BytesIO(st.session_state['planilha_bytes']),
                    acumular_log,
                    tag_cpf=tag_cpf
                ) [cite: 5]
                st.session_state['arquivo_zip'] = arquivo_zip
                if arquivo_zip:
                    st.success("🎉 Processo finalizado com sucesso!")
                else:
                    st.warning("⚠️ Nenhum arquivo gerado. Verifique os logs.")
            except Exception as e:
                import traceback
                st.error(f"Erro fatal: {e}")
                st.code(traceback.format_exc())
else:
    st.info("⬆️ Carregue os arquivos XML e a planilha para habilitar o processamento.")

# --- DOWNLOAD DO RESULTADO ---
if st.session_state.get('arquivo_zip'):
    nome_download = st.session_state.get('planilha_nome', 'XMLs').rsplit('.', 1)[0]
    st.download_button(
        label="📥 Baixar XMLs Organizados (.zip)",
        data=st.session_state['arquivo_zip'],
        file_name=f"{nome_download}_organizado.zip",
        mime="application/zip",
        type="primary"
    ) [cite: 5]

# --- LOGS DE PROCESSAMENTO ---
if 'log_sucesso' in st.session_state and (st.session_state.get('log_sucesso') or st.session_state.get('log_falha')):
    st.markdown("---")
    st.subheader("📋 Log de Atividades")
    tab_sucesso, tab_falha = st.tabs(["✅ Sucesso", "⚠️ Falhas/Avisos"])

    with tab_sucesso:
        st.metric("Sucessos", len(st.session_state.log_sucesso))
        if st.session_state.log_sucesso:
            st.text_area("Lista de Processados:", value="\n".join(st.session_state.log_sucesso), height=250)

    with tab_falha:
        st.metric("Alertas", len(st.session_state.log_falha))
        if st.session_state.log_falha:
            st.text_area("Lista de Erros:", value="\n".join(st.session_state.log_falha), height=250)

    if st.button("🧹 Limpar Processamento Atual"):
        for key in ['log_sucesso', 'log_falha', 'arquivo_zip', 'xml_bytes', 'planilha_bytes']:
            st.session_state.pop(key, None)
        st.rerun()

# --- RODAPÉ ---
st.markdown(f"""
<div style="text-align: center; color: grey; font-size: 12px; margin-top: 50px; padding: 20px; border-top: 1px solid #eee;">
    <p><strong>Data Mining Solutions IT</strong></p>
    <p>Suporte: valbersantana@gmail.com</p>
    <p>Acesso atual por: {st.session_state.get('username')}</p>
</div>
""", unsafe_allow_html=True) [cite: 5]
