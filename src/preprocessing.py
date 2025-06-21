import pandas as pd

def filtrar_estabelecimentos(df):
    termos_alvo = [
        "RESTAURANTES E SIMILARES",
        "LANCHONETES, CASAS DE CHÁ, DE SUCOS E SIMILARES",
        "BARES E OUTROS ESTABELECIMENTOS ESPECIALIZADOS EM SERVIR BEBIDAS, SEM ENTRETENIMENTO",
        "BARES E OUTROS ESTABELECIMENTOS ESPECIALIZADOS EM SERVIR BEBIDAS, COM ENTRETENIMENTO",
        "SERVIÇOS AMBULANTES DE ALIMENTAÇÃO",
        "CANTINAS - SERVIÇOS DE ALIMENTAÇÃO PRIVATIVOS",
        "SERVIÇOS DE ALIMENTAÇÃO PARA EVENTOS E RECEPÇÕES - BUFÊ"
    ]
    df['DESCRICAO_CNAE_PRINCIPAL'] = df['DESCRICAO_CNAE_PRINCIPAL'].str.strip()
    return df[df['DESCRICAO_CNAE_PRINCIPAL'].str.upper().isin(termos_alvo)].copy()

def montar_endereco(row):
    logradouro = f"{row['DESC_LOGRADOURO']} {row['NOME_LOGRADOURO']}".strip()
    numero = str(row['NUMERO_IMOVEL']).strip()
    complemento = str(row['COMPLEMENTO']).strip() if pd.notnull(row['COMPLEMENTO']) else ""
    bairro = row['NOME_BAIRRO'].strip()

    endereco = f"{logradouro}, {numero}"
    if complemento:
        endereco += f", {complemento}"
    endereco += f", {bairro}, BELO HORIZONTE, MG, BRASIL"
    return endereco

def preparar_dados(df):
    df = df.copy()
    df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])
    df = df.drop_duplicates(subset=['LATITUDE', 'LONGITUDE'], keep='first')
    df['NOME_EXIBIDO'] = df['NOME_FANTASIA'].combine_first(df['NOME'])
    colunas_finais = ['NOME_EXIBIDO', 'ENDERECO', 'DATA_INICIO_ATIVIDADE', 'IND_POSSUI_ALVARA', 'LATITUDE', 'LONGITUDE']
    df = df[colunas_finais]
    return df.rename(columns={
        'NOME_EXIBIDO': 'NOME',
        'ENDERECO': 'ENDERECO',
        'DATA_INICIO_ATIVIDADE': 'DATA_INICIO',
        'IND_POSSUI_ALVARA': 'ALVARA',
        'LATITUDE': 'LAT',
        'LONGITUDE': 'LON'
    }).reset_index(drop=True)