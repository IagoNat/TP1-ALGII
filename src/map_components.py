import dash_leaflet as dl
from dash import html
from .comida_di_buteco import gerar_marcadores_comida_di_buteco

def gerar_marcadores(df):
  marcadores = []
  for _, row in df.iterrows():
    marcador = dl.Marker(
      position=(row['LAT'], row['LON']),
      children=[
        dl.Tooltip(row['NOME'] if row['NOME'] else "Sem nome"),
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
    marcadores.append(marcador)
  return marcadores

def carregar_geojson_bairros(caminho_geojson="assets/bairros_bh.geojson"):
  import json
  with open(caminho_geojson, "r", encoding="utf-8") as f:
    return json.load(f)

def construir_layout_mapa(df_bares, geojson_bairros, bares_comida_di_buteco):
  return html.Div([dl.Map(
      center=[-19.92, -43.94], zoom=13,
      children=[
        dl.TileLayer(),
        dl.GeoJSON(
          data=geojson_bairros,
          id="geojson-bairros",
          options=dict(style=dict(color="red", weight=2, opacity=0.5))
        ),
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
        dl.LayerGroup(id="layer-marcadores", 
          children=gerar_marcadores(df_bares) + gerar_marcadores_comida_di_buteco(bares_comida_di_buteco))
    ],
    style={'width': '100%', 'height': '600px'},
    id='map'
  )], style={
    'border': '1px solid #cccccc',
    'borderRadius': '8px',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
    'marginBottom': '20px',
    'backgroundColor': '#ffffff',
    'padding': '10px'
  })