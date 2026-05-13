import requests
import zipfile
import pandas as pd
import argparse
import logging
import datetime
import os

TIPOS_PLANILHA = [
    'Aposentados_BACEN',
    'Aposentados_SIAPE',
    'Honorarios_Advocaticios',
    'Honorarios_Jetons',
    'Militares',
    'Pensionistas_BACEN',
    'Pensionistas_DEFESA',
    'Pensionistas_SIAPE',
    'Reserva_Reforma_Militares',
    'Servidores_BACEN',
    'Servidores_SIAPE'
]
MAX_RETRIES = 3

def formatar_moeda(valor):
    return f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def formatar_inteiro(valor):
    return f'{valor:,}'.replace(',', '.')

def get_arguments() -> tuple[str, str, str]:
    parser = argparse.ArgumentParser(
        prog="Coletador do Governo",
        description='Colete dados de remuneração de servidores públicos',
        epilog='Exemplo: python main.py -m 1 -a 2026 -t Servidores_SIAPE'
    )

    parser.add_argument('-m', "--mes", help='Mês', required=True, type=int, choices=range(1, 13))
    parser.add_argument('-a', "--ano", help='Ano', required=True, type=int)
    parser.add_argument(
        '-t',
        '--tipo',
        help='Tipo de planilha',
        required=True,
        choices=TIPOS_PLANILHA
    )

    args = parser.parse_args()

    mes = f'{int(args.mes):02d}'
    ano = str(args.ano)
    tipo = args.tipo

    return mes, ano, tipo

def setup_log(mes:str, ano:str, tipo:str) -> None:
    os.makedirs('./logs', exist_ok=True)

    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(asctime)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        handlers=[
            logging.FileHandler(
                f"logs/{mes}_{ano}_{tipo}_{now}.log",
                encoding='utf-8'
            ),
            logging.StreamHandler()
        ]
    )

def download_zip(url:str, filename:str) -> None:
    logging.info(f'Baixando arquivo da url {url}')

    for tentativa in range(MAX_RETRIES):
        try:
            with requests.get(url, stream=True, timeout=30) as response:
                response.raise_for_status()

                with open(filename, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                    
                    logging.info('Download concluído')
                    return

        except requests.HTTPError as error:
            logging.exception(f'Erro HTTP: {error}')
            raise

        except requests.ConnectionError as error:
            logging.warning(f'Erro de conexão na tentativa {tentativa + 1}')

        except requests.Timeout as error:
            logging.warning(f'Tempo limite excedido na tentativa {tentativa + 1}')

        except Exception as error:
            logging.exception(f'Erro inesperado: {error}')
            raise

    logging.exception('Falha após múltiplas tentativas')
    raise RuntimeError('Falha após múltiplas tentativas')

def extrai_zip(nome_zip:str, folder:str) -> None:
    logging.info('Extraindo arquivos ZIP')
    try:
        with zipfile.ZipFile(nome_zip, 'r') as zip_ref:
            zip_ref.extractall(folder)

    except zipfile.BadZipFile as error:
        logging.exception(f'Erro ao extrair arquivo ZIP: {error}')
        raise

    finally:
        if os.path.exists(nome_zip):
            os.remove(nome_zip)

def carregar_csv(csv_path:str) -> pd.DataFrame:
    logging.info('Carregando CSV')

    df = None
    try:
        df = pd.read_csv(
            csv_path,
            sep=';',
            encoding='latin1'
        )

    except Exception as error:
        logging.exception(f'Erro ao carregar CSV: {error}')
        raise

    logging.info(f'CSV carregado com {len(df)} registros')

    return df

def gerar_relatorio(df:pd.DataFrame) -> dict:
    logging.info(f'Gerando relatório')
    colunas_transformar_float = ['REMUNERAÇÃO APÓS DEDUÇÕES OBRIGATÓRIAS (R$)', 'TOTAL DE VERBAS INDENIZATÓRIAS (R$)(*)']
    for coluna in colunas_transformar_float:
        df[coluna] = (
            df[coluna]
            .fillna('0')
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )

    df['RENDIMENTOS_TOTAIS'] = (
        df['REMUNERAÇÃO APÓS DEDUÇÕES OBRIGATÓRIAS (R$)']
        + df['TOTAL DE VERBAS INDENIZATÓRIAS (R$)(*)']
    )

    total_servidores = df['CPF'].nunique()
    media_salarial = df['RENDIMENTOS_TOTAIS'].mean()

    top_10 = df.nlargest(10, 'RENDIMENTOS_TOTAIS')[['NOME', 'RENDIMENTOS_TOTAIS']].sort_values('RENDIMENTOS_TOTAIS', ascending=False).reset_index(drop=True)

    return {
        'total_servidores': total_servidores,
        'media_salarial': media_salarial,
        'top_10': top_10
    }

def salvar_relatorio(filename:str, resumo:dict, mes:str, ano:str, tipo:str) -> None:
    logging.info(f'Salvando relatório')

    os.makedirs('./output', exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as resultados_file:
        resultados_file.write(
'''==============================
RESUMO DE REMUNERAÇÕES
==============================\n
'''
)
        
        resultados_file.write(f'Período analisado: {mes}/{ano}\n')
        resultados_file.write(f'Tipo de planilha: {tipo}\n\n\n')

        resultados_file.write(f'Total de servidores: {formatar_inteiro(resumo['total_servidores'])}\n')
        resultados_file.write(f'Média salarial: R$ {formatar_moeda(resumo['media_salarial'])}\n')

        for i, row in resumo['top_10'].iterrows():
            nome = row['NOME']
            renda = row['RENDIMENTOS_TOTAIS']

            resultados_file.write(f'\n{i+1}. {nome} - R$ {formatar_moeda(renda)}')

    logging.info(f'Relatório salvo em {filename}')

def main() -> None:
    mes, ano, tipo = get_arguments()
    setup_log(mes, ano, tipo)

    # https://portaldatransparencia.gov.br/download-de-dados/servidores
    url = f'https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/servidores/{ano}{mes}_{tipo}.zip'
    nome_zip = f'servidores_{mes}_{ano}.zip'
    download_zip(url, nome_zip)

    folder ='data'
    extrai_zip(nome_zip, folder)

    csv_path = folder + (f'/{ano}{mes}_Remuneracao.csv')
    df = carregar_csv(csv_path)
    
    resumo = gerar_relatorio(df)
    
    output_txt = f'output/{mes}-{ano}_{tipo}.txt'
    salvar_relatorio(
        output_txt,
        resumo,
        mes,
        ano,
        tipo
    )

if __name__ == '__main__':
    main()