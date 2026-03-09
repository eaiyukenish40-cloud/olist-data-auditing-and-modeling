# %%

import pandas as pd
import os
import glob
from sqlalchemy import create_engine

#
db_connection = 'mysql+pymysql://root:@localhost:3306/olist_v2'
engine = create_engine(db_connection)

# %%
try:
    path = r'C:\Users\gusta\Documents\GitHub\Olist\olist-data-auditing-and-modeling\python\data_cleaning_results'
    arquivos_csv = glob.glob(f'{path}/*.csv')
except Exception as e:
    print(f'Erro ao acessar os arquivos CSV: {e}')
else:
    for arquivo in arquivos_csv:
        try:
            nome_tabela = os.path.basename(arquivo).replace('.csv', '')
            print(f'Processando arquivo: {nome_tabela}.csv')
            df = pd.read_csv(arquivo)
        except Exception as e:
            print(f'Erro ao processar o arquivo {arquivo}: {e}')
        else:
            df.to_sql(nome_tabela, con=engine, if_exists='replace', index=False,chunksize=500)
            print(f'Upload concluído com sucesso! Tabela {nome_tabela} criada no MySQL.')

# %%


# %%
