import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import sqlite3
import pandas as pd

# Criar o aplicativo Dash
app = dash.Dash(__name__)

# Função para carregar os dados do banco SQLite
def load_data_from_db():
    conn = sqlite3.connect('inflacao.db')
    query = "SELECT * FROM ipca"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Carregar dados iniciais
df = load_data_from_db()

# Remover os dados da linha "Ano" para gráficos mensais
df_mensal = df[df['mes'] != 'Ano']

# Layout do Dash
app.layout = html.Div([
    html.H1('Dashboard de Inflação (IPCA)', style={'textAlign': 'center'}),
    
    # Filtros
    html.Div([
        html.Label('Selecione o Ano:'),
        dcc.Dropdown(
            id='ano-dropdown',
            options=[{'label': str(ano), 'value': ano} for ano in sorted(df['ano'].unique())],
            value=df['ano'].min(),  # Valor inicial
            style={'width': '48%', 'display': 'inline-block'}
        ),
        
        html.Label('Selecione o Mês:'),
        dcc.Dropdown(
            id='mes-dropdown',
            options=[{'label': mes, 'value': mes} for mes in df_mensal['mes'].unique()],
            value=None,  # Todos os meses por padrão
            multi=True,  # Permite selecionar múltiplos meses
            style={'width': '48%', 'display': 'inline-block'}
        ),
    ], style={'padding': '20px'}),
    
    # Gráfico de Inflação Mensal
    dcc.Graph(id='grafico-ipca'),
    
    # Gráfico de Acumulado Anual
    dcc.Graph(id='grafico-acumulado-anual'),
])

# Função callback para atualizar o gráfico mensal
@app.callback(
    Output('grafico-ipca', 'figure'),
    [Input('ano-dropdown', 'value'),
     Input('mes-dropdown', 'value')]
)
def update_mensal_graph(ano, meses):
    # Filtrar os dados com base no ano e mês
    filtered_df = df_mensal[df_mensal['ano'] == ano]
    
    if meses:
        filtered_df = filtered_df[filtered_df['mes'].isin(meses)]
    
    # Criar o gráfico com Plotly Express
    fig = px.line(
        filtered_df, x='mes', y='indice',
        title=f'IPCA Mensal para o Ano {ano}',
        labels={'indice': 'Índice de Inflação (%)', 'mes': 'Mês'},
        markers=True
    )
    
    # Configurações do gráfico
    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Índice de Inflação (%)',
        template='plotly_dark'
    )
    
    return fig

# Função callback para o gráfico de acumulado anual
@app.callback(
    Output('grafico-acumulado-anual', 'figure'),
    [Input('ano-dropdown', 'value')]
)
def update_acumulado_graph(ano):
    # Filtrar o acumulado anual
    filtered_df = df[df['mes'] == 'Ano']
    filtered_df = filtered_df[filtered_df['ano'] == ano]
    
    # Criar o gráfico de barras para o acumulado anual
    fig = px.bar(
        filtered_df, x='ano', y='indice',
        title=f'IPCA Acumulado Anual ({ano})',
        labels={'indice': 'Índice Acumulado (%)', 'ano': 'Ano'},
        text='indice'
    )
    
    # Configurações do gráfico
    fig.update_layout(
        xaxis_title='Ano',
        yaxis_title='Índice Acumulado (%)',
        template='plotly_dark'
    )
    
    return fig

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
