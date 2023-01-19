#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import numpy as np
from shroomdk import ShroomDK
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import numpy as np
import altair as alt
sdk = ShroomDK("679043b4-298f-4b7f-9394-54d64db46007")
st.set_page_config(page_title="$LUNA price run investigation", layout="wide",initial_sidebar_state="collapsed")



# In[2]:


import time
my_bar = st.progress(0)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1)


# In[5]:


st.title('Terra Run Price Investigation')
st.write('')
st.markdown('Beginning in the wee hours of Monday, January 9 (ET), the price of LUNA skyrocketed, from 1.37 to a high of nearly 2 before settling down at roughly 1.60.')
st.markdown(' The idea of this work is to try to find some reason why these jumps are occurring. The goal here is to understand why did the price jump so suddenly on Monday night and if the price seems to remain above or below the current marks.')
st.write('')
st.write('For this reason, this dashboard comprehens the following sections:')
st.markdown('1. LUNA price comparison against the major competitors')
st.markdown('2. Terra main activity comparison against LUNA price')
st.markdown('3. Terra development before and after $LUNA jumps')
st.markdown('4. Terra staking activity before and after LUNA jumps')
st.write('')

st.subheader('1. $LUNA price comparison')
st.write('In this analysis we will focus on the evolution of the LUNA token during since the start of the year and we are gonna compare against the major crypto competitors. More specifically.')
sql="""
WITH
t1 as (
select
  trunc(recorded_hour,'hour') as date,
  'LUNA' as symbol,
  avg(close) as price_usd
  from crosschain.core.fact_hourly_prices where id='terra-luna-2' and date>='2023-01-01'
  group by 1,2
),
  t2 as (
select
  trunc(recorded_at,'hour') as date,
  symbol,
  avg(price) as price_usd
  from osmosis.core.dim_prices where symbol in ('OSMO','ATOM','JUNO','EVMOS') and date>='2023-01-01'
  group by 1,2
)
SELECT * from t1 union select * from t2
"""

sql2="""
WITH
t1 as (
select
  trunc(recorded_hour,'day') as date,
  'LUNA' as symbol,
  avg(close) as price_usd
  from crosschain.core.fact_hourly_prices where id='terra-luna-2' and date>='2023-01-01'
  group by 1,2
),
  t2 as (
select
  trunc(recorded_at,'day') as date,
  symbol,
  avg(price) as price_usd
  from osmosis.core.dim_prices where symbol in ('OSMO','JUNO','EVMOS') and date>='2023-01-01'
  group by 1,2
)
SELECT * from t1 union select * from t2
"""
st.experimental_memo(ttl=50000)
def memory(code):
    data=sdk.query(code)
    return data

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()
results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

with st.expander("Check the analysis"):
    st.altair_chart(alt.Chart(df)
    .mark_line()
    .encode(x='date:N', y='price_usd:Q',color='symbol')
    .properties(title='Hourly prices evolution'),width=1000)
    
    st.altair_chart(alt.Chart(df2)
    .mark_line()
    .encode(x='date:N', y='price_usd:Q',color='symbol',width=1000)
    .properties(title='Daily prices evolution'))


st.write('')
st.subheader('2. Terra main activity comparison against LUNA price')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the activity of Terra ecosystem during this year in comparison to the LUNA price. More specifically, we will analyze the following data:')
st.markdown('● Total number transactions vs LUNA price')
st.markdown('● Total active users vs LUNA price')
st.markdown('● Total volume moved vs LUNA price')
st.write('')

sql="""
with 
luna as (
select
  trunc(recorded_hour,'hour') as date,
  avg(close) as price_usd
  from crosschain.core.fact_hourly_prices where id='terra-luna-2' and date>='2023-01-01'
  group by 1
),
txns as(
select 
  date_trunc('hour',block_timestamp) as date,
  count(distinct tx_id) as n_txns,
  count(distinct tx_sender) as n_wallets,
  sum(fee) as fee_luna
from terra.core.fact_transactions
  where block_timestamp >= '2023-01-01'
group by date
order by date desc
),
new_wallets as (
select 
  date,
  count(tx_sender) as n_new_wallets
  from (
select 
  date_trunc('hour',min(block_timestamp)) as date,
  tx_sender
from terra.core.fact_transactions
group by tx_sender
)
  where date >= '2023-01-01'
group by date
)

select 
  t.*,
  price_usd,
  n.n_new_wallets
from txns t left join new_wallets n using(date) left join luna l using(date)
order by date desc

"""

st.experimental_memo(ttl=50000)
def memory(code):
    data=sdk.query(code)
    return data

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()
    


with st.expander("Check the analysis"):
    
    base=alt.Chart(df).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='blue',opacity=0.5).encode(y='n_txns:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly transactions vs LUNA price'))
    
    base=alt.Chart(df).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='green',opacity=0.5).encode(y='n_wallets:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly active wallets vs LUNA price'))
    
    base=alt.Chart(df).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='red',opacity=0.5).encode(y='n_new_wallets:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly new wallets vs LUNA price'))
    


st.subheader("3. Ecosystem development before and after LUNA price movements")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the Terra main ecosystem development against LUNA price evolution. More specifically, we will analyze the following data:')
st.markdown('● New deployed contracts vs LUNA price')
st.markdown('● Used contracts vs LUNA price')
st.markdown('● Swaps activity vs LUNA price')



sql="""
with
luna as (
select
  trunc(recorded_hour,'hour') as date,
  avg(close) as price_usd
  from crosschain.core.fact_hourly_prices where id='terra-luna-2' and date>='2023-01-01'
  group by date
),
contracts as (
select 
   date_trunc('hour',block_timestamp) as date,    
  count(distinct tx_id) as new_contracts
from terra.core.ez_messages
where message_type = '/cosmwasm.wasm.v1.MsgInstantiateContract'
	and block_timestamp >= '2023-01-01'
group by date
order by date desc
)
select x.date,new_contracts,price_usd from contracts x join luna y on x.date=y.date 


"""


sql2="""
with
luna as (
select
  trunc(recorded_hour,'hour') as date,
  avg(close) as price_usd
  from crosschain.core.fact_hourly_prices where id='terra-luna-2' and date>='2023-01-01'
  group by date
),
contracts as (
select 
   date_trunc('hour',block_timestamp) as date,
  count(distinct tx:body:messages[0]:contract) as n_contracts
  from terra.core.fact_transactions 
  --where ATTRIBUTE_KEY in ('contract','u_contract_address','contract_name',
  --'contract_version','contract_addr','contract_address','dao_contract_address','pair_contract_addr','nft_contract')
  where block_timestamp >= '2023-01-01'

group by date
order by date desc
)
select x.date,n_contracts,price_usd from contracts x join luna y on x.date=y.date 


"""


sql3=""" 
with
luna as (
select
  trunc(recorded_hour,'hour') as date,
  avg(close) as price_usd
  from crosschain.core.fact_hourly_prices where id='terra-luna-2' and date>='2023-01-01'
  group by date
),
txns as(
select 
  date_trunc('hour',block_timestamp) as date,
  count(distinct tx_id) as n_txns,
  count(distinct trader) as n_wallets,
  sum(to_amount/1e6) as fee_luna
from terra.core.ez_swaps
  where block_timestamp >= '2023-01-01'
  and to_currency = 'uluna'
group by date
order by date desc
),
new_wallets as (
select 
  date,
  count(trader) as n_new_swappers
  from (
select 
  date_trunc('hour',min(block_timestamp)) as date,
  trader
from terra.core.ez_swaps
group by trader
)
   where date >= '2023-01-01'
group by date
)

select 
  t.*,
  price_usd,
  n.n_new_swappers
from txns t left join new_wallets n using(date) left join luna l using(date)
order by date desc

"""

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

results3 = memory(sql3)
df3 = pd.DataFrame(results3.records)
df3.info()

with st.expander("Check the analysis"):
    
    base=alt.Chart(df).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='blue',opacity=0.5).encode(y='new_contracts:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly new contracts vs LUNA price'))
    
    base=alt.Chart(df2).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='dark blue',opacity=0.6).encode(y='n_contracts:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly active contracts vs LUNA price'))
    
    base=alt.Chart(df3).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='dark green',opacity=0.5).encode(y='n_txns:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly swaps vs LUNA price'))
    
    base=alt.Chart(df3).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='green',opacity=0.6).encode(y='n_wallets:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly active swappers vs LUNA price'))
    
    base=alt.Chart(df3).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='red',opacity=0.5).encode(y='n_new_wallets:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly new swappers vs LUNA price'))
    


# In[9]:


st.subheader("4. Staking before and after LUNA price movements")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the Terra staking against LUNA price evolution. More specifically, we will analyze the following data:')
st.markdown('● Staking actions vs LUNA price')
st.markdown('● Active stakers vs LUNA price')
st.markdown('● Active validators vs LUNA price')



sql="""
with
luna as (
select
  trunc(recorded_hour,'hour') as date,
  avg(close) as price_usd
  from crosschain.core.fact_hourly_prices where id='terra-luna-2' and date>='2023-01-01'
  group by date
), 
txns as(
select 
  date_trunc('hour',block_timestamp) as date,
  count(distinct tx_id) as n_txns,
  count(distinct delegator_address) as n_wallets,
  count(distinct validator_address) as n_validators,
  sum(amount/1e6) as fee_luna
from terra.core.ez_staking
  where action = 'Delegate'
  and block_timestamp >= '2023-01-01'
group by date
order by date desc
),
new_wallets as (
select 
  date,
  count(delegator_address) as n_new
  from (
select 
  date_trunc('hour',min(block_timestamp)) as date,
  delegator_address
from terra.core.ez_staking
group by delegator_address
)
  where date >= '2023-01-01'
group by date
),
new_validators as (
select 
  date,
  count(validator_address) as n_new
  from (
select 
  date_trunc('hour',min(block_timestamp)) as date,
  validator_address
from terra.core.ez_staking
group by validator_address
)
  where date >= '2023-01-01'
group by date
)

select 
  t.*,
  price_usd,
  coalesce(n.n_new, 0) as n_new_wallets,
  coalesce(v.n_new, 0) as n_new_validators
from txns t 
  left join new_wallets n using(date)
  left join new_validators v using(date)
  left join luna l using(date)
order by date desc
"""



results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

with st.expander("Check the analysis"):
    
    base=alt.Chart(df).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='blue',opacity=0.5).encode(y='n_txns:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly staking actions vs LUNA price'))
    
    base=alt.Chart(df).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='red',opacity=0.4).encode(y='n_wallets:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly active stakers vs LUNA price'))
    
    base=alt.Chart(df).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='dark green',opacity=0.5).encode(y='n_validators:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly active validators vs LUNA price'))
    
    base=alt.Chart(df).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='red',opacity=0.6).encode(y='n_new_wallets:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly new stakers vs LUNA price'))
    
    base=alt.Chart(df).encode(x=alt.X('date:O'))
    line=base.mark_line(color='orange').encode(y=alt.Y('price_usd:Q', axis=alt.Axis(grid=True)))
    bar=base.mark_bar(color='green',opacity=0.5).encode(y='n_new_validators:Q')
    st.altair_chart((bar + line).resolve_scale(y='independent').properties(title='Hourly new validators vs LUNA price'))
    


# In[14]:


st.markdown('This dashboard has been done by _Cristina Tintó_ powered by **Flipside Crypto** data and carried out for **MetricsDAO**.')
st.markdown('All the codes can be found in [Github](https://github.com/cristinatinto/terra-price-run-investigation-)')


# In[ ]:




