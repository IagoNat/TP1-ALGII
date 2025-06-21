import pandas as pd
import dash
from dash import html, dash_table, dcc
from src.preprocessing import filtrar_estabelecimentos, montar_endereco, preparar_dados
from src.geocode import geocodificar_dataframe
from src.kd_tree import gerar_estrutura_kdtree, gerar_estrutura_kdtree_buteco
from src.map_components import construir_layout_mapa, carregar_geojson_bairros
from src.callbacks import registrar_callbacks
from src.comida_di_buteco import carregar_bares_comida_di_buteco
NUMERO_DE_BARES = 100 # Até 5120

# 1. Carregar dados
# caminho_csv = "./data/20250401_atividade_economica.csv"
# df_raw = pd.read_csv(caminho_csv, sep=";", encoding="utf-8")
# df_filtrado = filtrar_estabelecimentos(df_raw)
# df_filtrado['ENDERECO'] = df_filtrado.apply(montar_endereco, axis=1)
df_buteco = carregar_bares_comida_di_buteco()

# 2. Geocodificar
# geocodificar_dataframe(df_filtrado)

# 3. Processar e refinar colunas
df_filtrado = pd.read_csv("./data/bares_restaurantes_geocodificados.csv", sep=",", encoding="utf-8")
df_bares = preparar_dados(df_filtrado)
df_bares = df_bares.sample(n=NUMERO_DE_BARES)

# 4. Construir KDTrees
arvore_kd = gerar_estrutura_kdtree(df_bares)
arvore_kd_buteco = gerar_estrutura_kdtree_buteco(df_buteco)

# 5. Iniciar app Dash
app = dash.Dash(__name__)
server = app.server

# 6. Layout
geojson_bairros = carregar_geojson_bairros()
mapa = construir_layout_mapa(df_bares, geojson_bairros, df_buteco)

tabela = dash_table.DataTable(
  id='tabela-estabelecimentos',
  columns=[
    {'name': 'Nome', 'id': 'NOME'},
    {'name': 'Endereço', 'id': 'ENDERECO'},
    {'name': 'Data de Início', 'id': 'DATA_INICIO'},
    {'name': 'Alvará', 'id': 'ALVARA'}
  ],
  data=df_bares.to_dict('records') + df_buteco.to_dict('records'),
  style_table={
    'minHeight': '300px',
    'height': '500px',
    'overflowY': 'auto'
  },
  style_header={
      'backgroundColor': '#e0e0e0',
      'fontWeight': 'bold',
      'textAlign': 'left',
      'padding': '10px'
  },
  style_cell={
      'padding': '8px',
      'whiteSpace': 'normal',
      'textAlign': 'left',
      'fontSize': '14px'
  },
  page_action='none',
  sort_action='native',
  filter_action='native'
)

botao = html.Button("Resetar Filtro", id="reset-button", n_clicks=0, style={
    'backgroundColor': '#1976d2',
    'color': 'white',
    'border': 'none',
    'padding': '10px 20px',
    'fontSize': '14px',
    'borderRadius': '5px',
    'cursor': 'pointer',
    'margin': '10px 0'
})


app.layout = html.Div(
  style={
    'fontFamily': 'Segoe UI, sans-serif',
    'backgroundColor': '#f9f9f9',
    'padding': '20px'
  },
  children=[
  dcc.Store(
    id="dados-originais",
    data=df_bares.to_dict('records') + df_buteco.to_dict('records')
  ),
  html.H1("Visualização de Bares e Restaurantes - BH", style={
      "textAlign": "center",
      "color": "#333333"
  }),
  mapa,
  html.Br(),
  botao,
  html.Br(),
  tabela
])

# 7. Callbacks
registrar_callbacks(app, df_bares, arvore_kd, df_buteco, arvore_kd_buteco)

# 8. Run
if __name__ == '__main__':
    app.run(debug=True)
