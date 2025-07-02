import pandas as pd
import streamlit as st
import plotly.express as px
import datetime
from datetime import date, timedelta

#dicionario de cores
cores_personalizadas = {
    'MB': '#2E86AB',         # azul elegante para a Mb
    'MEC': '#A569BD',
    'MA': '#F1C40F',
    'Financeiro': '#16A085',
    'Comercial': '#E67E22'
    # inclua outras áreas conforme necessário
}

# === Configura a página ===
st.set_page_config(layout="wide")

# === Carrega os dados ===
df = pd.read_excel('ferias.xlsx')
df['Inicio_Ferias'] = pd.to_datetime(df['Inicio_Ferias'])
df['Fim_Ferias'] = df['Inicio_Ferias'] + pd.to_timedelta(df['Dias'], unit='d')

# === Define datas padrão com base na data atual ===
hoje = date.today()
inicio_padrao = hoje - timedelta(days=15)
fim_padrao = hoje + timedelta(days=30)

min_data = df['Inicio_Ferias'].min().date()
max_data = df['Fim_Ferias'].max().date()

# === Sidebar: filtros ===
st.sidebar.header("Filtros")

# Filtro por nome
nomes = df['Nome'].unique()
nome_selecionado = st.sidebar.selectbox("Colaborador", ["Todos"] + list(nomes))

# Filtro por área
areas = df['Area'].unique()
area_selecionada = st.sidebar.selectbox("Área", ["Todas"] + list(areas))

# Filtro por período com calendários
data_inicio_sel = st.sidebar.date_input("Data inicial", value=inicio_padrao, min_value=min_data, max_value=max_data)
data_fim_sel = st.sidebar.date_input("Data final", value=fim_padrao, min_value=min_data, max_value=max_data)

# Conversão para datetime
periodo_inicio = pd.to_datetime(data_inicio_sel)
periodo_fim = pd.to_datetime(data_fim_sel)

# Verificação de validade
if periodo_fim < periodo_inicio:
    st.sidebar.error("🚫 A data final não pode ser anterior à data inicial!")
    st.stop()

# Seletor de critério de ordenação
criterio_ordenacao = st.sidebar.selectbox(
    "Ordenar eixo Y por",
    options=["Data de início", "Nome", "Área"]
)

# === Aplica os filtros ===
df_filtrado = df.copy()
if nome_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Nome'] == nome_selecionado]
if area_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Area'] == area_selecionada]

df_filtrado = df_filtrado[
    (df_filtrado['Inicio_Ferias'] <= periodo_fim) &
    (df_filtrado['Fim_Ferias'] >= periodo_inicio)
]

# Aplica ordenação
if criterio_ordenacao == "Data de início":
    df_filtrado = df_filtrado.sort_values(by="Inicio_Ferias")
elif criterio_ordenacao == "Nome":
    df_filtrado = df_filtrado.sort_values(by="Nome")
elif criterio_ordenacao == "Área":
    df_filtrado = df_filtrado.sort_values(by=["Area", "Inicio_Ferias"])

# === Gráfico de Gantt ===
fig = px.timeline(
    df_filtrado,
    x_start="Inicio_Ferias",
    x_end="Fim_Ferias",
    y="Nome",
    color="Area",
    title=None,
    category_orders={"Nome": df_filtrado["Nome"].tolist()},
    color_discrete_map=cores_personalizadas

)
fig.update_yaxes(autorange=True)

fig.update_layout(
    xaxis=dict(
        title=None,
        range=[periodo_inicio, periodo_fim],
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=0.5,
        tickformat="%d/%m",
        dtick="86400000",
        ticklabelmode="period",
        tickangle=90
    )
)

# === Adiciona faixas de fim de semana ===
data = periodo_inicio
while data <= periodo_fim:
    if data.weekday() == 5:  # sábado
        fig.add_vrect(
            x0=data,
            x1=data + datetime.timedelta(days=2),
            fillcolor="lightblue",
            opacity=0.2,
            layer="below",
            line_width=0,
        )
    data += datetime.timedelta(days=1)

# === Exibe no Streamlit ===
st.title('Dashboard de Férias')
st.plotly_chart(fig, use_container_width=True)
