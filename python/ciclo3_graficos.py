# %%
import pandas as pd
import sys
import func_estatistica as fe

"selecione seu caminho de pasta onde está localizado o modulo func_estatistica"
sys.path.append(r'C:\Users\gusta\OneDrive\Documentos\GitHub\Projeto Portifólio Olist - V2 Power BI\olist-data-auditing-and-modeling\python')

# olist_order_items_dataset.csv - order_id e order_item_id (PK - composta) price #RangeIndex: 112650
# olist_customers_dataset.csv - customer_id (pk) customer_state # RangeIndex: 99441
# olist_order_payments_dataset.csv - order_id e payment_sequential - (PK - composta) e payment_value #RangeIndex: 103886
# olist_orders_dataset.csv - order_id (pk)	customer_id	(pk) RangeIndex: 99441

# %%
orders_items = pd.read_csv('../Olist/olist_order_items_dataset.csv',sep=',')

#%%

customers = pd.read_csv('../Olist/olist_customers_dataset.csv',sep=',')

# %%

pagamentos = pd.read_csv('../Olist/olist_order_payments_dataset.csv',sep=',')

# %%
orders = pd.read_csv('../Olist/olist_orders_dataset.csv',sep=',')

# %%
"pagamentos construção dos cálculos de forma manual:"

pagamentos_estatistica = pagamentos.describe()


MAE_pagamentos = (pagamentos['payment_value'] - pagamentos['payment_value'].mean()).abs().mean()
cv_pagamentos = pagamentos['payment_value'].std()/pagamentos['payment_value'].mean()
IQR_pagamentos = pagamentos_estatistica['payment_value'].loc['75%'] - pagamentos_estatistica['payment_value'].loc['25%']
outlier_max = pagamentos_estatistica['payment_value'].loc['75%'] + (1.5*IQR_pagamentos)
outlier_min = pagamentos_estatistica['payment_value'].loc['25%'] - (1.5*IQR_pagamentos)

#%%
" uso da função criada estatística para obter os valores de IQR, CV, STD e outliers..."
lista = fe.estatisticas(pagamentos.groupby(by='order_id').agg({
    'payment_value':'sum'
})['payment_value'])


# %%
"join por meio da tabela de pagamentos"
vendas_estado = pagamentos.merge(right=orders,how='left', on = ['order_id'], suffixes=['_pagamentos','_orders']).merge(right=customers,how='left', on= 'customer_id',suffixes=['_1','_customers'])
# %%

teste1 = fe.estatisticas(vendas_estado.groupby(by='order_id').agg({
    'payment_value':'sum'
})['payment_value'])
# %%
"check dos valores de preço e frete como valor a ser pago pelo cliente"
orders_items['valor pago'] = orders_items['price'] + orders_items['freight_value']
# %%
"cálculo das estatísticas da coluna de preço + pagamento"
teste2 = fe.estatisticas(orders_items.groupby(by='order_id').agg({
    'valor pago':'sum'
})['valor pago'])

# %%
"merge por meio da tabela orders items"

preco_frete_estado = orders_items.merge(right=orders,how='left', on = ['order_id'], suffixes=['_items','_orders']).merge(right=customers,how='left', on= 'customer_id',suffixes=['_1','_customers'])

# %%
"comparação entre as duas tabelas joins agregando os order_id através da soma do valor"
soma_preco_frete_estado = preco_frete_estado.groupby(by='order_id')['valor pago'].sum()
soma_vendas_estado = vendas_estado.groupby(by='order_id')['payment_value'].sum()

"verificar as estatísticas desse agrupamento e validar se os valores de pagamento e preço estão de acordo"
estatisticas_preco_frete = fe.estatisticas(soma_preco_frete_estado)
estatisticas_vendas_estado = fe.estatisticas(soma_vendas_estado)
# %%
"foi possível notar uma diferença na quantidade de orders id's nas estatísticas anterior, vou investigar o que são esses casos"
vendas_estado_agrupado_order_id = vendas_estado.groupby(by='order_id').agg({
    'payment_value': 'sum',
    'order_status': 'first',
    'customer_state': 'first',
    'order_purchase_timestamp': 'first'}).reset_index()

"obter a lista de order id que não está presente na tabela order item mas está na tabela de pagamentos"
casos_especificos = vendas_estado_agrupado_order_id.merge(right=pd.DataFrame(soma_preco_frete_estado).reset_index()['order_id'],how='outer',indicator=True)

casos_especificos = casos_especificos[casos_especificos['_merge'] == 'left_only']
lista_order_id_payment = casos_especificos['order_id'].to_list()

filtrado_vendas_estado = vendas_estado[(vendas_estado['order_id'].isin(lista_order_id_payment))]

"filtra os itens em comuns"
vendas_estado_preco_frete = vendas_estado[~(vendas_estado['order_id'].isin(lista_order_id_payment))]

agregado = vendas_estado_preco_frete.groupby(by='order_id').agg({'payment_value':'sum'
})['payment_value']

# %%

"encontro do único id que não foi encontrado no cruzamento da tabela de pagamento e orders"
check_id = vendas_estado.merge(orders['order_id'],how='outer',indicator=True)
check_id = check_id[check_id['_merge'] == 'right_only']
lista_teste = check_id['order_id'].to_list()
filtrado_check_id = orders[orders['order_id'].isin(lista_teste)]
# %%

"teste matplotlib"
vendas_por_estado = vendas_estado.groupby('customer_state')['payment_value'].sum().sort_values(ascending=False)

plt.bar(vendas_por_estado.index,vendas_por_estado.values, color = 'skyblue')
plt.title('Vendas por Estado')
plt.xlabel('Estados')
plt.ylabel('Pagamentos')
# %%
"criar csv para enviar ao power bi"

vendas_estado.to_csv('vendas por estado completo.csv')

preco_frete_estado.to_csv('preco + frete completo.csv')

filtrado_vendas_estado.to_csv('orders presentes apenas nas vendas.csv')

vendas_estado_preco_frete.to_csv('tabela filtrada com as mesmas orders.csv')
# %%
