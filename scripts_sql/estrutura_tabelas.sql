USE olist_v2;
-- -------------------------------------------
DESCRIBE customers_2_limpa;
SELECT*FROM customers_2_limpa;

ALTER TABLE customers_2_limpa
modify column customer_id VARCHAR(32),
modify column customer_unique_id VARCHAR(32),
modify column customer_zip_code_prefix int,
modify column  customer_city VARCHAR(50),
modify column customer_state CHAR(2);


ALTER TABLE customers_2_limpa 
ADD PRIMARY KEY (customer_id);

-- -------------------------------------------
describe forecast_mensal_explodida_limpa;
SELECT*FROM forecast_mensal_explodida_limpa LIMIT 5;

ALTER TABLE forecast_mensal_explodida_limpa
modify column order_id VARCHAR(32),
modify column payment_type VARCHAR(25),
modify column payment_installments tinyint,
modify column parcelas smallint,
modify column mes_offset tinyint,
modify column flag_parcelamento tinyint,
modify column flag_inconsistencia_parcelamento tinyint,
modify column order_status VARCHAR(25),
modify column order_delivered_customer_date DATETIME,
modify column order_purchase_timestamp datetime,
modify column flag_integridade tinyint,
modify column flg_atraso tinyint,
modify column data_prevista_pagamento DATETIME;

ALTER TABLE forecast_mensal_explodida_limpa
ADD foreign key (order_id) references orders_limpa(order_id);

-- -------------------------------------------
describe geolocation_limpa;
SELECT*FROM geolocation_limpa LIMIT 5;

ALTER TABLE geolocation_limpa
modify column geolocation_city VARCHAR(100),
modify column geolocation_zip_code_prefix int,
modify column geolocation_state CHAR(2);
-- -------------------------------------------
describe order_items_limpa;
SELECT*FROM order_items_limpa LIMIT 5;

ALTER TABLE order_items_limpa
modify column order_id VARCHAR(32),
modify column order_item_id tinyint,
modify column product_id VARCHAR(32),
modify column seller_id VARCHAR(32),
modify column shipping_limit_date DATETIME,
modify column price float,
modify column freight_value float,
modify column valor_pago float,
modify column flag_frete_gratis tinyint,
modify column flag_outlier_preco_max tinyint,
modify column flag_outlier_preco_min tinyint,
modify column flag_outlier_frete_max tinyint,
modify column flag_outlier_frete_min tinyint,
modify column categoria_preco varchar(32),
modify column flag_outlier_proporcao_max tinyint,
modify column flag_frete_abusivo tinyint,
modify column categoria_frete varchar(32);


ALTER TABLE order_items_limpa
ADD PRIMARY KEY (order_id, order_item_id),
ADD FOREIGN KEY (order_id) REFERENCES orders_limpa(order_id),
ADD FOREIGN KEY (product_id) REFERENCES produtos_limpa(product_id),
ADD FOREIGN KEY (seller_id) REFERENCES vendedores_limpa(seller_id);
-- -------------------------------------------
describe order_reviews_limpa;
select *from order_reviews_limpa;

ALTER TABLE order_reviews_limpa
modify column review_id VARCHAR(32),
modify column order_id VARCHAR(32),
modify column review_score tinyint,
modify column review_creation_date DATETIME,
modify column review_answer_timestamp DATETIME,
modify column tempo_resposta int,
modify column classificacao_tempo_reposta varchar(30);

ALTER TABLE order_reviews_limpa
ADD PRIMARY KEY (review_id, order_id),
ADD FOREIGN KEY (order_id) REFERENCES orders_limpa(order_id);
-- -------------------------------------------
describe orders_limpa;
select*from orders_limpa;

ALTER TABLE orders_limpa
modify column order_id VARCHAR(32),
modify column customer_id VARCHAR(32),
modify column order_status VARCHAR(25),
modify column order_purchase_timestamp DATETIME,
modify column order_approved_at DATETIME,
modify column order_delivered_carrier_date DATETIME,
modify column order_delivered_customer_date DATETIME,
modify column order_estimated_delivery_date DATETIME,
modify column dias_para_entrega int,
modify column tempo_aprovacao_pedido int,
modify column tempo_coleta_item int,
modify column antecedencia_entrega int,
modify column flg_atraso tinyint,
modify column flag_integridade tinyint;

ALTER TABLE orders_limpa
ADD PRIMARY KEY (order_id),
ADD FOREIGN KEY (customer_id) REFERENCES customers_2_limpa(customer_id);

-- -------------------------------------------

describe payments_limpa;
select*from payments_limpa limit 5;

ALTER TABLE payments_limpa
modify column order_id VARCHAR(32),
modify column payment_sequential int,
modify column payment_type VARCHAR(32),
modify column payment_installments tinyint,
modify column payment_value float,
modify column flag_parcelamento tinyint,
modify column flag_inconsistencia_parcelamento tinyint;


ALTER TABLE payments_limpa
ADD PRIMARY KEY (order_id, payment_sequential),
ADD FOREIGN KEY (order_id) REFERENCES orders_limpa(order_id);
-- -------------------------------------------
describe produtos_limpa;
select*from produtos_limpa limit 5;

ALTER TABLE produtos_limpa
modify column product_id VARCHAR(32);


ALTER TABLE produtos_limpa
ADD PRIMARY KEY (product_id);
-- -------------------------------------------
describe vendedores_limpa;
select*from vendedores_limpa limit 5;

ALTER TABLE vendedores_limpa
modify column seller_id VARCHAR(32),
modify column seller_city VARCHAR(100),
modify column seller_zip_code_prefix int,
modify column seller_state CHAR(2);

ALTER TABLE vendedores_limpa
ADD PRIMARY KEY (seller_id);

