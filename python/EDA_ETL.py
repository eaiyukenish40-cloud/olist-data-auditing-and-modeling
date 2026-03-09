# %%

import pandas as pd
from unidecode import unidecode
import sys
import func_estatistica as fe
import class_elt as elt
import numpy
import matplotlib.pyplot as plt


"selecione seu caminho de pasta onde está localizado o modulo func_estatistica"
sys.path.append(r'C:\Users\gusta\OneDrive\Documentos\GitHub\Projeto Portifólio Olist - V2 Power BI\olist-data-auditing-and-modeling\python')

# %%
"tabela orders" #RangeIndex: 99441 order_id pk e customer_id fk
orders = pd.read_csv('../Olist/olist_orders_dataset.csv',sep=',')

"conversão de colunas de datas para formtado datetime"
colunas_datas = ['order_purchase_timestamp','order_approved_at','order_delivered_carrier_date','order_delivered_customer_date','order_estimated_delivery_date']

orders[colunas_datas] = orders[colunas_datas].apply(pd.to_datetime)

"diferença de tempo entre as etapas logísticas"
orders['dias_para_entrega'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days

orders['tempo_aprovacao_pedido'] = (orders['order_approved_at'] - orders['order_purchase_timestamp']).dt.days

orders['tempo_coleta_item'] = (orders['order_delivered_carrier_date'] - orders['order_purchase_timestamp']).dt.days

orders['antecedencia_entrega'] = (orders['order_estimated_delivery_date'] - orders['order_delivered_customer_date']).dt.days

orders['flg_atraso'] = numpy.where(orders['antecedencia_entrega'] < 0, 1, 0)


"verifica os erros de integridade. Onde o sistema consta como entregue, mas não há a data de entrega"

filtro_integridade_orders = (orders['order_delivered_customer_date'].isnull())*(orders['order_status'] == 'delivered')
orders[filtro_integridade_orders]
orders['flag_integridade'] = numpy.where(filtro_integridade_orders,1,0)


# %%

'tabela order_items' #RangeIndex: 112650 order_id  & order_item_id (PK - composta) 
# shipping_limit_date - tempo limite do vendedor entregar o item pra logística

order_items = pd.read_csv('../Olist/olist_order_items_dataset.csv',sep=',')

order_items['valor pago'] = order_items['price'] + order_items['freight_value']


filtro_frete_gratis = order_items['freight_value'] == 0
order_items['flag_frete_gratis'] = numpy.where(filtro_frete_gratis,1,0)


"flags outliers preco e frete" # removido da versão final não faz sentido do ponto de vista de negócio
outlier_preco_max = fe.estatisticas(order_items['price'])['outlier_max']
outlier_preco_min = fe.estatisticas(order_items['price'])['outlier_min']
outlier_frete_max = fe.estatisticas(order_items['freight_value'])['outlier_max']
outlier_frete_min = fe.estatisticas(order_items['freight_value'])['outlier_min']

order_items['flag_outlier_preco_max'] = numpy.where(order_items['price'] > outlier_preco_max, 1, 0)
order_items['flag_outlier_preco_min'] = numpy.where(order_items['price'] < outlier_preco_min, 1, 0)
order_items['flag_outlier_frete_max'] = numpy.where(order_items['freight_value'] > outlier_frete_max, 1, 0)
order_items['flag_outlier_frete_min'] = numpy.where(order_items['freight_value'] < outlier_frete_min, 1, 0)



"categorizacao ticket dos produtos"
rotulos_ticket = ['Ticket Baixo', 'Ticket Médio', 'Ticket Alto', 'Ticket Premium']
"classificacao com base nos quartis de preco"
order_items['categoria_preco'] = pd.qcut(order_items['price'], q=4,labels = rotulos_ticket)


'flag outliers proporcao preço e frete'
order_items['peso_frete_no_preco'] = order_items['freight_value'].div(order_items['price']).replace([numpy.inf, -numpy.inf], 0)

outlier_proporcao_max = fe.estatisticas(order_items['peso_frete_no_preco'])['outlier_max']


order_items['flag_outlier_proporcao_max'] = numpy.where(order_items['peso_frete_no_preco'] > outlier_proporcao_max,1,0)

order_items['flag_frete_abusivo'] = numpy.where(order_items['peso_frete_no_preco'] >= 0.50, 1, 0)

rotulos_frete = ['Barato','Normal','Caro','Abusivo']
order_items['categoria_frete'] = pd.qcut(order_items['peso_frete_no_preco'], q=4,labels = rotulos_frete)

# %%

"order_reviews " #rows: 99224
order_reviews = pd.read_csv('../Olist/olist_order_reviews_dataset.csv',sep=',')


datas_reviews = ['review_answer_timestamp','review_creation_date']
order_reviews[datas_reviews] = order_reviews[datas_reviews].apply(pd.to_datetime)
order_reviews['tempo_resposta'] = (order_reviews['review_answer_timestamp'] - order_reviews['review_creation_date']).dt.days


rotulos_atraso = ['rapido','normal','demorado','problemas']
order_reviews['classificacao_tempo_reposta'] =  pd.cut(order_reviews['tempo_resposta'],bins=[-1, 1, 3, 5, 9999] , labels=rotulos_atraso)


'revela a tendencia de comentários nulos por classificação de nota' # não enviei ao mysql
qtde_por_notas = order_reviews.groupby('review_score').agg({
    'review_id':'count',
    'review_comment_message':'count'}).reset_index()
qtde_por_notas['nulos_por_nota'] = qtde_por_notas['review_id'] - qtde_por_notas['review_comment_message']

qtde_por_notas['proporcao_comentarios_nulos_nota'] = qtde_por_notas['nulos_por_nota']/qtde_por_notas['review_comment_message']

# %%

#103886 order_id - 99440 (distintos) and payment_sequential são pk composta
payments = pd.read_csv('../Olist/olist_order_payments_dataset.csv',sep=',')


# %%
'orders com parcelamento 0. Inconsistencia.'
payments['payment_installments'].value_counts()
payments[(payments['payment_installments'] == 0)]



payments['flag_parcelamento'] = numpy.where(payments['payment_installments'] > 1,1,0)
payments['flag_inconsistencia_parcelamento'] = numpy.where(payments['payment_installments'] == 0,1,0)


'Análise dos dados orders repetidas. Onde foi possível concluir que são casos de pedidos com mais de um tipo de pagamento.'

contagem_id = payments.groupby('order_id').agg({'order_id':'count'})
contagem_id.columns = ['order_id_count']
contagem_id = contagem_id.reset_index()
lista_id_repetidos = contagem_id[(contagem_id['order_id_count'] > 1)]['order_id'].to_list()


'calcular o forecast de receita mensal considerando a data do pedido e o valor pago'

'junção com a tabela orders para obter as informações de datas'
forecast_mensal = payments.merge(right= orders[['order_id','customer_id','order_status','order_delivered_customer_date','order_purchase_timestamp','flag_integridade','flg_atraso']], how='left', on='order_id', suffixes=['_payments','_orders'])

colunas_analisadas = ['order_id','payment_type','payment_installments','parcelas','mes_offset','flag_parcelamento','flag_inconsistencia_parcelamento' ,'order_status','order_delivered_customer_date','order_purchase_timestamp','flag_integridade','flg_atraso']



'inicio do cálculo de forecast mensal'
forecast_mensal['parcelas'] = forecast_mensal['payment_value'].div(forecast_mensal['payment_installments']).replace([numpy.inf, -numpy.inf], 0) # tabela intermediaria não enviada ao mysql

forecast_mensal['mes_offset'] = forecast_mensal['payment_installments'].apply(lambda x: list(range(0,x)) if x >= 1 else [0])

forecast_mensal_explodida = forecast_mensal.explode('mes_offset')
forecast_mensal_explodida = forecast_mensal_explodida[colunas_analisadas]

forecast_mensal_explodida['data_prevista_pagamento'] = forecast_mensal_explodida.apply(lambda x: x['order_purchase_timestamp'] + pd.DateOffset(months=x['mes_offset']), axis=1)

#tabela a ser enviada ao mysql
forecast_mensal_explodida[(forecast_mensal_explodida['flag_integridade'] == 0)]

# %%

# ROWS: 99441 - customer_id (pk)/ 96096: customer_unique_id

"criacao das funções de leitura e limpeza de dados essa funções irão evoluir para uma classe de ETL para ser reaproveitada em outros projetos e facilitar o acesso aos atributos"

'''def leitura_dados_csv():
    path = input(r'Digite o caminho que será analisado: ').strip()
    tabela_analidada = input('Digite o arquivo csv que será analisado: ')
    coluna_analisada = input('Digite as colunas que deseja analisar: ')
    acesso = f'{path}\{tabela_analidada}.csv'
    return acesso,coluna_analisada
retorno = leitura_dados_csv()
leitura = {'caminho':retorno[0], 'coluna':retorno[1]}

def limpeza_dados(coluna_df: pd.Series):

    coluna_limpa = coluna_df.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
    coluna_limpa = coluna_limpa.str.split(r'[/,\-]',n=1).str[0]
    coluna_limpa = coluna_limpa.str.replace(r"'", ' ', regex=True)
    coluna_limpa = coluna_limpa.str.strip()
    coluna_limpa = numpy.where(coluna_limpa.str.contains('@',na=False), 'desconhecido', coluna_limpa)
    correcoes = (coluna_df != coluna_limpa).sum()
    return coluna_limpa, correcoes

customers = pd.read_csv(leitura['caminho'],sep=',')'''

# %%

path = r'C:\Users\gusta\Documents\GitHub\Olist\olist-data-auditing-and-modeling\Olist'
tabela = 'olist_customers_dataset'
coluna = input('Digite as colunas que deseja analisar: ').strip()

customers_2_inst = elt.ETL(path, tabela, coluna)
customers_2 = customers_2_inst.leitura_dados_csv()
coluna_limpa_customers = customers_2_inst.limpeza_dados(customers_2[coluna])
customers_2[coluna] = coluna_limpa_customers



"limpeza de acentos e padronização para caixa baixa da coluna analisada"
#  %%
'utilizando a biblioteca unidecode para remover acentos e caracteres especiais e função temporária lambda para aplicar a limpeza em cada valor da coluna'

'''coluna_limpa = customers[leitura['coluna']].apply(lambda x : unidecode(str(x)).lower() if pd.notnull(x) else x)
# ou
'uso do str para a limpeza vetorizada.'
coluna_limpa = customers[leitura['coluna']].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
coluna_limpa = coluna_limpa.str.split(r'[/,\-]',n=1).str[0]
coluna_limpa = coluna_limpa.str.replace(r"'", ' ', regex=True)
coluna_limpa = coluna_limpa.str.strip()
coluna_limpa = numpy.where(coluna_limpa.str.contains('@',na=False), 'desconhecido', coluna_limpa)

correcoes = (customers[leitura['coluna']] != coluna_limpa).sum()'''



# %%


vendedores_inst = elt.ETL(path, 'olist_sellers_dataset', 'seller_city')
vendedores = vendedores_inst.leitura_dados_csv()
coluna_limpa_vendedores = vendedores_inst.limpeza_dados(vendedores['seller_city'])
vendedores['seller_city'] = coluna_limpa_vendedores

# %%

produtos_inst = elt.ETL(path, 'olist_products_dataset', 'product_category_name')
produtos = produtos_inst.leitura_dados_csv()
coluna_limpa_produtos = produtos_inst.limpeza_dados(produtos['product_category_name'])
produtos['product_category_name'] = coluna_limpa_produtos

# %%

geolocation_inst = elt.ETL(path, 'olist_geolocation_dataset', 'geolocation_city')
geolocation =geolocation_inst.leitura_dados_csv()
coluna_limpa_geolocation = geolocation_inst.limpeza_dados(geolocation_inst.leitura_dados_csv()['geolocation_city'])

geolocation['geolocation_city'] = coluna_limpa_geolocation
# %%
'exportando tabelas limpas para csv'

orders.to_csv('data_cleaning_results/orders_limpa.csv', index=False)
order_items.to_csv('data_cleaning_results/order_items_limpa.csv', index=False)
order_reviews.to_csv('data_cleaning_results/order_reviews_limpa.csv', index=False)
payments.to_csv('data_cleaning_results/payments_limpa.csv', index=False)
forecast_mensal_explodida.to_csv('data_cleaning_results/forecast_mensal_explodida_limpa.csv', index=False)
customers_2.to_csv('data_cleaning_results/customers_2_limpa.csv', index=False)
vendedores.to_csv('data_cleaning_results/vendedores_limpa.csv', index=False)
produtos.to_csv('data_cleaning_results/produtos_limpa.csv', index=False)
geolocation.to_csv('data_cleaning_results/geolocation_limpa.csv', index=False)

# %%
