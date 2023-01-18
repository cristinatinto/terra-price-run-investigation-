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
st.set_page_config(page_title="Terra in 2023", layout="wide",initial_sidebar_state="collapsed")



# In[2]:


import time
my_bar = st.progress(0)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1)


# In[5]:


st.title('Terra New Year New Activity')
st.write('')
st.markdown('The holidays and New Year are often chaotic in the crypto and DEFI space, as users make a spree of new transactions and wallets as they receive (and give) some cash and coins as holiday gifts.')
st.markdown(' The idea of this work is to try to respond if this flurry of winter activity has impacted the Terra ecosystem, if users are creating new wallets or buying tokens with their newfound holiday wealth.')
st.write('This dashboard comprehens the following sections:')
st.markdown('1. Terra main activity comparison before and after holidays')
st.markdown('2. Terra supply before and after holidays')
st.markdown('3. Terra development before and after holidays')
st.markdown('4. Terra staking activity before and after holidays')
st.write('')
st.subheader('1. Terra main activity')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the activity of Terra ecosystem during this past month. More specifically, we will analyze the following data:')
st.markdown('● Total number transactions')
st.markdown('● Total active users')
st.markdown('● Total volume moved')
st.write('')

sql="""
with txns as(
select 
  date_trunc('day',block_timestamp) as date,
  count(distinct tx_id) as n_txns,
  count(distinct tx_sender) as n_wallets,
  sum(fee) as fee_luna
from terra.core.fact_transactions
  where block_timestamp >= '2022-12-08' and block_timestamp <= '2023-01-08'
group by date
order by date desc
),
new_wallets as (
select 
  date,
  count(tx_sender) as n_new_wallets
  from (
select 
  date_trunc('day',min(block_timestamp)) as date,
  tx_sender
from terra.core.fact_transactions
group by tx_sender
)
  where date >= '2022-12-08' and date <= '2023-01-08'
group by date
)

select 
  t.*,
    case when t.date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
  n.n_new_wallets,
  sum(n_new_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_wallets
from txns t left join new_wallets n using(date)
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
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_txns:Q',color='period')
        .properties(title='Daily transactions evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_txns:Q',color='period')
        .properties(title='Transactions comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_wallets:Q',color='period')
        .properties(title='Daily active wallets evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_wallets:Q',color='period')
        .properties(title='Active wallets comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='fee_luna:Q',color='period')
        .properties(title='Daily fees evolution',))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='fee_luna:Q',color='period')
        .properties(title='Fees comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_new_wallets:Q',color='period')
        .properties(title='Daily new users evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_new_wallets:Q',color='period')
        .properties(title='New users comparison'))
    
    


# In[7]:


st.subheader("2. Supply before and after holidays")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the LUNA supply. More specifically, we will analyze the following data:')
st.markdown('● $LUNA supply')
st.markdown('● Circulating supply')



sql="""
--credits: adriaparcerisas
with SEND as 
(select SENDER,
  sum(AMOUNT) as sent_amount
from 
terra.core.ez_transfers
WHERE
CURRENCY ilike 'uluna'
group by SENDER
  ),
  
RECEIVE as 
(select RECEIVER,
  sum(AMOUNT) as received_amount
from 
terra.core.ez_transfers
WHERE
CURRENCY ilike 'uluna'
group by RECEIVER
  ),
total_supp as (select sum(received_amount)/1e4 as total_supply 
  from RECEIVE r 
  left join SEND s on r.RECEIVER=s.SENDER 
  where sent_amount is null),
t1 as
(select date_trunc('day',BLOCK_TIMESTAMP) as date,
sum(case when FROM_CURRENCY ilike 'uluna' then FROM_AMOUNT/1e6 else null end) as from_amountt,
sum(case when to_CURRENCY ilike 'uluna' then FROM_AMOUNT/1e6 else null end) as to_amountt,
from_amountt-to_amountt as circulating_volume
from
  terra.core.ez_swaps
group by 1
), 
  t3 as (select 
sum(circulating_volume) over (order by date) as circulating_supply ,
  DATE from t1
  )
select total_supply,circulating_supply,  circulating_supply*100/total_supply as ratio 
  from t3 join total_supp
where 
date=CURRENT_DATE-30
    """

sql2="""
--credits: adriaparcerisas
with SEND as 
(select SENDER,
  sum(AMOUNT) as sent_amount
from 
terra.core.ez_transfers
WHERE
CURRENCY ilike 'uluna'
group by SENDER
  ),
  
RECEIVE as 
(select RECEIVER,
  sum(AMOUNT) as received_amount
from 
terra.core.ez_transfers
WHERE
CURRENCY ilike 'uluna'
group by RECEIVER
  ),
total_supp as (select sum(received_amount)/1e4 as total_supply 
  from RECEIVE r 
  left join SEND s on r.RECEIVER=s.SENDER 
  where sent_amount is null),
t1 as
(select date_trunc('day',BLOCK_TIMESTAMP) as date,
sum(case when FROM_CURRENCY ilike 'uluna' then FROM_AMOUNT/1e6 else null end) as from_amountt,
sum(case when to_CURRENCY ilike 'uluna' then FROM_AMOUNT/1e6 else null end) as to_amountt,
from_amountt-to_amountt as circulating_volume
from
  terra.core.ez_swaps
group by 1
), 
  t3 as (select 
sum(circulating_volume) over (order by date) as circulating_supply ,
  DATE from t1
  )
select total_supply,circulating_supply,  circulating_supply*100/total_supply as ratio 
  from t3 join total_supp
where 
date=CURRENT_DATE-1

"""

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

with st.expander("Check the analysis"):
    col1,col2=st.columns(2)
    with col1:
        st.metric('Total supply before holidays',df['total_supply'])
    col2.metric('Total supply after holidays',df2['total_supply'])
    
    col1,col2=st.columns(2)

    with col1:
        st.metric('Circulating supply before holidays',df['circulating_supply'])
    col2.metric('Circulating supply after holidays',df2['circulating_supply'])
    
    col1,col2=st.columns(2)
    with col1:
        st.metric('Ratio before holidays',df['ratio'])
    col2.metric('Ratio after holidays',df2['ratio'])
    
    


# In[8]:


st.subheader("3. Ecosystem development before and after holidays")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the Terra main ecosystem development. More specifically, we will analyze the following data:')
st.markdown('● New deployed contracts')
st.markdown('● Used contracts')
st.markdown('● Swaps activity')



sql="""
select 
   date_trunc('day',block_timestamp) as date,    
   case when date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
  count(distinct tx_id) as n_contracts,
  sum(n_contracts) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_contracts
from terra.core.ez_messages
where message_type = '/cosmwasm.wasm.v1.MsgInstantiateContract'
	and block_timestamp >= '2022-12-08' and block_timestamp <= '2023-01-08'
group by date, period
order by date desc


"""


sql2="""
select 
   date_trunc('day',block_timestamp) as date,
      case when date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
  count(distinct tx:body:messages[0]:contract) as n_contracts,
    sum(n_contracts) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_contracts
  from terra.core.fact_transactions 
  --where ATTRIBUTE_KEY in ('contract','u_contract_address','contract_name',
  --'contract_version','contract_addr','contract_address','dao_contract_address','pair_contract_addr','nft_contract')
  where block_timestamp >= '2022-12-08' and block_timestamp <= '2023-01-08'

group by date, period
order by date desc
"""


sql3="""
with txns as(
select 
  date_trunc('day',block_timestamp) as date,
      case when date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
  count(distinct tx_id) as n_txns,
  count(distinct trader) as n_wallets,
  sum(to_amount/1e6) as fee_luna,
  sum(n_txns) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_txns,
  sum(n_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_wallets,
  sum(fee_luna) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_fee_luna
from terra.core.ez_swaps
  where block_timestamp >= '2022-12-08' and block_timestamp <= '2023-01-08'
  and to_currency = 'uluna'
group by date, period
order by date desc
),
new_wallets as (
select 
  date,
  count(trader) as n_new_wallets
  from (
select 
  date_trunc('day',min(block_timestamp)) as date,
  trader
from terra.core.ez_swaps
group by trader
)
   where date >= '2022-12-08' and date <= '2023-01-08'
group by date
)

select 
  t.*,
  n.n_new_wallets,
  sum(n_new_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_wallets
from txns t left join new_wallets n using(date)
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
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_contracts:Q',color='period')
        .properties(title='Daily new contracts evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_contracts:Q',color='period')
        .properties(title='New contracts comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='date:N', y='n_contracts:Q',color='period')
        .properties(title='Daily active contracts evolution'))
    
    col2.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='period:N', y='n_contracts:Q',color='period')
        .properties(title='Active contracts comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_txns:Q',color='period')
        .properties(title='Daily swaps evolution'))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_txns:Q',color='period')
        .properties(title='Swaps comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_wallets:Q',color='period')
        .properties(title='Daily active swappers evolution'))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_wallets:Q',color='period')
        .properties(title='Active swappers comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='fee_luna:Q',color='period')
        .properties(title='Daily swap fees evolution'))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='fee_luna:Q',color='period')
        .properties(title='Swap fees comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_new_wallets:Q',color='period')
        .properties(title='Daily new swappers evolution'))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_new_wallets:Q',color='period')
        .properties(title='New swappers comparison'))
    


# In[9]:


st.subheader("3. Staking before and after holidays")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the Terra staking. More specifically, we will analyze the following data:')
st.markdown('● Staking actions')
st.markdown('● Stakers')
st.markdown('● Validators')



sql="""
--credits: cryptolcicle
with txns as(
select 
  date_trunc('day',block_timestamp) as date,
      case when date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
  count(distinct tx_id) as n_txns,
  count(distinct delegator_address) as n_wallets,
  count(distinct validator_address) as n_validators,
  sum(amount/1e6) as fee_luna,
  sum(n_txns) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_txns,
  sum(n_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_wallets,
  sum(fee_luna) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_fee_luna
from terra.core.ez_staking
  where action = 'Delegate'
  and block_timestamp >= '2022-12-08' and block_timestamp <= '2023-01-08'
group by date, period
order by date desc
),
new_wallets as (
select 
  date,
  count(delegator_address) as n_new
  from (
select 
  date_trunc('day',min(block_timestamp)) as date,
  delegator_address
from terra.core.ez_staking
group by delegator_address
)
  where date >= '2022-12-08' and date <= '2023-01-08'
group by date
),
new_validators as (
select 
  date,
  count(validator_address) as n_new
  from (
select 
  date_trunc('day',min(block_timestamp)) as date,
  validator_address
from terra.core.ez_staking
group by validator_address
)
  where date >= '2022-12-08' and date <= '2023-01-08'
group by date
)

select 
  t.*,
  coalesce(n.n_new, 0) as n_new_wallets,
  sum(n_new_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_wallets,
  coalesce(v.n_new, 0) as n_new_validators,
  sum(n_new_validators) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_validators
from txns t 
  left join new_wallets n using(date)
  left join new_validators v using(date)
order by date desc
"""



results = memory(sql)
df = pd.DataFrame(results.records)
df.info()



with st.expander("Check the analysis"):
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_txns:Q',color='period')
        .properties(title='Daily staking actions evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_txns:Q',color='period')
        .properties(title='Staking actions comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_wallets:Q',color='period')
        .properties(title='Daily active stakers evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_wallets:Q',color='period')
        .properties(title='Active stakers comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_validators:Q',color='period')
        .properties(title='Daily validators evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_validators:Q',color='period')
        .properties(title='Active validators comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='fee_luna:Q',color='period')
        .properties(title='Daily staking fees evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='fee_luna:Q',color='period')
        .properties(title='Staking fees comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_new_wallets:Q',color='period')
        .properties(title='Daily new stakers evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_new_wallets:Q',color='period')
        .properties(title='New stakers comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_new_validators:Q',color='period')
        .properties(title='Daily new validators evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_new_validators:Q',color='period')
        .properties(title='New validators comparison'))
    


# In[14]:


st.markdown('This dashboard has been done by _Cristina Tintó_ powered by **Flipside Crypto** data and carried out for **MetricsDAO**.')


# In[ ]:




