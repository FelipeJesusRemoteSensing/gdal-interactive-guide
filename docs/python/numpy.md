# 🔢 NumPy — Operadores Python

Operações em arrays essenciais para reclassificação de rasters, aplicação de máscaras e análise estatística.

---

## numpy.where

**Assinatura:** `numpy.where(condition, x, y)`

Aplica condição elemento a elemento em arrays. Muito usado para reclassificação de rasters.

**Tags:** <span class="tag">condicional</span> <span class="tag">reclassificar</span> <span class="tag">máscara</span> <span class="tag">array</span>

```python
import numpy as np
# Reclassificar: valores > 500 = 1, resto = 0
reclassificado = np.where(array > 500, 1, 0)
```

---

## numpy.ma.masked_where

**Assinatura:** `numpy.ma.masked_where(condition, a)`

Cria array mascarado onde a condição é verdadeira. Útil para ignorar nodata em operações.

**Tags:** <span class="tag">máscara</span> <span class="tag">nodata</span> <span class="tag">masked array</span> <span class="tag">raster</span>

```python
import numpy as np
# Mascarar nodata (-9999)
array_masked = np.ma.masked_where(array == -9999, array)
media = array_masked.mean()
```

---

## numpy.histogram

**Assinatura:** `numpy.histogram(a, bins=10, range=None)`

Calcula histograma de valores de um array. Útil para análise de distribuição de valores de raster.

**Tags:** <span class="tag">histograma</span> <span class="tag">estatística</span> <span class="tag">distribuição</span> <span class="tag">análise</span>

```python
import numpy as np
contagens, limites = np.histogram(array.flatten(), bins=50)
print('Faixas de valor:', limites[:5])
```
