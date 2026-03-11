# olist-data-auditing-and-modeling
Desenvolvimento da versão aprimorada do portifólio da Olist, trabalhado em dezembro.

Perguntas de negócio:
-  Qual é a taxa de quebra de SLA (Service Level Agreement) de entrega e como o atraso logístico está impactando diretamente a retenção de receita?
-  Qual é a nossa penetração e margem de lucro por região? O custo do frete (freight_value) está canibalizando vendas no Norte/Nordeste?
-  Quais são os projetos/categorias com mais vendas?
-  Como foi a performance das categorias nos últimos 6 meses
-  Como está o nosso ticket médio?
-  Qual a satisfação dos nossos clientes?
-  Temos muitos atrasos nas entregas?
-  Como está a concentração de risco no nosso ecossistema? (ex: 80% da nossa receita depende de apenas 5% dos sellers?). Quem são os sellers tóxicos (alto volume, mas com péssimos reviews que destroem a marca)?
-  Qual a projeção de fluxo de caixa baseada no perfil de parcelamento (payment_installments) vs. pagamentos à vista (payment_type)?

Capítulo 1: A Saúde Financeira (A Visão Macro):
- Pergunta: Como evoluiu a Receita Bruta Total (GMV - Gross Merchandise Volume) ao longo dos 3 anos? Tivemos sazonalidade (ex: Black Friday)?
- Pergunta: O Ticket Médio (Produto + Frete) aumentou ou diminuiu? Os clientes estão comprando mais itens por pedido ou itens mais caros?
- Pergunta: Qual é a nossa exposição no fluxo de caixa? (Seu forecast de parcelamentos entra aqui como a "cereja do bolo").

Capítulo 2: A Eficiência Operacional (O Motor Logístico):
- Pergunta: Qual a diferença entre a "Promessa" (order_estimated_delivery_date) e a "Realidade" (order_delivered_customer_date)?
- Pergunta: Onde está o gargalo da operação? É o seller demorando para despachar para a transportadora (order_delivered_carrier_date), ou a transportadora demorando para entregar ao cliente?
- Pergunta: O custo do frete médio (freight_value) versus o valor do produto (price) é sustentável? (Ex: Pagar R$ 50 de frete num produto de R$ 30 inviabiliza o negócio).

Capítulo 3: A Qualidade do Ecossistema (Sellers & Categorias)
Não vendemos os produtos, nós intermediamos. Os parceiros são bons?
- Pergunta: Curva ABC de Sellers: Quantos sellers representam o maior volume de faturamento e quais categorias eles dominam?
- Pergunta: Qual é a taxa de rejeição das categorias? (Ex: Vender eletrônicos traz muita receita, mas tem o maior número de devoluções/reviews ruins?).

Capítulo 4: O Termômetro da Marca (Satisfação do Cliente)
O impacto do processo na percepção do usuário.
- Pergunta: Como o Review Score médio flutuou ao longo dos 3 anos?
- Pergunta (A Mais Matadora): Qual é a correlação exata entre Atraso na Entrega e Reviews Nota 1?

Status Projeto:
- [x] EDA: Análise exploratória dos dados. Entendimento dos campos, análises estatísticas e distribuição dos dados.
- [x] Entendimetno das tabelas dimensão e fato.

ETL: Processamento e limpeza dos dados.
- [x] Encontrar por inconsistencia de dados.
- [x] Limpeza e tratamento dos erros.
- [x] Processamento de dados criação de novas colunas flag para clusters.

Banco de dados:
- [x] Upload dos dados no SQL.
- [x] Modelagem dos dados: definição das PK e FK's.
- [x] Levantamento de perguntas de negócio.
- [ ] Joins para análises.

Tabelas:
- [x] Order_itens e orders. Verificado a inconsistencia de qtde de order_id com a tabela payments.
- [x] Verificado o status das orders referente a order_id existentes apenas na tabela payments. O status apresentado são de itens cancelados e indisponíveis
- [x] Verificado a diferença de valores entre order_items e payments devido aos order_id existentes na payments.
- [ ] Construir o join da tabela payments e realizar os filtros necessários estudados para a view final que será utilizada.

Levantamento de hipóteses:
Hipótese 1: A "Taxa de Queima" Logística
- Hipótese: A maioria das avaliações negativas (Score 1 e 2) não ocorre por má qualidade do produto, mas sim devido a falhas de SLA na ponta logística (atrasos).
Análise Necessária: Cruzar tb_order_reviews (score <= 2) com tb_orders (onde order_delivered_customer_date > order_estimated_delivery_date).
Ação Recomendada: Criar um programa de penalização para sellers que demoram a despachar e renegociar contratos com as transportadoras que mais atrasam nos Estados críticos.

Hipótese 2: O Risco de Concentração (Pareto)
- Hipótese: Aplicando o princípio de Pareto, assumimos que 20% dos sellers geram 80% do faturamento da Olist.
Análise Necessária: Rankear os sellers por GMV (Receita Total) e criar um percentual acumulado.
Ação Recomendada: Desenvolver um programa de fidelização "Key Accounts" para proteger os top 20% de migrarem para a concorrência (Mercado Livre/Amazon).

Hipótese 3: O Paradoxo do Frete
- Hipótese: Em categorias de baixo ticket (produtos baratos), a taxa de abandono ou baixo volume de vendas está diretamente ligada ao valor do frete ultrapassar X% do valor do produto.
Análise Necessária: Calcular a razão freight_value / price. Ver se o volume de vendas cai drasticamente quando essa razão ultrapassa 30% ou 40%.
Ação Recomendada: Rever a estratégia de precificação de frete nessas categorias ou criar Centros de Distribuição (CDs) mais próximos das regiões com pior relação Frete/Preço.
