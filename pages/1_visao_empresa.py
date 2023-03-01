'''pip install haversine
pip install pandas
pip install numpy
pip install plotly
pip install folium'''
import os
import pandas as pd
import numpy as np
import re
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
#from utils import clean_code

st.set_page_config(page_title = 'Visão Empresa', layout = 'wide')

#-----------------------------------------------------------------
# Funções
#-----------------------------------------------------------------
def country_maps( df1 ):
    df_aux = (df1.loc[:,['ID', 'City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
              .groupby(['City', 'Road_traffic_density'])
              .median()
              .reset_index() )
    map = folium.Map()

    for index, location in df_aux.iterrows():
        folium.Marker( [location['Delivery_location_latitude'],
                        location['Delivery_location_longitude']],
                        popup = location[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width = 800, height = 600)
    return None


def order_share_by_week( df1 ):
    # Quantidade de pedidos por semana/ Número único de entregadores por semana
    df_aux1 = df1.loc[:, ['ID', 'Order_Week']].groupby('Order_Week').count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'Order_Week']].groupby('Order_Week').nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, how = 'inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x = 'Order_Week', y = 'order_by_deliver')
            
    return fig
        

def order_by_week( df1 ):
    #criando coluna de semanas
    df1['Order_Week'] = df1['Order_Date'].dt.strftime('%U')
    #selecionando colunas
    cols = ['ID', 'Order_Week']
    #calculando quantidade de pedidos por semana
    df_aux = df1.loc[:, cols].groupby('Order_Week').count().reset_index()
    #gráfico de linhas
    fig = px.line(df_aux, x='Order_Week', y = 'ID')
        
    return fig
    
    

def traffic_order_city( df1 ):
    df_aux = df1.loc[:,['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig
        
        

def traffic_order_share( df1 ):
    df_aux = df1.loc[:,['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.bar(df_aux, x = 'Road_traffic_density', y = 'entregas_perc')
            
    return fig

        

def order_metric( df1 ):
    cols = ['ID', 'Order_Date']
        
    #seleção de linhas
    df_aux = df1.loc[:,cols].groupby('Order_Date').count().reset_index()

    #gráfico de barras
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
            
    return fig



def clean_code(df1):
    """Esta função tem a responsabilidade de limpar o DataFrame
    
    Tipos de limpeza:
    
    1. Remoção dos dados NaN
    2. Mudança do tipo da coluna de dados
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna de data
    5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
    
    Input: DataFrame
    Outpoot: DataFrame
    
    """
    #Convertendo a coluna Age de texto para número

    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #Convertendo a coluna Ratings de texto para float

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #Convertendo a coluna Date de texto para data

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y')

    #Convertendo a coluna Multiple de texto para int

    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #Limpando espaços vazios dentro de strings
    #df1 = df1.reset_index(drop = True)
    #for i in range(len(df1)):
      #df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()

    # Limpando espaços vazios dentro de strings
    df1.loc[: , 'ID'] = df1.loc[: , 'ID'].str.strip()
    df1.loc[: , 'Road_traffic_density'] = df1.loc[: , 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[: , 'Type_of_order'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[: , 'Festival'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[: , 'Type_of_vehicle'].str.strip()
    df1.loc[: , 'City'] = df1.loc[: , 'City'].str.strip()

    # Limpando a coluna de time taken

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ') [1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

#------------------------------------------------------------------------
# Início da estrutura lógica do código
#------------------------------------------------------------------------

#Import dataset
df = pd.read_csv('train.csv', encoding='utf-8')

#Limpando os dados
df1 = clean_code(df)


#========================================================================
# SIDEBAR
#========================================================================

st.header('Marketplace - Visão Empresa')

image = Image.open('logo.JPG')
st.sidebar.image(image, width=150)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('# Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Select a limit language')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2023, 4, 13),
    min_value = pd.datetime(2022, 2 , 11),
    max_value = pd.datetime(2022, 4 , 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')


# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

st.dataframe( df1 )

#========================================================================
# STREAMLIT LAYOUT
#========================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        fig = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig, use_container_width=True)
        
        
        
    with st.container():
        col1, col2 = st.columns(2)
        
            
    with col1:
        fig = traffic_order_share( df1 )
        st.header('# Traffic Order Share')
        st.plotly_chart(fig, use_container_width = True, sharing="streamlit", theme=None)
        
        
    with col2:
        st.header("Traffic Order City")
        fig = traffic_order_city( df1 )
        st.plotly_chart(fig, use_container_width=True)
        
                
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week( df1 )
        st.plotly_chart(fig, use_container_width = True)

    
    with st.container():
        st.markdown('# Order  Share by Week')
        fig = order_share_by_week( df1 )
        st.plotly_chart(fig, use_container_width = True)

                
                
with tab3:
    st.markdown('# Country Maps')
    country_maps( df1 )
