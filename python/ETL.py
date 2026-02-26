# %%

import pandas as pd
from unidecode import unidecode
import sys
import func_estatistica as fe

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
# %%

'tabela order_items' #RangeIndex: 112650 order_id  & order_item_id (PK - composta) 
# shipping_limit_date - tempo limite do vendedor entregar o item pra logística

order_items = pd.read_csv('../Olist/olist_order_items_dataset.csv',sep=',')

order_items['valor pago'] = order_items['price'] + order_items['freight_value']

# %%
order_reviews = pd.read_csv('../Olist/olist_order_reviews_dataset.csv',sep=',')
# %%
