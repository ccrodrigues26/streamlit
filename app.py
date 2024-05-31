import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import os
import subprocess

st.title('Informações de Vendas')

DATE_COLUMN='ORDERDATE'

file_path = 'sales_data_sample.csv'
df = pd.read_csv(file_path, encoding='latin1')
df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN]) 

if st.checkbox('Mostrar Dados'):     
    st.write(df)

if st.checkbox('Estatísticas'):     
    st.write(df.describe())

if st.checkbox('Tipo Colunas'):     
    st.write(df.dtypes)

if st.checkbox('Valores Ausentes'):   
    st.write(df.isnull().sum())
    

if st.checkbox('Gráficos'): 
    st.subheader('Vendas por Dia')
    selecione_mes = st.selectbox("Selecione o mês:", sorted(df['ORDERDATE'].dt.strftime('%m').unique()))
    filtered_data = df[df['ORDERDATE'].dt.strftime('%m') == selecione_mes]
    sales_by_day = filtered_data.groupby(filtered_data['ORDERDATE'].dt.day)['SALES'].sum().reset_index()  
    chart = alt.Chart(sales_by_day).mark_bar().encode(
    x='ORDERDATE:O',
    y='SALES:Q',
    tooltip=['ORDERDATE:O', 'SALES:Q']
    ).properties(
        width=800,
        height=400
    ).interactive()  
    st.write(chart)
    
    st.subheader('Vendas por Mes')
    selecione_Ano = st.selectbox("Selecione o mês:", sorted(df['ORDERDATE'].dt.strftime('%Y').unique()))
    filtered_data = df[df['ORDERDATE'].dt.strftime('%Y') == selecione_Ano]
    sales_by_mes = filtered_data.groupby(filtered_data['ORDERDATE'].dt.month)['SALES'].sum().reset_index()   
    chart = alt.Chart(sales_by_mes).mark_bar().encode(
    x='ORDERDATE:O',
    y='SALES:Q',
    tooltip=['ORDERDATE:O', 'SALES:Q']
    ).properties(
        width=800,
        height=400
    ).interactive()    
    st.write(chart)
    

    st.subheader('Vendas por Ano/Pais')
    df['YEAR'] = df['ORDERDATE'].dt.year
    sales_by_country_year = df.groupby(['COUNTRY', 'YEAR'])['SALES'].sum().reset_index()
    chart = alt.Chart(sales_by_country_year).mark_bar().encode(
    x='YEAR:N',
    y='SALES:Q',
    color='COUNTRY:N',
    tooltip=['COUNTRY:N', 'SALES:Q']
    ).properties(
    width=800,
    height=400
    ).interactive()

    st.write(chart)
    
    
    st.subheader('Vendas por Ano-Mês')
    # Criar uma nova coluna 'YEAR_MONTH' que combina Ano e Mês
    df['YEAR_MONTH'] = df['ORDERDATE'].dt.to_period('M')

    # Agrupar os dados por 'YEAR_MONTH' e calcular a soma das vendas
    sales_by_month = df.groupby('YEAR_MONTH')['SALES'].sum().reset_index()

    # Converter 'YEAR_MONTH' de volta para datetime para melhor compatibilidade com Altair
    sales_by_month['YEAR_MONTH'] = sales_by_month['YEAR_MONTH'].dt.to_timestamp()

    # Criar gráfico de linhas com Altair
    chart = alt.Chart(sales_by_month).mark_line().encode(
    x='YEAR_MONTH:T',
    y='SALES:Q',
    tooltip=['YEAR_MONTH:T', 'SALES:Q']
    ).properties(
    width=800,
    height=400
    ).interactive()

    # Exibir gráfico
    st.write(chart)
    
    
    st.subheader('Vendas por País')
    # Extrair o ano da coluna ORDERDATE
    df['YEAR'] = df['ORDERDATE'].dt.year

    # Agrupar os dados por país e ano e calcular a soma das vendas
    sales_by_country_year = df.groupby(['COUNTRY', 'YEAR'])['SALES'].sum().reset_index()

    # Criar seletor de ano incluindo a opção "Todos"
    years = sorted(sales_by_country_year['YEAR'].unique())
    years.insert(0, 'Todos')
    selected_year = st.selectbox("Selecione o ano:", years)

    # Filtrar os dados pelo ano selecionado ou usar todos os anos
    if selected_year == 'Todos':
        filtered_data = sales_by_country_year.groupby('COUNTRY')['SALES'].sum().reset_index()
    else:
        filtered_data = sales_by_country_year[sales_by_country_year['YEAR'] == selected_year]

    # Ordenar os dados por volume de vendas e determinar os 10 principais países
    top_10_countries = filtered_data.nlargest(10, 'SALES')

    # Determinar os países restantes e somar suas vendas
    other_countries_sales = filtered_data[~filtered_data['COUNTRY'].isin(top_10_countries['COUNTRY'])]['SALES'].sum()

    # Adicionar uma linha para "Other" no DataFrame
    other_row = pd.DataFrame([{'COUNTRY': 'Outros', 'SALES': other_countries_sales}])
    final_data = pd.concat([top_10_countries, other_row], ignore_index=True)

    # Criar gráfico de pizza com Altair
    chart = alt.Chart(final_data).mark_arc().encode(
        theta=alt.Theta(field='SALES', type='quantitative'),
        color=alt.Color(field='COUNTRY', type='nominal'),
        tooltip=['COUNTRY', 'SALES']
    ).properties(
        width=600,
        height=400
    )
    # Exibir gráfico
    st.altair_chart(chart, use_container_width=True)
    