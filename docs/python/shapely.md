# 📐 Shapely — Operadores Python

Manipulação de geometrias: buffer, interseção, união, dissolve e operações topológicas.

---

## shapely.buffer

**Assinatura:** `geometry.buffer(distance, resolution=16)`

Cria um buffer ao redor de uma geometria. Funciona com pontos, linhas e polígonos.

**Tags:** <span class="tag">buffer</span> <span class="tag">zona</span> <span class="tag">distância</span> <span class="tag">geometria</span>

```python
from shapely.geometry import Point
ponto = Point(-49.25, -16.68)
buffer_1km = ponto.buffer(0.01)  # graus
print(buffer_1km.area)
```

---

## shapely.intersection

**Assinatura:** `geom_a.intersection(geom_b)`

Retorna a geometria resultante da interseção entre duas geometrias.

**Tags:** <span class="tag">interseção</span> <span class="tag">overlay</span> <span class="tag">recortar</span> <span class="tag">geometria</span>

```python
from shapely.geometry import Polygon
poly_a = Polygon([(0,0),(2,0),(2,2),(0,2)])
poly_b = Polygon([(1,1),(3,1),(3,3),(1,3)])
result = poly_a.intersection(poly_b)
```

---

## shapely.unary_union

**Assinatura:** `shapely.ops.unary_union(geoms)`

Une (dissolve) uma coleção de geometrias em uma única geometria resultante.

**Tags:** <span class="tag">dissolve</span> <span class="tag">unir</span> <span class="tag">merge</span> <span class="tag">geometrias</span>

```python
from shapely.ops import unary_union
from shapely.geometry import Polygon
polys = [Polygon(...), Polygon(...)]
unido = unary_union(polys)
```
