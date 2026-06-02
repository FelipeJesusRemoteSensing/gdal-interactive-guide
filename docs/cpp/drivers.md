# 🔌 Drivers (gdal/frmts)

Código-fonte de drivers de formato selecionados do repositório GDAL. Estes são modelos reais de como implementar drivers para novos formatos de dados geoespaciais.

**Total:** 8 arquivos

---

## Drivers (gdal/frmts/esric)

??? example "esric/esric_dataset.cpp"

    <span class="badge badge-cpp">Drivers (gdal/frmts/esric)</span> **Caminho:** `gdal/frmts/esric/esric_dataset.cpp`

    ```cpp
    /******************************************************************************
     *
     * Purpose : gdal driver for reading Esri compact cache as raster
     *           based on public documentation available at
     *           https://github.com/Esri/raster-tiles-compactcache
     *
     * Author : Lucian Plesea
     *
     * Udate : 06 / 10 / 2020
     *
     *  Copyright 2020 Esri
     *
     * SPDX-License-Identifier: MIT
     *****************************************************************************/
    
    #include "gdal_priv.h"
    #include <cassert>
    #include <vector>
    #include <algorithm>
    #include "cpl_json.h"
    #include "gdal_proxy.h"
    #include "gdal_utils.h"
    #include "cpl_vsi_virtual.h"
    
    using namespace std;
    
    CPL_C_START
    void CPL_DLL GDALRegister_ESRIC();
    CPL_C_END
    
    namespace ESRIC
    {
    
    #define ENDS_WITH_CI(a, b)                                                     \
        (strlen(a) >= strlen(b) && EQUAL(a + strlen(a) - strlen(b), b))
    
    // ESRI tpkx files use root.json
    static int IdentifyJSON(GDALOpenInfo *poOpenInfo)
    {
        if (poOpenInfo->eAccess != GA_ReadOnly || poOpenInfo->nHeaderBytes < 512)
            return false;
    
        // Recognize .tpkx file directly passed
        if (!STARTS_WITH(poOpenInfo->pszFilename, "/vsizip/") &&
    #if !defined(FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION)
            ENDS_WITH_CI(poOpenInfo->pszFilename, ".tpkx") &&
    #endif
            memcmp(poOpenInfo->pabyHeader, "PK\x03\x04", 4) == 0)
        {
            return true;
        }
    
    #if !defined(FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION)
        if (!ENDS_WITH_CI(poOpenInfo->pszFilename, "root.json"))
            return false;
    #endif
        for (int i = 0; i < 2; ++i)
        {
            const std::string osHeader(
                reinterpret_cast<char *>(poOpenInfo->pabyHeader),
                poOpenInfo->nHeaderBytes);
            if (std::string::npos != osHeader.find("tileBundlesPath"))
            {
                return true;
            }
            // If we didn't find tileBundlesPath i, the first bytes, but find
            // other elements typically of .tpkx, then ingest more bytes and
            // retry
            constexpr int MORE_BYTES = 8192;
            if (poOpenInfo->nHeaderBytes < MORE_BYTES &&
                (std::string::npos != osHeader.find("tileInfo") ||
                 std::string::npos != osHeader.find("tileImageInfo")))
            {
                poOpenInfo->TryToIngest(MORE_BYTES);
            }
            else
                break;
        }
        return false;
    }
    
    // Without full XML parsing, weak, might still fail
    static int IdentifyXML(GDALOpenInfo *poOpenInfo)
    {
        if (poOpenInfo->eAccess != GA_ReadOnly
    #if !defined(FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION)
            || !ENDS_WITH_CI(poOpenInfo->pszFilename, "conf.xml")
    #endif
            || poOpenInfo->nHeaderBytes < 512)
            return false;
        CPLString header(reinterpret_cast<char *>(poOpenInfo->pabyHeader),
                         poOpenInfo->nHeaderBytes);
        return (CPLString::npos != header.find("<CacheInfo"));
    }
    
    static int Identify(GDALOpenInfo *poOpenInfo)
    {
        return (IdentifyXML(poOpenInfo) || IdentifyJSON(poOpenInfo));
    }
    
    // Stub default delete, don't delete a tile cache from GDAL
    static CPLErr Delete(const char *)
    {
        return CE_None;
    }
    
    // Read a 32bit unsigned integer stored in little endian
    // Same as CPL_LSBUINT32PTR
    static inline GUInt32 u32lat(void *data)
    {
        GUInt32 val;
        memcpy(&val, data, 4);
        return CPL_LSBWORD32(val);
    }
    
    struct Bundle
    {
        void Init(const char *filename)
        {
            name = filename;
            fh.reset(VSIFOpenL(name.c_str(), "rb"));
            if (nullptr == fh)
                return;
            GByte header[64] = {0};
            // Check a few header locations, then read the index
            fh->Read(header, 1, 64);
            index.resize(BSZ * BSZ);
            if (3 != u32lat(header) || 5 != u32lat(header + 12) ||
                40 != u32lat(header + 32) || 0 != u32lat(header + 36) ||
                BSZ * BSZ * 8 != u32lat(header + 60) ||
                index.size() != fh->Read(index.data(), 8, index.size()))
            {
                fh.reset();
            }
    
            if constexpr (!CPL_IS_LSB)
            {
                for (auto &v : index)
                    CPL_LSBPTR64(&v);
            }
        }
    
        std::vector<GUInt64> index{};
        VSIVirtualHandleUniquePtr fh{};
        bool isV2 = false;
        CPLString name{};
        const size_t BSZ = 128;
    };
    
    class ECDataset final : public GDALDataset
    {
        friend class ECBand;
    
      public:
        ECDataset();
    
        CPLErr GetGeoTransform(GDALGeoTransform &gt) const override
        {
            gt = m_gt;
            return CE_None;
        }
    
        const OGRSpatialReference *GetSpatialRef() const override;
    
        static GDALDataset *Open(GDALOpenInfo *poOpenInfo);
        static GDALDataset *Open(GDALOpenInfo *poOpenInfo,
                                 const char *pszDescription);
    
      protected:
        GDALGeoTransform m_gt{};
        CPLString dname{};
        int isV2{};  // V2 bundle format
        int BSZ{};   // Bundle size in tiles
        int TSZ{};   // Tile size in pixels
        std::vector<Bundle> bundles{};
    
        Bundle &GetBundle(const char *fname);
    
      private:
        CPLErr Initialize(CPLXMLNode *CacheInfo, bool ignoreOversizedLods);
        CPLErr InitializeFromJSON(const CPLJSONObject &oRoot,
                                  bool ignoreOversizedLods);
        CPLString compression{};
        std::vector<double> resolutions{};
        int m_nMinLOD = 0;
        OGRSpatialReference oSRS{};
        std::vector<GByte> tilebuffer{};  // Last read tile, decompressed
        std::vector<GByte> filebuffer{};  // raw tile buffer
    
        OGREnvelope m_sInitialExtent{};
        OGREnvelope m_sFullExtent{};
    };
    
    const OGRSpatialReference *ECDataset::GetSpatialRef() const
    {
        return &oSRS;
    }
    
    class ECBand final : public GDALRasterBand
    {
        friend class ECDataset;
    
      public:
        ECBand(ECDataset *parent, int b, int level = 0);
        ~ECBand() override;
    
        CPLErr IReadBlock(int xblk, int yblk, void *buffer) override;
    
        GDALColorInterp GetColorInterpretation() override
        {
            return ci;
        }
    
        int GetOverviewCount() override
        {
            return static_cast<int>(overviews.size());
        }
    
        GDALRasterBand *GetOverview(int n) override
        {
            return (n >= 0 && n < GetOverviewCount()) ? overviews[n] : nullptr;
        }
    
      protected:
      private:
        int lvl{};
        GDALColorInterp ci{};
    
        // Image image;
        void AddOverviews();
        std::vector<ECBand *> overviews{};
    };
    
    ECDataset::ECDataset() : isV2(true), BSZ(128), TSZ(256)
    {
    }
    
    CPLErr ECDataset::Initialize(CPLXMLNode *CacheInfo, bool ignoreOversizedLods)
    {
        CPLErr error = CE_None;
        try
        {
            CPLXMLNode *CSI = CPLGetXMLNode(CacheInfo, "CacheStorageInfo");
            CPLXMLNode *TCI = CPLGetXMLNode(CacheInfo, "TileCacheInfo");
            if (!CSI || !TCI)
                throw CPLString("Error parsing cache configuration");
            auto format = CPLGetXMLValue(CSI, "StorageFormat", "");
            isV2 = EQUAL(format, "esriMapCacheStorageModeCompactV2");
            if (!isV2)
                throw CPLString("Not recognized as esri V2 bundled cache");
            if (BSZ != CPLAtof(CPLGetXMLValue(CSI, "PacketSize", "128")))
                throw CPLString("Only PacketSize of 128 is supported");
            TSZ = static_cast<int>(CPLAtof(CPLGetXMLValue(TCI, "TileCols", "256")));
            if (TSZ != CPLAtof(CPLGetXMLValue(TCI, "TileRows", "256")))
                throw CPLString("Non-square tiles are not supported");
            if (TSZ < 0 || TSZ > 8192)
                throw CPLString("Unsupported TileCols value");
    
            double minx = CPLAtof(CPLGetXMLValue(TCI, "TileOrigin.X", "-180"));
            double maxy = CPLAtof(CPLGetXMLValue(TCI, "TileOrigin.Y", "90"));
            // Assume symmetric coverage, check custom end
            double maxx = -minx;
            double miny = -maxy;
            const char *pszmaxx = CPLGetXMLValue(TCI, "TileEnd.X", nullptr);
            const char *pszminy = CPLGetXMLValue(TCI, "TileEnd.Y", nullptr);
            if (pszmaxx && pszminy)
            {
                maxx = CPLAtof(pszmaxx);
                miny = CPLAtof(pszminy);
            }
    
            CPLXMLNode *LODInfo = CPLGetXMLNode(TCI, "LODInfos.LODInfo");
            double res = 0;
            while (LODInfo)
            {
                res = CPLAtof(CPLGetXMLValue(LODInfo, "Resolution", "0"));
                if (!(res > 0))
                    throw CPLString("Can't parse resolution for LOD");
    
                double dxsz = (maxx - minx) / res;
                double dysz = (maxy - miny) / res;
                // Allow size just above INT32_MAX to handle FP rounding. Actual size is later clamped to INT32_MAX
                double maxRasterSize = static_cast<double>(INT32_MAX) + 2;
                if (dxsz < 1 || dxsz > maxRasterSize || dysz < 1 ||
                    dysz > maxRasterSize)
                {
                    if (ignoreOversizedLods)
                    {
                        CPLDebug(
                            "ESRIC",
                            "Skipping resolution %.10f: raster size exceeds the "
                            "GDAL limit",
                            res);
                    }
                    else
                    {
                        throw CPLString(
                            "Too many levels, resulting raster size exceeds "
                            "the GDAL limit. Open with IGNORE_OVERSIZED_LODS=YES "
                            "to ignore this");
                    }
                }
                else
                {
                    resolutions.push_back(res);
                }
    
                LODInfo = LODInfo->psNext;
            }
    
            sort(resolutions.begin(), resolutions.end());
            if (resolutions.empty())
                throw CPLString("Can't parse LODInfos");
    
            CPLString RawProj(
                CPLGetXMLValue(TCI, "SpatialReference.WKT", "EPSG:4326"));
            if (OGRERR_NONE != oSRS.SetFromUserInput(RawProj.c_str()))
                throw CPLString("Invalid Spatial Reference");
            oSRS.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER);
    
            // resolution is the smallest figure
            res = resolutions[0];
            m_gt = GDALGeoTransform();
            m_gt.xorig = minx;
            m_gt.yorig = maxy;
            m_gt.xscale = res;
            m_gt.yscale = -res;
    
            double dxsz = (maxx - minx) / res;
            double dysz = (maxy - miny) / res;
    
            nRasterXSize = int(std::min(dxsz, double(INT32_MAX)));
            nRasterYSize = int(std::min(dysz, double(INT32_MAX)));
    
            SetMetadataItem("INTERLEAVE", "PIXEL", "IMAGE_STRUCTURE");
            compression =
                CPLGetXMLValue(CacheInfo, "TileImageInfo.CacheTileFormat", "JPEG");
            SetMetadataItem("COMPRESS", compression.c_str(), "IMAGE_STRUCTURE");
    
            nBands = EQUAL(compression, "JPEG") ? 3 : 4;
            for (int i = 1; i <= nBands; i++)
            {
                ECBand *band = new ECBand(this, i);
                SetBand(i, band);
            }
            // Keep 4 bundle files open
            bundles.resize(4);
        }
        catch (CPLString &err)
        {
            error = CE_Failure;
            CPLError(error, CPLE_OpenFailed, "%s", err.c_str());
        }
        return error;
    }
    
    static std::unique_ptr<OGRSpatialReference>
    CreateSRS(const CPLJSONObject &oSRSRoot)
    {
        auto poSRS = std::make_unique<OGRSpatialReference>();
    
        bool bSuccess = false;
        const int nCode = oSRSRoot.GetInteger("wkid");
        // The concept of LatestWKID is explained in
        // https://support.esri.com/en/technical-article/000013950
        const int nLatestCode = oSRSRoot.GetInteger("latestWkid");
    
        // Try first with nLatestWKID as there is a higher chance it is a
        // EPSG code and not an ESRI one.
        if (nLatestCode > 0)
        {
            if (nLatestCode > 32767)
            {
                if (poSRS->SetFromUserInput(CPLSPrintf("ESRI:%d", nLatestCode)) ==
                    OGRERR_NONE)
                {
                    bSuccess = true;
                }
            }
            else if (poSRS->importFromEPSG(nLatestCode) == OGRERR_NONE)
            {
                bSuccess = true;
            }
        }
        if (!bSuccess && nCode > 0)
        {
            if (nCode > 32767)
            {
                if (poSRS->SetFromUserInput(CPLSPrintf("ESRI:%d", nCode)) ==
                    OGRERR_NONE)
                {
                    bSuccess = true;
                }
            }
            else if (poSRS->importFromEPSG(nCode) == OGRERR_NONE)
            {
                bSuccess = true;
            }
        }
        if (!bSuccess)
        {
            return nullptr;
        }
    
        poSRS->SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER);
        return poSRS;
    }
    
    CPLErr ECDataset::InitializeFromJSON(const CPLJSONObject &oRoot,
                                         bool ignoreOversizedLods)
    {
        CPLErr error = CE_None;
        try
        {
            auto format = oRoot.GetString("storageInfo/storageFormat");
            isV2 = EQUAL(format.c_str(), "esriMapCacheStorageModeCompactV2");
            if (!isV2)
                throw CPLString("Not recognized as esri V2 bundled cache");
            if (BSZ != oRoot.GetInteger("storageInfo/packetSize"))
                throw CPLString("Only PacketSize of 128 is supported");
    
            TSZ = oRoot.GetInteger("tileInfo/rows");
            if (TSZ != oRoot.GetInteger("tileInfo/cols"))
                throw CPLString("Non-square tiles are not supported");
            if (TSZ < 0 || TSZ > 8192)
                throw CPLString("Unsupported tileInfo/rows value");
    
            double minx = oRoot.GetDouble("tileInfo/origin/x");
            double maxy = oRoot.GetDouble("tileInfo/origin/y");
            // Assume symmetric coverage
            double maxx = -minx;
            double miny = -maxy;
    
            const auto oLODs = oRoot.GetArray("tileInfo/lods");
            double res = 0;
            // we need to skip levels that don't have bundle files
            m_nMinLOD = oRoot.GetInteger("minLOD");
            if (m_nMinLOD < 0 || m_nMinLOD >= 31)
                throw CPLString("Invalid minLOD");
            const int maxLOD = std::min(oRoot.GetInteger("maxLOD"), 31);
            for (const auto &oLOD : oLODs)
            {
                const int level = oLOD.GetInteger("level");
                if (level < m_nMinLOD || level > maxLOD)
                    continue;
    
                res = oLOD.GetDouble("resolution");
                if (!(res > 0))
                    throw CPLString("Can't parse resolution for LOD");
    
                double dxsz = (maxx - minx) / res;
                double dysz = (maxy - miny) / res;
                // Allow size just above INT32_MAX to handle FP rounding. Actual size is later clamped to INT32_MAX
                double maxRasterSize = static_cast<double>(INT32_MAX) + 2;
                if (dxsz < 1 || dxsz > maxRasterSize || dysz < 1 ||
                    dysz > maxRasterSize)
                {
                    if (ignoreOversizedLods)
                    {
                        CPLDebug("ESRIC",
                                 "Skipping LOD with resolution %.10f: raster size "
                                 "exceeds the GDAL limit",
                                 res);
                        continue;
                    }
                    else
                    {
                        throw CPLString(
                            "Too many levels, resulting raster size exceeds "
                            "the GDAL limit. Open with IGNORE_OVERSIZED_LODS=YES "
                            "to ignore this");
                    }
                }
    
                resolutions.push_back(res);
            }
            sort(resolutions.begin(), resolutions.end());
            if (resolutions.empty())
                throw CPLString("Can't parse lods");
    
            {
                auto poSRS = CreateSRS(oRoot.GetObj("spatialReference"));
                if (!poSRS)
                {
                    throw CPLString("Invalid Spatial Reference");
                }
                oSRS = std::move(*poSRS);
            }
    
            // resolution is the smallest figure
            res = resolutions[0];
            m_gt = GDALGeoTransform();
            m_gt.xorig = minx;
            m_gt.yorig = maxy;
            m_gt.xscale = res;
            m_gt.yscale = -res;
    
            double dxsz = (maxx - minx) / res;
            double dysz = (maxy - miny) / res;
    
            nRasterXSize = int(std::min(dxsz, double(INT32_MAX)));
            nRasterYSize = int(std::min(dysz, double(INT32_MAX)));
    
            SetMetadataItem("INTERLEAVE", "PIXEL", "IMAGE_STRUCTURE");
            compression = oRoot.GetString("tileImageInfo/format");
            SetMetadataItem("COMPRESS", compression.c_str(), "IMAGE_STRUCTURE");
    
            auto oInitialExtent = oRoot.GetObj("initialExtent");
            if (oInitialExtent.IsValid() &&
                oInitialExtent.GetType() == CPLJSONObject::Type::Object)
            {
                m_sInitialExtent.MinX = oInitialExtent.GetDouble("xmin");
                m_sInitialExtent.MinY = oInitialExtent.GetDouble("ymin");
                m_sInitialExtent.MaxX = oInitialExtent.GetDouble("xmax");
                m_sInitialExtent.MaxY = oInitialExtent.GetDouble("ymax");
                auto oSRSRoot = oInitialExtent.GetObj("spatialReference");
                if (oSRSRoot.IsValid())
                {
                    auto poSRS = CreateSRS(oSRSRoot);
                    if (!poSRS)
                    {
                        throw CPLString(
                            "Invalid Spatial Reference in initialExtent");
                    }
                    if (!poSRS->IsSame(&oSRS))
                    {
                        CPLError(CE_Warning, CPLE_AppDefined,
                                 "Ignoring initialExtent, because its SRS is "
                                 "different from the main one");
                        m_sInitialExtent = OGREnvelope();
                    }
                }
            }
    
            auto oFullExtent = oRoot.GetObj("fullExtent");
            if (oFullExtent.IsValid() &&
                oFullExtent.GetType() == CPLJSONObject::Type::Object)
            {
                m_sFullExtent.MinX = oFullExtent.GetDouble("xmin");
                m_sFullExtent.MinY = oFullExtent.GetDouble("ymin");
                m_sFullExtent.MaxX = oFullExtent.GetDouble("xmax");
                m_sFullExtent.MaxY = oFullExtent.GetDouble("ymax");
                auto oSRSRoot = oFullExtent.GetObj("spatialReference");
                if (oSRSRoot.IsValid())
                {
                    auto poSRS = CreateSRS(oSRSRoot);
                    if (!poSRS)
                    {
                        throw CPLString("Invalid Spatial Reference in fullExtent");
                    }
                    if (!poSRS->IsSame(&oSRS))
                    {
                        CPLError(CE_Warning, CPLE_AppDefined,
                                 "Ignoring fullExtent, because its SRS is "
                                 "different from the main one");
                        m_sFullExtent = OGREnvelope();
                    }
                }
            }
    
            nBands = EQUAL(compression, "JPEG") ? 3 : 4;
            for (int i = 1; i <= nBands; i++)
            {
                ECBand *band = new ECBand(this, i);
                SetBand(i, band);
            }
            // Keep 4 bundle files open
            bundles.resize(4);
        }
        catch (CPLString &err)
        {
            error = CE_Failure;
            CPLError(error, CPLE_OpenFailed, "%s", err.c_str());
        }
        return error;
    }
    
    class ESRICProxyRasterBand final : public GDALProxyRasterBand
    {
      private:
        GDALRasterBand *m_poUnderlyingBand = nullptr;
    
        CPL_DISALLOW_COPY_ASSIGN(ESRICProxyRasterBand)
    
      protected:
        GDALRasterBand *RefUnderlyingRasterBand(bool /*bForceOpen*/) const override;
    
      public:
        explicit ESRICProxyRasterBand(GDALRasterBand *poUnderlyingBand)
            : m_poUnderlyingBand(poUnderlyingBand)
        {
            nBand = poUnderlyingBand->GetBand();
            eDataType = poUnderlyingBand->GetRasterDataType();
            nRasterXSize = poUnderlyingBand->GetXSize();
            nRasterYSize = poUnderlyingBand->GetYSize();
            poUnderlyingBand->GetBlockSize(&nBlockXSize, &nBlockYSize);
        }
    };
    
    GDALRasterBand *
    ESRICProxyRasterBand::RefUnderlyingRasterBand(bool /*bForceOpen*/) const
    {
        return m_poUnderlyingBand;
    }
    
    class ESRICProxyDataset final : public GDALProxyDataset
    {
      private:
        // m_poSrcDS must be placed before m_poUnderlyingDS for proper destruction
        // as m_poUnderlyingDS references m_poSrcDS
        std::unique_ptr<GDALDataset> m_poSrcDS{};
        std::unique_ptr<GDALDataset> m_poUnderlyingDS{};
        CPLStringList m_aosFileList{};
    
      protected:
        GDALDataset *RefUnderlyingDataset() const override;
    
      public:
        ESRICProxyDataset(GDALDataset *poSrcDS, GDALDataset *poUnderlyingDS,
                          const char *pszDescription)
            : m_poSrcDS(poSrcDS), m_poUnderlyingDS(poUnderlyingDS)
        {
            nRasterXSize = poUnderlyingDS->GetRasterXSize();
            nRasterYSize = poUnderlyingDS->GetRasterYSize();
            for (int i = 0; i < poUnderlyingDS->GetRasterCount(); ++i)
                SetBand(i + 1, new ESRICProxyRasterBand(
                                   poUnderlyingDS->GetRasterBand(i + 1)));
            m_aosFileList.AddString(pszDescription);
        }
    
        GDALDriver *GetDriver() const override
        {
            return GDALDriver::FromHandle(GDALGetDriverByName("ESRIC"));
        }
    
        char **GetFileList() override
        {
            return CSLDuplicate(m_aosFileList.List());
        }
    };
    
    GDALDataset *ESRICProxyDataset::RefUnderlyingDataset() const
    {
        return m_poUnderlyingDS.get();
    }
    
    GDALDataset *ECDataset::Open(GDALOpenInfo *poOpenInfo)
    {
        return Open(poOpenInfo, poOpenInfo->pszFilename);
    }
    
    GDALDataset *ECDataset::Open(GDALOpenInfo *poOpenInfo,
                                 const char *pszDescription)
    {
        bool ignoreOversizedLods = CPL_TO_BOOL(CSLFetchBoolean(
            poOpenInfo->papszOpenOptions, "IGNORE_OVERSIZED_LODS", FALSE));
        if (IdentifyXML(poOpenInfo))
        {
            CPLXMLNode *config = CPLParseXMLFile(poOpenInfo->pszFilename);
            if (!config)  // Error was reported from parsing XML
                return nullptr;
            CPLXMLNode *CacheInfo = CPLGetXMLNode(config, "=CacheInfo");
            if (!CacheInfo)
            {
                CPLError(
                    CE_Warning, CPLE_OpenFailed,
                    "Error parsing configuration, can't find CacheInfo element");
                CPLDestroyXMLNode(config);
                return nullptr;
            }
            auto ds = new ECDataset();
            ds->dname = CPLGetDirnameSafe(poOpenInfo->pszFilename) + "/_alllayers";
            CPLErr error = ds->Initialize(CacheInfo, ignoreOversizedLods);
            CPLDestroyXMLNode(config);
            if (CE_None != error)
            {
                delete ds;
                ds = nullptr;
            }
            return ds;
        }
        else if (IdentifyJSON(poOpenInfo))
        {
            // Recognize .tpkx file directly passed
            if (!STARTS_WITH(poOpenInfo->pszFilename, "/vsizip/") &&
    #if !defined(FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION)
                ENDS_WITH_CI(poOpenInfo->pszFilename, ".tpkx") &&
    #endif
                memcmp(poOpenInfo->pabyHeader, "PK\x03\x04", 4) == 0)
            {
                GDALOpenInfo oOpenInfo((std::string("/vsizip/{") +
                                        poOpenInfo->pszFilename + "}/root.json")
                                           .c_str(),
                                       GA_ReadOnly);
                oOpenInfo.papszOpenOptions = poOpenInfo->papszOpenOptions;
                return Open(&oOpenInfo, pszDescription);
            }
    
            CPLJSONDocument oJSONDocument;
            if (!oJSONDocument.Load(poOpenInfo->pszFilename))
            {
                CPLError(CE_Warning, CPLE_OpenFailed,
                         "Error parsing configuration");
                return nullptr;
            }
    
            const CPLJSONObject &oRoot = oJSONDocument.GetRoot();
            if (!oRoot.IsValid())
            {
                CPLError(CE_Warning, CPLE_OpenFailed, "Invalid json document root");
                return nullptr;
            }
    
            auto ds = std::make_unique<ECDataset>();
            auto tileBundlesPath = oRoot.GetString("tileBundlesPath");
            // Strip leading relative path indicator (if present)
            if (tileBundlesPath.substr(0, 2) == "./")
            {
                tileBundlesPath.erase(0, 2);
            }
    
            ds->dname.Printf("%s/%s",
                             CPLGetDirnameSafe(poOpenInfo->pszFilename).c_str(),
                             tileBundlesPath.c_str());
            CPLErr error = ds->InitializeFromJSON(oRoot, ignoreOversizedLods);
            if (CE_None != error)
            {
                return nullptr;
            }
    
            const bool bIsFullExtentValid =
                (ds->m_sFullExtent.IsInit() &&
                 ds->m_sFullExtent.MinX < ds->m_sFullExtent.MaxX &&
                 ds->m_sFullExtent.MinY < ds->m_sFullExtent.MaxY);
            const char *pszExtentSource =
                CSLFetchNameValue(poOpenInfo->papszOpenOptions, "EXTENT_SOURCE");
    
            CPLStringList aosOptions;
            if ((!pszExtentSource && bIsFullExtentValid) ||
                (pszExtentSource && EQUAL(pszExtentSource, "FULL_EXTENT")))
            {
                if (!bIsFullExtentValid)
                {
                    CPLError(CE_Failure, CPLE_AppDefined,
                             "fullExtent is not valid");
                    return nullptr;
                }
                aosOptions.AddString("-projwin");
                aosOptions.AddString(CPLSPrintf("%.17g", ds->m_sFullExtent.MinX));
                aosOptions.AddString(CPLSPrintf("%.17g", ds->m_sFullExtent.MaxY));
                aosOptions.AddString(CPLSPrintf("%.17g", ds->m_sFullExtent.MaxX));
                aosOptions.AddString(CPLSPrintf("%.17g", ds->m_sFullExtent.MinY));
            }
            else if (pszExtentSource && EQUAL(pszExtentSource, "INITIAL_EXTENT"))
            {
                const bool bIsInitialExtentValid =
                    (ds->m_sInitialExtent.IsInit() &&
                     ds->m_sInitialExtent.MinX < ds->m_sInitialExtent.MaxX &&
                     ds->m_sInitialExtent.MinY < ds->m_sInitialExtent.MaxY);
                if (!bIsInitialExtentValid)
                {
                    CPLError(CE_Failure, CPLE_AppDefined,
                             "initialExtent is not valid");
                    return nullptr;
                }
                aosOptions.AddString("-projwin");
                aosOptions.AddString(
                    CPLSPrintf("%.17g", ds->m_sInitialExtent.MinX));
                aosOptions.AddString(
                    CPLSPrintf("%.17g", ds->m_sInitialExtent.MaxY));
                aosOptions.AddString(
                    CPLSPrintf("%.17g", ds->m_sInitialExtent.MaxX));
                aosOptions.AddString(
                    CPLSPrintf("%.17g", ds->m_sInitialExtent.MinY));
            }
    
            if (!aosOptions.empty())
            {
                aosOptions.AddString("-of");
                aosOptions.AddString("VRT");
                aosOptions.AddString("-co");
                aosOptions.AddString(CPLSPrintf("BLOCKXSIZE=%d", ds->TSZ));
                aosOptions.AddString("-co");
                aosOptions.AddString(CPLSPrintf("BLOCKYSIZE=%d", ds->TSZ));
                auto psOptions =
                    GDALTranslateOptionsNew(aosOptions.List(), nullptr);
                auto hDS = GDALTranslate("", GDALDataset::ToHandle(ds.get()),
                                         psOptions, nullptr);
                GDALTranslateOptionsFree(psOptions);
                if (!hDS)
                {
                    return nullptr;
                }
                return new ESRICProxyDataset(
                    ds.release(), GDALDataset::FromHandle(hDS), pszDescription);
            }
            return ds.release();
        }
        return nullptr;
    }
    
    // Fetch a reference to an initialized bundle, based on file name
    // The returned bundle could still have an invalid file handle, if the
    // target bundle is not valid
    Bundle &ECDataset::GetBundle(const char *fname)
    {
        for (auto &bundle : bundles)
        {
            // If a bundle is missing, it still occupies a slot, with fh == nullptr
            if (EQUAL(bundle.name.c_str(), fname))
                return bundle;
        }
        // Not found, look for an empty // missing slot
        for (auto &bundle : bundles)
        {
            if (nullptr == bundle.fh)
            {
                bundle.Init(fname);
                return bundle;
            }
        }
        // No empties, eject one
        Bundle &bundle = bundles[
    #ifndef __COVERITY__
            rand() % bundles.size()
    #else
            0
    #endif
        ];
        bundle.Init(fname);
        return bundle;
    }
    
    ECBand::~ECBand()
    {
        for (auto ovr : overviews)
            if (ovr)
                delete ovr;
        overviews.clear();
    }
    
    ECBand::ECBand(ECDataset *parent, int b, int level)
        : lvl(level), ci(GCI_Undefined)
    {
        static const GDALColorInterp rgba[4] = {GCI_RedBand, GCI_GreenBand,
                                                GCI_BlueBand, GCI_AlphaBand};
        static const GDALColorInterp la[2] = {GCI_GrayIndex, GCI_AlphaBand};
        poDS = parent;
        nBand = b;
    
        double factor = parent->resolutions[0] / parent->resolutions[lvl];
        nRasterXSize = static_cast<int>(parent->nRasterXSize * factor + 0.5);
        nRasterYSize = static_cast<int>(parent->nRasterYSize * factor + 0.5);
        nBlockXSize = nBlockYSize = parent->TSZ;
    
        // Default color interpretation
        assert(b - 1 >= 0);
        if (parent->nBands >= 3)
        {
            assert(b - 1 < static_cast<int>(CPL_ARRAYSIZE(rgba)));
            ci = rgba[b - 1];
        }
        else
        {
            assert(b - 1 < static_cast<int>(CPL_ARRAYSIZE(la)));
            ci = la[b - 1];
        }
        if (0 == lvl)
            AddOverviews();
    }
    
    void ECBand::AddOverviews()
    {
        auto parent = cpl::down_cast<ECDataset *>(poDS);
        for (size_t i = 1; i < parent->resolutions.size(); i++)
        {
            ECBand *ovl = new ECBand(parent, nBand, int(i));
            if (!ovl)
                break;
            overviews.push_back(ovl);
        }
    }
    
    CPLErr ECBand::IReadBlock(int nBlockXOff, int nBlockYOff, void *pData)
    {
        auto parent = cpl::down_cast<ECDataset *>(poDS);
        auto &buffer = parent->tilebuffer;
        auto TSZ = parent->TSZ;
        auto BSZ = parent->BSZ;
        size_t nBytes = size_t(TSZ) * TSZ;
    
        buffer.resize(nBytes * parent->nBands);
    
        const int lxx = parent->m_nMinLOD +
                        static_cast<int>(parent->resolutions.size() - lvl - 1);
        int bx, by;
        bx = (nBlockXOff / BSZ) * BSZ;
        by = (nBlockYOff / BSZ) * BSZ;
        CPLString fname;
        fname = CPLString().Printf("%s/L%02d/R%04xC%04x.bundle",
                                   parent->dname.c_str(), lxx, by, bx);
        Bundle &bundle = parent->GetBundle(fname);
        if (nullptr == bundle.fh)
        {  // This is not an error in general, bundles can be missing
            CPLDebug("ESRIC", "Can't open bundle %s", fname.c_str());
            memset(pData, 0, nBytes);
            return CE_None;
        }
        int block = static_cast<int>((nBlockYOff % BSZ) * BSZ + (nBlockXOff % BSZ));
        GUInt64 offset = bundle.index[block] & 0xffffffffffull;
        GUInt64 size = bundle.index[block] >> 40;
        if (0 == size)
        {
            memset(pData, 0, nBytes);
            return CE_None;
        }
        auto &fbuffer = parent->filebuffer;
        fbuffer.resize(size_t(size));
        bundle.fh->Seek(offset, SEEK_SET);
        if (size != bundle.fh->Read(fbuffer.data(), size_t(1), size_t(size)))
        {
            CPLError(CE_Failure, CPLE_FileIO,
                     "Error reading tile, reading " CPL_FRMT_GUIB
                     " at " CPL_FRMT_GUIB,
                     GUInt64(size), GUInt64(offset));
            return CE_Failure;
        }
        const CPLString magic(VSIMemGenerateHiddenFilename("esric.tmp"));
        auto mfh = VSIFileFromMemBuffer(magic.c_str(), fbuffer.data(), size, false);
        VSIFCloseL(mfh);
        // Can't open a raster by handle?
        auto inds = GDALOpen(magic.c_str(), GA_ReadOnly);
        if (!inds)
        {
            VSIUnlink(magic.c_str());
            CPLError(CE_Failure, CPLE_FileIO, "Error opening tile");
            return CE_Failure;
        }
        // Duplicate first band if not sufficient bands are provided
        auto inbands = GDALGetRasterCount(inds);
        int ubands[4] = {1, 1, 1, 1};
        int *usebands = nullptr;
        int bandcount = parent->nBands;
        GDALColorTableH hCT = nullptr;
        if (inbands != bandcount)
        {
            // Opaque if output expects alpha channel
            if (0 == bandcount % 2)
            {
                fill(buffer.begin(), buffer.end(), GByte(255));
                bandcount--;
            }
            if (3 == inbands)
            {
                // Lacking opacity, copy the first three bands
                ubands[1] = 2;
                ubands[2] = 3;
                usebands = ubands;
            }
            else if (1 == inbands)
            {
                // Grayscale, expecting color
                usebands = ubands;
                // Check for the color table of 1 band rasters
                hCT = GDALGetRasterColorTable(GDALGetRasterBand(inds, 1));
            }
        }
    
        auto errcode = CE_None;
        if (nullptr != hCT)
        {
            // Expand color indexed to RGB(A)
            errcode = GDALDatasetRasterIO(
                inds, GF_Read, 0, 0, TSZ, TSZ, buffer.data(), TSZ, TSZ, GDT_UInt8,
                1, usebands, parent->nBands, parent->nBands * TSZ, 1);
            if (CE_None == errcode)
            {
                GByte abyCT[4 * 256];
                GByte *pabyTileData = buffer.data();
                const int nEntries = std::min(256, GDALGetColorEntryCount(hCT));
                for (int i = 0; i < nEntries; i++)
                {
                    const GDALColorEntry *psEntry = GDALGetColorEntry(hCT, i);
                    abyCT[4 * i] = static_cast<GByte>(psEntry->c1);
                    abyCT[4 * i + 1] = static_cast<GByte>(psEntry->c2);
                    abyCT[4 * i + 2] = static_cast<GByte>(psEntry->c3);
                    abyCT[4 * i + 3] = static_cast<GByte>(psEntry->c4);
                }
                for (int i = nEntries; i < 256; i++)
                {
                    abyCT[4 * i] = 0;
                    abyCT[4 * i + 1] = 0;
                    abyCT[4 * i + 2] = 0;
                    abyCT[4 * i + 3] = 0;
                }
    
                if (parent->nBands == 4)
                {
                    for (size_t i = 0; i < nBytes; i++)
                    {
                        const GByte byVal = pabyTileData[4 * i];
                        pabyTileData[4 * i] = abyCT[4 * byVal];
                        pabyTileData[4 * i + 1] = abyCT[4 * byVal + 1];
                        pabyTileData[4 * i + 2] = abyCT[4 * byVal + 2];
                        pabyTileData[4 * i + 3] = abyCT[4 * byVal + 3];
                    }
                }
                else if (parent->nBands == 3)
                {
                    for (size_t i = 0; i < nBytes; i++)
                    {
                        const GByte byVal = pabyTileData[3 * i];
                        pabyTileData[3 * i] = abyCT[4 * byVal];
                        pabyTileData[3 * i + 1] = abyCT[4 * byVal + 1];
                        pabyTileData[3 * i + 2] = abyCT[4 * byVal + 2];
                    }
                }
                else
                {
                    // Assuming grayscale output
                    for (size_t i = 0; i < nBytes; i++)
                    {
                        const GByte byVal = pabyTileData[i];
                        pabyTileData[i] = abyCT[4 * byVal];
                    }
                }
            }
        }
        else
        {
            errcode = GDALDatasetRasterIO(
                inds, GF_Read, 0, 0, TSZ, TSZ, buffer.data(), TSZ, TSZ, GDT_UInt8,
                bandcount, usebands, parent->nBands, parent->nBands * TSZ, 1);
        }
        GDALClose(inds);
        VSIUnlink(magic.c_str());
        // Error while unpacking tile
        if (CE_None != errcode)
            return errcode;
    
        for (int iBand = 1; iBand <= parent->nBands; iBand++)
        {
            auto band = parent->GetRasterBand(iBand);
            if (lvl)
                band = band->GetOverview(lvl - 1);
            GDALRasterBlock *poBlock = nullptr;
            if (band != this)
            {
                poBlock = band->GetLockedBlockRef(nBlockXOff, nBlockYOff, 1);
                if (poBlock != nullptr)
                {
                    GDALCopyWords(buffer.data() + iBand - 1, GDT_UInt8,
                                  parent->nBands, poBlock->GetDataRef(), GDT_UInt8,
                                  1, TSZ * TSZ);
                    poBlock->DropLock();
                }
            }
            else
            {
                GDALCopyWords(buffer.data() + iBand - 1, GDT_UInt8, parent->nBands,
                              pData, GDT_UInt8, 1, TSZ * TSZ);
            }
        }
    
        return CE_None;
    }  // IReadBlock
    
    }  // namespace ESRIC
    
    void CPL_DLL GDALRegister_ESRIC()
    {
        if (GDALGetDriverByName("ESRIC") != nullptr)
            return;
    
        auto poDriver = new GDALDriver;
    
        poDriver->SetDescription("ESRIC");
        poDriver->SetMetadataItem(GDAL_DCAP_RASTER, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_VIRTUALIO, "YES");
        poDriver->SetMetadataItem(GDAL_DMD_LONGNAME, "Esri Compact Cache");
    
        poDriver->SetMetadataItem(GDAL_DMD_EXTENSIONS, "json tpkx");
    
        poDriver->SetMetadataItem(
            GDAL_DMD_OPENOPTIONLIST,
            "<OpenOptionList>"
            "  <Option name='EXTENT_SOURCE' type='string-select' "
            "description='Which source is used to determine the extent' "
            "default='FULL_EXTENT'>"
            "    <Value>FULL_EXTENT</Value>"
            "    <Value>INITIAL_EXTENT</Value>"
            "    <Value>TILING_SCHEME</Value>"
            "  </Option>"
            "  <Option name='IGNORE_OVERSIZED_LODS' type='boolean' "
            "description='Whether to silently ignore LODs that exceed the "
            "maximum size supported by GDAL (INT32_MAX)' "
            "default='NO'>"
            "  </Option>"
            "</OpenOptionList>");
        poDriver->pfnIdentify = ESRIC::Identify;
        poDriver->pfnOpen = ESRIC::ECDataset::Open;
        poDriver->pfnDelete = ESRIC::Delete;
    
        GetGDALDriverManager()->RegisterDriver(poDriver);
    }
    
    ```


## Drivers (gdal/frmts/mem)

??? example "mem/gdal_mem.h"

    <span class="badge badge-cpp">Drivers (gdal/frmts/mem)</span> **Caminho:** `gdal/frmts/mem/gdal_mem.h`

    ```cpp
    /******************************************************************************
     *
     * Project:  MEM GDAL Datasets
     * Purpose:  C/Public declarations of MEM GDAL dataset objects.
     * Author:   Kristin Cowalcijk <kristincowalcijk@gmail.com>
     *
     ******************************************************************************
     * Copyright (c) 2026, Kristin Cowalcijk <kristincowalcijk@gmail.com>
     *
     * SPDX-License-Identifier: MIT
     ****************************************************************************/
    
    #ifndef GDAL_MEM_H_INCLUDED
    #define GDAL_MEM_H_INCLUDED
    
    /**
     * \file gdal_mem.h
     *
     * Public (C callable) entry points for MEM GDAL dataset objects.
     */
    
    #include "cpl_port.h"
    #include "gdal.h"
    
    CPL_C_START
    
    GDALDatasetH CPL_DLL MEMCreate(int nXSize, int nYSize, int nBands,
                                   GDALDataType eType, CSLConstList papszOptions);
    
    CPL_C_END
    
    #endif /* GDAL_MEM_H_INCLUDED */
    
    ```


??? example "mem/memdataset.cpp"

    <span class="badge badge-cpp">Drivers (gdal/frmts/mem)</span> **Caminho:** `gdal/frmts/mem/memdataset.cpp`

    ```cpp
    /******************************************************************************
     *
     * Project:  Memory Array Translator
     * Purpose:  Complete implementation.
     * Author:   Frank Warmerdam, warmerdam@pobox.com
     *
     ******************************************************************************
     * Copyright (c) 2000, Frank Warmerdam
     * Copyright (c) 2008-2013, Even Rouault <even dot rouault at spatialys.com>
     *
     * SPDX-License-Identifier: MIT
     ****************************************************************************/
    
    #include "cpl_port.h"
    #include "memdataset.h"
    #include "memmultidim.h"
    
    #include <algorithm>
    #include <climits>
    #include <cstdlib>
    #include <cstring>
    #include <limits>
    #include <vector>
    
    #include "cpl_config.h"
    #include "cpl_conv.h"
    #include "cpl_error.h"
    #include "cpl_minixml.h"
    #include "cpl_progress.h"
    #include "cpl_string.h"
    #include "cpl_vsi.h"
    #include "gdal.h"
    #include "gdal_frmts.h"
    #include "gdal_mem.h"
    
    struct MEMDataset::Private
    {
        std::shared_ptr<GDALGroup> m_poRootGroup{};
        std::map<std::string, std::unique_ptr<GDALRelationship>>
            m_oMapRelationships{};
    };
    
    /************************************************************************/
    /*                             MEMCreate()                              */
    /************************************************************************/
    
    /**
     * Create a new in-memory raster dataset.
     *
     * @param nXSize Width of created raster in pixels.
     * @param nYSize Height of created raster in pixels.
     * @param nBands Number of bands.
     * @param eType Type of raster bands.
     * @param papszOptions MEM driver creation options.
     *
     * @return NULL on failure, or a new MEM dataset handle on success.
     */
    
    GDALDatasetH MEMCreate(int nXSize, int nYSize, int nBands, GDALDataType eType,
                           CSLConstList papszOptions)
    
    {
        return GDALDataset::ToHandle(
            MEMDataset::Create("", nXSize, nYSize, nBands, eType, papszOptions));
    }
    
    /************************************************************************/
    /*                        MEMCreateRasterBand()                         */
    /************************************************************************/
    
    GDALRasterBandH MEMCreateRasterBand(GDALDataset *poDS, int nBand,
                                        GByte *pabyData, GDALDataType eType,
                                        int nPixelOffset, int nLineOffset,
                                        int bAssumeOwnership)
    
    {
        return GDALRasterBand::ToHandle(
            new MEMRasterBand(poDS, nBand, pabyData, eType, nPixelOffset,
                              nLineOffset, bAssumeOwnership));
    }
    
    /************************************************************************/
    /*                       MEMCreateRasterBandEx()                        */
    /************************************************************************/
    
    GDALRasterBandH MEMCreateRasterBandEx(GDALDataset *poDS, int nBand,
                                          GByte *pabyData, GDALDataType eType,
                                          GSpacing nPixelOffset,
                                          GSpacing nLineOffset,
                                          int bAssumeOwnership)
    
    {
        return GDALRasterBand::ToHandle(
            new MEMRasterBand(poDS, nBand, pabyData, eType, nPixelOffset,
                              nLineOffset, bAssumeOwnership));
    }
    
    /************************************************************************/
    /*                           MEMRasterBand()                            */
    /************************************************************************/
    
    MEMRasterBand::MEMRasterBand(GByte *pabyDataIn, GDALDataType eTypeIn,
                                 int nXSizeIn, int nYSizeIn, bool bOwnDataIn)
        : GDALPamRasterBand(FALSE), pabyData(pabyDataIn),
          nPixelOffset(GDALGetDataTypeSizeBytes(eTypeIn)), nLineOffset(0),
          bOwnData(bOwnDataIn)
    {
        eAccess = GA_Update;
        eDataType = eTypeIn;
        nRasterXSize = nXSizeIn;
        nRasterYSize = nYSizeIn;
        nBlockXSize = nXSizeIn;
        nBlockYSize = 1;
        nLineOffset = nPixelOffset * static_cast<size_t>(nBlockXSize);
    
        PamInitializeNoParent();
    }
    
    /************************************************************************/
    /*                           MEMRasterBand()                            */
    /************************************************************************/
    
    MEMRasterBand::MEMRasterBand(GDALDataset *poDSIn, int nBandIn,
                                 GByte *pabyDataIn, GDALDataType eTypeIn,
                                 GSpacing nPixelOffsetIn, GSpacing nLineOffsetIn,
                                 int bAssumeOwnership, const char *pszPixelType)
        : GDALPamRasterBand(FALSE), pabyData(pabyDataIn),
          nPixelOffset(nPixelOffsetIn), nLineOffset(nLineOffsetIn),
          bOwnData(bAssumeOwnership)
    {
        poDS = poDSIn;
        nBand = nBandIn;
    
        eAccess = poDS->GetAccess();
    
        eDataType = eTypeIn;
    
        nBlockXSize = poDS->GetRasterXSize();
        nBlockYSize = 1;
    
        if (nPixelOffsetIn == 0)
            nPixelOffset = GDALGetDataTypeSizeBytes(eTypeIn);
    
        if (nLineOffsetIn == 0)
            nLineOffset = nPixelOffset * static_cast<size_t>(nBlockXSize);
    
        if (pszPixelType && EQUAL(pszPixelType, "SIGNEDBYTE"))
            SetMetadataItem("PIXELTYPE", "SIGNEDBYTE", "IMAGE_STRUCTURE");
    
        PamInitializeNoParent();
    }
    
    /************************************************************************/
    /*                           ~MEMRasterBand()                           */
    /************************************************************************/
    
    MEMRasterBand::~MEMRasterBand()
    
    {
        if (bOwnData)
        {
            VSIFree(pabyData);
        }
    }
    
    /************************************************************************/
    /*                             IReadBlock()                             */
    /************************************************************************/
    
    CPLErr MEMRasterBand::IReadBlock(CPL_UNUSED int nBlockXOff, int nBlockYOff,
                                     void *pImage)
    {
        CPLAssert(nBlockXOff == 0);
    
        const int nWordSize = GDALGetDataTypeSizeBytes(eDataType);
    
        if (nPixelOffset == nWordSize)
        {
            memcpy(pImage, pabyData + nLineOffset * static_cast<size_t>(nBlockYOff),
                   static_cast<size_t>(nPixelOffset) * nBlockXSize);
        }
        else
        {
            GByte *const pabyCur =
                pabyData + nLineOffset * static_cast<size_t>(nBlockYOff);
    
            for (int iPixel = 0; iPixel < nBlockXSize; iPixel++)
            {
                memcpy(static_cast<GByte *>(pImage) + iPixel * nWordSize,
                       pabyCur + iPixel * nPixelOffset, nWordSize);
            }
        }
    
        return CE_None;
    }
    
    /************************************************************************/
    /*                            IWriteBlock()                             */
    /************************************************************************/
    
    CPLErr MEMRasterBand::IWriteBlock(CPL_UNUSED int nBlockXOff, int nBlockYOff,
                                      void *pImage)
    {
        CPLAssert(nBlockXOff == 0);
        const int nWordSize = GDALGetDataTypeSizeBytes(eDataType);
    
        if (nPixelOffset == nWordSize)
        {
            memcpy(pabyData + nLineOffset * static_cast<size_t>(nBlockYOff), pImage,
                   static_cast<size_t>(nPixelOffset) * nBlockXSize);
        }
        else
        {
            GByte *pabyCur =
                pabyData + nLineOffset * static_cast<size_t>(nBlockYOff);
    
            for (int iPixel = 0; iPixel < nBlockXSize; iPixel++)
            {
                memcpy(pabyCur + iPixel * nPixelOffset,
                       static_cast<GByte *>(pImage) + iPixel * nWordSize,
                       nWordSize);
            }
        }
    
        return CE_None;
    }
    
    /************************************************************************/
    /*                             IRasterIO()                              */
    /************************************************************************/
    
    CPLErr MEMRasterBand::IRasterIO(GDALRWFlag eRWFlag, int nXOff, int nYOff,
                                    int nXSize, int nYSize, void *pData,
                                    int nBufXSize, int nBufYSize,
                                    GDALDataType eBufType, GSpacing nPixelSpaceBuf,
                                    GSpacing nLineSpaceBuf,
                                    GDALRasterIOExtraArg *psExtraArg)
    {
        if (nXSize != nBufXSize || nYSize != nBufYSize)
        {
            return GDALRasterBand::IRasterIO(eRWFlag, nXOff, nYOff, nXSize, nYSize,
                                             pData, nBufXSize, nBufYSize, eBufType,
                                             static_cast<int>(nPixelSpaceBuf),
                                             nLineSpaceBuf, psExtraArg);
        }
    
        // In case block based I/O has been done before.
        FlushCache(false);
    
        if (eRWFlag == GF_Read)
        {
            for (int iLine = 0; iLine < nYSize; iLine++)
            {
                GDALCopyWords64(pabyData +
                                    nLineOffset *
                                        static_cast<GPtrDiff_t>(iLine + nYOff) +
                                    nXOff * nPixelOffset,
                                eDataType, static_cast<int>(nPixelOffset),
                                static_cast<GByte *>(pData) +
                                    nLineSpaceBuf * static_cast<GPtrDiff_t>(iLine),
                                eBufType, static_cast<int>(nPixelSpaceBuf), nXSize);
            }
        }
        else
        {
            if (nXSize == nRasterXSize && nPixelSpaceBuf == nPixelOffset &&
                nLineSpaceBuf == nLineOffset)
            {
                GDALCopyWords64(pData, eBufType, static_cast<int>(nPixelSpaceBuf),
                                pabyData +
                                    nLineOffset * static_cast<GPtrDiff_t>(nYOff),
                                eDataType, static_cast<int>(nPixelOffset),
                                static_cast<GPtrDiff_t>(nXSize) * nYSize);
            }
            else
            {
                for (int iLine = 0; iLine < nYSize; iLine++)
                {
                    GDALCopyWords64(
                        static_cast<GByte *>(pData) +
                            nLineSpaceBuf * static_cast<GPtrDiff_t>(iLine),
                        eBufType, static_cast<int>(nPixelSpaceBuf),
                        pabyData +
                            nLineOffset * static_cast<GPtrDiff_t>(iLine + nYOff) +
                            nXOff * nPixelOffset,
                        eDataType, static_cast<int>(nPixelOffset), nXSize);
                }
            }
        }
        return CE_None;
    }
    
    /************************************************************************/
    /*                             IRasterIO()                              */
    /************************************************************************/
    
    CPLErr MEMDataset::IRasterIO(GDALRWFlag eRWFlag, int nXOff, int nYOff,
                                 int nXSize, int nYSize, void *pData, int nBufXSize,
                                 int nBufYSize, GDALDataType eBufType,
                                 int nBandCount, BANDMAP_TYPE panBandMap,
                                 GSpacing nPixelSpaceBuf, GSpacing nLineSpaceBuf,
                                 GSpacing nBandSpaceBuf,
                                 GDALRasterIOExtraArg *psExtraArg)
    {
        const int eBufTypeSize = GDALGetDataTypeSizeBytes(eBufType);
    
        const auto IsPixelInterleaveDataset = [this, nBandCount, panBandMap]()
        {
            GDALDataType eDT = GDT_Unknown;
            GByte *pabyData = nullptr;
            GSpacing nPixelOffset = 0;
            GSpacing nLineOffset = 0;
            int eDTSize = 0;
            for (int iBandIndex = 0; iBandIndex < nBandCount; iBandIndex++)
            {
                if (panBandMap[iBandIndex] != iBandIndex + 1)
                    return false;
    
                MEMRasterBand *poBand =
                    cpl::down_cast<MEMRasterBand *>(GetRasterBand(iBandIndex + 1));
                if (iBandIndex == 0)
                {
                    eDT = poBand->GetRasterDataType();
                    pabyData = poBand->pabyData;
                    nPixelOffset = poBand->nPixelOffset;
                    nLineOffset = poBand->nLineOffset;
                    eDTSize = GDALGetDataTypeSizeBytes(eDT);
                    if (nPixelOffset != static_cast<GSpacing>(nBands) * eDTSize)
                        return false;
                }
                else if (poBand->GetRasterDataType() != eDT ||
                         nPixelOffset != poBand->nPixelOffset ||
                         nLineOffset != poBand->nLineOffset ||
                         poBand->pabyData != pabyData + iBandIndex * eDTSize)
                {
                    return false;
                }
            }
            return true;
        };
    
        // Detect if we have a pixel-interleaved buffer
        if (nXSize == nBufXSize && nYSize == nBufYSize && nBandCount == nBands &&
            nBands > 1 && nBandSpaceBuf == eBufTypeSize &&
            nPixelSpaceBuf == nBandSpaceBuf * nBands)
        {
            const auto IsBandSeparatedDataset = [this, nBandCount, panBandMap]()
            {
                GDALDataType eDT = GDT_Unknown;
                GSpacing nPixelOffset = 0;
                GSpacing nLineOffset = 0;
                int eDTSize = 0;
                for (int iBandIndex = 0; iBandIndex < nBandCount; iBandIndex++)
                {
                    if (panBandMap[iBandIndex] != iBandIndex + 1)
                        return false;
    
                    MEMRasterBand *poBand = cpl::down_cast<MEMRasterBand *>(
                        GetRasterBand(iBandIndex + 1));
                    if (iBandIndex == 0)
                    {
                        eDT = poBand->GetRasterDataType();
                        nPixelOffset = poBand->nPixelOffset;
                        nLineOffset = poBand->nLineOffset;
                        eDTSize = GDALGetDataTypeSizeBytes(eDT);
                        if (nPixelOffset != eDTSize)
                            return false;
                    }
                    else if (poBand->GetRasterDataType() != eDT ||
                             nPixelOffset != poBand->nPixelOffset ||
                             nLineOffset != poBand->nLineOffset)
                    {
                        return false;
                    }
                }
                return true;
            };
    
            if (IsPixelInterleaveDataset())
            {
                FlushCache(false);
                const auto poFirstBand =
                    cpl::down_cast<MEMRasterBand *>(papoBands[0]);
                const GDALDataType eDT = poFirstBand->GetRasterDataType();
                GByte *pabyData = poFirstBand->pabyData;
                const GSpacing nPixelOffset = poFirstBand->nPixelOffset;
                const GSpacing nLineOffset = poFirstBand->nLineOffset;
                const int eDTSize = GDALGetDataTypeSizeBytes(eDT);
                if (eRWFlag == GF_Read)
                {
                    for (int iLine = 0; iLine < nYSize; iLine++)
                    {
                        GDALCopyWords(
                            pabyData +
                                nLineOffset * static_cast<size_t>(iLine + nYOff) +
                                nXOff * nPixelOffset,
                            eDT, eDTSize,
                            static_cast<GByte *>(pData) +
                                nLineSpaceBuf * static_cast<size_t>(iLine),
                            eBufType, eBufTypeSize, nXSize * nBands);
                    }
                }
                else
                {
                    for (int iLine = 0; iLine < nYSize; iLine++)
                    {
                        GDALCopyWords(
                            static_cast<GByte *>(pData) +
                                nLineSpaceBuf * static_cast<size_t>(iLine),
                            eBufType, eBufTypeSize,
                            pabyData +
                                nLineOffset * static_cast<size_t>(iLine + nYOff) +
                                nXOff * nPixelOffset,
                            eDT, eDTSize, nXSize * nBands);
                    }
                }
                return CE_None;
            }
            else if (eRWFlag == GF_Write && nBandCount <= 4 &&
                     IsBandSeparatedDataset())
            {
                // TODO: once we have a GDALInterleave() function, implement the
                // GF_Read case
                FlushCache(false);
                const auto poFirstBand =
                    cpl::down_cast<MEMRasterBand *>(papoBands[0]);
                const GDALDataType eDT = poFirstBand->GetRasterDataType();
                void *ppDestBuffer[4] = {nullptr, nullptr, nullptr, nullptr};
                if (nXOff == 0 && nXSize == nRasterXSize &&
                    poFirstBand->nLineOffset ==
                        poFirstBand->nPixelOffset * nXSize &&
                    nLineSpaceBuf == nPixelSpaceBuf * nXSize)
                {
                    // Optimization of the general case in the below else() clause:
                    // writing whole strips from a fully packed buffer
                    for (int i = 0; i < nBandCount; ++i)
                    {
                        const auto poBand =
                            cpl::down_cast<MEMRasterBand *>(papoBands[i]);
                        ppDestBuffer[i] =
                            poBand->pabyData + poBand->nLineOffset * nYOff;
                    }
                    GDALDeinterleave(pData, eBufType, nBandCount, ppDestBuffer, eDT,
                                     static_cast<size_t>(nXSize) * nYSize);
                }
                else
                {
                    for (int iLine = 0; iLine < nYSize; iLine++)
                    {
                        for (int i = 0; i < nBandCount; ++i)
                        {
                            const auto poBand =
                                cpl::down_cast<MEMRasterBand *>(papoBands[i]);
                            ppDestBuffer[i] = poBand->pabyData +
                                              poBand->nPixelOffset * nXOff +
                                              poBand->nLineOffset * (iLine + nYOff);
                        }
                        GDALDeinterleave(
                            static_cast<GByte *>(pData) +
                                nLineSpaceBuf * static_cast<size_t>(iLine),
                            eBufType, nBandCount, ppDestBuffer, eDT, nXSize);
                    }
                }
                return CE_None;
            }
        }
        // From a band-interleaved buffer to a pixel-interleaved dataset
        else if (eRWFlag == GF_Write && nXSize == nBufXSize &&
                 nYSize == nBufYSize && nXSize == nRasterXSize &&
                 nBandCount == nBands && nBands > 1 &&
                 nPixelSpaceBuf == eBufTypeSize &&
                 nLineSpaceBuf == nPixelSpaceBuf * nBufXSize &&
                 nBandSpaceBuf == nLineSpaceBuf * nBufYSize &&
                 IsPixelInterleaveDataset())
        {
            FlushCache(false);
    
            auto poDstBand = cpl::down_cast<MEMRasterBand *>(papoBands[0]);
            GDALTranspose2D(pData, eBufType,
                            poDstBand->pabyData + nYOff * poDstBand->nLineOffset,
                            poDstBand->GetRasterDataType(),
                            static_cast<size_t>(nXSize) * nYSize, nBands);
            return CE_None;
        }
    
        if (nBufXSize != nXSize || nBufYSize != nYSize)
            return GDALDataset::IRasterIO(eRWFlag, nXOff, nYOff, nXSize, nYSize,
                                          pData, nBufXSize, nBufYSize, eBufType,
                                          nBandCount, panBandMap, nPixelSpaceBuf,
                                          nLineSpaceBuf, nBandSpaceBuf, psExtraArg);
    
        return GDALDataset::BandBasedRasterIO(
            eRWFlag, nXOff, nYOff, nXSize, nYSize, pData, nBufXSize, nBufYSize,
            eBufType, nBandCount, panBandMap, nPixelSpaceBuf, nLineSpaceBuf,
            nBandSpaceBuf, psExtraArg);
    }
    
    /************************************************************************/
    /*                          GetOverviewCount()                          */
    /************************************************************************/
    
    int MEMRasterBand::GetOverviewCount()
    {
        MEMDataset *poMemDS = dynamic_cast<MEMDataset *>(poDS);
        if (poMemDS == nullptr)
            return 0;
        return static_cast<int>(poMemDS->m_apoOverviewDS.size());
    }
    
    /************************************************************************/
    /*                            GetOverview()                             */
    /************************************************************************/
    
    GDALRasterBand *MEMRasterBand::GetOverview(int i)
    
    {
        MEMDataset *poMemDS = dynamic_cast<MEMDataset *>(poDS);
        if (poMemDS == nullptr)
            return nullptr;
        if (i < 0 || i >= static_cast<int>(poMemDS->m_apoOverviewDS.size()))
            return nullptr;
        return poMemDS->m_apoOverviewDS[i]->GetRasterBand(nBand);
    }
    
    /************************************************************************/
    /*                           CreateMaskBand()                           */
    /************************************************************************/
    
    CPLErr MEMRasterBand::CreateMaskBand(int nFlagsIn)
    {
        InvalidateMaskBand();
    
        MEMDataset *poMemDS = dynamic_cast<MEMDataset *>(poDS);
        if ((nFlagsIn & GMF_PER_DATASET) != 0 && nBand != 1 && poMemDS != nullptr)
        {
            MEMRasterBand *poFirstBand =
                dynamic_cast<MEMRasterBand *>(poMemDS->GetRasterBand(1));
            if (poFirstBand != nullptr)
                return poFirstBand->CreateMaskBand(nFlagsIn);
        }
    
        GByte *pabyMaskData =
            static_cast<GByte *>(VSI_CALLOC_VERBOSE(nRasterXSize, nRasterYSize));
        if (pabyMaskData == nullptr)
            return CE_Failure;
    
        nMaskFlags = nFlagsIn;
        auto poMemMaskBand = std::unique_ptr<MEMRasterBand>(
            new MEMRasterBand(pabyMaskData, GDT_UInt8, nRasterXSize, nRasterYSize,
                              /* bOwnData= */ true));
        poMemMaskBand->m_bIsMask = true;
        poMask.reset(std::move(poMemMaskBand));
        if ((nFlagsIn & GMF_PER_DATASET) != 0 && nBand == 1 && poMemDS != nullptr)
        {
            for (int i = 2; i <= poMemDS->GetRasterCount(); ++i)
            {
                MEMRasterBand *poOtherBand =
                    cpl::down_cast<MEMRasterBand *>(poMemDS->GetRasterBand(i));
                poOtherBand->InvalidateMaskBand();
                poOtherBand->nMaskFlags = nFlagsIn;
                poOtherBand->poMask.resetNotOwned(poMask.get());
            }
        }
        return CE_None;
    }
    
    /************************************************************************/
    /*                             IsMaskBand()                             */
    /************************************************************************/
    
    bool MEMRasterBand::IsMaskBand() const
    {
        return m_bIsMask || GDALPamRasterBand::IsMaskBand();
    }
    
    /************************************************************************/
    /* ==================================================================== */
    /*      MEMDataset                                                     */
    /* ==================================================================== */
    /************************************************************************/
    
    /************************************************************************/
    /*                             MEMDataset()                             */
    /************************************************************************/
    
    MEMDataset::MEMDataset()
        : GDALDataset(FALSE), bGeoTransformSet(FALSE), m_poPrivate(new Private())
    {
        m_gt.yscale = -1;
        DisableReadWriteMutex();
    }
    
    /************************************************************************/
    /*                            ~MEMDataset()                             */
    /************************************************************************/
    
    MEMDataset::~MEMDataset()
    
    {
        MEMDataset::Close();
    }
    
    /************************************************************************/
    /*                               Close()                                */
    /************************************************************************/
    
    CPLErr MEMDataset::Close(GDALProgressFunc, void *)
    {
        CPLErr eErr = CE_None;
        if (nOpenFlags != OPEN_FLAGS_CLOSED)
        {
            const bool bSuppressOnCloseBackup = bSuppressOnClose;
            bSuppressOnClose = true;
            FlushCache(true);
            for (int i = 0; i < nBands; ++i)
            {
                auto poMEMBand = dynamic_cast<MEMRasterBand *>(papoBands[i]);
                if (poMEMBand && poMEMBand->poMask)
                    poMEMBand->poMask.get()->FlushCache(true);
            }
            bSuppressOnClose = bSuppressOnCloseBackup;
            m_apoOverviewDS.clear();
            eErr = GDALDataset::Close();
        }
    
        return eErr;
    }
    
    #if 0
    /************************************************************************/
    /*                           EnterReadWrite()                           */
    /************************************************************************/
    
    int MEMDataset::EnterReadWrite(CPL_UNUSED GDALRWFlag eRWFlag)
    {
        return TRUE;
    }
    
    /************************************************************************/
    /*                           LeaveReadWrite()                           */
    /************************************************************************/
    
    void MEMDataset::LeaveReadWrite()
    {
    }
    #endif  // if 0
    
    /************************************************************************/
    /*                           GetSpatialRef()                            */
    /************************************************************************/
    
    const OGRSpatialReference *MEMDataset::GetSpatialRef() const
    
    {
        if (GetLayerCount())
            return GDALDataset::GetSpatialRef();
        return GetSpatialRefRasterOnly();
    }
    
    /************************************************************************/
    /*                      GetSpatialRefRasterOnly()                       */
    /************************************************************************/
    
    const OGRSpatialReference *MEMDataset::GetSpatialRefRasterOnly() const
    
    {
        return m_oSRS.IsEmpty() ? nullptr : &m_oSRS;
    }
    
    /************************************************************************/
    /*                           SetSpatialRef()                            */
    /************************************************************************/
    
    CPLErr MEMDataset::SetSpatialRef(const OGRSpatialReference *poSRS)
    
    {
        m_oSRS.Clear();
        if (poSRS)
            m_oSRS = *poSRS;
    
        return CE_None;
    }
    
    /************************************************************************/
    /*                          GetGeoTransform()                           */
    /************************************************************************/
    
    CPLErr MEMDataset::GetGeoTransform(GDALGeoTransform &gt) const
    
    {
        gt = m_gt;
        if (bGeoTransformSet)
            return CE_None;
    
        return CE_Failure;
    }
    
    /************************************************************************/
    /*                          SetGeoTransform()                           */
    /************************************************************************/
    
    CPLErr MEMDataset::SetGeoTransform(const GDALGeoTransform &gt)
    
    {
        m_gt = gt;
        bGeoTransformSet = TRUE;
    
        return CE_None;
    }
    
    /************************************************************************/
    /*                         GetInternalHandle()                          */
    /************************************************************************/
    
    void *MEMDataset::GetInternalHandle(const char *pszRequest)
    
    {
        // check for MEMORYnnn string in pszRequest (nnnn can be up to 10
        // digits, or even omitted)
        if (STARTS_WITH_CI(pszRequest, "MEMORY"))
        {
            if (int BandNumber = static_cast<int>(CPLScanLong(&pszRequest[6], 10)))
            {
                MEMRasterBand *RequestedRasterBand =
                    cpl::down_cast<MEMRasterBand *>(GetRasterBand(BandNumber));
    
                // we're within a MEMDataset so the only thing a RasterBand
                // could be is a MEMRasterBand
    
                if (RequestedRasterBand != nullptr)
                {
                    // return the internal band data pointer
                    return RequestedRasterBand->GetData();
                }
            }
        }
    
        return nullptr;
    }
    
    /************************************************************************/
    /*                            GetGCPCount()                             */
    /************************************************************************/
    
    int MEMDataset::GetGCPCount()
    
    {
        return static_cast<int>(m_aoGCPs.size());
    }
    
    /************************************************************************/
    /*                          GetGCPSpatialRef()                          */
    /************************************************************************/
    
    const OGRSpatialReference *MEMDataset::GetGCPSpatialRef() const
    
    {
        return m_oGCPSRS.IsEmpty() ? nullptr : &m_oGCPSRS;
    }
    
    /************************************************************************/
    /*                              GetGCPs()                               */
    /************************************************************************/
    
    const GDAL_GCP *MEMDataset::GetGCPs()
    
    {
        return gdal::GCP::c_ptr(m_aoGCPs);
    }
    
    /************************************************************************/
    /*                              SetGCPs()                               */
    /************************************************************************/
    
    CPLErr MEMDataset::SetGCPs(int nNewCount, const GDAL_GCP *pasNewGCPList,
                               const OGRSpatialReference *poSRS)
    
    {
        m_oGCPSRS.Clear();
        if (poSRS)
            m_oGCPSRS = *poSRS;
    
        m_aoGCPs = gdal::GCP::fromC(pasNewGCPList, nNewCount);
    
        return CE_None;
    }
    
    /************************************************************************/
    /*                              AddBand()                               */
    /*                                                                      */
    /*      Add a new band to the dataset, allowing creation options to     */
    /*      specify the existing memory to use, otherwise create new        */
    /*      memory.                                                         */
    /************************************************************************/
    
    CPLErr MEMDataset::AddBand(GDALDataType eType, CSLConstList papszOptions)
    
    {
        const int nBandId = GetRasterCount() + 1;
        const GSpacing nPixelSize = GDALGetDataTypeSizeBytes(eType);
        if (nPixelSize == 0)
        {
            ReportError(CE_Failure, CPLE_IllegalArg,
                        "Illegal GDT_Unknown/GDT_TypeCount argument");
            return CE_Failure;
        }
    
        /* -------------------------------------------------------------------- */
        /*      Do we need to allocate the memory ourselves?  This is the       */
        /*      simple case.                                                    */
        /* -------------------------------------------------------------------- */
        const CPLStringList aosOptions(papszOptions);
        if (aosOptions.FetchNameValue("DATAPOINTER") == nullptr)
        {
            const GSpacing nTmp = nPixelSize * GetRasterXSize();
            GByte *pData =
    #if SIZEOF_VOIDP == 4
                (nTmp > INT_MAX) ? nullptr :
    #endif
                                 static_cast<GByte *>(VSI_CALLOC_VERBOSE(
                                     static_cast<size_t>(nTmp), GetRasterYSize()));
    
            if (pData == nullptr)
            {
                return CE_Failure;
            }
    
            SetBand(nBandId,
                    new MEMRasterBand(this, nBandId, pData, eType, nPixelSize,
                                      nPixelSize * GetRasterXSize(), TRUE));
    
            return CE_None;
        }
    
        /* -------------------------------------------------------------------- */
        /*      Get layout of memory and other flags.                           */
        /* -------------------------------------------------------------------- */
        const char *pszDataPointer = aosOptions.FetchNameValue("DATAPOINTER");
        GByte *pData = static_cast<GByte *>(CPLScanPointer(
            pszDataPointer, static_cast<int>(strlen(pszDataPointer))));
    
        const char *pszOption = aosOptions.FetchNameValue("PIXELOFFSET");
        GSpacing nPixelOffset;
        if (pszOption == nullptr)
            nPixelOffset = nPixelSize;
        else
            nPixelOffset = CPLAtoGIntBig(pszOption);
    
        pszOption = aosOptions.FetchNameValue("LINEOFFSET");
        GSpacing nLineOffset;
        if (pszOption == nullptr)
            nLineOffset = GetRasterXSize() * static_cast<size_t>(nPixelOffset);
        else
            nLineOffset = CPLAtoGIntBig(pszOption);
    
        SetBand(nBandId, new MEMRasterBand(this, nBandId, pData, eType,
                                           nPixelOffset, nLineOffset, FALSE));
    
        return CE_None;
    }
    
    /************************************************************************/
    /*                             AddMEMBand()                             */
    /************************************************************************/
    
    void MEMDataset::AddMEMBand(GDALRasterBandH hMEMBand)
    {
        auto poBand = GDALRasterBand::FromHandle(hMEMBand);
        CPLAssert(dynamic_cast<MEMRasterBand *>(poBand) != nullptr);
        SetBand(1 + nBands, poBand);
    }
    
    /************************************************************************/
    /*                          IBuildOverviews()                           */
    /************************************************************************/
    
    CPLErr MEMDataset::IBuildOverviews(const char *pszResampling, int nOverviews,
                                       const int *panOverviewList, int nListBands,
                                       const int *panBandList,
                                       GDALProgressFunc pfnProgress,
                                       void *pProgressData,
                                       CSLConstList papszOptions)
    {
        if (nBands == 0)
        {
            CPLError(CE_Failure, CPLE_NotSupported, "Dataset has zero bands.");
            return CE_Failure;
        }
    
        if (nListBands != nBands)
        {
            CPLError(CE_Failure, CPLE_NotSupported,
                     "Generation of overviews in MEM only"
                     "supported when operating on all bands.");
            return CE_Failure;
        }
    
        if (nOverviews == 0)
        {
            // Cleanup existing overviews
            m_apoOverviewDS.clear();
            return CE_None;
        }
    
        /* -------------------------------------------------------------------- */
        /*      Force cascading. Help to get accurate results when masks are    */
        /*      involved.                                                       */
        /* -------------------------------------------------------------------- */
        if (nOverviews > 1 &&
            (STARTS_WITH_CI(pszResampling, "AVER") ||
             STARTS_WITH_CI(pszResampling, "GAUSS") ||
             EQUAL(pszResampling, "CUBIC") || EQUAL(pszResampling, "CUBICSPLINE") ||
             EQUAL(pszResampling, "LANCZOS") || EQUAL(pszResampling, "BILINEAR")))
        {
            double dfTotalPixels = 0;
            for (int i = 0; i < nOverviews; i++)
            {
                dfTotalPixels += static_cast<double>(nRasterXSize) * nRasterYSize /
                                 (panOverviewList[i] * panOverviewList[i]);
            }
    
            double dfAccPixels = 0;
            for (int i = 0; i < nOverviews; i++)
            {
                double dfPixels = static_cast<double>(nRasterXSize) * nRasterYSize /
                                  (panOverviewList[i] * panOverviewList[i]);
                void *pScaledProgress = GDALCreateScaledProgress(
                    dfAccPixels / dfTotalPixels,
                    (dfAccPixels + dfPixels) / dfTotalPixels, pfnProgress,
                    pProgressData);
                CPLErr eErr = IBuildOverviews(
                    pszResampling, 1, &panOverviewList[i], nListBands, panBandList,
                    GDALScaledProgress, pScaledProgress, papszOptions);
                GDALDestroyScaledProgress(pScaledProgress);
                dfAccPixels += dfPixels;
                if (eErr == CE_Failure)
                    return eErr;
            }
            return CE_None;
        }
    
        /* -------------------------------------------------------------------- */
        /*      Establish which of the overview levels we already have, and     */
        /*      which are new.                                                  */
        /* -------------------------------------------------------------------- */
        GDALRasterBand *poBand = GetRasterBand(1);
    
        for (int i = 0; i < nOverviews; i++)
        {
            bool bExisting = false;
            for (int j = 0; j < poBand->GetOverviewCount(); j++)
            {
                GDALRasterBand *poOverview = poBand->GetOverview(j);
                if (poOverview == nullptr)
                    continue;
    
                int nOvFactor =
                    GDALComputeOvFactor(poOverview->GetXSize(), poBand->GetXSize(),
                                        poOverview->GetYSize(), poBand->GetYSize());
    
                if (nOvFactor == panOverviewList[i] ||
                    nOvFactor == GDALOvLevelAdjust2(panOverviewList[i],
                                                    poBand->GetXSize(),
                                                    poBand->GetYSize()))
                {
                    bExisting = true;
                    break;
                }
            }
    
            // Create new overview dataset if needed.
            if (!bExisting)
            {
                auto poOvrDS = std::make_unique<MEMDataset>();
                poOvrDS->eAccess = GA_Update;
                poOvrDS->nRasterXSize =
                    DIV_ROUND_UP(nRasterXSize, panOverviewList[i]);
                poOvrDS->nRasterYSize =
                    DIV_ROUND_UP(nRasterYSize, panOverviewList[i]);
                poOvrDS->bGeoTransformSet = bGeoTransformSet;
                poOvrDS->m_gt = m_gt;
                const double dfOvrXRatio =
                    static_cast<double>(nRasterXSize) / poOvrDS->nRasterXSize;
                const double dfOvrYRatio =
                    static_cast<double>(nRasterYSize) / poOvrDS->nRasterYSize;
                poOvrDS->m_gt.Rescale(dfOvrXRatio, dfOvrYRatio);
                poOvrDS->m_oSRS = m_oSRS;
                for (int iBand = 0; iBand < nBands; iBand++)
                {
                    const GDALDataType eDT =
                        GetRasterBand(iBand + 1)->GetRasterDataType();
                    if (poOvrDS->AddBand(eDT, nullptr) != CE_None)
                    {
                        return CE_Failure;
                    }
                }
                m_apoOverviewDS.emplace_back(poOvrDS.release());
            }
        }
    
        /* -------------------------------------------------------------------- */
        /*      Build band list.                                                */
        /* -------------------------------------------------------------------- */
        GDALRasterBand **pahBands = static_cast<GDALRasterBand **>(
            CPLCalloc(sizeof(GDALRasterBand *), nBands));
        for (int i = 0; i < nBands; i++)
            pahBands[i] = GetRasterBand(panBandList[i]);
    
        /* -------------------------------------------------------------------- */
        /*      Refresh overviews that were listed.                             */
        /* -------------------------------------------------------------------- */
        GDALRasterBand **papoOverviewBands =
            static_cast<GDALRasterBand **>(CPLCalloc(sizeof(void *), nOverviews));
        GDALRasterBand **papoMaskOverviewBands =
            static_cast<GDALRasterBand **>(CPLCalloc(sizeof(void *), nOverviews));
    
        CPLErr eErr = CE_None;
        for (int iBand = 0; iBand < nBands && eErr == CE_None; iBand++)
        {
            poBand = GetRasterBand(panBandList[iBand]);
    
            int nNewOverviews = 0;
            for (int i = 0; i < nOverviews; i++)
            {
                for (int j = 0; j < poBand->GetOverviewCount(); j++)
                {
                    GDALRasterBand *poOverview = poBand->GetOverview(j);
    
                    int bHasNoData = FALSE;
                    double noDataValue = poBand->GetNoDataValue(&bHasNoData);
    
                    if (bHasNoData)
                        poOverview->SetNoDataValue(noDataValue);
    
                    const int nOvFactor = GDALComputeOvFactor(
                        poOverview->GetXSize(), poBand->GetXSize(),
                        poOverview->GetYSize(), poBand->GetYSize());
    
                    if (nOvFactor == panOverviewList[i] ||
                        nOvFactor == GDALOvLevelAdjust2(panOverviewList[i],
                                                        poBand->GetXSize(),
                                                        poBand->GetYSize()))
                    {
                        papoOverviewBands[nNewOverviews++] = poOverview;
                        break;
                    }
                }
            }
    
            // If the band has an explicit mask, we need to create overviews
            // for it
            MEMRasterBand *poMEMBand = cpl::down_cast<MEMRasterBand *>(poBand);
            const bool bMustGenerateMaskOvr =
                ((poMEMBand->poMask != nullptr && poMEMBand->poMask.IsOwned()) ||
                 // Or if it is a per-dataset mask, in which case just do it for the
                 // first band
                 ((poMEMBand->nMaskFlags & GMF_PER_DATASET) != 0 && iBand == 0)) &&
                dynamic_cast<MEMRasterBand *>(poBand->GetMaskBand()) != nullptr;
    
            if (nNewOverviews > 0 && bMustGenerateMaskOvr)
            {
                for (int i = 0; i < nNewOverviews; i++)
                {
                    MEMRasterBand *poMEMOvrBand =
                        cpl::down_cast<MEMRasterBand *>(papoOverviewBands[i]);
                    if (!(poMEMOvrBand->poMask != nullptr &&
                          poMEMOvrBand->poMask.IsOwned()) &&
                        (poMEMOvrBand->nMaskFlags & GMF_PER_DATASET) == 0)
                    {
                        poMEMOvrBand->CreateMaskBand(poMEMBand->nMaskFlags);
                    }
                    papoMaskOverviewBands[i] = poMEMOvrBand->GetMaskBand();
                }
    
                void *pScaledProgress = GDALCreateScaledProgress(
                    1.0 * iBand / nBands, 1.0 * (iBand + 0.5) / nBands, pfnProgress,
                    pProgressData);
    
                MEMRasterBand *poMaskBand =
                    cpl::down_cast<MEMRasterBand *>(poBand->GetMaskBand());
                // Make the mask band to be its own mask, similarly to what is
                // done for alpha bands in GDALRegenerateOverviews() (#5640)
                poMaskBand->InvalidateMaskBand();
                poMaskBand->poMask.resetNotOwned(poMaskBand);
                poMaskBand->nMaskFlags = 0;
                eErr = GDALRegenerateOverviewsEx(
                    GDALRasterBand::ToHandle(poMaskBand), nNewOverviews,
                    reinterpret_cast<GDALRasterBandH *>(papoMaskOverviewBands),
                    pszResampling, GDALScaledProgress, pScaledProgress,
                    papszOptions);
                poMaskBand->InvalidateMaskBand();
                GDALDestroyScaledProgress(pScaledProgress);
            }
    
            // Generate overview of bands *AFTER* mask overviews
            if (nNewOverviews > 0 && eErr == CE_None)
            {
                void *pScaledProgress = GDALCreateScaledProgress(
                    1.0 * (iBand + (bMustGenerateMaskOvr ? 0.5 : 1)) / nBands,
                    1.0 * (iBand + 1) / nBands, pfnProgress, pProgressData);
                eErr = GDALRegenerateOverviewsEx(
                    GDALRasterBand::ToHandle(poBand), nNewOverviews,
                    reinterpret_cast<GDALRasterBandH *>(papoOverviewBands),
                    pszResampling, GDALScaledProgress, pScaledProgress,
                    papszOptions);
                GDALDestroyScaledProgress(pScaledProgress);
            }
        }
    
        /* -------------------------------------------------------------------- */
        /*      Cleanup                                                         */
        /* -------------------------------------------------------------------- */
        CPLFree(papoOverviewBands);
        CPLFree(papoMaskOverviewBands);
        CPLFree(pahBands);
    
        return eErr;
    }
    
    /************************************************************************/
    /*                           CreateMaskBand()                           */
    /************************************************************************/
    
    CPLErr MEMDataset::CreateMaskBand(int nFlagsIn)
    {
        GDALRasterBand *poFirstBand = GetRasterBand(1);
        if (poFirstBand == nullptr)
            return CE_Failure;
        return poFirstBand->CreateMaskBand(nFlagsIn | GMF_PER_DATASET);
    }
    
    /************************************************************************/
    /*                            CanBeCloned()                             */
    /************************************************************************/
    
    /** Implements GDALDataset::CanBeCloned()
     *
     * This method is called by GDALThreadSafeDataset::Create() to determine if
     * it is possible to create a thread-safe wrapper for a dataset, which involves
     * the ability to Clone() it.
     *
     * The implementation of this method must be thread-safe.
     */
    bool MEMDataset::CanBeCloned(int nScopeFlags, bool bCanShareState) const
    {
        return nScopeFlags == GDAL_OF_RASTER && bCanShareState &&
               typeid(this) == typeid(const MEMDataset *);
    }
    
    /************************************************************************/
    /*                               Clone()                                */
    /************************************************************************/
    
    /** Implements GDALDataset::Clone()
     *
     * This method returns a new instance, identical to "this", but which shares the
     * same memory buffer as "this".
     *
     * The implementation of this method must be thread-safe.
     */
    std::unique_ptr<GDALDataset> MEMDataset::Clone(int nScopeFlags,
                                                   bool bCanShareState) const
    {
        if (MEMDataset::CanBeCloned(nScopeFlags, bCanShareState))
        {
            auto poNewDS = std::make_unique<MEMDataset>();
            poNewDS->poDriver = poDriver;
            poNewDS->nRasterXSize = nRasterXSize;
            poNewDS->nRasterYSize = nRasterYSize;
            poNewDS->bGeoTransformSet = bGeoTransformSet;
            poNewDS->m_gt = m_gt;
            poNewDS->m_oSRS = m_oSRS;
            poNewDS->m_aoGCPs = m_aoGCPs;
            poNewDS->m_oGCPSRS = m_oGCPSRS;
            for (const auto &poOvrDS : m_apoOverviewDS)
            {
                poNewDS->m_apoOverviewDS.emplace_back(
                    poOvrDS->Clone(nScopeFlags, bCanShareState).release());
            }
    
            poNewDS->SetDescription(GetDescription());
            poNewDS->oMDMD = oMDMD;
    
            // Clone bands
            for (int i = 1; i <= nBands; ++i)
            {
                auto poSrcMEMBand =
                    dynamic_cast<const MEMRasterBand *>(papoBands[i - 1]);
                CPLAssert(poSrcMEMBand);
                auto poNewBand = std::make_unique<MEMRasterBand>(
                    poNewDS.get(), i, poSrcMEMBand->pabyData,
                    poSrcMEMBand->GetRasterDataType(), poSrcMEMBand->nPixelOffset,
                    poSrcMEMBand->nLineOffset,
                    /* bAssumeOwnership = */ false);
    
                poNewBand->SetDescription(poSrcMEMBand->GetDescription());
                poNewBand->oMDMD = poSrcMEMBand->oMDMD;
    
                if (poSrcMEMBand->psPam)
                {
                    poNewBand->PamInitialize();
                    CPLAssert(poNewBand->psPam);
                    poNewBand->psPam->CopyFrom(*(poSrcMEMBand->psPam));
                }
    
                // Instantiates a mask band when needed.
                if ((poSrcMEMBand->nMaskFlags &
                     (GMF_ALL_VALID | GMF_ALPHA | GMF_NODATA)) == 0)
                {
                    auto poSrcMaskBand = dynamic_cast<const MEMRasterBand *>(
                        poSrcMEMBand->poMask.get());
                    if (poSrcMaskBand)
                    {
                        auto poMaskBand =
                            std::unique_ptr<MEMRasterBand>(new MEMRasterBand(
                                poSrcMaskBand->pabyData, GDT_UInt8, nRasterXSize,
                                nRasterYSize, /* bOwnData = */ false));
                        poMaskBand->m_bIsMask = true;
                        poNewBand->poMask.reset(std::move(poMaskBand));
                        poNewBand->nMaskFlags = poSrcMaskBand->nMaskFlags;
                    }
                }
    
                poNewDS->SetBand(i, std::move(poNewBand));
            }
    
            return poNewDS;
        }
        return GDALDataset::Clone(nScopeFlags, bCanShareState);
    }
    
    /************************************************************************/
    /*                                Open()                                */
    /************************************************************************/
    
    GDALDataset *MEMDataset::Open(GDALOpenInfo *poOpenInfo)
    
    {
        /* -------------------------------------------------------------------- */
        /*      Do we have the special filename signature for MEM format        */
        /*      description strings?                                            */
        /* -------------------------------------------------------------------- */
        if (!STARTS_WITH_CI(poOpenInfo->pszFilename, "MEM:::") ||
            poOpenInfo->fpL != nullptr)
            return nullptr;
    
    #ifndef GDAL_MEM_ENABLE_OPEN
        if (!CPLTestBool(CPLGetConfigOption("GDAL_MEM_ENABLE_OPEN", "NO")))
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "Opening a MEM dataset with the MEM:::DATAPOINTER= syntax "
                     "is no longer supported by default for security reasons. "
                     "If you want to allow it, define the "
                     "GDAL_MEM_ENABLE_OPEN "
                     "configuration option to YES, or build GDAL with the "
                     "GDAL_MEM_ENABLE_OPEN compilation definition");
            return nullptr;
        }
    #endif
    
        const CPLStringList aosOptions(CSLTokenizeStringComplex(
            poOpenInfo->pszFilename + 6, ",", TRUE, FALSE));
    
        /* -------------------------------------------------------------------- */
        /*      Verify we have all required fields                              */
        /* -------------------------------------------------------------------- */
        if (aosOptions.FetchNameValue("PIXELS") == nullptr ||
            aosOptions.FetchNameValue("LINES") == nullptr ||
            aosOptions.FetchNameValue("DATAPOINTER") == nullptr)
        {
            CPLError(
                CE_Failure, CPLE_AppDefined,
                "Missing required field (one of PIXELS, LINES or DATAPOINTER).  "
                "Unable to access in-memory array.");
    
            return nullptr;
        }
    
        /* -------------------------------------------------------------------- */
        /*      Create the new MEMDataset object.                               */
        /* -------------------------------------------------------------------- */
        auto poDS = std::make_unique<MEMDataset>();
    
        poDS->nRasterXSize = atoi(aosOptions.FetchNameValue("PIXELS"));
        poDS->nRasterYSize = atoi(aosOptions.FetchNameValue("LINES"));
        poDS->eAccess = poOpenInfo->eAccess;
    
        /* -------------------------------------------------------------------- */
        /*      Extract other information.                                      */
        /* -------------------------------------------------------------------- */
        const char *pszOption = aosOptions.FetchNameValue("BANDS");
        int nBands = 1;
        if (pszOption != nullptr)
        {
            nBands = atoi(pszOption);
        }
    
        if (!GDALCheckDatasetDimensions(poDS->nRasterXSize, poDS->nRasterYSize) ||
            !GDALCheckBandCount(nBands, TRUE))
        {
            return nullptr;
        }
    
        pszOption = aosOptions.FetchNameValue("DATATYPE");
        GDALDataType eType = GDT_UInt8;
        if (pszOption != nullptr)
        {
            if (atoi(pszOption) > 0 && atoi(pszOption) < GDT_TypeCount)
                eType = static_cast<GDALDataType>(atoi(pszOption));
            else
            {
                eType = GDALGetDataTypeByName(pszOption);
                if (eType == GDT_Unknown)
                {
                    CPLError(CE_Failure, CPLE_AppDefined,
                             "DATATYPE=%s not recognised.", pszOption);
                    return nullptr;
                }
            }
        }
    
        pszOption = aosOptions.FetchNameValue("PIXELOFFSET");
        GSpacing nPixelOffset;
        if (pszOption == nullptr)
            nPixelOffset = GDALGetDataTypeSizeBytes(eType);
        else
            nPixelOffset =
                CPLScanUIntBig(pszOption, static_cast<int>(strlen(pszOption)));
    
        pszOption = aosOptions.FetchNameValue("LINEOFFSET");
        GSpacing nLineOffset = 0;
        if (pszOption == nullptr)
            nLineOffset = poDS->nRasterXSize * static_cast<size_t>(nPixelOffset);
        else
            nLineOffset =
                CPLScanUIntBig(pszOption, static_cast<int>(strlen(pszOption)));
    
        pszOption = aosOptions.FetchNameValue("BANDOFFSET");
        GSpacing nBandOffset = 0;
        if (pszOption == nullptr)
            nBandOffset = nLineOffset * static_cast<size_t>(poDS->nRasterYSize);
        else
            nBandOffset =
                CPLScanUIntBig(pszOption, static_cast<int>(strlen(pszOption)));
    
        const char *pszDataPointer = aosOptions.FetchNameValue("DATAPOINTER");
        GByte *pabyData = static_cast<GByte *>(CPLScanPointer(
            pszDataPointer, static_cast<int>(strlen(pszDataPointer))));
    
        /* -------------------------------------------------------------------- */
        /*      Create band information objects.                                */
        /* -------------------------------------------------------------------- */
        for (int iBand = 0; iBand < nBands; iBand++)
        {
            poDS->SetBand(iBand + 1,
                          std::make_unique<MEMRasterBand>(
                              poDS.get(), iBand + 1, pabyData + iBand * nBandOffset,
                              eType, nPixelOffset, nLineOffset, FALSE));
        }
    
        /* -------------------------------------------------------------------- */
        /*      Set GeoTransform information.                                   */
        /* -------------------------------------------------------------------- */
    
        pszOption = aosOptions.FetchNameValue("GEOTRANSFORM");
        if (pszOption != nullptr)
        {
            const CPLStringList values(
                CSLTokenizeStringComplex(pszOption, "/", TRUE, FALSE));
            if (values.size() == 6)
            {
                GDALGeoTransform gt;
                for (size_t i = 0; i < 6; ++i)
                {
                    gt[i] = CPLScanDouble(values[i],
                                          static_cast<int>(strlen(values[i])));
                }
                poDS->SetGeoTransform(gt);
            }
        }
    
        /* -------------------------------------------------------------------- */
        /*      Set Projection Information                                      */
        /* -------------------------------------------------------------------- */
    
        pszOption = aosOptions.FetchNameValue("SPATIALREFERENCE");
        if (pszOption != nullptr)
        {
            poDS->m_oSRS.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER);
            if (poDS->m_oSRS.SetFromUserInput(pszOption) != OGRERR_NONE)
            {
                CPLError(CE_Warning, CPLE_AppDefined, "Unrecognized crs: %s",
                         pszOption);
            }
        }
        /* -------------------------------------------------------------------- */
        /*      Try to return a regular handle on the file.                     */
        /* -------------------------------------------------------------------- */
        return poDS.release();
    }
    
    /************************************************************************/
    /*                               Create()                               */
    /************************************************************************/
    
    MEMDataset *MEMDataset::Create(const char * /* pszFilename */, int nXSize,
                                   int nYSize, int nBandsIn, GDALDataType eType,
                                   CSLConstList papszOptions)
    {
    
        /* -------------------------------------------------------------------- */
        /*      Do we want a pixel interleaved buffer?  I mostly care about     */
        /*      this to test pixel interleaved IO in other contexts, but it     */
        /*      could be useful to create a directly accessible buffer for      */
        /*      some apps.                                                      */
        /* -------------------------------------------------------------------- */
        bool bPixelInterleaved = false;
        const char *pszOption = CSLFetchNameValue(papszOptions, "INTERLEAVE");
        if (pszOption && EQUAL(pszOption, "PIXEL"))
            bPixelInterleaved = true;
    
        /* -------------------------------------------------------------------- */
        /*      First allocate band data, verifying that we can get enough      */
        /*      memory.                                                         */
        /* -------------------------------------------------------------------- */
        const int nWordSize = GDALGetDataTypeSizeBytes(eType);
        if (nBandsIn > 0 && nWordSize > 0 &&
            (nBandsIn > INT_MAX / nWordSize ||
             static_cast<GIntBig>(nXSize) * nYSize >
                 GINTBIG_MAX / (nWordSize * nBandsIn)))
        {
            CPLError(CE_Failure, CPLE_OutOfMemory, "Multiplication overflow");
            return nullptr;
        }
    
        const GUIntBig nGlobalBigSize =
            static_cast<GUIntBig>(nWordSize) * nBandsIn * nXSize * nYSize;
        const size_t nGlobalSize = static_cast<size_t>(nGlobalBigSize);
    #if SIZEOF_VOIDP == 4
        if (static_cast<GUIntBig>(nGlobalSize) != nGlobalBigSize)
        {
            CPLError(CE_Failure, CPLE_OutOfMemory,
                     "Cannot allocate " CPL_FRMT_GUIB " bytes on this platform.",
                     nGlobalBigSize);
            return nullptr;
        }
    #endif
    
        std::vector<GByte *> apbyBandData;
        if (nBandsIn > 0)
        {
            GByte *pabyData =
                static_cast<GByte *>(VSI_CALLOC_VERBOSE(1, nGlobalSize));
            if (!pabyData)
            {
                return nullptr;
            }
    
            if (bPixelInterleaved)
            {
                for (int iBand = 0; iBand < nBandsIn; iBand++)
                {
                    apbyBandData.push_back(pabyData + iBand * nWordSize);
                }
            }
            else
            {
                for (int iBand = 0; iBand < nBandsIn; iBand++)
                {
                    apbyBandData.push_back(
                        pabyData +
                        (static_cast<size_t>(nWordSize) * nXSize * nYSize) * iBand);
                }
            }
        }
    
        /* -------------------------------------------------------------------- */
        /*      Create the new GTiffDataset object.                             */
        /* -------------------------------------------------------------------- */
        MEMDataset *poDS = new MEMDataset();
    
        poDS->nRasterXSize = nXSize;
        poDS->nRasterYSize = nYSize;
        poDS->eAccess = GA_Update;
    
        const char *pszPixelType = CSLFetchNameValue(papszOptions, "PIXELTYPE");
        if (pszPixelType && EQUAL(pszPixelType, "SIGNEDBYTE"))
            poDS->SetMetadataItem("PIXELTYPE", "SIGNEDBYTE", "IMAGE_STRUCTURE");
    
        if (nXSize != 0 && nYSize != 0)
        {
            if (bPixelInterleaved)
                poDS->SetMetadataItem("INTERLEAVE", "PIXEL", "IMAGE_STRUCTURE");
            else
                poDS->SetMetadataItem("INTERLEAVE", "BAND", "IMAGE_STRUCTURE");
        }
    
        /* -------------------------------------------------------------------- */
        /*      Create band information objects.                                */
        /* -------------------------------------------------------------------- */
        for (int iBand = 0; iBand < nBandsIn; iBand++)
        {
            MEMRasterBand *poNewBand = nullptr;
    
            if (bPixelInterleaved)
                poNewBand = new MEMRasterBand(
                    poDS, iBand + 1, apbyBandData[iBand], eType,
                    cpl::fits_on<int>(nWordSize * nBandsIn), 0, iBand == 0);
            else
                poNewBand = new MEMRasterBand(poDS, iBand + 1, apbyBandData[iBand],
                                              eType, 0, 0, iBand == 0);
    
            if (const char *pszNBITS = CSLFetchNameValue(papszOptions, "NBITS"))
            {
                poNewBand->SetMetadataItem("NBITS", pszNBITS, "IMAGE_STRUCTURE");
            }
    
            poDS->SetBand(iBand + 1, poNewBand);
        }
    
        /* -------------------------------------------------------------------- */
        /*      Try to return a regular handle on the file.                     */
        /* -------------------------------------------------------------------- */
        return poDS;
    }
    
    GDALDataset *MEMDataset::CreateBase(const char *pszFilename, int nXSize,
                                        int nYSize, int nBandsIn,
                                        GDALDataType eType,
                                        CSLConstList papszOptions)
    {
        return Create(pszFilename, nXSize, nYSize, nBandsIn, eType, papszOptions);
    }
    
    /************************************************************************/
    /*                        ~MEMAttributeHolder()                         */
    /************************************************************************/
    
    MEMAttributeHolder::~MEMAttributeHolder() = default;
    
    /************************************************************************/
    /*                          RenameAttribute()                           */
    /************************************************************************/
    
    bool MEMAttributeHolder::RenameAttribute(const std::string &osOldName,
                                             const std::string &osNewName)
    {
        if (m_oMapAttributes.find(osNewName) != m_oMapAttributes.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "An attribute with same name already exists");
            return false;
        }
        auto oIter = m_oMapAttributes.find(osOldName);
        if (oIter == m_oMapAttributes.end())
        {
            CPLAssert(false);
            return false;
        }
        auto poAttr = std::move(oIter->second);
        m_oMapAttributes.erase(oIter);
        m_oMapAttributes[osNewName] = std::move(poAttr);
        return true;
    }
    
    /************************************************************************/
    /*                          GetMDArrayNames()                           */
    /************************************************************************/
    
    std::vector<std::string> MEMGroup::GetMDArrayNames(CSLConstList) const
    {
        if (!CheckValidAndErrorOutIfNot())
            return {};
        std::vector<std::string> names;
        for (const auto &iter : m_oMapMDArrays)
            names.push_back(iter.first);
        return names;
    }
    
    /************************************************************************/
    /*                            OpenMDArray()                             */
    /************************************************************************/
    
    std::shared_ptr<GDALMDArray> MEMGroup::OpenMDArray(const std::string &osName,
                                                       CSLConstList) const
    {
        if (!CheckValidAndErrorOutIfNot())
            return nullptr;
        auto oIter = m_oMapMDArrays.find(osName);
        if (oIter != m_oMapMDArrays.end())
            return oIter->second;
        return nullptr;
    }
    
    /************************************************************************/
    /*                           GetGroupNames()                            */
    /************************************************************************/
    
    std::vector<std::string> MEMGroup::GetGroupNames(CSLConstList) const
    {
        if (!CheckValidAndErrorOutIfNot())
            return {};
        std::vector<std::string> names;
        for (const auto &iter : m_oMapGroups)
            names.push_back(iter.first);
        return names;
    }
    
    /************************************************************************/
    /*                             OpenGroup()                              */
    /************************************************************************/
    
    std::shared_ptr<GDALGroup> MEMGroup::OpenGroup(const std::string &osName,
                                                   CSLConstList) const
    {
        if (!CheckValidAndErrorOutIfNot())
            return nullptr;
        auto oIter = m_oMapGroups.find(osName);
        if (oIter != m_oMapGroups.end())
            return oIter->second;
        return nullptr;
    }
    
    /************************************************************************/
    /*                               Create()                               */
    /************************************************************************/
    
    /*static*/
    std::shared_ptr<MEMGroup> MEMGroup::Create(const std::string &osParentName,
                                               const char *pszName)
    {
        auto newGroup(
            std::shared_ptr<MEMGroup>(new MEMGroup(osParentName, pszName)));
        newGroup->SetSelf(newGroup);
        if (osParentName.empty())
            newGroup->m_poRootGroupWeak = newGroup;
        return newGroup;
    }
    
    /************************************************************************/
    /*                            CreateGroup()                             */
    /************************************************************************/
    
    std::shared_ptr<GDALGroup> MEMGroup::CreateGroup(const std::string &osName,
                                                     CSLConstList /*papszOptions*/)
    {
        if (!CheckValidAndErrorOutIfNot())
            return nullptr;
        if (osName.empty())
        {
            CPLError(CE_Failure, CPLE_NotSupported,
                     "Empty group name not supported");
            return nullptr;
        }
        if (m_oMapGroups.find(osName) != m_oMapGroups.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "A group with same name already exists");
            return nullptr;
        }
        auto newGroup = MEMGroup::Create(GetFullName(), osName.c_str());
        newGroup->m_pParent = std::dynamic_pointer_cast<MEMGroup>(m_pSelf.lock());
        newGroup->m_poRootGroupWeak = m_poRootGroupWeak;
        m_oMapGroups[osName] = newGroup;
        return newGroup;
    }
    
    /************************************************************************/
    /*                            DeleteGroup()                             */
    /************************************************************************/
    
    bool MEMGroup::DeleteGroup(const std::string &osName,
                               CSLConstList /*papszOptions*/)
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
        auto oIter = m_oMapGroups.find(osName);
        if (oIter == m_oMapGroups.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "Group %s is not a sub-group of this group", osName.c_str());
            return false;
        }
    
        oIter->second->Deleted();
        m_oMapGroups.erase(oIter);
        return true;
    }
    
    /************************************************************************/
    /*                      NotifyChildrenOfDeletion()                      */
    /************************************************************************/
    
    void MEMGroup::NotifyChildrenOfDeletion()
    {
        for (const auto &oIter : m_oMapGroups)
            oIter.second->ParentDeleted();
        for (const auto &oIter : m_oMapMDArrays)
            oIter.second->ParentDeleted();
        for (const auto &oIter : m_oMapAttributes)
            oIter.second->ParentDeleted();
        for (const auto &oIter : m_oMapDimensions)
            oIter.second->ParentDeleted();
    }
    
    /************************************************************************/
    /*                           CreateMDArray()                            */
    /************************************************************************/
    
    std::shared_ptr<GDALMDArray> MEMGroup::CreateMDArray(
        const std::string &osName,
        const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
        const GDALExtendedDataType &oType, void *pData, CSLConstList papszOptions)
    {
        if (!CheckValidAndErrorOutIfNot())
            return nullptr;
        if (osName.empty())
        {
            CPLError(CE_Failure, CPLE_NotSupported,
                     "Empty array name not supported");
            return nullptr;
        }
        if (m_oMapMDArrays.find(osName) != m_oMapMDArrays.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "An array with same name already exists");
            return nullptr;
        }
        auto newArray(
            MEMMDArray::Create(GetFullName(), osName, aoDimensions, oType));
    
        GByte *pabyData = nullptr;
        std::vector<GPtrDiff_t> anStrides;
        if (pData)
        {
            pabyData = static_cast<GByte *>(pData);
            const char *pszStrides = CSLFetchNameValue(papszOptions, "STRIDES");
            if (pszStrides)
            {
                CPLStringList aosStrides(CSLTokenizeString2(pszStrides, ",", 0));
                if (static_cast<size_t>(aosStrides.size()) != aoDimensions.size())
                {
                    CPLError(CE_Failure, CPLE_AppDefined,
                             "Invalid number of strides");
                    return nullptr;
                }
                for (int i = 0; i < aosStrides.size(); i++)
                {
                    const auto nStride = CPLAtoGIntBig(aosStrides[i]);
                    anStrides.push_back(static_cast<GPtrDiff_t>(nStride));
                }
            }
        }
        if (!newArray->Init(pabyData, anStrides))
            return nullptr;
    
        for (auto &poDim : newArray->GetDimensions())
        {
            const auto dim = std::dynamic_pointer_cast<MEMDimension>(poDim);
            if (dim)
                dim->RegisterUsingArray(newArray.get());
        }
    
        newArray->RegisterGroup(m_pSelf);
        m_oMapMDArrays[osName] = newArray;
        return newArray;
    }
    
    std::shared_ptr<GDALMDArray> MEMGroup::CreateMDArray(
        const std::string &osName,
        const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
        const GDALExtendedDataType &oType, CSLConstList papszOptions)
    {
        void *pData = nullptr;
        const char *pszDataPointer = CSLFetchNameValue(papszOptions, "DATAPOINTER");
        if (pszDataPointer)
        {
            // Will not work on architectures with "capability pointers"
            pData = CPLScanPointer(pszDataPointer,
                                   static_cast<int>(strlen(pszDataPointer)));
        }
        return CreateMDArray(osName, aoDimensions, oType, pData, papszOptions);
    }
    
    /************************************************************************/
    /*                           DeleteMDArray()                            */
    /************************************************************************/
    
    bool MEMGroup::DeleteMDArray(const std::string &osName,
                                 CSLConstList /*papszOptions*/)
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
        auto oIter = m_oMapMDArrays.find(osName);
        if (oIter == m_oMapMDArrays.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "Array %s is not an array of this group", osName.c_str());
            return false;
        }
    
        oIter->second->Deleted();
        m_oMapMDArrays.erase(oIter);
        return true;
    }
    
    /************************************************************************/
    /*                       MEMGroupCreateMDArray()                        */
    /************************************************************************/
    
    // Used by NUMPYMultiDimensionalDataset
    std::shared_ptr<GDALMDArray> MEMGroupCreateMDArray(
        GDALGroup *poGroup, const std::string &osName,
        const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
        const GDALExtendedDataType &oDataType, void *pData,
        CSLConstList papszOptions)
    {
        auto poMemGroup = dynamic_cast<MEMGroup *>(poGroup);
        if (!poMemGroup)
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "MEMGroupCreateMDArray(): poGroup not of type MEMGroup");
            return nullptr;
        }
        return poMemGroup->CreateMDArray(osName, aoDimensions, oDataType, pData,
                                         papszOptions);
    }
    
    /************************************************************************/
    /*                            GetAttribute()                            */
    /************************************************************************/
    
    std::shared_ptr<GDALAttribute>
    MEMGroup::GetAttribute(const std::string &osName) const
    {
        if (!CheckValidAndErrorOutIfNot())
            return nullptr;
        auto oIter = m_oMapAttributes.find(osName);
        if (oIter != m_oMapAttributes.end())
            return oIter->second;
        return nullptr;
    }
    
    /************************************************************************/
    /*                           GetAttributes()                            */
    /************************************************************************/
    
    std::vector<std::shared_ptr<GDALAttribute>>
    MEMGroup::GetAttributes(CSLConstList) const
    {
        if (!CheckValidAndErrorOutIfNot())
            return {};
        std::vector<std::shared_ptr<GDALAttribute>> oRes;
        for (const auto &oIter : m_oMapAttributes)
        {
            oRes.push_back(oIter.second);
        }
        return oRes;
    }
    
    /************************************************************************/
    /*                           GetDimensions()                            */
    /************************************************************************/
    
    std::vector<std::shared_ptr<GDALDimension>>
    MEMGroup::GetDimensions(CSLConstList) const
    {
        if (!CheckValidAndErrorOutIfNot())
            return {};
        std::vector<std::shared_ptr<GDALDimension>> oRes;
        for (const auto &oIter : m_oMapDimensions)
        {
            oRes.push_back(oIter.second);
        }
        return oRes;
    }
    
    /************************************************************************/
    /*                          CreateAttribute()                           */
    /************************************************************************/
    
    std::shared_ptr<GDALAttribute>
    MEMGroup::CreateAttribute(const std::string &osName,
                              const std::vector<GUInt64> &anDimensions,
                              const GDALExtendedDataType &oDataType, CSLConstList)
    {
        if (!CheckValidAndErrorOutIfNot())
            return nullptr;
        if (osName.empty())
        {
            CPLError(CE_Failure, CPLE_NotSupported,
                     "Empty attribute name not supported");
            return nullptr;
        }
        if (m_oMapAttributes.find(osName) != m_oMapAttributes.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "An attribute with same name already exists");
            return nullptr;
        }
        auto newAttr(MEMAttribute::Create(
            std::dynamic_pointer_cast<MEMGroup>(m_pSelf.lock()), osName,
            anDimensions, oDataType));
        if (!newAttr)
            return nullptr;
        m_oMapAttributes[osName] = newAttr;
        return newAttr;
    }
    
    /************************************************************************/
    /*                          DeleteAttribute()                           */
    /************************************************************************/
    
    bool MEMGroup::DeleteAttribute(const std::string &osName,
                                   CSLConstList /*papszOptions*/)
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
        auto oIter = m_oMapAttributes.find(osName);
        if (oIter == m_oMapAttributes.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "Attribute %s is not an attribute of this group",
                     osName.c_str());
            return false;
        }
    
        oIter->second->Deleted();
        m_oMapAttributes.erase(oIter);
        return true;
    }
    
    /************************************************************************/
    /*                               Rename()                               */
    /************************************************************************/
    
    bool MEMGroup::Rename(const std::string &osNewName)
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
        if (osNewName.empty())
        {
            CPLError(CE_Failure, CPLE_NotSupported, "Empty name not supported");
            return false;
        }
        if (m_osName == "/")
        {
            CPLError(CE_Failure, CPLE_NotSupported, "Cannot rename root group");
            return false;
        }
        auto pParent = m_pParent.lock();
        if (pParent)
        {
            if (pParent->m_oMapGroups.find(osNewName) !=
                pParent->m_oMapGroups.end())
            {
                CPLError(CE_Failure, CPLE_AppDefined,
                         "A group with same name already exists");
                return false;
            }
            pParent->m_oMapGroups.erase(pParent->m_oMapGroups.find(m_osName));
        }
    
        BaseRename(osNewName);
    
        if (pParent)
        {
            CPLAssert(m_pSelf.lock());
            pParent->m_oMapGroups[m_osName] = m_pSelf.lock();
        }
    
        return true;
    }
    
    /************************************************************************/
    /*                      NotifyChildrenOfRenaming()                      */
    /************************************************************************/
    
    void MEMGroup::NotifyChildrenOfRenaming()
    {
        for (const auto &oIter : m_oMapGroups)
            oIter.second->ParentRenamed(m_osFullName);
        for (const auto &oIter : m_oMapMDArrays)
            oIter.second->ParentRenamed(m_osFullName);
        for (const auto &oIter : m_oMapAttributes)
            oIter.second->ParentRenamed(m_osFullName);
        for (const auto &oIter : m_oMapDimensions)
            oIter.second->ParentRenamed(m_osFullName);
    }
    
    /************************************************************************/
    /*                          RenameDimension()                           */
    /************************************************************************/
    
    bool MEMGroup::RenameDimension(const std::string &osOldName,
                                   const std::string &osNewName)
    {
        if (m_oMapDimensions.find(osNewName) != m_oMapDimensions.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "A dimension with same name already exists");
            return false;
        }
        auto oIter = m_oMapDimensions.find(osOldName);
        if (oIter == m_oMapDimensions.end())
        {
            CPLAssert(false);
            return false;
        }
        auto poDim = std::move(oIter->second);
        m_oMapDimensions.erase(oIter);
        m_oMapDimensions[osNewName] = std::move(poDim);
        return true;
    }
    
    /************************************************************************/
    /*                            RenameArray()                             */
    /************************************************************************/
    
    bool MEMGroup::RenameArray(const std::string &osOldName,
                               const std::string &osNewName)
    {
        if (m_oMapMDArrays.find(osNewName) != m_oMapMDArrays.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "An array with same name already exists");
            return false;
        }
        auto oIter = m_oMapMDArrays.find(osOldName);
        if (oIter == m_oMapMDArrays.end())
        {
            CPLAssert(false);
            return false;
        }
        auto poArray = std::move(oIter->second);
        m_oMapMDArrays.erase(oIter);
        m_oMapMDArrays[osNewName] = std::move(poArray);
        return true;
    }
    
    /************************************************************************/
    /*                         MEMAbstractMDArray()                         */
    /************************************************************************/
    
    MEMAbstractMDArray::MEMAbstractMDArray(
        const std::string &osParentName, const std::string &osName,
        const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
        const GDALExtendedDataType &oType)
        : GDALAbstractMDArray(osParentName, osName), m_aoDims(aoDimensions),
          m_oType(oType)
    {
    }
    
    /************************************************************************/
    /*                        ~MEMAbstractMDArray()                         */
    /************************************************************************/
    
    MEMAbstractMDArray::~MEMAbstractMDArray()
    {
        FreeArray();
    }
    
    /************************************************************************/
    /*                             FreeArray()                              */
    /************************************************************************/
    
    void MEMAbstractMDArray::FreeArray()
    {
        if (m_bOwnArray)
        {
            if (m_oType.NeedsFreeDynamicMemory())
            {
                GByte *pabyPtr = m_pabyArray;
                GByte *pabyEnd = m_pabyArray + m_nTotalSize;
                const auto nDTSize(m_oType.GetSize());
                while (pabyPtr < pabyEnd)
                {
                    m_oType.FreeDynamicMemory(pabyPtr);
                    pabyPtr += nDTSize;
                }
            }
            VSIFree(m_pabyArray);
            m_pabyArray = nullptr;
            m_nTotalSize = 0;
            m_bOwnArray = false;
        }
    }
    
    /************************************************************************/
    /*                                Init()                                */
    /************************************************************************/
    
    bool MEMAbstractMDArray::Init(GByte *pData,
                                  const std::vector<GPtrDiff_t> &anStrides)
    {
        GUInt64 nTotalSize = m_oType.GetSize();
        if (!m_aoDims.empty())
        {
            if (anStrides.empty())
            {
                m_anStrides.resize(m_aoDims.size());
            }
            else
            {
                CPLAssert(anStrides.size() == m_aoDims.size());
                m_anStrides = anStrides;
            }
    
            // To compute strides we must proceed from the fastest varying dimension
            // (the last one), and then reverse the result
            for (size_t i = m_aoDims.size(); i != 0;)
            {
                --i;
                const auto &poDim = m_aoDims[i];
                auto nDimSize = poDim->GetSize();
                if (nDimSize == 0)
                {
                    CPLError(CE_Failure, CPLE_IllegalArg,
                             "Illegal dimension size 0");
                    return false;
                }
                if (nTotalSize > std::numeric_limits<GUInt64>::max() / nDimSize)
                {
                    CPLError(CE_Failure, CPLE_OutOfMemory, "Too big allocation");
                    return false;
                }
                auto nNewSize = nTotalSize * nDimSize;
                if (anStrides.empty())
                    m_anStrides[i] = static_cast<size_t>(nTotalSize);
                nTotalSize = nNewSize;
            }
        }
    
        // We restrict the size of the allocation so that all elements can be
        // indexed by GPtrDiff_t
        if (nTotalSize >
            static_cast<size_t>(std::numeric_limits<GPtrDiff_t>::max()))
        {
            CPLError(CE_Failure, CPLE_OutOfMemory, "Too big allocation");
            return false;
        }
        m_nTotalSize = static_cast<size_t>(nTotalSize);
        if (pData)
        {
            m_pabyArray = pData;
        }
        else
        {
            m_pabyArray = static_cast<GByte *>(VSI_CALLOC_VERBOSE(1, m_nTotalSize));
            m_bOwnArray = true;
        }
    
        return m_pabyArray != nullptr;
    }
    
    /************************************************************************/
    /*                              FastCopy()                              */
    /************************************************************************/
    
    template <int N>
    inline static void FastCopy(size_t nIters, GByte *dstPtr, const GByte *srcPtr,
                                GPtrDiff_t dst_inc_offset,
                                GPtrDiff_t src_inc_offset)
    {
        if (nIters >= 8)
        {
    #define COPY_ELT(i)                                                            \
        memcpy(dstPtr + (i) * dst_inc_offset, srcPtr + (i) * src_inc_offset, N)
            while (true)
            {
                COPY_ELT(0);
                COPY_ELT(1);
                COPY_ELT(2);
                COPY_ELT(3);
                COPY_ELT(4);
                COPY_ELT(5);
                COPY_ELT(6);
                COPY_ELT(7);
                nIters -= 8;
                srcPtr += 8 * src_inc_offset;
                dstPtr += 8 * dst_inc_offset;
                if (nIters < 8)
                    break;
            }
            if (nIters == 0)
                return;
        }
        while (true)
        {
            memcpy(dstPtr, srcPtr, N);
            if ((--nIters) == 0)
                break;
            srcPtr += src_inc_offset;
            dstPtr += dst_inc_offset;
        }
    }
    
    /************************************************************************/
    /*                             ReadWrite()                              */
    /************************************************************************/
    
    void MEMAbstractMDArray::ReadWrite(bool bIsWrite, const size_t *count,
                                       std::vector<StackReadWrite> &stack,
                                       const GDALExtendedDataType &srcType,
                                       const GDALExtendedDataType &dstType) const
    {
        const auto nDims = m_aoDims.size();
        const auto nDimsMinus1 = nDims - 1;
        const bool bBothAreNumericDT = srcType.GetClass() == GEDTC_NUMERIC &&
                                       dstType.GetClass() == GEDTC_NUMERIC;
        const bool bSameNumericDT =
            bBothAreNumericDT &&
            srcType.GetNumericDataType() == dstType.GetNumericDataType();
        const auto nSameDTSize = bSameNumericDT ? srcType.GetSize() : 0;
        const bool bCanUseMemcpyLastDim =
            bSameNumericDT &&
            stack[nDimsMinus1].src_inc_offset ==
                static_cast<GPtrDiff_t>(nSameDTSize) &&
            stack[nDimsMinus1].dst_inc_offset ==
                static_cast<GPtrDiff_t>(nSameDTSize);
        const size_t nCopySizeLastDim =
            bCanUseMemcpyLastDim ? nSameDTSize * count[nDimsMinus1] : 0;
        const bool bNeedsFreeDynamicMemory =
            bIsWrite && dstType.NeedsFreeDynamicMemory();
    
        auto lambdaLastDim = [&](size_t idxPtr)
        {
            auto srcPtr = stack[idxPtr].src_ptr;
            auto dstPtr = stack[idxPtr].dst_ptr;
            if (nCopySizeLastDim)
            {
                memcpy(dstPtr, srcPtr, nCopySizeLastDim);
            }
            else
            {
                size_t nIters = count[nDimsMinus1];
                const auto dst_inc_offset = stack[nDimsMinus1].dst_inc_offset;
                const auto src_inc_offset = stack[nDimsMinus1].src_inc_offset;
                if (bSameNumericDT)
                {
                    if (nSameDTSize == 1)
                    {
                        FastCopy<1>(nIters, dstPtr, srcPtr, dst_inc_offset,
                                    src_inc_offset);
                        return;
                    }
                    if (nSameDTSize == 2)
                    {
                        FastCopy<2>(nIters, dstPtr, srcPtr, dst_inc_offset,
                                    src_inc_offset);
                        return;
                    }
                    if (nSameDTSize == 4)
                    {
                        FastCopy<4>(nIters, dstPtr, srcPtr, dst_inc_offset,
                                    src_inc_offset);
                        return;
                    }
                    if (nSameDTSize == 8)
                    {
                        FastCopy<8>(nIters, dstPtr, srcPtr, dst_inc_offset,
                                    src_inc_offset);
                        return;
                    }
                    if (nSameDTSize == 16)
                    {
                        FastCopy<16>(nIters, dstPtr, srcPtr, dst_inc_offset,
                                     src_inc_offset);
                        return;
                    }
                    CPLAssert(false);
                }
                else if (bBothAreNumericDT
    #if SIZEOF_VOIDP >= 8
                         && src_inc_offset <= std::numeric_limits<int>::max() &&
                         dst_inc_offset <= std::numeric_limits<int>::max()
    #endif
                )
                {
                    GDALCopyWords64(srcPtr, srcType.GetNumericDataType(),
                                    static_cast<int>(src_inc_offset), dstPtr,
                                    dstType.GetNumericDataType(),
                                    static_cast<int>(dst_inc_offset),
                                    static_cast<GPtrDiff_t>(nIters));
                    return;
                }
    
                while (true)
                {
                    if (bNeedsFreeDynamicMemory)
                    {
                        dstType.FreeDynamicMemory(dstPtr);
                    }
                    GDALExtendedDataType::CopyValue(srcPtr, srcType, dstPtr,
                                                    dstType);
                    if ((--nIters) == 0)
                        break;
                    srcPtr += src_inc_offset;
                    dstPtr += dst_inc_offset;
                }
            }
        };
    
        if (nDims == 1)
        {
            lambdaLastDim(0);
        }
        else if (nDims == 2)
        {
            auto nIters = count[0];
            while (true)
            {
                lambdaLastDim(0);
                if ((--nIters) == 0)
                    break;
                stack[0].src_ptr += stack[0].src_inc_offset;
                stack[0].dst_ptr += stack[0].dst_inc_offset;
            }
        }
        else if (nDims == 3)
        {
            stack[0].nIters = count[0];
            while (true)
            {
                stack[1].src_ptr = stack[0].src_ptr;
                stack[1].dst_ptr = stack[0].dst_ptr;
                auto nIters = count[1];
                while (true)
                {
                    lambdaLastDim(1);
                    if ((--nIters) == 0)
                        break;
                    stack[1].src_ptr += stack[1].src_inc_offset;
                    stack[1].dst_ptr += stack[1].dst_inc_offset;
                }
                if ((--stack[0].nIters) == 0)
                    break;
                stack[0].src_ptr += stack[0].src_inc_offset;
                stack[0].dst_ptr += stack[0].dst_inc_offset;
            }
        }
        else
        {
            // Implementation valid for nDims >= 3
    
            size_t dimIdx = 0;
            // Non-recursive implementation. Hence the gotos
            // It might be possible to rewrite this without gotos, but I find they
            // make it clearer to understand the recursive nature of the code
        lbl_next_depth:
            if (dimIdx == nDimsMinus1 - 1)
            {
                auto nIters = count[dimIdx];
                while (true)
                {
                    lambdaLastDim(dimIdx);
                    if ((--nIters) == 0)
                        break;
                    stack[dimIdx].src_ptr += stack[dimIdx].src_inc_offset;
                    stack[dimIdx].dst_ptr += stack[dimIdx].dst_inc_offset;
                }
                // If there was a test if( dimIdx > 0 ), that would be valid for
                // nDims == 2
                goto lbl_return_to_caller;
            }
            else
            {
                stack[dimIdx].nIters = count[dimIdx];
                while (true)
                {
                    dimIdx++;
                    stack[dimIdx].src_ptr = stack[dimIdx - 1].src_ptr;
                    stack[dimIdx].dst_ptr = stack[dimIdx - 1].dst_ptr;
                    goto lbl_next_depth;
                lbl_return_to_caller:
                    dimIdx--;
                    if ((--stack[dimIdx].nIters) == 0)
                        break;
                    stack[dimIdx].src_ptr += stack[dimIdx].src_inc_offset;
                    stack[dimIdx].dst_ptr += stack[dimIdx].dst_inc_offset;
                }
                if (dimIdx > 0)
                    goto lbl_return_to_caller;
            }
        }
    }
    
    /************************************************************************/
    /*                               IRead()                                */
    /************************************************************************/
    
    bool MEMAbstractMDArray::IRead(const GUInt64 *arrayStartIdx,
                                   const size_t *count, const GInt64 *arrayStep,
                                   const GPtrDiff_t *bufferStride,
                                   const GDALExtendedDataType &bufferDataType,
                                   void *pDstBuffer) const
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
    
        const auto nDims = m_aoDims.size();
        if (nDims == 0)
        {
            GDALExtendedDataType::CopyValue(m_pabyArray, m_oType, pDstBuffer,
                                            bufferDataType);
            return true;
        }
        std::vector<StackReadWrite> stack(nDims);
        const auto nBufferDTSize = bufferDataType.GetSize();
        GPtrDiff_t startSrcOffset = 0;
        for (size_t i = 0; i < nDims; i++)
        {
            startSrcOffset +=
                static_cast<GPtrDiff_t>(arrayStartIdx[i] * m_anStrides[i]);
            stack[i].src_inc_offset =
                static_cast<GPtrDiff_t>(arrayStep[i] * m_anStrides[i]);
            stack[i].dst_inc_offset =
                static_cast<GPtrDiff_t>(bufferStride[i] * nBufferDTSize);
        }
        stack[0].src_ptr = m_pabyArray + startSrcOffset;
        stack[0].dst_ptr = static_cast<GByte *>(pDstBuffer);
    
        ReadWrite(false, count, stack, m_oType, bufferDataType);
        return true;
    }
    
    /************************************************************************/
    /*                               IWrite()                               */
    /************************************************************************/
    
    bool MEMAbstractMDArray::IWrite(const GUInt64 *arrayStartIdx,
                                    const size_t *count, const GInt64 *arrayStep,
                                    const GPtrDiff_t *bufferStride,
                                    const GDALExtendedDataType &bufferDataType,
                                    const void *pSrcBuffer)
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
        if (!m_bWritable)
        {
            CPLError(CE_Failure, CPLE_AppDefined, "Non updatable object");
            return false;
        }
    
        m_bModified = true;
    
        const auto nDims = m_aoDims.size();
        if (nDims == 0)
        {
            m_oType.FreeDynamicMemory(m_pabyArray);
            GDALExtendedDataType::CopyValue(pSrcBuffer, bufferDataType, m_pabyArray,
                                            m_oType);
            return true;
        }
        std::vector<StackReadWrite> stack(nDims);
        const auto nBufferDTSize = bufferDataType.GetSize();
        GPtrDiff_t startDstOffset = 0;
        for (size_t i = 0; i < nDims; i++)
        {
            startDstOffset +=
                static_cast<GPtrDiff_t>(arrayStartIdx[i] * m_anStrides[i]);
            stack[i].dst_inc_offset =
                static_cast<GPtrDiff_t>(arrayStep[i] * m_anStrides[i]);
            stack[i].src_inc_offset =
                static_cast<GPtrDiff_t>(bufferStride[i] * nBufferDTSize);
        }
    
        stack[0].dst_ptr = m_pabyArray + startDstOffset;
        stack[0].src_ptr = static_cast<const GByte *>(pSrcBuffer);
    
        ReadWrite(true, count, stack, bufferDataType, m_oType);
        return true;
    }
    
    /************************************************************************/
    /*                             MEMMDArray()                             */
    /************************************************************************/
    
    MEMMDArray::MEMMDArray(
        const std::string &osParentName, const std::string &osName,
        const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
        const GDALExtendedDataType &oType)
        : GDALAbstractMDArray(osParentName, osName),
          MEMAbstractMDArray(osParentName, osName, aoDimensions, oType),
          GDALMDArray(osParentName, osName)
    {
    }
    
    /************************************************************************/
    /*                            ~MEMMDArray()                             */
    /************************************************************************/
    
    MEMMDArray::~MEMMDArray()
    {
        if (m_pabyNoData)
        {
            m_oType.FreeDynamicMemory(&m_pabyNoData[0]);
            CPLFree(m_pabyNoData);
        }
    
        for (auto &poDim : GetDimensions())
        {
            const auto dim = std::dynamic_pointer_cast<MEMDimension>(poDim);
            if (dim)
                dim->UnRegisterUsingArray(this);
        }
    }
    
    /************************************************************************/
    /*                         GetRawNoDataValue()                          */
    /************************************************************************/
    
    const void *MEMMDArray::GetRawNoDataValue() const
    {
        return m_pabyNoData;
    }
    
    /************************************************************************/
    /*                         SetRawNoDataValue()                          */
    /************************************************************************/
    
    bool MEMMDArray::SetRawNoDataValue(const void *pNoData)
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
        if (m_pabyNoData)
        {
            m_oType.FreeDynamicMemory(&m_pabyNoData[0]);
        }
    
        if (pNoData == nullptr)
        {
            CPLFree(m_pabyNoData);
            m_pabyNoData = nullptr;
        }
        else
        {
            const auto nSize = m_oType.GetSize();
            if (m_pabyNoData == nullptr)
            {
                m_pabyNoData = static_cast<GByte *>(CPLMalloc(nSize));
            }
            memset(m_pabyNoData, 0, nSize);
            GDALExtendedDataType::CopyValue(pNoData, m_oType, m_pabyNoData,
                                            m_oType);
        }
        return true;
    }
    
    /************************************************************************/
    /*                            GetAttribute()                            */
    /************************************************************************/
    
    std::shared_ptr<GDALAttribute>
    MEMMDArray::GetAttribute(const std::string &osName) const
    {
        if (!CheckValidAndErrorOutIfNot())
            return nullptr;
        auto oIter = m_oMapAttributes.find(osName);
        if (oIter != m_oMapAttributes.end())
            return oIter->second;
        return nullptr;
    }
    
    /************************************************************************/
    /*                           GetAttributes()                            */
    /************************************************************************/
    
    std::vector<std::shared_ptr<GDALAttribute>>
    MEMMDArray::GetAttributes(CSLConstList) const
    {
        if (!CheckValidAndErrorOutIfNot())
            return {};
        std::vector<std::shared_ptr<GDALAttribute>> oRes;
        for (const auto &oIter : m_oMapAttributes)
        {
            oRes.push_back(oIter.second);
        }
        return oRes;
    }
    
    /************************************************************************/
    /*                          CreateAttribute()                           */
    /************************************************************************/
    
    std::shared_ptr<GDALAttribute>
    MEMMDArray::CreateAttribute(const std::string &osName,
                                const std::vector<GUInt64> &anDimensions,
                                const GDALExtendedDataType &oDataType, CSLConstList)
    {
        if (!CheckValidAndErrorOutIfNot())
            return nullptr;
        if (osName.empty())
        {
            CPLError(CE_Failure, CPLE_NotSupported,
                     "Empty attribute name not supported");
            return nullptr;
        }
        if (m_oMapAttributes.find(osName) != m_oMapAttributes.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "An attribute with same name already exists");
            return nullptr;
        }
        auto poSelf = std::dynamic_pointer_cast<MEMMDArray>(m_pSelf.lock());
        CPLAssert(poSelf);
        auto newAttr(MEMAttribute::Create(poSelf, osName, anDimensions, oDataType));
        if (!newAttr)
            return nullptr;
        m_oMapAttributes[osName] = newAttr;
        return newAttr;
    }
    
    /************************************************************************/
    /*                          DeleteAttribute()                           */
    /************************************************************************/
    
    bool MEMMDArray::DeleteAttribute(const std::string &osName,
                                     CSLConstList /*papszOptions*/)
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
        auto oIter = m_oMapAttributes.find(osName);
        if (oIter == m_oMapAttributes.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "Attribute %s is not an attribute of this array",
                     osName.c_str());
            return false;
        }
    
        oIter->second->Deleted();
        m_oMapAttributes.erase(oIter);
        return true;
    }
    
    /************************************************************************/
    /*                       GetCoordinateVariables()                       */
    /************************************************************************/
    
    std::vector<std::shared_ptr<GDALMDArray>>
    MEMMDArray::GetCoordinateVariables() const
    {
        if (!CheckValidAndErrorOutIfNot())
            return {};
        std::vector<std::shared_ptr<GDALMDArray>> ret;
        const auto poCoordinates = GetAttribute("coordinates");
        if (poCoordinates &&
            poCoordinates->GetDataType().GetClass() == GEDTC_STRING &&
            poCoordinates->GetDimensionCount() == 0)
        {
            const char *pszCoordinates = poCoordinates->ReadAsString();
            if (pszCoordinates)
            {
                auto poGroup = m_poGroupWeak.lock();
                if (!poGroup)
                {
                    CPLError(CE_Failure, CPLE_AppDefined,
                             "Cannot access coordinate variables of %s has "
                             "belonging group has gone out of scope",
                             GetName().c_str());
                }
                else
                {
                    const CPLStringList aosNames(
                        CSLTokenizeString2(pszCoordinates, " ", 0));
                    for (int i = 0; i < aosNames.size(); i++)
                    {
                        auto poCoordinateVar = poGroup->OpenMDArray(aosNames[i]);
                        if (poCoordinateVar)
                        {
                            ret.emplace_back(poCoordinateVar);
                        }
                        else
                        {
                            CPLError(CE_Warning, CPLE_AppDefined,
                                     "Cannot find variable corresponding to "
                                     "coordinate %s",
                                     aosNames[i]);
                        }
                    }
                }
            }
        }
    
        return ret;
    }
    
    /************************************************************************/
    /*                               Resize()                               */
    /************************************************************************/
    
    bool MEMMDArray::Resize(const std::vector<GUInt64> &anNewDimSizes,
                            CSLConstList /* papszOptions */)
    {
        return Resize(anNewDimSizes, /*bResizeOtherArrays=*/true);
    }
    
    bool MEMMDArray::Resize(const std::vector<GUInt64> &anNewDimSizes,
                            bool bResizeOtherArrays)
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
        if (!IsWritable())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "Resize() not supported on read-only file");
            return false;
        }
        if (!m_bOwnArray)
        {
            CPLError(
                CE_Failure, CPLE_AppDefined,
                "Resize() not supported on an array that does not own its memory");
            return false;
        }
    
        const auto nDimCount = GetDimensionCount();
        if (anNewDimSizes.size() != nDimCount)
        {
            CPLError(CE_Failure, CPLE_IllegalArg,
                     "Not expected number of values in anNewDimSizes.");
            return false;
        }
    
        auto &dims = GetDimensions();
        std::vector<size_t> anDecreasedDimIdx;
        std::vector<size_t> anGrownDimIdx;
        std::map<GDALDimension *, GUInt64> oMapDimToSize;
        for (size_t i = 0; i < nDimCount; ++i)
        {
            auto oIter = oMapDimToSize.find(dims[i].get());
            if (oIter != oMapDimToSize.end() && oIter->second != anNewDimSizes[i])
            {
                CPLError(CE_Failure, CPLE_AppDefined,
                         "Cannot resize a dimension referenced several times "
                         "to different sizes");
                return false;
            }
            if (anNewDimSizes[i] != dims[i]->GetSize())
            {
                if (anNewDimSizes[i] == 0)
                {
                    CPLError(CE_Failure, CPLE_IllegalArg,
                             "Illegal dimension size 0");
                    return false;
                }
                auto dim = std::dynamic_pointer_cast<MEMDimension>(dims[i]);
                if (!dim)
                {
                    CPLError(
                        CE_Failure, CPLE_AppDefined,
                        "Cannot resize a dimension that is not a MEMDimension");
                    return false;
                }
                oMapDimToSize[dim.get()] = anNewDimSizes[i];
                if (anNewDimSizes[i] < dims[i]->GetSize())
                {
                    anDecreasedDimIdx.push_back(i);
                }
                else
                {
                    anGrownDimIdx.push_back(i);
                }
            }
            else
            {
                oMapDimToSize[dims[i].get()] = dims[i]->GetSize();
            }
        }
    
        const auto ResizeOtherArrays = [this, &anNewDimSizes, nDimCount, &dims]()
        {
            std::set<MEMMDArray *> oSetArrays;
            std::map<GDALDimension *, GUInt64> oMapNewSize;
            for (size_t i = 0; i < nDimCount; ++i)
            {
                if (anNewDimSizes[i] != dims[i]->GetSize())
                {
                    auto dim = std::dynamic_pointer_cast<MEMDimension>(dims[i]);
                    if (!dim)
                    {
                        CPLAssert(false);
                    }
                    else
                    {
                        oMapNewSize[dims[i].get()] = anNewDimSizes[i];
                        for (const auto &poArray : dim->GetUsingArrays())
                        {
                            if (poArray != this)
                                oSetArrays.insert(poArray);
                        }
                    }
                }
            }
    
            bool bOK = true;
            for (auto *poArray : oSetArrays)
            {
                const auto &apoOtherDims = poArray->GetDimensions();
                std::vector<GUInt64> anOtherArrayNewDimSizes(
                    poArray->GetDimensionCount());
                for (size_t i = 0; i < anOtherArrayNewDimSizes.size(); ++i)
                {
                    auto oIter = oMapNewSize.find(apoOtherDims[i].get());
                    if (oIter != oMapNewSize.end())
                        anOtherArrayNewDimSizes[i] = oIter->second;
                    else
                        anOtherArrayNewDimSizes[i] = apoOtherDims[i]->GetSize();
                }
                if (!poArray->Resize(anOtherArrayNewDimSizes,
                                     /*bResizeOtherArrays=*/false))
                {
                    bOK = false;
                    break;
                }
            }
            if (!bOK)
            {
                CPLError(CE_Failure, CPLE_AppDefined,
                         "Resizing of another array referencing the same dimension "
                         "as one modified on the current array failed. All arrays "
                         "referencing that dimension will be invalidated.");
                Invalidate();
                for (auto *poArray : oSetArrays)
                {
                    poArray->Invalidate();
                }
            }
    
            return bOK;
        };
    
        // Decrease slowest varying dimension
        if (anGrownDimIdx.empty() && anDecreasedDimIdx.size() == 1 &&
            anDecreasedDimIdx[0] == 0)
        {
            CPLAssert(m_nTotalSize % dims[0]->GetSize() == 0);
            const size_t nNewTotalSize = static_cast<size_t>(
                (m_nTotalSize / dims[0]->GetSize()) * anNewDimSizes[0]);
            if (m_oType.NeedsFreeDynamicMemory())
            {
                GByte *pabyPtr = m_pabyArray + nNewTotalSize;
                GByte *pabyEnd = m_pabyArray + m_nTotalSize;
                const auto nDTSize(m_oType.GetSize());
                while (pabyPtr < pabyEnd)
                {
                    m_oType.FreeDynamicMemory(pabyPtr);
                    pabyPtr += nDTSize;
                }
            }
            // shrinking... cannot fail, and even if it does, that's ok
            GByte *pabyArray = static_cast<GByte *>(
                VSI_REALLOC_VERBOSE(m_pabyArray, nNewTotalSize));
            if (pabyArray)
                m_pabyArray = pabyArray;
            m_nTotalSize = nNewTotalSize;
    
            if (bResizeOtherArrays)
            {
                if (!ResizeOtherArrays())
                    return false;
    
                auto dim = std::dynamic_pointer_cast<MEMDimension>(dims[0]);
                if (dim)
                {
                    dim->SetSize(anNewDimSizes[0]);
                }
                else
                {
                    CPLAssert(false);
                }
            }
            return true;
        }
    
        // Increase slowest varying dimension
        if (anDecreasedDimIdx.empty() && anGrownDimIdx.size() == 1 &&
            anGrownDimIdx[0] == 0)
        {
            CPLAssert(m_nTotalSize % dims[0]->GetSize() == 0);
            GUInt64 nNewTotalSize64 = m_nTotalSize / dims[0]->GetSize();
            if (nNewTotalSize64 >
                std::numeric_limits<GUInt64>::max() / anNewDimSizes[0])
            {
                CPLError(CE_Failure, CPLE_OutOfMemory, "Too big allocation");
                return false;
            }
            nNewTotalSize64 *= anNewDimSizes[0];
            // We restrict the size of the allocation so that all elements can be
            // indexed by GPtrDiff_t
            if (nNewTotalSize64 >
                static_cast<size_t>(std::numeric_limits<GPtrDiff_t>::max()))
            {
                CPLError(CE_Failure, CPLE_OutOfMemory, "Too big allocation");
                return false;
            }
            const size_t nNewTotalSize = static_cast<size_t>(nNewTotalSize64);
            GByte *pabyArray = static_cast<GByte *>(
                VSI_REALLOC_VERBOSE(m_pabyArray, nNewTotalSize));
            if (!pabyArray)
                return false;
            memset(pabyArray + m_nTotalSize, 0, nNewTotalSize - m_nTotalSize);
            m_pabyArray = pabyArray;
            m_nTotalSize = nNewTotalSize;
    
            if (bResizeOtherArrays)
            {
                if (!ResizeOtherArrays())
                    return false;
    
                auto dim = std::dynamic_pointer_cast<MEMDimension>(dims[0]);
                if (dim)
                {
                    dim->SetSize(anNewDimSizes[0]);
                }
                else
                {
                    CPLAssert(false);
                }
            }
            return true;
        }
    
        // General case where we modify other dimensions that the first one.
    
        // Create dummy dimensions at the new sizes
        std::vector<std::shared_ptr<GDALDimension>> aoNewDims;
        for (size_t i = 0; i < nDimCount; ++i)
        {
            aoNewDims.emplace_back(std::make_shared<MEMDimension>(
                std::string(), dims[i]->GetName(), std::string(), std::string(),
                anNewDimSizes[i]));
        }
    
        // Create a temporary array
        auto poTempMDArray =
            Create(std::string(), std::string(), aoNewDims, GetDataType());
        if (!poTempMDArray->Init())
            return false;
        std::vector<GUInt64> arrayStartIdx(nDimCount);
        std::vector<size_t> count(nDimCount);
        std::vector<GInt64> arrayStep(nDimCount, 1);
        std::vector<GPtrDiff_t> bufferStride(nDimCount);
        for (size_t i = nDimCount; i > 0;)
        {
            --i;
            if (i == nDimCount - 1)
                bufferStride[i] = 1;
            else
            {
                bufferStride[i] = static_cast<GPtrDiff_t>(bufferStride[i + 1] *
                                                          dims[i + 1]->GetSize());
            }
            const auto nCount = std::min(anNewDimSizes[i], dims[i]->GetSize());
            count[i] = static_cast<size_t>(nCount);
        }
        // Copy the current content into the array with the new layout
        if (!poTempMDArray->Write(arrayStartIdx.data(), count.data(),
                                  arrayStep.data(), bufferStride.data(),
                                  GetDataType(), m_pabyArray))
        {
            return false;
        }
    
        // Move content of the temporary array into the current array, and
        // invalidate the temporary array
        FreeArray();
        m_bOwnArray = true;
        m_pabyArray = poTempMDArray->m_pabyArray;
        m_nTotalSize = poTempMDArray->m_nTotalSize;
        m_anStrides = poTempMDArray->m_anStrides;
    
        poTempMDArray->m_bOwnArray = false;
        poTempMDArray->m_pabyArray = nullptr;
        poTempMDArray->m_nTotalSize = 0;
    
        if (bResizeOtherArrays && !ResizeOtherArrays())
            return false;
    
        // Update dimension size
        for (size_t i = 0; i < nDimCount; ++i)
        {
            if (anNewDimSizes[i] != dims[i]->GetSize())
            {
                auto dim = std::dynamic_pointer_cast<MEMDimension>(dims[i]);
                if (dim)
                {
                    dim->SetSize(anNewDimSizes[i]);
                }
                else
                {
                    CPLAssert(false);
                }
            }
        }
    
        return true;
    }
    
    /************************************************************************/
    /*                               Rename()                               */
    /************************************************************************/
    
    bool MEMMDArray::Rename(const std::string &osNewName)
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
        if (osNewName.empty())
        {
            CPLError(CE_Failure, CPLE_NotSupported, "Empty name not supported");
            return false;
        }
    
        if (auto poParentGroup =
                std::dynamic_pointer_cast<MEMGroup>(m_poGroupWeak.lock()))
        {
            if (!poParentGroup->RenameArray(m_osName, osNewName))
            {
                return false;
            }
        }
    
        BaseRename(osNewName);
    
        return true;
    }
    
    /************************************************************************/
    /*                      NotifyChildrenOfRenaming()                      */
    /************************************************************************/
    
    void MEMMDArray::NotifyChildrenOfRenaming()
    {
        for (const auto &oIter : m_oMapAttributes)
            oIter.second->ParentRenamed(m_osFullName);
    }
    
    /************************************************************************/
    /*                      NotifyChildrenOfDeletion()                      */
    /************************************************************************/
    
    void MEMMDArray::NotifyChildrenOfDeletion()
    {
        for (const auto &oIter : m_oMapAttributes)
            oIter.second->ParentDeleted();
    }
    
    /************************************************************************/
    /*                          BuildDimensions()                           */
    /************************************************************************/
    
    static std::vector<std::shared_ptr<GDALDimension>>
    BuildDimensions(const std::vector<GUInt64> &anDimensions)
    {
        std::vector<std::shared_ptr<GDALDimension>> res;
        for (size_t i = 0; i < anDimensions.size(); i++)
        {
            res.emplace_back(std::make_shared<GDALDimensionWeakIndexingVar>(
                std::string(), CPLSPrintf("dim%u", static_cast<unsigned>(i)),
                std::string(), std::string(), anDimensions[i]));
        }
        return res;
    }
    
    /************************************************************************/
    /*                            MEMAttribute()                            */
    /************************************************************************/
    
    MEMAttribute::MEMAttribute(const std::string &osParentName,
                               const std::string &osName,
                               const std::vector<GUInt64> &anDimensions,
                               const GDALExtendedDataType &oType)
        : GDALAbstractMDArray(osParentName, osName),
          MEMAbstractMDArray(osParentName, osName, BuildDimensions(anDimensions),
                             oType),
          GDALAttribute(osParentName, osName)
    {
    }
    
    /************************************************************************/
    /*                        MEMAttribute::Create()                        */
    /************************************************************************/
    
    std::shared_ptr<MEMAttribute>
    MEMAttribute::Create(const std::string &osParentName, const std::string &osName,
                         const std::vector<GUInt64> &anDimensions,
                         const GDALExtendedDataType &oType)
    {
        auto attr(std::shared_ptr<MEMAttribute>(
            new MEMAttribute(osParentName, osName, anDimensions, oType)));
        attr->SetSelf(attr);
        if (!attr->Init())
            return nullptr;
        return attr;
    }
    
    /************************************************************************/
    /*                        MEMAttribute::Create()                        */
    /************************************************************************/
    
    std::shared_ptr<MEMAttribute> MEMAttribute::Create(
        const std::shared_ptr<MEMGroup> &poParentGroup, const std::string &osName,
        const std::vector<GUInt64> &anDimensions, const GDALExtendedDataType &oType)
    {
        const std::string osParentName =
            (poParentGroup && poParentGroup->GetName().empty())
                ?
                // Case of the ZarrAttributeGroup::m_oGroup fake group
                poParentGroup->GetFullName()
                : ((poParentGroup == nullptr || poParentGroup->GetFullName() == "/"
                        ? "/"
                        : poParentGroup->GetFullName() + "/") +
                   "_GLOBAL_");
        auto attr(Create(osParentName, osName, anDimensions, oType));
        if (!attr)
            return nullptr;
        attr->m_poParent = poParentGroup;
        return attr;
    }
    
    /************************************************************************/
    /*                        MEMAttribute::Create()                        */
    /************************************************************************/
    
    std::shared_ptr<MEMAttribute> MEMAttribute::Create(
        const std::shared_ptr<MEMMDArray> &poParentArray, const std::string &osName,
        const std::vector<GUInt64> &anDimensions, const GDALExtendedDataType &oType)
    {
        auto attr(
            Create(poParentArray->GetFullName(), osName, anDimensions, oType));
        if (!attr)
            return nullptr;
        attr->m_poParent = poParentArray;
        return attr;
    }
    
    /************************************************************************/
    /*                               Rename()                               */
    /************************************************************************/
    
    bool MEMAttribute::Rename(const std::string &osNewName)
    {
        if (!CheckValidAndErrorOutIfNot())
            return false;
        if (osNewName.empty())
        {
            CPLError(CE_Failure, CPLE_NotSupported, "Empty name not supported");
            return false;
        }
    
        if (auto poParent = m_poParent.lock())
        {
            if (!poParent->RenameAttribute(m_osName, osNewName))
            {
                return false;
            }
        }
    
        BaseRename(osNewName);
    
        m_bModified = true;
    
        return true;
    }
    
    /************************************************************************/
    /*                            MEMDimension()                            */
    /************************************************************************/
    
    MEMDimension::MEMDimension(const std::string &osParentName,
                               const std::string &osName, const std::string &osType,
                               const std::string &osDirection, GUInt64 nSize)
        : GDALDimensionWeakIndexingVar(osParentName, osName, osType, osDirection,
                                       nSize)
    {
    }
    
    /************************************************************************/
    /*                         RegisterUsingArray()                         */
    /************************************************************************/
    
    void MEMDimension::RegisterUsingArray(MEMMDArray *poArray)
    {
        m_oSetArrays.insert(poArray);
    }
    
    /************************************************************************/
    /*                        UnRegisterUsingArray()                        */
    /************************************************************************/
    
    void MEMDimension::UnRegisterUsingArray(MEMMDArray *poArray)
    {
        m_oSetArrays.erase(poArray);
    }
    
    /************************************************************************/
    /*                               Create()                               */
    /************************************************************************/
    
    /* static */
    std::shared_ptr<MEMDimension>
    MEMDimension::Create(const std::shared_ptr<MEMGroup> &poParentGroup,
                         const std::string &osName, const std::string &osType,
                         const std::string &osDirection, GUInt64 nSize)
    {
        auto newDim(std::make_shared<MEMDimension>(
            poParentGroup->GetFullName(), osName, osType, osDirection, nSize));
        newDim->m_poParentGroup = poParentGroup;
        return newDim;
    }
    
    /************************************************************************/
    /*                          CreateDimension()                           */
    /************************************************************************/
    
    std::shared_ptr<GDALDimension>
    MEMGroup::CreateDimension(const std::string &osName, const std::string &osType,
                              const std::string &osDirection, GUInt64 nSize,
                              CSLConstList)
    {
        if (osName.empty())
        {
            CPLError(CE_Failure, CPLE_NotSupported,
                     "Empty dimension name not supported");
            return nullptr;
        }
        if (m_oMapDimensions.find(osName) != m_oMapDimensions.end())
        {
            CPLError(CE_Failure, CPLE_AppDefined,
                     "A dimension with same name already exists");
            return nullptr;
        }
        auto newDim(MEMDimension::Create(
            std::dynamic_pointer_cast<MEMGroup>(m_pSelf.lock()), osName, osType,
            osDirection, nSize));
        m_oMapDimensions[osName] = newDim;
        return newDim;
    }
    
    /************************************************************************/
    /*                               Rename()                               */
    /************************************************************************/
    
    bool MEMDimension::Rename(const std::string &osNewName)
    {
        if (osNewName.empty())
        {
            CPLError(CE_Failure, CPLE_NotSupported, "Empty name not supported");
            return false;
        }
    
        if (auto poParentGroup = m_poParentGroup.lock())
        {
            if (!poParentGroup->RenameDimension(m_osName, osNewName))
            {
                return false;
            }
        }
    
        BaseRename(osNewName);
    
        return true;
    }
    
    /************************************************************************/
    /*                       CreateMultiDimensional()                       */
    /************************************************************************/
    
    GDALDataset *
    MEMDataset::CreateMultiDimensional(const char *pszFilename,
                                       CSLConstList /*papszRootGroupOptions*/,
                                       CSLConstList /*papszOptions*/)
    {
        auto poDS = new MEMDataset();
    
        poDS->SetDescription(pszFilename);
        auto poRootGroup = MEMGroup::Create(std::string(), nullptr);
        poDS->m_poPrivate->m_poRootGroup = poRootGroup;
    
        return poDS;
    }
    
    /************************************************************************/
    /*                            GetRootGroup()                            */
    /************************************************************************/
    
    std::shared_ptr<GDALGroup> MEMDataset::GetRootGroup() const
    {
        return m_poPrivate->m_poRootGroup;
    }
    
    /************************************************************************/
    /*                         MEMDatasetIdentify()                         */
    /************************************************************************/
    
    static int MEMDatasetIdentify(GDALOpenInfo *poOpenInfo)
    {
        return (STARTS_WITH(poOpenInfo->pszFilename, "MEM:::") &&
                poOpenInfo->fpL == nullptr);
    }
    
    /************************************************************************/
    /*                          MEMDatasetDelete()                          */
    /************************************************************************/
    
    static CPLErr MEMDatasetDelete(const char * /* fileName */)
    {
        /* Null implementation, so that people can Delete("MEM:::") */
        return CE_None;
    }
    
    /************************************************************************/
    /*                            CreateLayer()                             */
    /************************************************************************/
    
    OGRMemLayer *MEMDataset::CreateLayer(const OGRFeatureDefn &oDefn,
                                         CSLConstList papszOptions)
    {
        auto poLayer = std::make_unique<OGRMemLayer>(oDefn);
    
        if (CPLFetchBool(papszOptions, "ADVERTIZE_UTF8", false))
            poLayer->SetAdvertizeUTF8(true);
    
        poLayer->SetDataset(this);
        poLayer->SetFIDColumn(CSLFetchNameValueDef(papszOptions, "FID", ""));
    
        // Add layer to data source layer list.
        m_apoLayers.emplace_back(std::move(poLayer));
        return m_apoLayers.back().get();
    }
    
    /************************************************************************/
    /*                            ICreateLayer()                            */
    /************************************************************************/
    
    OGRLayer *MEMDataset::ICreateLayer(const char *pszLayerName,
                                       const OGRGeomFieldDefn *poGeomFieldDefn,
                                       CSLConstList papszOptions)
    {
        // Create the layer object.
    
        const auto eType = poGeomFieldDefn ? poGeomFieldDefn->GetType() : wkbNone;
        const auto poSRSIn =
            poGeomFieldDefn ? poGeomFieldDefn->GetSpatialRef() : nullptr;
    
        OGRSpatialReference *poSRS = nullptr;
        if (poSRSIn)
        {
            poSRS = poSRSIn->Clone();
            poSRS->SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER);
        }
        auto poLayer = std::make_unique<OGRMemLayer>(pszLayerName, poSRS, eType);
        if (poSRS)
        {
            poSRS->Release();
        }
    
        if (CPLFetchBool(papszOptions, "ADVERTIZE_UTF8", false))
            poLayer->SetAdvertizeUTF8(true);
    
        poLayer->SetDataset(this);
        poLayer->SetFIDColumn(CSLFetchNameValueDef(papszOptions, "FID", ""));
    
        // Add layer to data source layer list.
        m_apoLayers.emplace_back(std::move(poLayer));
        return m_apoLayers.back().get();
    }
    
    /************************************************************************/
    /*                            DeleteLayer()                             */
    /************************************************************************/
    
    OGRErr MEMDataset::DeleteLayer(int iLayer)
    
    {
        if (iLayer >= 0 && iLayer < static_cast<int>(m_apoLayers.size()))
        {
            m_apoLayers.erase(m_apoLayers.begin() + iLayer);
            return OGRERR_NONE;
        }
    
        return OGRERR_FAILURE;
    }
    
    /************************************************************************/
    /*                           TestCapability()                           */
    /************************************************************************/
    
    int MEMDataset::TestCapability(const char *pszCap) const
    
    {
        if (EQUAL(pszCap, ODsCCreateLayer) || EQUAL(pszCap, ODsCDeleteLayer) ||
            EQUAL(pszCap, ODsCCreateGeomFieldAfterCreateLayer) ||
            EQUAL(pszCap, ODsCCurveGeometries) ||
            EQUAL(pszCap, ODsCMeasuredGeometries) ||
            EQUAL(pszCap, ODsCZGeometries) || EQUAL(pszCap, ODsCRandomLayerWrite) ||
            EQUAL(pszCap, ODsCAddFieldDomain) ||
            EQUAL(pszCap, ODsCDeleteFieldDomain) ||
            EQUAL(pszCap, ODsCUpdateFieldDomain) ||
            EQUAL(pszCap, GDsCAddRelationship) ||
            EQUAL(pszCap, GDsCDeleteRelationship) ||
            EQUAL(pszCap, GDsCUpdateRelationship))
        {
            return true;
        }
    
        return GDALDataset::TestCapability(pszCap);
    }
    
    /************************************************************************/
    /*                              GetLayer()                              */
    /************************************************************************/
    
    const OGRLayer *MEMDataset::GetLayer(int iLayer) const
    
    {
        if (iLayer < 0 || iLayer >= static_cast<int>(m_apoLayers.size()))
            return nullptr;
    
        return m_apoLayers[iLayer].get();
    }
    
    /************************************************************************/
    /*                           AddFieldDomain()                           */
    /************************************************************************/
    
    bool MEMDataset::AddFieldDomain(std::unique_ptr<OGRFieldDomain> &&domain,
                                    std::string &failureReason)
    {
        if (GetFieldDomain(domain->GetName()) != nullptr)
        {
            failureReason = "A domain of identical name already exists";
            return false;
        }
        const std::string domainName(domain->GetName());
        m_oMapFieldDomains[domainName] = std::move(domain);
        return true;
    }
    
    /************************************************************************/
    /*                         DeleteFieldDomain()                          */
    /************************************************************************/
    
    bool MEMDataset::DeleteFieldDomain(const std::string &name,
                                       std::string &failureReason)
    {
        const auto iter = m_oMapFieldDomains.find(name);
        if (iter == m_oMapFieldDomains.end())
        {
            failureReason = "Domain does not exist";
            return false;
        }
    
        m_oMapFieldDomains.erase(iter);
    
        for (auto &poLayer : m_apoLayers)
        {
            for (int j = 0; j < poLayer->GetLayerDefn()->GetFieldCount(); ++j)
            {
                OGRLayer *poLayerAsLayer = poLayer.get();
                OGRFieldDefn *poFieldDefn =
                    poLayerAsLayer->GetLayerDefn()->GetFieldDefn(j);
                if (poFieldDefn->GetDomainName() == name)
                {
                    whileUnsealing(poFieldDefn)->SetDomainName(std::string());
                }
            }
        }
    
        return true;
    }
    
    /************************************************************************/
    /*                         UpdateFieldDomain()                          */
    /************************************************************************/
    
    bool MEMDataset::UpdateFieldDomain(std::unique_ptr<OGRFieldDomain> &&domain,
                                       std::string &failureReason)
    {
        const std::string domainName(domain->GetName());
        const auto iter = m_oMapFieldDomains.find(domainName);
        if (iter == m_oMapFieldDomains.end())
        {
            failureReason = "No matching domain found";
            return false;
        }
        m_oMapFieldDomains[domainName] = std::move(domain);
        return true;
    }
    
    /************************************************************************/
    /*                        GetRelationshipNames()                        */
    /************************************************************************/
    
    std::vector<std::string> MEMDataset::GetRelationshipNames(CSLConstList) const
    {
        std::vector<std::string> ret;
        for (const auto &kv : m_poPrivate->m_oMapRelationships)
            ret.push_back(kv.first);
        return ret;
    }
    
    /************************************************************************/
    /*                          GetRelationship()                           */
    /************************************************************************/
    
    const GDALRelationship *
    MEMDataset::GetRelationship(const std::string &name) const
    {
        const auto iter = m_poPrivate->m_oMapRelationships.find(name);
        if (iter != m_poPrivate->m_oMapRelationships.end())
            return iter->second.get();
        return nullptr;
    }
    
    /************************************************************************/
    /*                          AddRelationship()                           */
    /************************************************************************/
    
    bool MEMDataset::AddRelationship(
        std::unique_ptr<GDALRelationship> &&relationship,
        std::string &failureReason)
    {
        const std::string osName(relationship->GetName());
        const auto iter = m_poPrivate->m_oMapRelationships.find(osName);
        if (iter != m_poPrivate->m_oMapRelationships.end())
        {
            failureReason = "A relationship of identical name already exists";
            return false;
        }
        m_poPrivate->m_oMapRelationships[osName] = std::move(relationship);
        return true;
    }
    
    /************************************************************************/
    /*                         DeleteRelationship()                         */
    /************************************************************************/
    
    bool MEMDataset::DeleteRelationship(const std::string &name,
                                        std::string &failureReason)
    {
        const auto iter = m_poPrivate->m_oMapRelationships.find(name);
        if (iter == m_poPrivate->m_oMapRelationships.end())
        {
            failureReason = "No matching relationship found";
            return false;
        }
        m_poPrivate->m_oMapRelationships.erase(iter);
        return true;
    }
    
    /************************************************************************/
    /*                         UpdateRelationship()                         */
    /************************************************************************/
    
    bool MEMDataset::UpdateRelationship(
        std::unique_ptr<GDALRelationship> &&relationship,
        std::string &failureReason)
    {
        const std::string osName(relationship->GetName());
        const auto iter = m_poPrivate->m_oMapRelationships.find(osName);
        if (iter == m_poPrivate->m_oMapRelationships.end())
        {
            failureReason = "No matching relationship found";
            return false;
        }
        iter->second = std::move(relationship);
        return true;
    }
    
    /************************************************************************/
    /*                             ExecuteSQL()                             */
    /************************************************************************/
    
    OGRLayer *MEMDataset::ExecuteSQL(const char *pszStatement,
                                     OGRGeometry *poSpatialFilter,
                                     const char *pszDialect)
    {
        if (EQUAL(pszStatement, "PRAGMA read_only=1"))  // as used by VDV driver
        {
            for (auto &poLayer : m_apoLayers)
                poLayer->SetUpdatable(false);
            return nullptr;
        }
        return GDALDataset::ExecuteSQL(pszStatement, poSpatialFilter, pszDialect);
    }
    
    /************************************************************************/
    /*                          GDALRegister_MEM()                          */
    /************************************************************************/
    
    void GDALRegister_MEM()
    {
        auto poDM = GetGDALDriverManager();
        if (poDM->GetDriverByName("MEM") != nullptr)
            return;
    
        GDALDriver *poDriver = new GDALDriver();
    
        poDriver->SetDescription("MEM");
        poDriver->SetMetadataItem(GDAL_DCAP_RASTER, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_MULTIDIM_RASTER, "YES");
        poDriver->SetMetadataItem(
            GDAL_DMD_LONGNAME,
            "In Memory raster, vector and multidimensional raster");
        poDriver->SetMetadataItem(
            GDAL_DMD_CREATIONDATATYPES,
            "Byte Int8 Int16 UInt16 Int32 UInt32 Int64 UInt64 Float32 Float64 "
            "CInt16 CInt32 CFloat32 CFloat64");
        poDriver->SetMetadataItem(GDAL_DCAP_COORDINATE_EPOCH, "YES");
    
        poDriver->SetMetadataItem(
            GDAL_DMD_CREATIONOPTIONLIST,
            "<CreationOptionList>"
            "   <Option name='INTERLEAVE' type='string-select' default='BAND'>"
            "       <Value>BAND</Value>"
            "       <Value>PIXEL</Value>"
            "   </Option>"
            "  <Option name='NBITS' type='int' description='Bit depth per band'/>"
            "</CreationOptionList>");
    
        poDriver->SetMetadataItem(GDAL_DCAP_VECTOR, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_CREATE_LAYER, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_DELETE_LAYER, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_CREATE_FIELD, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_DELETE_FIELD, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_REORDER_FIELDS, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_CURVE_GEOMETRIES, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_MEASURED_GEOMETRIES, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_Z_GEOMETRIES, "YES");
        poDriver->SetMetadataItem(GDAL_DMD_SUPPORTED_SQL_DIALECTS, "OGRSQL SQLITE");
    
        poDriver->SetMetadataItem(GDAL_DCAP_RELATIONSHIPS, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_CREATE_RELATIONSHIP, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_DELETE_RELATIONSHIP, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_UPDATE_RELATIONSHIP, "YES");
        poDriver->SetMetadataItem(
            GDAL_DMD_RELATIONSHIP_FLAGS,
            "OneToOne OneToMany ManyToOne ManyToMany Composite Association "
            "Aggregation ForwardPathLabel MultipleFieldKeys BackwardPathLabel");
    
        poDriver->SetMetadataItem(
            GDAL_DMD_CREATIONFIELDDATATYPES,
            "Integer Integer64 Real String Date DateTime Time IntegerList "
            "Integer64List RealList StringList Binary");
        poDriver->SetMetadataItem(GDAL_DMD_CREATIONFIELDDATASUBTYPES,
                                  "Boolean Int16 Float32 JSON UUID");
        poDriver->SetMetadataItem(GDAL_DMD_CREATION_FIELD_DEFN_FLAGS,
                                  "WidthPrecision Nullable Default Unique "
                                  "Comment AlternativeName Domain");
        poDriver->SetMetadataItem(GDAL_DMD_ALTER_FIELD_DEFN_FLAGS,
                                  "Name Type WidthPrecision Nullable Default "
                                  "Unique Domain AlternativeName Comment");
    
        poDriver->SetMetadataItem(
            GDAL_DS_LAYER_CREATIONOPTIONLIST,
            "<LayerCreationOptionList>"
            "  <Option name='ADVERTIZE_UTF8' type='boolean' description='Whether "
            "the layer will contain UTF-8 strings' default='NO'/>"
            "  <Option name='FID' type='string' description="
            "'Name of the FID column to create' default='' />"
            "</LayerCreationOptionList>");
    
        poDriver->SetMetadataItem(GDAL_DCAP_COORDINATE_EPOCH, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_MULTIPLE_VECTOR_LAYERS, "YES");
    
        poDriver->SetMetadataItem(GDAL_DCAP_FIELD_DOMAINS, "YES");
        poDriver->SetMetadataItem(GDAL_DMD_CREATION_FIELD_DOMAIN_TYPES,
                                  "Coded Range Glob");
    
        poDriver->SetMetadataItem(GDAL_DMD_ALTER_GEOM_FIELD_DEFN_FLAGS,
                                  "Name Type Nullable SRS CoordinateEpoch");
        poDriver->SetMetadataItem(GDAL_DCAP_UPSERT, "YES");
    
        // Define GDAL_NO_OPEN_FOR_MEM_DRIVER macro to undefine Open() method for
        // MEM driver.  Otherwise, bad user input can trigger easily a GDAL crash
        // as random pointers can be passed as a string.  All code in GDAL tree
        // using the MEM driver use the Create() method only, so Open() is not
        // needed, except for esoteric uses.
    #ifndef GDAL_NO_OPEN_FOR_MEM_DRIVER
        poDriver->pfnOpen = MEMDataset::Open;
        poDriver->pfnIdentify = MEMDatasetIdentify;
    #endif
        poDriver->pfnCreate = MEMDataset::CreateBase;
        poDriver->pfnCreateMultiDimensional = MEMDataset::CreateMultiDimensional;
        poDriver->pfnDelete = MEMDatasetDelete;
    
        poDM->RegisterDriver(poDriver);
    }
    
    ```


??? example "mem/memdataset.h"

    <span class="badge badge-cpp">Drivers (gdal/frmts/mem)</span> **Caminho:** `gdal/frmts/mem/memdataset.h`

    ```cpp
    /******************************************************************************
     *
     * Project:  Memory Array Translator
     * Purpose:  Declaration of MEMDataset, and MEMRasterBand.
     * Author:   Frank Warmerdam, warmerdam@pobox.com
     *
     ******************************************************************************
     * Copyright (c) 2000, Frank Warmerdam
     *
     * SPDX-License-Identifier: MIT
     ****************************************************************************/
    
    #ifndef MEMDATASET_H_INCLUDED
    #define MEMDATASET_H_INCLUDED
    
    #include "gdal_pam.h"
    #include "gdal_priv.h"
    #include "gdal_rat.h"
    #include "ogr_feature.h"
    #include "ogrsf_frmts.h"
    
    #include <map>
    #include <memory>
    
    CPL_C_START
    
    void CPL_DLL GDALRegister_MEM();
    
    /* Caution: if changing this prototype, also change in
       swig/include/gdal_python.i where it is redefined */
    GDALRasterBandH CPL_DLL MEMCreateRasterBand(GDALDataset *, int, GByte *,
                                                GDALDataType, int, int, int);
    GDALRasterBandH CPL_DLL MEMCreateRasterBandEx(GDALDataset *, int, GByte *,
                                                  GDALDataType, GSpacing, GSpacing,
                                                  int);
    CPL_C_END
    
    /************************************************************************/
    /*                              MEMDataset                              */
    /************************************************************************/
    
    class MEMRasterBand;
    class OGRMemLayer;
    
    class CPL_DLL MEMDataset CPL_NON_FINAL : public GDALDataset
    {
        CPL_DISALLOW_COPY_ASSIGN(MEMDataset)
    
        friend class MEMRasterBand;
    
        int bGeoTransformSet;
        GDALGeoTransform m_gt{};
    
        OGRSpatialReference m_oSRS{};
    
        std::vector<gdal::GCP> m_aoGCPs{};
        OGRSpatialReference m_oGCPSRS{};
    
        using GDALDatasetRefCountedPtr =
            std::unique_ptr<GDALDataset, GDALDatasetUniquePtrReleaser>;
    
        std::vector<GDALDatasetRefCountedPtr> m_apoOverviewDS{};
    
        struct Private;
        std::unique_ptr<Private> m_poPrivate;
    
        std::vector<std::unique_ptr<OGRMemLayer>> m_apoLayers{};
    
    #if 0
      protected:
        virtual int                 EnterReadWrite(GDALRWFlag eRWFlag);
        virtual void                LeaveReadWrite();
    #endif
    
        friend void GDALRegister_MEM();
    
        // cppcheck-suppress unusedPrivateFunction
        static GDALDataset *CreateBase(const char *pszFilename, int nXSize,
                                       int nYSize, int nBands, GDALDataType eType,
                                       CSLConstList papszParamList);
    
      protected:
        bool CanBeCloned(int nScopeFlags, bool bCanShareState) const override;
    
        std::unique_ptr<GDALDataset> Clone(int nScopeFlags,
                                           bool bCanShareState) const override;
    
      public:
        MEMDataset();
        ~MEMDataset() override;
    
        CPLErr Close(GDALProgressFunc = nullptr, void * = nullptr) override;
    
        const OGRSpatialReference *GetSpatialRef() const override;
        const OGRSpatialReference *GetSpatialRefRasterOnly() const override;
        CPLErr SetSpatialRef(const OGRSpatialReference *poSRS) override;
    
        CPLErr GetGeoTransform(GDALGeoTransform &gt) const override;
        CPLErr SetGeoTransform(const GDALGeoTransform &gt) override;
    
        void *GetInternalHandle(const char *) override;
    
        int GetGCPCount() override;
        const OGRSpatialReference *GetGCPSpatialRef() const override;
        const GDAL_GCP *GetGCPs() override;
        CPLErr SetGCPs(int nGCPCount, const GDAL_GCP *pasGCPList,
                       const OGRSpatialReference *poSRS) override;
        virtual CPLErr AddBand(GDALDataType eType,
                               CSLConstList papszOptions = nullptr) override;
        CPLErr IRasterIO(GDALRWFlag eRWFlag, int nXOff, int nYOff, int nXSize,
                         int nYSize, void *pData, int nBufXSize, int nBufYSize,
                         GDALDataType eBufType, int nBandCount,
                         BANDMAP_TYPE panBandMap, GSpacing nPixelSpaceBuf,
                         GSpacing nLineSpaceBuf, GSpacing nBandSpaceBuf,
                         GDALRasterIOExtraArg *psExtraArg) override;
        CPLErr IBuildOverviews(const char *pszResampling, int nOverviews,
                               const int *panOverviewList, int nListBands,
                               const int *panBandList, GDALProgressFunc pfnProgress,
                               void *pProgressData,
                               CSLConstList papszOptions) override;
    
        CPLErr CreateMaskBand(int nFlagsIn) override;
    
        std::shared_ptr<GDALGroup> GetRootGroup() const override;
    
        void AddMEMBand(GDALRasterBandH hMEMBand);
    
        static GDALDataset *Open(GDALOpenInfo *);
        static MEMDataset *Create(const char *pszFilename, int nXSize, int nYSize,
                                  int nBands, GDALDataType eType,
                                  CSLConstList papszParamList);
        static GDALDataset *
        CreateMultiDimensional(const char *pszFilename,
                               CSLConstList papszRootGroupOptions,
                               CSLConstList papszOptions);
    
        // Vector capabilities
    
        int GetLayerCount() const override
        {
            return static_cast<int>(m_apoLayers.size());
        }
    
        const OGRLayer *GetLayer(int) const override;
    
        using GDALDataset::CreateLayer;
    
        OGRMemLayer *CreateLayer(const OGRFeatureDefn &oDefn,
                                 CSLConstList papszOptions);
    
        OGRLayer *ICreateLayer(const char *pszName,
                               const OGRGeomFieldDefn *poGeomFieldDefn,
                               CSLConstList papszOptions) override;
        OGRErr DeleteLayer(int iLayer) override;
    
        int TestCapability(const char *) const override;
    
        OGRLayer *ExecuteSQL(const char *pszStatement, OGRGeometry *poSpatialFilter,
                             const char *pszDialect) override;
    
        bool AddFieldDomain(std::unique_ptr<OGRFieldDomain> &&domain,
                            std::string &failureReason) override;
    
        bool DeleteFieldDomain(const std::string &name,
                               std::string &failureReason) override;
    
        bool UpdateFieldDomain(std::unique_ptr<OGRFieldDomain> &&domain,
                               std::string &failureReason) override;
    
        std::vector<std::string>
        GetRelationshipNames(CSLConstList papszOptions = nullptr) const override;
    
        const GDALRelationship *
        GetRelationship(const std::string &name) const override;
    
        bool AddRelationship(std::unique_ptr<GDALRelationship> &&relationship,
                             std::string &failureReason) override;
    
        bool DeleteRelationship(const std::string &name,
                                std::string &failureReason) override;
    
        bool UpdateRelationship(std::unique_ptr<GDALRelationship> &&relationship,
                                std::string &failureReason) override;
    };
    
    /************************************************************************/
    /*                            MEMRasterBand                             */
    /************************************************************************/
    
    class CPL_DLL MEMRasterBand CPL_NON_FINAL : public GDALPamRasterBand
    {
      private:
        CPL_DISALLOW_COPY_ASSIGN(MEMRasterBand)
    
      protected:
        friend class MEMDataset;
    
        GByte *pabyData;
        GSpacing nPixelOffset;
        GSpacing nLineOffset;
        int bOwnData;
    
        bool m_bIsMask = false;
    
        MEMRasterBand(GByte *pabyDataIn, GDALDataType eTypeIn, int nXSizeIn,
                      int nYSizeIn, bool bOwnDataIn);
    
      public:
        MEMRasterBand(GDALDataset *poDS, int nBand, GByte *pabyData,
                      GDALDataType eType, GSpacing nPixelOffset,
                      GSpacing nLineOffset, int bAssumeOwnership,
                      const char *pszPixelType = nullptr);
        ~MEMRasterBand() override;
    
        CPLErr IReadBlock(int, int, void *) override;
        CPLErr IWriteBlock(int, int, void *) override;
        CPLErr IRasterIO(GDALRWFlag eRWFlag, int nXOff, int nYOff, int nXSize,
                         int nYSize, void *pData, int nBufXSize, int nBufYSize,
                         GDALDataType eBufType, GSpacing nPixelSpaceBuf,
                         GSpacing nLineSpaceBuf,
                         GDALRasterIOExtraArg *psExtraArg) override;
    
        int GetOverviewCount() override;
        GDALRasterBand *GetOverview(int) override;
    
        CPLErr CreateMaskBand(int nFlagsIn) override;
        bool IsMaskBand() const override;
    
        // Allow access to MEM driver's private internal memory buffer.
        GByte *GetData() const
        {
            return (pabyData);
        }
    };
    
    /************************************************************************/
    /*                             OGRMemLayer                              */
    /************************************************************************/
    
    class IOGRMemLayerFeatureIterator;
    
    class CPL_DLL OGRMemLayer CPL_NON_FINAL : public OGRLayer
    {
        CPL_DISALLOW_COPY_ASSIGN(OGRMemLayer)
    
        typedef std::map<GIntBig, std::unique_ptr<OGRFeature>> FeatureMap;
        typedef FeatureMap::iterator FeatureIterator;
    
        OGRFeatureDefnRefCountedPtr m_poFeatureDefn{};
    
        GIntBig m_nFeatureCount = 0;
    
        GIntBig m_iNextReadFID = 0;
        GIntBig m_nMaxFeatureCount = 0;  // Max size of papoFeatures.
        OGRFeature **m_papoFeatures = nullptr;
        bool m_bHasHoles = false;
    
        FeatureMap m_oMapFeatures{};
        FeatureIterator m_oMapFeaturesIter{};
    
        GIntBig m_iNextCreateFID = 0;
    
        bool m_bUpdatable = true;
        bool m_bAdvertizeUTF8 = false;
    
        bool m_bUpdated = false;
    
        std::string m_osFIDColumn{};
    
        GDALDataset *m_poDS{};
    
        // Only use it in the lifetime of a function where the list of features
        // doesn't change.
        IOGRMemLayerFeatureIterator *GetIterator();
        void PrepareCreateFeature(OGRFeature *poFeature);
        OGRErr SetFeatureInternal(std::unique_ptr<OGRFeature> poFeature,
                                  GIntBig *pnFID = nullptr);
    
      protected:
        OGRFeature *GetFeatureRef(GIntBig nFeatureId);
    
      public:
        // Clone poSRS if not nullptr
        OGRMemLayer(const char *pszName, const OGRSpatialReference *poSRS,
                    OGRwkbGeometryType eGeomType);
        explicit OGRMemLayer(const OGRFeatureDefn &oFeatureDefn);
        ~OGRMemLayer() override;
    
        void ResetReading() override;
        OGRFeature *GetNextFeature() override;
        OGRErr SetNextByIndex(GIntBig nIndex) override;
    
        OGRFeature *GetFeature(GIntBig nFeatureId) override;
    
        OGRErr ISetFeatureUniqPtr(std::unique_ptr<OGRFeature> poFeature) override;
        OGRErr ISetFeature(OGRFeature *poFeature) override;
    
        OGRErr ICreateFeatureUniqPtr(std::unique_ptr<OGRFeature> poFeature,
                                     GIntBig *pnFID = nullptr) override;
        OGRErr ICreateFeature(OGRFeature *poFeature) override;
    
        OGRErr IUpsertFeature(OGRFeature *poFeature) override;
        OGRErr IUpdateFeature(OGRFeature *poFeature, int nUpdatedFieldsCount,
                              const int *panUpdatedFieldsIdx,
                              int nUpdatedGeomFieldsCount,
                              const int *panUpdatedGeomFieldsIdx,
                              bool bUpdateStyleString) override;
        OGRErr DeleteFeature(GIntBig nFID) override;
    
        using OGRLayer::GetLayerDefn;
    
        const OGRFeatureDefn *GetLayerDefn() const override
        {
            return m_poFeatureDefn.get();
        }
    
        GIntBig GetFeatureCount(int = true) override;
    
        virtual OGRErr CreateField(const OGRFieldDefn *poField,
                                   int bApproxOK = TRUE) override;
        OGRErr DeleteField(int iField) override;
        OGRErr ReorderFields(int *panMap) override;
        virtual OGRErr AlterFieldDefn(int iField, OGRFieldDefn *poNewFieldDefn,
                                      int nFlags) override;
        virtual OGRErr
        AlterGeomFieldDefn(int iGeomField,
                           const OGRGeomFieldDefn *poNewGeomFieldDefn,
                           int nFlagsIn) override;
        virtual OGRErr CreateGeomField(const OGRGeomFieldDefn *poGeomField,
                                       int bApproxOK = TRUE) override;
    
        int TestCapability(const char *) const override;
    
        const char *GetFIDColumn() const override
        {
            return m_osFIDColumn.c_str();
        }
    
        bool IsUpdatable() const
        {
            return m_bUpdatable;
        }
    
        void SetUpdatable(bool bUpdatableIn)
        {
            m_bUpdatable = bUpdatableIn;
        }
    
        void SetAdvertizeUTF8(bool bAdvertizeUTF8In)
        {
            m_bAdvertizeUTF8 = bAdvertizeUTF8In;
        }
    
        void SetFIDColumn(const char *pszFIDColumn)
        {
            m_osFIDColumn = pszFIDColumn;
        }
    
        bool HasBeenUpdated() const
        {
            return m_bUpdated;
        }
    
        void SetUpdated(bool bUpdated)
        {
            m_bUpdated = bUpdated;
        }
    
        GIntBig GetNextReadFID()
        {
            return m_iNextReadFID;
        }
    
        void SetDataset(GDALDataset *poDS)
        {
            m_poDS = poDS;
        }
    
        GDALDataset *GetDataset() override
        {
            return m_poDS;
        }
    };
    
    #endif /* ndef MEMDATASET_H_INCLUDED */
    
    ```


??? example "mem/memmultidim.h"

    <span class="badge badge-cpp">Drivers (gdal/frmts/mem)</span> **Caminho:** `gdal/frmts/mem/memmultidim.h`

    ```cpp
    /******************************************************************************
     *
     * Project:  GDAL
     * Purpose:  MEM driver multidimensional classes
     * Author:   Even Rouault <even dot rouault at spatialys.com>
     *
     ******************************************************************************
     * Copyright (c) 2021, Even Rouault <even dot rouault at spatialys.com>
     *
     * SPDX-License-Identifier: MIT
     ****************************************************************************/
    
    #ifndef MEMMULTIDIM_H
    #define MEMMULTIDIM_H
    
    #include "gdal_priv.h"
    
    #include <set>
    
    // If modifying the below declaration, modify it in gdal_array.i too
    std::shared_ptr<GDALMDArray> CPL_DLL MEMGroupCreateMDArray(
        GDALGroup *poGroup, const std::string &osName,
        const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
        const GDALExtendedDataType &oDataType, void *pData,
        CSLConstList papszOptions);
    
    /************************************************************************/
    /*                          MEMAttributeHolder                          */
    /************************************************************************/
    
    class CPL_DLL MEMAttributeHolder CPL_NON_FINAL
    {
      protected:
        std::map<CPLString, std::shared_ptr<GDALAttribute>> m_oMapAttributes{};
    
      public:
        virtual ~MEMAttributeHolder();
    
        bool RenameAttribute(const std::string &osOldName,
                             const std::string &osNewName);
    };
    
    /************************************************************************/
    /*                               MEMGroup                               */
    /************************************************************************/
    
    class CPL_DLL MEMGroup CPL_NON_FINAL : public GDALGroup,
                                           public MEMAttributeHolder
    {
        friend class MEMMDArray;
    
        std::map<CPLString, std::shared_ptr<GDALGroup>> m_oMapGroups{};
        std::map<CPLString, std::shared_ptr<GDALMDArray>> m_oMapMDArrays{};
        std::map<CPLString, std::shared_ptr<GDALDimension>> m_oMapDimensions{};
        std::weak_ptr<MEMGroup> m_pParent{};
        std::weak_ptr<GDALGroup> m_poRootGroupWeak{};
    
      protected:
        friend class MEMDimension;
        bool RenameDimension(const std::string &osOldName,
                             const std::string &osNewName);
    
        bool RenameArray(const std::string &osOldName,
                         const std::string &osNewName);
    
        void NotifyChildrenOfRenaming() override;
    
        void NotifyChildrenOfDeletion() override;
    
        MEMGroup(const std::string &osParentName, const char *pszName)
            : GDALGroup(osParentName, pszName ? pszName : "")
        {
            if (!osParentName.empty() && !pszName)
                m_osFullName = osParentName;
        }
    
      public:
        static std::shared_ptr<MEMGroup> Create(const std::string &osParentName,
                                                const char *pszName);
    
        void SetFullName(const std::string &osFullName)
        {
            m_osFullName = osFullName;
        }
    
        std::vector<std::string>
        GetMDArrayNames(CSLConstList papszOptions) const override;
        std::shared_ptr<GDALMDArray>
        OpenMDArray(const std::string &osName,
                    CSLConstList papszOptions) const override;
    
        std::vector<std::string>
        GetGroupNames(CSLConstList papszOptions) const override;
        std::shared_ptr<GDALGroup>
        OpenGroup(const std::string &osName,
                  CSLConstList papszOptions) const override;
    
        std::shared_ptr<GDALGroup> CreateGroup(const std::string &osName,
                                               CSLConstList papszOptions) override;
    
        bool DeleteGroup(const std::string &osName,
                         CSLConstList papszOptions) override;
    
        std::shared_ptr<GDALDimension>
        CreateDimension(const std::string &, const std::string &,
                        const std::string &, GUInt64,
                        CSLConstList papszOptions) override;
    
        std::shared_ptr<GDALMDArray> CreateMDArray(
            const std::string &osName,
            const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
            const GDALExtendedDataType &oDataType,
            CSLConstList papszOptions) override;
    
        std::shared_ptr<GDALMDArray> CreateMDArray(
            const std::string &osName,
            const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
            const GDALExtendedDataType &oDataType, void *pData,
            CSLConstList papszOptions);
    
        bool DeleteMDArray(const std::string &osName,
                           CSLConstList papszOptions) override;
    
        std::shared_ptr<GDALAttribute>
        GetAttribute(const std::string &osName) const override;
    
        std::vector<std::shared_ptr<GDALAttribute>>
        GetAttributes(CSLConstList papszOptions) const override;
    
        std::vector<std::shared_ptr<GDALDimension>>
        GetDimensions(CSLConstList papszOptions) const override;
    
        std::shared_ptr<GDALAttribute>
        CreateAttribute(const std::string &osName,
                        const std::vector<GUInt64> &anDimensions,
                        const GDALExtendedDataType &oDataType,
                        CSLConstList papszOptions) override;
    
        bool DeleteAttribute(const std::string &osName,
                             CSLConstList papszOptions) override;
    
        bool Rename(const std::string &osNewName) override;
    };
    
    /************************************************************************/
    /*                          MEMAbstractMDArray                          */
    /************************************************************************/
    
    class CPL_DLL MEMAbstractMDArray : virtual public GDALAbstractMDArray
    {
        std::vector<std::shared_ptr<GDALDimension>> m_aoDims;
    
        struct StackReadWrite
        {
            size_t nIters = 0;
            const GByte *src_ptr = nullptr;
            GByte *dst_ptr = nullptr;
            GPtrDiff_t src_inc_offset = 0;
            GPtrDiff_t dst_inc_offset = 0;
        };
    
        void ReadWrite(bool bIsWrite, const size_t *count,
                       std::vector<StackReadWrite> &stack,
                       const GDALExtendedDataType &srcType,
                       const GDALExtendedDataType &dstType) const;
    
        MEMAbstractMDArray(const MEMAbstractMDArray &) = delete;
        MEMAbstractMDArray &operator=(const MEMAbstractMDArray &) = delete;
    
      protected:
        bool m_bOwnArray = false;
        bool m_bWritable = true;
        bool m_bModified = false;
        GDALExtendedDataType m_oType;
        size_t m_nTotalSize = 0;
        GByte *m_pabyArray{};
        std::vector<GPtrDiff_t> m_anStrides{};
    
        bool
        IRead(const GUInt64 *arrayStartIdx,    // array of size GetDimensionCount()
              const size_t *count,             // array of size GetDimensionCount()
              const GInt64 *arrayStep,         // step in elements
              const GPtrDiff_t *bufferStride,  // stride in elements
              const GDALExtendedDataType &bufferDataType,
              void *pDstBuffer) const override;
    
        bool
        IWrite(const GUInt64 *arrayStartIdx,    // array of size GetDimensionCount()
               const size_t *count,             // array of size GetDimensionCount()
               const GInt64 *arrayStep,         // step in elements
               const GPtrDiff_t *bufferStride,  // stride in elements
               const GDALExtendedDataType &bufferDataType,
               const void *pSrcBuffer) override;
    
        void FreeArray();
    
      public:
        MEMAbstractMDArray(
            const std::string &osParentName, const std::string &osName,
            const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
            const GDALExtendedDataType &oType);
        ~MEMAbstractMDArray() override;
    
        const std::vector<std::shared_ptr<GDALDimension>> &
        GetDimensions() const override
        {
            return m_aoDims;
        }
    
        const GDALExtendedDataType &GetDataType() const override
        {
            return m_oType;
        }
    
        bool
        Init(GByte *pData = nullptr,
             const std::vector<GPtrDiff_t> &anStrides = std::vector<GPtrDiff_t>());
    
        void SetWritable(bool bWritable)
        {
            m_bWritable = bWritable;
        }
    
        bool IsModified() const
        {
            return m_bModified;
        }
    
        void SetModified(bool bModified)
        {
            m_bModified = bModified;
        }
    };
    
    /************************************************************************/
    /*                              MEMMDArray                              */
    /************************************************************************/
    
    #ifdef _MSC_VER
    #pragma warning(push)
    // warning C4250: 'MEMMDArray': inherits
    // 'MEMAbstractMDArray::MEMAbstractMDArray::IRead' via dominance
    #pragma warning(disable : 4250)
    #endif  //_MSC_VER
    
    class CPL_DLL MEMMDArray CPL_NON_FINAL : public MEMAbstractMDArray,
                                             public GDALMDArray,
                                             public MEMAttributeHolder
    {
        std::string m_osUnit{};
        std::shared_ptr<OGRSpatialReference> m_poSRS{};
        GByte *m_pabyNoData = nullptr;
        double m_dfScale = 1.0;
        double m_dfOffset = 0.0;
        bool m_bHasScale = false;
        bool m_bHasOffset = false;
        GDALDataType m_eOffsetStorageType = GDT_Unknown;
        GDALDataType m_eScaleStorageType = GDT_Unknown;
        std::string m_osFilename{};
        std::weak_ptr<GDALGroup> m_poGroupWeak{};
        std::weak_ptr<GDALGroup> m_poRootGroupWeak{};
    
        MEMMDArray(const MEMMDArray &) = delete;
        MEMMDArray &operator=(const MEMMDArray &) = delete;
    
        bool Resize(const std::vector<GUInt64> &anNewDimSizes,
                    bool bResizeOtherArrays);
    
        void NotifyChildrenOfRenaming() override;
    
        void NotifyChildrenOfDeletion() override;
    
      protected:
        MEMMDArray(const std::string &osParentName, const std::string &osName,
                   const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
                   const GDALExtendedDataType &oType);
    
      public:
        // MEMAbstractMDArray::Init() should be called afterwards
        static std::shared_ptr<MEMMDArray>
        Create(const std::string &osParentName, const std::string &osName,
               const std::vector<std::shared_ptr<GDALDimension>> &aoDimensions,
               const GDALExtendedDataType &oType)
        {
            auto array(std::shared_ptr<MEMMDArray>(
                new MEMMDArray(osParentName, osName, aoDimensions, oType)));
            array->SetSelf(array);
            return array;
        }
    
        ~MEMMDArray() override;
    
        void Invalidate()
        {
            m_bValid = false;
        }
    
        bool IsWritable() const override
        {
            return m_bWritable;
        }
    
        const std::string &GetFilename() const override
        {
            return m_osFilename;
        }
    
        void RegisterGroup(const std::weak_ptr<GDALGroup> &group)
        {
            m_poGroupWeak = group;
        }
    
        std::shared_ptr<GDALAttribute>
        GetAttribute(const std::string &osName) const override;
    
        std::vector<std::shared_ptr<GDALAttribute>>
        GetAttributes(CSLConstList papszOptions) const override;
    
        std::shared_ptr<GDALAttribute>
        CreateAttribute(const std::string &osName,
                        const std::vector<GUInt64> &anDimensions,
                        const GDALExtendedDataType &oDataType,
                        CSLConstList papszOptions) override;
    
        bool DeleteAttribute(const std::string &osName,
                             CSLConstList papszOptions) override;
    
        const std::string &GetUnit() const override
        {
            return m_osUnit;
        }
    
        bool SetUnit(const std::string &osUnit) override
        {
            m_osUnit = osUnit;
            return true;
        }
    
        bool SetSpatialRef(const OGRSpatialReference *poSRS) override
        {
            m_poSRS.reset(poSRS ? poSRS->Clone() : nullptr);
            return true;
        }
    
        std::shared_ptr<OGRSpatialReference> GetSpatialRef() const override
        {
            return m_poSRS;
        }
    
        const void *GetRawNoDataValue() const override;
    
        bool SetRawNoDataValue(const void *) override;
    
        double GetOffset(bool *pbHasOffset,
                         GDALDataType *peStorageType) const override
        {
            if (pbHasOffset)
                *pbHasOffset = m_bHasOffset;
            if (peStorageType)
                *peStorageType = m_eOffsetStorageType;
            return m_dfOffset;
        }
    
        double GetScale(bool *pbHasScale,
                        GDALDataType *peStorageType) const override
        {
            if (pbHasScale)
                *pbHasScale = m_bHasScale;
            if (peStorageType)
                *peStorageType = m_eScaleStorageType;
            return m_dfScale;
        }
    
        bool SetOffset(double dfOffset, GDALDataType eStorageType) override
        {
            m_bHasOffset = true;
            m_dfOffset = dfOffset;
            m_eOffsetStorageType = eStorageType;
            return true;
        }
    
        bool SetScale(double dfScale, GDALDataType eStorageType) override
        {
            m_bHasScale = true;
            m_dfScale = dfScale;
            m_eScaleStorageType = eStorageType;
            return true;
        }
    
        std::vector<std::shared_ptr<GDALMDArray>>
        GetCoordinateVariables() const override;
    
        bool Resize(const std::vector<GUInt64> &anNewDimSizes,
                    CSLConstList) override;
    
        bool Rename(const std::string &osNewName) override;
    
        std::shared_ptr<GDALGroup> GetRootGroup() const override
        {
            return m_poRootGroupWeak.lock();
        }
    };
    
    /************************************************************************/
    /*                             MEMAttribute                             */
    /************************************************************************/
    
    class CPL_DLL MEMAttribute CPL_NON_FINAL : public MEMAbstractMDArray,
                                               public GDALAttribute
    {
        std::weak_ptr<MEMAttributeHolder> m_poParent{};
    
      protected:
        MEMAttribute(const std::string &osParentName, const std::string &osName,
                     const std::vector<GUInt64> &anDimensions,
                     const GDALExtendedDataType &oType);
    
      public:
        // May return nullptr as it calls MEMAbstractMDArray::Init() which can
        // fail
        static std::shared_ptr<MEMAttribute>
        Create(const std::string &osParentName, const std::string &osName,
               const std::vector<GUInt64> &anDimensions,
               const GDALExtendedDataType &oType);
    
        static std::shared_ptr<MEMAttribute>
        Create(const std::shared_ptr<MEMGroup> &poParentGroup,
               const std::string &osName, const std::vector<GUInt64> &anDimensions,
               const GDALExtendedDataType &oType);
    
        static std::shared_ptr<MEMAttribute>
        Create(const std::shared_ptr<MEMMDArray> &poParentArray,
               const std::string &osName, const std::vector<GUInt64> &anDimensions,
               const GDALExtendedDataType &oType);
    
        bool Rename(const std::string &osNewName) override;
    };
    
    #ifdef _MSC_VER
    #pragma warning(pop)
    #endif  //_MSC_VER
    
    /************************************************************************/
    /*                             MEMDimension                             */
    /************************************************************************/
    
    class MEMDimension CPL_NON_FINAL : public GDALDimensionWeakIndexingVar
    {
        std::set<MEMMDArray *> m_oSetArrays{};
        std::weak_ptr<MEMGroup> m_poParentGroup{};
    
      public:
        MEMDimension(const std::string &osParentName, const std::string &osName,
                     const std::string &osType, const std::string &osDirection,
                     GUInt64 nSize);
    
        static std::shared_ptr<MEMDimension>
        Create(const std::shared_ptr<MEMGroup> &poParentGroupy,
               const std::string &osName, const std::string &osType,
               const std::string &osDirection, GUInt64 nSize);
    
        void RegisterUsingArray(MEMMDArray *poArray);
        void UnRegisterUsingArray(MEMMDArray *poArray);
    
        const std::set<MEMMDArray *> &GetUsingArrays() const
        {
            return m_oSetArrays;
        }
    
        bool Rename(const std::string &osNewName) override;
    };
    
    #endif  //  MEMMULTIDIM_H
    
    ```


??? example "mem/ogrmemlayer.cpp"

    <span class="badge badge-cpp">Drivers (gdal/frmts/mem)</span> **Caminho:** `gdal/frmts/mem/ogrmemlayer.cpp`

    ```cpp
    /******************************************************************************
     *
     * Project:  OpenGIS Simple Features Reference Implementation
     * Purpose:  Implements OGRMemLayer class.
     * Author:   Frank Warmerdam, warmerdam@pobox.com
     *
     ******************************************************************************
     * Copyright (c) 2003, Frank Warmerdam <warmerdam@pobox.com>
     * Copyright (c) 2009-2013, Even Rouault <even dot rouault at spatialys.com>
     *
     * SPDX-License-Identifier: MIT
     ****************************************************************************/
    
    #include "cpl_port.h"
    #include "memdataset.h"
    
    #include <cstddef>
    #include <cstring>
    #include <algorithm>
    #include <map>
    #include <new>
    #include <utility>
    
    #include "cpl_conv.h"
    #include "cpl_error.h"
    #include "cpl_vsi.h"
    #include "ogr_api.h"
    #include "ogr_core.h"
    #include "ogr_feature.h"
    #include "ogr_geometry.h"
    #include "ogr_p.h"
    #include "ogr_spatialref.h"
    #include "ogrsf_frmts.h"
    
    /************************************************************************/
    /*                     IOGRMemLayerFeatureIterator                      */
    /************************************************************************/
    
    class IOGRMemLayerFeatureIterator
    {
      public:
        virtual ~IOGRMemLayerFeatureIterator();
    
        virtual OGRFeature *Next() = 0;
    };
    
    IOGRMemLayerFeatureIterator::~IOGRMemLayerFeatureIterator() = default;
    
    /************************************************************************/
    /*                            OGRMemLayer()                             */
    /************************************************************************/
    
    OGRMemLayer::OGRMemLayer(const char *pszName,
                             const OGRSpatialReference *poSRSIn,
                             OGRwkbGeometryType eReqType)
        : m_poFeatureDefn(OGRFeatureDefnRefCountedPtr::makeInstance(pszName))
    {
        OGRMemLayer::SetDescription(m_poFeatureDefn->GetName());
        m_poFeatureDefn->SetGeomType(eReqType);
    
        if (eReqType != wkbNone && poSRSIn != nullptr)
        {
            OGRSpatialReference *poSRS = poSRSIn->Clone();
            m_poFeatureDefn->GetGeomFieldDefn(0)->SetSpatialRef(poSRS);
            poSRS->Release();
        }
    
        m_oMapFeaturesIter = m_oMapFeatures.begin();
        m_poFeatureDefn->Seal(/* bSealFields = */ true);
    }
    
    OGRMemLayer::OGRMemLayer(const OGRFeatureDefn &oFeatureDefn)
        : m_poFeatureDefn(oFeatureDefn.Clone())
    {
        OGRMemLayer::SetDescription(m_poFeatureDefn->GetName());
    
        m_oMapFeaturesIter = m_oMapFeatures.begin();
        m_poFeatureDefn->Seal(/* bSealFields = */ true);
    }
    
    /************************************************************************/
    /*                            ~OGRMemLayer()                            */
    /************************************************************************/
    
    OGRMemLayer::~OGRMemLayer()
    
    {
        if (m_nFeaturesRead > 0 && m_poFeatureDefn != nullptr)
        {
            CPLDebug("Mem", CPL_FRMT_GIB " features read on layer '%s'.",
                     m_nFeaturesRead, m_poFeatureDefn->GetName());
        }
    
        if (m_papoFeatures != nullptr)
        {
            for (GIntBig i = 0; i < m_nMaxFeatureCount; i++)
            {
                if (m_papoFeatures[i] != nullptr)
                    delete m_papoFeatures[i];
            }
            CPLFree(m_papoFeatures);
        }
    }
    
    /************************************************************************/
    /*                            ResetReading()                            */
    /************************************************************************/
    
    void OGRMemLayer::ResetReading()
    
    {
        m_iNextReadFID = 0;
        m_oMapFeaturesIter = m_oMapFeatures.begin();
    }
    
    /************************************************************************/
    /*                           GetNextFeature()                           */
    /************************************************************************/
    
    OGRFeature *OGRMemLayer::GetNextFeature()
    
    {
        if (m_iNextReadFID < 0)
            return nullptr;
    
        while (true)
        {
            OGRFeature *poFeature = nullptr;
            if (m_papoFeatures)
            {
                if (m_iNextReadFID >= m_nMaxFeatureCount)
                    return nullptr;
                poFeature = m_papoFeatures[m_iNextReadFID++];
                if (poFeature == nullptr)
                    continue;
            }
            else if (m_oMapFeaturesIter != m_oMapFeatures.end())
            {
                poFeature = m_oMapFeaturesIter->second.get();
                ++m_oMapFeaturesIter;
            }
            else
            {
                break;
            }
    
            if ((m_poFilterGeom == nullptr ||
                 FilterGeometry(poFeature->GetGeomFieldRef(m_iGeomFieldFilter))) &&
                (m_poAttrQuery == nullptr || m_poAttrQuery->Evaluate(poFeature)))
            {
                m_nFeaturesRead++;
                return poFeature->Clone();
            }
        }
    
        return nullptr;
    }
    
    /************************************************************************/
    /*                           SetNextByIndex()                           */
    /************************************************************************/
    
    OGRErr OGRMemLayer::SetNextByIndex(GIntBig nIndex)
    
    {
        if (m_poFilterGeom != nullptr || m_poAttrQuery != nullptr ||
            m_papoFeatures == nullptr || m_bHasHoles)
            return OGRLayer::SetNextByIndex(nIndex);
    
        if (nIndex < 0 || nIndex >= m_nMaxFeatureCount)
        {
            m_iNextReadFID = -1;
            return OGRERR_NON_EXISTING_FEATURE;
        }
    
        m_iNextReadFID = nIndex;
    
        return OGRERR_NONE;
    }
    
    /************************************************************************/
    /*                           GetFeatureRef()                            */
    /************************************************************************/
    
    OGRFeature *OGRMemLayer::GetFeatureRef(GIntBig nFeatureId)
    
    {
        if (nFeatureId < 0)
            return nullptr;
    
        OGRFeature *poFeature = nullptr;
        if (m_papoFeatures != nullptr)
        {
            if (nFeatureId >= m_nMaxFeatureCount)
                return nullptr;
            poFeature = m_papoFeatures[nFeatureId];
        }
        else
        {
            FeatureIterator oIter = m_oMapFeatures.find(nFeatureId);
            if (oIter != m_oMapFeatures.end())
                poFeature = oIter->second.get();
        }
    
        return poFeature;
    }
    
    /************************************************************************/
    /*                             GetFeature()                             */
    /************************************************************************/
    
    OGRFeature *OGRMemLayer::GetFeature(GIntBig nFeatureId)
    
    {
        const OGRFeature *poFeature = GetFeatureRef(nFeatureId);
        return poFeature ? poFeature->Clone() : nullptr;
    }
    
    /************************************************************************/
    /*                            ISetFeature()                             */
    /************************************************************************/
    
    OGRErr OGRMemLayer::ISetFeature(OGRFeature *poFeature)
    
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        if (poFeature == nullptr)
            return OGRERR_FAILURE;
    
        GIntBig nFID = poFeature->GetFID();
        OGRErr eErr = SetFeatureInternal(
            std::unique_ptr<OGRFeature>(poFeature->Clone()), &nFID);
        poFeature->SetFID(nFID);
        return eErr;
    }
    
    /************************************************************************/
    /*                         ISetFeatureUniqPtr()                         */
    /************************************************************************/
    
    OGRErr OGRMemLayer::ISetFeatureUniqPtr(std::unique_ptr<OGRFeature> poFeature)
    
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        if (poFeature == nullptr)
            return OGRERR_FAILURE;
    
        return SetFeatureInternal(std::move(poFeature));
    }
    
    /************************************************************************/
    /*                         SetFeatureInternal()                         */
    /************************************************************************/
    
    OGRErr OGRMemLayer::SetFeatureInternal(std::unique_ptr<OGRFeature> poFeature,
                                           GIntBig *pnFID)
    {
        // If we don't have a FID, find one available
        GIntBig nFID = poFeature->GetFID();
        if (nFID == OGRNullFID)
        {
            if (m_papoFeatures != nullptr)
            {
                while (m_iNextCreateFID < m_nMaxFeatureCount &&
                       m_papoFeatures[m_iNextCreateFID] != nullptr)
                {
                    m_iNextCreateFID++;
                }
            }
            else
            {
                FeatureIterator oIter;
                while ((oIter = m_oMapFeatures.find(m_iNextCreateFID)) !=
                       m_oMapFeatures.end())
                    ++m_iNextCreateFID;
            }
            nFID = m_iNextCreateFID++;
            poFeature->SetFID(nFID);
        }
        else if (nFID < OGRNullFID)
        {
            CPLError(CE_Failure, CPLE_NotSupported,
                     "negative FID are not supported");
            return OGRERR_FAILURE;
        }
        else if (!m_bHasHoles)
        {
            // If the feature does not exist, set m_bHasHoles
            if (m_papoFeatures != nullptr)
            {
                if (nFID >= m_nMaxFeatureCount || m_papoFeatures[nFID] == nullptr)
                {
                    m_bHasHoles = true;
                }
            }
            else
            {
                FeatureIterator oIter = m_oMapFeatures.find(nFID);
                if (oIter == m_oMapFeatures.end())
                    m_bHasHoles = true;
            }
        }
        if (pnFID)
            *pnFID = nFID;
    
        if (m_papoFeatures != nullptr && nFID > 100000 &&
            nFID > m_nMaxFeatureCount + 1000)
        {
            // Convert to map if gap from current max size is too big.
            auto poIter =
                std::unique_ptr<IOGRMemLayerFeatureIterator>(GetIterator());
            try
            {
                OGRFeature *poFeatureIter = nullptr;
                while ((poFeatureIter = poIter->Next()) != nullptr)
                {
                    m_oMapFeatures[poFeatureIter->GetFID()] =
                        std::unique_ptr<OGRFeature>(poFeatureIter);
                }
                CPLFree(m_papoFeatures);
                m_papoFeatures = nullptr;
                m_nMaxFeatureCount = 0;
            }
            catch (const std::bad_alloc &)
            {
                m_oMapFeatures.clear();
                m_oMapFeaturesIter = m_oMapFeatures.end();
                CPLError(CE_Failure, CPLE_OutOfMemory, "Cannot allocate memory");
                return OGRERR_FAILURE;
            }
        }
    
        for (int i = 0; i < m_poFeatureDefn->GetGeomFieldCount(); ++i)
        {
            OGRGeometry *poGeom = poFeature->GetGeomFieldRef(i);
            if (poGeom != nullptr && poGeom->getSpatialReference() == nullptr)
            {
                poGeom->assignSpatialReference(
                    m_poFeatureDefn->GetGeomFieldDefn(i)->GetSpatialRef());
            }
        }
    
        if (m_papoFeatures != nullptr || (m_oMapFeatures.empty() && nFID <= 100000))
        {
            if (nFID >= m_nMaxFeatureCount)
            {
                const GIntBig nNewCount = std::max(
                    m_nMaxFeatureCount + m_nMaxFeatureCount / 3 + 10, nFID + 1);
                if (static_cast<GIntBig>(static_cast<size_t>(sizeof(OGRFeature *)) *
                                         nNewCount) !=
                    static_cast<GIntBig>(sizeof(OGRFeature *)) * nNewCount)
                {
                    CPLError(CE_Failure, CPLE_OutOfMemory,
                             "Cannot allocate array of " CPL_FRMT_GIB " elements",
                             nNewCount);
                    return OGRERR_FAILURE;
                }
    
                OGRFeature **papoNewFeatures =
                    static_cast<OGRFeature **>(VSI_REALLOC_VERBOSE(
                        m_papoFeatures,
                        static_cast<size_t>(sizeof(OGRFeature *) * nNewCount)));
                if (papoNewFeatures == nullptr)
                {
                    return OGRERR_FAILURE;
                }
                m_papoFeatures = papoNewFeatures;
                memset(m_papoFeatures + m_nMaxFeatureCount, 0,
                       sizeof(OGRFeature *) *
                           static_cast<size_t>(nNewCount - m_nMaxFeatureCount));
                m_nMaxFeatureCount = nNewCount;
            }
    
    #ifdef DEBUG
            // Just to please Coverity. Cannot happen.
            if (m_papoFeatures == nullptr)
            {
                return OGRERR_FAILURE;
            }
    #endif
    
            if (m_papoFeatures[nFID] != nullptr)
            {
                delete m_papoFeatures[nFID];
                m_papoFeatures[nFID] = nullptr;
            }
            else
            {
                ++m_nFeatureCount;
            }
    
            m_papoFeatures[nFID] = poFeature.release();
        }
        else
        {
            FeatureIterator oIter = m_oMapFeatures.find(nFID);
            if (oIter != m_oMapFeatures.end())
            {
                oIter->second = std::move(poFeature);
            }
            else
            {
                try
                {
                    m_oMapFeatures[nFID] = std::move(poFeature);
                    m_oMapFeaturesIter = m_oMapFeatures.end();
                    m_nFeatureCount++;
                }
                catch (const std::bad_alloc &)
                {
                    CPLError(CE_Failure, CPLE_OutOfMemory,
                             "Cannot allocate memory");
                    return OGRERR_FAILURE;
                }
            }
        }
    
        m_bUpdated = true;
    
        return OGRERR_NONE;
    }
    
    /************************************************************************/
    /*                        PrepareCreateFeature()                        */
    /************************************************************************/
    
    void OGRMemLayer::PrepareCreateFeature(OGRFeature *poFeature)
    {
        if (poFeature->GetFID() != OGRNullFID &&
            poFeature->GetFID() != m_iNextCreateFID)
            m_bHasHoles = true;
    
        // If the feature has already a FID and that a feature with the same
        // FID is already registered in the layer, then unset our FID.
        if (poFeature->GetFID() >= 0)
        {
            if (m_papoFeatures != nullptr)
            {
                if (poFeature->GetFID() < m_nMaxFeatureCount &&
                    m_papoFeatures[poFeature->GetFID()] != nullptr)
                {
                    poFeature->SetFID(OGRNullFID);
                }
            }
            else
            {
                FeatureIterator oIter = m_oMapFeatures.find(poFeature->GetFID());
                if (oIter != m_oMapFeatures.end())
                    poFeature->SetFID(OGRNullFID);
            }
        }
    }
    
    /************************************************************************/
    /*                           ICreateFeature()                           */
    /************************************************************************/
    
    OGRErr OGRMemLayer::ICreateFeature(OGRFeature *poFeature)
    
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        PrepareCreateFeature(poFeature);
    
        GIntBig nFID = poFeature->GetFID();
        const OGRErr eErr = SetFeatureInternal(
            std::unique_ptr<OGRFeature>(poFeature->Clone()), &nFID);
        poFeature->SetFID(nFID);
        return eErr;
    }
    
    /************************************************************************/
    /*                       ICreateFeatureUniqPtr()                        */
    /************************************************************************/
    
    OGRErr OGRMemLayer::ICreateFeatureUniqPtr(std::unique_ptr<OGRFeature> poFeature,
                                              GIntBig *pnFID)
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        PrepareCreateFeature(poFeature.get());
    
        return SetFeatureInternal(std::move(poFeature), pnFID);
    }
    
    /************************************************************************/
    /*                           UpsertFeature()                            */
    /************************************************************************/
    
    OGRErr OGRMemLayer::IUpsertFeature(OGRFeature *poFeature)
    
    {
        if (!TestCapability(OLCUpsertFeature))
            return OGRERR_FAILURE;
    
        if (GetFeatureRef(poFeature->GetFID()))
        {
            return ISetFeature(poFeature);
        }
        else
        {
            return ICreateFeature(poFeature);
        }
    }
    
    /************************************************************************/
    /*                           UpdateFeature()                            */
    /************************************************************************/
    
    OGRErr OGRMemLayer::IUpdateFeature(OGRFeature *poFeature,
                                       int nUpdatedFieldsCount,
                                       const int *panUpdatedFieldsIdx,
                                       int nUpdatedGeomFieldsCount,
                                       const int *panUpdatedGeomFieldsIdx,
                                       bool bUpdateStyleString)
    
    {
        if (!TestCapability(OLCUpdateFeature))
            return OGRERR_FAILURE;
    
        auto poFeatureRef = GetFeatureRef(poFeature->GetFID());
        if (!poFeatureRef)
            return OGRERR_NON_EXISTING_FEATURE;
    
        for (int i = 0; i < nUpdatedFieldsCount; ++i)
        {
            poFeatureRef->SetField(
                panUpdatedFieldsIdx[i],
                poFeature->GetRawFieldRef(panUpdatedFieldsIdx[i]));
        }
        for (int i = 0; i < nUpdatedGeomFieldsCount; ++i)
        {
            poFeatureRef->SetGeomFieldDirectly(
                panUpdatedGeomFieldsIdx[i],
                poFeature->StealGeometry(panUpdatedGeomFieldsIdx[i]));
        }
        if (bUpdateStyleString)
        {
            poFeatureRef->SetStyleString(poFeature->GetStyleString());
        }
    
        m_bUpdated = true;
    
        return OGRERR_NONE;
    }
    
    /************************************************************************/
    /*                           DeleteFeature()                            */
    /************************************************************************/
    
    OGRErr OGRMemLayer::DeleteFeature(GIntBig nFID)
    
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        if (nFID < 0)
        {
            return OGRERR_FAILURE;
        }
    
        if (m_papoFeatures != nullptr)
        {
            if (nFID >= m_nMaxFeatureCount || m_papoFeatures[nFID] == nullptr)
            {
                return OGRERR_FAILURE;
            }
            delete m_papoFeatures[nFID];
            m_papoFeatures[nFID] = nullptr;
        }
        else
        {
            FeatureIterator oIter = m_oMapFeatures.find(nFID);
            if (oIter == m_oMapFeatures.end())
            {
                return OGRERR_FAILURE;
            }
            m_oMapFeatures.erase(oIter);
        }
    
        m_bHasHoles = true;
        --m_nFeatureCount;
    
        m_bUpdated = true;
    
        return OGRERR_NONE;
    }
    
    /************************************************************************/
    /*                          GetFeatureCount()                           */
    /*                                                                      */
    /*      If a spatial filter is in effect, we turn control over to       */
    /*      the generic counter.  Otherwise we return the total count.      */
    /*      Eventually we should consider implementing a more efficient     */
    /*      way of counting features matching a spatial query.              */
    /************************************************************************/
    
    GIntBig OGRMemLayer::GetFeatureCount(int bForce)
    
    {
        if (m_poFilterGeom != nullptr || m_poAttrQuery != nullptr)
            return OGRLayer::GetFeatureCount(bForce);
    
        return m_nFeatureCount;
    }
    
    /************************************************************************/
    /*                           TestCapability()                           */
    /************************************************************************/
    
    int OGRMemLayer::TestCapability(const char *pszCap) const
    
    {
        if (EQUAL(pszCap, OLCRandomRead))
            return TRUE;
    
        else if (EQUAL(pszCap, OLCSequentialWrite) || EQUAL(pszCap, OLCRandomWrite))
            return m_bUpdatable;
    
        else if (EQUAL(pszCap, OLCFastFeatureCount))
            return m_poFilterGeom == nullptr && m_poAttrQuery == nullptr;
    
        else if (EQUAL(pszCap, OLCFastSpatialFilter))
            return FALSE;
    
        else if (EQUAL(pszCap, OLCDeleteFeature) ||
                 EQUAL(pszCap, OLCUpsertFeature) || EQUAL(pszCap, OLCUpdateFeature))
            return m_bUpdatable;
    
        else if (EQUAL(pszCap, OLCCreateField) ||
                 EQUAL(pszCap, OLCCreateGeomField) ||
                 EQUAL(pszCap, OLCDeleteField) || EQUAL(pszCap, OLCReorderFields) ||
                 EQUAL(pszCap, OLCAlterFieldDefn) ||
                 EQUAL(pszCap, OLCAlterGeomFieldDefn))
            return m_bUpdatable;
    
        else if (EQUAL(pszCap, OLCFastSetNextByIndex))
            return m_poFilterGeom == nullptr && m_poAttrQuery == nullptr &&
                   ((m_papoFeatures != nullptr && !m_bHasHoles) ||
                    m_oMapFeatures.empty());
    
        else if (EQUAL(pszCap, OLCStringsAsUTF8))
            return m_bAdvertizeUTF8;
    
        else if (EQUAL(pszCap, OLCCurveGeometries))
            return TRUE;
    
        else if (EQUAL(pszCap, OLCMeasuredGeometries))
            return TRUE;
    
        else if (EQUAL(pszCap, OLCZGeometries))
            return TRUE;
    
        return FALSE;
    }
    
    /************************************************************************/
    /*                            CreateField()                             */
    /************************************************************************/
    
    OGRErr OGRMemLayer::CreateField(const OGRFieldDefn *poField,
                                    int /* bApproxOK */)
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        // Simple case, no features exist yet.
        if (m_nFeatureCount == 0)
        {
            whileUnsealing(m_poFeatureDefn)->AddFieldDefn(poField);
            return OGRERR_NONE;
        }
    
        // Add field definition and setup remap definition.
        {
            whileUnsealing(m_poFeatureDefn)->AddFieldDefn(poField);
        }
    
        // Remap all the internal features.  Hopefully there aren't any
        // external features referring to our OGRFeatureDefn!
        auto poIter = std::unique_ptr<IOGRMemLayerFeatureIterator>(GetIterator());
        OGRFeature *poFeature = nullptr;
        while ((poFeature = poIter->Next()) != nullptr)
        {
            poFeature->AppendField();
        }
    
        m_bUpdated = true;
    
        return OGRERR_NONE;
    }
    
    /************************************************************************/
    /*                            DeleteField()                             */
    /************************************************************************/
    
    OGRErr OGRMemLayer::DeleteField(int iField)
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        if (iField < 0 || iField >= m_poFeatureDefn->GetFieldCount())
        {
            CPLError(CE_Failure, CPLE_NotSupported, "Invalid field index");
            return OGRERR_FAILURE;
        }
    
        // Update all the internal features.  Hopefully there aren't any
        // external features referring to our OGRFeatureDefn!
        auto poIter = std::unique_ptr<IOGRMemLayerFeatureIterator>(GetIterator());
        while (OGRFeature *poFeature = poIter->Next())
        {
            OGRField *poFieldRaw = poFeature->GetRawFieldRef(iField);
            if (poFeature->IsFieldSetAndNotNull(iField) &&
                !poFeature->IsFieldNull(iField))
            {
                // Little trick to unallocate the field.
                OGRField sField;
                OGR_RawField_SetUnset(&sField);
                poFeature->SetField(iField, &sField);
            }
    
            if (iField < m_poFeatureDefn->GetFieldCount() - 1)
            {
                memmove(poFieldRaw, poFieldRaw + 1,
                        sizeof(OGRField) *
                            (m_poFeatureDefn->GetFieldCount() - 1 - iField));
            }
        }
    
        m_bUpdated = true;
    
        return whileUnsealing(m_poFeatureDefn)->DeleteFieldDefn(iField);
    }
    
    /************************************************************************/
    /*                           ReorderFields()                            */
    /************************************************************************/
    
    OGRErr OGRMemLayer::ReorderFields(int *panMap)
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        if (m_poFeatureDefn->GetFieldCount() == 0)
            return OGRERR_NONE;
    
        const OGRErr eErr =
            OGRCheckPermutation(panMap, m_poFeatureDefn->GetFieldCount());
        if (eErr != OGRERR_NONE)
            return eErr;
    
        // Remap all the internal features.  Hopefully there aren't any
        // external features referring to our OGRFeatureDefn!
        auto poIter = std::unique_ptr<IOGRMemLayerFeatureIterator>(GetIterator());
        while (OGRFeature *poFeature = poIter->Next())
        {
            poFeature->RemapFields(nullptr, panMap);
        }
    
        m_bUpdated = true;
    
        return whileUnsealing(m_poFeatureDefn)->ReorderFieldDefns(panMap);
    }
    
    /************************************************************************/
    /*                           AlterFieldDefn()                           */
    /************************************************************************/
    
    OGRErr OGRMemLayer::AlterFieldDefn(int iField, OGRFieldDefn *poNewFieldDefn,
                                       int nFlagsIn)
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        if (iField < 0 || iField >= m_poFeatureDefn->GetFieldCount())
        {
            CPLError(CE_Failure, CPLE_NotSupported, "Invalid field index");
            return OGRERR_FAILURE;
        }
    
        OGRFieldDefn *poFieldDefn = m_poFeatureDefn->GetFieldDefn(iField);
        auto oTemporaryUnsealer(poFieldDefn->GetTemporaryUnsealer());
    
        if ((nFlagsIn & ALTER_TYPE_FLAG) &&
            (poFieldDefn->GetType() != poNewFieldDefn->GetType() ||
             poFieldDefn->GetSubType() != poNewFieldDefn->GetSubType()))
        {
            if ((poNewFieldDefn->GetType() == OFTDate ||
                 poNewFieldDefn->GetType() == OFTTime ||
                 poNewFieldDefn->GetType() == OFTDateTime) &&
                (poFieldDefn->GetType() == OFTDate ||
                 poFieldDefn->GetType() == OFTTime ||
                 poFieldDefn->GetType() == OFTDateTime))
            {
                // Do nothing on features.
            }
            else if (poNewFieldDefn->GetType() == OFTInteger64 &&
                     poFieldDefn->GetType() == OFTInteger)
            {
                // Update all the internal features.  Hopefully there aren't any
                // external features referring to our OGRFeatureDefn!
                IOGRMemLayerFeatureIterator *poIter = GetIterator();
                OGRFeature *poFeature = nullptr;
                while ((poFeature = poIter->Next()) != nullptr)
                {
                    OGRField *poFieldRaw = poFeature->GetRawFieldRef(iField);
                    if (poFeature->IsFieldSetAndNotNull(iField) &&
                        !poFeature->IsFieldNull(iField))
                    {
                        const GIntBig nVal = poFieldRaw->Integer;
                        poFieldRaw->Integer64 = nVal;
                    }
                }
                delete poIter;
            }
            else if (poNewFieldDefn->GetType() == OFTReal &&
                     poFieldDefn->GetType() == OFTInteger)
            {
                // Update all the internal features.  Hopefully there aren't any
                // external features referring to our OGRFeatureDefn!
                IOGRMemLayerFeatureIterator *poIter = GetIterator();
                OGRFeature *poFeature = nullptr;
                while ((poFeature = poIter->Next()) != nullptr)
                {
                    OGRField *poFieldRaw = poFeature->GetRawFieldRef(iField);
                    if (poFeature->IsFieldSetAndNotNull(iField) &&
                        !poFeature->IsFieldNull(iField))
                    {
                        const double dfVal = poFieldRaw->Integer;
                        poFieldRaw->Real = dfVal;
                    }
                }
                delete poIter;
            }
            else if (poNewFieldDefn->GetType() == OFTReal &&
                     poFieldDefn->GetType() == OFTInteger64)
            {
                // Update all the internal features.  Hopefully there aren't any
                // external features referring to our OGRFeatureDefn!
                IOGRMemLayerFeatureIterator *poIter = GetIterator();
                OGRFeature *poFeature = nullptr;
                while ((poFeature = poIter->Next()) != nullptr)
                {
                    OGRField *poFieldRaw = poFeature->GetRawFieldRef(iField);
                    if (poFeature->IsFieldSetAndNotNull(iField) &&
                        !poFeature->IsFieldNull(iField))
                    {
                        const double dfVal =
                            static_cast<double>(poFieldRaw->Integer64);
                        poFieldRaw->Real = dfVal;
                    }
                }
                delete poIter;
            }
            else
            {
                if (poNewFieldDefn->GetType() != OFTString)
                {
                    CPLError(CE_Failure, CPLE_NotSupported,
                             "Can only convert from OFTInteger to OFTReal, "
                             "or from anything to OFTString");
                    return OGRERR_FAILURE;
                }
    
                // Update all the internal features.  Hopefully there aren't any
                // external features referring to our OGRFeatureDefn!
                IOGRMemLayerFeatureIterator *poIter = GetIterator();
                OGRFeature *poFeature = nullptr;
                while ((poFeature = poIter->Next()) != nullptr)
                {
                    OGRField *poFieldRaw = poFeature->GetRawFieldRef(iField);
                    if (poFeature->IsFieldSetAndNotNull(iField) &&
                        !poFeature->IsFieldNull(iField))
                    {
                        char *pszVal =
                            CPLStrdup(poFeature->GetFieldAsString(iField));
    
                        // Little trick to unallocate the field.
                        OGRField sField;
                        OGR_RawField_SetUnset(&sField);
                        poFeature->SetField(iField, &sField);
    
                        poFieldRaw->String = pszVal;
                    }
                }
                delete poIter;
            }
    
            poFieldDefn->SetSubType(OFSTNone);
            poFieldDefn->SetType(poNewFieldDefn->GetType());
            poFieldDefn->SetSubType(poNewFieldDefn->GetSubType());
        }
    
        if (nFlagsIn & ALTER_NAME_FLAG)
            poFieldDefn->SetName(poNewFieldDefn->GetNameRef());
        if (nFlagsIn & ALTER_WIDTH_PRECISION_FLAG)
        {
            poFieldDefn->SetWidth(poNewFieldDefn->GetWidth());
            poFieldDefn->SetPrecision(poNewFieldDefn->GetPrecision());
        }
    
        m_bUpdated = true;
    
        return OGRERR_NONE;
    }
    
    /************************************************************************/
    /*                         AlterGeomFieldDefn()                         */
    /************************************************************************/
    
    OGRErr OGRMemLayer::AlterGeomFieldDefn(
        int iGeomField, const OGRGeomFieldDefn *poNewGeomFieldDefn, int nFlagsIn)
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        if (iGeomField < 0 || iGeomField >= m_poFeatureDefn->GetGeomFieldCount())
        {
            CPLError(CE_Failure, CPLE_NotSupported, "Invalid field index");
            return OGRERR_FAILURE;
        }
    
        auto poFieldDefn = m_poFeatureDefn->GetGeomFieldDefn(iGeomField);
        auto oTemporaryUnsealer(poFieldDefn->GetTemporaryUnsealer());
    
        if (nFlagsIn & ALTER_GEOM_FIELD_DEFN_NAME_FLAG)
            poFieldDefn->SetName(poNewGeomFieldDefn->GetNameRef());
        if (nFlagsIn & ALTER_GEOM_FIELD_DEFN_TYPE_FLAG)
        {
            if (poNewGeomFieldDefn->GetType() == wkbNone)
                return OGRERR_FAILURE;
            poFieldDefn->SetType(poNewGeomFieldDefn->GetType());
        }
        if (nFlagsIn & ALTER_GEOM_FIELD_DEFN_NULLABLE_FLAG)
            poFieldDefn->SetNullable(poNewGeomFieldDefn->IsNullable());
    
        if (nFlagsIn & ALTER_GEOM_FIELD_DEFN_SRS_FLAG)
        {
            OGRSpatialReference *poSRSNew = nullptr;
            const auto poSRSNewRef = poNewGeomFieldDefn->GetSpatialRef();
            if (poSRSNewRef)
            {
                poSRSNew = poSRSNewRef->Clone();
                if ((nFlagsIn & ALTER_GEOM_FIELD_DEFN_SRS_COORD_EPOCH_FLAG) == 0)
                {
                    const auto poSRSOld = poFieldDefn->GetSpatialRef();
                    if (poSRSOld)
                        poSRSNew->SetCoordinateEpoch(
                            poSRSOld->GetCoordinateEpoch());
                    else
                        poSRSNew->SetCoordinateEpoch(0);
                }
            }
            poFieldDefn->SetSpatialRef(poSRSNew);
            if (poSRSNew)
                poSRSNew->Release();
        }
        else if (nFlagsIn & ALTER_GEOM_FIELD_DEFN_SRS_COORD_EPOCH_FLAG)
        {
            const auto poSRSOld = poFieldDefn->GetSpatialRef();
            const auto poSRSNewRef = poNewGeomFieldDefn->GetSpatialRef();
            if (poSRSOld && poSRSNewRef)
            {
                auto poSRSNew = poSRSOld->Clone();
                poSRSNew->SetCoordinateEpoch(poSRSNewRef->GetCoordinateEpoch());
                poFieldDefn->SetSpatialRef(poSRSNew);
                poSRSNew->Release();
            }
        }
    
        m_bUpdated = true;
    
        return OGRERR_NONE;
    }
    
    /************************************************************************/
    /*                          CreateGeomField()                           */
    /************************************************************************/
    
    OGRErr OGRMemLayer::CreateGeomField(const OGRGeomFieldDefn *poGeomField,
                                        int /* bApproxOK */)
    {
        if (!m_bUpdatable)
            return OGRERR_FAILURE;
    
        // Simple case, no features exist yet.
        if (m_nFeatureCount == 0)
        {
            whileUnsealing(m_poFeatureDefn)->AddGeomFieldDefn(poGeomField);
            return OGRERR_NONE;
        }
    
        // Add field definition and setup remap definition.
        whileUnsealing(m_poFeatureDefn)->AddGeomFieldDefn(poGeomField);
    
        const int nGeomFieldCount = m_poFeatureDefn->GetGeomFieldCount();
        std::vector<int> anRemap(nGeomFieldCount);
        for (int i = 0; i < nGeomFieldCount; ++i)
        {
            if (i < nGeomFieldCount - 1)
                anRemap[i] = i;
            else
                anRemap[i] = -1;
        }
    
        // Remap all the internal features.  Hopefully there aren't any
        // external features referring to our OGRFeatureDefn!
        auto poIter = std::unique_ptr<IOGRMemLayerFeatureIterator>(GetIterator());
        while (OGRFeature *poFeature = poIter->Next())
        {
            poFeature->RemapGeomFields(nullptr, anRemap.data());
        }
    
        m_bUpdated = true;
    
        return OGRERR_NONE;
    }
    
    /************************************************************************/
    /*                       OGRMemLayerIteratorArray                       */
    /************************************************************************/
    
    class OGRMemLayerIteratorArray final : public IOGRMemLayerFeatureIterator
    {
        GIntBig m_iCurIdx = 0;
        const GIntBig m_nMaxFeatureCount;
        OGRFeature **const m_papoFeatures;
    
        CPL_DISALLOW_COPY_ASSIGN(OGRMemLayerIteratorArray)
    
      public:
        OGRMemLayerIteratorArray(GIntBig nMaxFeatureCount,
                                 OGRFeature **papoFeatures)
            : m_nMaxFeatureCount(nMaxFeatureCount), m_papoFeatures(papoFeatures)
        {
        }
    
        OGRFeature *Next() override;
    };
    
    OGRFeature *OGRMemLayerIteratorArray::Next()
    {
        while (m_iCurIdx < m_nMaxFeatureCount)
        {
            OGRFeature *poFeature = m_papoFeatures[m_iCurIdx];
            ++m_iCurIdx;
            if (poFeature != nullptr)
                return poFeature;
        }
        return nullptr;
    }
    
    /************************************************************************/
    /*                        OGRMemLayerIteratorMap                        */
    /************************************************************************/
    
    class OGRMemLayerIteratorMap final : public IOGRMemLayerFeatureIterator
    {
        typedef std::map<GIntBig, std::unique_ptr<OGRFeature>> FeatureMap;
        typedef FeatureMap::iterator FeatureIterator;
    
        const FeatureMap &m_oMapFeatures;
        FeatureIterator m_oIter;
    
      public:
        explicit OGRMemLayerIteratorMap(FeatureMap &oMapFeatures)
            : m_oMapFeatures(oMapFeatures), m_oIter(oMapFeatures.begin())
        {
        }
    
        OGRFeature *Next() override;
    
      private:
        CPL_DISALLOW_COPY_ASSIGN(OGRMemLayerIteratorMap)
    };
    
    OGRFeature *OGRMemLayerIteratorMap::Next()
    {
        if (m_oIter != m_oMapFeatures.end())
        {
            OGRFeature *poFeature = m_oIter->second.get();
            ++m_oIter;
            return poFeature;
        }
        return nullptr;
    }
    
    /************************************************************************/
    /*                            GetIterator()                             */
    /************************************************************************/
    
    IOGRMemLayerFeatureIterator *OGRMemLayer::GetIterator()
    {
        if (m_oMapFeatures.empty())
            return new OGRMemLayerIteratorArray(m_nMaxFeatureCount, m_papoFeatures);
    
        return new OGRMemLayerIteratorMap(m_oMapFeatures);
    }
    
    ```


## Drivers (gdal/frmts/null)

??? example "null/nulldataset.cpp"

    <span class="badge badge-cpp">Drivers (gdal/frmts/null)</span> **Caminho:** `gdal/frmts/null/nulldataset.cpp`

    ```cpp
    /******************************************************************************
     *
     * Project:  GDAL
     * Purpose:  NULL driver.
     * Author:   Even Rouault, <even dot rouault at spatialys dot org>
     *
     ******************************************************************************
     * Copyright (c) 2012-2017, Even Rouault, <even dot rouault at spatialys dot
     *org>
     *
     * SPDX-License-Identifier: MIT
     ****************************************************************************/
    
    #include "gdal_priv.h"
    #include "gdal_frmts.h"
    #include "ogrsf_frmts.h"
    
    /************************************************************************/
    /*                           GDALNullDataset                            */
    /************************************************************************/
    
    class GDALNullDataset final : public GDALDataset
    {
        int m_nLayers;
        OGRLayer **m_papoLayers;
    
        CPL_DISALLOW_COPY_ASSIGN(GDALNullDataset)
    
      public:
        GDALNullDataset();
        ~GDALNullDataset() override;
    
        int GetLayerCount() const override
        {
            return m_nLayers;
        }
    
        const OGRLayer *GetLayer(int) const override;
    
        OGRLayer *ICreateLayer(const char *pszName,
                               const OGRGeomFieldDefn *poGeomFieldDefn,
                               CSLConstList papszOptions) override;
    
        int TestCapability(const char *) const override;
    
        CPLErr SetSpatialRef(const OGRSpatialReference *poSRS) override;
    
        CPLErr SetGeoTransform(const GDALGeoTransform &gt) override;
    
        static GDALDataset *Open(GDALOpenInfo *poOpenInfo);
        static GDALDataset *Create(const char *pszFilename, int nXSize, int nYSize,
                                   int nBands, GDALDataType eType,
                                   CSLConstList papszOptions);
    };
    
    /************************************************************************/
    /*                            GDALNullLayer                             */
    /************************************************************************/
    
    class GDALNullRasterBand final : public GDALRasterBand
    {
      public:
        explicit GDALNullRasterBand(GDALDataType eDT);
    
        CPLErr SetCategoryNames(CPL_UNUSED char **papszNames) override
        {
            return CE_None;
        }
    
        CPLErr SetNoDataValue(CPL_UNUSED double dfNoData) override
        {
            return CE_None;
        }
    
        CPLErr SetNoDataValueAsInt64(CPL_UNUSED int64_t nNoData) override
        {
            return CE_None;
        }
    
        CPLErr SetNoDataValueAsUInt64(CPL_UNUSED uint64_t nNoData) override
        {
            return CE_None;
        }
    
        CPLErr DeleteNoDataValue() override
        {
            return CE_None;
        }
    
        CPLErr SetColorTable(CPL_UNUSED GDALColorTable *poCT) override
        {
            return CE_None;
        }
    
        CPLErr
        SetColorInterpretation(CPL_UNUSED GDALColorInterp eColorInterp) override
        {
            return CE_None;
        }
    
        CPLErr SetOffset(CPL_UNUSED double dfNewOffset) override
        {
            return CE_None;
        }
    
        CPLErr SetScale(CPL_UNUSED double dfNewScale) override
        {
            return CE_None;
        }
    
        CPLErr SetUnitType(CPL_UNUSED const char *pszNewValue) override
        {
            return CE_None;
        }
    
        CPLErr SetDefaultRAT(const GDALRasterAttributeTable *) override
        {
            return CE_None;
        }
    
        CPLErr IReadBlock(int, int, void *) override;
        CPLErr IWriteBlock(int, int, void *) override;
        CPLErr IRasterIO(GDALRWFlag eRWFlag, int nXOff, int nYOff, int nXSize,
                         int nYSize, void *pData, int nBufXSize, int nBufYSize,
                         GDALDataType eBufType, GSpacing nPixelSpace,
                         GSpacing nLineSpace,
                         GDALRasterIOExtraArg *psExtraArg) override;
    };
    
    /************************************************************************/
    /*                            GDALNullLayer                             */
    /************************************************************************/
    
    class GDALNullLayer final : public OGRLayer
    {
        OGRFeatureDefn *poFeatureDefn;
        OGRSpatialReference *poSRS = nullptr;
    
        CPL_DISALLOW_COPY_ASSIGN(GDALNullLayer)
    
      public:
        GDALNullLayer(const char *pszLayerName, const OGRSpatialReference *poSRS,
                      OGRwkbGeometryType eType);
        ~GDALNullLayer() override;
    
        const OGRFeatureDefn *GetLayerDefn() const override
        {
            return poFeatureDefn;
        }
    
        const OGRSpatialReference *GetSpatialRef() const override
        {
            return poSRS;
        }
    
        void ResetReading() override
        {
        }
    
        int TestCapability(const char *) const override;
    
        OGRFeature *GetNextFeature() override
        {
            return nullptr;
        }
    
        OGRErr ICreateFeature(OGRFeature *) override
        {
            return OGRERR_NONE;
        }
    
        virtual OGRErr CreateField(const OGRFieldDefn *poField,
                                   int bApproxOK = TRUE) override;
    };
    
    /************************************************************************/
    /*                         GDALNullRasterBand()                         */
    /************************************************************************/
    
    GDALNullRasterBand::GDALNullRasterBand(GDALDataType eDT)
    {
        eDataType = eDT;
        nBlockXSize = 256;
        nBlockYSize = 256;
    }
    
    /************************************************************************/
    /*                             IRasterIO()                              */
    /************************************************************************/
    
    CPLErr GDALNullRasterBand::IRasterIO(GDALRWFlag eRWFlag, int nXOff, int nYOff,
                                         int nXSize, int nYSize, void *pData,
                                         int nBufXSize, int nBufYSize,
                                         GDALDataType eBufType,
                                         GSpacing nPixelSpace, GSpacing nLineSpace,
                                         GDALRasterIOExtraArg *psExtraArg)
    {
        if (eRWFlag == GF_Write)
            return CE_None;
        if (psExtraArg->eResampleAlg != GRIORA_NearestNeighbour &&
            (nBufXSize != nXSize || nBufYSize != nYSize))
        {
            return GDALRasterBand::IRasterIO(eRWFlag, nXOff, nYOff, nXSize, nYSize,
                                             pData, nBufXSize, nBufYSize, eBufType,
                                             nPixelSpace, nLineSpace, psExtraArg);
        }
        if (nPixelSpace == GDALGetDataTypeSizeBytes(eBufType) &&
            nLineSpace == nPixelSpace * nBufXSize)
        {
            memset(pData, 0, static_cast<size_t>(nLineSpace) * nBufYSize);
        }
        else
        {
            for (int iY = 0; iY < nBufYSize; iY++)
            {
                double dfZero = 0;
                GDALCopyWords(&dfZero, GDT_Float64, 0,
                              reinterpret_cast<GByte *>(pData) + iY * nLineSpace,
                              eBufType, static_cast<int>(nPixelSpace), nBufXSize);
            }
        }
        return CE_None;
    }
    
    /************************************************************************/
    /*                             IReadBlock()                             */
    /************************************************************************/
    
    CPLErr GDALNullRasterBand::IReadBlock(int, int, void *pData)
    {
        memset(pData, 0,
               static_cast<size_t>(nBlockXSize) * nBlockYSize *
                   GDALGetDataTypeSizeBytes(eDataType));
        return CE_None;
    }
    
    /************************************************************************/
    /*                            IWriteBlock()                             */
    /************************************************************************/
    
    CPLErr GDALNullRasterBand::IWriteBlock(int, int, void *)
    {
        return CE_None;
    }
    
    /************************************************************************/
    /*                          GDALNullDataset()                           */
    /************************************************************************/
    
    GDALNullDataset::GDALNullDataset() : m_nLayers(0), m_papoLayers(nullptr)
    {
        eAccess = GA_Update;
    }
    
    /************************************************************************/
    /*                          ~GDALNullDataset()                          */
    /************************************************************************/
    
    GDALNullDataset::~GDALNullDataset()
    {
        for (int i = 0; i < m_nLayers; i++)
            delete m_papoLayers[i];
        CPLFree(m_papoLayers);
    }
    
    /************************************************************************/
    /*                            ICreateLayer()                            */
    /************************************************************************/
    
    OGRLayer *GDALNullDataset::ICreateLayer(const char *pszLayerName,
                                            const OGRGeomFieldDefn *poGeomFieldDefn,
                                            CSLConstList /*papszOptions */)
    {
        const auto eType = poGeomFieldDefn ? poGeomFieldDefn->GetType() : wkbNone;
        const auto poSRS =
            poGeomFieldDefn ? poGeomFieldDefn->GetSpatialRef() : nullptr;
    
        m_papoLayers = static_cast<OGRLayer **>(
            CPLRealloc(m_papoLayers, sizeof(OGRLayer *) * (m_nLayers + 1)));
        m_papoLayers[m_nLayers] = new GDALNullLayer(pszLayerName, poSRS, eType);
        m_nLayers++;
        return m_papoLayers[m_nLayers - 1];
    }
    
    /************************************************************************/
    /*                           TestCapability()                           */
    /************************************************************************/
    
    int GDALNullDataset::TestCapability(const char *pszCap) const
    
    {
        if (EQUAL(pszCap, ODsCCreateLayer))
            return TRUE;
        if (EQUAL(pszCap, ODsCRandomLayerWrite))
            return TRUE;
        return FALSE;
    }
    
    /************************************************************************/
    /*                              GetLayer()                              */
    /************************************************************************/
    
    const OGRLayer *GDALNullDataset::GetLayer(int iLayer) const
    
    {
        if (iLayer < 0 || iLayer >= m_nLayers)
            return nullptr;
        else
            return m_papoLayers[iLayer];
    }
    
    /************************************************************************/
    /*                           SetSpatialRef()                            */
    /************************************************************************/
    
    CPLErr GDALNullDataset::SetSpatialRef(const OGRSpatialReference *)
    
    {
        return CE_None;
    }
    
    /************************************************************************/
    /*                          SetGeoTransform()                           */
    /************************************************************************/
    
    CPLErr GDALNullDataset::SetGeoTransform(const GDALGeoTransform &)
    
    {
        return CE_None;
    }
    
    /************************************************************************/
    /*                                Open()                                */
    /************************************************************************/
    
    GDALDataset *GDALNullDataset::Open(GDALOpenInfo *poOpenInfo)
    {
        if (!STARTS_WITH_CI(poOpenInfo->pszFilename, "NULL:"))
            return nullptr;
    
        const char *pszStr = poOpenInfo->pszFilename + strlen("NULL:");
        char **papszTokens = CSLTokenizeString2(pszStr, ",", 0);
        int nXSize = atoi(CSLFetchNameValueDef(papszTokens, "width", "512"));
        int nYSize = atoi(CSLFetchNameValueDef(papszTokens, "height", "512"));
        int nBands = atoi(CSLFetchNameValueDef(papszTokens, "bands", "1"));
        const char *pszDTName = CSLFetchNameValueDef(papszTokens, "type", "Byte");
        GDALDataType eDT = GDT_UInt8;
        for (int iType = 1; iType < GDT_TypeCount; iType++)
        {
            if (GDALGetDataTypeName(static_cast<GDALDataType>(iType)) != nullptr &&
                EQUAL(GDALGetDataTypeName(static_cast<GDALDataType>(iType)),
                      pszDTName))
            {
                eDT = static_cast<GDALDataType>(iType);
                break;
            }
        }
        CSLDestroy(papszTokens);
    
        return Create("", nXSize, nYSize, nBands, eDT, nullptr);
    }
    
    /************************************************************************/
    /*                               Create()                               */
    /************************************************************************/
    
    GDALDataset *GDALNullDataset::Create(const char *, int nXSize, int nYSize,
                                         int nBandsIn, GDALDataType eType,
                                         CSLConstList)
    {
        GDALNullDataset *poDS = new GDALNullDataset();
        poDS->nRasterXSize = nXSize;
        poDS->nRasterYSize = nYSize;
        for (int i = 0; i < nBandsIn; i++)
            poDS->SetBand(i + 1, new GDALNullRasterBand(eType));
        return poDS;
    }
    
    /************************************************************************/
    /*                           GDALNullLayer()                            */
    /************************************************************************/
    
    GDALNullLayer::GDALNullLayer(const char *pszLayerName,
                                 const OGRSpatialReference *poSRSIn,
                                 OGRwkbGeometryType eType)
        : poFeatureDefn(new OGRFeatureDefn(pszLayerName))
    {
        SetDescription(poFeatureDefn->GetName());
        poFeatureDefn->SetGeomType(eType);
        poFeatureDefn->Reference();
    
        if (poSRSIn)
            poSRS = poSRSIn->Clone();
    }
    
    /************************************************************************/
    /*                           ~GDALNullLayer()                           */
    /************************************************************************/
    
    GDALNullLayer::~GDALNullLayer()
    {
        poFeatureDefn->Release();
    
        if (poSRS)
            poSRS->Release();
    }
    
    /************************************************************************/
    /*                           TestCapability()                           */
    /************************************************************************/
    
    int GDALNullLayer::TestCapability(const char *pszCap) const
    
    {
        if (EQUAL(pszCap, OLCSequentialWrite))
            return TRUE;
        if (EQUAL(pszCap, OLCCreateField))
            return TRUE;
        return FALSE;
    }
    
    /************************************************************************/
    /*                            CreateField()                             */
    /************************************************************************/
    
    OGRErr GDALNullLayer::CreateField(const OGRFieldDefn *poField, int)
    {
        poFeatureDefn->AddFieldDefn(poField);
        return OGRERR_NONE;
    }
    
    /************************************************************************/
    /*                         GDALRegister_NULL()                          */
    /************************************************************************/
    
    void GDALRegister_NULL()
    
    {
        if (GDALGetDriverByName("NULL") != nullptr)
            return;
    
        GDALDriver *poDriver;
        poDriver = new GDALDriver();
    
        poDriver->SetDescription("NULL");
        poDriver->SetMetadataItem(GDAL_DMD_CONNECTION_PREFIX, "NULL:");
        poDriver->SetMetadataItem(GDAL_DCAP_RASTER, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_VECTOR, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_CREATE_LAYER, "YES");
        poDriver->SetMetadataItem(GDAL_DCAP_CREATE_FIELD, "YES");
        poDriver->SetMetadataItem(GDAL_DMD_LONGNAME, "NULL");
    
        poDriver->SetMetadataItem(GDAL_DMD_CREATIONFIELDDATATYPES,
                                  "Integer Integer64 Real String Date DateTime "
                                  "Binary IntegerList Integer64List "
                                  "RealList StringList");
    
        poDriver->SetMetadataItem(GDAL_DMD_SUPPORTED_SQL_DIALECTS, "OGRSQL SQLITE");
    
        poDriver->pfnOpen = GDALNullDataset::Open;
        poDriver->pfnCreate = GDALNullDataset::Create;
    
        GetGDALDriverManager()->RegisterDriver(poDriver);
    }
    
    ```


## Drivers (gdal/frmts/tsx)

??? example "tsx/tsxdataset.cpp"

    <span class="badge badge-cpp">Drivers (gdal/frmts/tsx)</span> **Caminho:** `gdal/frmts/tsx/tsxdataset.cpp`

    ```cpp
    /******************************************************************************
     *
     * Project:     TerraSAR-X XML Product Support
     * Purpose:     Support for TerraSAR-X XML Metadata files
     * Author:      Philippe Vachon <philippe@cowpig.ca>
     * Description: This driver adds support for reading metadata and georef data
     *              associated with TerraSAR-X products.
     *
     ******************************************************************************
     * Copyright (c) 2007, Philippe Vachon <philippe@cowpig.ca>
     * Copyright (c) 2009-2012, Even Rouault <even dot rouault at spatialys.com>
     *
     * SPDX-License-Identifier: MIT
     ****************************************************************************/
    
    #include "cpl_minixml.h"
    #include "gdal_frmts.h"
    #include "gdal_pam.h"
    #include "gdal_driver.h"
    #include "gdal_drivermanager.h"
    #include "gdal_openinfo.h"
    #include "gdal_cpp_functions.h"
    #include "ogr_spatialref.h"
    
    #define MAX_GCPS 5000  // this should be more than enough ground control points
    
    namespace gdal::TSX
    {
    enum ePolarization
    {
        HH = 0,
        HV,
        VH,
        VV
    };
    
    enum eProductType
    {
        eSSC = 0,
        eMGD,
        eEEC,
        eGEC,
        eUnknown
    };
    }  // namespace gdal::TSX
    
    using namespace gdal::TSX;
    
    /************************************************************************/
    /*                           Helper Functions                           */
    /************************************************************************/
    
    /* GetFilePath: return a relative path to a file within an XML node.
     * Returns Null on failure
     */
    static CPLString GetFilePath(CPLXMLNode *psXMLNode, const char **pszNodeType)
    {
        const char *pszDirectory =
            CPLGetXMLValue(psXMLNode, "file.location.path", "");
        const char *pszFilename =
            CPLGetXMLValue(psXMLNode, "file.location.filename", "");
        *pszNodeType = CPLGetXMLValue(psXMLNode, "type", " ");
    
        if (pszDirectory == nullptr || pszFilename == nullptr)
        {
            return "";
        }
    
        return CPLString(pszDirectory) + '/' + pszFilename;
    }
    
    /************************************************************************/
    /* ==================================================================== */
    /*                                TSXDataset                                 */
    /* ==================================================================== */
    /************************************************************************/
    
    class TSXDataset final : public GDALPamDataset
    {
        int nGCPCount;
        GDAL_GCP *pasGCPList;
    
        OGRSpatialReference m_oGCPSRS{};
    
        OGRSpatialReference m_oSRS{};
        GDALGeoTransform m_gt{};
        bool bHaveGeoTransform;
    
        eProductType nProduct;
    
      public:
        TSXDataset();
        ~TSXDataset() override;
    
        int GetGCPCount() override;
        const OGRSpatialReference *GetGCPSpatialRef() const override;
        const GDAL_GCP *GetGCPs() override;
    
        CPLErr GetGeoTransform(GDALGeoTransform &gt) const override;
        const OGRSpatialReference *GetSpatialRef() const override;
    
        static GDALDataset *Open(GDALOpenInfo *poOpenInfo);
        static int Identify(GDALOpenInfo *poOpenInfo);
    
      private:
        bool getGCPsFromGEOREF_XML(const char *pszGeorefFilename);
    };
    
    /************************************************************************/
    /* ==================================================================== */
    /*                                TSXRasterBand                           */
    /* ==================================================================== */
    /************************************************************************/
    
    class TSXRasterBand final : public GDALPamRasterBand
    {
        GDALDataset *poBand;
        ePolarization ePol;
    
      public:
        TSXRasterBand(TSXDataset *poDSIn, GDALDataType eDataType,
                      ePolarization ePol, GDALDataset *poBand);
        ~TSXRasterBand() override;
    
        CPLErr IReadBlock(int nBlockXOff, int nBlockYOff, void *pImage) override;
    
        static GDALDataset *Open(GDALOpenInfo *poOpenInfo);
    };
    
    /************************************************************************/
    /*                            TSXRasterBand                             */
    /************************************************************************/
    
    TSXRasterBand::TSXRasterBand(TSXDataset *poDSIn, GDALDataType eDataTypeIn,
                                 ePolarization ePolIn, GDALDataset *poBandIn)
        : poBand(poBandIn), ePol(ePolIn)
    {
        poDS = poDSIn;
        eDataType = eDataTypeIn;
    
        switch (ePol)
        {
            case HH:
                SetMetadataItem("POLARIMETRIC_INTERP", "HH");
                break;
            case HV:
                SetMetadataItem("POLARIMETRIC_INTERP", "HV");
                break;
            case VH:
                SetMetadataItem("POLARIMETRIC_INTERP", "VH");
                break;
            case VV:
                SetMetadataItem("POLARIMETRIC_INTERP", "VV");
                break;
        }
    
        /* now setup the actual raster reader */
        GDALRasterBand *poSrcBand = poBandIn->GetRasterBand(1);
        poSrcBand->GetBlockSize(&nBlockXSize, &nBlockYSize);
    }
    
    /************************************************************************/
    /*                           TSXRasterBand()                            */
    /************************************************************************/
    
    TSXRasterBand::~TSXRasterBand()
    {
        if (poBand != nullptr)
            GDALClose(reinterpret_cast<GDALRasterBandH>(poBand));
    }
    
    /************************************************************************/
    /*                             IReadBlock()                             */
    /************************************************************************/
    
    CPLErr TSXRasterBand::IReadBlock(int nBlockXOff, int nBlockYOff, void *pImage)
    {
        int nRequestYSize;
    
        /* Check if the last strip is partial so we can avoid over-requesting */
        if ((nBlockYOff + 1) * nBlockYSize > nRasterYSize)
        {
            nRequestYSize = nRasterYSize - nBlockYOff * nBlockYSize;
            memset(pImage, 0,
                   static_cast<size_t>(GDALGetDataTypeSizeBytes(eDataType)) *
                       nBlockXSize * nBlockYSize);
        }
        else
        {
            nRequestYSize = nBlockYSize;
        }
    
        /* Read Complex Data */
        if (eDataType == GDT_CInt16)
        {
            return poBand->RasterIO(
                GF_Read, nBlockXOff * nBlockXSize, nBlockYOff * nBlockYSize,
                nBlockXSize, nRequestYSize, pImage, nBlockXSize, nRequestYSize,
                GDT_CInt16, 1, nullptr, 4, nBlockXSize * 4, 0, nullptr);
        }
    
        // Detected Product
        return poBand->RasterIO(
            GF_Read, nBlockXOff * nBlockXSize, nBlockYOff * nBlockYSize,
            nBlockXSize, nRequestYSize, pImage, nBlockXSize, nRequestYSize,
            GDT_UInt16, 1, nullptr, 2, nBlockXSize * 2, 0, nullptr);
    }
    
    /************************************************************************/
    /* ==================================================================== */
    /*                                TSXDataset                                */
    /* ==================================================================== */
    /************************************************************************/
    
    /************************************************************************/
    /*                             TSXDataset()                             */
    /************************************************************************/
    
    TSXDataset::TSXDataset()
        : nGCPCount(0), pasGCPList(nullptr), bHaveGeoTransform(false),
          nProduct(eUnknown)
    {
        m_oSRS.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER);
        m_oGCPSRS.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER);
    }
    
    /************************************************************************/
    /*                            ~TSXDataset()                             */
    /************************************************************************/
    
    TSXDataset::~TSXDataset()
    {
        FlushCache(true);
    
        if (nGCPCount > 0)
        {
            GDALDeinitGCPs(nGCPCount, pasGCPList);
            CPLFree(pasGCPList);
        }
    }
    
    /************************************************************************/
    /*                              Identify()                              */
    /************************************************************************/
    
    int TSXDataset::Identify(GDALOpenInfo *poOpenInfo)
    {
        if (poOpenInfo->fpL == nullptr || poOpenInfo->nHeaderBytes < 260)
        {
            if (poOpenInfo->bIsDirectory)
            {
                const CPLString osFilename = CPLFormCIFilenameSafe(
                    poOpenInfo->pszFilename,
                    CPLGetFilename(poOpenInfo->pszFilename), "xml");
    
                /* Check if the filename contains TSX1_SAR (TerraSAR-X) or TDX1_SAR
                 * (TanDEM-X) or PAZ1_SAR (PAZ) */
                if (!(STARTS_WITH_CI(CPLGetBasenameSafe(osFilename).c_str(),
                                     "TSX1_SAR") ||
                      STARTS_WITH_CI(CPLGetBasenameSafe(osFilename).c_str(),
                                     "TDX1_SAR") ||
                      STARTS_WITH_CI(CPLGetBasenameSafe(osFilename).c_str(),
                                     "PAZ1_SAR")))
                    return 0;
    
                VSIStatBufL sStat;
                if (VSIStatL(osFilename, &sStat) == 0)
                    return 1;
            }
    
            return 0;
        }
    
        /* Check if the filename contains TSX1_SAR (TerraSAR-X) or TDX1_SAR
         * (TanDEM-X) or PAZ1_SAR (PAZ) */
        if (!(STARTS_WITH_CI(CPLGetBasenameSafe(poOpenInfo->pszFilename).c_str(),
                             "TSX1_SAR") ||
              STARTS_WITH_CI(CPLGetBasenameSafe(poOpenInfo->pszFilename).c_str(),
                             "TDX1_SAR") ||
              STARTS_WITH_CI(CPLGetBasenameSafe(poOpenInfo->pszFilename).c_str(),
                             "PAZ1_SAR")))
            return 0;
    
        /* finally look for the <level1Product tag */
        if (!STARTS_WITH_CI(reinterpret_cast<char *>(poOpenInfo->pabyHeader),
                            "<level1Product"))
            return 0;
    
        return 1;
    }
    
    /************************************************************************/
    /*                                getGCPsFromGEOREF_XML()               */
    /*Reads georeferencing information from the TerraSAR-X GEOREF.XML file    */
    /*and writes the information to the dataset's gcp list and projection     */
    /*string.                                                                */
    /*Returns true on success.                                                */
    /************************************************************************/
    bool TSXDataset::getGCPsFromGEOREF_XML(const char *pszGeorefFilename)
    {
        // open GEOREF.xml
        CPLXMLNode *psGeorefData = CPLParseXMLFile(pszGeorefFilename);
        if (psGeorefData == nullptr)
            return false;
    
        // get the ellipsoid and semi-major, semi-minor axes
        OGRSpatialReference osr;
        CPLXMLNode *psSphere =
            CPLGetXMLNode(psGeorefData, "=geoReference.referenceFrames.sphere");
        if (psSphere != nullptr)
        {
            const char *pszEllipsoidName =
                CPLGetXMLValue(psSphere, "ellipsoidID", "");
            const double minor_axis =
                CPLAtof(CPLGetXMLValue(psSphere, "semiMinorAxis", "0.0"));
            const double major_axis =
                CPLAtof(CPLGetXMLValue(psSphere, "semiMajorAxis", "0.0"));
            // save datum parameters to the spatial reference
            if (EQUAL(pszEllipsoidName, "") || minor_axis == 0.0 ||
                major_axis == 0.0)
            {
                CPLError(CE_Warning, CPLE_AppDefined,
                         "Warning- incomplete"
                         " ellipsoid information.  Using wgs-84 parameters.");
                osr.SetWellKnownGeogCS("WGS84");
            }
            else if (EQUAL(pszEllipsoidName, "WGS84"))
            {
                osr.SetWellKnownGeogCS("WGS84");
            }
            else
            {
                const double inv_flattening =
                    major_axis / (major_axis - minor_axis);
                osr.SetGeogCS("", "", pszEllipsoidName, major_axis, inv_flattening);
            }
        }
    
        // get gcps
        CPLXMLNode *psGeolocationGrid =
            CPLGetXMLNode(psGeorefData, "=geoReference.geolocationGrid");
        if (psGeolocationGrid == nullptr)
        {
            CPLDestroyXMLNode(psGeorefData);
            return false;
        }
        nGCPCount = atoi(
            CPLGetXMLValue(psGeolocationGrid, "numberOfGridPoints.total", "0"));
        // count the gcps if the given count value is invalid
        CPLXMLNode *psNode = nullptr;
        if (nGCPCount <= 0)
        {
            for (psNode = psGeolocationGrid->psChild; psNode != nullptr;
                 psNode = psNode->psNext)
                if (EQUAL(psNode->pszValue, "gridPoint"))
                    nGCPCount++;
        }
        // if there are no gcps, fail
        if (nGCPCount <= 0)
        {
            CPLDestroyXMLNode(psGeorefData);
            return false;
        }
    
        // put some reasonable limits of the number of gcps
        if (nGCPCount > MAX_GCPS)
            nGCPCount = MAX_GCPS;
        // allocate memory for the gcps
        pasGCPList =
            static_cast<GDAL_GCP *>(CPLCalloc(sizeof(GDAL_GCP), nGCPCount));
    
        // loop through all gcps and set info
    
        // save the number allocated to ensure it does not run off the end of the
        // array
        const int gcps_allocated = nGCPCount;
        nGCPCount = 0;  // reset to zero and count
        // do a check on the grid point to make sure it has lat,long row, and column
        // it seems that only SSC products contain row, col - how to map lat long
        // otherwise?? for now fail if row and col are not present - just check the
        // first and assume the rest are the same
        for (psNode = psGeolocationGrid->psChild; psNode != nullptr;
             psNode = psNode->psNext)
        {
            if (!EQUAL(psNode->pszValue, "gridPoint"))
                continue;
    
            if (!strcmp(CPLGetXMLValue(psNode, "col", "error"), "error") ||
                !strcmp(CPLGetXMLValue(psNode, "row", "error"), "error") ||
                !strcmp(CPLGetXMLValue(psNode, "lon", "error"), "error") ||
                !strcmp(CPLGetXMLValue(psNode, "lat", "error"), "error"))
            {
                CPLDestroyXMLNode(psGeorefData);
                return false;
            }
        }
        for (psNode = psGeolocationGrid->psChild; psNode != nullptr;
             psNode = psNode->psNext)
        {
            // break out if the end of the array has been reached
            if (nGCPCount >= gcps_allocated)
            {
                CPLError(CE_Warning, CPLE_AppDefined,
                         "GDAL TSX driver: Truncating the number of GCPs.");
                break;
            }
    
            GDAL_GCP *psGCP = pasGCPList + nGCPCount;
    
            if (!EQUAL(psNode->pszValue, "gridPoint"))
                continue;
    
            nGCPCount++;
    
            char szID[32];
            snprintf(szID, sizeof(szID), "%d", nGCPCount);
            psGCP->pszId = CPLStrdup(szID);
            psGCP->pszInfo = CPLStrdup("");
            psGCP->dfGCPPixel = CPLAtof(CPLGetXMLValue(psNode, "col", "0"));
            psGCP->dfGCPLine = CPLAtof(CPLGetXMLValue(psNode, "row", "0"));
            psGCP->dfGCPX = CPLAtof(CPLGetXMLValue(psNode, "lon", ""));
            psGCP->dfGCPY = CPLAtof(CPLGetXMLValue(psNode, "lat", ""));
            // looks like height is in meters - should it be converted so xyz are
            // all on the same scale??
            psGCP->dfGCPZ = 0;
            // CPLAtof(CPLGetXMLValue(psNode,"height",""));
        }
    
        m_oGCPSRS = std::move(osr);
    
        CPLDestroyXMLNode(psGeorefData);
    
        return true;
    }
    
    /************************************************************************/
    /*                                Open()                                */
    /************************************************************************/
    
    GDALDataset *TSXDataset::Open(GDALOpenInfo *poOpenInfo)
    {
        /* -------------------------------------------------------------------- */
        /*      Is this a TerraSAR-X product file?                              */
        /* -------------------------------------------------------------------- */
        if (!TSXDataset::Identify(poOpenInfo))
        {
            return nullptr; /* nope */
        }
    
        /* -------------------------------------------------------------------- */
        /*      Confirm the requested access is supported.                      */
        /* -------------------------------------------------------------------- */
        if (poOpenInfo->eAccess == GA_Update)
        {
            ReportUpdateNotSupportedByDriver("TSX");
            return nullptr;
        }
    
        CPLString osFilename;
    
        if (poOpenInfo->bIsDirectory)
        {
            osFilename = CPLFormCIFilenameSafe(
                poOpenInfo->pszFilename, CPLGetFilename(poOpenInfo->pszFilename),
                "xml");
        }
        else
            osFilename = poOpenInfo->pszFilename;
    
        /* Ingest the XML */
        CPLXMLTreeCloser psData(CPLParseXMLFile(osFilename));
        if (psData == nullptr)
            return nullptr;
    
        /* find the product components */
        const CPLXMLNode *psComponents =
            CPLGetXMLNode(psData.get(), "=level1Product.productComponents");
        if (psComponents == nullptr)
        {
            CPLError(CE_Failure, CPLE_OpenFailed,
                     "Unable to find <productComponents> tag in file.");
            return nullptr;
        }
    
        /* find the product info tag */
        const CPLXMLNode *psProductInfo =
            CPLGetXMLNode(psData.get(), "=level1Product.productInfo");
        if (psProductInfo == nullptr)
        {
            CPLError(CE_Failure, CPLE_OpenFailed,
                     "Unable to find <productInfo> tag in file.");
            return nullptr;
        }
    
        /* -------------------------------------------------------------------- */
        /*      Create the dataset.                                             */
        /* -------------------------------------------------------------------- */
    
        auto poDS = std::make_unique<TSXDataset>();
    
        /* -------------------------------------------------------------------- */
        /*      Read in product info.                                           */
        /* -------------------------------------------------------------------- */
    
        poDS->SetMetadataItem(
            "SCENE_CENTRE_TIME",
            CPLGetXMLValue(psProductInfo,
                           "sceneInfo.sceneCenterCoord.azimuthTimeUTC", "unknown"));
        poDS->SetMetadataItem("OPERATIONAL_MODE",
                              CPLGetXMLValue(psProductInfo,
                                             "generationInfo.groundOperationsType",
                                             "unknown"));
        poDS->SetMetadataItem(
            "ORBIT_CYCLE",
            CPLGetXMLValue(psProductInfo, "missionInfo.orbitCycle", "unknown"));
        poDS->SetMetadataItem(
            "ABSOLUTE_ORBIT",
            CPLGetXMLValue(psProductInfo, "missionInfo.absOrbit", "unknown"));
        poDS->SetMetadataItem(
            "ORBIT_DIRECTION",
            CPLGetXMLValue(psProductInfo, "missionInfo.orbitDirection", "unknown"));
        poDS->SetMetadataItem("IMAGING_MODE",
                              CPLGetXMLValue(psProductInfo,
                                             "acquisitionInfo.imagingMode",
                                             "unknown"));
        poDS->SetMetadataItem("PRODUCT_VARIANT",
                              CPLGetXMLValue(psProductInfo,
                                             "productVariantInfo.productVariant",
                                             "unknown"));
        std::string osDataType =
            CPLGetXMLValue(psProductInfo, "imageDataInfo.imageDataType", "unknown");
        poDS->SetMetadataItem("IMAGE_TYPE", osDataType.c_str());
    
        /* Get raster information */
        int nRows = atoi(CPLGetXMLValue(
            psProductInfo, "imageDataInfo.imageRaster.numberOfRows", ""));
        int nCols = atoi(CPLGetXMLValue(
            psProductInfo, "imageDataInfo.imageRaster.numberOfColumns", ""));
    
        poDS->nRasterXSize = nCols;
        poDS->nRasterYSize = nRows;
    
        poDS->SetMetadataItem("ROW_SPACING",
                              CPLGetXMLValue(psProductInfo,
                                             "imageDataInfo.imageRaster.rowSpacing",
                                             "unknown"));
        poDS->SetMetadataItem(
            "COL_SPACING",
            CPLGetXMLValue(psProductInfo, "imageDataInfo.imageRaster.columnSpacing",
                           "unknown"));
        poDS->SetMetadataItem(
            "COL_SPACING_UNITS",
            CPLGetXMLValue(psProductInfo,
                           "imageDataInfo.imageRaster.columnSpacing.units",
                           "unknown"));
    
        /* Get equivalent number of looks */
        poDS->SetMetadataItem(
            "AZIMUTH_LOOKS",
            CPLGetXMLValue(psProductInfo, "imageDataInfo.imageRaster.azimuthLooks",
                           "unknown"));
        poDS->SetMetadataItem("RANGE_LOOKS",
                              CPLGetXMLValue(psProductInfo,
                                             "imageDataInfo.imageRaster.rangeLooks",
                                             "unknown"));
    
        const char *pszProductVariant = CPLGetXMLValue(
            psProductInfo, "productVariantInfo.productVariant", "unknown");
    
        poDS->SetMetadataItem("PRODUCT_VARIANT", pszProductVariant);
    
        /* Determine what product variant this is */
        if (STARTS_WITH_CI(pszProductVariant, "SSC"))
            poDS->nProduct = eSSC;
        else if (STARTS_WITH_CI(pszProductVariant, "MGD"))
            poDS->nProduct = eMGD;
        else if (STARTS_WITH_CI(pszProductVariant, "EEC"))
            poDS->nProduct = eEEC;
        else if (STARTS_WITH_CI(pszProductVariant, "GEC"))
            poDS->nProduct = eGEC;
        else
            poDS->nProduct = eUnknown;
    
        /* Start reading in the product components */
        std::string osGeorefFile;
        CPLErr geoTransformErr = CE_Failure;
        for (CPLXMLNode *psComponent = psComponents->psChild;
             psComponent != nullptr; psComponent = psComponent->psNext)
        {
            const char *pszType = nullptr;
            const std::string osFilePath = GetFilePath(psComponent, &pszType);
            if (CPLHasPathTraversal(osFilePath.c_str()))
            {
                CPLError(CE_Failure, CPLE_AppDefined,
                         "Path traversal detected in %s", osFilePath.c_str());
                return nullptr;
            }
            std::string osPath = CPLFormFilenameSafe(
                CPLGetDirnameSafe(osFilename).c_str(), osFilePath.c_str(), "");
            const char *pszPolLayer = CPLGetXMLValue(psComponent, "polLayer", " ");
    
            if (!STARTS_WITH_CI(pszType, " "))
            {
                if (STARTS_WITH_CI(pszType, "MAPPING_GRID"))
                {
                    /* the mapping grid... save as a metadata item this path */
                    poDS->SetMetadataItem("MAPPING_GRID", osPath.c_str());
                }
                else if (STARTS_WITH_CI(pszType, "GEOREF"))
                {
                    /* save the path to the georef data for later use */
                    osGeorefFile = std::move(osPath);
                }
            }
            else if (!STARTS_WITH_CI(pszPolLayer, " ") &&
                     STARTS_WITH_CI(psComponent->pszValue, "imageData"))
            {
                /* determine the polarization of this band */
                ePolarization ePol;
                if (STARTS_WITH_CI(pszPolLayer, "HH"))
                {
                    ePol = HH;
                }
                else if (STARTS_WITH_CI(pszPolLayer, "HV"))
                {
                    ePol = HV;
                }
                else if (STARTS_WITH_CI(pszPolLayer, "VH"))
                {
                    ePol = VH;
                }
                else
                {
                    ePol = VV;
                }
    
                GDALDataType eDataType =
                    STARTS_WITH_CI(osDataType.c_str(), "COMPLEX") ? GDT_CInt16
                                                                  : GDT_UInt16;
    
                /* try opening the file that represents that band */
                GDALDataset *poBandData =
                    GDALDataset::FromHandle(GDALOpen(osPath.c_str(), GA_ReadOnly));
                if (poBandData != nullptr)
                {
                    TSXRasterBand *poBand =
                        new TSXRasterBand(poDS.get(), eDataType, ePol, poBandData);
                    poDS->SetBand(poDS->GetRasterCount() + 1, poBand);
    
                    // copy georeferencing info from the band
                    // need error checking??
                    // it will just save the info from the last band
                    const auto poSrcSRS = poBandData->GetSpatialRef();
                    if (poSrcSRS)
                        poDS->m_oSRS = *poSrcSRS;
    
                    geoTransformErr = poBandData->GetGeoTransform(poDS->m_gt);
                }
            }
        }
    
        // now check if there is a geotransform
        if (!poDS->m_oSRS.IsEmpty() && geoTransformErr == CE_None)
        {
            poDS->bHaveGeoTransform = TRUE;
        }
        else
        {
            poDS->bHaveGeoTransform = FALSE;
            poDS->m_oSRS.Clear();
            poDS->m_gt = GDALGeoTransform();
        }
    
        /* -------------------------------------------------------------------- */
        /*      Check and set matrix representation.                            */
        /* -------------------------------------------------------------------- */
    
        if (poDS->GetRasterCount() == 4)
        {
            poDS->SetMetadataItem("MATRIX_REPRESENTATION", "SCATTERING");
        }
    
        /* -------------------------------------------------------------------- */
        /*      Read the four corners and centre GCPs in                        */
        /* -------------------------------------------------------------------- */
    
        const CPLXMLNode *psSceneInfo =
            CPLGetXMLNode(psData.get(), "=level1Product.productInfo.sceneInfo");
        if (psSceneInfo != nullptr)
        {
            /* extract the GCPs from the provided file */
            bool success = false;
            if (!osGeorefFile.empty())
                success = poDS->getGCPsFromGEOREF_XML(osGeorefFile.c_str());
    
            // if the gcp's cannot be extracted from the georef file, try to get the
            // corner coordinates for now just SSC because the others don't have
            // refColumn and refRow
            if (!success && poDS->nProduct == eSSC)
            {
                int nGCP = 0;
                double dfAvgHeight = CPLAtof(
                    CPLGetXMLValue(psSceneInfo, "sceneAverageHeight", "0.0"));
    
                // count and allocate gcps - there should be five - 4 corners and a
                // centre
                poDS->nGCPCount = 0;
                const CPLXMLNode *psNode = psSceneInfo->psChild;
                for (; psNode != nullptr; psNode = psNode->psNext)
                {
                    if (!EQUAL(psNode->pszValue, "sceneCenterCoord") &&
                        !EQUAL(psNode->pszValue, "sceneCornerCoord"))
                        continue;
    
                    poDS->nGCPCount++;
                }
                if (poDS->nGCPCount > 0)
                {
                    poDS->pasGCPList =
                        (GDAL_GCP *)CPLCalloc(sizeof(GDAL_GCP), poDS->nGCPCount);
    
                    /* iterate over GCPs */
                    for (psNode = psSceneInfo->psChild; psNode != nullptr;
                         psNode = psNode->psNext)
                    {
                        GDAL_GCP *psGCP = poDS->pasGCPList + nGCP;
    
                        if (!EQUAL(psNode->pszValue, "sceneCenterCoord") &&
                            !EQUAL(psNode->pszValue, "sceneCornerCoord"))
                            continue;
    
                        psGCP->dfGCPPixel =
                            CPLAtof(CPLGetXMLValue(psNode, "refColumn", "0.0"));
                        psGCP->dfGCPLine =
                            CPLAtof(CPLGetXMLValue(psNode, "refRow", "0.0"));
                        psGCP->dfGCPX =
                            CPLAtof(CPLGetXMLValue(psNode, "lon", "0.0"));
                        psGCP->dfGCPY =
                            CPLAtof(CPLGetXMLValue(psNode, "lat", "0.0"));
                        psGCP->dfGCPZ = dfAvgHeight;
                        psGCP->pszId = CPLStrdup(CPLSPrintf("%d", nGCP));
                        psGCP->pszInfo = CPLStrdup("");
    
                        nGCP++;
                    }
    
                    // set the projection string - the fields are lat/long - seems
                    // to be WGS84 datum
                    poDS->m_oGCPSRS.SetWellKnownGeogCS("WGS84");
                }
            }
    
            // gcps override geotransform - does it make sense to have both??
            if (poDS->nGCPCount > 0)
            {
                poDS->bHaveGeoTransform = FALSE;
                poDS->m_oSRS.Clear();
                poDS->m_gt = GDALGeoTransform();
            }
        }
        else
        {
            CPLError(CE_Warning, CPLE_AppDefined,
                     "Unable to find sceneInfo tag in XML document. "
                     "Proceeding with caution.");
        }
    
        /* -------------------------------------------------------------------- */
        /*      Initialize any PAM information.                                 */
        /* -------------------------------------------------------------------- */
        poDS->SetDescription(poOpenInfo->pszFilename);
        poDS->TryLoadXML();
    
        /* -------------------------------------------------------------------- */
        /*      Check for overviews.                                            */
        /* -------------------------------------------------------------------- */
        poDS->oOvManager.Initialize(poDS.get(), poOpenInfo->pszFilename);
    
        return poDS.release();
    }
    
    /************************************************************************/
    /*                            GetGCPCount()                             */
    /************************************************************************/
    
    int TSXDataset::GetGCPCount()
    {
        return nGCPCount;
    }
    
    /************************************************************************/
    /*                          GetGCPSpatialRef()                          */
    /************************************************************************/
    
    const OGRSpatialReference *TSXDataset::GetGCPSpatialRef() const
    {
        return m_oGCPSRS.IsEmpty() ? nullptr : &m_oGCPSRS;
    }
    
    /************************************************************************/
    /*                              GetGCPs()                               */
    /************************************************************************/
    
    const GDAL_GCP *TSXDataset::GetGCPs()
    {
        return pasGCPList;
    }
    
    /************************************************************************/
    /*                           GetSpatialRef()                            */
    /************************************************************************/
    
    const OGRSpatialReference *TSXDataset::GetSpatialRef() const
    
    {
        return m_oSRS.IsEmpty() ? nullptr : &m_oSRS;
    }
    
    /************************************************************************/
    /*                          GetGeotransform()                           */
    /************************************************************************/
    CPLErr TSXDataset::GetGeoTransform(GDALGeoTransform &gt) const
    {
        gt = m_gt;
    
        if (bHaveGeoTransform)
            return CE_None;
    
        return CE_Failure;
    }
    
    /************************************************************************/
    /*                          GDALRegister_TSX()                          */
    /************************************************************************/
    
    void GDALRegister_TSX()
    {
        if (GDALGetDriverByName("TSX") != nullptr)
            return;
    
        GDALDriver *poDriver = new GDALDriver();
    
        poDriver->SetDescription("TSX");
        poDriver->SetMetadataItem(GDAL_DCAP_RASTER, "YES");
        poDriver->SetMetadataItem(GDAL_DMD_LONGNAME, "TerraSAR-X Product");
        poDriver->SetMetadataItem(GDAL_DMD_HELPTOPIC, "drivers/raster/tsx.html");
        poDriver->SetMetadataItem(GDAL_DCAP_VIRTUALIO, "YES");
    
        poDriver->pfnOpen = TSXDataset::Open;
        poDriver->pfnIdentify = TSXDataset::Identify;
    
        GetGDALDriverManager()->RegisterDriver(poDriver);
    }
    
    ```

