import os
import sys
import streamlit.web.cli as stcli

def resource_path(relative_path):
    """Retorna o caminho absoluto para o recurso, funciona para dev e PyInstaller"""
    try:
        # Caminho temporario do PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def main():
    # Localiza o script da interface
    app_path = resource_path("streamlit_app.py")

    # Verifica se o arquivo existe antes de tentar rodar
    if not os.path.exists(app_path):
        print(f"ERRO: Nao foi possivel encontrar {app_path}")
        input("Pressione ENTER para sair...")
        return

    # Configura os argumentos do Streamlit
    # --server.headless=false forca a tentativa de abrir o navegador
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.port=8501",
        "--server.headless=false",
        "--global.developmentMode=false",
        "--browser.gatherUsageStats=false"
    ]

    # Inicia o servidor Streamlit
    try:
        print("Iniciando Processador XML... Aguarde a abertura do navegador.")
        stcli.main()
    except Exception as e:
        print(f"Erro ao iniciar aplicacao: {e}")
        input("Pressione ENTER para sair...")

if __name__ == "__main__":
    main()
    