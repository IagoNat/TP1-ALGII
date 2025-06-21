import overpy
import geojson

api = overpy.Overpass()

query = """
[out:json][timeout:50];
area["name"="Belo Horizonte"]["boundary"="administrative"]->.a;
(
  relation["admin_level"="10"]["type"="boundary"](area.a);
);
out body;
>;
out skel qt;
"""

result = api.query(query)

features = []

for rel in result.relations:
    coordinates = []
    for member in rel.members:
        if isinstance(member, overpy.RelationWay):
            coords = [(float(n.lon), float(n.lat)) for n in member.resolve().nodes]
            if coords:
                coordinates.append(coords)

    if coordinates:
        geometry = geojson.MultiLineString(coordinates)
        feature = geojson.Feature(geometry=geometry, properties={"name": rel.tags.get("name", "")})
        features.append(feature)

geojson_data = geojson.FeatureCollection(features)

with open("bairros_bh.geojson", "w", encoding="utf-8") as f:
    geojson.dump(geojson_data, f, ensure_ascii=False, indent=2)
