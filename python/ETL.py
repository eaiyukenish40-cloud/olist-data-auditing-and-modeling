# %%

import pandas as pd
from unidecode import unidecode
import sys
import func_estatistica as fe
import numpy

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

# %%
filtro_frete_gratis = order_items['freight_value'] == 0
order_items['flag_frete_gratis'] = numpy.where(filtro_frete_gratis,1,0)

# %%
"flags outliers preco e frete" # removido da versão final não faz sentido do ponto de vista de negócio
outlier_preco_max = fe.estatisticas(order_items['price'])['outlier_max']
outlier_preco_min = fe.estatisticas(order_items['price'])['outlier_min']
outlier_frete_max = fe.estatisticas(order_items['freight_value'])['outlier_max']
outlier_frete_min = fe.estatisticas(order_items['freight_value'])['outlier_min']

order_items['flag_outlier_preco_max'] = numpy.where(order_items['price'] > outlier_preco_max, 1, 0)
order_items['flag_outlier_preco_min'] = numpy.where(order_items['price'] < outlier_preco_min, 1, 0)
order_items['flag_outlier_frete_max'] = numpy.where(order_items['freight_value'] > outlier_frete_max, 1, 0)
order_items['flag_outlier_frete_min'] = numpy.where(order_items['freight_value'] < outlier_frete_min, 1, 0)

# %%

"categorizacao ticket dos produtos"
rotulos_ticket = ['Ticket Baixo', 'Ticket Médio', 'Ticket Alto', 'Ticket Premium']
"classificacao com base nos quartis de preco"
order_items['categoria_preco'] = pd.qcut(order_items['price'], q=4,labels = rotulos_ticket)

# %%
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


'revela a tendencia de comentários nulos por classificação de nota'
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

# %%

payments['flag_parcelamento'] = numpy.where(payments['payment_installments'] == 0,1,0)
