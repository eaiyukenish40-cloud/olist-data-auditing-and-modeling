-- VIEWS Para PBI

-- 1. Fato
CREATE VIEW f_pedido_item_valor AS
SELECT
-- chaves
	order_items.order_id, 
    order_items.order_item_id, 
    order_items.product_id, 
    order_items.seller_id, 
    orders.customer_id,
-- categorias:
	orders.order_status,
    produtos.product_category_name,
    order_items.categoria_preco,
    order_items.categoria_frete,
-- datas:
    orders.order_purchase_timestamp,
    orders.order_approved_at,
    order_items.shipping_limit_date,
    orders.order_delivered_carrier_date, 
    orders.order_delivered_customer_date, 
    orders.order_estimated_delivery_date,
-- flags:
	order_items.flag_frete_gratis, 
    order_items.flag_outlier_preco_max, 
    order_items.flag_outlier_preco_min, 
    order_items.flag_outlier_frete_max, 
    order_items.flag_outlier_frete_min,
	order_items.flag_outlier_proporcao_max, 
    order_items.flag_frete_abusivo,
    orders.flg_atraso, flag_integridade,
-- métricas:
	order_items.price, 
    order_items.freight_value, 
    order_items.valor_pago,
    order_items.peso_frete_no_preco, 
    orders.dias_para_entrega, 
    orders.tempo_aprovacao_pedido,
    orders.tempo_coleta_item, 
    orders.antecedencia_entrega
FROM order_items_limpa as order_items
LEFT JOIN orders_limpa as orders ON order_items.order_id = orders.order_id
LEFT JOIN produtos_limpa as produtos ON produtos.product_id = order_items.product_id;


-- 2. fato pagamentos
CREATE VIEW f_pagamentos_consolidados AS
-- criação deste filtro inicial através de CTE para encontar os id's que não existiam na tb order_itens por meio de todas as id's da tb orders.select
-- com as id's encontradas, filtrar a tabela pagamentos removendo as id's encontradas no passo anterior dessa tabela
WITH orders_itens_inexistente AS(
	SELECT 
		tb2.order_id,
		tb2.order_status,
        CASE 	
			WHEN order_status in ('invoiced', 'shipped') THEN 'Inconsistencia_origem'
            WHEN order_status IN ('canceled','unavailable') THEN 'Estorno/Reembolso'
            ELSE 'Acompanhar'
		END as status_id_inexistentes
	FROM order_items_limpa tb1
	RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
	WHERE tb1.order_id is null
)
SELECT 
	-- chaves
	pag.order_id, 
    pag.payment_sequential, 
    orders.customer_id,
    -- categorias
    orders.order_status,
    pag.payment_type, 
    id.status_id_inexistentes,
    pag.payment_installments,
    -- métricas
    pag.payment_value,
    orders.dias_para_entrega, 
	orders.tempo_aprovacao_pedido,
    orders.tempo_coleta_item, 
    orders.antecedencia_entrega,
    -- flags
    pag.flag_parcelamento, 
    pag.flag_inconsistencia_parcelamento,
    orders.flg_atraso, orders.flag_integridade,
    -- datas
	orders.order_purchase_timestamp, 
    orders.order_approved_at, 
    orders.order_delivered_carrier_date, 
	orders.order_delivered_customer_date, 
    orders.order_estimated_delivery_date  
FROM payments_limpa as pag
LEFT JOIN orders_limpa as orders ON orders.order_id = pag.order_id
LEFT JOIN orders_itens_inexistente as id ON id.order_id = pag.order_id
WHERE id.status_id_inexistentes = 'Acompanhar' OR orders.order_status not IN ('canceled','unavailable')  AND  id.status_id_inexistentes is null;


-- 3. fato forecast

CREATE VIEW f_forecast AS
WITH orders_itens_inexistente AS(
	SELECT 
		tb2.order_id,
		tb2.order_status,
        CASE 	
			WHEN order_status in ('invoiced', 'shipped') THEN 'Inconsistencia_origem'
            WHEN order_status IN ('canceled','unavailable') THEN 'Estorno/Reembolso'
            ELSE 'Acompanhar'
		END as status_id_inexistentes
	FROM order_items_limpa tb1
	RIGHT JOIN orders_limpa tb2 ON tb1.order_id = tb2.order_id
	WHERE tb1.order_id is null
)
SELECT 
	-- chaves
    forecast.order_id,
    -- métrica
    forecast.payment_installments, 
    forecast.parcelas,
    -- categorias
    forecast.order_status,
    forecast.payment_type, 
    id.order_status as order_status_filtro, 
    id.status_id_inexistentes,
    -- datas
    forecast.order_purchase_timestamp,
    forecast.order_delivered_customer_date, 
	forecast.data_prevista_pagamento,
    -- flags
    forecast.flag_parcelamento, 
    forecast.flag_inconsistencia_parcelamento, 
    forecast.flag_integridade,
	forecast.flg_atraso    
FROM forecast_mensal_explodida_limpa as forecast
LEFT JOIN orders_itens_inexistente as id ON id.order_id = forecast.order_id
WHERE status_id_inexistentes = 'Acompanhar' OR forecast.order_status not IN ('canceled','unavailable')  AND  status_id_inexistentes is null;

-- dimensões
CREATE VIEW d_clientes AS
SELECT 
	*
FROM customers_2_limpa;

CREATE VIEW d_produtos AS
SELECT
	*
FROM produtos_limpa;

CREATE VIEW d_vendedores AS
SELECT 
	*
FROM vendedores_limpa;

CREATE VIEW d_geolocalização AS
SELECT 
	DISTINCT geolocation_zip_code_prefix,
    geolocation_city,geolocation_state,    
	CASE 
		WHEN geolocation_state in ('AC','AP','AM','PA','RO','RR','TO') THEN 'Norte'
		WHEN geolocation_state in ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
		WHEN geolocation_state in ('DF','GO','MT','MS') THEN 'Centro-Oeste'
		WHEN geolocation_state in ('ES','MG','RJ','SP') THEN 'Sudeste'
		WHEN geolocation_state in ('PR','SC','RS') THEN 'Sul'
	END as regiões
FROM geolocation_limpa;

