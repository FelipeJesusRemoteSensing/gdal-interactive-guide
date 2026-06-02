# 🔧 Comandos Utilitários

Comandos utilitários auxiliares do ecossistema GDAL.

**Total:** 8 comandos

---

??? note "gnmanalyse"

    <span class="badge badge-util">Utilitário</span>

    Analyses networks

    **Keywords:** <span class="tag">analyses</span> <span class="tag">networks</span> <span class="tag">gnmanalyse</span>

    **Sintaxe Básica**

    ```bash
    gnmanalyse --help
    ```


??? note "gnmmanage"

    <span class="badge badge-util">Utilitário</span>

    Manages networks

    **Keywords:** <span class="tag">manages</span> <span class="tag">networks</span> <span class="tag">gnmmanage</span>

    **Sintaxe Básica**

    ```bash
    gnmmanage --help
    ```


??? note "migration_guide_to_gdal_cli"

    <span class="badge badge-util">Utilitário</span>

    This page documents, through examples, how to migrate from the traditional GDAL

    **Keywords:** <span class="tag">from</span> <span class="tag">traditional</span> <span class="tag">through</span> <span class="tag">gdal</span> <span class="tag">documents</span> <span class="tag">page</span> <span class="tag">this</span> <span class="tag">migrate</span> <span class="tag">migration_guide_to_gdal_cli</span> <span class="tag">examples</span>

    *** Getting information on a raster dataset in human-readable format**

    ```bash
    gdalinfo my.tif
    
    ==>
    
    gdal raster info my.tif
    ```

    *** Converting a georeferenced netCDF file to cloud-optimized GeoTIFF**

    ```bash
    gdal_translate -of COG in.nc out.tif
    
    ==>
    
    gdal raster convert --of=COG in.nc out.tif
    ```

    *** Reprojecting a GeoTIFF file to a Deflate compressed tiled GeoTIFF file**

    ```bash
    gdalwarp -t_srs EPSG:4326 -co TILED=YES -co COMPRESS=DEFLATE -overwrite in.tif out.tif
    
    ==>
    
    gdal raster reproject --output-crs=EPSG:4326 --co=TILED=YES,COMPRESS=DEFLATE --overwrite in.tif out.tif
    ```

    *** Update existing out.tif with content of in.tif using cubic interpolation**

    ```bash
    gdalwarp -r cubic in.tif out.tif
    
    ==>
    
    gdal raster update -r cubic in.tif out.tif
    ```

    *** Converting a PNG file to a tiled GeoTIFF file, adding georeferencing for world coverage in WGS 84 and metadata**

    ```bash
    gdal_translate -a_ullr -180 90 180 -90 -a_srs EPSG:4326 -co TILED=YES -mo DESCRIPTION=Mean_day_temperature in.png out.tif
    
    ==>
    
    gdal raster pipeline read in.png ! edit --crs=EPSG:4326 --bbox=-180,-90,180,90 --metadata=DESCRIPTION=Mean_day_temperature ! write --co=TILED=YES out.tif
    ```

    *** Clipping a raster with a bounding box**

    ```bash
    gdal_translate -projwin 2 50 3 49 in.tif out.tif
    
    ==>
    
    gdal raster clip --bbox=2,49,3,50 in.tif out.tif
    ```

    *** Creating a virtual mosaic (.vrt) from all GeoTIFF files in a directory**

    ```bash
    gdalbuildvrt out.vrt src/*.tif
    
    ==>
    
    gdal raster mosaic src/*.tif out.vrt
    ```

    *** Creating a mosaic in COG format from all GeoTIFF files in a directory**

    ```bash
    gdalbuildvrt tmp.vrt src/*.tif
    gdal_translate -of COG tmp.vrt out.tif
    
    ==>
    
    gdal raster mosaic --of=COG src/*.tif out.tif
    ```

    *** Adding internal overviews for reduction factors 2, 4, 8 and 16 to a GeoTIFF file**

    ```bash
    gdaladdo -r average my.tif 2 4 8 16
    
    ==>
    
    gdal raster overview add -r average --levels=2,4,8,16 my.tif
    ```

    *** Combining single-band rasters into a multi-band raster**

    ```bash
    gdalbuildvrt tmp.vrt red.tif green.tif blue.tif
    gdal_translate tmp.vrt out.tif
    
    ==>
    
    gdal raster stack red.tif green.tif blue.tif out.tif
    ```

    *** Reorder a 3-band dataset with bands ordered Blue, Green, Red to Red, Green, Blue**

    ```bash
    gdal_translate -b 3 -b 2 -b 1 bgr.tif rgb.tif
    
    ==>
    
    gdal raster select --band 3,2,1 bgr.tif rgb.tif --overwrite
    ```

    *** Expand a dataset with a color table to RGB**

    ```bash
    gdal_translate -expand rgb color_table.tif rgb.tif
    
    ==>
    
    gdal raster color-map color_table.tif rgb.tif --overwrite
    ```

    *** Apply an external color-map to a dataset**

    ```bash
    gdaldem color-map color_table.tif color_map.txt rgb.tif
    
    ==>
    
    gdal raster color-map --color-map=color_map.txt color_table.tif rgb.tif --overwrite
    ```

    *** Convert nearly black values of the collar to black**

    ```bash
    nearblack -nb 1 -near 10 my.tif
    
    ==>
    
    gdal raster clean-collar --update --color-threshold=1 --pixel-distance=10 my.tif
    ```

    *** Generating tiles between zoom level 2 and 5 of WebMercator from an input GeoTIFF**

    ```bash
    gdal2tiles --zoom=2-5 input.tif output_folder
    
    ==>
    
    gdal raster tile --min-zoom=2 --max-zoom=5 input.tif output_folder
    ```

    *** Getting information on a vector dataset in human-readable format**

    ```bash
    ogrinfo -al -so my.gpkg
    
    ==>
    
    gdal vector info my.gpkg
    ```

    *** Converting a shapefile to a GeoPackage**

    ```bash
    ogr2ogr out.gpkg in.shp
    
    ==>
    
    gdal vector convert in.shp out.gpkg
    ```

    *** Reprojecting a shapefile to a GeoPackage**

    ```bash
    ogr2ogr -t_srs EPSG:4326 out.gpkg in.shp
    
    ==>
    
    gdal vector reproject --output-crs=EPSG:4326 in.shp out.gpkg
    ```

    *** Clipping a GeoPackage file**

    ```bash
    ogr2ogr -clipsrc 2 49 3 50 out.gpkg in.shp
    
    ==>
    
    gdal vector clip --bbox=2,49,3,50 in.gpkg out.gpkg
    ```

    *** Selecting features from a GeoPackage file intersecting a bounding box, but not clipping them to it**

    ```bash
    ogr2ogr -spat 2 49 3 50 out.gpkg in.shp
    
    ==>
    
    gdal vector filter --bbox=2,49,3,50 in.gpkg out.gpkg
    ```

    ***  Selecting features from a shapefile intersecting a bounding box, but not clipping them to it and reprojecting**

    ```bash
    ogr2ogr -t_srs EPSG:32631 -spat 2 49 3 50 out.gpkg in.shp
    
    ==>
    
    gdal vector pipeline read in.gpkg ! filter --bbox=2,49,3,50 ! reproject --output-crs=EPSG:32631 ! write out.gpkg
    ```

    *** Selecting features from a shapefile based on an attribute query, and restricting to a few fields**

    ```bash
    ogr2ogr -where "country='Greenland'" -select population,_ogr_geometry_ out.gpkg in.shp
    
    ==>
    
    gdal vector pipeline ! read in.shp ! filter --where "country='Greenland'" ! select --fields population,_ogr_geometry_ ! write out.gpkg
    ```

    *** Creating a GeoPackage stacking all input shapefiles in separate layers.**

    ```bash
    ogrmerge -f GPKG -o merged.gpkg *.shp
    
    ==>
    
    gdal vector concat --mode=stack *.shp merged.gpkg
    ```

    *** Modify in-place a GeoPackage dataset by running a SQL command.**

    ```bash
    ogrinfo my.gpkg -sql "DELETE FROM countries WHERE pop > 1e6"
    
    ==>
    
    gdal vector sql --update my.gpkg --sql "DELETE FROM countries WHERE pop > 1e6"
    ```

    *** Listing the contents of a remote :ref:`vector.pmtiles` dataset, using :ref:`gdal_vsi_list`.**

    ```bash
    python gdal_ls.py -lr "/vsipmtiles//vsicurl/https://protomaps.github.io/PMTiles/protomaps(vector)ODbL_firenze.pmtiles"
    
    ==>
    
    gdal vsi list -lR "/vsipmtiles//vsicurl/https://protomaps.github.io/PMTiles/protomaps(vector)ODbL_firenze.pmtiles"
    ```

    *** Listing the contents of a vsis3 dataset.**

    ```bash
    export AWS_NO_SIGN_REQUEST="YES"
    gdal_ls.py "/vsis3/overturemaps-us-west-2/release/2025-10-22.0/theme=buildings/type=building"
    
    ==>
    
    export AWS_NO_SIGN_REQUEST="YES"
    gdal vsi list "/vsis3/overturemaps-us-west-2/release/2025-10-22.0/theme=buildings/type=building"
    ```

    *** Extracting all remote content into a local directory, using :ref:`gdal_vsi_copy`.**

    ```bash
    gdal_cp.py "/vsipmtiles//vsicurl/https://protomaps.github.io/PMTiles/protomaps(vector)ODbL_firenze.pmtiles/metadata.json" /vsistdout/ | jq
    
    ==>
    
    gdal vsi copy -r "/vsipmtiles//vsicurl/https://protomaps.github.io/PMTiles/protomaps(vector)ODbL_firenze.pmtiles" out_pmtiles
    ```


??? note "nearblack"

    <span class="badge badge-util">Utilitário</span>

    Converte pixels quase pretos ou quase brancos ao redor das bordas de uma imagem em valores nodata ou transparentes.

    **Keywords:** <span class="tag">imagem</span> <span class="tag">converte</span> <span class="tag">redor</span> <span class="tag">valores</span> <span class="tag">nearblack</span> <span class="tag">quase</span> <span class="tag">bordas</span> <span class="tag">pretos</span> <span class="tag">transparentes</span> <span class="tag">pixels</span> <span class="tag">nodata</span> <span class="tag">brancos</span>

    **Sintaxe Básica**

    ```bash
    nearblack --help
    ```


??? note "nodata_handling_gdaladdo_gdal_translate"

    <span class="badge badge-util">Utilitário</span>

    Utilitário do ecossistema GDAL/OGR para manipulação de dados espaciais.

    **Keywords:** <span class="tag">gdal</span> <span class="tag">nodata_handling_gdaladdo_gdal_translate</span> <span class="tag">manipulação</span> <span class="tag">utilitário</span> <span class="tag">espaciais</span> <span class="tag">ecossistema</span> <span class="tag">dados</span>

    **Sintaxe Básica**

    ```bash
    nodata_handling_gdaladdo_gdal_translate --help
    ```


??? note "pct2rgb"

    <span class="badge badge-util">Utilitário</span>

    Convert an 8bit paletted image to 24bit RGB.

    **Keywords:** <span class="tag">image</span> <span class="tag">convert</span> <span class="tag">pct2rgb</span> <span class="tag">8bit</span> <span class="tag">24bit</span> <span class="tag">paletted</span>

    **--------**

    ```bash
    pct2rgb [--help] [--help-general]
               [-of format] [-b band] [-rgba] [-pct palette_file] <source_file> <dest_file>
    ```


??? note "rgb2pct"

    <span class="badge badge-util">Utilitário</span>

    Convert a 24bit RGB image to 8bit paletted.

    **Keywords:** <span class="tag">image</span> <span class="tag">convert</span> <span class="tag">rgb2pct</span> <span class="tag">8bit</span> <span class="tag">24bit</span> <span class="tag">paletted</span>

    **--------**

    ```bash
    rgb2pct [--help] [--help-general] [--creation-option OPTION]
               [-n colors | -pct palette_file] [-of format] <source_file> <dest_file>
    ```

    **237/237/237/255, 236/236/236/255 and 229/229/229/255.**

    ```console
    $ rgb2pct -pct palette.vrt rgb.tif pseudo-colored.tif
    $ more < palette.vrt
    <VRTDataset rasterXSize="226" rasterYSize="271">
        <VRTRasterBand dataType="Byte" band="1">
            <ColorInterp>Palette</ColorInterp>
            <ColorTable>
            <Entry c1="238" c2="238" c3="238" c4="255"/>
            <Entry c1="237" c2="237" c3="237" c4="255"/>
            <Entry c1="236" c2="236" c3="236" c4="255"/>
            <Entry c1="229" c2="229" c3="229" c4="255"/>
            </ColorTable>
        </VRTRasterBand>
    </VRTDataset>
    ```


??? note "sozip"

    <span class="badge badge-util">Utilitário</span>

    Generate a seek-optimized ZIP (SOZip) file.

    **Keywords:** <span class="tag">sozip</span> <span class="tag">generate</span> <span class="tag">seek</span> <span class="tag">optimized</span> <span class="tag">file</span>

    **--------**

    ```bash
    sozip [--help] [--help-general]
          [--quiet|--verbose]
          [[-g|--grow] | [--overwrite]]
          [-r|--recurse-paths]
          [-j|--junk-paths]
          [-l|--list]
          [--optimize-from=<input.zip>]
          [--validate]
          [--enable-sozip={auto|yes|no}]
          [--sozip-chunk-size=<value>]
          [--sozip-min-file-size=<value>]
          [--content-type=<value>]
          <zip_filename> [<filename>]...
    ```

