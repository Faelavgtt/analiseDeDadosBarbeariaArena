import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# lendo os arquivos exportados do sistema
df1 = pd.read_csv('comandas_fev_mar.csv')
df2 = pd.read_csv('comandas_abr_mai.csv')
df3 = pd.read_csv('comandas_jun_jul.csv')
df4 = pd.read_csv('comandas_ago_set.csv')
df5 = pd.read_csv('comandas_out_nov.csv')

# juntando tudo
df = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)

# tirando as colunas inuteis que vem do sistema (Info, Ver, Cancelar e Cartão vazio)
df = df[['Comanda', 'Data', 'Valor', 'Cliente', 'Obs', 'Cadastrou', 'Profissional']]

# removendo comandas repetidas (pq na virada de um arquivo pro outro as vezes repete o dia)
df = df.drop_duplicates(subset=['Comanda'])

print("Total de atendimentos:", len(df))

# arrumando o valor pra numero
df['Valor'] = df['Valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
df['Valor'] = pd.to_numeric(df['Valor'])

# arrumando a data
df['Data_dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y %H:%M')
df['Hora'] = df['Data_dt'].dt.hour
df['Dia_num'] = df['Data_dt'].dt.day_of_week

dias = {
    0: 'Segunda',
    1: 'Terça',
    2: 'Quarta',
    3: 'Quinta',
    4: 'Sexta',
    5: 'Sábado',
    6: 'Domingo'
}
df['Dia_Semana'] = df['Dia_num'].map(dias)

# separando por turno/periodo pra ver se manha ou tarde é mais vazio
def pegar_periodo(h):
    if h < 12:
        return 'Manhã (08h-12h)'
    elif h < 18:
        return 'Tarde (12h-18h)'
    else:
        return 'Noite (18h+)'

df['Periodo'] = df['Hora'].apply(pegar_periodo)

# limpando o "+ 1" que aparece no nome do barbeiro as vezes
df['Profissional'] = df['Profissional'].astype(str).str.replace(' + 1', '', regex=False)

# print(df.head())

ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

print("\n--- ATENDIMENTOS POR DIA DA SEMANA ---")
por_dia = df['Dia_Semana'].value_counts().reindex(ordem_dias)
print(por_dia)

print("\n--- ATENDIMENTOS POR PERIODO (MANHA / TARDE / NOITE) ---")
tabela_periodo = pd.crosstab(df['Dia_Semana'], df['Periodo']).reindex(ordem_dias)
print(tabela_periodo)

print("\n--- ATENDIMENTOS POR HORA ---")
df_hora = df[(df['Hora'] >= 9) & (df['Hora'] <= 19)]
por_hora = df_hora['Hora'].value_counts().sort_index()
print(por_hora)


# GRAFICO 1 - Atendimentos por dia
plt.figure(figsize=(8, 5))
plt.bar(por_dia.index, por_dia.values, color='steelblue')
plt.title('Atendimentos por Dia da Semana')
plt.xlabel('Dia')
plt.ylabel('Quantidade')
for i, v in enumerate(por_dia.values):
    plt.text(i, v + 10, str(v), ha='center')
plt.ylim(0, 750)
plt.savefig('graficos/atendimentos_dia_semana.png')
plt.close()

# GRAFICO 2 - Movimento por hora
plt.figure(figsize=(9, 5))
plt.plot(por_hora.index, por_hora.values, marker='o', color='darkblue')
plt.title('Atendimentos por Horário (9h às 19h)')
plt.xlabel('Hora do dia')
plt.ylabel('Quantidade de clientes')
plt.xticks(por_hora.index, [f"{h}h" for h in por_hora.index])
plt.grid(True)
plt.savefig('graficos/movimento_por_horario.png')
plt.close()

# GRAFICO 3 - Mapa de calor Dia x Hora
cruzamento = pd.crosstab(df_hora['Dia_Semana'], df_hora['Hora']).reindex(ordem_dias)
plt.figure(figsize=(10, 6))
sns.heatmap(cruzamento, cmap='YlOrRd', annot=True, fmt='d')
plt.title('Mapa de Calor - Dia da Semana x Horário')
plt.xlabel('Hora')
plt.ylabel('Dia')
plt.savefig('graficos/mapa_calor_horarios.png')
plt.close()

# GRAFICO 4 - Comparacao Manha vs Tarde por dia
plt.figure(figsize=(9, 5))
sns.countplot(data=df, x='Dia_Semana', hue='Periodo', order=ordem_dias, palette='Set2')
plt.title('Movimento por Período em cada Dia da Semana')
plt.xlabel('Dia da Semana')
plt.ylabel('Atendimentos')
plt.savefig('graficos/atendimentos_por_periodo.png')
plt.close()

print("\nPronto! Graficos salvos na pasta graficos/")
