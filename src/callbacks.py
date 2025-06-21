import dash
from dash.dependencies import Input, Output
import dash_leaflet as dl
import pandas as pd
from src.kd_tree import search_range
from src.map_components import gerar_marcadores
from src.comida_di_buteco import gerar_marcadores_comida_di_buteco

def registrar_callbacks(app, df_bares, arvore_kd, df_buteco, arvore_kd_buteco):
  @app.callback(
    Output("edit-control", "editToolbar"),
    Input("reset-button", "n_clicks")
  )
  def trigger_action(n_clicks):
    return dict(mode="remove", action="clear all", n_clicks=n_clicks)

  @app.callback(
    [Output("layer-marcadores", "children"),
     Output("tabela-estabelecimentos", "data"),
     Output("tabela-estabelecimentos", "filter_query")],
    [Input("edit-control", "geojson"),
     Input("reset-button", "n_clicks")],
    prevent_initial_call=True
  )
  def atualizar_visualizacao(geojson, n_clicks):
    ctx = dash.callback_context

    marcadores_normais = gerar_marcadores(df_bares)
    marcadores_buteco = gerar_marcadores_comida_di_buteco(df_buteco)

    if ctx.triggered and ctx.triggered[0]['prop_id'].startswith("reset-button"):
      return marcadores_buteco + marcadores_normais, df_bares.to_dict('records') + df_buteco.to_dict('records'), ''

    if not geojson or not geojson.get("features"):
      return marcadores_buteco + marcadores_normais, df_bares.to_dict('records') + df_buteco.to_dict('records'), ''

    try:
      geometry = [f["geometry"] for f in geojson["features"]]
      coords = [g["coordinates"][0] for g in geometry]

      resultados_bares = []
      resultados_buteco = []
      for coord in coords:
        lats = [lat for lon, lat in coord]
        lons = [lon for lon, lat in coord]
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)

        resultados_bares.extend(search_range(arvore_kd.root, lat_min, lat_max, lon_min, lon_max))
        resultados_buteco.extend(search_range(arvore_kd_buteco.root, lat_min, lat_max, lon_min, lon_max))
      df_filtrado_bares = pd.DataFrame(resultados_bares)
      df_filtrado_buteco = pd.DataFrame(resultados_buteco)

      return gerar_marcadores(df_filtrado_bares) + gerar_marcadores_comida_di_buteco(df_filtrado_buteco), df_filtrado_bares.to_dict('records') + df_filtrado_buteco.to_dict('records'), ''
    except Exception as e:
      print("Erro ao processar seleção:", e)
      return gerar_marcadores(df_bares), df_bares.to_dict('records'), ''
