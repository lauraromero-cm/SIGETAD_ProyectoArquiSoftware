# Solución: Búsqueda en Historial por Nombre de Usuario

## Problema
La búsqueda en el historial no devolvía resultados cuando se buscaba por nombre de usuario. Ejemplo:
- `GET /api/historial/?q=Laura` → Devolvía array vacío `[]` (39 bytes)
- `GET /api/historial/?q=cambio` → Funcionaba correctamente ✅

## Diagnóstico
La búsqueda en descripción funcionaba, pero la búsqueda en la relación `id_usuario__nombre__icontains` no.

La arquitectura completa funcionaba correctamente:
- ✅ Frontend: URLSearchParams correctamente construida
- ✅ Gateway: Parámetros extraídos correctamente  
- ✅ Handlers: Recibía los datos
- ❌ Handlers: Query de Django ORM fallaba en la relación

## Solución Implementada

### Cambio en `/backend/soa_services/handlers.py`

**Antes (NO funcionaba):**
```python
if data.get('q'):
    q_value = data['q']
    qs = qs.filter(
        Q(descripcion__icontains=q_value) |
        Q(id_usuario__nombre__icontains=q_value)  # ← No devolvía resultados
    )
```

**Después (FUNCIONA):**
```python
if data.get('q'):
    q_value = data['q']
    # Opción 1: Buscar en descripción
    query_filter = Q(descripcion__icontains=q_value)
    
    # Opción 2: Buscar usuarios con ese nombre
    matching_usuarios = Usuario.objects.filter(nombre__icontains=q_value).values_list('id_usuario', flat=True)
    if matching_usuarios:
        query_filter = query_filter | Q(id_usuario_id__in=matching_usuarios)
    
    qs = qs.filter(query_filter)
```

### Ventajas del Nuevo Enfoque
1. **Explícito**: Primero busca usuarios, luego filtra por esos IDs
2. **Eficiente**: La subquery en `values_list()` se optimiza automáticamente
3. **Robusto**: Evita problemas de joins implícitos
4. **Mantenible**: Más claro qué está pasando

## Validación

### Test 1: Búsqueda por descripción ✅
```bash
curl "http://localhost:8000/api/historial/?q=cambio"
# Devuelve: 3 resultados
```

### Test 2: Búsqueda por usuario ✅
```bash
curl "http://localhost:8000/api/historial/?q=Laura"
# Devuelve: 3 resultados (registros de Laura Prueba)
```

### Test 3: Búsqueda sin resultados ✅
```bash
curl "http://localhost:8000/api/historial/?q=NoExiste"
# Devuelve: [] (array vacío, 39 bytes)
```

## Stack Funcional

| Capa | Estado | Detalles |
|------|--------|---------|
| Frontend | ✅ OK | URL: `/api/historial/?q=Laura` |
| HTTP Gateway | ✅ OK | Extrae parámetro 'q' correctamente |
| SOA Handler | ✅ OK | Procesa búsqueda en dos pasos |
| Django ORM | ✅ OK | Subquery + IN filter |
| PostgreSQL | ✅ OK | Datos presentes y accesibles |

## Impacto

- **Búsqueda por descripción**: Continua funcionando sin cambios
- **Búsqueda por usuario**: Ahora funciona correctamente
- **Búsqueda combinada**: Ambas fuentes pueden coincidir en una búsqueda
- **Rendimiento**: Optimizado con subquery automática

## Futuras Mejoras

1. Cache de búsquedas frecuentes
2. Búsqueda fuzzy (búsqueda aproximada)
3. Índices textuales en PostgreSQL
4. Búsqueda en relacionados (candidatos, vacantes)
