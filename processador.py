import pandas as pd
from lxml import etree
import re
import io
import zipfile


def processar_arquivos_em_memoria(xml_bytes_list, planilha_bytes, log_callback, tag_cpf):
    """
    Recebe lista de dicts {"nome": str, "conteudo": bytes} e um BytesIO da planilha.
    Retorna bytes do ZIP com XMLs organizados por setor.
    """
    # --- Leitura da planilha ---
    try:
        df = pd.read_excel(planilha_bytes, engine='openpyxl')

        colunas_necessarias = ['CPF', 'Nome', 'Setor']
        faltantes = [c for c in colunas_necessarias if c not in df.columns]
        if faltantes:
            log_callback('error', f"❌ Colunas faltantes na planilha: {', '.join(faltantes)}")
            return None

        df['CPF'] = df['CPF'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(11)
        log_callback('info', f"📄 Planilha carregada: {len(df)} registros.")

    except Exception as e:
        log_callback('error', f"❌ Erro ao ler a planilha: {str(e)}")
        return None

    if not xml_bytes_list:
        log_callback('warning', "⚠️ Nenhum arquivo XML enviado.")
        return None

    log_callback('info', f"📊 Processando {len(xml_bytes_list)} arquivo(s)...")

    zip_buffer = io.BytesIO()
    sucesso = 0

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in xml_bytes_list:
            nome_arquivo = item['nome']
            conteudo = item['conteudo']

            try:
                if not conteudo:
                    log_callback('warning', f"⚠️ Arquivo vazio: {nome_arquivo}")
                    continue

                parser = etree.XMLParser(recover=True, encoding='utf-8')
                root = etree.parse(io.BytesIO(conteudo), parser).getroot()

                elementos = root.xpath(f"//*[local-name()='{tag_cpf}']/text()")

                if not elementos:
                    log_callback('warning', f"⚠️ Tag <{tag_cpf}> ausente em: {nome_arquivo}")
                    continue

                cpf_xml = ''.join(c for c in elementos[0] if c.isdigit()).zfill(11)
                registro = df.loc[df['CPF'] == cpf_xml]

                if registro.empty:
                    log_callback('warning', f"⚠️ CPF {cpf_xml} não encontrado ({nome_arquivo})")
                    continue

                nome_func = sanitizar(str(registro['Nome'].iloc[0]))
                setor_func = sanitizar(str(registro['Setor'].iloc[0]))

                nome_base = nome_arquivo.rsplit('.', 1)[0]
                caminho_zip = f"{setor_func}/{nome_base}_{nome_func[:50]}.xml"
                zf.writestr(caminho_zip, conteudo)

                log_callback('success', f"✅ {nome_arquivo} → {setor_func}")
                sucesso += 1

            except Exception as e:
                log_callback('error', f"❌ Falha em {nome_arquivo}: {str(e)}")

    log_callback('info', f"📈 Concluído: {sucesso} arquivo(s) organizados.")

    if sucesso == 0:
        return None

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def sanitizar(texto):
    if pd.isna(texto) or str(texto).strip() == "":
        return "Nao_Identificado"
    texto = re.sub(r'[<>:"/\\|?*]', '', str(texto))
    texto = re.sub(r'\s+', '_', texto).strip('_')
    return texto[:100]
