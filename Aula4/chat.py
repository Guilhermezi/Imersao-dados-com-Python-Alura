import streamlit as st
import pandas as pd
import plotly.express as px

# === Configurações iniciais da página ===
st.set_page_config(
    page_title="Dashboard Salários Área de Dados - Guilherme Izidio",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Título e descrição na página principal ===
st.title("💼 Dashboard Salarial na Área de Dados")
st.markdown(
    """
    Bem-vindo(a) ao dashboard interativo de análise salarial na área de dados!  
    Use os filtros no menu lateral para explorar dados salariais, tipos de contrato, senioridade, localização e muito mais.  
    Desenvolvido por **Guilherme Izidio**.
    """
)

# === Carregamento dos dados ===
@st.cache_data(ttl=3600)
def carregar_dados():
    url = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
    df = pd.read_csv(url)
    return df

df = carregar_dados()

# === Filtros na sidebar ===
st.sidebar.header("🔎 Filtros personalizados")

# Função para criar multiselect com default completo
def filtro_multiselect(label, df_col):
    opcoes = sorted(df_col.unique())
    return st.sidebar.multiselect(label, opcoes, default=opcoes)

anos_selecionados = filtro_multiselect("Ano", df['ano'])
senioridades_selecionadas = filtro_multiselect("Senioridade", df['senioridade'])
contratos_selecionados = filtro_multiselect("Tipo de Contrato", df['contrato'])
tamanhos_selecionados = filtro_multiselect("Tamanho da Empresa", df['tamanho_empresa'])

# Filtragem do DataFrame
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# === KPIs principais ===
st.subheader("📊 Métricas Principais")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_medio = salario_maximo = 0
    total_registros = 0
    cargo_mais_frequente = "–"

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Salário Médio (USD)", f"${salario_medio:,.0f}")
col2.metric("📈 Salário Máximo (USD)", f"${salario_maximo:,.0f}")
col3.metric("📋 Total de Registros", f"{total_registros:,}")
col4.metric("🏆 Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")

# === Visualizações ===
st.subheader("📈 Visualizações Interativas")

# Gráfico 1: Top 10 cargos por salário médio
with st.expander("Ver Top 10 cargos por salário médio"):
    if not df_filtrado.empty:
        top_cargos = (
            df_filtrado.groupby('cargo')['usd']
            .mean()
            .nlargest(10)
            .sort_values()
            .reset_index()
        )
        fig_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            labels={'usd': 'Salário médio anual (USD)', 'cargo': ''},
            title="Top 10 cargos por salário médio"
        )
        fig_cargos.update_layout(title_x=0.05, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_cargos, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para o gráfico de cargos.")

# Gráfico 2: Distribuição de salários
with st.expander("Ver distribuição dos salários anuais"):
    if not df_filtrado.empty:
        fig_dist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            labels={'usd': 'Faixa salarial (USD)', 'count': 'Contagem'},
            title="Distribuição de salários anuais"
        )
        fig_dist.update_layout(title_x=0.05)
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para o gráfico de distribuição.")

# Gráfico 3: Proporção dos tipos de trabalho (Remoto vs Presencial)
with st.expander("Ver proporção dos tipos de trabalho"):
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['Tipo de Trabalho', 'Quantidade']
        fig_remoto = px.pie(
            remoto_contagem,
            names='Tipo de Trabalho',
            values='Quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        fig_remoto.update_traces(textinfo='percent+label')
        fig_remoto.update_layout(title_x=0.05)
        st.plotly_chart(fig_remoto, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para o gráfico de tipos de trabalho.")

# Gráfico 4: Salário médio de Data Scientist por país
with st.expander("Ver salário médio de Data Scientist por país"):
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        if not df_ds.empty:
            media_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
            fig_pais = px.choropleth(
                media_pais,
                locations='residencia_iso3',
                color='usd',
                color_continuous_scale='RdYlGn',
                title='Salário médio de Cientista de Dados por país',
                labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'}
            )
            fig_pais.update_layout(title_x=0.05)
            st.plotly_chart(fig_pais, use_container_width=True)
        else:
            st.info("Nenhum dado para Cientista de Dados nesta seleção.")
    else:
        st.info("Nenhum dado disponível para o gráfico por país.")

st.markdown("---")

# === Tabela detalhada ===
st.subheader("📋 Tabela de Dados Detalhados")
st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)

# === Rodapé ===
st.markdown(
    """
    ---
    <p style="text-align:center; font-size:12px; color:gray;">
    Desenvolvido por <strong>Guilherme Izidio</strong> &nbsp;&middot;&nbsp; 
    Dados: https://github.com/vqrca/dashboard_salarios_dados
    </p>
    """,
    unsafe_allow_html=True
)
