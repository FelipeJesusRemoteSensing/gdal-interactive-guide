# 📐 Comandos Vetor

Comandos para processamento de dados vetoriais: conversão, buffer, dissolve, overlay, reprojeção e validação de geometrias.

**Total:** 47 comandos

---

??? note "gdal_vector"

    <span class="badge badge-vetor">Vetor</span>

    Entry point for vector commands

    **Keywords:** <span class="tag">gdal_vector</span> <span class="tag">point</span> <span class="tag">entry</span> <span class="tag">vector</span> <span class="tag">commands</span>

    **Getting information on the file :file:`poly.gpkg` (with text output)**

    ```console
    $ gdal vector info poly.gpkg
    ```

    **Converting file :file:`poly.gpkg` to Esri File Geodatabase**

    ```console
    $ gdal vector convert --format=OpenFileGDB poly.gpkg poly.gdb
    ```


??? note "gdal_vector_buffer"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Buffer. Compute a buffer around geometries of a vector dataset.

    **Keywords:** <span class="tag">gdal_vector_buffer</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">área de influência</span> <span class="tag">vetor buffer</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">buffer</span> <span class="tag">correspondente</span> <span class="tag">geometries</span> <span class="tag">vector</span> <span class="tag">compute</span>

    **Compute a buffer of one km around input geometries (assuming the CRS is in meters)**

    ```bash
    $ gdal vector buffer --distance=1000 in.gpkg out.gpkg --overwrite
    ```

    **Buffer a point dataset with 20 segments per quadrant (instead of default 8) to better approximate a circle**

    ```bash
    $ gdal vector buffer --distance=20 --quadrant-segments=20 points.gpkg point_buffers.gpkg
    ```

    **Buffer lines to the left using join and end cap styles**

    ```bash
    $ gdal vector buffer --distance=10 --endcap-style=flat --side=left --join-style=mitre --mitre-limit=2 lines.gpkg lines-buffer-endcap.gpkg
    ```


??? note "gdal_vector_check_coverage"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Check Coverage. Checks whether a polygon dataset forms a valid coverage.

    **Keywords:** <span class="tag">forms</span> <span class="tag">vetorial</span> <span class="tag">whether</span> <span class="tag">gdal_vector_check_coverage</span> <span class="tag">gdal</span> <span class="tag">check</span> <span class="tag">coverage</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">valid</span> <span class="tag">correspondente</span> <span class="tag">polygon</span>

    **Output coverage errors in a :ref:`TopoJSON &lt;vector.topojson&gt;` file to a :ref:`GeoJSON &lt;vector.geojson&gt;` file**

    ```bash
    $ gdal vector check-coverage "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-albers-10m.json" --layer counties counties-errors.geojson
    ```


??? note "gdal_vector_check_geometry"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Check Geometry. Checks that geometries are valid and simple according to the :term:`OGC` Simple Features standard.

    **Keywords:** <span class="tag">term</span> <span class="tag">vetorial</span> <span class="tag">geometry</span> <span class="tag">gdal</span> <span class="tag">according</span> <span class="tag">check</span> <span class="tag">that</span> <span class="tag">standard</span> <span class="tag">operação</span> <span class="tag">valid</span> <span class="tag">simple</span> <span class="tag">correspondente</span>

    **Print invalidity locations to console**

    ```console
    $ gdal vector check-geometry ne_10m_admin_0_countries.shp \
             --quiet \
             -f CSV \
             --lco GEOMETRY=AS_XY \
             --lco SEPARATOR=TAB \
             /vsistdout/
    # X	Y	error
    # 35.6210871060001	23.1392929140001	Ring Self-intersection
    ```


??? note "gdal_vector_clean_coverage"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Clean Coverage. Adjust the boundaries of a polygonal dataset, removing gaps and overlaps.

    **Keywords:** <span class="tag">clean</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">boundaries</span> <span class="tag">removing</span> <span class="tag">overlaps</span> <span class="tag">coverage</span> <span class="tag">dataset</span> <span class="tag">adjust</span> <span class="tag">polygonal</span> <span class="tag">operação</span> <span class="tag">gdal_vector_clean_coverage</span>

    **Create and then simplify a polygonal coverage**

    ```bash
    $ gdal vector pipeline read ne_10m_admin_0_countries.shp ! \
                           make-valid ! \
                           clean-coverage ! \
                           simplify-coverage --tolerance 1 ! \
                           write countries.shp
    ```


??? note "gdal_vector_clip"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Clip. Clip a vector dataset.

    **Keywords:** <span class="tag">gdal_vector_clip</span> <span class="tag">clip</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">vector</span>

    **Clip a GeoPackage file to the bounding box from longitude 2, latitude 49, to longitude 3, latitude 50 in WGS 84**

    ```bash
    $ gdal vector clip --bbox=2,49,3,50 --bbox-crs=EPSG:4326 in.gpkg out.gpkg --overwrite
    ```


??? note "gdal_vector_combine"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Combine. Combine geometries into collections

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">collections</span> <span class="tag">into</span> <span class="tag">gdal</span> <span class="tag">operação</span> <span class="tag">combine</span> <span class="tag">gdal_vector_combine</span> <span class="tag">correspondente</span> <span class="tag">geometries</span>

    **Sintaxe Básica**

    ```bash
    gdal_vector_combine --help
    ```


??? note "gdal_vector_concat"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Concat. Concatenate vector datasets

    **Keywords:** <span class="tag">datasets</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">concatenate</span> <span class="tag">operação</span> <span class="tag">concat</span> <span class="tag">correspondente</span> <span class="tag">vector</span> <span class="tag">gdal_vector_concat</span>

    **Creating a GeoPackage stacking all input shapefiles in separate layers.**

    ```bash
    gdal vector concat --mode=stack *.shp out.gpkg
    ```

    **'germany' depending where it comes from:**

    ```bash
    gdal vector concat --mode=single --source-layer-field-name=country --output-crs=EPSG:4258 france.shp germany.shp merged.shp
    ```


??? note "gdal_vector_concave_hull"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Concave Hull. Compute a concave hull around geometries of a vector dataset.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">gdal_vector_concave_hull</span> <span class="tag">concave</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">hull</span> <span class="tag">correspondente</span> <span class="tag">geometries</span> <span class="tag">vector</span> <span class="tag">compute</span> <span class="tag">around</span>

    **up with a point or line geometry.**

    ```bash
    gdal vector pipeline ! \
        read ne_10m_populated_places.shp ! \
        buffer 0.1 ! \
        combine --group-by ADM0_A3 ! \
        concave-hull --ratio 0.5 ! \
        write country_city_hulls.gpkg
    ```

    **The ``sql`` stage helps rendering smaller countries on top of larger ones.**

    ```bash
    gdal vector pipeline ! \
        read /vsizip//vsicurl/https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip ! \
        combine --group-by admin,geonunit ! \
        dissolve ! \
        concave-hull --ratio 0.1 ! \
        rename-layer --output-layer countries_concave_hull_of_polygons ! \
        sql --sql "SELECT * FROM countries_concave_hull_of_polygons ORDER BY ST_Area(geometry) DESC" --dialect SQLite ! \
        write countries_concave_hull_of_polygons.gpkg
    ```


??? note "gdal_vector_convert"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Convert. Convert a vector dataset.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">convert</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">vector</span> <span class="tag">gdal_vector_convert</span>

    **Converting file :file:`poly.shp` to a GeoPackage**

    ```console
    $ gdal vector convert poly.shp output.gpkg
    ```

    **Add new layer from file :file:`line.shp` to an existing GeoPackage, and rename it "lines"**

    ```console
    $ gdal vector convert --update --output-layer=lines line.shp output.gpkg
    ```

    **Append features from from file :file:`poly2.shp` to an existing layer ``poly`` of a GeoPackage, without a progress bar**

    ```console
    $ gdal vector convert --quiet --append --output-layer=poly poly2.shp output.gpkg
    ```


??? note "gdal_vector_convex_hull"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Convex Hull. Compute a convex hull around geometries of a vector dataset.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">convex</span> <span class="tag">geometries</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">hull</span> <span class="tag">correspondente</span> <span class="tag">gdal_vector_convex_hull</span> <span class="tag">vector</span> <span class="tag">compute</span> <span class="tag">around</span>

    **Compute the convex hull of each country**

    ```bash
    gdal vector convex-hull countries.gpkg countries_convexhull.gpkg
    ```

    **up with a point or line geometry.**

    ```bash
    gdal vector pipeline ! \
        read ne_10m_populated_places.shp ! \
        buffer 0.1 ! \
        combine --group-by ADM0_A3 ! \
        convex-hull ! \
        write country_city_hulls.gpkg
    ```


??? note "gdal_vector_create"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Create. Create one or more vector layers, creating the dataset if it doesn't exist.

    **Keywords:** <span class="tag">gdal_vector_create</span> <span class="tag">layers</span> <span class="tag">vetorial</span> <span class="tag">create</span> <span class="tag">gdal</span> <span class="tag">more</span> <span class="tag">creating</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">doesn</span> <span class="tag">vector</span>

    **Create a POINT layer named `names` with a string field named `name` in a new vector dataset**

    ```bash
    gdal vector create --geometry-type point  --crs EPSG:4326 --field name:string --output-layer names points.gpkg
    ```

    **Add a POINT layer named `names2` with a string field named `name` to an existing vector dataset**

    ```bash
    gdal vector create --update --geometry-type point --crs EPSG:4326 --field name:string --output-layer names2 points.gpkg
    ```

    **Create a new vector dataset with a layer named `countries_new` based on the layer `countries` of an existing dataset**

    ```bash
    gdal vector create --like ../data/poly.gpkg --input-layer poly --output-layer areas_new areas.gpkg
    ```


??? note "gdal_vector_dissolve"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Dissolve. Unions the elements of each feature's geometry.

    **Keywords:** <span class="tag">gdal_vector_dissolve</span> <span class="tag">vetorial</span> <span class="tag">geometry</span> <span class="tag">gdal</span> <span class="tag">dissolve</span> <span class="tag">unions</span> <span class="tag">feature</span> <span class="tag">operação</span> <span class="tag">each</span> <span class="tag">elements</span> <span class="tag">correspondente</span>

    **Dissolve country boundaries into continent boundaries**

    ```bash
    gdal vector pipeline read countries.shp !
        combine --group-by CONTINENT ! \
        dissolve ! \
        write continents.shp
    ```


??? note "gdal_vector_edit"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Edit. Edit metadata of a vector dataset.

    **Keywords:** <span class="tag">edit</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">gdal_vector_edit</span> <span class="tag">metadata</span> <span class="tag">vector</span>

    **Change the CRS of a GeoPackage file (without reprojecting it) and its geometry type**

    ```bash
    $ gdal vector edit --crs=EPSG:4326 --geometry-type=POLYGONZM in.gpkg out.gpkg --overwrite
    ```

    **Apply a CRS to a Shapefile**

    ```bash
    $ gdal vector edit --crs=EPSG:3857 in.shp out.shp
    ```


??? note "gdal_vector_explode_collections"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Explode Collections. Explode geometries of type collection of a vector dataset.

    **Keywords:** <span class="tag">gdal_vector_explode_collections</span> <span class="tag">vetorial</span> <span class="tag">collections</span> <span class="tag">gdal</span> <span class="tag">collection</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">explode</span> <span class="tag">correspondente</span> <span class="tag">geometries</span> <span class="tag">type</span> <span class="tag">vector</span>

    **Only retain parts of geometry collections that are of type Point.**

    ```bash
    $ gdal vector explode-collections --geometry-type=POINT --skip-on-type-mismatch in.gpkg points.shp --overwrite
    ```


??? note "gdal_vector_export_schema"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Export Schema. Export the OGR_SCHEMA from a vector dataset.

    **Keywords:** <span class="tag">gdal_vector_export_schema</span> <span class="tag">from</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">schema</span> <span class="tag">ogr_schema</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">vector</span> <span class="tag">export</span>

    **Extracting the OGR_SCHEMA from the file :file:`poly.gpkg`**

    ```bash
    gdal vector export-schema poly.gpkg
    ```

    **Validate an OGR_SCHEMA file using Python**

    ```bash
    $ pip install check-jsonschema
    $ check-jsonschema --schemafile https://raw.githubusercontent.com/OSGeo/gdal/master/ogr/data/ogr_fields_override.schema.json countries.json --verbose
    ```


??? note "gdal_vector_filter"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Filter. Filter a vector dataset.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">filter</span> <span class="tag">gdal</span> <span class="tag">dataset</span> <span class="tag">gdal_vector_filter</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">vector</span>

    **Select features from a GeoPackage file that intersect the bounding box from longitude 2, latitude 49, to longitude 3, latitude 50 in WGS 84**

    ```bash
    $ gdal vector filter --bbox=2,49,3,50 in.gpkg out.gpkg --overwrite
    ```


??? note "gdal_vector_grid"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Grid. Create a regular grid from scattered points

    **Keywords:** <span class="tag">from</span> <span class="tag">vetorial</span> <span class="tag">points</span> <span class="tag">create</span> <span class="tag">gdal</span> <span class="tag">regular</span> <span class="tag">grid</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">scattered</span> <span class="tag">gdal_vector_grid</span>

    **content:**

    ```xml
    <OGRVRTDataSource>
        <OGRVRTLayer name="dem">
            <SrcDataSource>dem.csv</SrcDataSource>
            <GeometryType>wkbPoint</GeometryType>
            <GeometryField encoding="PointFromColumns" x="Easting" y="Northing" z="Elevation"/>
        </OGRVRTLayer>
    </OGRVRTDataSource>
    ```

    **columns, switch columns, etc. OK, now the final step:**

    ```bash
    gdal vector grid invdist dem.vrt demv.tif
    ```

    **Or, if we do not wish to use a VRT file:**

    ```bash
    gdal vector grid invdist -l dem -oo X_POSSIBLE_NAMES=Easting \
    -oo Y_POSSIBLE_NAMES=Northing --zfield=Elevation dem.csv dem.tif
    ```

    **in the VRT file in the following way:**

    ```xml
    <GeometryField encoding="PointFromColumns" x="field_1" y="field_2" z="field_3"/>
    ```

    **Create a raster from a VRT datasource using inverse distance to a power**

    ```bash
    gdal vector grid invdist --power=2.0 --smoothing=1.0 --extent=85000,894000,89000,890000 \
        --size=400,400 -l dem dem.vrt dem.tif
    ```

    **Read values to interpolate from an attribute field**

    ```bash
    gdal vector grid invdist --zfield=Elevation --config GDAL_NUM_THREADS ALL_CPUS \
        --power=2.0 --smoothing=1.0 --extent=85000,894000,89000,890000 \
        --size=400,400 -l dem dem.vrt dem.tif
    ```


??? note "gdal_vector_index"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Index. Create a vector index of vector datasets.

    **Keywords:** <span class="tag">vector</span> <span class="tag">vetorial</span> <span class="tag">datasets</span> <span class="tag">create</span> <span class="tag">gdal</span> <span class="tag">operação</span> <span class="tag">index</span> <span class="tag">correspondente</span> <span class="tag">gdal_vector_index</span>

    **shape showing its bounds:**

    ```bash
    gdal vector index countries/*.shp index.gpkg
    ```

    **envelopes into the same output projection:**

    ```bash
    gdal vector index --output-crs EPSG:4326 --source-crs-field-name=src_srs countries/*.shp index.gpkg
    ```


??? note "gdal_vector_info"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Info. Get information on a vector dataset.

    **Keywords:** <span class="tag">information</span> <span class="tag">ler</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">inspecionar</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">gdal_vector_info</span> <span class="tag">info</span> <span class="tag">correspondente</span> <span class="tag">metadados</span> <span class="tag">vector</span>

    **Example of ``--where`` and quoting:**

    ```console
    --where "\"Corner Point Identifier\" LIKE '%__00_00'"
    ```

    **List all layers in a dataset using ``jq``**

    ```bash
    gdal vector info av_2056.gpkg --format json | jq ".layers[].name"
    ```

    **returns:**

    ```bash
    counties: geom (Geometry)
    states: geom (MultiPolygon)
    nation: geom (MultiPolygon)
    ```


??? note "gdal_vector_layer_algebra"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Layer Algebra. Perform algebraic operation between 2 layers

    **Keywords:** <span class="tag">layers</span> <span class="tag">algebraic</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">perform</span> <span class="tag">between</span> <span class="tag">gdal_vector_layer_algebra</span> <span class="tag">operação</span> <span class="tag">algebra</span> <span class="tag">layer</span> <span class="tag">correspondente</span> <span class="tag">operation</span>

    **Performs a union between both input and method layers.**

    ```bash
    $ gdal vector layer-algebra union input.shp method.shp output.shp
    ```


??? note "gdal_vector_make_point"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Make Point. Create point geometries from attribute fields containing coordinates.

    **Keywords:** <span class="tag">attribute</span> <span class="tag">from</span> <span class="tag">vetorial</span> <span class="tag">make</span> <span class="tag">create</span> <span class="tag">gdal</span> <span class="tag">containing</span> <span class="tag">coordinates</span> <span class="tag">point</span> <span class="tag">fields</span> <span class="tag">operação</span> <span class="tag">correspondente</span>

    **Sintaxe Básica**

    ```bash
    gdal_vector_make_point --help
    ```


??? note "gdal_vector_make_valid"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Make Valid. Fix validity of geometries of a vector dataset

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">make</span> <span class="tag">gdal</span> <span class="tag">validity</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">valid</span> <span class="tag">gdal_vector_make_valid</span> <span class="tag">geometries</span> <span class="tag">vector</span>

    **Basic use of make-valid**

    ```bash
    $ gdal vector make-valid in.gpkg out.gpkg --overwrite
    ```


??? note "gdal_vector_materialize"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Materialize. Materialize a piped dataset on disk to increase the efficiency of the following steps

    **Keywords:** <span class="tag">disk</span> <span class="tag">efficiency</span> <span class="tag">vetorial</span> <span class="tag">piped</span> <span class="tag">gdal</span> <span class="tag">materialize</span> <span class="tag">increase</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">steps</span> <span class="tag">correspondente</span> <span class="tag">following</span>

    **Reproject a GeoPackage file to CRS EPSG:32632 ("WGS 84 / UTM zone 32N"), materialize it to a temporary file and rasterize it**

    ```bash
    $ gdal pipeline ! read in.gpkg ! reproject --output-crs=EPSG:32632 ! \
                    ! materialize ! rasterize --resolution 10,10 ! write out.gpkg --overwrite
    ```


??? note "gdal_vector_partition"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Partition. Partition a vector dataset into multiple files.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">into</span> <span class="tag">files</span> <span class="tag">gdal</span> <span class="tag">partition</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">gdal_vector_partition</span> <span class="tag">multiple</span> <span class="tag">correspondente</span> <span class="tag">vector</span>

    **Create a partition based on the "continent" and "country" fields**

    ```bash
    $ gdal vector partition world_cities.gpkg out_directory --field continent,country --format Parquet
    ```

    **Create a partition based on the "country" field, filtering on cities with population bigger than 1 million, with a flat partitioning scheme**

    ```bash
    $ gdal pipeline ! read world_cities.gpkg ! filter --where "pop > 1e6" ! partition out_directory --field country --format GPKG --scheme flat
    ```

    **Create multiple Shapefiles, one for each geometry type, from a GeoPackage file, by grouping together POLYGON/MULTIPOLYGON or LINESTRING/MULTILINESTRING.**

    ```bash
    $ gdal vector pipeline ! read input.gpkg ! set-geom-type --multi ! partition out_directory --scheme flat --field OGR_GEOMETRY --format "ESRI Shapefile"
    ```

    **Split a file into files with at most 100,000 features.**

    ```bash
    $ gdal vector partition world_cities.gpkg out_directory --feature-limit 100000 --scheme flat --format Parquet
    ```

    **Sort a file spatially and split it into files with at most 100,000 features.**

    ```bash
    $ gdal vector pipeline read world_cities.gpkg ! sort ! partition out_directory --feature-limit 100000 --scheme flat --format Parquet
    ```


??? note "gdal_vector_pipeline"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Pipeline. Process a vector dataset applying several steps.

    **Keywords:** <span class="tag">process</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">several</span> <span class="tag">pipeline</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">gdal_vector_pipeline</span> <span class="tag">applying</span> <span class="tag">steps</span> <span class="tag">correspondente</span> <span class="tag">vector</span>

    **``gdal vector pipeline ! .... ! write out.gdalg.json``.**

    ```json
    {
        "type": "gdal_streamed_alg",
        "command_line": "gdal vector pipeline ! read in.gpkg ! reproject --output-crs=EPSG:32632"
    }
    ```

    **``stream`` output format and a non-significant output dataset name.**

    ```json
    {
        "type": "gdal_streamed_alg",
        "command_line": "gdal vector pipeline ! read in.gpkg ! reproject --output-crs=EPSG:32632 ! write --output-format=streamed streamed_dataset"
    }
    ```

    **Reproject a GeoPackage file to CRS EPSG:32632 ("WGS 84 / UTM zone 32N")**

    ```bash
    $ gdal vector pipeline ! read in.gpkg ! reproject --output-crs=EPSG:32632 ! write out.gpkg --overwrite
    ```

    **Serialize the command of a reprojection of a GeoPackage file in a GDALG file, and later read it**

    ```bash
    $ gdal vector pipeline ! read in.gpkg ! reproject --output-crs=EPSG:32632 ! write in_epsg_32632.gdalg.json --overwrite
    $ gdal vector info in_epsg_32632.gdalg.json
    ```

    **Union 2 source shapefiles (with similar structure), reproject them to EPSG:32632, keep only cities larger than 1 million inhabitants and write to a GeoPackage**

    ```bash
    $ gdal vector pipeline ! concat --single --output-crs=EPSG:32632 france.shp belgium.shp ! filter --where "pop > 1e6" ! write out.gpkg --overwrite
    ```


??? note "gdal_vector_rasterize"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Rasterize. Burns vector geometries into a raster

    **Keywords:** <span class="tag">rasterizar</span> <span class="tag">gdal_vector_rasterize</span> <span class="tag">burns</span> <span class="tag">vector</span> <span class="tag">vetorial</span> <span class="tag">queimar</span> <span class="tag">into</span> <span class="tag">criar raster</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">vetor para raster</span>

    **Burn a shapefile into a raster**

    ```bash
    gdal vector rasterize -b 1,2,3 --burn 255,0,0 -l mask mask.shp work.tif
    ```

    **The following would burn all "class A" buildings into the output elevation file, pulling the top elevation from the ROOF_H attribute.**

    ```bash
    gdal vector rasterize -a ROOF_H --where "class='A'" -l footprints footprints.shp city_dem.tif
    ```

    **The following would burn all polygons from :file:`footprint.shp` into a new 1000x1000 rgb TIFF as the color red.**

    ```bash
    gdal vector rasterize --burn 255,0,0 --ot Byte --size 1000,1000 -l footprints footprints.shp mask.tif
    ```

    **Burn a shapefile into a raster using a specific where condition to select features, and restrict the extent to the one of selected features**

    ```bash
    gdal pipeline read /vsizip/vsicurl/https://www2.census.gov/geo/tiger/TIGER2025/STATE/tl_2025_us_state.zip ! \
                    filter --where  "stusps = 'CA'" --update-extent ! \
                    rasterize  --burn 1 --size 1500,1500 --datatype Byte ! \
                    write out.png --overwrite
    ```


??? note "gdal_vector_read"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Read. Read a vector dataset (pipeline only)

    **Keywords:** <span class="tag">only</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">pipeline</span> <span class="tag">read</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">gdal_vector_read</span> <span class="tag">vector</span>

    **Read a GeoPackage file**

    ```bash
    $ gdal vector pipeline read input.gpkg ! ... [other commands here] ...
    ```

    **Read and buffer a single point**

    ```console
    $ gdal vector pipeline read "SRID=32145;POINT (442922 217537)" ! buffer 20 ! ... [other commands here] ...
    ```


??? note "gdal_vector_rename_layer"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Rename Layer. Rename layer(s) of a vector dataset.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">gdal_vector_rename_layer</span> <span class="tag">gdal</span> <span class="tag">rename</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">layer</span> <span class="tag">correspondente</span> <span class="tag">vector</span>

    **Rename a given layer to a user selected name.**

    ```console
    $ gdal vector rename-layer input.gpkg output.gpkg --input-layer "name with space" --output-layer "without_space"
    ```

    **Force layer names to ASCII, lower case, without space character and to be filename compatible.**

    ```console
    $ gdal vector rename-layer input.gpkg output_shp_directory --output-format "ESRI Shapefile" --ascii --lower-case --filename-compatible --reserved-characters " "
    ```


??? note "gdal_vector_reproject"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Reproject. Reproject a vector dataset.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">gdal_vector_reproject</span> <span class="tag">reproject</span> <span class="tag">correspondente</span> <span class="tag">vector</span>

    **Reproject a GeoPackage file to CRS EPSG:32632 ("WGS 84 / UTM zone 32N")**

    ```bash
    $ gdal vector reproject --output-crs=EPSG:32632 in.gpkg out.gpkg --overwrite
    ```

    **Reproject data using various CRS formats**

    ```bash
    # OGC CRS URI
    $ gdal vector reproject \
        --output-crs="http://www.opengis.net/def/crs/EPSG/0/3857" \
        natural_earth_vector.gpkg --layer=ne_10m_populated_places \
        places.json --overwrite
    
    # OGC CRS URN
    $ gdal vector reproject \
        --output-crs="urn:ogc:def:crs:EPSG::3857" \
        natural_earth_vector.gpkg --layer=ne_10m_populated_places \
        places.json --overwrite
    
    # PROJ string (legacy format)
    $ PROJ4="+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +k=1 +units=m +nadgrids=@null +wktext +no_defs +type=crs"
    $ gdal vector reproject \
        --output-crs="$PROJ4" \
        natural_earth_vector.gpkg --layer=ne_10m_populated_places \
        places.json --overwrite
    ```

    **Reproject a layer in a GeoPackage to Web Mercator GeoJSON**

    ```bash
    ERROR 1: Full reprojection failed, but partial is possible if you define OGR_ENABLE_PARTIAL_REPROJECTION configuration option to TRUE
    ERROR 1: PROJ: webmerc: Invalid latitude
    ERROR 1: Reprojection failed, err = 2049, further errors will be suppressed on the transform object.
    ```

    **Errors from PROJ relating to invalid coordinates (``ERROR 1: PROJ: webmerc: Invalid latitude``) will still be reported, but all features will be written to the output.**

    ```bash
    $ gdal vector reproject \
        --output-crs=EPSG:3857 \
        --config OGR_ENABLE_PARTIAL_REPROJECTION=TRUE \
        natural_earth_vector.gpkg --layer=ne_10m_time_zones \
        ne_10m_time_zones.json \
        --overwrite
    ```


??? note "gdal_vector_segmentize"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Segmentize. Segmentize geometries of a vector dataset.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">geometries</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">gdal_vector_segmentize</span> <span class="tag">segmentize</span> <span class="tag">vector</span>

    **Make sure that segments of geometries are no longer than one km (assuming the CRS is in meters)**

    ```bash
    $ gdal vector segmentize --max-length=1000 in.gpkg out.gpkg --overwrite
    ```


??? note "gdal_vector_select"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Select. Select a subset of fields from a vector dataset.

    **Keywords:** <span class="tag">from</span> <span class="tag">vetorial</span> <span class="tag">vector</span> <span class="tag">gdal</span> <span class="tag">select</span> <span class="tag">fields</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">gdal_vector_select</span> <span class="tag">correspondente</span> <span class="tag">subset</span>

    **``a field with " double quote`` with a Unix shell:**

    ```bash
    --fields "regular_field,\"a_field_with space, and comma\",\"a field with \\\" double quote\""
    ```

    **Select the EAS_ID field and the geometry field from a Shapefile**

    ```bash
    $ gdal vector select in.shp out.gpkg "EAS_ID,_ogr_geometry_" --overwrite
    ```

    **Remove sensitive fields from a layer**

    ```bash
    $ gdal vector select in.shp out.gpkg --exclude "name,surname,address" --overwrite
    ```


??? note "gdal_vector_set_field_type"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Set Field Type. Change the type of a field of a vector layer.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">change</span> <span class="tag">operação</span> <span class="tag">layer</span> <span class="tag">correspondente</span> <span class="tag">field</span> <span class="tag">type</span> <span class="tag">vector</span> <span class="tag">gdal_vector_set_field_type</span>

    **Change the type of a field given by its name to Integer**

    ```bash
    $ gdal vector set-field-type input.gpkg output.gpkg --field-name myfield --field-type Integer
    ```

    **Change the type of all fields of type Date to DateTime**

    ```bash
    $ gdal vector set-field-type input.gpkg output.gpkg --input-field-type Date --output-field-type DateTime
    ```


??? note "gdal_vector_set_geom_type"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Set Geom Type. Modify the geometry type of a vector dataset.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">geometry</span> <span class="tag">gdal</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">modify</span> <span class="tag">correspondente</span> <span class="tag">gdal_vector_set_geom_type</span> <span class="tag">type</span> <span class="tag">vector</span> <span class="tag">geom</span>

    **Convert a shapefile mixing polygons and multipolygons to a GeoPackage with multipolygons**

    ```bash
    $ gdal vector set-geom-type --geometry-type=MULTIPOLYGON in.shp out.gpkg --overwrite
    ```

    **Convert a GeoPackage with curve geometries to a Shapefile (that does not support them)**

    ```bash
    $ gdal vector set-geom-type --linear in.gpkg out.shp --overwrite
    ```


??? note "gdal_vector_simplify"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Simplify. Simplify geometries of a vector dataset.

    **Keywords:** <span class="tag">simplify</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">gdal_vector_simplify</span> <span class="tag">simplificar</span> <span class="tag">dataset</span> <span class="tag">simplificação</span> <span class="tag">operação</span> <span class="tag">suavizar</span> <span class="tag">correspondente</span> <span class="tag">geometries</span> <span class="tag">vector</span>

    **Simplify geometries using a tolerance of one km (assuming the CRS is in meters)**

    ```bash
    $ gdal vector simplify --tolerance=1000 in.gpkg out.gpkg --overwrite
    ```


??? note "gdal_vector_simplify_coverage"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Simplify Coverage. Simplify boundaries of a polygonal vector dataset.

    **Keywords:** <span class="tag">simplify</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">boundaries</span> <span class="tag">gdal_vector_simplify_coverage</span> <span class="tag">coverage</span> <span class="tag">simplificar</span> <span class="tag">dataset</span> <span class="tag">polygonal</span> <span class="tag">simplificação</span> <span class="tag">operação</span> <span class="tag">suavizar</span>

    **Simplify geometries using a tolerance of one square meter (assuming the CRS is in meters)**

    ```bash
    $ gdal vector simplify-coverage --tolerance=1 in.gpkg out.gpkg --overwrite
    ```

    **Using simplify-coverage as part of a vector pipeline**

    ```bash
    $ gdal vector pipeline ! read tl_2024_us_state.shp ! simplify-coverage --tolerance 2 ! set-geom-type --multi ! write out.gpkg --overwrite
    ```


??? note "gdal_vector_sort"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Sort. Spatially sort a vector dataset.

    **Keywords:** <span class="tag">spatially</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">sort</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">gdal_vector_sort</span> <span class="tag">vector</span>

    **Create a cloud-optimized Shapefile**

    ```bash
    $ gdal vector sort in.gpkg out.shp --method hilbert --lco SPATIAL_INDEX=YES
    ```


??? note "gdal_vector_sql"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Sql. Apply SQL statement(s) to a dataset.

    **Keywords:** <span class="tag">vetorial</span> <span class="tag">apply</span> <span class="tag">gdal</span> <span class="tag">gdal_vector_sql</span> <span class="tag">dataset</span> <span class="tag">filtrar</span> <span class="tag">query</span> <span class="tag">operação</span> <span class="tag">consulta</span> <span class="tag">sql</span> <span class="tag">statement</span> <span class="tag">correspondente</span>

    **Generate a GeoPackage file with a layer sorted by descending population**

    ```bash
    $ gdal vector sql in.gpkg out.gpkg --output-layer country_sorted_by_pop --sql="SELECT * FROM country ORDER BY pop DESC"
    ```

    **Generate a GeoPackage file with 2 SQL result layers**

    ```bash
    $ gdal vector sql in.gpkg out.gpkg --output-layer=beginning,end --sql="SELECT * FROM my_layer LIMIT 100" --sql="SELECT * FROM my_layer OFFSET 100000 LIMIT 100"
    ```

    **Modify in-place a GeoPackage dataset**

    ```bash
    $ gdal vector sql --update my.gpkg --sql "DELETE FROM countries WHERE pop > 1e6"
    ```

    **Add a new field to an existing layer of a GeoPackage**

    ```bash
    $ gdal vector sql --update my.gpkg --sql "ALTER TABLE countries ADD COLUMN abbrev STRING(10)"
    ```

    **Append to an existing layer of a GeoPackage file**

    ```bash
    $ gdal vector pipeline read europe.gpkg ! \
                           sql --sql "SELECT * FROM country WHERE pop > 1e6" ! \
                           write --append --output-layer-name=world world.gpkg
    ```


??? note "gdal_vector_swap_xy"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Swap Xy. Swap X and Y coordinates of geometries of a vector dataset.

    **Keywords:** <span class="tag">gdal_vector_swap_xy</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">coordinates</span> <span class="tag">swap</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">geometries</span> <span class="tag">vector</span>

    **Basic usage**

    ```bash
    $ gdal vector swap-xy in.gpkg out.gpkg --overwrite
    ```


??? note "gdal_vector_update"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Update. Update an existing vector dataset with an input vector dataset

    **Keywords:** <span class="tag">existing</span> <span class="tag">vector</span> <span class="tag">vetorial</span> <span class="tag">input</span> <span class="tag">gdal_vector_update</span> <span class="tag">gdal</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">with</span> <span class="tag">correspondente</span> <span class="tag">update</span>

    **Update existing :file:`out.gpkg` with content of :file:`in.gpkg`, using ``identifier`` as the key.**

    ```bash
    $ gdal vector update --key identifier in.gpkg out.gpkg
    ```


??? note "gdal_vector_write"

    <span class="badge badge-vetor">Vetor</span>

    Operação vetorial GDAL correspondente a: Write. Write a vector dataset (pipeline only)

    **Keywords:** <span class="tag">only</span> <span class="tag">write</span> <span class="tag">vetorial</span> <span class="tag">gdal</span> <span class="tag">pipeline</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">vector</span> <span class="tag">gdal_vector_write</span>

    **Write a GeoPackage file**

    ```bash
    $ gdal vector pipeline ... [other commands here] ... ! write out.gpkg --overwrite
    ```


??? note "ogr2ogr"

    <span class="badge badge-vetor">Vetor</span>

    Converte feições vetoriais (Shapefile, GeoJSON, GPKG) entre formatos, realiza filtros espaciais/atributos e reprojeta coordenadas.

    **Keywords:** <span class="tag">feições</span> <span class="tag">realiza</span> <span class="tag">converter</span> <span class="tag">conversão</span> <span class="tag">gpkg</span> <span class="tag">coordenadas</span> <span class="tag">converte</span> <span class="tag">ogr2ogr</span> <span class="tag">shapefile</span> <span class="tag">reprojeta</span> <span class="tag">vetoriais</span> <span class="tag">mudar formato</span>

    **``a field with " double quote`` with a Unix shell:**

    ```bash
    -select "regular_field,\"a_field_with space, and comma\",\"a field with \\\" double quote\""
    ```

    **Basic conversion from Shapefile to GeoPackage**

    ```bash
    ogr2ogr output.gpkg input.shp
    ```

    **Change the coordinate reference system from ``EPSG:4326`` to ``EPSG:3857``**

    ```bash
    ogr2ogr -s_srs EPSG:4326 -t_srs EPSG:3857 output.gpkg input.gpkg
    ```

    **Appending to an existing layer**

    ```bash
    ogr2ogr -append -f PostgreSQL PG:dbname=warmerda abc.tab
    ```

    **Clip input layer with a bounding box**

    ```bash
    ogr2ogr -spat -13.931 34.886 46.23 74.12 output.gpkg natural_earth_vector.gpkg
    ```

    **Filter Features by a ``-where`` clause**

    ```bash
    ogr2ogr -where "\"POP_EST\" < 1000000" \
      output.gpkg natural_earth_vector.gpkg ne_10m_admin_0_countries
    ```

    **Reprojecting from ETRS_1989_LAEA_52N_10E to EPSG:4326 and clipping to a bounding box**

    ```bash
    ogr2ogr -wrapdateline -t_srs EPSG:4326 -clipdst -5 40 15 55 france_4326.shp europe_laea.shp
    ```

    **layer used to fill the fifth field of the target layer.**

    ```bash
    ogr2ogr -append -fieldmap 2,-1,4 dst.shp src.shp
    ```

    **Outputting geometries with the CSV driver.**

    ```bash
    ogr2ogr -lco GEOMETRY=AS_XYZ TrackWaypoint.csv TrackWaypoint.kml
    ```

    **Extracting only geometries**

    ```console
    $ ogrinfo -so CadNSDI.gdb.zip PLSSPoint | grep 'Geometry Column'
    Geometry Column = SHAPE
    ```

    **and can thus be referenced directly in a SELECT statement.**

    ```bash
    ogr2ogr -sql "SELECT SHAPE FROM PLSSPoint" \
      -lco GEOMETRY=AS_XY -f CSV /vsistdout/ CadNSDI.gdb.zip
    ```

    **escaped and the final SELECT statement could look like:**

    ```bash
    ogr2ogr -sql "SELECT \"_ogr_geometry_\" FROM PLSSPoint" \
      -lco GEOMETRY=AS_XY -f CSV /vsistdout/ CadNSDI.shp
    ```

    **name is ``geometry`` when the source geometry column has no name.**

    ```bash
    ogr2ogr -sql "SELECT geometry FROM PLSSPoint" -dialect SQLite \
      -lco GEOMETRY=AS_XY -f CSV /vsistdout/ CadNSDI.shp
    ```


??? note "ogr_layer_algebra"

    <span class="badge badge-vetor">Vetor</span>

    Performs various Vector layer algebraic operations.

    **Keywords:** <span class="tag">algebraic</span> <span class="tag">operations</span> <span class="tag">ogr_layer_algebra</span> <span class="tag">performs</span> <span class="tag">layer</span> <span class="tag">various</span> <span class="tag">vector</span>

    **--------**

    ```bash
    ogr_layer_algebra [--help] [--help-general]
                        Union|Intersection|SymDifference|Identity|Update|Clip|Erase
                        -input_ds <path> [-input_lyr <name>]
                        -method_ds <path> [-method_lyr <name>]
                        -output_ds <path> [-output_lyr <name>] [-overwrite]
                        [-opt <NAME>=<VALUE>]...
                        [-f <format_name>] [-dsco <NAME>=<VALUE>]... [-lco <NAME>=<VALUE>]...
                        [-input_fields {NONE|ALL|<fld1>,<fl2>,...<fldN>}] [-method_fields {NONE|ALL|<fld1>,<fl2>,...<fldN>}]
                        [-nlt <geom_type>] [-a_srs <srs_def>]
    ```


??? note "ogrinfo"

    <span class="badge badge-vetor">Vetor</span>

    Lista informações sobre fontes de dados vetoriais (camadas, contagem de feições, atributos e geometria).

    **Keywords:** <span class="tag">filtrar</span> <span class="tag">query</span> <span class="tag">verificar</span> <span class="tag">ogrinfo</span> <span class="tag">dados</span> <span class="tag">feições</span> <span class="tag">lista</span> <span class="tag">fontes</span> <span class="tag">geometria</span> <span class="tag">info</span> <span class="tag">ler</span> <span class="tag">contagem</span>

    **Example of ``-where`` and quoting:**

    ```bash
    -where "\"Corner Point Identifier\" LIKE '%__00_00'"
    ```

    **Reporting the names of the layers in a NTF file**

    ```console
    $ ogrinfo wrk/SHETLAND_ISLANDS.NTF
    
    INFO: Open of `wrk/SHETLAND_ISLANDS.NTF'
    using driver `UK .NTF' successful.
    1: BL2000_LINK (Line String)
    2: BL2000_POLY (None)
    3: BL2000_COLLECTIONS (None)
    4: FEATURE_CLASSES (None)
    ```

    **Retrieving a summary (``-so``) of a layer without showing details about every feature**

    ```console
    $ ogrinfo \
      -so \
      natural_earth_vector.gpkg \
      ne_10m_admin_0_antarctic_claim_limit_lines
    
    INFO: Open of `natural_earth_vector.gpkg'
         using driver `GPKG' successful.
    
    Layer name: ne_10m_admin_0_antarctic_claim_limit_lines
    Geometry: Line String
    Feature Count: 23
    Extent: (-150.000000, -90.000000) - (160.100000, -60.000000)
    Layer SRS WKT:
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]]
    FID Column = fid
    Geometry Column = geom
    type: String (15.0)
    scalerank: Integer (0.0)
    featurecla: String (50.0)
    ```

    **Retrieving information on a file in JSON format without showing details about every feature**

    ```bash
    ogrinfo -json poly.shp
    ```

    **ogrinfo -json poly.shp**

    ```json
    {
      "description":"autotest/ogr/data/poly.shp",
      "driverShortName":"ESRI Shapefile",
      "driverLongName":"ESRI Shapefile",
      "layers":[
        {
          "name":"poly",
          "metadata":{
            "":{
              "DBF_DATE_LAST_UPDATE":"2018-08-02"
            },
            "SHAPEFILE":{
              "SOURCE_ENCODING":""
            }
          },
          "geometryFields":[
            {
              "name":"",
              "type":"Polygon",
              "nullable":true,
              "extent":[
                478315.53125,
                4762880.5,
                481645.3125,
                4765610.5
              ],
              "coordinateSystem":{
                "wkt":"PROJCRS[\"OSGB36 / British National Grid\",BASEGEOGCRS[\"OSGB36\",DATUM...",
                "projjson":{
                  "$schema":"https://proj.org/schemas/v0.6/projjson.schema.json",
                  "type":"ProjectedCRS",
                  "name":"OSGB36 / British National Grid",
                  "base_crs":{
                    "name":"OSGB36",
                    "datum":{
                      "type":"GeodeticReferenceFrame",
                      "name":"Ordnance Survey of Great Britain 1936",
                      "ellipsoid":{
                        "name":"Airy 1830",
                        "semi_major_axis":6377563.396,
                        "inverse_flattening":299.3249646
                      }
                    },
                    "coordinate_system":{
                      "subtype":"ellipsoidal",
                      "axis":[
                        {
                          "name":"Geodetic latitude",
                          "abbreviation":"Lat",
                          "direction":"north",
                          "unit":"degree"
                        },
                        {
                          "name":"Geodetic longitude",
                          "abbreviation":"Lon",
                          "direction":"east",
                          "unit":"degree"
                        }
                      ]
                    },
                    "id":{
                      "authority":"EPSG",
                      "code":4277
                    }
                  },
                  "conversion":{
                    "name":"British National Grid",
                    "method":{
                      "name":"Transverse Mercator",
                      "id":{
                        "authority":"EPSG",
                        "code":9807
                      }
                    },
                    "parameters":[
                      {
                        "name":"Latitude of natural origin",
                        "value":49,
                        "unit":"degree",
                        "id":{
                          "authority":"EPSG",
                          "code":8801
                        }
                      },
                      {
                        "name":"Longitude of natural origin",
                        "value":-2,
                        "unit":"degree",
                        "id":{
                          "authority":"EPSG",
                          "code":8802
                        }
                      },
                      {
                        "name":"Scale factor at natural origin",
                        "value":0.9996012717,
                        "unit":"unity",
                        "id":{
                          "authority":"EPSG",
                          "code":8805
                        }
                      },
                      {
                        "name":"False easting",
                        "value":400000,
                        "unit":"metre",
                        "id":{
                          "authority":"EPSG",
                          "code":8806
                        }
                      },
                      {
                        "name":"False northing",
                        "value":-100000,
                        "unit":"metre",
                        "id":{
                          "authority":"EPSG",
                          "code":8807
                        }
                      }
                    ]
                  },
                  "coordinate_system":{
                    "subtype":"Cartesian",
                    "axis":[
                      {
                        "name":"Easting",
                        "abbreviation":"E",
                        "direction":"east",
                        "unit":"metre"
                      },
                      {
                        "name":"Northing",
                        "abbreviation":"N",
                        "direction":"north",
                        "unit":"metre"
                      }
                    ]
                  },
                  "scope":"Engineering survey, topographic mapping.",
                  "area":"United Kingdom (UK) - offshore to boundary of UKCS within 49°45...",
                  "bbox":{
                    "south_latitude":49.75,
                    "west_longitude":-9,
                    "north_latitude":61.01,
                    "east_longitude":2.01
                  },
                  "id":{
                    "authority":"EPSG",
                    "code":27700
                  }
                },
                "dataAxisToSRSAxisMapping":[
                  1,
                  2
                ]
              }
            }
          ],
          "featureCount":10,
          "fields":[
            {
              "name":"AREA",
              "type":"Real",
              "width":12,
              "precision":3,
              "nullable":true,
              "uniqueConstraint":false
            },
            {
              "name":"EAS_ID",
              "type":"Integer64",
              "width":11,
              "nullable":true,
              "uniqueConstraint":false
            },
            {
              "name":"PRFEDEA",
              "type":"String",
              "width":16,
              "nullable":true,
              "uniqueConstraint":false
            }
          ]
        }
      ],
      "metadata":{
      },
      "domains":{
      },
      "relationships":{
      }
    }
    ```

    **Using :option:`-q` and an attribute query to restrict the output to certain features in a layer**

    ```console
    $ ogrinfo -q -ro \
        -where 'GLOBAL_LINK_ID=185878' \
        wrk/SHETLAND_ISLANDS.NTF BL2000_LINK
    
    Layer name: BL2000_LINK
    OGRFeature(BL2000_LINK):2
      LINE_ID (Integer) = 2
      GEOM_ID (Integer) = 2
      FEAT_CODE (String) = (null)
      GLOBAL_LINK_ID (Integer) = 185878
      TILE_REF (String) = SHETLAND I
      LINESTRING (419832.100 1069046.300,419820.100 1069043.800,...
    ```

    **Updating a value of an attribute in a shapefile with SQL by using the SQLite dialect**

    ```bash
    ogrinfo test.shp -dialect sqlite -sql "update test set attr='bar' where attr='foo'"
    ```

    **Adding a column to an input file**

    ```bash
    ogrinfo input.shp -sql "ALTER TABLE input ADD fieldX float"
    ```

    **Performing a SQL query without an input file**

    ```bash
    ogrinfo :memory: -sql "SELECT ST_Buffer(ST_GeomFromText('POINT(0 0)'), 1)"
    ```


??? note "ogrlineref"

    <span class="badge badge-vetor">Vetor</span>

    Create linear reference and provide some calculations using it

    **Keywords:** <span class="tag">calculations</span> <span class="tag">create</span> <span class="tag">provide</span> <span class="tag">ogrlineref</span> <span class="tag">reference</span> <span class="tag">using</span> <span class="tag">linear</span> <span class="tag">some</span>

    **--------**

    ```bash
    ogrlineref [--help] [--help-general] [-progress] [-quiet]
               [-f <format_name>] [-dsco <NAME>=<VALUE>]... [-lco <NAME>=<VALUE>]...
               [-create]
               [-l <src_line_datasource_name>] [-ln <layer_name>] [-lf <field_name>]
               [-p <src_repers_datasource_name>] [-pn <layer_name>] [-pm <pos_field_name>] [-pf <field_name>]
               [-r <src_parts_datasource_name>] [-rn <layer_name>]
               [-o <dst_datasource_name>] [-on <layer_name>] [-of <field_name>] [-s <step>]
               [-get_pos] [-x <long>] [-y <lat>]
               [-get_coord] [-m <position>]
               [-get_subline] [-mb <position>] [-me <position>]
    ```

    **a data needed for linear referencing (1 km parts):**

    ```bash
    ogrlineref -create -l roads.shp -p references.shp -pm dist -o parts.shp -s 1000 -progress
    ```


??? note "ogrmerge"

    <span class="badge badge-vetor">Vetor</span>

    Merge several vector datasets into a single one.

    **Keywords:** <span class="tag">juntar</span> <span class="tag">single</span> <span class="tag">datasets</span> <span class="tag">ogrmerge</span> <span class="tag">mosaico</span> <span class="tag">into</span> <span class="tag">several</span> <span class="tag">merge</span> <span class="tag">mesclar</span> <span class="tag">unir</span> <span class="tag">vector</span>

    **--------**

    ```bash
    ogrmerge [--help] [--help-general]
                -o <out_dsname> <src_dsname> [<src_dsname>]...
                [-f format] [-single] [-nln <layer_name_template>]
                [-update | -overwrite_ds] [-append | -overwrite_layer]
                [-src_geom_type <geom_type_name>[,<geom_type_name>]...]
                [-dsco <NAME>=<VALUE>]... [-lco <NAME>=<VALUE>]...
                [-s_srs <srs_def>] [-t_srs <srs_def> | -a_srs <srs_def>]
                [-progress] [-skipfailures] [--help-general]
    ```

    **Options specific to the :ref:`-single &lt;ogrmerge_single_option&gt;` option:**

    ```bash
    [-field_strategy FirstLayer|Union|Intersection]
    [-src_layer_field_name <name>]
    [-src_layer_field_content <layer_name_template>]
    ```

    **Creating a VRT with a layer for each input shapefile**

    ```bash
    ogrmerge -o merged.vrt *.shp
    ```

    **Creating a GeoPackage with a layer for each input shapefile**

    ```bash
    ogrmerge -o merged.gpkg *.shp
    ```

    **'germany' depending where it comes from:**

    ```bash
    ogrmerge -single -o merged.shp france.shp germany.shp -src_layer_field_name country
    ```


??? note "ogrtindex"

    <span class="badge badge-vetor">Vetor</span>

    Creates a tileindex.

    **Keywords:** <span class="tag">ogrtindex</span> <span class="tag">tileindex</span> <span class="tag">creates</span>

    **in the :file:`wrk` directory:**

    ```bash
    ogrtindex tindex.shp wrk/*.NTF
    ```

