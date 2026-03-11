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


DESCRIBE orders_limpa;
-- colunas de fora: tabela order itens: shipping_limit_date; tabela orders: order_id	customer_id
select*from order_items_limpa limit 5; 
-- este join permite responder cap 1 pergunta 1,2. cap 2 perguntas 1,2,3
SELECT
	
-- colunas tb order_items_limpa
	order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value, valor_pago, flag_frete_gratis, flag_outlier_preco_max, flag_outlier_preco_min, flag_outlier_frete_max, flag_outlier_frete_min,
	categoria_preco, peso_frete_no_preco, flag_outlier_proporcao_max, flag_frete_abusivo, categoria_frete,
-- colunas tb orders_limpa
	customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, dias_para_entrega, tempo_aprovacao_pedido,
	tempo_coleta_item, antecedencia_entrega, flg_atraso, flag_integridade
FROM order_items_limpa as order_items
LEFT JOIN orders_limpa as orders ON order_items.order_id = orders.order_id;
-- --------------------------------

-- conferindo o tamanho das tabelas com order_id

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
-- --------------------------------
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

-- Encontrar as informações onde as order_id que não existem na tb order_itens, existem na tabela pagamentos.
WITH orders_itens_inexistente AS(
	SELECT 
		tb2.order_id,
		tb2.order_status,
		COUNT(tb2.order_status) as qtde_status
	FROM order_items_limpa tb1
	RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
	WHERE tb1.order_id is null
	GROUP BY tb2.order_status
)
SELECT *
FROM payments_limpa tb1
JOIN orders_itens_inexistente tb2 ON tb2.order_id = tb1.order_id;




