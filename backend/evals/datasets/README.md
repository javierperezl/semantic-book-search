# Conjunto de evaluación fijo

Este archivo (`queries.json`) es el conjunto de consultas de prueba para
**todos** los experimentos (embeddings, generación, intención, representación
semántica, pipeline de recuperación, número de candidatos).

## Regla de oro
**No modificar este archivo una vez empezada la experimentación.**
Si se agregan o cambian queries a mitad de camino, los resultados de
experimentos ya corridos dejan de ser comparables contra los nuevos.

Si en algún momento se detecta que falta cubrir un caso importante,
agregarlo es válido, pero implica **re-correr todos los experimentos
anteriores** contra el set actualizado, no solo el siguiente.

## Categorías (según el plan de experimentos del equipo)
- `libros_similares` — "libros como X pero..."
- `libros_sobre_tema` — tema explícito, sin libro de referencia
- `perfil_especifico` — libro para un tipo de lector (nivel, edad, experiencia)
- `comparacion` — pide comparar dos libros o decidir entre ellos
- `ambigua` — sin tema ni preferencia clara, prueba que el sistema no fuerce un match
- `muy_especifica` — nicho poco común, prueba el comportamiento con pocos candidatos
- `amplia` — género o tema genérico con muchos candidatos posibles
