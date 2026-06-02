# 🌍 GDAL/OGR — Operadores Python

Funções nativas da biblioteca GDAL/OGR para manipulação de dados raster e vetoriais.

---

## gdal.Open

<span class="badge badge-raster">Raster</span>

**Assinatura:** `gdal.Open(filename, access=GA_ReadOnly)`

Abre um arquivo raster. Retorna um objeto Dataset. Use `GA_Update` para abertura com escrita.

**Tags:** <span class="tag">raster</span> <span class="tag">abrir</span> <span class="tag">dataset</span> <span class="tag">arquivo</span>

```python
from osgeo import gdal
ds = gdal.Open('meu_raster.tif')
band = ds.GetRasterBand(1)
array = band.ReadAsArray()
```

---

## gdal.Warp

<span class="badge badge-raster">Raster</span>

**Assinatura:** `gdal.Warp(destNameOrDestDS, srcDSOrSrcDSTab, **kwargs)`

Reprojeção e transformação de rasters. Substitui o comando gdalwarp. Suporta reprojeção, recorte, reamostragem.

**Tags:** <span class="tag">reprojetar</span> <span class="tag">warp</span> <span class="tag">recortar</span> <span class="tag">CRS</span>

```python
from osgeo import gdal
gdal.Warp('saida.tif', 'entrada.tif',
    dstSRS='EPSG:4326',
    cutlineDSName='mascara.shp',
    cropToCutline=True)
```

---

## gdal.Translate

<span class="badge badge-raster">Raster</span>

**Assinatura:** `gdal.Translate(destName, srcDS, **kwargs)`

Converte formato, recorta por extent, seleciona bandas ou altera tipo de dado de rasters.

**Tags:** <span class="tag">converter</span> <span class="tag">formato</span> <span class="tag">recortar</span> <span class="tag">bandas</span>

```python
from osgeo import gdal
gdal.Translate('saida.tif', 'entrada.vrt',
    projWin=[xmin, ymax, xmax, ymin],
    outputType=gdal.GDT_Float32)
```

---

## gdal.BuildVRT

<span class="badge badge-raster">Raster</span>

**Assinatura:** `gdal.BuildVRT(destName, srcDSOrSrcDSTab, **kwargs)`

Cria um VRT (Virtual Raster Table) a partir de múltiplos arquivos raster, sem copiar dados.

**Tags:** <span class="tag">vrt</span> <span class="tag">mosaico</span> <span class="tag">virtual</span> <span class="tag">combinar</span>

```python
from osgeo import gdal
import glob
arquivos = glob.glob('tiles/*.tif')
gdal.BuildVRT('mosaico.vrt', arquivos)
```

---

## ogr.Open

<span class="badge badge-vetor">Vetor</span>

**Assinatura:** `ogr.Open(filename, update=0)`

Abre um arquivo vetorial (shapefile, GeoJSON, GPKG etc). Retorna um DataSource OGR.

**Tags:** <span class="tag">vetor</span> <span class="tag">shapefile</span> <span class="tag">abrir</span> <span class="tag">datasource</span>

```python
from osgeo import ogr
ds = ogr.Open('arquivo.shp')
layer = ds.GetLayer(0)
for feature in layer:
    geom = feature.GetGeometryRef()
    print(geom.ExportToWkt())
```

---

## ogr.CreateGeometryFromWkt

<span class="badge badge-vetor">Vetor</span>

**Assinatura:** `ogr.CreateGeometryFromWkt(wkt, srs=None)`

Cria um objeto de geometria OGR a partir de uma string WKT (Well-Known Text).

**Tags:** <span class="tag">geometria</span> <span class="tag">WKT</span> <span class="tag">criar</span> <span class="tag">vetor</span>

```python
from osgeo import ogr
wkt = 'POINT (-49.25 -16.68)'
ponto = ogr.CreateGeometryFromWkt(wkt)
print(ponto.ExportToJson())
```

---

## osr.SpatialReference

<span class="badge badge-info">CRS</span>

**Assinatura:** `osr.SpatialReference()`

Define e manipula sistemas de referência espacial (SRS/CRS). Permite conversão entre projeções.

**Tags:** <span class="tag">projeção</span> <span class="tag">CRS</span> <span class="tag">SRS</span> <span class="tag">EPSG</span>

```python
from osgeo import osr
srs = osr.SpatialReference()
srs.ImportFromEPSG(31983)  # SIRGAS 2000 / UTM 23S
print(srs.ExportToWkt())
```
