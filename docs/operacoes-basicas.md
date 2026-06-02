# 📖 Glossário de Operações Básicas

Guia rápido das **7 operações geoespaciais fundamentais** no GDAL, incluindo comandos CLI, APIs Python e formatos suportados.

---

## 🔄 Conversão de Formatos (Tradução / Translation)

Converte arquivos espaciais (raster ou vetor) de um formato de arquivo para outro (ex: converter Shapefile em GeoPackage, ou GeoTIFF em PNG).

| Propriedade | Detalhes |
|---|---|
| **Comandos CLI** | `gdal_translate` (Raster), `ogr2ogr` (Vetor) |
| **APIs Python** | `gdal.Translate`, `gdal.VectorTranslate` |
| **Formatos Suportados** | **Raster:** GeoTIFF, GeoPackage, PNG, JPEG, HDF5, NetCDF, VRT. **Vetor:** Shapefile, GeoPackage, GeoJSON, KML, GPX, CSV, DXF. |

=== "🖥️ Comando CLI"

    ```bash
    gdal_translate -of PNG input.tif output.png
    ogr2ogr -f GeoJSON output.geojson input.shp
    ```

=== "🐍 Script Python"

    ```python
    from osgeo import gdal

    # Raster
    gdal.Translate('output.png', 'input.tif', format='PNG')

    # Vetor
    gdal.VectorTranslate('output.geojson', 'input.shp', format='GeoJSON')
    ```

---

## 🌐 Reprojeção e Transformação Espacial (Reprojection / Warping)

Altera o Sistema de Referência de Coordenadas (CRS) ou projeção de dados espaciais georreferenciados para outro Datum/EPSG.

| Propriedade | Detalhes |
|---|---|
| **Comandos CLI** | `gdalwarp` (Raster), `ogr2ogr -t_srs` (Vetor) |
| **APIs Python** | `gdal.Warp`, `gdal.VectorTranslate` |
| **Formatos CRS** | EPSG (ex: EPSG:4326 para WGS84, EPSG:31983 para SIRGAS2000 UTM 23S), PROJ.4 strings, WKT (Well-Known Text). |

=== "🖥️ Comando CLI"

    ```bash
    gdalwarp -t_srs EPSG:31983 input.tif reprojected.tif
    ogr2ogr -t_srs EPSG:4326 output.shp input.shp
    ```

=== "🐍 Script Python"

    ```python
    from osgeo import gdal

    # Raster
    gdal.Warp('reprojected.tif', 'input.tif', dstSRS='EPSG:31983')

    # Vetor
    gdal.VectorTranslate('output.shp', 'input.shp', dstSRS='EPSG:4326')
    ```

---

## 🧱 Rasterização (Vetor para Raster / Rasterizing)

Queima (grava) feições geométricas de arquivos vetoriais (pontos, linhas, polígonos) em uma imagem matricial raster.

| Propriedade | Detalhes |
|---|---|
| **Comandos CLI** | `gdal_rasterize` |
| **APIs Python** | `gdal.Rasterize` |
| **Tipos Suportados** | **Geometrias:** Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon. **Bandas:** Byte, Int16, Float32, etc. |

=== "🖥️ Comando CLI"

    ```bash
    gdal_rasterize -b 1 -burn 255 -tr 10 10 input.shp output.tif
    ```

=== "🐍 Script Python"

    ```python
    from osgeo import gdal
    options = gdal.RasterizeOptions(xRes=10, yRes=10, burnValues=[255])
    gdal.Rasterize('output.tif', 'input.shp', options=options)
    ```

---

## 📐 Vetorização / Poligonização (Raster para Vetor / Polygonizing)

Gera geometrias de polígonos a partir de grupos de pixels raster com valores conectados e semelhantes.

| Propriedade | Detalhes |
|---|---|
| **Comandos CLI** | `gdal_polygonize.py` |
| **APIs Python** | `gdal.Polygonize` |
| **Tipos Suportados** | **Geometrias resultantes:** Polygon, MultiPolygon. **Atributos:** Tabela contendo os valores originais do pixel. |

=== "🖥️ Comando CLI"

    ```bash
    gdal_polygonize.py input.tif -f "ESRI Shapefile" output.shp layername
    ```

=== "🐍 Script Python"

    ```python
    from osgeo import gdal, ogr
    src_ds = gdal.Open('input.tif')
    src_band = src_ds.GetRasterBand(1)
    drv = ogr.GetDriverByName('ESRI Shapefile')
    dst_ds = drv.CreateDataSource('output.shp')
    dst_layer = dst_ds.CreateLayer('layername', geom_type=ogr.wkbPolygon)
    gdal.Polygonize(src_band, None, dst_layer, -1, [], callback=None)
    ```

---

## 🥞 Mosaico e Fusão (Merging / Mosaicking)

Une múltiplos pedaços (tiles) de dados geográficos raster ou VRTs em um único mosaico contínuo.

| Propriedade | Detalhes |
|---|---|
| **Comandos CLI** | `gdal_merge.py`, `gdalbuildvrt` |
| **APIs Python** | `gdal.BuildVRT` |
| **Formatos** | VRT (Mosaico virtual extremamente leve), GeoTIFF, HFA (Erdas Imagine). |

=== "🖥️ Comando CLI"

    ```bash
    gdal_merge.py -o mosaic.tif file1.tif file2.tif
    gdalbuildvrt mosaic.vrt *.tif
    ```

=== "🐍 Script Python"

    ```python
    from osgeo import gdal
    # Criando mosaico virtual (VRT)
    gdal.BuildVRT('mosaic.vrt', ['file1.tif', 'file2.tif'])
    ```

---

## 📋 Extração de Metadados e Inspeção (Info)

Inspeciona dados espaciais para exibir informações estruturadas de metadados, extensões geográficas, CRS e estatísticas.

| Propriedade | Detalhes |
|---|---|
| **Comandos CLI** | `gdalinfo` (Raster), `ogrinfo` (Vetor), `gdalsrsinfo` (CRS) |
| **APIs Python** | `gdal.Info`, `ogr.Open`, `osr.SpatialReference` |
| **Formatos de Saída** | JSON estruturado, texto simples, WKT, PROJ.4. |

=== "🖥️ Comando CLI"

    ```bash
    gdalinfo -stats input.tif
    ogrinfo -al -so input.shp
    gdalsrsinfo -o wkt EPSG:4326
    ```

=== "🐍 Script Python"

    ```python
    from osgeo import gdal
    ds = gdal.Open('input.tif')
    print(gdal.Info(ds))

    # CRS
    from osgeo import osr
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    print(srs.ExportToWkt())
    ```

---

## 🏔️ Geração de Modelos de Terreno (DEM Processing)

Extrai características morfológicas e físicas de Modelos Digitais de Elevação (DEM) raster.

| Propriedade | Detalhes |
|---|---|
| **Comandos CLI** | `gdaldem` (hillshade, slope, aspect, color-relief, TRI, TPI, roughness) |
| **APIs Python** | `gdal.DEMProcessing` |
| **Subcomandos/Tipos** | hillshade (sombreamento), slope (declividade em graus/porcentagem), aspect (orientação das encostas), color-relief (mapa colorido de relevo), TRI (Índice de Rugosidade), TPI (Índice de Posição Topográfica). |

=== "🖥️ Comando CLI"

    ```bash
    gdaldem hillshade dem.tif hillshade.tif
    gdaldem slope dem.tif slope.tif
    ```

=== "🐍 Script Python"

    ```python
    from osgeo import gdal
    # Hillshade
    gdal.DEMProcessing('hillshade.tif', 'dem.tif', 'hillshade')
    # Slope
    gdal.DEMProcessing('slope.tif', 'dem.tif', 'slope')
    ```
