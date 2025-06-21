import json
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def geocodificar_dataframe(df, cache_path="cache/cache_geocode.json", get=0):
  try:
    with open(cache_path, "r", encoding="utf-8") as f:
      cache = json.load(f)  
  except FileNotFoundError:
    cache = {}

  geolocator = Nominatim(user_agent="pbh_geocodificacao")
  geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

  for idx, row in df.iterrows():
    endereco = row['ENDERECO']
    coords = None
    if endereco in cache:
      coords = cache[endereco]
    elif get:
      try:
        location = geocode(endereco)
        if location:
          coords = {'LATITUDE': location.latitude, 'LONGITUDE': location.longitude}
        else:
          coords = {'LATITUDE': None, 'LONGITUDE': None}
      except:
        coords = {'LATITUDE': None, 'LONGITUDE': None}
      cache[endereco] = coords
      time.sleep(1)
    if coords:
      df.at[idx, 'LATITUDE'] = coords['LATITUDE']
      df.at[idx, 'LONGITUDE'] = coords['LONGITUDE']

  with open(cache_path, "w", encoding="utf-8") as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

  return df