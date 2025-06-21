import pandas as pd
import time
import json
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm
import dash
from dash import html, dcc, dash_table
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.dependencies import Output, Input, State

# ------------------ Pré-processamento ------------------

def filtragem_dos_dados(df):
  termos_alvo = [
    "RESTAURANTES E SIMILARES",
    "LANCHONETES, CASAS DE CHÁ, DE SUCOS E SIMILARES",
    "BARES E OUTROS ESTABELECIMENTOS ESPECIALIZADOS EM SERVIR BEBIDAS, SEM ENTRETENIMENTO",
    "BARES E OUTROS ESTABELECIMENTOS ESPECIALIZADOS EM SERVIR BEBIDAS, COM ENTRETENIMENTO",
    "SERVIÇOS AMBULANTES DE ALIMENTAÇÃO",
    "CANTINAS - SERVIÇOS DE ALIMENTAÇÃO PRIVATIVOS",
    "SERVIÇOS DE ALIMENTAÇÃO PARA EVENTOS E RECEPÇÕES - BUFÊ"
  ]

  df['DESCRICAO_CNAE_PRINCIPAL'] = df['DESCRICAO_CNAE_PRINCIPAL'].str.strip()
  df_bares_restaurantes = df[
      df['DESCRICAO_CNAE_PRINCIPAL'].str.upper().isin(termos_alvo)
  ].copy()

  return df_bares_restaurantes

def montar_endereco(row):
  logradouro = f"{row['DESC_LOGRADOURO']} {row['NOME_LOGRADOURO']}".strip()
  numero = str(row['NUMERO_IMOVEL']).strip()
  complemento = str(row['COMPLEMENTO']).strip() if pd.notnull(row['COMPLEMENTO']) else ""
  bairro = row['NOME_BAIRRO'].strip()

  endereco = f"{logradouro}, {numero}"
  if complemento:
      endereco += f", {complemento}"
  endereco += f", {bairro}, BELO HORIZONTE, MG, BRASIL"
  return endereco

def geocodificacao(df_bares_restaurantes, p=1):
  try:
    with open("cache_geocode.json", "r", encoding="utf-8") as f:
      cache = json.load(f)
  except FileNotFoundError:
    cache = {}

  geolocator = Nominatim(user_agent="pbh_geocodificacao")
  geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

  if 'LATITUDE' not in df_bares_restaurantes.columns:
    df_bares_restaurantes['LATITUDE'] = None
    df_bares_restaurantes['LONGITUDE'] = None

  if p:
    def pegar_latitude(endereco):
      return cache[endereco]["LATITUDE"] if endereco in cache else None

    def pegar_longitude(endereco):
      return cache[endereco]["LONGITUDE"] if endereco in cache else None

    df_bares_restaurantes['LATITUDE'] = df_bares_restaurantes['ENDERECO'].apply(pegar_latitude)
    df_bares_restaurantes['LONGITUDE'] = df_bares_restaurantes['ENDERECO'].apply(pegar_longitude)
  else:
    salvar_a_cada = 100
    contador = 0
    for idx, row in tqdm(df_bares_restaurantes.iterrows(), total=len(df_bares_restaurantes)):
      endereco = row['ENDERECO']
      if endereco in cache:
        coords = cache[endereco]
      else:
        try:
          location = geocode(endereco)
          if location:
            coords = {'LATITUDE': location.latitude, 'LONGITUDE': location.longitude}
          else:
            coords = {'LATITUDE': None, 'LONGITUDE': None}
        except:
          coords = {'LATITUDE': None, 'LONGITUDE': None}
        cache[endereco] = coords
        contador += 1

      df_bares_restaurantes.at[idx, 'LATITUDE'] = coords['LATITUDE']
      df_bares_restaurantes.at[idx, 'LONGITUDE'] = coords['LONGITUDE']

      if contador >= salvar_a_cada:
        with open("cache_geocode.json", "w", encoding="utf-8") as f:
          json.dump(cache, f, ensure_ascii=False, indent=2)
        df_bares_restaurantes.to_csv("bares_restaurantes_geocodificados.csv", index=False)
        contador = 0

    with open("cache_geocode.json", "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    df_bares_restaurantes.to_csv("bares_restaurantes_geocodificados.csv", index=False)

def processamento_dos_dados(df):
  df_bares_restaurantes = filtragem_dos_dados(df)

  df_bares_restaurantes['ENDERECO'] = df_bares_restaurantes.apply(montar_endereco, axis=1)

  geocodificacao(df_bares_restaurantes)

  df_bares_restaurantes = df_bares_restaurantes.dropna(subset=['LATITUDE', 'LONGITUDE'])
  
  df_bares_restaurantes = df_bares_restaurantes.copy()
  
  df_bares_restaurantes["NOME_EXIBIDO"] = df_bares_restaurantes["NOME_FANTASIA"].combine_first(df_bares_restaurantes["NOME"])
  
  colunas_finais = [
    'NOME_EXIBIDO', 'ENDERECO', 'DATA_INICIO_ATIVIDADE', 'IND_POSSUI_ALVARA', 'LATITUDE', 'LONGITUDE']
  
  df_bares_restaurantes = df_bares_restaurantes[colunas_finais]
  
  df_bares_restaurantes = df_bares_restaurantes.rename(columns={
    'NOME_EXIBIDO': 'NOME',
    'ENDERECO': 'ENDERECO',
    'DATA_INICIO_ATIVIDADE': 'DATA_INICIO',
    'IND_POSSUI_ALVARA': 'ALVARA',
    'LATITUDE': 'LAT',
    'LONGITUDE': 'LON'
  })
  
  return df_bares_restaurantes.reset_index(drop=True)

# ------------------ k-d Tree ------------------

class KDNode:
  def __init__(self, point, data, left=None, right=None):
    self.point = point
    self.data = data
    self.left = left
    self.right = right

class KDTree:
  def __init__(self, points_with_data, depth=0):
    if not points_with_data:
      self.root = None
      return
    self.root = self.build(points_with_data, depth)

  def build(self, points_with_data, depth):
    if not points_with_data:
      return None
    k = 2
    axis = depth % k
    points_with_data.sort(key=lambda x: x[0][axis])
    median = len(points_with_data) // 2
    point, data = points_with_data[median]
    left = self.build(points_with_data[:median], depth + 1)
    right = self.build(points_with_data[median + 1:], depth + 1)
    return KDNode(point, data, left, right)

def search_range(node, lat_min, lat_max, lon_min, lon_max, depth=0, resultados=None):
  if node is None:
    return []
  if resultados is None:
    resultados = []
  lat, lon = node.point
  k = 2
  axis = depth % k
  if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
    resultados.append(node.data)
  if axis == 0:
    if lat >= lat_min:
      search_range(node.left, lat_min, lat_max, lon_min, lon_max, depth + 1, resultados)
    if lat <= lat_max:
      search_range(node.right, lat_min, lat_max, lon_min, lon_max, depth + 1, resultados)
  else:
    if lon >= lon_min:
      search_range(node.left, lat_min, lat_max, lon_min, lon_max, depth + 1, resultados)
    if lon <= lon_max:
      search_range(node.right, lat_min, lat_max, lon_min, lon_max, depth + 1, resultados)
  return resultados

def gerar_estrutura_kdtree(df):
  points_with_data = []
  for _, row in df.iterrows():
    ponto = (row['LAT'], row['LON'])
    dados = {
      'NOME': row['NOME'],
      'ENDERECO': row['ENDERECO'],
      'DATA_INICIO': row['DATA_INICIO'],
      'ALVARA': row['ALVARA'],
      'LAT': row['LAT'],
      'LON': row['LON']
    }
    points_with_data.append((ponto, dados))
  return KDTree(points_with_data)

# ------------------ Dash + Mapa ------------------

df_bares = None
arvore_kd = None

def gerar_marcadores(df):
  marcadores = []
  for _, row in df.iterrows():
    marker = dl.Marker(
      position=(row['LAT'], row['LON']),
      children=[
        dl.Tooltip(row['NOME'] if pd.notnull(row['NOME']) else "Sem nome"),
        dl.Popup([
          html.B(row['NOME']),
          html.Br(),
          row['ENDERECO'],
          html.Br(),
          f"Alvará: {row['ALVARA']}",
          html.Br(),
          f"Início: {row['DATA_INICIO']}"
        ])
      ]
    )
    marcadores.append(marker)
  return marcadores

def construir_app():
  app = dash.Dash(__name__)
  server = app.server
  BH_CENTER = [-19.92, -43.94]
  ZOOM = 13

  with open("bairros_bh.geojson", "r", encoding="utf-8") as f:
    geojson_bairros = json.load(f)
  
  app.layout = html.Div([
    html.H1("Visualização de Bares e Restaurantes - BH", style={"textAlign": "center"}),
    html.Div([
      html.Div(style={'padding': '10px'}, children=[
        dl.Map(center=BH_CENTER, zoom=ZOOM, children=[
          dl.TileLayer(),
          dl.GeoJSON(data=geojson_bairros, id="geojson-bairros", options=dict(style=dict(color="red", weight=2, opacity=0.5))),
          dl.FeatureGroup(id="drawn-features", children=[
            dl.EditControl(
              id="edit-control",
              draw={
                "rectangle": True, 
                "marker": False, 
                "polygon": False, 
                "circle": False, 
                "circlemarker": False, 
                "polyline": False
              },
              edit={"edit": False, "remove": True},
              drawToolbar=True
            )
          ]),
          dl.LayerGroup(id="layer-marcadores", children=gerar_marcadores(df_bares))
        ], style={'width': '100%', 'height': '600px'}, id='map'),
        html.Br(),
        html.Button("Resetar Filtro", id="reset-button", n_clicks=0),
      ]),
      html.Div(style={'padding': '10px'}, children=[
        dash_table.DataTable(
          id='tabela-estabelecimentos',
          columns=[
            {'name': 'Nome', 'id': 'NOME'},
            {'name': 'Endereço', 'id': 'ENDERECO'},
            {'name': 'Data de Início', 'id': 'DATA_INICIO'},
            {'name': 'Alvará', 'id': 'ALVARA'}
          ],
          data=df_bares.to_dict('records'),
          style_cell_conditional=[
            {
              'if': {'column_id': 'ALVARA'},
              'minWidth': '50px',
              'maxWidth': '60px',
              'whiteSpace': 'normal'
            }
          ],
          style_table={
            'minHeight': '300px',
            'height': '500px',
            'overflowY': 'auto',
            'overflowX': 'hidden',
            'tableLayout': 'fixed'
          },
          style_header={
            'whiteSpace': 'normal',
            'height': 'auto',
            'fontWeight': 'bold',
            'textAlign': 'left'
          },
          style_cell={
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'height': 'auto',
            'maxWidth': '200px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'overflowWrap': 'break-word'
          },
          page_action='none',
          sort_action='native',
          filter_action='native'
        )
      ])
    ])
  ])

  return app

# ------------------ Callback ------------------

def registrar_callbacks(app):
  @app.callback(Output("edit-control", "editToolbar"), Input("reset-button", "n_clicks"))
  def trigger_action(n_clicks):
    return dict(mode="remove", action="clear all", n_clicks=n_clicks)

  @app.callback(
    [Output("layer-marcadores", "children"),
    Output("tabela-estabelecimentos", "data")],
    [Input("edit-control", "geojson"),
     Input("reset-button", "n_clicks")],
    prevent_initial_call=True
  )
  def atualizar_visualizacao(geojson, n_clicks):
    ctx = dash.callback_context
    global df_bares, arvore_kd

    if ctx.triggered and ctx.triggered[0]['prop_id'].startswith("reset-button"):
      return gerar_marcadores(df_bares), df_bares.to_dict('records')

    if not geojson or not geojson.get("features"):
      return gerar_marcadores(df_bares), df_bares.to_dict('records')

    try:
      geometry = [f["geometry"] for f in geojson["features"]]
      coords = [g["coordinates"][0] for g in geometry]

      resultados = []
      for coord in coords: 
        lats = [lat for lon, lat in coord]
        lons = [lon for lon, lat in coord]
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)

        resultados.extend(search_range(arvore_kd.root, lat_min, lat_max, lon_min, lon_max))
      df_filtrado = pd.DataFrame(resultados)

      return gerar_marcadores(df_filtrado), df_filtrado.to_dict('records')
    except Exception as e:
      print("Erro ao processar seleção:", e)
      return gerar_marcadores(df_bares), df_bares.to_dict('records')


# ------------------ MAIN ------------------

if __name__ == '__main__':
  df_raw = pd.read_csv("20250401_atividade_economica.csv", sep=";", encoding="utf-8")
  df_bares = processamento_dos_dados(df_raw)
  hold = df_bares
  df_bares = hold.sample(n=120) # n <= 5120
  arvore_kd = gerar_estrutura_kdtree(df_bares)
  app = construir_app()
  registrar_callbacks(app)
  app.run(debug=True)