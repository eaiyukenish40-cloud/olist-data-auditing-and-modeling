import pandas as pd
import numpy
import unidecode

class ETL:
    def __init__(self, path: str, tabela: str, coluna: str):
        self.path = path
        self.tabela = tabela
        self.coluna = coluna
        self.correcoes = 0
        self.arquivo_csv = ''

    def leitura_dados_csv(self):
        acesso = f'{self.path}\{self.tabela}.csv'
        leitura_df = pd.read_csv(acesso, sep=',')
        self.arquivo_csv = acesso
        return leitura_df
    
    def limpeza_dados(self, coluna_df: pd.Series):
        if self.arquivo_csv != '':
            coluna_limpa = self.leitura_dados_csv()[self.coluna].apply(lambda x : unidecode(str(x)).lower() if pd.notnull(x) else x)
        
        #ignora acentos e caracteres especiais, padroniza para caixa baixa, remove espaços em branco e padroniza valores desconhecidos
        coluna_limpa = coluna_df.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
        #divide a string em partes usando os delimitadores '/' ',' '-' e mantém apenas a primeira parte
        coluna_limpa = coluna_limpa.str.split(r'[/,\-]',n=1).str[0]
        #substitui os caracteres de aspas simples por espaço em branco, remove espaços em branco extras 
        coluna_limpa = coluna_limpa.str.replace(r"'", ' ', regex=True)
        coluna_limpa = coluna_limpa.str.strip()
        # padroniza valores desconhecidos onde há presença de números ou caracteres de email
        coluna_limpa = numpy.where(coluna_limpa.str.contains('@',na=False), 'desconhecido', coluna_limpa)
        coluna_limpa = numpy.where(coluna_limpa.str.match(r'^\d+$', na=False),'desconhecido',coluna_limpa)
        self.correcoes = (coluna_df != coluna_limpa).sum()
        return coluna_limpa