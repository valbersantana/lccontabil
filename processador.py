import os
import sys
import shutil
import pandas as pd
from lxml import etree
import traceback
import re

def processar_arquivos_com_planilha(pasta_origem, pasta_destino, arquivo_planilha, log_callback, tag_cpf):
    """
    Lê arquivos XML, busca um CPF em uma tag específica, encontra os dados
    em uma planilha e organiza os arquivos em subpastas por setor.
    """
    try:
        # Lê a planilha garantindo o motor openpyxl
        df_funcionarios = pd.read_excel(arquivo_planilha, engine='openpyxl')
        
        colunas_necessarias = ['CPF', 'Nome', 'Setor']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df_funcionarios.columns]
        
        if colunas_faltantes:
            log_callback('error', f"❌ ERRO: Colunas faltantes na planilha: {', '.join(colunas_faltantes)}")
            return
        
        # Normalização rigorosa do CPF para evitar falhas de busca
        df_funcionarios['CPF'] = df_funcionarios['CPF'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(11)
        log_callback('info', f"📄 Planilha carregada com {len(df_funcionarios)} registros.")
        
    except Exception as e:
        log_callback('error', f"❌ ERRO CRÍTICO ao ler a planilha: {str(e)}")
        return

    # Validação de acesso às pastas
    if not os.path.exists(pasta_origem):
        log_callback('error', f"❌ ERRO: Pasta de origem não encontrada: {pasta_origem}")
        return

    # Listagem de XMLs
    try:
        arquivos = [f for f in os.listdir(pasta_origem) if f.lower().endswith('.xml')]
    except Exception as e:
        log_callback('error', f"❌ ERRO ao listar arquivos: {str(e)}")
        return

    if not arquivos:
        log_callback('warning', "⚠️ Nenhum arquivo .xml encontrado.")
        return

    log_callback('info', f"📊 Processando {len(arquivos)} arquivos...")
    arquivos_com_sucesso = 0

    for nome_arquivo in arquivos:
        caminho_original = os.path.join(pasta_origem, nome_arquivo)
        
        try:
            # Parse robusto ignorando namespaces do eSocial
            parser = etree.XMLParser(recover=True, encoding='utf-8')
            with open(caminho_original, 'rb') as f:
                tree = etree.parse(f, parser)
            root = tree.getroot()
            
            # Busca dinâmica da tag (cpfTrab ou cpfBenef)
            xpath_query = f"//*[local-name()='{tag_cpf}']/text()"
            elementos_cpf = root.xpath(xpath_query)

            if elementos_cpf:
                cpf_xml = ''.join(c for c in elementos_cpf[0] if c.isdigit()).zfill(11)
                info_func = df_funcionarios.loc[df_funcionarios['CPF'] == cpf_xml]

                if not info_func.empty:
                    nome_func = str(info_func['Nome'].iloc[0])
                    setor_func = str(info_func['Setor'].iloc[0])
                    
                    # Sanitização para evitar erros de sistema de arquivos
                    nome_limpo = sanitizar_nome_arquivo(nome_func)
                    setor_limpo = sanitizar_nome_arquivo(setor_func)
                    
                    # Criação da estrutura de pastas: Destino/Setor/
                    pasta_setor = os.path.join(pasta_destino, setor_limpo)
                    os.makedirs(pasta_setor, exist_ok=True)
                    
                    # Nome final do arquivo limitado para evitar caminhos muito longos
                    novo_nome = f"{os.path.splitext(nome_arquivo)[0]}_{nome_limpo[:50]}.xml"
                    caminho_final = os.path.join(pasta_setor, novo_nome)
                    
                    shutil.copy2(caminho_original, caminho_final)
                    log_callback('success', f"✅ Sucesso: {nome_arquivo} -> {setor_limpo}")
                    arquivos_com_sucesso += 1
                else:
                    log_callback('warning', f"⚠️ CPF {cpf_xml} não encontrado na planilha ({nome_arquivo}).")
            else:
                log_callback('warning', f"⚠️ Tag <{tag_cpf}> ausente no arquivo {nome_arquivo}.")
                
        except Exception as e:
            log_callback('error', f"❌ Falha no arquivo {nome_arquivo}: {str(e)}")

    log_callback('info', f"📈 Fim: {arquivos_com_sucesso} arquivos organizados.")


def sanitizar_nome_arquivo(texto):
    """Remove caracteres proibidos no Windows e limita o tamanho."""
    if pd.isna(texto) or str(texto).strip() == "":
        return "Nao_Identificado"
    
    # Remove acentos e caracteres especiais
    texto = re.sub(r'[<>:"/\\|?*]', '', str(texto))
    # Substitui espaços e múltiplos underscores por um único underscore
    texto = re.sub(r'\s+', '_', texto).strip('_')
    return texto[:100]