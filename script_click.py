
import click
import subprocess
import os

@click.group()
def cli():
    """
    CLI para automação do processo de criação do executável, limpeza das pastas e execução do Streamlit.
    """
    pass

@click.command('build')
@click.option('--source', default='./', help='Diretório de origem dos arquivos')
@click.option('--destination', default='./dist', help='Diretório de destino do executável')
@click.option('--recursive-metadata', is_flag=True, help='Copiar metadados recursivamente')
def build_executable(source, destination, recursive_metadata):
    """
    Cria o executável usando o PyInstaller com a opção de copiar os metadados do streamlit.
    """
    # Adicionando o nome correto do arquivo .spec ao comando pyinstaller
    pyinstaller_command = [
        'pyinstaller',
        '--clean',
        '--copy-metadata', 'streamlit',
        '--recursive-copy-metadata' if recursive_metadata else '',
        'ProcessadorXML.spec'  # Certificando que o .spec seja passado corretamente
    ]
    
    # Limpar argumentos vazios
    pyinstaller_command = [arg for arg in pyinstaller_command if arg]
    
    try:
        print(f'Executando o comando: {" ".join(pyinstaller_command)}')
        subprocess.run(pyinstaller_command, check=True)
        print(f'Executável criado com sucesso em: {destination}')
    except subprocess.CalledProcessError as e:
        print(f'Erro ao executar o comando: {e}')

@click.command('clean')
def clean_build():
    """
    Limpa as pastas de build e dist.
    """
    subprocess.run(['rmdir', '/s', '/q', 'build', 'dist'], check=True)
    print("Pastas de build e dist limpas com sucesso!")

@click.command('start')
def start_app():
    """
    Inicia o aplicativo usando Streamlit.
    """
    subprocess.run(['streamlit', 'run', 'streamlit_app.py'], check=True)
    print("Aplicativo iniciado com sucesso!")

# Adiciona as funções ao grupo CLI
cli.add_command(build_executable)
cli.add_command(clean_build)
cli.add_command(start_app)

if __name__ == '__main__':
    cli()
