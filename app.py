import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.preprocessing import MinMaxScaler



# Carregar dados tratados

@st.cache_data
def load_data():
    df = pd.read_excel("dados_tratados/base_final_sus.xlsx")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    # Padronizar valores da coluna tipo_evento
    df['tipo_evento'] = df['tipo_evento'].str.strip().str.lower().replace({
        'internação': 'Internação',
        'internacao': 'Internação',
        'óbito': 'Óbito',
        'obito': 'Óbito'
    })
    return df

df = load_data()


# Título do dashboard

st.title("Análise de Dados Públicos de Saúde de Campo Grande - MS e Ponta Porã - MS")

st.markdown(
    "Fonte dos dados: **Sistema de Informações de Saúde – DataSUS, TabNet**. "
    "Acesso em: Dezembro/2025. "
    "Disponível em: [http://tabnet.datasus.gov.br](http://tabnet.datasus.gov.br)"
)

st.markdown("Dados coletados de Janeiro a Outubro dos anos de 2024 e 2025.")



# Filtro por cidade

cidade = st.selectbox("Selecione a cidade:", sorted(df['cidade'].unique()))
df_cidade = df[df['cidade'] == cidade]
st.write(f"### Dados da cidade: {cidade}")


# Gráfico 1: Internações e Óbitos por Sexo

# Agrupar dados por tipo de evento e sexo, reorganizando para o gráfico
sexo_evento = (
    df_cidade.groupby('tipo_evento')[['masculino', 'feminino']]
    .sum()
    .reset_index()
    .melt('tipo_evento', ['masculino', 'feminino'], 'Sexo', 'Total')
)

fig_sexo = px.bar(
    sexo_evento,
    x='tipo_evento',
    y='Total',
    color='Sexo',
    barmode='group',
    title=f"Internações e Óbitos por Sexo — {cidade}",
    labels={'tipo_evento':'Tipo de Evento', 'Total':'Número de Casos', 'Sexo':'Sexo'},
    color_discrete_map={'masculino':'#1f77b4', 'feminino':'#ff7f0e'}  # azul e laranja
)
st.plotly_chart(fig_sexo, use_container_width=True)

st.write("🔹 Observação: A maioria das internações está concentrada entre mulheres, enquanto os óbitos estão concentrados entre homens, em ambas cidades.")


# Gráfico 2: Proporção de Internações vs Óbitos

# Agrupar e calcular total de casos por tipo de evento
totais_tipo = (
    df_cidade.groupby('tipo_evento')[['masculino', 'feminino']]
    .sum()
    .reset_index()
)
totais_tipo['total'] = totais_tipo[['masculino', 'feminino']].sum(axis=1)

# Padronizar labels para gráfico de pizza
totais_tipo['evento_label'] = totais_tipo['tipo_evento'].str.lower().replace({
    'internação': 'Internação',
    'internacao': 'Internação',
    'óbito': 'Óbito',
    'obito': 'Óbito'
})

fig_totais = px.pie(
    totais_tipo,
    names='evento_label',
    values='total',
    title=f"Proporção de Internações e Óbitos — {cidade}",
    hole=0.4,
    category_orders={'evento_label': ['Internação', 'Óbito']}
)

st.plotly_chart(fig_totais, use_container_width=True)

st.write("🔹 Observação: Internações representam a maior parte dos casos, enquanto os óbitos são menos frequentes, indicando que a maioria dos pacientes recebe tratamento hospitalar com sucesso.")


# Tabela resumida por tipo de evento e sexo

st.write("### Resumo de Internações e Óbitos por Sexo")
st.dataframe(sexo_evento.pivot(index='tipo_evento', columns='Sexo', values='Total'))


# Fim do dashboard

st.markdown("Fonte: **DataSUS 2024-2025**")


# Ranking de Causas por Cidade

st.write(f"### Ranking de causas de internações e óbitos para {cidade}")

# Internações
internacoes_cid = (
    df_cidade[df_cidade['tipo_evento'] == 'Internação']
    .groupby('lista_morbidade_cid')[['masculino','feminino']]
    .sum()
    .reset_index()
)
internacoes_cid['total'] = internacoes_cid[['masculino','feminino']].sum(axis=1)
internacoes_cid = internacoes_cid.sort_values('total', ascending=False).head(10)

fig_internacoes = px.bar(
    internacoes_cid,
    x='total',
    y='lista_morbidade_cid',
    orientation='h',
    title=f"Top 10 Causas de Internação — {cidade}",
    labels={'lista_morbidade_cid':'CID / Morbidade', 'total':'Número de Internações'},
    color_discrete_sequence=['#1f77b4']  # azul
)
fig_internacoes.update_layout(yaxis={'categoryorder':'total descending'})
st.plotly_chart(fig_internacoes, use_container_width=True)

# Comentário abaixo do gráfico
st.write("🔹 Observação: As principais causas de internação na cidade estão concentradas nestas morbidades, permitindo identificar áreas prioritárias de atenção à saúde.")

# Óbitos
obitos_cid = (
    df_cidade[df_cidade['tipo_evento'] == 'Óbito']
    .groupby('lista_morbidade_cid')[['masculino','feminino']]
    .sum()
    .reset_index()
)
obitos_cid['total'] = obitos_cid[['masculino','feminino']].sum(axis=1)
obitos_cid = obitos_cid.sort_values('total', ascending=False).head(10)

fig_obitos = px.bar(
    obitos_cid,
    x='total',
    y='lista_morbidade_cid',
    orientation='h',
    title=f"Top 10 Causas de Óbito — {cidade}",
    labels={'lista_morbidade_cid':'CID / Morbidade', 'total':'Número de Óbitos'},
    color_discrete_sequence=['#d62728'] 
)
fig_obitos.update_layout(yaxis={'categoryorder':'total descending'})
st.plotly_chart(fig_obitos, use_container_width=True)

# Comentário abaixo do gráfico
st.write("🔹 Observação: As principais causas de óbito na cidade indicam os problemas de saúde mais críticos e onde políticas públicas podem ser direcionadas.")



# Comparativo das 5 principais causas de Internações e Óbitos entre cidades


st.write("### Comparativo das 5 Principais Causas de Internações entre Cidades")

# Internações
internacoes_top = (
    df[df['tipo_evento'] == 'Internação']
    .groupby(['cidade', 'lista_morbidade_cid'])[['masculino','feminino']]
    .sum()
    .reset_index()
)
internacoes_top['total'] = internacoes_top[['masculino','feminino']].sum(axis=1)

# Selecionar top 5 causas considerando todas as cidades juntas
top5_internacoes = internacoes_top.groupby('lista_morbidade_cid')['total'].sum().sort_values(ascending=False).head(5).index
internacoes_top = internacoes_top[internacoes_top['lista_morbidade_cid'].isin(top5_internacoes)]

# Gráfico de barras
fig_internacoes_comp = px.bar(
    internacoes_top,
    x='total',
    y='lista_morbidade_cid',
    color='cidade',
    barmode='group',
    orientation='h',
    title="Top 5 Causas de Internação — Comparativo entre Cidades",
    labels={'lista_morbidade_cid':'CID / Morbidade', 'total':'Número de Internações', 'cidade':'Cidade'},
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_internacoes_comp.update_layout(yaxis={'categoryorder':'total descending'})
st.plotly_chart(fig_internacoes_comp, use_container_width=True)
st.write("🔹 Observação:As cinco principais causas de internação em ambas as cidades são: fratura de ossos, parto único espontâneo, pneumonia, trauma múltiplo e catarata. Campo Grande apresenta muito mais internações em todas essas causas, indicando maior demanda hospitalar. Já Ponta Porã tem menos casos, mas as causas principais são semelhantes, mostrando perfis de saúde parecidos.")


st.write("### Comparativo das 5 Principais Causas de Óbitos entre Cidades")

# Óbitos
obitos_top = (
    df[df['tipo_evento'] == 'Óbito']
    .groupby(['cidade', 'lista_morbidade_cid'])[['masculino','feminino']]
    .sum()
    .reset_index()
)
obitos_top['total'] = obitos_top[['masculino','feminino']].sum(axis=1)

# Selecionar top 5 causas considerando todas as cidades juntas
top5_obitos = obitos_top.groupby('lista_morbidade_cid')['total'].sum().sort_values(ascending=False).head(5).index
obitos_top = obitos_top[obitos_top['lista_morbidade_cid'].isin(top5_obitos)]

# Gráfico de barras
fig_obitos_comp = px.bar(
    obitos_top,
    x='total',
    y='lista_morbidade_cid',
    color='cidade',
    barmode='group',
    orientation='h',
    title="Top 5 Causas de Óbito — Comparativo entre Cidades",
    labels={'lista_morbidade_cid':'CID / Morbidade', 'total':'Número de Óbitos', 'cidade':'Cidade'},
    color_discrete_sequence=px.colors.qualitative.Set1
)
fig_obitos_comp.update_layout(yaxis={'categoryorder':'total descending'})
st.plotly_chart(fig_obitos_comp, use_container_width=True)
st.write("🔹 Observação: Em Campo Grande, as mortes são majoritariamente por doenças infecciosas, com Pneumonia liderando, seguida de outras infecções bacterianas e problemas respiratórios e urinários. Em Ponta Porã, Pneumonia também é a principal causa, mas há maior diversidade de causas, incluindo Septicemia, doenças respiratórias, problemas vasculares cerebrais e transtornos metabólicos. Isso indica que, enquanto Pneumonia é um desafio comum, Ponta Porã requer estratégias de saúde pública mais amplas devido à variedade de fatores de risco.")



# MODELAGEM DE RISCO EPIDEMIOLÓGICO (IRE)

st.markdown("---")
st.write("## 🚦 Índice de Risco Epidemiológico (IRE)")
st.write(
    "Classificação das causas (CID) segundo nível de risco epidemiológico, "
    "com base em indicadores históricos de frequência, letalidade e "
    "vulnerabilidade por sexo."
)


# Base para modelagem


df_modelo = df[df['cidade'] == cidade]

# Remover eventos assistenciais não associados a risco epidemiológico
df_modelo = df_modelo[
    ~df_modelo['lista_morbidade_cid'].str.contains(
        'parto|anticoncepção|prob part|anomalias cromossômicas', case=False, na=False
    )
]


# Agregar por CID e tipo de evento
modelo = (
    df_modelo
    .groupby(['lista_morbidade_cid', 'tipo_evento'])[['masculino', 'feminino']]
    .sum()
    .reset_index()
)

modelo['total'] = modelo[['masculino', 'feminino']].sum(axis=1)

# Separar internações e óbitos
internacoes = modelo[modelo['tipo_evento'] == 'Internação']
obitos = modelo[modelo['tipo_evento'] == 'Óbito'][['lista_morbidade_cid', 'total']]

# Unir bases
base_risco = internacoes.merge(
    obitos,
    on='lista_morbidade_cid',
    how='left',
    suffixes=('_internacoes', '_obitos')
)

base_risco['total_obitos'] = base_risco['total_obitos'].fillna(0)


# Indicadores epidemiológicos

# Frequência total de casos
base_risco['frequencia'] = (
    base_risco['total_internacoes'] + base_risco['total_obitos']
)

# Letalidade
base_risco['letalidade'] = (
    base_risco['total_obitos'] / base_risco['frequencia']
)

# Vulnerabilidade por sexo
base_risco['dif_sexo'] = (
    abs(base_risco['masculino'] - base_risco['feminino']) / base_risco['frequencia']
)

# Padronização dos indicadores (0 a 1)


scaler = MinMaxScaler()

base_risco[['freq_norm', 'letal_norm', 'sexo_norm']] = scaler.fit_transform(
    base_risco[['frequencia', 'letalidade', 'dif_sexo']]
)


# Índice de Risco Epidemiológico (IRE)

# Ajuste dos pesos: mais peso para frequência, depois letalidade, pouco para sexo
base_risco['IRE'] = (
    0.55 * base_risco['freq_norm'] +   # frequência tem maior influência
    0.35 * base_risco['letal_norm'] +  # letalidade com peso secundário
    0.10 * base_risco['sexo_norm']     # sexo tem menor peso
)

# Classificação do risco
def classificar_risco(ire):
    if ire >= 0.6:
        return 'Alto Risco 🔴'
    elif ire >= 0.3:
        return 'Médio Risco 🟡'
    else:
        return 'Baixo Risco 🟢'

base_risco['nivel_risco'] = base_risco['IRE'].apply(classificar_risco)


# Tabela de risco por CID

st.write(f"### Classificação de Risco Epidemiológico por CID — {cidade}")

st.dataframe(
    base_risco[
        ['lista_morbidade_cid', 'frequencia', 'letalidade', 'IRE', 'nivel_risco']
    ].sort_values('IRE', ascending=False)
)

# Gráfico: Top 10 CIDs por risco


fig_risco = px.bar(
    base_risco.sort_values('IRE', ascending=False).head(10),
    x='IRE',
    y='lista_morbidade_cid',
    color='nivel_risco',
    orientation='h',
    title=f"Top 10 CIDs por Risco Epidemiológico — {cidade}",
    labels={'IRE': 'Índice de Risco Epidemiológico', 'lista_morbidade_cid': 'CID / Morbidade'},
    color_discrete_map={
        'Alto Risco 🔴': '#d62728',
        'Médio Risco 🟡': '#ffbf00',
        'Baixo Risco 🟢': '#2ca02c'
    }
)

fig_risco.update_layout(yaxis={'categoryorder': 'total descending'})
st.plotly_chart(fig_risco, use_container_width=True)

st.write(
    "🔹 Observação: O Índice de Risco Epidemiológico (IRE) combina frequência de casos, "
    "letalidade e vulnerabilidade por sexo. CIDs classificados como alto risco "
    "devem ser priorizados em ações de prevenção, monitoramento e alocação de recursos "
    "na saúde pública."
)

st.markdown("---")
st.markdown("## 🏥 Resumo Final dos Principais Riscos Epidemiológicos")

st.markdown(
    """
    Com base na análise dos dados históricos de saúde pública das cidades, identificamos as principais causas de risco epidemiológico que impactam a população local. 
    Essas informações são fundamentais para orientar ações preventivas, políticas públicas e cuidados individuais.
    """
)


st.markdown("### 🦠 Doenças Infecciosas e Bacterianas")
st.markdown(
    """
    - Pneumonia, septicemia, leishmaniose e outras infecções representam riscos médios com alta letalidade potencial.  
    - A prevenção inclui vacinação, higiene adequada e acesso rápido a serviços de saúde.
    """
)

st.markdown("### 🎗️ Neoplasias Malignas (Cânceres Diversos)")
st.markdown(
    """
    - Incluem cânceres do encéfalo, próstata, traqueia, pâncreas, órgãos digestivos e genitais femininos.  
    - São causas frequentes e de alto impacto, reforçando a importância de diagnóstico precoce, programas de rastreamento e tratamento especializado.
    """
)

st.markdown("### 🦴 Fraturas de Ossos dos Membros")
st.markdown(
    """
    - Alta frequência de internações devido a traumas e acidentes, incluindo acidentes de trânsito.  
    - Campanhas de prevenção no trânsito, uso de equipamentos de segurança e melhorias no atendimento emergencial são essenciais para reduzir esses casos.
    """
)

st.markdown("### 🧠 Acidente Vascular Cerebral (AVC) e ❤️ Infarto Agudo do Miocárdio (IAM)")
st.markdown(
    """
    **Acidente Vascular Cerebral (AVC)**  
    - Condição grave que impacta significativamente a mortalidade e a qualidade de vida.  
    - Controle rigoroso dos fatores de risco, como hipertensão e diabetes, é crucial.  

    **Infarto Agudo do Miocárdio (IAM)**  
    - Condição grave que afeta diretamente a mortalidade cardiovascular.  
    - Controle de fatores de risco como hipertensão, diabetes, colesterol elevado e tabagismo é essencial.  
    - Intervenções rápidas, como atendimento emergencial e tratamento médico adequado, podem salvar vidas.
    """
)


st.markdown("### 💡 Recomendações para a População")
st.markdown(
    """
    - Adotar hábitos de vida saudáveis: alimentação equilibrada, exercícios regulares, evitar tabaco e álcool em excesso.  
    - Realizar acompanhamento médico preventivo e buscar atendimento rápido para sinais de infecção ou sintomas graves.  
    - Praticar prevenção de acidentes, redobrar a atenção no trânsito e utilizar equipamentos de proteção em trabalhos de risco.
    """
)

st.markdown(
    """
    🔹 Este resumo ajuda a população e gestores a compreenderem os desafios locais de saúde, priorizando ações que salvam vidas e promovem o bem-estar.
    """
)
