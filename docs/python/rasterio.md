# 🗺️ Rasterio — Operadores Python

Interface Pythônica moderna para leitura, recorte e mosaico de arquivos raster.

---

## rasterio.open

**Assinatura:** `rasterio.open(fp, mode='r', **kwargs)`

Abre arquivos raster com interface Pythônica moderna. Retorna um DatasetReader com metadados e dados.

**Tags:** <span class="tag">abrir</span> <span class="tag">raster</span> <span class="tag">leitura</span> <span class="tag">tif</span>

```python
import rasterio
with rasterio.open('raster.tif') as src:
    array = src.read(1)  # banda 1
    perfil = src.profile
    crs = src.crs
    transform = src.transform
```

---

## rasterio.mask.mask

**Assinatura:** `rasterio.mask.mask(dataset, shapes, crop=False)`

Recorta (clip) um raster usando geometrias vetoriais. Essencial para recorte por polígono.

**Tags:** <span class="tag">recortar</span> <span class="tag">clip</span> <span class="tag">máscara</span> <span class="tag">polígono</span>

```python
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
with rasterio.open('raster.tif') as src:
    out_image, out_transform = mask(src, [mapping(geom)], crop=True)
```

---

## rasterio.merge.merge

**Assinatura:** `rasterio.merge.merge(datasets, **kwargs)`

Mescla (mosaica) múltiplos datasets raster em um único raster de saída.

**Tags:** <span class="tag">mosaico</span> <span class="tag">merge</span> <span class="tag">combinar</span> <span class="tag">tiles</span>

```python
from rasterio.merge import merge
import rasterio
src_files = [rasterio.open(f) for f in arquivos]
mosaic, out_trans = merge(src_files)
```
