# 🐼 GeoPandas — Operadores Python

DataFrames geoespaciais: leitura, reprojeção, overlay e exportação de dados vetoriais com interface pandas.

---

## geopandas.read_file

**Assinatura:** `geopandas.read_file(filename, **kwargs)`

Lê qualquer formato vetorial suportado pelo Fiona (SHP, GeoJSON, GPKG, etc) em um GeoDataFrame.

**Tags:** <span class="tag">ler</span> <span class="tag">shapefile</span> <span class="tag">geojson</span> <span class="tag">vetor</span>

```python
import geopandas as gpd
gdf = gpd.read_file('municipios.shp')
print(gdf.crs)
print(gdf.head())
```

---

## GeoDataFrame.to_crs

**Assinatura:** `gdf.to_crs(crs=None, epsg=None)`

Reprojetar um GeoDataFrame para outro sistema de coordenadas.

**Tags:** <span class="tag">reprojetar</span> <span class="tag">CRS</span> <span class="tag">EPSG</span> <span class="tag">projeção</span>

```python
import geopandas as gpd
gdf = gpd.read_file('municipios.shp')
gdf_utm = gdf.to_crs(epsg=31983)  # SIRGAS 2000 UTM 23S
gdf_utm.to_file('municipios_utm.shp')
```

---

## geopandas.overlay

**Assinatura:** `geopandas.overlay(df1, df2, how='intersection')`

Operações de overlay espacial: interseção, união, diferença, diferença simétrica entre dois GeoDataFrames.

**Tags:** <span class="tag">overlay</span> <span class="tag">interseção</span> <span class="tag">união</span> <span class="tag">espacial</span>

```python
import geopandas as gpd
result = gpd.overlay(gdf1, gdf2, how='intersection')
# how: 'union', 'difference', 'symmetric_difference'
```
