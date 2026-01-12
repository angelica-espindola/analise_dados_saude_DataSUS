import pandas as pd

# Ler todas as abas de cada planilha 

# Internações
xls_internacoes = pd.ExcelFile("dados_tratados/tabela_internacoes.xlsx")
dfs_internacoes = [pd.read_excel(xls_internacoes, sheet_name=sheet) for sheet in xls_internacoes.sheet_names]

# Óbitos
xls_obitos = pd.ExcelFile("dados_tratados/tabela_obitos.xlsx")
dfs_obitos = [pd.read_excel(xls_obitos, sheet_name=sheet) for sheet in xls_obitos.sheet_names]

# Conferir nomes das abas
print("Abas internações:", xls_internacoes.sheet_names)
print("Abas óbitos:", xls_obitos.sheet_names)

# Concatenar abas de cada tipo de evento
df_internacoes = pd.concat(dfs_internacoes, ignore_index=True)
df_obitos = pd.concat(dfs_obitos, ignore_index=True)

# Unir internações e óbitos
df_final = pd.concat([df_internacoes, df_obitos], ignore_index=True)

# Corrigir tipo da coluna Ano 
df_final['Ano'] = df_final['Ano'].astype(int) 

# Padronizar nomes das colunas (minúsculas e sem espaço)
df_final.columns = df_final.columns.str.strip().str.lower().str.replace(" ", "_")

# Padronizar o tipo de evento (primeira letra maiúscula, restante minúscula)
if 'tipo_evento' in df_final.columns:
    df_final['tipo_evento'] = df_final['tipo_evento'].str.strip().str.lower().str.capitalize()

# Verificar e tratar valores nulos 
# Substituir valores nulos em colunas numéricas por 0
colunas_numericas = ['masculino', 'feminino', 'total']
for col in colunas_numericas:
    if col in df_final.columns:
        df_final[col] = df_final[col].fillna(0)

# Substituir valores nulos em colunas de texto por string vazia
colunas_texto = ['cidade', 'tipo_evento', 'lista_morbidade_cid']
for col in colunas_texto:
    if col in df_final.columns:
        df_final[col] = df_final[col].fillna('')

# Remover duplicados 
df_final = df_final.drop_duplicates()

# Remover a coluna 'total' antes de salvar
if 'total' in df_final.columns:
    df_final = df_final.drop(columns=['total'])

# Conferir dados finais
print("Dimensão da base final:", df_final.shape)
print("Colunas:", df_final.columns.tolist())
print("Primeiras linhas:\n", df_final.head())
print("Resumo estatístico:\n", df_final[['masculino', 'feminino']].describe())

# Salvar tabela final sem a coluna 'total'
df_final.to_excel("dados_tratados/base_final_sus.xlsx", index=False)
print("Base final salva sem a coluna 'total' como 'base_final_sus.xlsx'")


import pandas as pd

# Carregar base final tratada
df = pd.read_excel("dados_tratados/base_final_sus.xlsx")

# Padronizar colunas só para garantir
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Agrupar por cidade e tipo de evento
totais_cidade = (
    df.groupby(['cidade', 'tipo_evento'])[['masculino', 'feminino']]
    .sum()
    .reset_index()
)

# Adicionar coluna de total calculado
totais_cidade['total'] = totais_cidade['masculino'] + totais_cidade['feminino']

# Mostrar resultado
print(totais_cidade)


# Filtrar óbitos e agrupar por cidade e CID
obitos_por_cidade = (
    df[df['tipo_evento'] == 'Óbito']
    .groupby(['cidade', 'lista_morbidade_cid'])[['masculino', 'feminino']]
    .sum()
    .reset_index()
)

# Calcular total por causa
obitos_por_cidade['total'] = obitos_por_cidade['masculino'] + obitos_por_cidade['feminino']

# Para Campo Grande, mostrar top 5 causas
top5_cg = obitos_por_cidade[obitos_por_cidade['cidade'] == 'Campo Grande'] \
    .sort_values('total', ascending=False).head(5)

print("Top 5 causas de óbito em Campo Grande:")
print(top5_cg[['lista_morbidade_cid', 'total']])

# Para Ponta Porã, mostrar top 5 causas
top5_pp = obitos_por_cidade[obitos_por_cidade['cidade'] == 'Ponta Porã'] \
    .sort_values('total', ascending=False).head(5)

print("\nTop 5 causas de óbito em Ponta Porã:")
print(top5_pp[['lista_morbidade_cid', 'total']])
