# 🖥️ Biblioteca de Códigos C++ (GDAL API)

Explore tutoriais de API nativa C++ e o código-fonte completo de **325+ arquivos reais** do repositório GDAL.

---

## 🛠️ Tutoriais e Exemplos Rápidos

### Leitura Básica de Raster (GDALOpen)

<span class="badge badge-cpp">Operações Básicas</span>

**Assinatura:** `GDALDataset* poDS = (GDALDataset*) GDALOpen(filename, GA_ReadOnly)`

Carrega um dataset raster em C++, lê os metadados de geotransformação e extrai a primeira banda de pixels.

**Tags:** <span class="tag">raster</span> <span class="tag">ler</span> <span class="tag">API</span> <span class="tag">C++</span>

```cpp
#include "gdal_priv.h"
#include "cpl_conv.h"

void ReadRaster() {
    GDALAllRegister();
    GDALDataset *poDataset = (GDALDataset *) GDALOpen("imagem.tif", GA_ReadOnly);
    if(poDataset != nullptr) {
        double adfGeoTransform[6];
        if(poDataset->GetGeoTransform(adfGeoTransform) == CE_None) {
            double originX = adfGeoTransform[0];
            double originY = adfGeoTransform[3];
            double pixelSizeX = adfGeoTransform[1];
            double pixelSizeY = adfGeoTransform[5];
            printf("Resolução: X=%.2f, Y=%.2f\\n", pixelSizeX, pixelSizeY);
        }

        GDALRasterBand *poBand = poDataset->GetRasterBand(1);
        int nXSize = poBand->GetXSize();
        float *pafScanline = (float *) CPLMalloc(sizeof(float)*nXSize);
        poBand->RasterIO(GF_Read, 0, 0, nXSize, 1, pafScanline, nXSize, 1, GDT_Float32, 0, 0);

        CPLFree(pafScanline);
        GDALClose(poDataset);
    }
}
```

---

### Leitura de Vetores OGR (GDALOpenEx)

<span class="badge badge-cpp">Operações Básicas</span>

**Assinatura:** `GDALDataset* poDS = (GDALDataset*) GDALOpenEx(filename, GDAL_OF_VECTOR, ...)`

Carrega um arquivo vetorial genérico em C++, acessa suas camadas, percorre feições e lê a geometria de cada feição.

**Tags:** <span class="tag">vector</span> <span class="tag">OGR</span> <span class="tag">C++</span> <span class="tag">geometria</span>

```cpp
#include "ogrsf_frmts.h"

void ReadVector() {
    GDALAllRegister();
    GDALDataset *poDS = (GDALDataset*) GDALOpenEx("pontos.shp", GDAL_OF_VECTOR, nullptr, nullptr, nullptr);
    if(poDS != nullptr) {
        OGRLayer *poLayer = poDS->GetLayer(0);
        poLayer->ResetReading();
        OGRFeature *poFeature;

        while((poFeature = poLayer->GetNextFeature()) != nullptr) {
            OGRGeometry *poGeometry = poFeature->GetGeometryRef();
            if(poGeometry != nullptr && wkbFlatten(poGeometry->getGeometryType()) == wkbPoint) {
                OGRPoint *poPoint = poGeometry->toPoint();
                printf("ID: %lld, Coord: %.4f, %.4f\\n",
                       poFeature->GetFID(), poPoint->getX(), poPoint->getY());
            }
            OGRFeature::DestroyFeature(poFeature);
        }
        GDALClose(poDS);
    }
}
```

---

### Modelo de Driver Mínimo (nulldataset.cpp)

<span class="badge badge-cpp">Modelos de Drivers</span>

**Assinatura:** `class GDALNullDataset : public GDALDataset`

Modelo de esqueleto mínimo para criação e registro de novos drivers no ecossistema C++ do GDAL (baseado em nulldataset.cpp).

**Tags:** <span class="tag">driver</span> <span class="tag">dataset</span> <span class="tag">C++</span> <span class="tag">null</span>

```cpp
#include "gdal_priv.h"

class GDALNullDataset final : public GDALDataset
{
    int m_nLayers;
    OGRLayer **m_papoLayers;
public:
    GDALNullDataset() : m_nLayers(0), m_papoLayers(nullptr) {}
    ~GDALNullDataset() override {
        for(int i = 0; i < m_nLayers; ++i) delete m_papoLayers[i];
        CPLFree(m_papoLayers);
    }
    int GetLayerCount() const override { return m_nLayers; }

    static GDALDataset *Open(GDALOpenInfo *poOpenInfo) {
        // Exemplo: rejeitar se for arquivo físico real
        if (poOpenInfo->fpL != nullptr) return nullptr;
        return new GDALNullDataset();
    }
};

void RegisterGDALNull() {
    if (GDALGetDriverByName("NULL") != nullptr) return;
    GDALDriver *poDriver = new GDALDriver();
    poDriver->SetDescription("NULL");
    poDriver->SetMetadataItem(GDAL_DMD_LONGNAME, "NULL/Null Driver");
    poDriver->pfnOpen = GDALNullDataset::Open;
    GetGDALDriverManager()->RegisterDriver(poDriver);
}
```

---

### Dataset em Memória (memdataset.cpp)

<span class="badge badge-cpp">Modelos de Drivers</span>

**Assinatura:** `class MEMDataset : public GDALDataset`

Referência rápida sobre como instanciar rasters virtuais e ler/gravar dados em memória RAM com o driver MEM.

**Tags:** <span class="tag">RAM</span> <span class="tag">memory</span> <span class="tag">C++</span> <span class="tag">dataset</span>

```cpp
#include "gdal_priv.h"
#include "gdal_mem.h"

void CreateInMemoryRaster() {
    GDALAllRegister();
    GDALDriver *poDriver = GetGDALDriverManager()->GetDriverByName("MEM");
    if (poDriver != nullptr) {
        // Cria um dataset de 512x512 em memória (sem arquivo físico)
        GDALDataset *poDS = poDriver->Create("", 512, 512, 1, GDT_Byte, nullptr);
        GDALRasterBand *poBand = poDS->GetRasterBand(1);

        // Aloca e preenche pixels com valor cinza (128)
        GByte abyData[512];
        memset(abyData, 128, sizeof(abyData));
        poBand->RasterIO(GF_Write, 0, 0, 512, 1, abyData, 512, 1, GDT_Byte, 0, 0);

        GDALClose(poDS); // Libera a memória RAM
    }
}
```

---

## 📂 Explorador de Código Real

Para explorar o código-fonte completo dos 325+ arquivos do repositório GDAL, consulte:

<div class="cards-grid" markdown>

<div class="glass-card" markdown>
<div class="card-icon">⚙️</div>
<div class="card-title">Aplicativos (gdal/apps)</div>
<div class="card-desc">317 arquivos C++ dos utilitários de produção: gdalinfo, gdalwarp, gdal_translate, ogr2ogr e muitos mais.</div>

[:octicons-arrow-right-24: Explorar Aplicativos](apps.md)
</div>

<div class="glass-card" markdown>
<div class="card-icon">🔌</div>
<div class="card-title">Drivers (gdal/frmts)</div>
<div class="card-desc">Código-fonte dos drivers de formato: null, mem, tsx, esric — modelos reais de como implementar drivers GDAL.</div>

[:octicons-arrow-right-24: Explorar Drivers](drivers.md)
</div>

</div>

---

<div style="text-align:center; padding: 1rem; color: #4a5568; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace;">
  💡 Documentação oficial da API C++: <a href="https://gdal.org/api/" target="_blank" style="color: #22d3ee;">gdal.org/api</a>
</div>
