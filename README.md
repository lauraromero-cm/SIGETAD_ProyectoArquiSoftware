# SIGETAD SOA - Django + React + Bus TCP + PostgreSQL

Proyecto funcional para el **Sistema de Gestión de Talento y Reclutamiento Digital (SIGETAD)** de FirmaFast.

La arquitectura implementa el flujo:

```text
Frontend React -> Bus TCP/ESB -> Servicios Django -> PostgreSQL
```
## Componentes

- **Frontend:** React + Vite.
- **Backend API:** Django.
- **Bus TCP/ESB:** Python socket server basado y adaptado desde `bus.zip`.
- **Servicios SOA:** apps Django separadas:
  - usuarios
  - vacantes
  - candidatos
  - postulaciones
  - evaluaciones
  - historial
  - documentos
- **Base de datos:** PostgreSQL centralizada.

## Requisitos

- Docker
- Docker Compose

## Levantar el proyecto

```bash
cd sigetad-soa
cp .env.example .env
sudo docker compose up --build
sudo docker-compose build
```

Luego abre:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000/api/health/
Bus TCP:  localhost:5000
```

## Usuarios de prueba

El sistema crea usuarios iniciales automáticamente con el comando `seed_data`.

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@firmafast.cl | admin123 |
| Analista | analista@firmafast.cl | admin123 |
| Jefe de Área | jefe@firmafast.cl | admin123 |
| Candidato | candidato@correo.cl | admin123 |

## Comandos útiles

Entrar al contenedor backend:

```bash
docker compose exec backend bash
```

Ejecutar migraciones manualmente:

```bash
docker compose exec backend python manage.py migrate
```

Cargar datos de prueba:

```bash
docker compose exec backend python manage.py seed_data
```

Ver logs del bus:

```bash
docker compose logs -f bus
```

Ver logs de un servicio SOA:

```bash
docker compose logs -f service_usuarios
```

## Protocolo del Bus TCP

Se mantiene la idea original de `bus.zip`:

```text
[5 bytes largo][5 bytes servicio][payload JSON]
```

Ejemplo:

```json
{
  "action": "listar_vacantes",
  "data": {}
}
```

El bus enruta por código de servicio:

| Servicio | Código TCP |
|---|---|
| Usuarios | USUAR |
| Vacantes | VACAN |
| Candidatos | CANDI |
| Postulaciones | POSTU |
| Evaluaciones | EVALU |
| Historial | HISTO |
| Documentos | DOCUM |

## Documentos PDF

El gateway expone carga `multipart/form-data` y mantiene la operación de negocio dentro de SOA mediante el servicio `DOCUM`.

- `POST /api/documentos/`: sube un PDF en el campo `archivo` o `file`. Opcionalmente acepta `id_postulacion`.
- `GET /api/documentos/`: lista documentos visibles para el usuario autenticado.
- `GET /api/documentos/<id>/url-descarga/`: genera una URL firmada y temporal.
- `GET /api/documentos/<id>/download/?token=...`: descarga usando el token firmado.
- `GET /api/documentos/auditoria/`: lista auditoría de documentos para roles internos.

Validaciones implementadas: extensión PDF, `content-type`, firma `%PDF-`, tamaño máximo configurable, rechazo del archivo de prueba antivirus EICAR y escaneo con `clamscan` cuando está disponible en el contenedor/sistema. La persistencia por defecto es disco local en `backend/uploads/documentos`. Variables relevantes: `MEDIA_ROOT`, `DOCUMENTOS_MAX_UPLOAD_BYTES` y `DOCUMENTOS_DOWNLOAD_TOKEN_SECONDS`.

## Decisión sobre CV y foto de perfil

Para mantener el proyecto simple, funcional y alineado al modelo, el CV y la foto de perfil se guardan como campos de texto (`cv` y `foto_perfil`). Pueden representar una URL, nombre de archivo o ruta. Esto evita complejidad innecesaria con subida binaria por TCP y mantiene el foco en SOA.

## Estructura principal

```text
sigetad-soa/
  backend/
    bus/                  # librería TCP adaptada + servidor ESB
    config/               # settings Django
    gateway/              # capa HTTP para React
    usuarios/             # servicio usuarios
    vacantes/             # servicio vacantes
    candidatos/           # servicio candidatos
    postulaciones/        # servicio postulaciones
    evaluaciones/         # servicio evaluaciones
    historial/            # servicio historial
    soa_services/         # command runner de servicios TCP
  frontend/
    src/
      App.jsx
      api.js
      styles.css
  docker-compose.yml
```

## Notas SOA

- Los servicios son apps separadas dentro del mismo proyecto Django.
- No son microservicios independientes.
- La separación se hace por responsabilidad funcional.
- La comunicación de negocio pasa por el bus TCP.
- PostgreSQL se mantiene como base de datos centralizada.

## Seguridad de Contraseñas

Las contraseñas se almacenan **hasheadas** usando el algoritmo **PBKDF2-SHA256** con los siguientes parámetros:

- **Algoritmo**: PBKDF2 (Password-Based Key Derivation Function 2)
- **Función Hash**: SHA256
- **Iteraciones**: 720,000 (estándar OWASP recomendado)
- **Salt**: Generado automáticamente por Django para cada contraseña
- **Mecanismo**: Implementado por defecto en Django mediante `django.contrib.auth.hashers.PBKDF2PasswordHasher`

**Características de seguridad**:
- ✅ Las contraseñas nunca se almacenan en texto plano
- ✅ Es computacionalmente costoso intentar descifrar una contraseña hasheada
- ✅ Cada contraseña tiene su propio salt, previniendo ataques por diccionario
- ✅ Compatible con los estándares de seguridad actuales (OWASP, NIST)

**Configuración**: Ver `backend/config/settings.py` en la sección `PASSWORD_HASHERS`
