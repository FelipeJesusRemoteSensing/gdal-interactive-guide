# 🔧 Built-ins — Operadores Python

Utilitários padrão do Python essenciais em scripts de geoprocessamento.

---

## os.path.join

**Assinatura:** `os.path.join(path, *paths)`

Constrói caminhos de arquivo de forma segura e multiplataforma. Indispensável em scripts de geoprocessamento.

**Tags:** <span class="tag">caminho</span> <span class="tag">arquivo</span> <span class="tag">path</span> <span class="tag">diretório</span>

```python
import os
pasta = '/dados/rasters'
arquivo = os.path.join(pasta, 'chuva_2024.tif')
print(arquivo)  # /dados/rasters/chuva_2024.tif
```

---

## glob.glob

**Assinatura:** `glob.glob(pathname, recursive=False)`

Lista arquivos usando padrões wildcard. Muito usado para processar múltiplos rasters em lote.

**Tags:** <span class="tag">listar</span> <span class="tag">lote</span> <span class="tag">wildcard</span> <span class="tag">arquivos</span>

```python
import glob
# Listar todos os TIFs em subpastas
arquivos = glob.glob('/dados/**/*.tif', recursive=True)
for arq in arquivos:
    print(arq)
```
