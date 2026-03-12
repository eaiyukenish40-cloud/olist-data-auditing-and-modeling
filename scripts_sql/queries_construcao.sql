CREATE DATABASE olist_v2;
use olist_v2;
-- customers_2_limpa
-- forecast_mensal_explodida_limpa
-- geolocation_limpa
-- orders_limpa
-- order_items_limpa
-- order_reviews_limpa
-- payments_limpa
-- produtos_limpa
-- vendedores_limpa

-- 1. responde a pergunta 3 do capítulo 1
describe forecast_mensal_explodida_limpa;

WITH orders_itens_inexistente AS(
	SELECT 
		tb2.order_id,
		tb2.order_status
	FROM order_items_limpa tb1
	RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
	WHERE tb1.order_id is null
),
id_inexistentes AS (
	SELECT 
		order_id,order_status,
        CASE 	
			WHEN order_status in ('invoiced', 'shipped') THEN 'Inconsistencia_origem'
            WHEN order_status IN ('canceled','unavailable') THEN 'Estorno/Reembolso'
            ELSE 'Acompanhar'
		END as status_id_inexistentes
	FROM orders_itens_inexistente
)
SELECT 
	-- forecast
    forecast.order_id, payment_type, payment_installments, parcelas, mes_offset, flag_parcelamento, flag_inconsistencia_parcelamento, forecast.order_status, order_delivered_customer_date, order_purchase_timestamp, flag_integridade,
	flg_atraso, data_prevista_pagamento,
    -- CTE filtro
    id.order_status as order_status_filtro, status_id_inexistentes,
    count(distinct forecast.order_id)
FROM forecast_mensal_explodida_limpa as forecast
LEFT JOIN id_inexistentes as id ON id.order_id = forecast.order_id
WHERE status_id_inexistentes = 'Acompanhar' OR forecast.order_status not IN ('canceled','unavailable')  AND  status_id_inexistentes is null 
;


-- ----------------------------------------

-- 2. preparação da tabela para responder cap 1 pergunta 1,2. cap 2 perguntas 1,2,3
DESCRIBE orders_limpa;
select count(*)from order_items_limpa limit 5; 

-- colunas de fora: tabela order itens: shipping_limit_date; tabela orders: order_id	customer_id

SELECT
-- colunas tb order_items_limpa
	order_items.order_id, order_item_id, order_items.product_id, seller_id, shipping_limit_date, price, freight_value, valor_pago, flag_frete_gratis, flag_outlier_preco_max, flag_outlier_preco_min, flag_outlier_frete_max, flag_outlier_frete_min,
	categoria_preco, peso_frete_no_preco, flag_outlier_proporcao_max, flag_frete_abusivo, categoria_frete,
-- colunas tb orders_limpa
	customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, dias_para_entrega, tempo_aprovacao_pedido,
	tempo_coleta_item, antecedencia_entrega, flg_atraso, flag_integridade,
-- sum(valor_pago) as total_pago
-- count(DISTINCT order_items.order_id)

-- tb produtos
	product_category_name
FROM order_items_limpa as order_items
LEFT JOIN orders_limpa as orders ON order_items.order_id = orders.order_id
LEFT JOIN produtos_limpa as produtos ON produtos.product_id = order_items.product_id
-- WHERE order_status not in ('canceled','unavailable')
;
describe produtos_limpa;
-- --------------------------------

-- 3. Verificando joins pra tabelas pagamentos

WITH orders_itens_inexistente AS(
	SELECT 
		tb2.order_id,
		tb2.order_status
	FROM order_items_limpa tb1
	RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
	WHERE tb1.order_id is null
),
id_inexistentes AS (
	SELECT 
		order_id,order_status,
        CASE 	
			WHEN order_status in ('invoiced', 'shipped') THEN 'Inconsistencia_origem'
            WHEN order_status IN ('canceled','unavailable') THEN 'Estorno/Reembolso'
            ELSE 'Acompanhar'
		END as status_id_inexistentes
	FROM orders_itens_inexistente
)
SELECT 
	-- Tb: payments
	pag.order_id, payment_sequential, payment_type, payment_installments, payment_value, flag_parcelamento, flag_inconsistencia_parcelamento
    -- tb: orders
    customer_id, orders.order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, dias_para_entrega, tempo_aprovacao_pedido,
	tempo_coleta_item, antecedencia_entrega, flg_atraso, flag_integridade,
    -- filtro join 
    status_id_inexistentes
FROM payments_limpa as pag
LEFT JOIN orders_limpa as orders ON orders.order_id = pag.order_id
LEFT JOIN id_inexistentes as id ON id.order_id = pag.order_id
WHERE status_id_inexistentes = 'Acompanhar' OR orders.order_status not IN ('canceled','unavailable')  AND  status_id_inexistentes is null;
-- --------------------------------
-- 4. criação da view para clientes 

SELECT
-- colunas tb order_items_limpa
	order_items.order_id, order_item_id, order_items.product_id, seller_id, shipping_limit_date, price, freight_value, valor_pago, flag_frete_gratis, flag_outlier_preco_max, flag_outlier_preco_min, flag_outlier_frete_max, flag_outlier_frete_min,
	categoria_preco, peso_frete_no_preco, flag_outlier_proporcao_max, flag_frete_abusivo, categoria_frete,
-- colunas tb orders_limpa
	orders.customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, dias_para_entrega, tempo_aprovacao_pedido,
	tempo_coleta_item, antecedencia_entrega, flg_atraso, flag_integridade,
-- sum(valor_pago) as total_pago
-- count(DISTINCT order_items.order_id)
-- colunas clientes:
	customer_zip_code_prefix, customer_city, customer_state,
    CASE 
		WHEN customer_state in ('AC','AP','AM','PA','RO','RR','TO') THEN 'Norte'
        WHEN customer_state in ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
        WHEN customer_state in ('DF','GO','MT','MS') THEN 'Centro-Oeste'
        WHEN customer_state in ('ES','MG','RJ','SP') THEN 'Sudeste'
        WHEN customer_state in ('PR','SC','RS') THEN 'Sul'
	END as regiões,
-- tb produtos:
	product_category_name
FROM order_items_limpa as order_items
LEFT JOIN orders_limpa as orders ON order_items.order_id = orders.order_id
LEFT JOIN customers_2_limpa as clientes ON clientes.customer_id = orders.customer_id
LEFT JOIN produtos_limpa as produtos ON produtos.product_id = order_items.product_id;
-- WHERE order_status not in ('canceled','unavailable')


describe customers_2_limpa;
SELECT *
FROM customers_2_limpa
group by customer_state;
-- --------------------------------

-- 5. criação da view para vendedores

SELECT
-- colunas tb order_items_limpa

	order_items.order_id, order_item_id, order_items.product_id, order_items.seller_id, shipping_limit_date, price, freight_value, valor_pago, flag_frete_gratis, flag_outlier_preco_max, flag_outlier_preco_min, flag_outlier_frete_max, flag_outlier_frete_min,
	categoria_preco, peso_frete_no_preco, flag_outlier_proporcao_max, flag_frete_abusivo, categoria_frete,
-- colunas tb orders_limpa

	order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, dias_para_entrega, tempo_aprovacao_pedido,
	tempo_coleta_item, antecedencia_entrega, flg_atraso, flag_integridade,
-- sum(valor_pago) as total_pago
-- count(DISTINCT order_items.order_id)

-- colunas vendedores:
	seller_zip_code_prefix, seller_city, seller_state,
    CASE 
		WHEN seller_state in ('AC','AP','AM','PA','RO','RR','TO') THEN 'Norte'
        WHEN seller_state in ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
        WHEN seller_state in ('DF','GO','MT','MS') THEN 'Centro-Oeste'
        WHEN seller_state in ('ES','MG','RJ','SP') THEN 'Sudeste'
        WHEN seller_state in ('PR','SC','RS') THEN 'Sul'
	END as regiões,
    -- tabela produtos
    product_category_name
FROM order_items_limpa as order_items
LEFT JOIN orders_limpa as orders ON order_items.order_id = orders.order_id
LEFT JOIN vendedores_limpa as vendedores ON vendedores.seller_id = order_items.seller_id
LEFT JOIN produtos_limpa as produtos ON produtos.product_id = order_items.product_id;

describe vendedores_limpa;

-- --------------------------------
-- 6. trabalho de conferencia e validação dos dados para realizar os joins e criação das views conferindo o tamanho das tabelas com order_id

-- pk order_id: 99441 contem todas as orders (referencia)
SELECT count(DISTINCT order_id)
FROM orders_limpa;

-- order_id distintas: 99440
SELECT count(DISTINCT order_id)
FROM payments_limpa
;

-- linhas distintas de order_id: 98666
SELECT count(DISTINCT order_id)
FROM order_items_limpa;

-- encontrar a única order_id distinta entre order_limpa e pagamentos

-- encontrar o order_id que não existe na tabela de pagamentos.
SELECT 
	tb2.order_id
FROM payments_limpa tb1
RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
WHERE tb1.order_id is null;

-- usando como subquery: como é a característica deste item? Foi entregue?
SELECT *
FROM orders_limpa
WHERE order_id = (SELECT 
	tb2.order_id
FROM payments_limpa tb1
RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
WHERE tb1.order_id is null);


-- usando como subquery para a tabela order_item
SELECT *
FROM order_items_limpa
WHERE order_id = (SELECT 
	tb2.order_id
FROM payments_limpa tb1
RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
WHERE tb1.order_id is null);

-- itens entregues atrasados.
SELECT count(*)
FROM orders_limpa
WHERE  flg_atraso = 1;

-- Encontrar os itens que não há intersecção entre order_itens e orders: 775 order_id

SELECT 
	*
FROM order_items_limpa tb1
RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
WHERE tb1.order_id is null
ORDER BY order_approved_at DESC;


SELECT 
	tb2.order_status,
	COUNT(tb2.order_status) as qtde_status
FROM order_items_limpa tb1
RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
WHERE tb1.order_id is null
GROUP BY tb2.order_status;

-- Encontrar as informações onde as order_id que não existem na tb order_itens, existem na tabela pagamentos.
WITH orders_itens_inexistente AS(
	SELECT 
		tb2.order_id,
		tb2.order_status
	FROM order_items_limpa tb1
	RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
	WHERE tb1.order_id is null
),
resumo_pagamento_orders_inexistentes AS(
	SELECT 
		order_status,
		count(order_status) as qtde_tipo,
		sum(payment_value) as soma_pagamento
	FROM payments_limpa tb1
	JOIN orders_itens_inexistente tb2 ON tb2.order_id = tb1.order_id
	GROUP BY tb2.order_id
)

-- Valor da tabela pagamentos R$ 162.591,95 de itens que não existem na ordem item que são (indisponível,cancelado = 161.676)
SELECT 
	order_status,
	COUNT(qtde_tipo) AS qtde_tipo,
    SUM(soma_pagamento) as soma_pagamento
FROM resumo_pagamento_orders_inexistentes
group by order_status
;

-- descontando o valor encontrado do valor da tabela do pagamento, chegamos no valor próximo do order_items. 
SELECT SUM(payment_value)
FROM payments_limpa;

SELECT
SUM(valor_pago)
FROM order_items_limpa;
-- --------------------------------