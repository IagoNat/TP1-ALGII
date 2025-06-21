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
    else:
      self.root = self.build(points_with_data, depth)

  def build(self, points_with_data, depth):
    if not points_with_data:
      return None
    axis = depth % 2
    points_with_data.sort(key=lambda x: x[0][axis])
    median = len(points_with_data) // 2
    point, data = points_with_data[median]
    return KDNode(
      point,
      data,
      self.build(points_with_data[:median], depth + 1),
      self.build(points_with_data[median + 1:], depth + 1)
    )

def search_range(node, lat_min, lat_max, lon_min, lon_max, depth=0, resultados=None):
  if node is None:
    return resultados if resultados is not None else []

  if resultados is None:
    resultados = [] 

  lat, lon = node.point
  axis = depth % 2

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

def gerar_estrutura_kdtree_buteco(df):
  points_with_data = []
  for _, row in df.iterrows():
    ponto = (row['LAT'], row['LON'])
    dados = {
      'NOME': row['NOME'],
      'ENDERECO': row['ENDERECO'],
      'PETISCO': row['PETISCO'],
      'DESCRICAO': row['DESCRICAO'],
      'LAT': row['LAT'],
      'LON': row['LON'],
      'DATA_INICIO': '',
      'ALVARA': ''
    }
    points_with_data.append((ponto, dados))
  return KDTree(points_with_data)