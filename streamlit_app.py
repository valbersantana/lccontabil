import streamlit as st
import io
import time

# --- 1. CONFIGURAÇÃO DA PÁGINA (OBRIGATORIAMENTE O PRIMEIRO COMANDO) ---
# Movido para o topo absoluto para evitar o NameError/Redact Error
st.set_page_config(page_title="Processador de XMLs", page_icon="📁", layout="wide")

# --- 2. FUNÇÕES DE AUTENTICAÇÃO ---
def check_password():
    """Gerencia a proteção por senha via Streamlit Secrets."""
    
    def login_form():
        """Renderiza a interface de login centralizada."""
        _, col_central, _ = st.columns([1, 1, 1])
        
        with col_central:
            st.markdown("### 🔐 NexusPS - Acesso Restrito")
            with st.form("login_form"):
                user_input = st.text_input("Usuário")
                password_input = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar", type="primary", use_container_width=True)
                
                if submit:
                    # Animação de carregamento ao clicar em entrar
                    with st.spinner("Autenticando..."):
                        time.sleep(0.8) # Efeito visual de validação
                        
                        users = st.secrets.get("users", {})
                        if user_input in users and str(users[user_input]) == password_input:
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = user_input
                            st.toast(f"Bem-vindo, {user_input}!", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ Usuário ou senha incorretos")

    if not st.session_state.get("authenticated"):
        login_form()
        st.stop() # Bloqueia o restante do app
        return False
    return True

def logout():
    """Encerra a sessão e limpa cache."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- 3. EXECUÇÃO DA SEGURANÇA ---
check_password()

# --- 4. ÁREA LOGADA (SEU SISTEMA ORIGINAL) ---

# Importação do processador (lógica de negócio separada)
try:
    from processador import processar_arquivos_em_memoria
    IMPORT_OK = True
except ImportError as e:
    IMPORT_OK = False
    IMPORT_ERROR = str(e)

# Barra Lateral (Sidebar)
with st.sidebar:
    st.title("Controle")
    st.write(f"👤 Usuário: **{st.session_state.get('username')}**")
    if st.button("Sair do Sistema", use_container_width=True):
        logout()
    st.divider()
    st.caption("Data Mining Solutions IT")

# Interface Principal
if not IMPORT_OK:
    st.error(f"Erro ao carregar processador.py: {IMPORT_ERROR}")
    st.stop()

st.title("📁 Processador e Organizador de Arquivos XML")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ 1. Arquivos XML")
    arquivos_xml = st.file_uploader(
        "Carregue os XMLs", type=['xml'], accept_multiple_files=True, key="uploader_xml"
    )
    if arquivos_xml:
        st.session_state['xml_bytes'] = [{"nome": f.name, "conteudo": f.read()} for f in arquivos_xml]
        st.success(f"✅ {len(arquivos_xml)} arquivos prontos.")

    st.subheader("🏷️ 2. Tag do CPF")
    tag_cpf = st.selectbox("Tag XML:", options=["cpfTrab", "cpfBenef"])

with col2:
    st.subheader("📄 3. Planilha")
    uploaded_planilha = st.file_uploader("Selecione a planilha", type=['xls', 'xlsx'], key="uploader_planilha")
    if uploaded_planilha:
        st.session_state['planilha_bytes'] = uploaded_planilha.read()
        st.session_state['planilha_nome'] = uploaded_planilha.name
        st.success("✅ Planilha carregada.")

# Lógica de Processamento
xml_ok = 'xml_bytes' in st.session_state and len(st.session_state['xml_bytes']) > 0
planilha_ok = 'planilha_bytes' in st.session_state

if xml_ok and planilha_ok:
    st.markdown("---")
    if st.button("⚡ Processar Agora!", type="primary", use_container_width=True):
        st.session_state['log_sucesso'] = []
        st.session_state['log_falha'] = []
        
        # Animação de processamento
        with st.status("Processando dados...", expanded=True) as status:
            try:
                def log_callback(tipo, msg):
                    if tipo == 'success': st.session_state.log_sucesso.append(msg)
                    else: st.session_state.log_falha.append(msg)

                resultado = processar_arquivos_em_memoria(
                    st.session_state['xml_bytes'],
                    io.BytesIO(st.session_state['planilha_bytes']),
                    log_callback,
                    tag_cpf=tag_cpf
                )
                st.session_state['arquivo_zip'] = resultado
                
                if resultado:
                    status.update(label="✅ Processamento concluído!", state="complete", expanded=False)
                    st.toast("Arquivos organizados com sucesso!", icon="📦")
                else:
                    status.update(label="⚠️ Nenhum arquivo gerado.", state="error")
            except Exception as e:
                st.error(f"Erro: {e}")

# Download e Logs
if st.session_state.get('arquivo_zip'):
    st.download_button(
        label="📥 Baixar ZIP Organizado",
        data=st.session_state['arquivo_zip'],
        file_name="XMLs_Organizados.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True
    )

# Exibição de Logs
if 'log_sucesso' in st.session_state:
    with st.expander("Ver detalhes do processamento"):
        st.write(f"Sucessos: {len(st.session_state.log_sucesso)}")
        st.write(f"Falhas: {len(st.session_state.log_falha)}")

st.markdown(f"""
<div style="text-align: center; color: grey; font-size: 11px; margin-top: 50px;">
    <hr> Desenvolvido por Valber Santana | Data Mining Solutions IT
</div>
""", unsafe_allow_html=True)
