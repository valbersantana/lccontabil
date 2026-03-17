import pandas as pd
from lxml import etree
import traceback
import re
import io
import zipfile


def processar_arquivos_em_memoria(arquivos_xml, arquivo_planilha, log_callback, tag_cpf):
    """
    Lê arquivos XML em memória, busca o CPF, encontra os dados na planilha
    e retorna um arquivo ZIP em memória com os XMLs organizados por setor.
    """
    # --- Leitura da planilha ---
    try:
        df_funcionarios = pd.read_excel(arquivo_planilha, engine='openpyxl')

        colunas_necessarias = ['CPF', 'Nome', 'Setor']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df_funcionarios.columns]

        if colunas_faltantes:
            log_callback('error', f"❌ ERRO: Colunas faltantes na planilha: {', '.join(colunas_faltantes)}")
            return None

        df_funcionarios['CPF'] = (
            df_funcionarios['CPF']
            .astype(str)
            .str.replace(r'\D', '', regex=True)
            .str.zfill(11)
        )
        log_callback('info', f"📄 Planilha carregada com {len(df_funcionarios)} registros.")

    except Exception as e:
        log_callback('error', f"❌ ERRO CRÍTICO ao ler a planilha: {str(e)}")
        return None

    if not arquivos_xml:
        log_callback('warning', "⚠️ Nenhum arquivo XML enviado.")
        return None

    log_callback('info', f"📊 Processando {len(arquivos_xml)} arquivos...")

    # --- Criação do ZIP em memória ---
    zip_buffer = io.BytesIO()
    arquivos_com_sucesso = 0

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for arquivo in arquivos_xml:
            nome_arquivo = arquivo.name
            try:
                conteudo = arquivo.read()

                # Parse do XML
                parser = etree.XMLParser(recover=True, encoding='utf-8')
                tree = etree.parse(io.BytesIO(conteudo), parser)
                root = tree.getroot()

                # Busca dinâmica da tag CPF
                xpath_query = f"//*[local-name()='{tag_cpf}']/text()"
                elementos_cpf = root.xpath(xpath_query)

                if elementos_cpf:
                    cpf_xml = ''.join(c for c in elementos_cpf[0] if c.isdigit()).zfill(11)
                    info_func = df_funcionarios.loc[df_funcionarios['CPF'] == cpf_xml]

                    if not info_func.empty:
                        nome_func = str(info_func['Nome'].iloc[0])
                        setor_func = str(info_func['Setor'].iloc[0])

                        nome_limpo = sanitizar_nome_arquivo(nome_func)
                        setor_limpo = sanitizar_nome_arquivo(setor_func)

                        # Estrutura dentro do ZIP: Setor/arquivo_Nome.xml
                        novo_nome = f"{setor_limpo}/{nome_arquivo.rsplit('.', 1)[0]}_{nome_limpo[:50]}.xml"
                        zf.writestr(novo_nome, conteudo)

                        log_callback('success', f"✅ Sucesso: {nome_arquivo} -> {setor_limpo}")
                        arquivos_com_sucesso += 1
                    else:
                        log_callback('warning', f"⚠️ CPF {cpf_xml} não encontrado na planilha ({nome_arquivo}).")
                else:
                    log_callback('warning', f"⚠️ Tag <{tag_cpf}> ausente no arquivo {nome_arquivo}.")

            except Exception as e:
                log_callback('error', f"❌ Falha no arquivo {nome_arquivo}: {str(e)}")

    log_callback('info', f"📈 Fim: {arquivos_com_sucesso} arquivos organizados.")

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def sanitizar_nome_arquivo(texto):
    """Remove caracteres proibidos e limita o tamanho."""
    if pd.isna(texto) or str(texto).strip() == "":
        return "Nao_Identificado"
    texto = re.sub(r'[<>:"/\\|?*]', '', str(texto))
    texto = re.sub(r'\s+', '_', texto).strip('_')
    return texto[:100]
