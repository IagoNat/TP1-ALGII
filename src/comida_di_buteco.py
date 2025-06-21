import json
import time
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import dash_leaflet as dl
from dash import html

def carregar_bares_comida_di_buteco(caminho_arquivo_json="data/bares_comida_di_buteco.json"):
  with open(caminho_arquivo_json, "r", encoding="utf-8") as f:
    bares = json.load(f)

  try:
    with open("cache/cache_geocode_buteco.json", "r", encoding="utf-8") as f:
      cache = json.load(f)
  except FileNotFoundError:
    cache = {}

  geolocator = Nominatim(user_agent="pbh_comida_di_buteco")
  geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

  for bar in bares:
    endereco = bar["ENDERECO"]
    if endereco in cache:
      coords = cache[endereco]
    else:
      try:
        location = geocode(endereco)
        if location:
          coords = {"LATITUDE": location.latitude, "LONGITUDE": location.longitude}
        else:
          coords = {"LATITUDE": None, "LONGITUDE": None}
      except:
        coords = {"LATITUDE": None, "LONGITUDE": None}
      cache[endereco] = coords
      time.sleep(1)

    bar["LAT"] = coords["LATITUDE"]
    bar["LON"] = coords["LONGITUDE"]
      
  with open("cache/cache_geocode_buteco.json", "w", encoding="utf-8") as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

  return pd.DataFrame([bar for bar in bares if bar["LAT"] and bar["LON"]])

def gerar_marcadores_comida_di_buteco(df_bares):
  marcadores = []
  for _, bar in df_bares.iterrows():
    marcador = dl.Marker(
      position=(bar["LAT"], bar["LON"]),
      icon=dict(
        iconUrl="https://cdn-icons-png.flaticon.com/512/3075/3075977.png",
        iconSize=[30, 40]
      ),
      children=[
        dl.Tooltip(
          html.Div([
            html.B(bar["NOME"], style={"color": "blue"}),
            html.Br(),
            html.B(bar["PETISCO"]),
            html.Br(),
            html.Span(bar["DESCRICAO"])
          ], style={
              "whiteSpace": "normal",
              "width": "200px",
              "wordWrap": "break-word", 
              "maxWidth": "300px"        
          }),
          direction="top",
          permanent=False,
          sticky=True
        ),
        dl.Popup([
          html.B(bar["NOME"]),
          html.Br(),
          bar["ENDERECO"],
          html.Br(),
          html.I(bar["PETISCO"]),
          html.Br(),
          bar["DESCRICAO"]
        ])
      ]
    )
    marcadores.append(marcador)
  return marcadores