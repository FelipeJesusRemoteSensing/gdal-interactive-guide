# 🔍 Comandos de Informação

Comandos para inspeção e extração de metadados: gdalinfo, ogrinfo, gdalsrsinfo e verificações de dataset.

**Total:** 9 comandos

---

??? note "gdal_dataset_check"

    <span class="badge badge-info">Informação</span>

    Check whether there are errors when reading the content of a dataset.

    **Keywords:** <span class="tag">errors</span> <span class="tag">content</span> <span class="tag">whether</span> <span class="tag">reading</span> <span class="tag">check</span> <span class="tag">dataset</span> <span class="tag">gdal_dataset_check</span> <span class="tag">there</span> <span class="tag">when</span>

    **Check whether there are errors when reading a dataset**

    ```console
    $ gdal dataset check NE1_50M_SR_W.tif
    ```


??? note "gdal_info"

    <span class="badge badge-info">Informação</span>

    Get information on a dataset.

    **Keywords:** <span class="tag">information</span> <span class="tag">ler</span> <span class="tag">inspecionar</span> <span class="tag">dataset</span> <span class="tag">info</span> <span class="tag">gdal_info</span> <span class="tag">metadados</span> <span class="tag">verificar</span>

    **Getting the list of all drivers (with JSON output)**

    ```console
    $ gdal --drivers
    ```


??? note "gdal_mdim_info"

    <span class="badge badge-info">Informação</span>

    Get information on a multidimensional dataset.

    **Keywords:** <span class="tag">information</span> <span class="tag">ler</span> <span class="tag">inspecionar</span> <span class="tag">dataset</span> <span class="tag">info</span> <span class="tag">metadados</span> <span class="tag">multidimensional</span> <span class="tag">gdal_mdim_info</span> <span class="tag">verificar</span>

    **Getting information on the file :file:`netcdf-4d.nc` as JSON output**

    ```console
    $ gdal mdim info netcdf-4d.nc
    ```

    **$ gdal mdim info netcdf-4d.nc**

    ```json
    {
      "type": "group",
      "name": "/",
      "attributes": {
        "Conventions": "CF-1.5"
      },
      "dimensions": [
        {
          "name": "levelist",
          "full_name": "/levelist",
          "size": 2,
          "type": "VERTICAL",
          "indexing_variable": "/levelist"
        },
        {
          "name": "longitude",
          "full_name": "/longitude",
          "size": 10,
          "type": "HORIZONTAL_X",
          "direction": "EAST",
          "indexing_variable": "/longitude"
        },
        {
          "name": "latitude",
          "full_name": "/latitude",
          "size": 10,
          "type": "HORIZONTAL_Y",
          "direction": "NORTH",
          "indexing_variable": "/latitude"
        },
        {
          "name": "time",
          "full_name": "/time",
            "size": 4,
          "type": "TEMPORAL",
          "indexing_variable": "/time"
          }
      ],
      "arrays": {
        "levelist": {
          "datatype": "Int32",
          "dimensions": [
              "/levelist"
            ],
          "attributes": {
            "long_name": "pressure_level"
          },
          "unit": "millibars"
        },
        "longitude": {
          "datatype": "Float32",
          "dimensions": [
            "/longitude"
          ],
          "attributes": {
            "standard_name": "longitude",
            "long_name": "longitude",
            "axis": "X"
          },
          "unit": "degrees_east"
        },
        "latitude": {
          "datatype": "Float32",
          "dimensions": [
            "/latitude"
          ],
          "attributes": {
            "standard_name": "latitude",
            "long_name": "latitude",
            "axis": "Y"
          },
          "unit": "degrees_north"
        },
        "time": {
          "datatype": "Float64",
          "dimensions": [
            "/time"
          ],
          "attributes": {
            "standard_name": "time",
            "calendar": "standard"
          },
          "unit": "hours since 1900-01-01 00:00:00"
        },
        "t": {
          "datatype": "Int32",
          "dimensions": [
            "/time",
            "/levelist",
            "/latitude",
            "/longitude"
          ],
          "nodata_value": -32767
        }
      },
      "structural_info": {
        "NC_FORMAT": "CLASSIC"
      }
    }
    ```


??? note "gdal_raster_info"

    <span class="badge badge-info">Informação</span>

    Operação raster GDAL correspondente a: Info. Get information on a raster dataset.

    **Keywords:** <span class="tag">information</span> <span class="tag">ler</span> <span class="tag">gdal</span> <span class="tag">gdal_raster_info</span> <span class="tag">inspecionar</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">info</span> <span class="tag">correspondente</span> <span class="tag">metadados</span> <span class="tag">verificar</span>

    **Sintaxe Básica**

    ```bash
    gdal_raster_info --help
    ```


??? note "gdal_raster_pixel_info"

    <span class="badge badge-info">Informação</span>

    Operação raster GDAL correspondente a: Pixel Info. Return information on a pixel of a raster dataset

    **Keywords:** <span class="tag">information</span> <span class="tag">ler</span> <span class="tag">gdal</span> <span class="tag">gdal_raster_pixel_info</span> <span class="tag">inspecionar</span> <span class="tag">pixel</span> <span class="tag">raster</span> <span class="tag">return</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">info</span> <span class="tag">correspondente</span>

    **Reading coordinates to extract from an input GeoPackage file and writing the output to a GeoPackage file**

    ```bash
    gdal raster pixel-info --position-dataset input.gpkg --input byte.tif --output output.gpkg
    ```

    **Getting pixel values from a on-the-fly resized raster dataset from coordinates in :file:`input.gpkg`.**

    ```bash
    gdal pipeline read byte.tif ! resize --size 50%,50% -r cubic ! pixel-info input.gpkg ! write output.gpkg
    ```

    **Getting pixel values from coordinates in a piped vector dataset, using the ``_`` placeholder dataset name**

    ```bash
    gdal pipeline read input.gml ! swap-xy ! pixel-info --input byte.tif --position-dataset _ ! write output.gpkg
    ```


??? note "gdalinfo"

    <span class="badge badge-info">Informação</span>

    Exibe informações e estatísticas detalhadas sobre um arquivo raster (dimensões, CRS, bandas, metadados).

    **Keywords:** <span class="tag">detalhadas</span> <span class="tag">estatísticas</span> <span class="tag">ler</span> <span class="tag">gdalinfo</span> <span class="tag">bandas</span> <span class="tag">exibe</span> <span class="tag">arquivo</span> <span class="tag">inspecionar</span> <span class="tag">raster</span> <span class="tag">dimensões</span> <span class="tag">info</span> <span class="tag">informações</span>

    **Sintaxe Básica**

    ```bash
    gdalinfo --help
    ```


??? note "gdallocationinfo"

    <span class="badge badge-info">Informação</span>

    Raster query tool

    **Keywords:** <span class="tag">query</span> <span class="tag">tool</span> <span class="tag">gdallocationinfo</span> <span class="tag">raster</span>

    **Reporting on pixel (256,256) on the file :file:`utm.tif`**

    ```console
    $ gdallocationinfo utm.tif 256 256
    Report:
    Location: (256P,256L)
    Band 1:
        Value: 115
    ```

    **Querying a VRT file providing the location in WGS84, and getting the result in XML**

    ```console
    $ gdallocationinfo -xml -wgs84 utm.vrt -117.5 33.75
    <Report pixel="217" line="282">
        <BandReport band="1">
            <LocationInfo>
            <File>utm.tif</File>
            </LocationInfo>
            <Value>16</Value>
        </BandReport>
    </Report>
    ```

    **Reading locations from stdin**

    ```console
    $ cat coordinates.txt
    443020 3748359
    441197 3749005
    443852 3747743
    
    $ cat coordinates.txt | gdallocationinfo -geoloc utmsmall.tif
    Report:
      Location: (38P,49L)
      Band 1:
        Value: 214
    Report:
      Location: (7P,38L)
      Band 1:
        Value: 107
    Report:
      Location: (52P,59L)
      Band 1:
        Value: 148
    
    $ cat coordinates.txt | gdallocationinfo -geoloc -valonly -E -field_sep , utmsmall.tif
    443020,3748359,214
    441197,3749005,107
    443852,3747743,148
    ```


??? note "gdalmdiminfo"

    <span class="badge badge-info">Informação</span>

    Reports structure and content of a multidimensional dataset.

    **Keywords:** <span class="tag">content</span> <span class="tag">reports</span> <span class="tag">structure</span> <span class="tag">dataset</span> <span class="tag">multidimensional</span> <span class="tag">gdalmdiminfo</span>

    **Display general structure**

    ```console
    $ gdalmdiminfo netcdf-4d.nc
    ```

    **$ gdalmdiminfo netcdf-4d.nc**

    ```json
    {
      "type": "group",
      "name": "/",
      "attributes": {
        "Conventions": "CF-1.5"
      },
      "dimensions": [
        {
          "name": "levelist",
          "full_name": "/levelist",
          "size": 2,
          "type": "VERTICAL",
          "indexing_variable": "/levelist"
        },
        {
          "name": "longitude",
          "full_name": "/longitude",
          "size": 10,
          "type": "HORIZONTAL_X",
          "direction": "EAST",
          "indexing_variable": "/longitude"
        },
        {
          "name": "latitude",
          "full_name": "/latitude",
          "size": 10,
          "type": "HORIZONTAL_Y",
          "direction": "NORTH",
          "indexing_variable": "/latitude"
        },
        {
          "name": "time",
          "full_name": "/time",
            "size": 4,
          "type": "TEMPORAL",
          "indexing_variable": "/time"
          }
      ],
      "arrays": {
        "levelist": {
          "datatype": "Int32",
          "dimensions": [
              "/levelist"
            ],
          "attributes": {
            "long_name": "pressure_level"
          },
          "unit": "millibars"
        },
        "longitude": {
          "datatype": "Float32",
          "dimensions": [
            "/longitude"
          ],
          "attributes": {
            "standard_name": "longitude",
            "long_name": "longitude",
            "axis": "X"
          },
          "unit": "degrees_east"
        },
        "latitude": {
          "datatype": "Float32",
          "dimensions": [
            "/latitude"
          ],
          "attributes": {
            "standard_name": "latitude",
            "long_name": "latitude",
            "axis": "Y"
          },
          "unit": "degrees_north"
        },
        "time": {
          "datatype": "Float64",
          "dimensions": [
            "/time"
          ],
          "attributes": {
            "standard_name": "time",
            "calendar": "standard"
          },
          "unit": "hours since 1900-01-01 00:00:00"
        },
        "t": {
          "datatype": "Int32",
          "dimensions": [
            "/time",
            "/levelist",
            "/latitude",
            "/longitude"
          ],
          "nodata_value": -32767
        }
      },
      "structural_info": {
        "NC_FORMAT": "CLASSIC"
      }
    }
    ```

    **Display detailed information about a given array**

    ```console
    $ gdalmdiminfo netcdf-4d.nc -array t -detailed -limit 3
    ```


??? note "gdalsrsinfo"

    <span class="badge badge-info">Informação</span>

    Exibe informações sobre o Sistema de Referência de Coordenadas (CRS) de um arquivo espacial em vários formatos (WKT, PROJ, EPSG).

    **Keywords:** <span class="tag">epsg</span> <span class="tag">sistema</span> <span class="tag">exibe</span> <span class="tag">arquivo</span> <span class="tag">informações</span> <span class="tag">formatos</span> <span class="tag">gdalsrsinfo</span> <span class="tag">espacial</span> <span class="tag">referência</span> <span class="tag">vários</span> <span class="tag">proj</span> <span class="tag">coordenadas</span>

    **--------**

    ```bash
    Usage: gdalsrsinfo [--help] [--help-general]
                       [--single-line] [-V] [-e][-o <out_type>] <srs_def>
    ```

    **Exemplo 2**

    ```console
    $ gdalsrsinfo -o proj4 landsat.tif
    PROJ.4 : '+proj=utm +zone=19 +south +datum=WGS84 +units=m +no_defs '
    ```

