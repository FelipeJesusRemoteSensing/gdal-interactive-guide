# 🗺️ Comandos Raster

Comandos para processamento de imagens matriciais (raster): conversão, reprojeção, recorte, mosaico, DEM, estatísticas e mais.

**Total:** 111 comandos

---

??? note "gdal"

    <span class="badge badge-raster">Raster</span>

    Main "gdal" entry point.

    **Keywords:** <span class="tag">main</span> <span class="tag">gdal</span> <span class="tag">point</span> <span class="tag">entry</span>

    **Getting information on the file :file:`utm.tif` (with JSON output)**

    ```console
    $ gdal info utm.tif
    ```

    **Converting file :file:`utm.tif` to GeoPackage raster**

    ```console
    $ gdal convert utm.tif utm.gpkg
    ```

    **Getting information on all available commands and subcommands as a JSON document.**

    ```console
    $ gdal --json-usage
    ```

    **Getting list of all formats supported by the current GDAL build, as text**

    ```console
    $ gdal --formats
    ```


??? note "gdal-config"

    <span class="badge badge-raster">Raster</span>

    Determines various information about a GDAL installation.

    **Keywords:** <span class="tag">information</span> <span class="tag">installation</span> <span class="tag">ler</span> <span class="tag">gdal-config</span> <span class="tag">gdal</span> <span class="tag">determines</span> <span class="tag">inspecionar</span> <span class="tag">info</span> <span class="tag">about</span> <span class="tag">metadados</span> <span class="tag">various</span> <span class="tag">verificar</span>

    **--------**

    ```bash
    gdal-config [OPTIONS]
    Options:
            [--prefix[=DIR]]
            [--libs]
            [--cflags]
            [--version]
            [--ogr-enabled]
            [--formats]
    ```


??? note "gdal2tiles"

    <span class="badge badge-raster">Raster</span>

    Generates directory with TMS tiles, KMLs and simple web viewers.

    **Keywords:** <span class="tag">gdal2tiles</span> <span class="tag">viewers</span> <span class="tag">kmls</span> <span class="tag">tiles</span> <span class="tag">directory</span> <span class="tag">simple</span> <span class="tag">with</span> <span class="tag">generates</span>

    **--------**

    ```bash
    gdal2tiles [--help] [--help-general]
                  [--legacy]
                  [-p <profile>] [-r resampling] [-s <srs>] [-z <zoom>]
                  [-e] [-a nodata] [-v] [-q] [-h] [-k] [-n] [-u <url>]
                  [-w <webviewer>] [-t <title>] [-c <copyright>]
                  [--processes=<NB_PROCESSES>] [--mpi] [--xyz]
                  [--tilesize=<PIXELS>] --tiledriver=<DRIVER> [--tmscompatible]
                  [--excluded-values=<EXCLUDED_VALUES>]
                  [--excluded-values-pct-threshold=<EXCLUDED_VALUES_PCT_THRESHOLD>]
                  [--nodata-values-pct-threshold=<NODATA_VALUES_PCT_THRESHOLD>]
                  [-g <googlekey] [-b <bingkey>] <input_file> [<output_dir>] [<COMMON_OPTIONS>]
    ```

    **Basic example**

    ```bash
    gdal2tiles --zoom=2-5 input.tif output_folder
    ```

    **MapML generation**

    ```bash
    gdal2tiles --zoom=16-18 -w mapml -p APSTILE --url "https://example.com" input.tif output_folder
    ```

    **MPI example**

    ```bash
    mpiexec -n $NB_PROCESSES gdal2tiles --mpi --config GDAL_CACHEMAX 500 --zoom=2-5 input.tif output_folder
    ```


??? note "gdal2xyz"

    <span class="badge badge-raster">Raster</span>

    Translates a raster file into `xyz` format.

    **Keywords:** <span class="tag">format</span> <span class="tag">geotiff</span> <span class="tag">gdal2xyz</span> <span class="tag">converter</span> <span class="tag">into</span> <span class="tag">raster</span> <span class="tag">translates</span> <span class="tag">resample</span> <span class="tag">recortar</span> <span class="tag">copiar</span> <span class="tag">file</span>

    **--------**

    ```bash
    gdal2xyz [--help] [--help-general]
        [-skip <factor>]
        [-srcwin <xoff> <yoff> <xsize> <ysize>]
        [-b <band>]... [-allbands]
        [-skipnodata]
        [-csv]
        [-srcnodata <value>] [-dstnodata <value>]
        <src_dataset> <dst_dataset>
    ```

    **--------**

    ```bash
    gdal2xyz -b 1 -b 2 -dstnodata 0 input.tif output.txt
    ```


??? note "gdal_calc"

    <span class="badge badge-raster">Raster</span>

    Calculadora raster para realizar operações algébricas sobre bandas (soma, subtração, NDVI, etc.).

    **Keywords:** <span class="tag">realizar</span> <span class="tag">bandas</span> <span class="tag">gdal_calc</span> <span class="tag">algébricas</span> <span class="tag">operações</span> <span class="tag">raster</span> <span class="tag">subtração</span> <span class="tag">ndvi</span> <span class="tag">calculadora</span> <span class="tag">soma</span>

    **--------**

    ```bash
    gdal_calc [--help] [--help-general]
                 --calc=expression --outfile=<out_filename> [-A <filename>]
                 [--A_band=<n>] [-B...-Z <filename>] [<other_options>]
    ```

    **Average of two files**

    ```bash
    gdal_calc -A input1.tif -B input2.tif --outfile=result.tif --calc="(A+B)/2"
    ```

    **floating point type before the division operation.**

    ```bash
    gdal_calc -A input.tif -B input2.tif --outfile=result.tif --calc="(A.astype(numpy.float64) + B) / 2"
    ```

    **Summing three files**

    ```bash
    gdal_calc -A input1.tif -B input2.tif -C input3.tif --outfile=result.tif --calc="A+B+C"
    ```

    **Combining three files into a 3D array and summing**

    ```bash
    gdal_calc -A input1.tif -A input2.tif -A input3.tif --outfile=result.tif --calc="numpy.sum(A,axis=0)".
    ```

    **Average of three files**

    ```bash
    gdal_calc -A input1.tif -B input2.tif -C input3.tif --outfile=result.tif --calc="(A+B+C)/3"
    ```

    **Average of three files, using 3D array**

    ```bash
    gdal_calc -A input1.tif input2.tif input3.tif --outfile=result.tif --calc="numpy.average(a,axis=0)".
    ```

    **Maximum of three files**

    ```bash
    gdal_calc -A input1.tif -B input2.tif -C input3.tif --outfile=result.tif --calc="numpy.max((A,B,C),axis=0)"
    ```

    **Maximum of three files, using a 3D array**

    ```bash
    gdal_calc -A input1.tif input2.tif input3.tif --outfile=result.tif --calc="numpy.max(A,axis=0)"
    ```

    **Setting values of zero and below to NODATA**

    ```bash
    gdal_calc -A input.tif --outfile=result.tif --calc="A*(A>0)" --NoDataValue=0
    ```

    **Using logical operator to keep a range of values from input**

    ```bash
    gdal_calc -A input.tif --outfile=result.tif --calc="A*logical_and(A>100,A<150)"
    ```

    **Performing two calculations and storing results in separate bands**

    ```bash
    gdal_calc -A input.tif --A_band=1 -B input.tif --B_band=2 \
      --outfile=result.tif --calc="(A+B)/2" --calc="B*logical_and(A>100,A<150)"
    ```

    **Add a raster to each band in a 3-band raster**

    ```bash
    gdal_calc -A 3band.tif -B 1band.tif --outfile result.tif --calc "A+B" --allBands A
    ```

    **Add two three-band rasters**

    ```bash
    gdal_calc -A 3band_a.tif -B 3band_b.tif --outfile result.tif --calc "A+B" --allBands A --allBands B
    ```


??? note "gdal_cli_from_c"

    <span class="badge badge-raster">Raster</span>

    The C API for ``gdal`` CLI algorithms is available in :file:`gdalalgorithm.h`.

    **Keywords:** <span class="tag">gdal</span> <span class="tag">gdalalgorithm</span> <span class="tag">algorithms</span> <span class="tag">gdal_cli_from_c</span> <span class="tag">available</span> <span class="tag">file</span>

    **For example:**

    ```cpp
    GDALAlgorithmRegistryH hRegistry = GDALGetGlobalAlgorithmRegistry();
    const char *const papszAlgPath[] = { "raster", "reproject", NULL };
    GDALAlgorithmH hAlg = GDALAlgorithmRegistryInstantiateAlgFromPath(hRegistry, papszAlgPath);
    GDALAlgorithmRegistryRelease(hRegistry);
    ```

    **For example:**

    ```cpp
    {
        GDALAlgorithmArgH hArg = GDALAlgorithmGetArg(hAlg, "input");
        GDALAlgorithmArgSetAsString(hArg, "byte.tif");
        GDALAlgorithmArgRelease(hArg);
    }
    {
        GDALAlgorithmArgH hArg = GDALAlgorithmGetArg(hAlg, "resolution");
        const double res[] = {60, 60};
        GDALAlgorithmArgSetAsDoubleList(hArg, 2, res);
        GDALAlgorithmArgRelease(hArg);
    }
    ```

    **it must be released with :cpp:func:`GDALAlgorithmFinalize`.**

    ```cpp
    int ret = 0;
    if( GDALAlgorithmRun(hAlg, NULL, NULL) )
    {
        // do something
        GDALAlgorithmArgRelease(hArg);
    }
    else
    {
        fprintf(stderr, "failure\n");
        ret = 1;
    }
    GDALAlgorithmFinalize(hAlg);
    GDALAlgorithmRelease(hAlg);
    ```

    **the output dataset with:**

    ```cpp
    GDALAlgorithmArgH hArg = GDALAlgorithmGetArg(hAlg, "output");
    GDALArgDatasetValueH hVal = GDALAlgorithmArgGetAsDatasetValue(hArg);
    GDALDatasetH hDS = GDALArgDatasetValueGetDatasetRef(hVal);
    ```

    **Putting all things together:**

    ```cpp
    #include "gdal.h"
    #include "gdalalgorithm.h"
    
    #include <stdio.h>
    
    int main()
    {
        GDALAllRegister();
        GDALAlgorithmRegistryH hRegistry = GDALGetGlobalAlgorithmRegistry();
        const char *const papszAlgPath[] = { "raster", "reproject", NULL };
        GDALAlgorithmH hAlg = GDALAlgorithmRegistryInstantiateAlgFromPath(hRegistry, papszAlgPath);
        GDALAlgorithmRegistryRelease(hRegistry);
        if( !hAlg )
        {
            fprintf(stderr, "cannot instantiate algorithm\n");
            return 1;
        }
    
        {
            GDALAlgorithmArgH hArg = GDALAlgorithmGetArg(hAlg, "input");
            GDALAlgorithmArgSetAsString(hArg, "byte.tif");
            GDALAlgorithmArgRelease(hArg);
        }
    
        {
            GDALAlgorithmArgH hArg = GDALAlgorithmGetArg(hAlg, "output-format");
            GDALAlgorithmArgSetAsString(hArg, "MEM");
            GDALAlgorithmArgRelease(hArg);
        }
    
        {
            GDALAlgorithmArgH hArg = GDALAlgorithmGetArg(hAlg, "dst-crs");
            GDALAlgorithmArgSetAsString(hArg, "EPSG:26711");
            GDALAlgorithmArgRelease(hArg);
        }
    
        {
            GDALAlgorithmArgH hArg = GDALAlgorithmGetArg(hAlg, "resolution");
            const double res[] = {60, 60};
            GDALAlgorithmArgSetAsDoubleList(hArg, 2, res);
            GDALAlgorithmArgRelease(hArg);
        }
    
        int ret = 0;
        if( GDALAlgorithmRun(hAlg, NULL, NULL) )
        {
            GDALAlgorithmArgH hArg = GDALAlgorithmGetArg(hAlg, "output");
            GDALArgDatasetValueH hVal = GDALAlgorithmArgGetAsDatasetValue(hArg);
            GDALDatasetH hDS = GDALArgDatasetValueGetDatasetRef(hVal);
            printf("width=%d, height=%d\n", GDALGetRasterXSize(hDS), GDALGetRasterYSize(hDS));
            GDALAlgorithmArgRelease(hArg);
        }
        else
        {
            fprintf(stderr, "failure\n");
            ret = 1;
        }
        GDALAlgorithmFinalize(hAlg);
        GDALAlgorithmRelease(hAlg);
        return ret;
    }
    ```


??? note "gdal_cli_from_cpp"

    <span class="badge badge-raster">Raster</span>

    ``gdal`` CLI algorithms are available as :cpp:class:`GDALAlgorithm` instances,

    **Keywords:** <span class="tag">gdal</span> <span class="tag">class</span> <span class="tag">gdalalgorithm</span> <span class="tag">algorithms</span> <span class="tag">instances</span> <span class="tag">available</span> <span class="tag">gdal_cli_from_cpp</span>

    **For example:**

    ```cpp
    auto &singleton = GDALGlobalAlgorithmRegistry::GetSingleton();
    GDALAlgorithm *algPtr = singleton.Instantiate("raster", "reproject");
    if (!algPtr)
    {
        std::cout << "cannot instantiate algorithm" << std::endl;
        return 1;
    }
    GDALAlgorithm &alg = *algPtr;
    ```

    **For example:**

    ```cpp
    alg["input"] = "byte.tif";
    alg["output"] = "out.tif";
    alg["dst-crs"] = "EPSG:26711";
    alg["resampling"] = "cubic";
    alg["resolution"] = std::vector<double>{60, 60};
    alg["overwrite"] = true;
    ```

    **For example:**

    ```cpp
    if (alg.Run() && alg.Finalize())
    {
        std::cout << "success" << std::endl;
        return 0;
    }
    else
    {
        std::cout << "failure" << std::endl;
        return 1;
    }
    ```

    **the output dataset with:**

    ```cpp
    GDALDataset *poDS = alg["output"].Get<GDALArgDatasetValue>().GetDatasetRef();
    ```

    **Putting all things together:**

    ```cpp
    #include "gdal.h"
    #include "gdalalgorithm.h"
    #include "gdal_dataset.h"
    
    #include <iostream>
    
    int main()
    {
        GDALAllRegister();
        auto& singleton = GDALGlobalAlgorithmRegistry::GetSingleton();
        GDALAlgorithm *algPtr = singleton.Instantiate("raster", "reproject");
        if( !algPtr )
        {
            std::cout << "cannot instantiate algorithm" << std::endl;
            return 1;
        }
        GDALAlgorithm& alg = *algPtr;
        alg["input"] = "byte.tif";
        alg["output-format"] = "MEM";
        alg["dst-crs"] = "EPSG:26711";
        alg["resampling"] = "cubic";
        alg["resolution"] = std::vector<double>{60, 60};
        if( alg.Run() )
        {
            GDALDataset *poDS = alg["output"].Get<GDALArgDatasetValue>().GetDatasetRef();
            std::cout << "width=" << poDS->GetRasterXSize() << std::endl;
            std::cout << "height=" << poDS->GetRasterYSize() << std::endl;
            alg.Finalize();
            return 0;
        }
        else
        {
            std::cout << "failure" << std::endl;
            return 1;
        }
    }
    ```


??? note "gdal_cli_from_python"

    <span class="badge badge-raster">Raster</span>

    Principles

    **Keywords:** <span class="tag">gdal_cli_from_python</span> <span class="tag">principles</span>

    **documentation page of each algorithm. They can also be obtained with**

    ```python
    >>> gdal.Algorithm("raster", "convert").GetArgNames()
    ['help', 'help-doc', 'version', 'json-usage', 'drivers', 'config', 'progress', 'output-format', 'open-option', 'input-format', 'input', 'output', 'creation-option', 'overwrite', 'append']
    ```

    **output, you can get the return value of :py:func:`osgeo.gdal.Run` and call the**

    ```python
    alg = gdal.Run("raster", "info", input="byte.tif")
    info_as_dict = alg.Output()
    ```

    **will be called at the exit of the context manager.**

    ```python
    with gdal.Run("raster reproject", input=src_ds, output_format="MEM",
                  dst_crs="EPSG:4326") as alg:
        values = alg.Output().ReadAsArray()
    ```

    **still references the dataset, it will not be closed and may still be accessed:**

    ```python
    >>> alg = gdal.Run("raster reproject", input=src_ds, output_format="MEM",
                   dst_crs="EPSG:4326")
    >>> out_ds = alg.Output()
    >>> print(out_ds.GetRefCount())
    2
    >>> alg.Finalize()
    >>> print(out_ds.GetRefCount())
    1
    >>> alg.Output().ReadAsArray() # no longer available from the algorithm
    AttributeError: 'NoneType' object has no attribute 'ReadAsMaskedArray'
    >>> out_ds.ReadAsArray() # still accessible via the existing reference
    array([[-9999., -9999., -9999., ...,
    ```

    **The above example running "gdal raster convert" can also be rewritten as:**

    ```python
    >>> from osgeo import gdal
    >>> gdal.alg.raster.convert(input="in.tif", output="out.tif")
    ```

    **The documentation of the function lists argument names, types and semantics:**

    ```python
    >>> from osgeo import gdal
    >>> help(gdal.alg.raster.convert)
    
        Help on function convert:
    
        convert(input: Union[List[osgeo.gdal.Dataset], List[str], List[os.PathLike[str]]], output: Union[osgeo.gdal.Dataset, str, os.PathLike[str]], input_format: Union[List[str], str, NoneType] = None, open_option: Union[List[str], str, NoneType] = None, output_format: Optional[str] = None, creation_option: Union[List[str], str, NoneType] = None, overwrite: Optional[bool] = None, append: Optional[bool] = None)
            Convert a raster dataset.
    
            Consult https://gdal.org/programs/gdal_raster_convert.html for more details.
    
            Parameters
            ----------
            input: Union[List[gdal.Dataset], List[str], List[os.PathLike[str]]]
                Input raster datasets
            output: Union[gdal.Dataset, str, os.PathLike[str]]
                Output raster dataset
            input_format: Optional[Union[List[str], str]]=None
                Input formats
            open_option: Optional[Union[List[str], dict, str]]=None
                Open options
            output_format: Optional[str]=None
                Output format ("GDALG" allowed)
            creation_option: Optional[Union[List[str], dict, str]]=None
                Creation option
            overwrite: Optional[bool]=None
                Whether overwriting existing output is allowed
            append: Optional[bool]=None
                Append as a subdataset to existing output
    
    
            Output parameters
            -----------------
            output: gdal.ArgDatasetValue
                Output raster dataset
    ```

    **Getting information on a raster dataset as JSON**

    ```python
    from osgeo import gdal
    
    gdal.UseExceptions()
    info_as_dict = gdal.alg.raster.info(input="byte.tif").Output()
    ```

    **Converting a georeferenced netCDF file to cloud-optimized GeoTIFF**

    ```python
    from osgeo import gdal
    
    gdal.UseExceptions()
    gdal.alg.raster.convert(input="in.tif", output="out.tif", output_format="COG", overwrite=True)
    ```

    **or**

    ```python
    from osgeo import gdal
    
    gdal.UseExceptions()
    gdal.Run("raster", "convert", input="in.tif", output="out.tif",
             output_format="COG", overwrite=True)
    ```

    **or**

    ```python
    from osgeo import gdal
    
    gdal.UseExceptions()
    gdal.Run(["raster", "convert"], {"input": "in.tif", "output": "out.tif", "output-format": "COG", "overwrite": True})
    ```

    **Reprojecting a GeoTIFF file to a Deflate-compressed tiled GeoTIFF file**

    ```python
    from osgeo import gdal
    
    gdal.UseExceptions()
    gdal.alg.raster.reproject(
              input="in.tif", output="out.tif",
              dst_crs="EPSG:4326",
              creation_options={ "TILED": "YES", "COMPRESS": "DEFLATE"})
    ```

    **Reprojecting a (possibly in-memory) dataset to a in-memory dataset**

    ```python
    from osgeo import gdal
    
    gdal.UseExceptions()
    with gdal.alg.raster.reproject(input=src_ds, output_format="MEM",
                  dst_crs="EPSG:4326") as alg:
        values = alg.Output().ReadAsArray()
    ```

    **Getting information on a vector dataset as JSON**

    ```python
    from osgeo import gdal
    
    gdal.UseExceptions()
    info_as_dict = gdal.alg.vector.info(input="poly.gpkg").Output()
    ```

    **Converting a shapefile to a GeoPackage**

    ```python
    from osgeo import gdal
    
    gdal.UseExceptions()
    gdal.alg.vector.convert(input="in.shp", output="out.gpkg", overwrite=True)
    ```

    **Perform raster reprojection and gets the result as a streamed dataset.**

    ```python
    from osgeo import gdal
    
    gdal.UseExceptions()
    with gdal.alg.pipeline(pipeline="read byte.tif ! reproject --output-crs EPSG:4326 --resampling cubic") as alg:
        ds = alg.Output()
        # do something with the dataset
    ```


??? note "gdal_cli_gdalg"

    <span class="badge badge-raster">Raster</span>

    A subset of subcommands of :program:`gdal` support generating

    **Keywords:** <span class="tag">subcommands</span> <span class="tag">program</span> <span class="tag">generating</span> <span class="tag">gdal</span> <span class="tag">gdal_cli_gdalg</span> <span class="tag">support</span> <span class="tag">subset</span>

    **streamed dataset.**

    ```python
    from osgeo import gdal
    gdal.UseExceptions()
    
    alg = gdal.GetGlobalAlgorithmRegistry()["vector"]["geom"]["set-type"]
    alg["input"] = src_ds
    alg["output"] = ""
    alg["output-format"] = "stream"
    alg["geometry-type"] = "LINESTRING Z"
    
    alg.Run()
    
    out_ds = alg["output"].GetDataset()
    out_lyr = out_ds.GetLayer(0)
    for f in our_lyr:
        f.DumpReadable()
    ```

    **Serialize the command of a reprojection of a GeoPackage file in a GDALG file, and later read it**

    ```bash
    $ gdal vector pipeline ! read in.gpkg ! reproject --output-crs=EPSG:32632 ! write in_epsg_32632.gdalg.json --overwrite
    $ gdal vector info in_epsg_32632.gdalg.json
    ```

    **The content of :file:`in_epsg_32632.gdalg.json` is:**

    ```json
    {
        "type": "gdal_streamed_alg",
        "command_line": "gdal vector pipeline ! read in.gpkg ! reproject --output-crs=EPSG:32632"
    }
    ```


??? note "gdal_contour"

    <span class="badge badge-raster">Raster</span>

    Gera curvas de nível (vetores) a partir de um Modelo Digital de Elevação raster.

    **Keywords:** <span class="tag">contorno</span> <span class="tag">gera</span> <span class="tag">vetores</span> <span class="tag">isolinhas</span> <span class="tag">raster</span> <span class="tag">curvas</span> <span class="tag">gdal_contour</span> <span class="tag">digital</span> <span class="tag">nível</span> <span class="tag">elevação</span> <span class="tag">partir</span> <span class="tag">curvas de nível</span>

    **--------**

    ```bash
    gdal_contour [--help] [--help-general]
                 [-b <band>] [-a <attribute_name>] [-amin <attribute_name>] [-amax <attribute_name>]
                 [-3d] [-inodata] [-snodata <n>] [-f <formatname>] [-i <interval>]
                 [-dsco <NAME>=<VALUE>]... [-lco <NAME>=<VALUE>]...
                 [-off <offset>] [-fl <level> <level>...] [-e <exp_base>]
                 [-nln <outlayername>] [-q] [-p] [-gt <n>|unlimited]
                 <src_filename> <dst_filename>
    ```

    **Creating contours from a DEM**

    ```bash
    gdal_contour -a elev dem.tif contour.shp -i 10.0
    ```

    **Creating polygonal contours from a DEM**

    ```bash
    $ cat test.asc
    ncols        2
    nrows        2
    xllcorner    0
    yllcorner    0
    cellsize     1
    4 15
    25 36
    
    $ gdal_contour test.asc -f GeoJSON /vsistdout/ -i 10 -p -amin min -amax max
    ```

    **and ``max`` attributes, including the minimum and maximum values from the raster.**

    ```bash
    {
        "type": "FeatureCollection",
        "name": "contour",
        "features": [
        { "type": "Feature", "properties": { "ID": 0, "min": 4.0, "max": 10.0 }, "geometry": { "type": "MultiPolygon", "coordinates": [ [ [ [ 0.5, 1.214285714285714 ], [ 1.045454545454545, 1.5 ], [ 1.045454545454545, 2.0 ], [ 1.0, 2.0 ], [ 0.5, 2.0 ], [ 0.0, 2.0 ], [ 0.0, 1.5 ], [ 0.0, 1.214285714285714 ], [ 0.5, 1.214285714285714 ] ] ] ] } },
        { "type": "Feature", "properties": { "ID": 1, "min": 10.0, "max": 20.0 }, "geometry": { "type": "MultiPolygon", "coordinates": [ [ [ [ 1.5, 1.261904761904762 ], [ 2.0, 1.261904761904762 ], [ 2.0, 1.5 ], [ 2.0, 2.0 ], [ 1.5, 2.0 ], [ 1.045454545454545, 2.0 ], [ 1.045454545454545, 1.5 ], [ 0.5, 1.214285714285714 ], [ 0.0, 1.214285714285714 ], [ 0.0, 1.0 ], [ 0.0, 0.738095238095238 ], [ 0.5, 0.738095238095238 ], [ 1.5, 1.261904761904762 ] ] ] ] } },
        { "type": "Feature", "properties": { "ID": 2, "min": 20.0, "max": 30.0 }, "geometry": { "type": "MultiPolygon", "coordinates": [ [ [ [ 0.954545454545455, 0.0 ], [ 0.954545454545455, 0.5 ], [ 1.5, 0.785714285714286 ], [ 2.0, 0.785714285714286 ], [ 2.0, 1.0 ], [ 2.0, 1.261904761904762 ], [ 1.5, 1.261904761904762 ], [ 0.5, 0.738095238095238 ], [ 0.0, 0.738095238095238 ], [ 0.0, 0.5 ], [ 0.0, 0.0 ], [ 0.5, 0.0 ], [ 0.954545454545455, 0.0 ] ] ] ] } },
        { "type": "Feature", "properties": { "ID": 3, "min": 30.0, "max": 36.0 }, "geometry": { "type": "MultiPolygon", "coordinates": [ [ [ [ 1.499999909090926, 0.0 ], [ 1.0, 0.0 ], [ 0.954545454545455, 0.0 ], [ 0.954545454545455, 0.5 ], [ 1.5, 0.785714285714286 ], [ 2.0, 0.785714285714286 ], [ 2.0, 0.500000047619043 ], [ 1.5, 0.500000047619043 ], [ 1.499999909090926, 0.5 ], [ 1.499999909090926, 0.0 ] ] ] ] } }
        ]
    }
    ```

    **Creating contours from a DEM with fixed levels**

    ```bash
    $ cat test.asc
    ncols        2
    nrows        2
    xllcorner    0
    yllcorner    0
    cellsize     1
    4 15
    25 36
    
    $ gdal_contour test.asc -f GeoJSON /vsistdout/ -fl 10 20 -p -amin min -amax max
    ```

    **(case insensitive) can be used:**

    ```bash
    $ cat test.asc
    ncols        2
    nrows        2
    xllcorner    0
    yllcorner    0
    cellsize     1
    4 15
    25 36
    
    $ gdal_contour test.asc -f GeoJSON /vsistdout/ -fl MIN 10 20 MAX -p -amin min -amax max
    ```

    **Creating contours from a DEM specifying an interval and fixed levels at the same time**

    ```bash
    $ cat test.asc
    ncols        2
    nrows        2
    xllcorner    0
    yllcorner    0
    cellsize     1
    4 15
    25 36
    
    $ gdal_contour test.asc -f GeoJSON /vsistdout/ -i 10 -fl 15 -p -amin min -amax max
    ```


??? note "gdal_convert"

    <span class="badge badge-raster">Raster</span>

    Convert a dataset.

    **Keywords:** <span class="tag">convert</span> <span class="tag">gdal_convert</span> <span class="tag">dataset</span>

    **Converting file :file:`utm.tif` to GeoPackage raster**

    ```console
    $ gdal convert utm.tif utm.gpkg
    ```


??? note "gdal_create"

    <span class="badge badge-raster">Raster</span>

    Create a raster file (without source dataset).

    **Keywords:** <span class="tag">gdal_create</span> <span class="tag">create</span> <span class="tag">source</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">without</span> <span class="tag">file</span>

    **Initialize a new GeoTIFF file with a uniform value of 10**

    ```bash
    gdal_create -outsize 20 20 -a_srs EPSG:4326 -a_ullr 2 50 3 49 -burn 10 out.tif
    ```

    **Create a PDF file from a XML composition file**

    ```bash
    gdal_create -co COMPOSITION_FILE=composition.xml out.pdf
    ```

    **Initialize a blank GeoTIFF file from an input one**

    ```bash
    gdal_create -if prototype.tif output.tif
    ```


??? note "gdal_dataset"

    <span class="badge badge-raster">Raster</span>

    Commands to manage datasets (identify, copy, rename, delete)

    **Keywords:** <span class="tag">copy</span> <span class="tag">delete</span> <span class="tag">datasets</span> <span class="tag">rename</span> <span class="tag">manage</span> <span class="tag">gdal_dataset</span> <span class="tag">identify</span> <span class="tag">commands</span>

    **Sintaxe Básica**

    ```bash
    gdal_dataset --help
    ```


??? note "gdal_dataset_copy"

    <span class="badge badge-raster">Raster</span>

    Copy files of a dataset

    **Keywords:** <span class="tag">copy</span> <span class="tag">gdal_dataset_copy</span> <span class="tag">files</span> <span class="tag">dataset</span>

    **Copy a dataset**

    ```console
    $ gdal dataset copy source.tif destination.tif
    ```


??? note "gdal_dataset_delete"

    <span class="badge badge-raster">Raster</span>

    Delete dataset(s).

    **Keywords:** <span class="tag">gdal_dataset_delete</span> <span class="tag">dataset</span> <span class="tag">delete</span>

    **Delete a dataset**

    ```console
    $ gdal dataset delete NE1_50M_SR_W.tif
    ```


??? note "gdal_dataset_identify"

    <span class="badge badge-raster">Raster</span>

    Identify driver opening dataset(s).

    **Keywords:** <span class="tag">opening</span> <span class="tag">driver</span> <span class="tag">gdal_dataset_identify</span> <span class="tag">dataset</span> <span class="tag">identify</span>

    **Identifying a single file**

    ```console
    $ gdal dataset identify NE1_50M_SR_W.tif
    
    NE1_50M_SR_W.tif: GTiff
    ```

    **Identifying a single file with JSON output**

    ```console
    $ gdal dataset identify --of=JSON NE1_50M_SR_W.tif
    ```

    **$ gdal dataset identify --of=JSON NE1_50M_SR_W.tif**

    ```json
    [
       {
         "name": "NE1_50M_SR_W.tif",
         "driver": "GTiff"
       }
    ]
    ```

    **Recursive mode will scan subfolders and report the data format**

    ```bash
    $ gdal dataset identify -r 50m_raster/
    
    NE1_50M_SR_W/ne1_50m.jpg: JPEG
    NE1_50M_SR_W/ne1_50m.png: PNG
    NE1_50M_SR_W/ne1_50m_20pct.tif: GTiff
    NE1_50M_SR_W/ne1_50m_band1.tif: GTiff
    NE1_50M_SR_W/ne1_50m_print.png: PNG
    NE1_50M_SR_W/NE1_50M_SR_W.aux: HFA
    NE1_50M_SR_W/NE1_50M_SR_W.tif: GTiff
    NE1_50M_SR_W/ne1_50m_sub.tif: GTiff
    NE1_50M_SR_W/ne1_50m_sub2.tif: GTiff
    ```

    **Recursively scans subfolders and reports detailed information into a CSV file**

    ```bash
    $ gdal dataset identify --output out.csv --detailed -r 50m_raster/
    ```

    **Check if a GeoTIFF file is cloud optimized using ``--detailed``**

    ```bash
    $ gdal dataset identify /vsicurl/https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/36/Q/WD/2020/7/S2A_36QWD_20200701_0_L2A/TCI.tif --detailed
    ```


??? note "gdal_dataset_rename"

    <span class="badge badge-raster">Raster</span>

    Rename files of a dataset

    **Keywords:** <span class="tag">gdal_dataset_rename</span> <span class="tag">files</span> <span class="tag">rename</span> <span class="tag">dataset</span>

    **Rename a dataset**

    ```console
    $ gdal dataset rename old_name.tif new_name.tif
    ```


??? note "gdal_driver_cog_validate"

    <span class="badge badge-raster">Raster</span>

    Validate if a TIFF file is a Cloud Optimized GeoTIFF

    **Keywords:** <span class="tag">tiff</span> <span class="tag">validate</span> <span class="tag">gdal_driver_cog_validate</span> <span class="tag">cloud</span> <span class="tag">optimized</span> <span class="tag">geotiff</span> <span class="tag">file</span>

    **--------**

    ```bash
    gdal driver cog validate /vsicurl/https://example.com/some.tif
    ```


??? note "gdal_driver_gpkg_repack"

    <span class="badge badge-raster">Raster</span>

    Repack/vacuum in-place a GeoPackage dataset

    **Keywords:** <span class="tag">repack</span> <span class="tag">gdal_driver_gpkg_repack</span> <span class="tag">dataset</span> <span class="tag">vacuum</span> <span class="tag">geopackage</span> <span class="tag">place</span>

    **--------**

    ```bash
    gdal driver gpkg repack my.gpkg
    ```


??? note "gdal_driver_gpkg_validate"

    <span class="badge badge-raster">Raster</span>

    Validate conformance of a GeoPackage dataset against the GeoPackage specification

    **Keywords:** <span class="tag">against</span> <span class="tag">gdal_driver_gpkg_validate</span> <span class="tag">validate</span> <span class="tag">conformance</span> <span class="tag">dataset</span> <span class="tag">geopackage</span> <span class="tag">specification</span>

    **--------**

    ```bash
    gdal driver gpkg validate my.gpkg
    ```


??? note "gdal_driver_gti_create"

    <span class="badge badge-raster">Raster</span>

    Create an index of raster datasets compatible with the GDAL Tile Index (GTI) driver.

    **Keywords:** <span class="tag">gdal_driver_gti_create</span> <span class="tag">driver</span> <span class="tag">datasets</span> <span class="tag">create</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">index</span> <span class="tag">tile</span> <span class="tag">compatible</span> <span class="tag">with</span>

    **for use by the GDAL GTI / Virtual Raster Tile Index driver.**

    ```bash
    gdal driver gti create --ot Byte --resolution=60,60 --band-count=3 --color-interpretation=Red,Green,Blue *.tif tile_index.gti.gpkg
    ```


??? note "gdal_driver_openfilegdb_repack"

    <span class="badge badge-raster">Raster</span>

    Repack in-place a FileGeodatabase dataset

    **Keywords:** <span class="tag">repack</span> <span class="tag">gdal_driver_openfilegdb_repack</span> <span class="tag">dataset</span> <span class="tag">filegeodatabase</span> <span class="tag">place</span>

    **--------**

    ```bash
    gdal driver openfilegdb repack my.gdb
    ```


??? note "gdal_driver_parquet_create_metadata_file"

    <span class="badge badge-raster">Raster</span>

    Create the _metadata file for a partitioned Parquet dataset

    **Keywords:** <span class="tag">create</span> <span class="tag">partitioned</span> <span class="tag">_metadata</span> <span class="tag">dataset</span> <span class="tag">parquet</span> <span class="tag">gdal_driver_parquet_create_metadata_file</span> <span class="tag">file</span>

    **--------**

    ```bash
    gdal driver parquet create-metadata-file --input partitioned/0.parquet \
                --input partitioned/1.parquet --output partitioned/_metadata
    ```


??? note "gdal_driver_pdf_list_layers"

    <span class="badge badge-raster">Raster</span>

    Return the list of layers of a PDF file.

    **Keywords:** <span class="tag">layers</span> <span class="tag">list</span> <span class="tag">return</span> <span class="tag">gdal_driver_pdf_list_layers</span> <span class="tag">file</span>

    **because the PDF driver needs to have read support for that operation.**

    ```bash
    Usage: gdal driver pdf list-layers [OPTIONS] <INPUT>
    
    List layers of a PDF dataset
    
    Positional arguments:
      -i, --input <INPUT>                                  Input raster or vector dataset [required]
    
    Common Options:
      -h, --help                                           Display help message and exit
      --json-usage                                         Display usage as JSON document and exit
      --config <KEY>=<VALUE>                               Configuration option [may be repeated]
    
    Options:
      -f, --of, --format, --output-format <OUTPUT-FORMAT>  Output format. OUTPUT-FORMAT=json|text (default: json)
    ```

    **Return the list of layers of a PDF file as a JSON array**

    ```bash
    gdal driver pdf list-layers autotest/gdrivers/data/pdf/adobe_style_geospatial.pdf
    ```

    **returns:**

    ```json
    [
      "New_Data_Frame",
      "New_Data_Frame.Graticule",
      "Layers",
      "Layers.Measured_Grid",
      "Layers.Graticule"
    ]
    ```

    **Return the list of layers of a PDF file as as a text list**

    ```bash
    gdal driver pdf list-layers --of=text autotest/gdrivers/data/pdf/adobe_style_geospatial.pdf
    ```

    **returns:**

    ```bash
    New_Data_Frame
    New_Data_Frame.Graticule
    Layers
    Layers.Measured_Grid
    Layers.Graticule
    ```


??? note "gdal_driver_zarr_add_georeferencing_convention"

    <span class="badge badge-raster">Raster</span>

    Add a georeferencing convention to an existing ZARR dataset

    **Keywords:** <span class="tag">zarr</span> <span class="tag">existing</span> <span class="tag">georeferencing</span> <span class="tag">convention</span> <span class="tag">gdal_driver_zarr_add_georeferencing_convention</span> <span class="tag">dataset</span>

    **because the Zar driver may not be built.**

    ```bash
    Usage: gdal driver zarr add-georeferencing-convention [OPTIONS] <INPUT> <CONVENTION>
    
    Add a georeferencing convention to an existing ZARR dataset
    
    Positional arguments:
      -i, --input <INPUT>        Input multidimensional raster dataset [required]
      --convention <CONVENTION>  Georeferencing convention. CONVENTION=GDAL|spatial_proj [required]
    
    Common Options:
      -h, --help                 Display help message and exit
      --json-usage               Display usage as JSON document and exit
      --config <KEY>=<VALUE>     Configuration option [may be repeated]
    ```

    **Add the ``spatial_proj`` convention.**

    ```bash
    gdal driver zarr add-georeferencing-conventions my.zarr spatial_proj
    ```


??? note "gdal_edit"

    <span class="badge badge-raster">Raster</span>

    Edit in place various information of an existing GDAL dataset.

    **Keywords:** <span class="tag">information</span> <span class="tag">edit</span> <span class="tag">gdal_edit</span> <span class="tag">existing</span> <span class="tag">ler</span> <span class="tag">gdal</span> <span class="tag">inspecionar</span> <span class="tag">dataset</span> <span class="tag">info</span> <span class="tag">metadados</span> <span class="tag">place</span> <span class="tag">various</span>

    **--------**

    ```bash
    gdal_edit [--help] [--help-general] [-ro] [-a_srs <srs_def>]
            [-a_ullr <ulx> <uly> <lrx> <lry>] [-a_ulurll <ulx> <uly> <urx> <ury> <llx> <lly>]
            [-tr <xres> <yres>] [-unsetgt] [-unsetrpc] [-a_nodata <value>] [-unsetnodata]
            [-a_coord_epoch <epoch>] [-unsetepoch]
            [-unsetstats] [-stats] [-approx_stats]
            [-setstats <min> <max> <mean> <stddev>]
            [-scale <value>] [-offset <value>] [-units <value>]
            [-colorinterp_<X> {red|green|blue|alpha|gray|undefined|pan|coastal|rededge|nir|swir|mwir|lwir|...}]...
            [-gcp <pixel> <line> <easting> <northing> [<elevation>]]...
            [-unsetmd] [-oo <NAME>=<VALUE>]... [-mo <META-TAG>=<VALUE>]...
            <datasetname>
    ```

    **Override the spatial bounds of a dataset and assign metadata values**

    ```bash
    gdal_edit -mo DATUM=WGS84 -mo PROJ=GEODETIC -a_ullr 7 47 8 46 test.ecw
    ```

    **Assign scale and offset values to dataset**

    ```bash
    gdal_edit -scale 1e3 1e4 -offset 0 10 twoBand.tif
    ```


??? note "gdal_external"

    <span class="badge badge-raster">Raster</span>

    Execute an external program as a step of a pipeline

    **Keywords:** <span class="tag">step</span> <span class="tag">program</span> <span class="tag">pipeline</span> <span class="tag">gdal_external</span> <span class="tag">external</span> <span class="tag">execute</span>

    **Pipeline running a `QGIS processing algorithm &lt;https://docs.qgis.org/latest/en/docs/user_manual/processing/standalone.html&gt;`__ to smooth a DEM before computing the hillshade.**

    ```bash
    $ gdal pipeline --config GDAL_ENABLE_EXTERNAL=YES \
        read dem.tif ! \
        external "qgis_process run native:rasterfeaturepreservingsmoothing -- INPUT=<INPUT> OUTPUT=<OUTPUT>" ! \
        hillshade ! \
        write out.tif
    ```


??? note "gdal_fillnodata"

    <span class="badge badge-raster">Raster</span>

    Fill raster regions by interpolation from edges.

    **Keywords:** <span class="tag">from</span> <span class="tag">fill</span> <span class="tag">raster</span> <span class="tag">gdal_fillnodata</span> <span class="tag">interpolation</span> <span class="tag">regions</span> <span class="tag">edges</span>

    **--------**

    ```bash
    gdal_fillnodata [--help] [--help-general] [-q] [-md <max_distance>]
               [-si <smoothing_iterations>] [-o <name>=<value> [<name>=<value> ...]]
               [-mask <filename>] [-interp {inv_dist,nearest}] [-b <band>]
               [-of <gdal_format>] [-co <name>=<value>]
               <src_file> <dst_file>
    ```


??? note "gdal_footprint"

    <span class="badge badge-raster">Raster</span>

    Compute footprint of a raster.

    **Keywords:** <span class="tag">gdal_footprint</span> <span class="tag">footprint</span> <span class="tag">compute</span> <span class="tag">raster</span>

    **Compute the footprint of a GeoTIFF file as a GeoJSON file**

    ```bash
    gdal_footprint -t_srs EPSG:4326 input.tif output.geojson
    ```


??? note "gdal_grid"

    <span class="badge badge-raster">Raster</span>

    Cria uma grade regular (raster) a partir de dados de pontos espaciais espalhados usando métodos de interpolação.

    **Keywords:** <span class="tag">métodos</span> <span class="tag">espalhados</span> <span class="tag">raster</span> <span class="tag">regular</span> <span class="tag">interpolação</span> <span class="tag">usando</span> <span class="tag">espaciais</span> <span class="tag">pontos</span> <span class="tag">grade</span> <span class="tag">partir</span> <span class="tag">cria</span> <span class="tag">gdal_grid</span>

    **--------**

    ```bash
    gdal_grid [--help] [--help-general]
              [-ot {Byte/Int16/UInt16/UInt32/Int32/Float32/Float64/
              CInt16/CInt32/CFloat32/CFloat64}]
              [-oo <NAME>=<VALUE>]...
              [-of <format>] [-co <NAME>=<VALUE>]...
              [-zfield <field_name>] [-z_increase <increase_value>] [-z_multiply <multiply_value>]
              [-a_srs <srs_def>] [-spat <xmin> <ymin> <xmax> <ymax>]
              [-clipsrc <xmin> <ymin> <xmax> <ymax>|<WKT>|<datasource>|spat_extent]
              [-clipsrcsql <sql_statement>] [-clipsrclayer <layer>]
              [-clipsrcwhere <expression>]
              [-l <layername>]... [-where <expression>] [-sql <select_statement>]
              [-txe <xmin> <xmax>] [-tye <ymin> <ymax>] [-tr <xres> <yres>] [-outsize <xsize> <ysize>]
              [-a {<algorithm>[[:<parameter1>=<value1>]...]}] [-q]
              <src_datasource> <dst_filename>
    ```

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
    gdal_grid dem.vrt demv.tif
    ```

    **Or, if we do not wish to use a VRT file:**

    ```bash
    gdal_grid -l dem -oo X_POSSIBLE_NAMES=Easting \
    -oo Y_POSSIBLE_NAMES=Northing -zfield Elevation dem.csv dem.tif
    ```

    **in the VRT file in the following way:**

    ```xml
    <GeometryField encoding="PointFromColumns" x="field_1" y="field_2" z="field_3"/>
    ```

    **and then use :ref:`gdalbuildvrt` -separate and then :ref:`gdal_translate`:**

    ```bash
    gdal_grid ... 1.tif; gdal_grid ... 2.tif; gdal_grid ... 3.tif
    gdalbuildvrt -separate 123.vrt 1.tif 2.tif 3.tif
    gdal_translate 123.vrt 123.tif
    ```

    **Or just use :ref:`gdal_merge`, to combine the one-band files into a single one:**

    ```bash
    gdal_grid ... a.tif; gdal_grid ... b.tif; gdal_grid ... c.tif
    gdal_merge -separate a.tif b.tif c.tif -o d.tif
    ```

    **Create a raster from a VRT datasource using inverse distance to a power**

    ```bash
    gdal_grid -a invdist:power=2.0:smoothing=1.0 -txe 85000 89000 -tye 894000 890000 \
        -outsize 400 400 -of GTiff -ot Float64 -l dem dem.vrt dem.tiff
    ```

    **Read values to interpolate from an attribute field**

    ```bash
    gdal_grid -zfield "Elevation" -a invdist:power=2.0:smoothing=1.0 -txe 85000 89000 \
        -tye 894000 890000 -outsize 400 400 -of GTiff -ot Float64 -l dem dem.vrt \
        dem.tiff --config GDAL_NUM_THREADS ALL_CPUS
    ```


??? note "gdal_mdim"

    <span class="badge badge-raster">Raster</span>

    Entry point for multidimensional commands

    **Keywords:** <span class="tag">gdal_mdim</span> <span class="tag">point</span> <span class="tag">entry</span> <span class="tag">multidimensional</span> <span class="tag">commands</span>

    **Getting information on the file :file:`temperatures.nc` (with JSON output)**

    ```console
    $ gdal mdim info temperatures.nc
    ```

    **Converting file :file:`temperatures.nc` to Zarr**

    ```console
    $ gdal mdim convert temperatures.nc temperatures.zarr
    ```

    **Getting the list of multidimensional drivers (with JSON output)**

    ```console
    $ gdal mdim --drivers
    ```


??? note "gdal_mdim_convert"

    <span class="badge badge-raster">Raster</span>

    Convert a multidimensional dataset.

    **Keywords:** <span class="tag">gdal_mdim_convert</span> <span class="tag">convert</span> <span class="tag">multidimensional</span> <span class="tag">dataset</span>

    **Convert a netCDF file to a multidimensional VRT file**

    ```bash
    gdal mdim convert in.nc out.vrt
    ```

    **Extract a 2D slice of a time,Y,X array**

    ```bash
    gdal mdim convert in.nc out.tif --subset "time(\"2010-01-01\")" --array temperature
    ```

    **Extract a a 3D chunk from a time-indexed GRIB file into a multiband GeoTIFF.**

    ```bash
    gdal mdim convert /vsicurl/https://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/VP.001-003/ds.qpf.bin tst.tif --subset "TIME(1763164800,1763251200)" --array QPF_0-SFC --co COMPRESS=DEFLATE
    ```

    **Subsample along x and y axis**

    ```bash
    gdal mdim convert in.nc out.nc --scale-axes "x(2),y(2)"
    ```

    **to bottom-to-top (or the reverse)**

    ```bash
    gdal mdim convert in.nc out.nc --array "name=temperature,view=[:,::-1,:]"
    ```

    **Transpose an array that has X,Y,time dimension order to time,Y,X**

    ```bash
    gdal mdim convert in.nc out.nc --array "name=temperature,transpose=[2,1,0]"
    ```


??? note "gdal_mdim_mosaic"

    <span class="badge badge-raster">Raster</span>

    Build a mosaic, either virtual (VRT) or materialized, from multidimensional datasets.

    **Keywords:** <span class="tag">from</span> <span class="tag">datasets</span> <span class="tag">either</span> <span class="tag">gdal_mdim_mosaic</span> <span class="tag">build</span> <span class="tag">virtual</span> <span class="tag">mosaic</span> <span class="tag">materialized</span> <span class="tag">multidimensional</span>

    **Mosaic together several all netCDF files starting with ``slice`` that are slices of a 3D array**

    ```bash
    gdal mdim mosaic slice*.nc out.vrt
    ```


??? note "gdal_merge"

    <span class="badge badge-raster">Raster</span>

    Mescla/une um conjunto de imagens raster em um único arquivo de saída.

    **Keywords:** <span class="tag">juntar</span> <span class="tag">mescla</span> <span class="tag">mosaico</span> <span class="tag">saída</span> <span class="tag">arquivo</span> <span class="tag">único</span> <span class="tag">raster</span> <span class="tag">mesclar</span> <span class="tag">unir</span> <span class="tag">gdal_merge</span> <span class="tag">conjunto</span> <span class="tag">imagens</span>

    **--------**

    ```bash
    gdal_merge [--help] [--help-general]
                  [-o <out_filename>] [-of <out_format>] [-co <NAME>=<VALUE>]...
                  [-ps <pixelsize_x> <pixelsize_y>] [-tap] [-separate] [-q] [-v] [-pct]
                  [-ul_lr <ulx> <uly> <lrx> <lry>] [-init "<value>[ <value>]..."]
                  [-n <nodata_value>] [-a_nodata <output_nodata_value>]
                  [-ot <datatype>] [-createonly] <input_file> [<input_file>]...
    ```

    **Creating an image with the pixels in all bands initialized to 255**

    ```bash
    gdal_merge -init 255 -o out.tif in1.tif in2.tif
    ```

    **Creating an RGB image that shows blue in pixels with no data**

    ```bash
    gdal_merge -init "0 0 255" -o out.tif in1.tif in2.tif
    ```

    **Passing a large list of files to :program:`gdal_merge`**

    ```bash
    ls -1 *.tif > tiff_list.txt
    ```

    **listing them in a text file using the command above on Linux, or:**

    ```doscon
    dir /b /s *.tif > tiff_list.txt
    ```

    **using `--optfile`:**

    ```bash
    gdal_merge -o mosaic.tif --optfile tiff_list.txt
    ```

    **Creating an RGB image by merging 3 different greyscale bands**

    ```bash
    gdal_merge -separate 1.tif 2.tif 3.tif -o rgb.tif
    ```

    **copied into the destination image if it is not already defined as nodata.**

    ```bash
    gdal_merge -o merge.tif -n 0 image1.tif image2.tif image3.tif image4.tif
    ```


??? note "gdal_pansharpen"

    <span class="badge badge-raster">Raster</span>

    Perform a pansharpen operation.

    **Keywords:** <span class="tag">perform</span> <span class="tag">operation</span> <span class="tag">pansharpen</span> <span class="tag">gdal_pansharpen</span>

    **--------**

    ```bash
    gdal_pansharpen [--help] [--help-general]
                    <pan_dataset>
                    <spectral_dataset>[,band=<num>] [<spectral_dataset>[,band=<num>]]...
                    <out_dataset>
                    [-of <format>] [-b <band>]... [-w <weight_val>]...
                    [-r {nearest|bilinear|cubic|cubicspline|lanczos|average}]
                    [-threads {ALL_CPUS|<number>}] [-bitdepth <val>] [-nodata <val>]
                    [-spat_adjust {union|intersection|none|nonewithoutwarning}]
                    [-co <NAME>=<VALUE>]... [-q]
    ```

    **With spectral bands in a single dataset**

    ```bash
    gdal_pansharpen panchro.tif multispectral.tif pansharpened_out.tif
    ```

    **With a few spectral bands from a single dataset, reordered**

    ```bash
    gdal_pansharpen panchro.tif multispectral.tif,band=3 multispectral.tif,band=2 multispectral.tif,band=1 pansharpened_out.tif
    ```

    **With spectral bands in several datasets**

    ```bash
    gdal_pansharpen panchro.tif band1.tif band2.tif band3.tif pansharpened_out.tif
    ```

    **Specifying weights**

    ```bash
    gdal_pansharpen -w 0.7 -w 0.2 -w 0.1 panchro.tif multispectral.tif pansharpened_out.tif
    ```

    **Specify RGB bands from a RGBNir multispectral dataset while computing the pseudo panchromatic intensity on the 4 RGBNir bands**

    ```bash
    gdal_pansharpen -b 1 -b 2 -b 3 panchro.tif rgbnir.tif pansharpened_out.tif
    ```


??? note "gdal_pipeline"

    <span class="badge badge-raster">Raster</span>

    Process a dataset applying several steps.

    **Keywords:** <span class="tag">gdal_pipeline</span> <span class="tag">process</span> <span class="tag">several</span> <span class="tag">dataset</span> <span class="tag">applying</span> <span class="tag">steps</span>

    **Compute the footprint of a raster and apply a buffer on the footprint**

    ```bash
    $ gdal pipeline ! read in.tif ! footprint ! buffer 20 ! write out.gpkg --overwrite
    ```

    **``gdal pipeline ! .... ! write out.gdalg.json``.**

    ```json
    {
        "type": "gdal_streamed_alg",
        "command_line": "gdal pipeline ! read in.tif ! footprint ! buffer 20"
    }
    ```

    **``stream`` output format and a non-significant output dataset name.**

    ```json
    {
        "type": "gdal_streamed_alg",
        "command_line": "gdal pipeline ! read in.tif ! footprint ! buffer 20 ! write --output-format=streamed streamed_dataset"
    }
    ```

    **Let's imagine we have a :file:`raster_reproject.gdalg.json` with the following content:**

    ```json
    {
        "type": "gdal_streamed_alg",
        "command_line": "gdal pipeline ! read in.tif ! reproject --output-crs=EPSG:4326 ! edit --metadata=CHANGES=reprojected"
    }
    ```

    **step with an ``output`` argument.**

    ```bash
    $ gdal pipeline raster_reproject.gdalg.json --read.input=other_input.tif --write.output=out.tif
    ```

    **will emit an error, so this is safe to do):**

    ```bash
    $ gdal pipeline raster_reproject.gdalg.json --input=other_input.tif --output=out.tif --co COMPRESS=LZW --overwrite
    ```

    **For example, given:**

    ```json
    {
        "type": "gdal_streamed_alg",
        "command_line": "gdal pipeline ! read in.tif ! edit --metadata=before=value ! reproject --output-crs=EPSG:4326 ! edit --metadata=CHANGES=reprojected"
    }
    ```

    **the following command line may be used:**

    ```bash
    $ gdal pipeline raster_reproject.gdalg.json --edit[0].metadata=before=modified --output=out.tif
    ```

    **Execution of pipelines and argument substitutions can also be done in Python with:**

    ```python
    gdal.Run("pipeline", pipeline="raster_reproject.gdalg.json", output="out.tif", arguments={"edit[0].metadata": "before=modified"})
    ```

    **Summarize mean elevation within 200m of points of interest**

    ```bash
    gdal pipeline read points.geojson ! buffer 200 ! \
        zonal-stats \
          --input dem.tif
          --zones _PIPE_ \
          --stat mean ! \
        write \
          --output-format CSV \
          --output /vsistdout/
    ```

    **Combine the output of shaded relief map and hypsometric rendering on a DEM to create a colorized shaded relief map.**

    ```bash
    $ gdal pipeline read n43.tif ! \
                    color-map --color-map color_file.txt ! \
                    blend --operator=hsv-value --overlay \
                        [ read n43.tif ! hillshade -z 30 ] ! \
                    write out.tif --overwrite
    ```

    **Split the content of a "cities" layer according to whether its population is below or above 1 million.**

    ```bash
    $ gdal pipeline read cities.gpkg ! \
            tee [ filter --where "pop < 1e6" ! write small_cities.gpkg ] \
                [ filter --where "pop >= 1e6" ! write big_cities.gpkg ]
    ```

    **Combine the output of shaded relief map and hypsometric rendering on**

    ```bash
    $ gdal pipeline read n43.tif ! \
                    color-map --color-map color_file.txt ! \
                    tee [ write colored.tif --overwrite ] ! \
                    blend --operator=hsv-value --overlay \
                        [ read n43.tif ! hillshade -z 30  ! tee [ write hillshade.tif --overwrite ] ] ! \
                    write colored-hillshade.tif --overwrite
    ```

    **Compute the footprint of a raster and apply a buffer on the footprint**

    ```bash
    $ gdal pipeline ! read in.tif ! footprint ! buffer 20 ! write out.gpkg --overwrite
    ```

    **Rasterize and reproject**

    ```bash
    $ gdal pipeline ! read in.gpkg ! rasterize --size 1000,1000 ! reproject --output-crs EPSG:4326 ! write out.tif --overwrite
    ```

    **Use an existing pipeline that rasterizes and reprojects, but change its input file and target CRS, and specify the output file**

    ```bash
    $ gdal pipeline raster_reproject.gdalg.json --input=my.gpkg --output=out.tif --output-crs=EPSG:32631
    ```

    **of this attribute is used as the buffer distance for each feature.**

    ```bash
    gdal vector pipeline \
        ! read lines.gpkg \
        ! sql "SELECT fid, ST_Buffer(geom, width) AS geom FROM lines" \
        ! set-geom-type --geometry-type Polygon \
        ! write buffered-lines.gpkg --output-layer=BufferedLines --overwrite --overwrite-layer
    ```


??? note "gdal_polygonize"

    <span class="badge badge-raster">Raster</span>

    Vetoriza um arquivo raster, criando polígonos a partir de grupos de pixels com valores conectados semelhantes.

    **Keywords:** <span class="tag">grupos</span> <span class="tag">semelhantes</span> <span class="tag">vetorizar</span> <span class="tag">vetoriza</span> <span class="tag">conectados</span> <span class="tag">gdal_polygonize</span> <span class="tag">arquivo</span> <span class="tag">valores</span> <span class="tag">raster</span> <span class="tag">polígonos</span> <span class="tag">raster para vetor</span> <span class="tag">poligonizar</span>

    **--------**

    ```bash
    gdal_polygonize [--help] [--help-general]
                       [-8] [-o <name>=<value>]... [-nomask]
                       [-mask <filename>] <raster_file> [-b <band>]
                       [-q] [-f <ogr_format>] [-lco <name>=<value>]...
                       [-overwrite] <out_file> [<layer>] [<fieldname>]
    ```


??? note "gdal_proximity"

    <span class="badge badge-raster">Raster</span>

    Gera um mapa de distância/proximidade raster, calculando a distância de cada pixel até feições de interesse.

    **Keywords:** <span class="tag">feições</span> <span class="tag">proximidade</span> <span class="tag">gera</span> <span class="tag">mapa</span> <span class="tag">distância</span> <span class="tag">cada</span> <span class="tag">interesse</span> <span class="tag">calculando</span> <span class="tag">raster</span> <span class="tag">pixel</span> <span class="tag">gdal_proximity</span>

    **--------**

    ```bash
    gdal_proximity [--help] [--help-general]
                      <srcfile> <dstfile> [-srcband <n>] [-dstband <n>]
                      [-of <format>] [-co <name>=<value>]...
                      [-ot Byte/UInt16/UInt32/Float32/etc]
                      [-values <n>,<n>,<n>] [-distunits {PIXEL|GEO}]
                      [-maxdist <n>] [-nodata <n>] [-use_input_nodata {YES|NO}]
                      [-fixed-buf-val <n>]
    ```


??? note "gdal_raster"

    <span class="badge badge-raster">Raster</span>

    Entry point for raster commands

    **Keywords:** <span class="tag">point</span> <span class="tag">raster</span> <span class="tag">gdal_raster</span> <span class="tag">entry</span> <span class="tag">commands</span>

    **Getting information on the file :file:`utm.tif` (with text output)**

    ```console
    $ gdal raster info utm.tif
    ```

    **Converting file :file:`utm.tif` to GeoPackage raster**

    ```console
    $ gdal raster convert utm.tif utm.gpkg
    ```

    **Getting the list of raster drivers (with JSON output)**

    ```console
    $ gdal raster --drivers
    ```


??? note "gdal_raster_as_features"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: As Features. Create features representing pixels of a raster

    **Keywords:** <span class="tag">create</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">gdal_raster_as_features</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">features</span> <span class="tag">pixels</span> <span class="tag">representing</span>

    **Create points at the center of pixels having a value less than 150**

    ```bash
    gdal pipeline read input.tif !
             reclassify -m "[-inf, 150)=1; DEFAULT=NO_DATA" !
             as-features --geometry-type point --skip-nodata !
             write out.shp
    ```

    **Create a polygon grid dividing the globe into 1-degree chunks**

    ```bash
    gdal pipeline create --bbox -180,-90,180,90 --size 360,180 !
             as-features --geometry-type polygon !
             write grid.shp
    ```


??? note "gdal_raster_aspect"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Aspect. Generate an aspect map

    **Keywords:** <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">gdal_raster_aspect</span> <span class="tag">operação</span> <span class="tag">generate</span> <span class="tag">correspondente</span> <span class="tag">aspect</span>

    **Generates an aspect map from a DTED0 file.**

    ```bash
    $ gdal raster aspect n43.dt0 out.tif --overwrite
    ```


??? note "gdal_raster_blend"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Blend. Blend/compose two raster datasets

    **Keywords:** <span class="tag">compose</span> <span class="tag">datasets</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">blend</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">gdal_raster_blend</span>

    **Alpha blending of two datasets using 75% opacity for the overlay dataset.**

    ```bash
    $ gdal raster blend --opacity 75 source.tif overlay.tif out.tif
    ```

    **Exemplo 2**

    ```bash
    $ gdal raster blend --overlay=hillshade.tif --operator=hsv-value \
                        hypsometric.tif hypsometric_combined_with_hillshade.tif
    ```

    **Combine a hillshade and a hypsometric rendering of a DEM into a colorized hillshade using the ``multiply`` blending operator.**

    ```bash
    $ gdal raster blend --overlay=hillshade.tif --operator=multiply \
                        hypsometric.tif hypsometric_combined_with_hillshade.tif
    ```

    **Combine a hillshade and a hypsometric rendering of a DEM into a colorized hillshade using the ``screen`` blending operator.**

    ```bash
    $ gdal raster blend --overlay=hillshade.tif --operator=screen \
                        hypsometric.tif hypsometric_combined_with_hillshade.tif
    ```

    **Combine a hillshade and a hypsometric rendering of a DEM into a colorized hillshade using the ``overlay`` blending operator.**

    ```bash
    $ gdal raster blend --overlay=hillshade.tif --operator=overlay \
                        hypsometric.tif hypsometric_combined_with_hillshade.tif
    ```

    **Combine a hillshade and a hypsometric rendering of a DEM into a colorized hillshade using the ``hard-light`` blending operator.**

    ```bash
    $ gdal raster blend --overlay=hillshade.tif --operator=hard-light \
                        hypsometric.tif hypsometric_combined_with_hillshade.tif
    ```

    **Combine a hillshade and a hypsometric rendering of a DEM into a colorized hillshade using the ``darken`` blending operator.**

    ```bash
    $ gdal raster blend --overlay=hillshade.tif --operator=darken \
                        hypsometric.tif hypsometric_combined_with_hillshade.tif
    ```

    **Combine a hillshade and a hypsometric rendering of a DEM into a colorized hillshade using the ``lighten`` blending operator.**

    ```bash
    $ gdal raster blend --overlay=hillshade.tif --operator=lighten \
                        hypsometric.tif hypsometric_combined_with_hillshade.tif
    ```

    **Combine a hillshade and a hypsometric rendering of a DEM into a colorized hillshade using the ``color-dodge`` blending operator.**

    ```bash
    $ gdal raster blend --overlay=hillshade.tif --operator=color-dodge \
                        hypsometric.tif hypsometric_combined_with_hillshade.tif
    ```

    **Combine a hillshade and a hypsometric rendering of a DEM into a colorized hillshade using the ``color-burn`` blending operator.**

    ```bash
    $ gdal raster blend --overlay=hillshade.tif --operator=color-burn \
                        hypsometric.tif hypsometric_combined_with_hillshade.tif
    ```


??? note "gdal_raster_calc"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Calc. Perform raster algebra

    **Keywords:** <span class="tag">gdal</span> <span class="tag">perform</span> <span class="tag">gdal_raster_calc</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">algebra</span> <span class="tag">calc</span> <span class="tag">correspondente</span>

    **Per-band sum of three files**

    ```bash
    gdal raster calc -i "A=file1.tif" -i "B=file2.tif" -i "C=file3.tif" --calc "A+B+C" -o out.tif
    ```

    **Per-dataset average of all bands of each dataset**

    ```bash
    gdal raster calc -i "A=file1.tif" -i "B=file2.tif" -i "C=file3.tif" --flatten --calc "avg(A)" --calc "avg(B)" --calc "avg(C)" -o out.tif
    ```

    **Per-band maximum of three files**

    ```bash
    gdal raster calc -i "A=file1.tif" -i "B=file2.tif" -i "C=file3.tif" --calc "max(A,B,C)" -o out.tif
    ```

    **Setting values of zero and below to NaN**

    ```bash
    gdal raster calc -i "A=input.tif" -o result.tif --calc="A > 0 ? A : NaN"
    ```

    **Compute the average (as a single band) of all bands of two input datasets**

    ```bash
    gdal raster calc -i A=input1.tif -i B=input2.tif -o result.tif --flatten --calc=mean --dialect=builtin
    ```

    **Generate a masked aspect layer where the slope angle is greater than 2 degrees, using nested pipelines (since GDAL 3.12.1)**

    ```bash
    gdal raster calc -i "SLOPE=[ read dem.tif ! slope ]" -i "ASPECT=[ read dem.tif ! aspect ]" -o result.tif --calc "(SLOPE >= 2) ? ASPECT : -9999" --nodata -9999
    ```

    **Latitude-based calculation using ``_CENTER_Y_``**

    ```bash
    gdal raster calc -i A=input.tif \
        --calc="sin(_CENTER_Y_ * 0.0174533)" \
        -o output.tif
    ```


??? note "gdal_raster_clean_collar"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Clean Collar. Clean the collar of a raster dataset, removing noise.

    **Keywords:** <span class="tag">collar</span> <span class="tag">clean</span> <span class="tag">gdal</span> <span class="tag">removing</span> <span class="tag">gdal_raster_clean_collar</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">noise</span> <span class="tag">correspondente</span>

    **Edit in place a dataset using the default black color as the color of the collar**

    ```bash
    $ gdal raster clean-collar --update my.tif
    ```

    **Create a new dataset, using black or white as the color of the collar, considering values in the [0,5] range as being considered black, and values in the [250,255] range to be white. It also adds an alpha band to the output dataset.**

    ```bash
    $ gdal raster clean-collar --add-alpha --color=black --color=white --color-threshold=5 in.tif out.tif
    ```


??? note "gdal_raster_clip"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Clip. Clip a raster dataset.

    **Keywords:** <span class="tag">clip</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">gdal_raster_clip</span>

    **Clip a GeoTIFF file to the bounding box from longitude 2, latitude 49, to longitude 3, latitude 50 in WGS 84**

    ```bash
    $ gdal raster clip --bbox=2,49,3,50 --bbox-crs=EPSG:4326 in.tif out.tif --overwrite
    ```

    **Clip a GeoTIFF file using the bounds of :file:`reference.tif`**

    ```bash
    $ gdal raster clip --like=reference.tif in.tif out.tif --overwrite
    ```

    **Clip a GeoTIFF file from raster column 1000 and line 2000, for a width of 500 pixels and a height of 600 pixels**

    ```bash
    $ gdal raster clip --window=1000,2000,500,600 in.tif out.tif --overwrite
    ```

    **Clip a GeoTIFF file using vector features**

    ```bash
    $ gdal raster clip NE2_50M_SR_W.tif clipped.tif \
         --like natural_earth_vector.gpkg \
         --like-layer "ne_50m_admin_0_countries" \
         --like-where "ADMIN='Romania'"
    ```

    **in the SQL query.**

    ```bash
    $ gdal raster clip NE2_50M_SR_W.tif clipped.tif \
        --like natural_earth_vector.gpkg \
        --like-sql "SELECT geom FROM ne_50m_admin_0_countries WHERE ADMIN = 'Romania'" \
        --overwrite
    ```

    **when the bounding box exceeds the raster extent.**

    ```bash
    $ gdal raster clip \
        --bbox=3757032.814272985,-626172.1357121654,4383204.9499851465,0 \
        --bbox-crs=EPSG:3857 \
        --allow-bbox-outside-source \
        in.tif out.tif \
        --overwrite \
        --output-format COG
    ```


??? note "gdal_raster_color_map"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Color Map. Generate a RGB or RGBA dataset from a single band, using a color map.

    **Keywords:** <span class="tag">single</span> <span class="tag">from</span> <span class="tag">gdal</span> <span class="tag">band</span> <span class="tag">raster</span> <span class="tag">gdal_raster_color_map</span> <span class="tag">generate</span> <span class="tag">operação</span> <span class="tag">color</span> <span class="tag">dataset</span> <span class="tag">using</span> <span class="tag">correspondente</span>

    **Generates a RGB dataset from a DTED0 file using an external color map**

    ```bash
    $ gdal raster color-map --color-map=color-map.txt n43.dt0 out.tif --overwrite
    ```


??? note "gdal_raster_compare"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Compare. Compare two raster datasets.

    **Keywords:** <span class="tag">datasets</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">compare</span> <span class="tag">correspondente</span> <span class="tag">gdal_raster_compare</span>

    **Comparing two datasets that differ by their data types**

    ```bash
    $ gdal raster compare autotest/gcore/data/byte.tif autotest/gcore/data/uint16.tif
    Reference file has size 736 bytes, whereas input file has size 1136 bytes.
    Reference band 1 has data type Byte, but input band has data type UInt16
    
    $ echo $?
    2
    ```

    **Comparing two datasets while values have different units**

    ```bash
    $ gdal raster pipeline read test_in_foot.tif ! calc --calc "X * 0.3048" ! compare --reference=reference_in_meter.tif
    ```


??? note "gdal_raster_contour"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Contour. Builds vector contour lines from a raster elevation model.

    **Keywords:** <span class="tag">model</span> <span class="tag">contorno</span> <span class="tag">from</span> <span class="tag">elevation</span> <span class="tag">gdal</span> <span class="tag">lines</span> <span class="tag">isolinhas</span> <span class="tag">raster</span> <span class="tag">builds</span> <span class="tag">operação</span> <span class="tag">contour</span> <span class="tag">curvas de nível</span>

    **Create contour lines from a raster elevation model**

    ```bash
    gdal raster contour --interval 100 elevation.tif contour.shp
    ```

    **Create contour polygons from a raster elevation model with custom attributes and fixed levels**

    ```bash
    gdal raster contour --levels MIN,100,200,MAX --polygonize --min-name MIN --max-name MAX elevation.tif contour.shp
    ```


??? note "gdal_raster_convert"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Convert. Convert a raster dataset.

    **Keywords:** <span class="tag">gdal</span> <span class="tag">gdal_raster_convert</span> <span class="tag">convert</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span>

    **Converting file :file:`utm.tif` to a cloud-optimized GeoTIFF using JPEG compression**

    ```console
    $ gdal raster convert --format=COG --co COMPRESS=JPEG utm.tif utm_cog.tif
    ```

    **Converting file :file:`utm.tif` to GeoPackage raster**

    ```console
    $ gdal raster convert utm.tif utm.gpkg
    ```


??? note "gdal_raster_create"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Create. Create a new raster dataset.

    **Keywords:** <span class="tag">gdal_raster_create</span> <span class="tag">create</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span>

    **Initialize a new GeoTIFF file with 3 bands and a uniform value of 10**

    ```bash
    gdal raster create --size=20,20 --band-count=3 --crs=EPSG:4326 --bbox=2,49,3,50 --burn 10 out.tif
    ```

    **Create a PDF file from a XML composition file**

    ```bash
    gdal raster create --creation-option COMPOSITION_FILE=composition.xml out.pdf
    ```

    **Initialize a blank GeoTIFF file from an input one**

    ```bash
    gdal raster create --like prototype.tif output.tif
    ```


??? note "gdal_raster_edit"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Edit. Edit in place a raster dataset.

    **Keywords:** <span class="tag">edit</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">place</span> <span class="tag">gdal_raster_edit</span>

    **Override (without reprojecting) the CRS of a dataset**

    ```bash
    $ gdal raster edit --crs=EPSG:32632 my.tif
    ```

    **Override (without reprojecting or subsetting) the bounding box of a dataset**

    ```bash
    $ gdal raster edit --bbox=2,49,3,50 my.tif
    ```

    **Add a metadata item**

    ```bash
    $ gdal raster edit --metadata AUTHOR=EvenR my.tif
    ```

    **Remove a metadata item**

    ```bash
    $ gdal raster edit --unset-metadata AUTHOR my.tif
    ```

    **Add 2 ground control point (GCP) for (column=0,line=0,X=2,Y=49) and (column=50,line=100,X=3,Y=48)**

    ```bash
    $ gdal raster edit --gcp 0,0,2,49 --gcp 50,100,3,48 my.tif
    ```

    **Add ground control point (GCP) from :file:`gcps.csv`, that must have fields named ``column``, ``line``, ``x`` and  ``y``.**

    ```bash
    $ gdal raster edit --gcp @gcps.csv my.tif
    ```

    **Set red, green, blue, NIR color interpretation to a 4-band dataset**

    ```bash
    $ gdal raster edit --color-interpretation red,green,blue,nir 4band.tif
    ```


??? note "gdal_raster_fill_nodata"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Fill Nodata. Fill nodata raster regions by interpolation from edges

    **Keywords:** <span class="tag">gdal_raster_fill_nodata</span> <span class="tag">from</span> <span class="tag">gdal</span> <span class="tag">fill</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">edges</span> <span class="tag">regions</span> <span class="tag">interpolation</span> <span class="tag">nodata</span> <span class="tag">correspondente</span>

    **The output will be saved in `output.tif`.**

    ```bash
    gdal raster fill-nodata -b 2 --max-distance 50 --smoothing-iterations 3 \
        --strategy nearest --mask mask.tif \
        input.tif output.tif
    ```


??? note "gdal_raster_footprint"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Footprint. Compute the footprint of a raster dataset

    **Keywords:** <span class="tag">footprint</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">gdal_raster_footprint</span> <span class="tag">correspondente</span> <span class="tag">compute</span>

    **Write the footprint of a GeoTIFF file into a GeoJSON file.**

    ```bash
    gdal raster footprint my_raster.tif footprint.geojson
    ```


??? note "gdal_raster_hillshade"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Hillshade. Generate a shaded relief map

    **Keywords:** <span class="tag">hillshade</span> <span class="tag">shaded</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">generate</span> <span class="tag">operação</span> <span class="tag">gdal_raster_hillshade</span> <span class="tag">correspondente</span> <span class="tag">relief</span>

    **Generates a shaded relief map from a DTED0 file, using a vertical exaggeration factor of 30.**

    ```bash
    $ gdal raster hillshade --zfactor=30 n43.dt0 out.tif --overwrite
    ```

    **Combine the output of shaded relief map and hypsometric rendering on a DEM to create a colorized shaded relief map.**

    ```bash
    $ gdal pipeline read n43.tif ! \
                    color-map --color-map color_file.txt ! \
                    blend --operator=hsv-value --overlay \
                        [ read n43.tif ! hillshade -z 30 ] ! \
                    write out.tif --overwrite
    ```


??? note "gdal_raster_index"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Index. Create a vector index of raster datasets.

    **Keywords:** <span class="tag">datasets</span> <span class="tag">create</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">index</span> <span class="tag">gdal_raster_index</span> <span class="tag">correspondente</span> <span class="tag">vector</span>

    **shape showing the bounds of the image:**

    ```bash
    gdal raster index doq/*.tif doq_index.gpkg
    ```

    **geometries into the same output projection:**

    ```bash
    gdal raster index --output-crs EPSG:4326 --source-crs-field-name=src_srs *.tif tile_index_mixed_crs.gpkg
    ```

    **Creates a STAC-GeoParquet compliant index.**

    ```bash
    gdal raster index --profile STAC-GeoParquet  *.tif index.parquet
    ```


??? note "gdal_raster_materialize"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Materialize. Materialize a piped dataset on disk to increase the efficiency of the following steps

    **Keywords:** <span class="tag">gdal_raster_materialize</span> <span class="tag">disk</span> <span class="tag">efficiency</span> <span class="tag">piped</span> <span class="tag">gdal</span> <span class="tag">materialize</span> <span class="tag">increase</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">steps</span> <span class="tag">correspondente</span>

    **Reproject a GeoTIFF file to CRS EPSG:32632 ("WGS 84 / UTM zone 32N"), materialize it to a temporary file and compute its contour lines**

    ```bash
    $ gdal pipeline ! read in.tif ! reproject --output-crs=EPSG:32632 ! \
                    ! materialize ! contour --interval=10 ! write out.gpkg --overwrite
    ```

    **Instead, you could use command `reproject` and use `--bbox` to limit the region of interest and set `--size` or `--resolution` to use lower resolution overview.**

    ```bash
    $ gdal pipeline ! read /vsicurl/https://some.storage.com/mydata/landcover.tif \
                    ! reproject -r mode -d EPSG:4326 --bbox=112,2,116,4.5 --bbox-crs=EPSG:4326 --size=3000,3000 \
                    ! materialize \
                    ! zonal-stats --zones=/vsicurl/https://some.storage.com/mydata/adm_level4.fgb --stat=values \
                    ! write out.geojson
    ```


??? note "gdal_raster_mosaic"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Mosaic. Build a mosaic, either virtual (VRT) or materialized

    **Keywords:** <span class="tag">gdal</span> <span class="tag">gdal_raster_mosaic</span> <span class="tag">raster</span> <span class="tag">either</span> <span class="tag">operação</span> <span class="tag">build</span> <span class="tag">virtual</span> <span class="tag">correspondente</span> <span class="tag">materialized</span> <span class="tag">mosaic</span>

    **Make a virtual mosaic with blue background colour (RGB: 0 0 255)**

    ```bash
    gdal raster mosaic --hide-nodata --output-nodata=0,0,255 doq/*.tif doq_index.vrt
    ```

    **Create a Cloud Optimized GeoTIFF (COG) mosaic from all GeoTIFFs in a folder**

    ```bash
    gdal raster mosaic --output-format COG --creation-option BIGTIFF=YES *.tif mosaic.tif
    ```


??? note "gdal_raster_neighbors"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Neighbors. Compute the value of each pixel from its neighbors (focal statistics).

    **Keywords:** <span class="tag">gdal_raster_neighbors</span> <span class="tag">neighbors</span> <span class="tag">from</span> <span class="tag">focal</span> <span class="tag">gdal</span> <span class="tag">statistics</span> <span class="tag">pixel</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">value</span> <span class="tag">each</span> <span class="tag">correspondente</span>

    **Compute the horizontal and vertical derivative of a single-band raster**

    ```bash
    gdal raster neighbors --kernel u --kernel v in.tif uv.tif
    ```

    **Compute the average value around each pixel in a 3x3 neighborhood**

    ```bash
    gdal raster neighbors --kernel equal --method mean in.tif mean.tif
    ```

    **Compute the maximum value around each pixel in a 5x5 neighborhood**

    ```bash
    gdal raster neighbors --kernel equal --size 5 --method max in.tif max.tif
    ```

    **Compute a sharpen filter of a single-band raster, by manually specifying the kernel coefficients.**

    ```bash
    gdal raster neighbors "--kernel=[[0,-1,0],[-1,5,-1],[0,-1,0]]" in.tif sharpen.tif
    ```


??? note "gdal_raster_nodata_to_alpha"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Nodata To Alpha. Replace nodata value(s) with an alpha band.

    **Keywords:** <span class="tag">with</span> <span class="tag">gdal</span> <span class="tag">alpha</span> <span class="tag">band</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">replace</span> <span class="tag">value</span> <span class="tag">gdal_raster_nodata_to_alpha</span> <span class="tag">correspondente</span> <span class="tag">nodata</span>

    **--------**

    ```console
    $ gdal raster nodata-to-alpha input_with_nodata.tif output_with_alpha_band.tif
    ```


??? note "gdal_raster_overview"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Overview. Manage overviews of a raster dataset

    **Keywords:** <span class="tag">overviews</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">manage</span> <span class="tag">correspondente</span> <span class="tag">gdal_raster_overview</span> <span class="tag">overview</span>

    **Sintaxe Básica**

    ```bash
    gdal_raster_overview --help
    ```


??? note "gdal_raster_overview_add"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Overview Add. Add overviews to a raster dataset

    **Keywords:** <span class="tag">overviews</span> <span class="tag">gdal</span> <span class="tag">gdal_raster_overview_add</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">overview</span>

    **Create overviews, embedded in the supplied TIFF file, with automatic computation of levels**

    ```bash
    gdal raster overview add -r average abc.tif
    ```

    **Create overviews, embedded in the supplied TIFF file**

    ```bash
    gdal raster overview add -r average --levels=2,4,8,16 abc.tif
    ```

    **Create an external compressed GeoTIFF overview file from the ERDAS .IMG file**

    ```bash
    gdal raster overview add --external --levels=2,4,8,16 --co COMPRESS=YES erdas.img
    ```

    **Create an external JPEG-compressed GeoTIFF overview file from a 3-band RGB dataset**

    ```bash
    gdal raster overview add --co OVERVIEW=JPEG --co PHOTOMETRIC=YCBCR \
                             --co INTERLEAVE=PIXEL rgb_dataset.ext 2 4 8 16
    ```

    **Create overviews for a specific subdataset**

    ```bash
    gdal raster overview add GPKG:file.gpkg:layer
    ```

    **Add 3 existing datasets at scale 1:25K, 1:50K and 1:100K as overviews of :file:`my.tif`.**

    ```bash
    gdal raster overview add --overview-src ovr_25k.tif --overview-src ovr_50k.tif --overview-src ovr_100k.tif --dataset my.tif
    ```

    **Create a COG file with non power-of-two overview levels.**

    ```bash
    gdal pipeline read input.tif ! reproject --output-crs=EPSG:4326 ! add overview --levels 16,64,128 ! write output.tif --format=COG
    ```


??? note "gdal_raster_overview_delete"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Overview Delete. Delete overviews of a raster dataset

    **Keywords:** <span class="tag">delete</span> <span class="tag">overviews</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">gdal_raster_overview_delete</span> <span class="tag">correspondente</span> <span class="tag">overview</span>

    **Delete overviews of a GeoTIFF file.**

    ```bash
    gdal raster overview delete my.tif
    ```


??? note "gdal_raster_overview_refresh"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Overview Refresh. Refresh overviews

    **Keywords:** <span class="tag">refresh</span> <span class="tag">overviews</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">gdal_raster_overview_refresh</span> <span class="tag">overview</span>

    **Refresh external overviews of a VRT file using timestamp of source files**

    ```bash
    gdal raster mosaic tile1.tif tile2.tif my.vrt               # create VRT
    gdal raster overview add --external -r cubic my.vrt         # initial overview generation
    touch tile1.tif                                             # simulate update of one of the source tiles
    gdal raster overview refresh --external -r cubic \
                              --use-source-timestamp my.vrt     # refresh overviews
    ```

    **Refresh (internal) overviews of a TIFF file**

    ```bash
    gdal raster mosaic tile1.tif tile2.tif mosaic.tif       # create mosaic
    gdal raster overview add -r cubic mosaic.tif            # initial overview generation
    gdalwarp tile1_modif.tif mosaic.tif                     # update mosaic
    gdal raster overview refresh --like=tile1.tif my.tif    # refresh overviews
    ```


??? note "gdal_raster_pansharpen"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Pansharpen. Perform a pansharpen operation.

    **Keywords:** <span class="tag">gdal_raster_pansharpen</span> <span class="tag">gdal</span> <span class="tag">perform</span> <span class="tag">pansharpen</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">operation</span>

    **With spectral bands in a single dataset**

    ```bash
    gdal raster pansharpen panchro.tif rgb.tif pansharpened_out.tif
    ```

    **With a few spectral bands from a single dataset, reordered**

    ```bash
    gdal raster pansharpen panchro.tif bgr.tif,band=3 bgr.tif,band=2 bgr.tif,band=1 pansharpened_out.tif
    ```

    **With spectral bands in several datasets**

    ```bash
    gdal raster pansharpen panchro.tif red.tif green.tif blue.tif pansharpened_out.tif
    ```

    **Specifying weights**

    ```bash
    gdal raster pansharpen -w 0.7,0.2,0.1 panchro.tif multispectral.tif pansharpened_out.tif
    ```

    **Select RGB bands from a RGBNir multispectral dataset while computing the pseudo panchromatic intensity on the 4 RGBNir bands**

    ```bash
    gdal raster pipeline read panchro.tif ! pansharpen rgbnir.tif ! select 1,2,3 ! write pansharpened_out.tif
    ```


??? note "gdal_raster_pipeline"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Pipeline. Process a raster dataset applying several steps.

    **Keywords:** <span class="tag">process</span> <span class="tag">gdal_raster_pipeline</span> <span class="tag">gdal</span> <span class="tag">several</span> <span class="tag">pipeline</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">applying</span> <span class="tag">steps</span> <span class="tag">correspondente</span>

    **``gdal raster pipeline ! .... ! write out.gdalg.json``.**

    ```json
    {
        "type": "gdal_streamed_alg",
        "command_line": "gdal raster pipeline ! read in.tif ! reproject --output-crs=EPSG:32632"
    }
    ```

    **``stream`` output format and a non-significant output dataset name.**

    ```json
    {
        "type": "gdal_streamed_alg",
        "command_line": "gdal raster pipeline ! read in.tif ! reproject --output-crs=EPSG:32632 ! write --output-format=streamed streamed_dataset"
    }
    ```

    **Reproject a GeoTIFF file to CRS EPSG:32632 ("WGS 84 / UTM zone 32N") and adding a metadata item**

    ```bash
    $ gdal raster pipeline ! read in.tif ! reproject --output-crs=EPSG:32632 ! edit --metadata AUTHOR=EvenR ! write out.tif --overwrite
    ```

    **Serialize the command of a reprojection of a GeoTIFF file in a GDALG file, and later read it**

    ```bash
    $ gdal raster pipeline ! read in.tif ! reproject --output-crs=EPSG:32632 ! write in_epsg_32632.gdalg.json --overwrite
    $ gdal raster info in_epsg_32632.gdalg.json
    ```

    **Mosaic on-the-fly several input files and tile that mosaic.**

    ```bash
    gdal raster pipeline ! mosaic input*.tif ! tile output_folder
    ```

    **Reclassify GeoTIFF and render it as RGB image.**

    ```bash
    $ gdal raster pipeline ! read in.tif ! reclassify -m "[1,10]=1; [11,20]=2; [21,30]=3; DEFAULT=NO_DATA" --ot=Byte ! color-map --color-map=color_map.txt --color-selection=exact --add-alpha ! write -f WEBP rendered.webp
    ```


??? note "gdal_raster_polygonize"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Polygonize. Create a polygon feature dataset from a raster band

    **Keywords:** <span class="tag">vetorizar</span> <span class="tag">from</span> <span class="tag">polygonize</span> <span class="tag">create</span> <span class="tag">gdal</span> <span class="tag">band</span> <span class="tag">gdal_raster_polygonize</span> <span class="tag">raster</span> <span class="tag">feature</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">raster para vetor</span>

    **Create a shapefile with polygons for the connected regions of band 1 of the input GeoTIFF.**

    ```bash
    gdal raster polygonize input.tif polygonize.shp
    ```


??? note "gdal_raster_proximity"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Proximity. Produces a raster proximity map.

    **Keywords:** <span class="tag">proximidade</span> <span class="tag">gdal</span> <span class="tag">distância</span> <span class="tag">produces</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">gdal_raster_proximity</span> <span class="tag">proximity</span>

    **Proximity map of a raster with max distance of 3 pixels**

    ```bash
    $ gdal raster proximity --max-distance 3  input.tif output.tif
    ```

    **Proximity map of a two bands raster with different target values for each band using a pipeline stack**

    ```bash
    $ gdal raster pipeline stack \
           [ read input.tif ! proximity -b 1 --target-values 1,2,3 ] \
           [ read input.tif ! proximity -b 2 --target-values 4,5,6 ] ! \
           write output.tif
    ```


??? note "gdal_raster_read"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Read. Read a raster dataset (pipeline only)

    **Keywords:** <span class="tag">gdal_raster_read</span> <span class="tag">only</span> <span class="tag">gdal</span> <span class="tag">pipeline</span> <span class="tag">read</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span>

    **Read a GeoTIFF file**

    ```bash
    $ gdal raster pipeline read input.tif ! ... [other commands here] ...
    ```


??? note "gdal_raster_reclassify"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Reclassify. Reclassify a raster dataset.

    **Keywords:** <span class="tag">gdal</span> <span class="tag">reclassify</span> <span class="tag">gdal_raster_reclassify</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span>

    **--------**

    ```console
    $ gdal raster reclassify -m "0=10; [2,4]=20; 1=40" -i wbm.tif -o typ.tif
    ```


??? note "gdal_raster_reproject"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Reproject. Reproject a raster dataset.

    **Keywords:** <span class="tag">gdal_raster_reproject</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">reproject</span> <span class="tag">correspondente</span>

    **Reproject a GeoTIFF file to CRS EPSG:32632 ("WGS 84 / UTM zone 32N")**

    ```bash
    $ gdal raster reproject --output-crs=EPSG:32632 in.tif out.tif --overwrite
    ```

    **instead of embedding CRS information in GeoTIFF metadata tags. See :ref:`GTiff &lt;raster.gtiff&gt;` ``PROFILE``.**

    ```bash
    $ gdal raster reproject --creation-option "PROFILE=BASELINE" --output-crs=ESRI:54052 input.tif output.tif --overwrite
    ```


??? note "gdal_raster_resize"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Resize. Resize a raster dataset without changing the georeferenced extents.

    **Keywords:** <span class="tag">extents</span> <span class="tag">changing</span> <span class="tag">gdal_raster_resize</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">without</span> <span class="tag">georeferenced</span> <span class="tag">resize</span>

    **Resize a dataset to 1000 columns and 500 lines using cubic resampling**

    ```bash
    $ gdal raster resize --size=1000,500 -r cubic in.tif out.tif --overwrite
    ```

    **Resize a dataset to half size using cubic resampling**

    ```bash
    $ gdal raster resize --size=50%,50% -r cubic in.tif out.tif --overwrite
    ```


??? note "gdal_raster_rgb_to_palette"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Rgb To Palette. Convert a RGB image into a pseudo-color / paletted image.

    **Keywords:** <span class="tag">pseudo</span> <span class="tag">into</span> <span class="tag">image</span> <span class="tag">gdal</span> <span class="tag">convert</span> <span class="tag">raster</span> <span class="tag">gdal_raster_rgb_to_palette</span> <span class="tag">operação</span> <span class="tag">color</span> <span class="tag">correspondente</span> <span class="tag">palette</span> <span class="tag">paletted</span>

    **--------**

    ```bash
    $ gdal raster rgb-to-palette input.tif output.png
    ```


??? note "gdal_raster_roughness"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Roughness. Generate a roughness map

    **Keywords:** <span class="tag">gdal_raster_roughness</span> <span class="tag">roughness</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">generate</span> <span class="tag">operação</span> <span class="tag">correspondente</span>

    **Generates a roughness map from a DTED0 file.**

    ```bash
    $ gdal raster roughness n43.dt0 out.tif --overwrite
    ```


??? note "gdal_raster_scale"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Scale. Scale the values of the bands of a raster dataset

    **Keywords:** <span class="tag">scale</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">values</span> <span class="tag">gdal_raster_scale</span> <span class="tag">correspondente</span> <span class="tag">bands</span>

    **Rescale linearly values of a UInt16 dataset from [0,4095] to a Byte dataset [0,255]**

    ```bash
    $ gdal raster scale --datatype Byte --input-min 0 --input-max 4095 uint16.tif byte.tif --overwrite
    ```


??? note "gdal_raster_select"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Select. Select a subset of bands from a raster dataset.

    **Keywords:** <span class="tag">gdal_raster_select</span> <span class="tag">from</span> <span class="tag">gdal</span> <span class="tag">select</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">subset</span> <span class="tag">bands</span>

    **Reorder a 3-band dataset with bands ordered Blue, Green, Red to Red, Green, Blue**

    ```bash
    $ gdal raster select --band 3,2,1 bgr.tif rgb.tif --overwrite
    ```

    **Select input bands by their color interpretation**

    ```bash
    $ gdal raster select --band red,green,blue input.tif rgb.tif --overwrite
    ```

    **Convert a RGBA dataset to a YCbCR JPEG compressed GeoTIFF**

    ```bash
    $ gdal raster select --band 1,2,3 --mask 4 --co COMPRESS=JPEG,PHOTOMETRIC=YCBCR rgba.tif rgb_mask.tif
    ```


??? note "gdal_raster_set_type"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Set Type. Modify the data type of bands of a raster dataset.

    **Keywords:** <span class="tag">bands</span> <span class="tag">gdal</span> <span class="tag">gdal_raster_set_type</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">modify</span> <span class="tag">correspondente</span> <span class="tag">type</span> <span class="tag">data</span>

    **Convert to Float32 data type**

    ```bash
    $ gdal raster set-type --datatype Float32 byte.tif float32.tif --overwrite
    ```


??? note "gdal_raster_sieve"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Sieve. Remove small raster polygons

    **Keywords:** <span class="tag">polygons</span> <span class="tag">gdal</span> <span class="tag">sieve</span> <span class="tag">small</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">remove</span> <span class="tag">gdal_raster_sieve</span>

    **Remove polygons smaller than 10 pixels from the band 2 of a raster.**

    ```bash
    $ gdal raster sieve -b 2 -s 10 input.tif output.tif
    ```


??? note "gdal_raster_slope"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Slope. Generate a slope map

    **Keywords:** <span class="tag">gdal_raster_slope</span> <span class="tag">slope</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">generate</span> <span class="tag">operação</span> <span class="tag">correspondente</span>

    **Generates a slope map from a DTED0 file.**

    ```bash
    $ gdal raster slope n43.dt0 out.tif --overwrite
    ```


??? note "gdal_raster_stack"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Stack. Combine together input bands into a multi-band output, either virtual (VRT) or materialized.

    **Keywords:** <span class="tag">gdal_raster_stack</span> <span class="tag">output</span> <span class="tag">multi</span> <span class="tag">input</span> <span class="tag">into</span> <span class="tag">gdal</span> <span class="tag">together</span> <span class="tag">band</span> <span class="tag">raster</span> <span class="tag">either</span> <span class="tag">operação</span> <span class="tag">stack</span>

    **Make a RGB stack from 3 single-band input files**

    ```bash
    gdal raster stack red.tif green.tif blue.tif rgb.tif
    ```

    **Make a virtual (VRT) stack from 2 single-band input files**

    ```bash
    gdal raster stack raster1.tif raster2.tif result.vrt
    ```


??? note "gdal_raster_tile"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Tile. Generate tiles in separate files from a raster dataset.

    **Keywords:** <span class="tag">from</span> <span class="tag">files</span> <span class="tag">gdal</span> <span class="tag">tiles</span> <span class="tag">gdal_raster_tile</span> <span class="tag">raster</span> <span class="tag">separate</span> <span class="tag">generate</span> <span class="tag">operação</span> <span class="tag">tile</span> <span class="tag">dataset</span> <span class="tag">correspondente</span>

    **Generate PNG tiles with WebMercatorQuad tiling scheme for zoom levels 2 to 5.**

    ```bash
    gdal raster tile --min-zoom=2 --max-zoom=5 input.tif output_folder
    ```

    **Retile a raster using its origin and resolution**

    ```bash
    gdal raster tile --tiling-scheme raster input.tif output_folder
    ```

    **Creating a tiled dataset, compatible with the Spatio-Temporal Asset Catalog Tiled Assets specification, using Cloud-Optimized GeoTIFF metatiles of dimension 4096x4096.**

    ```bash
    gdal raster tile --format COG --tile-size 4096 input.tif output_folder
    ```

    **Mosaic on-the-fly several input files and tile that mosaic.**

    ```bash
    gdal raster pipeline ! mosaic input*.tif ! tile output_folder
    ```


??? note "gdal_raster_tpi"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Tpi. Generate a Topographic Position Index (TPI) map

    **Keywords:** <span class="tag">topographic</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">generate</span> <span class="tag">operação</span> <span class="tag">gdal_raster_tpi</span> <span class="tag">index</span> <span class="tag">position</span> <span class="tag">correspondente</span>

    **Generates a Topographic Position Index (TPI) map from a DTED0 file.**

    ```bash
    $ gdal raster tpi n43.dt0 out.tif --overwrite
    ```


??? note "gdal_raster_tri"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Tri. Generate a Terrain Ruggedness Index (TRI) map

    **Keywords:** <span class="tag">ruggedness</span> <span class="tag">terrain</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">generate</span> <span class="tag">operação</span> <span class="tag">index</span> <span class="tag">correspondente</span> <span class="tag">gdal_raster_tri</span>

    **Generates a Terrain Ruggedness Index (TRI) map from a DTED0 file.**

    ```bash
    $ gdal raster tri n43.dt0 out.tif --overwrite
    ```


??? note "gdal_raster_unscale"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Unscale. Convert scaled values of a raster dataset into unscaled values.

    **Keywords:** <span class="tag">unscale</span> <span class="tag">into</span> <span class="tag">scaled</span> <span class="tag">gdal</span> <span class="tag">convert</span> <span class="tag">unscaled</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">values</span> <span class="tag">gdal_raster_unscale</span> <span class="tag">correspondente</span>

    **Unscale a scaled raster to a Float32 one**

    ```bash
    $ gdal raster unscale scaled_byte.tif unscaled_float32.tif --overwrite
    ```


??? note "gdal_raster_update"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Update. Update the destination raster with the content of the input one.

    **Keywords:** <span class="tag">destination</span> <span class="tag">content</span> <span class="tag">with</span> <span class="tag">input</span> <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">gdal_raster_update</span> <span class="tag">correspondente</span> <span class="tag">update</span>

    **Update existing out.tif with content of in.tif using cubic interpolation**

    ```bash
    $ gdal raster update -r cubic in.tif out.tif
    ```


??? note "gdal_raster_viewshed"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Viewshed. Compute the viewshed of a raster dataset.

    **Keywords:** <span class="tag">gdal</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span> <span class="tag">gdal_raster_viewshed</span> <span class="tag">compute</span> <span class="tag">viewshed</span>

    **Create a viewshed raster with a radius of 500 for a person standing at location (-10147017, 5108065).**

    ```bash
    gdal raster viewshed --max-distance=500 --pos=-10147017,5108065 source.tif destination.tif
    ```


??? note "gdal_raster_write"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Write. Write a raster dataset (pipeline only)

    **Keywords:** <span class="tag">only</span> <span class="tag">write</span> <span class="tag">gdal</span> <span class="tag">pipeline</span> <span class="tag">raster</span> <span class="tag">gdal_raster_write</span> <span class="tag">dataset</span> <span class="tag">operação</span> <span class="tag">correspondente</span>

    **Write a GeoTIFF file**

    ```bash
    $ gdal raster pipeline ... [other commands here] ... ! write out.tif --overwrite
    ```


??? note "gdal_raster_zonal_stats"

    <span class="badge badge-raster">Raster</span>

    Operação raster GDAL correspondente a: Zonal Stats. Compute raster zonal statistics.

    **Keywords:** <span class="tag">gdal</span> <span class="tag">gdal_raster_zonal_stats</span> <span class="tag">statistics</span> <span class="tag">raster</span> <span class="tag">operação</span> <span class="tag">stats</span> <span class="tag">correspondente</span> <span class="tag">compute</span> <span class="tag">zonal</span>

    **Summarize mean elevation within 200m of points of interest**

    ```bash
    gdal pipeline read dem.tif ! \
        zonal-stats \
          --zones [ read points.geojson ! buffer 200 ] \
          --stat mean ! \
        write \
          --output-format CSV \
          --output /vsistdout/
    ```

    **or, using the zone vector dataset as the piped dataset using the ``_PIPE_`` placeholder dataset name:**

    ```bash
    gdal pipeline read points.geojson ! \
        buffer 200 ! \
        zonal-stats \
          --input dem.tif
          --zones _PIPE_ \
          --stat mean ! \
        write \
          --output-format CSV \
          --output /vsistdout/
    ```

    **Create a layer with the highest points in each watershed**

    ```bash
    gdal pipeline read dem.tif !
        zonal-stats \
          --zones watersheds.shp \
          --stat max_center_x \
          --stat max_center_y ! \
        make-point \
          --x max_center_x \
          --y max_center_y \
          --output-crs EPSG:4326 ! \
        write out.geojson
    ```


??? note "gdal_rasterize"

    <span class="badge badge-raster">Raster</span>

    Queima geometrias vetoriais (pontos, linhas e polígonos) nas bandas de uma imagem raster.

    **Keywords:** <span class="tag">rasterizar</span> <span class="tag">queimar</span> <span class="tag">gdal_rasterize</span> <span class="tag">geometrias</span> <span class="tag">bandas</span> <span class="tag">imagem</span> <span class="tag">linhas</span> <span class="tag">raster</span> <span class="tag">queima</span> <span class="tag">polígonos</span> <span class="tag">vetoriais</span> <span class="tag">vetor para raster</span>

    **file :file:`work.tif` with the color red (RGB = 255,0,0).**

    ```bash
    gdal_rasterize -b 1 -b 2 -b 3 -burn 255 -burn 0 -burn 0 -l mask mask.shp work.tif
    ```

    **file, pulling the top elevation from the ROOF_H attribute.**

    ```bash
    gdal_rasterize -a ROOF_H -where "class='A'" -l footprints footprints.shp city_dem.tif
    ```

    **options determines the bands of the output raster.**

    ```bash
    gdal_rasterize -burn 255 -burn 0 -burn 0 -ot Byte -ts 1000 1000 -l footprints footprints.shp mask.tif
    ```


??? note "gdal_retile"

    <span class="badge badge-raster">Raster</span>

    Retiles a set of tiles and/or build tiled pyramid levels.

    **Keywords:** <span class="tag">levels</span> <span class="tag">tiles</span> <span class="tag">build</span> <span class="tag">gdal_retile</span> <span class="tag">retiles</span> <span class="tag">pyramid</span> <span class="tag">tiled</span>

    **--------**

    ```bash
    gdal_retile [--help] [--help-general]
                   [-v] [-co <NAME>=<VALUE>]... [-of <out_format>] [-ps <pixelWidth> <pixelHeight>]
                   [-overlap <val_in_pixel>]
                   [-ot  {Byte/Int8/Int16/UInt16/UInt32/Int32/Float32/Float64/
                           CInt16/CInt32/CFloat32/CFloat64}]'
                   [ -tileIndex <tileIndexName> [-tileIndexField <tileIndexFieldName>]]
                   [-csv <fileName> [-csvDelim <delimiter>]]
                   [-s_srs <srs_def>]  [-pyramidOnly]
                   [-r {near|bilinear|cubic|cubicspline|lanczos}]
                   -levels <numberoflevels>
                   [-useDirForEachRow] [-resume]
                   -targetDir <TileDirectory> <input_file> <input_file>...
    ```


??? note "gdal_sieve"

    <span class="badge badge-raster">Raster</span>

    Removes small raster polygons.

    **Keywords:** <span class="tag">polygons</span> <span class="tag">small</span> <span class="tag">raster</span> <span class="tag">removes</span> <span class="tag">gdal_sieve</span>

    **--------**

    ```bash
    gdal_sieve [--help] [--help-general]
                  [-q] [-st threshold] [-4] [-8] [-o name=value]
                  <srcfile> [-nomask] [-mask filename] [-of format] [<dstfile>]
    ```


??? note "gdal_translate"

    <span class="badge badge-raster">Raster</span>

    Converte datasets raster entre diferentes formatos, permitindo recortes, redimensionamentos e reamostragens.

    **Keywords:** <span class="tag">datasets</span> <span class="tag">converter</span> <span class="tag">conversão</span> <span class="tag">diferentes</span> <span class="tag">permitindo</span> <span class="tag">converte</span> <span class="tag">recortes</span> <span class="tag">raster</span> <span class="tag">mudar formato</span> <span class="tag">formatos</span> <span class="tag">redimensionamentos</span> <span class="tag">gdal_translate</span>

    **Creating a tiled GeoTIFF**

    ```bash
    gdal_translate -of GTiff -co "TILED=YES" utm.tif utm_tiled.tif
    ```

    **Creating a JPEG-compressed TIFF with internal mask from a RGBA dataset**

    ```bash
    gdal_translate rgba.tif withmask.tif -b 1 -b 2 -b 3 -mask 4 -co COMPRESS=JPEG \
      -co PHOTOMETRIC=YCBCR --config GDAL_TIFF_INTERNAL_MASK YES
    ```

    **Creating a RGBA dataset from a RGB dataset with a mask**

    ```bash
    gdal_translate withmask.tif rgba.tif -b 1 -b 2 -b 3 -b mask
    ```

    **Subsetting using :option:`-projwin` and :option:`-outsize`**

    ```bash
    gdal_translate -projwin -20037500 10037500 0 0 -outsize 100 100 frmt_wms_googlemaps_tms.xml junk.png
    ```

    **Use of strict mode with unsupported data type**

    ```console
    $ gdal_create test.tif -bands 3 -ot Int16 -outsize 1 1
    $ gdal_translate -strict test.tif test.webp
    ERROR 6: WEBP driver doesn't support data type Int16.
    Only UInt8 bands supported.
    ```


??? note "gdal_viewshed"

    <span class="badge badge-raster">Raster</span>

    Calculates a viewshed raster from an input raster DEM using method defined in [Wang2000]_ for a user defined point.

    **Keywords:** <span class="tag">calculates</span> <span class="tag">user</span> <span class="tag">from</span> <span class="tag">hillshade</span> <span class="tag">input</span> <span class="tag">sombra</span> <span class="tag">method</span> <span class="tag">wang2000</span> <span class="tag">defined</span> <span class="tag">relevo</span> <span class="tag">aspecto</span> <span class="tag">point</span>

    **Create a viewshed raster with a radius of 500 for a person standing at location (-10147017, 5108065).**

    ```bash
    gdal_viewshed -md 500 -ox -10147017 -oy 5108065 source.tif destination.tif
    ```


??? note "gdal_vsi"

    <span class="badge badge-raster">Raster</span>

    Entry point for GDAL Virtual System Interface (VSI) commands

    **Keywords:** <span class="tag">system</span> <span class="tag">gdal</span> <span class="tag">entry</span> <span class="tag">interface</span> <span class="tag">point</span> <span class="tag">gdal_vsi</span> <span class="tag">virtual</span> <span class="tag">commands</span>

    **Listing recursively files in /vsis3/bucket with details**

    ```console
    $ gdal vsi list -lR /vsis3/bucket
    ```


??? note "gdal_vsi_copy"

    <span class="badge badge-raster">Raster</span>

    Copy files located on GDAL Virtual System Interface (VSI)

    **Keywords:** <span class="tag">copy</span> <span class="tag">gdal_vsi_copy</span> <span class="tag">system</span> <span class="tag">files</span> <span class="tag">gdal</span> <span class="tag">interface</span> <span class="tag">virtual</span> <span class="tag">located</span>

    **Copy recursively files from /vsis3/bucket/my_dir to local directory, creating a my_dir directory if it does not exist.**

    ```console
    $ gdal vsi copy -r /vsis3/bucket/my_dir .
    ```

    **Copy recursively files from /vsis3/bucket/my_dir to local directory, *without* creating a my_dir directory, without progress bar**

    ```console
    $ gdal vsi copy --quiet -r /vsis3/bucket/my_dir/* .
    ```


??? note "gdal_vsi_delete"

    <span class="badge badge-raster">Raster</span>

    Delete files located on GDAL Virtual System Interface (VSI)

    **Keywords:** <span class="tag">delete</span> <span class="tag">system</span> <span class="tag">files</span> <span class="tag">gdal</span> <span class="tag">interface</span> <span class="tag">virtual</span> <span class="tag">gdal_vsi_delete</span> <span class="tag">located</span>

    **Delete recursively files from /vsis3/bucket/my_dir**

    ```console
    $ gdal vsi delete -r /vsis3/bucket/my_dir
    ```


??? note "gdal_vsi_list"

    <span class="badge badge-raster">Raster</span>

    List files of one of the GDAL Virtual System Interface (VSI)

    **Keywords:** <span class="tag">system</span> <span class="tag">list</span> <span class="tag">files</span> <span class="tag">gdal</span> <span class="tag">interface</span> <span class="tag">gdal_vsi_list</span> <span class="tag">virtual</span>

    **Listing recursively files in /vsis3/bucket with details**

    ```console
    $ gdal vsi list -lR /vsis3/bucket
    ```


??? note "gdal_vsi_move"

    <span class="badge badge-raster">Raster</span>

    Move/rename a file/directory located on GDAL Virtual System Interface (VSI)

    **Keywords:** <span class="tag">system</span> <span class="tag">gdal</span> <span class="tag">rename</span> <span class="tag">interface</span> <span class="tag">directory</span> <span class="tag">gdal_vsi_move</span> <span class="tag">virtual</span> <span class="tag">move</span> <span class="tag">located</span> <span class="tag">file</span>

    **Rename a file within the same virtual file system**

    ```console
    $ gdal vsi move /vsis3/bucket/my.tif /vsis3/bucket/new_name.tif
    ```

    **Move a file into another directory within the same virtual file system**

    ```console
    $ gdal vsi move /vsis3/bucket/my.tif /vsis3/bucket/existing_subdir
    ```

    **Move a directory between two different virtual file systems**

    ```console
    $ gdal vsi move /vsis3/bucket/my_directory /vsigs/bucket/
    ```


??? note "gdal_vsi_sozip"

    <span class="badge badge-raster">Raster</span>

    SOZIP (Seek-Optimized ZIP) related commands

    **Keywords:** <span class="tag">gdal_vsi_sozip</span> <span class="tag">sozip</span> <span class="tag">optimized</span> <span class="tag">seek</span> <span class="tag">related</span> <span class="tag">commands</span>

    **Create a, potentially seek-optimized, ZIP file with the content of my.gpkg**

    ```bash
    gdal vsi sozip create my.gpkg my.gpkg.zip
    ```

    **Create a, potentially seek-optimized, ZIP file from the content of a source directory:**

    ```bash
    gdal vsi sozip create -r source_dir/ my.gpkg.zip
    ```

    **Create a, potentially seek-optimized, ZIP file ``sozip_optimized.zip`` from an existing ZIP file ``in.zip``.**

    ```bash
    gdal vsi sozip optimize in.zip sozip_optimized.zip
    ```

    **List contents of ``my.zip``.**

    ```bash
    gdal vsi sozip list my.zip
    ```

    **Validate ``my.zip``.**

    ```bash
    gdal vsi sozip validate my.zip
    ```


??? note "gdal_vsi_sync"

    <span class="badge badge-raster">Raster</span>

    Synchronize source and target file/directory located on GDAL Virtual System Interface (VSI)

    **Keywords:** <span class="tag">system</span> <span class="tag">gdal</span> <span class="tag">interface</span> <span class="tag">target</span> <span class="tag">gdal_vsi_sync</span> <span class="tag">directory</span> <span class="tag">synchronize</span> <span class="tag">file</span> <span class="tag">virtual</span> <span class="tag">located</span> <span class="tag">source</span>

    **Synchronize a local directory onto a S3 bucket**

    ```console
    $ gdal vsi sync -r my_directory/ /vsis3/bucket/my_directory
    ```


??? note "gdaladdo"

    <span class="badge badge-raster">Raster</span>

    Adiciona imagens de visão geral (overviews / pirâmides) em arquivos raster para acelerar a renderização visual.

    **Keywords:** <span class="tag">gdaladdo</span> <span class="tag">overviews</span> <span class="tag">adiciona</span> <span class="tag">renderização</span> <span class="tag">pirâmides</span> <span class="tag">arquivos</span> <span class="tag">raster</span> <span class="tag">visual</span> <span class="tag">visão</span> <span class="tag">acelerar</span> <span class="tag">geral</span> <span class="tag">imagens</span>

    **Create overviews, embedded in the supplied TIFF file, with automatic computation of levels**

    ```bash
    gdaladdo -r average abc.tif
    ```

    **Create overviews, embedded in the supplied TIFF file**

    ```bash
    gdaladdo -r average abc.tif 2 4 8 16
    ```

    **Create an external compressed GeoTIFF overview file from the ERDAS .IMG file**

    ```bash
    gdaladdo -ro --config COMPRESS_OVERVIEW=YES erdas.img 2 4 8 16
    ```

    **Create an external JPEG-compressed GeoTIFF overview file from a 3-band RGB dataset**

    ```bash
    gdaladdo --config COMPRESS_OVERVIEW=JPEG --config PHOTOMETRIC_OVERVIEW=YCBCR
             --config INTERLEAVE_OVERVIEW=PIXEL rgb_dataset.ext 2 4 8 16
    ```

    **Create Erdas Imagine format overviews for the indicated JPEG file**

    ```bash
    gdaladdo --config USE_RRD=YES airphoto.jpg 3 9 27 81
    ```

    **Create overviews for a specific subdataset**

    ```bash
    gdaladdo GPKG:file.gpkg:layer
    ```

    **Refresh overviews of a VRT file**

    ```bash
    gdalbuildvrt my.vrt tile1.tif tile2.tif                          # create VRT
    gdaladdo -r cubic my.vrt                                         # initial overview generation
    touch tile1.tif                                                  # simulate update of one of the source tiles
    gdaladdo --partial-refresh-from-source-timestamp -r cubic my.vrt # refresh overviews
    ```

    **Refresh overviews of a TIFF file**

    ```bash
    gdalwarp -overwrite tile1.tif tile2.tif mosaic.tif                          # create mosaic
    gdaladdo -r cubic mosaic.tif                                                # initial overview generation
    touch tile1.tif                                                             # simulate update of one of the source tiles
    gdalwarp tile1.tif mosaic.tif                                               # update mosaic
    gdaladdo --partial-refresh-from-source-extent tile1.tif -r cubic mosaic.tif # refresh overviews
    ```


??? note "gdalattachpct"

    <span class="badge badge-raster">Raster</span>

    Attach a color table from one file to another file.

    **Keywords:** <span class="tag">attach</span> <span class="tag">from</span> <span class="tag">another</span> <span class="tag">color</span> <span class="tag">gdalattachpct</span> <span class="tag">table</span> <span class="tag">file</span>

    **--------**

    ```bash
    gdalattachpct [--help] [--help-general]
                     [-of format] <palette_file> <source_file> <dest_file>
    ```


??? note "gdalbuildvrt"

    <span class="badge badge-raster">Raster</span>

    Cria um arquivo VRT (Virtual Raster Tile) que funciona como um mosaico virtual de vários arquivos raster sem copiar dados.

    **Keywords:** <span class="tag">copiar</span> <span class="tag">mosaico</span> <span class="tag">dados</span> <span class="tag">gdalbuildvrt</span> <span class="tag">arquivo</span> <span class="tag">raster</span> <span class="tag">tile</span> <span class="tag">funciona</span> <span class="tag">virtual</span> <span class="tag">vários</span> <span class="tag">cria</span> <span class="tag">arquivos</span>

    **--------**

    ```bash
    gdalbuildvrt [--help] [--long-usage] [--help-general]
                 [--quiet]
                 [[-strict]|[-non_strict]]
                 [-tile_index <field_name>]
                 [-resolution user|average|common|highest|lowest|same]
                 [-tr <xres> <yres>] [-input_file_list <filename>]
                 [[-separate]|[-pixel-function <function>]]
                 [-pixel-function-arg <NAME>=<VALUE>]...
                 [-allow_projection_difference] [-sd <n>] [-tap]
                 [-te <xmin> <ymin> <xmax> <ymax>] [-addalpha] [-b <band>]...
                 [-hidenodata] [-overwrite]
                 [-srcnodata "<value>[ <value>]..."]
                 [-vrtnodata "<value>[ <value>]..."] [-a_srs <srs_def>]
                 [-r nearest|bilinear|cubic|cubicspline|lanczos|average|mode]
                 [-oo <NAME>=<VALUE>]... [-co <NAME>=<VALUE>]...
                 [-ignore_srcmaskband]
                 [-nodata_max_mask_threshold <threshold>]
                 <vrt_dataset_name> [<src_dataset_name>]...
    ```

    **Make a virtual mosaic from all TIFF files contained in a directory**

    ```bash
    gdalbuildvrt doq_index.vrt doq/*.tif
    ```

    **Make a virtual mosaic from files whose name is specified in a text file**

    ```bash
    gdalbuildvrt -input_file_list my_list.txt doq_index.vrt
    ```

    **Make a RGB virtual mosaic from 3 single-band input files**

    ```bash
    gdalbuildvrt -separate rgb.vrt red.tif green.tif blue.tif
    ```

    **Make a virtual mosaic with blue background colour (RGB: 0 0 255)**

    ```bash
    gdalbuildvrt -hidenodata -vrtnodata "0 0 255" doq_index.vrt doq/*.tif
    ```


??? note "gdalcompare"

    <span class="badge badge-raster">Raster</span>

    Compare two images.

    **Keywords:** <span class="tag">compare</span> <span class="tag">images</span> <span class="tag">gdalcompare</span>

    **--------**

    ```bash
    gdalcompare [--help] [--help-general]
                   [-dumpdiffs] [-skip_binary] [-skip_overviews]
                   [-skip_geolocation] [-skip_geotransform]
                   [-skip_metadata] [-skip_rpc] [-skip_srs]
                   [-sds] <golden_file> <new_file>
    ```

    **--------**

    ```bash
    gdalcompare -dumpdiffs N.tiff S.tiff; echo $?
    Files differ at the binary level.
    Band 1 checksum difference:
      Golden: 36694
      New:    40645
      Pixels Differing: 1509
      Maximum Pixel Difference: 255.0
      Wrote Diffs to: 1.tif
    Differences Found: 2
    2
    
    gdalcompare N.tiff N.tiff; echo $?
    Differences Found: 0
    0
    ```


??? note "gdaldem"

    <span class="badge badge-raster">Raster</span>

    Ferramenta para análise e geração de produtos derivados de Modelos Digitais de Elevação (DEM) como sombreamento (hillshade), declividade (slope), aspecto, etc.

    **Keywords:** <span class="tag">hillshade</span> <span class="tag">ferramenta</span> <span class="tag">slope</span> <span class="tag">sombra</span> <span class="tag">modelos</span> <span class="tag">produtos</span> <span class="tag">derivados</span> <span class="tag">aspecto</span> <span class="tag">relevo</span> <span class="tag">sombreamento</span> <span class="tag">gdaldem</span> <span class="tag">digitais</span>

    **--------**

    ```bash
    gdaldem [--help] [--help-general] <mode> <input> <output> <options>
    ```

    **Generate a shaded relief map:**

    ```bash
    gdaldem hillshade <input_dem> <output_hillshade>
                [-z <zfactor>] [[-s <scale>] | [-xscale <xscale> -yscale <yscale>]]
                [-az <azimuth>] [-alt <altitude>]
                [-alg ZevenbergenThorne] [-combined | -multidirectional | -igor]
                [-compute_edges] [-b <Band>] [-of <format>] [-co <NAME>=<VALUE>]... [-q]
    ```

    **Generate a slope map:**

    ```bash
    gdaldem slope <input_dem> <output_slope_map>
                [-p] [[-s <scale>] | [-xscale <xscale> -yscale <yscale>]]
                [-alg ZevenbergenThorne]
                [-compute_edges] [-b <band>] [-of <format>] [-co <NAME>=<VALUE>]... [-q]
    ```

    **outputs a 32-bit float raster with pixel values from 0-360 indicating azimuth:**

    ```bash
    gdaldem aspect <input_dem> <output_aspect_map>
                [-trigonometric] [-zero_for_flat]
                [-alg ZevenbergenThorne]
                [-compute_edges] [-b <band>] [-of format] [-co <NAME>=<VALUE>]... [-q]
    ```

    **Generate a color relief map:**

    ```bash
    gdaldem color-relief <input_dem> <color_text_file> <output_color_relief_map>
                 [-alpha] [-exact_color_entry | -nearest_color_entry]
                 [-b <band>] [-of format] [-co <NAME>=<VALUE>]... [-q]
    
    where color_text_file contains lines of the format "elevation_value red green blue [alpha]". If alpha column is present it can be enabled for use with '-alpha'.
    ```

    **Generate a Terrain Ruggedness Index (TRI) map:**

    ```bash
    gdaldem TRI input_dem output_TRI_map
                [-alg Wilson|Riley]
                [-compute_edges] [-b Band (default=1)] [-of format] [-q]
    ```

    **Generate a Topographic Position Index (TPI) map:**

    ```bash
    gdaldem TPI <input_dem> <output_TPI_map>
                [-compute_edges] [-b <band>] [-of <format>] [-co <NAME>=<VALUE>]... [-q]
    ```

    **Generate a roughness map:**

    ```bash
    gdaldem roughness <input_dem> <output_roughness_map>
                [-compute_edges] [-b <band>] [-of <format>] [-co <NAME>=<VALUE>]... [-q]
    ```


??? note "gdalenhance"

    <span class="badge badge-raster">Raster</span>

    Enhance the contrast of raster images using histogram equalization.

    **Keywords:** <span class="tag">enhance</span> <span class="tag">images</span> <span class="tag">contrast</span> <span class="tag">equalization</span> <span class="tag">raster</span> <span class="tag">using</span> <span class="tag">histogram</span> <span class="tag">gdalenhance</span>

    **--------**

    ```bash
    gdalenhance [--help-general]
                [-of format] [-co "NAME=VALUE"]*
                [-ot {Byte/Int16/UInt16/UInt32/Int32/Float32/Float64/
                        CInt16/CInt32/CFloat32/CFloat64}]
                [-equalize]
                [-config filename]
                <src_raster> [<dst_raster>]
    ```

    **Example of LUT file:**

    ```bash
    1:Band -0.5:ScaleMin 255.5:ScaleMax 0 0 8 16 16 17 17 17 17 18 18 18 18 18 18 19 19 19 19 20 20 20 21 21 21 22 22 22 23 23 24 24 25 25 26 27 27 28 29 30 30 31 32 33 34 35 36 37 38 39 40 42 43 44 46 47 48 50 51 53 55 56 58 60 62 63 65 67 69 71 73 75 77 79 81 83 85 87 89 91 93 95 97 99 101 103 105 107 109 111 113 115 117 119 121 123 125 127 129 131 133 135 137 138 140 142 144 146 148 150 152 153 155 157 159 161 162 164 166 168 169 171 173 174 176 178 179 181 182 184 186 187 189 190 192 193 195 196 198 199 200 202 203 205 206 207 208 210 211 212 213 214 216 217 218 219 220 221 222 223 224 225 226 227 228 229 230 231 232 233 234 234 235 236 237 238 239 239 240 241 241 242 243 244 244 245 245 246 246 247 247 248 248 249 249 250 250 250 251 251 251 251 251 252 252 252 252 252 252 252 252 252 252 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 254 254 254 254 254 254 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255
    2:Band -0.5:ScaleMin 255.5:ScaleMax 0 0 8 16 16 16 17 17 17 17 17 17 17 17 17 18 18 18 18 18 18 19 19 19 19 19 20 20 20 20 21 21 22 22 23 23 24 24 25 26 27 27 28 29 30 31 32 33 34 35 36 37 38 39 41 42 43 45 46 47 49 51 52 54 55 57 59 60 62 64 66 67 69 71 73 75 77 79 81 83 85 87 89 91 93 95 97 99 101 103 105 108 110 112 114 116 118 120 122 124 126 128 130 132 134 136 138 140 142 144 146 148 150 152 154 156 157 159 161 163 165 166 168 170 172 173 175 177 179 180 182 183 185 187 188 190 191 193 194 196 197 199 200 202 203 204 206 207 208 209 211 212 213 214 215 216 217 218 219 220 221 222 223 224 225 226 227 228 229 230 230 231 232 233 234 235 235 236 237 238 239 239 240 241 241 242 243 243 244 245 245 246 246 247 247 248 248 248 249 249 250 250 250 250 251 251 251 251 252 252 252 252 252 252 252 252 252 252 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 254 254 254 254 254 254 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255
    3:Band -0.5:ScaleMin 255.5:ScaleMax 0 0 9 17 17 18 18 18 18 18 19 19 19 19 19 19 20 20 20 20 20 20 21 21 21 21 21 21 22 22 22 22 22 23 23 23 24 24 24 25 25 26 26 27 28 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 44 45 46 47 48 50 51 53 54 56 57 59 60 62 63 65 67 69 70 72 74 76 78 80 82 84 86 88 90 92 94 97 99 101 103 105 107 109 111 113 115 116 118 120 122 124 126 127 129 131 133 134 136 138 139 141 143 144 146 147 149 151 152 154 155 157 159 160 162 163 165 167 168 170 171 173 175 176 178 179 181 182 184 186 187 189 190 192 193 195 197 198 200 201 203 204 206 207 209 210 212 213 214 216 217 218 219 220 222 223 224 225 226 227 228 229 230 231 232 233 233 234 235 236 237 238 239 239 240 241 242 243 243 244 245 246 246 247 247 248 248 249 249 250 250 251 251 251 251 252 252 252 252 252 252 252 252 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 253 254 254 255 255 255 255 255 255 2550
    ```

    **Apply equalization histogram to enhance the contrast of the image**

    ```bash
    gdalenhance -equalize rgb.tif rgb_equalize_enhance.tif
    ```

    **Write an equalization LUT to the console**

    ```bash
    gdalenhance -equalize rgb.tif
    ```

    **Apply a custom LUT (look up-table) to enhance the contrast of the image**

    ```bash
    gdalenhance -config enhance_config rgb.tif rgb_custom_enhance.tif
    ```


??? note "gdalmanage"

    <span class="badge badge-raster">Raster</span>

    Identify, delete, rename and copy dataset files.

    **Keywords:** <span class="tag">copy</span> <span class="tag">delete</span> <span class="tag">files</span> <span class="tag">rename</span> <span class="tag">dataset</span> <span class="tag">identify</span> <span class="tag">gdalmanage</span>

    **--------**

    ```bash
    Usage: gdalmanage [--help] [--help-general]
                      <mode> [-r] [-fr] [-u] [-f <format>]
                      <datasetname> [<newdatasetname>]
    ```

    **and specifying a data file name:**

    ```bash
    $ gdalmanage identify NE1_50M_SR_W.tif
    
    NE1_50M_SR_W.tif: GTiff
    ```

    **Recursive mode will scan subfolders and report the data format:**

    ```bash
    $ gdalmanage identify -r 50m_raster/
    
    NE1_50M_SR_W/ne1_50m.jpg: JPEG
    NE1_50M_SR_W/ne1_50m.png: PNG
    NE1_50M_SR_W/ne1_50m_20pct.tif: GTiff
    NE1_50M_SR_W/ne1_50m_band1.tif: GTiff
    NE1_50M_SR_W/ne1_50m_print.png: PNG
    NE1_50M_SR_W/NE1_50M_SR_W.aux: HFA
    NE1_50M_SR_W/NE1_50M_SR_W.tif: GTiff
    NE1_50M_SR_W/ne1_50m_sub.tif: GTiff
    NE1_50M_SR_W/ne1_50m_sub2.tif: GTiff
    ```

    **Copy the dataset:**

    ```bash
    $ gdalmanage copy NE1_50M_SR_W.tif ne1_copy.tif
    ```

    **Rename dataset:**

    ```bash
    $ gdalmanage rename NE1_50M_SR_W.tif ne1_rename.tif
    ```

    **Delete the dataset:**

    ```bash
    gdalmanage delete NE1_50M_SR_W.tif
    ```


??? note "gdalmdimtranslate"

    <span class="badge badge-raster">Raster</span>

    Converts multidimensional data between different formats, and perform subsetting.

    **Keywords:** <span class="tag">subsetting</span> <span class="tag">converts</span> <span class="tag">gdalmdimtranslate</span> <span class="tag">converter</span> <span class="tag">conversão</span> <span class="tag">perform</span> <span class="tag">between</span> <span class="tag">different</span> <span class="tag">mudar formato</span> <span class="tag">multidimensional</span> <span class="tag">formats</span> <span class="tag">data</span>

    **Convert a netCDF file to a multidimensional VRT file**

    ```bash
    gdalmdimtranslate in.nc out.vrt
    ```

    **Extract a 2D slice of a time,Y,X array**

    ```bash
    gdalmdimtranslate in.nc out.tif -subset 'time("2010-01-01")' -array temperature
    ```

    **Subsample along X and Y axis**

    ```bash
    gdalmdimtranslate in.nc out.nc -scaleaxes "X(2),Y(2)"
    ```

    **to bottom-to-top (or the reverse)**

    ```bash
    gdalmdimtranslate in.nc out.nc -array "name=temperature,view=[:,::-1,:]"
    ```

    **Transpose an array that has X,Y,time dimension order to time,Y,X**

    ```bash
    gdalmdimtranslate in.nc out.nc -array "name=temperature,transpose=[2,1,0]"
    ```


??? note "gdalmove"

    <span class="badge badge-raster">Raster</span>

    Transform georeferencing of raster file in place.

    **Keywords:** <span class="tag">transform</span> <span class="tag">georeferencing</span> <span class="tag">raster</span> <span class="tag">place</span> <span class="tag">gdalmove</span> <span class="tag">file</span>

    **--------**

    ```bash
    gdalmove [--help] [--help-general]
                [-s_srs <srs_defn>] -t_srs <srs_defn>
                [-et <max_pixel_err>] <target_file>
    ```


??? note "gdaltindex"

    <span class="badge badge-raster">Raster</span>

    Creates an OGR-supported dataset as a raster tileindex.

    **Keywords:** <span class="tag">gdaltindex</span> <span class="tag">raster</span> <span class="tag">dataset</span> <span class="tag">tileindex</span> <span class="tag">creates</span> <span class="tag">supported</span>

    **shape showing the bounds of the image:**

    ```bash
    gdaltindex doq_index.shp doq/*.tif
    ```

    **Perform the same command as before, but now we create a GeoPackage instead of a Shapefile.**

    ```bash
    gdaltindex -of GPKG doq_index.gpkg doq/*.tif
    ```

    **into the same output projection:**

    ```bash
    gdaltindex -t_srs EPSG:4326 -src_srs_name src_srs tile_index_mixed_srs.shp *.tif
    ```

    **for use by the GDAL GTI / Virtual Raster Tile Index driver.**

    ```bash
    gdaltindex tile_index.gti.gpkg -ot Byte -tr 60 60 -colorinterp Red,Green,Blue --optfile my_list.txt
    ```


??? note "gdaltransform"

    <span class="badge badge-raster">Raster</span>

    Transforms coordinates

    **Keywords:** <span class="tag">gdaltransform</span> <span class="tag">transforms</span> <span class="tag">coordinates</span>

    **Simple reprojection from one projected coordinate system to another:**

    ```bash
    gdaltransform -s_srs EPSG:28992 -t_srs EPSG:31370
    177502 311865
    ```

    **72" projection:**

    ```bash
    244296.724777415 165937.350217148 0
    ```

    **back to image coordinates.**

    ```bash
    gdaltransform -i -rpc 06OCT20025052-P2AS-005553965230_01_P001.TIF
    125.67206 39.85307 50
    ```

    **Produces this output measured in pixels and lines on the image:**

    ```bash
    3499.49282422381 2910.83892848414 50
    ```

    **for a coordinate at epoch 2000.0**

    ```bash
    gdaltransform -ct "+proj=pipeline +step +proj=unitconvert +xy_in=deg \
    +xy_out=rad +step +proj=cart +step +proj=helmert +convention=position_vector \
    +x=0.0127 +dx=-0.0029 +rx=-0.00039 +drx=-0.00011 +y=0.0065 +dy=-0.0002 \
    +ry=0.00080 +dry=-0.00019 +z=-0.0209 +dz=-0.0006 +rz=-0.00114 +drz=0.00007 \
    +s=0.00195 +ds=0.00001 +t_epoch=1988.0 +step +proj=cart +inv +step \
    +proj=unitconvert +xy_in=rad +xy_out=deg"
    2 49 0 2000
    ```

    **Produces this output measured in longitude degrees, latitude degrees and ellipsoid height in meters:**

    ```bash
    2.0000005420366 49.0000003766711 -0.0222802283242345
    ```

    **We'll use :ref:`--optfile &lt;raster_common_options_optfile&gt;` for easy reuse of our GCPs.**

    ```bash
    echo -output_xy \
    -gcp 0   0    -111.89114717 40.76932606 \
    -gcp 0   -500 -111.89114803 40.75846686 \
    -gcp 500 0    -111.87685039 40.76940631 > optfile.txt
    ```

    **Where is the address "370 S. 300 E."?**

    ```bash
    echo 300 -370 Address 370 S. 300 E. | gdaltransform --optfile optfile.txt
    -111.8825697384 40.761338402 Address 370 S. 300 E.
    ```

    **Nearby, a newly constructed building needs an address assigned. We use :option:`-i`:**

    ```bash
    echo -111.88705 40.76502 Building ABC123 | gdaltransform -i --optfile optfile.txt
    143.301947786644 -199.32683635161 Building ABC123
    ```


??? note "gdalwarp"

    <span class="badge badge-raster">Raster</span>

    Reprojeta imagens raster, calcula mosaicos de múltiplas imagens e ajusta resoluções de pixel.

    **Keywords:** <span class="tag">ajusta</span> <span class="tag">calcula</span> <span class="tag">resoluções</span> <span class="tag">gdalwarp</span> <span class="tag">mosaicos</span> <span class="tag">pixel</span> <span class="tag">raster</span> <span class="tag">reprojeta</span> <span class="tag">múltiplas</span> <span class="tag">imagens</span>

    **Red, Green, Blue.**

    ```bash
    gdalwarp in_bgrn.tif out_rgb.tif -b 3 -b 2 -b 1 -overwrite
    ```

    **at time.**

    ```bash
    gdal_create -if in_red.tif -bands 3 out_rgb.tif
    gdalwarp in_red.tif out_rgb.tif -srcband 1 -dstband 1
    gdalwarp in_green.tif out_rgb.tif -srcband 1 -dstband 2
    gdalwarp in_blue.tif out_rgb.tif -srcband 1 -dstband 3
    ```

    **the original values for some reason, for example:**

    ```bash
    # for this image we want to ignore black (0)
    gdalwarp -srcnodata 0 -dstnodata 0 orig-ignore-black.tif black-nodata.tif
    
    # and now we want to ignore white (0)
    gdalwarp -srcnodata 255 -dstnodata 255 orig-ignore-white.tif white-nodata.tif
    
    # and finally ignore a particular blue-grey (RGB 125 125 150)
    gdalwarp -srcnodata "125 125 150" -dstnodata "125 125 150" orig-ignore-grey.tif grey-nodata.tif
    
    # now we can mosaic them all and not worry about nodata parameters
    gdalwarp black-nodata.tif grey-nodata.tif white-nodata.tif final-mosaic.tif
    ```

    **setting the :config:`GDAL_CACHEMAX` configuration like:**

    ```bash
    gdalwarp --config GDAL_CACHEMAX 500 -wm 500 ...
    ```

    **running the following:**

    ```bash
    gdalwarp --debug on abc.tif def.tif
    ```

    **a message like the following will be output:**

    ```bash
    GDAL: 224 block reads on 32 block band 1 of utm.tif
    ```

    **like:**

    ```bash
    GDAL: GDALWarpKernel()::GWKNearestNoMasksByte()
    Src=0,0,512x512 Dst=0,0,512x512
    ```

    **follow up with :program:`gdal_translate` with compression:**

    ```bash
    gdalwarp infile tempfile.tif ...options...
    gdal_translate tempfile.tif outfile.tif -co compress=lzw ...etc.
    ```

    **real warping operation.**

    ```bash
    gdalwarp -of VRT infile tempfile.vrt ...options...
    gdal_translate tempfile.vrt outfile.tif -co compress=lzw ...etc.
    ```

    **- Basic transformation:**

    ```bash
    gdalwarp -t_srs EPSG:4326 input.tif output.tif
    ```

    **projection with a command like this:**

    ```bash
    gdalwarp -t_srs '+proj=utm +zone=11 +datum=WGS84' -overwrite raw_spot.tif utm11.tif
    ```

    **projection with a command like this:**

    ```bash
    gdalwarp -overwrite HDF4_SDS:ASTER_L1B:"pg-PR1B0000-2002031402_100_001":2 \
        pg-PR1B0000-2002031402_100_001_2.tif
    ```

    **- To apply a cutline on a un-georeferenced image and clip from pixel (220,60) to pixel (1160,690):**

    ```bash
    gdalwarp -overwrite -to SRC_METHOD=NO_GEOTRANSFORM -to DST_METHOD=NO_GEOTRANSFORM \
        -te 220 60 1160 690 -cutline cutline.csv in.png out.tif
    ```

    **where cutline.csv content is like:**

    ```bash
    id,WKT
    1,"POLYGON((....))"
    ```

    **- To transform a DEM from geoid elevations (using EGM96) to WGS84 ellipsoidal heights:**

    ```bash
    gdalwarp -overwrite in_dem.tif out_dem.tif -s_srs EPSG:4326+5773 -t_srs EPSG:4979
    ```

