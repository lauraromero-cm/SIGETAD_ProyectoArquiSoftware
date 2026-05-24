# Especificación de Contratos de Datos - SIGETAD SOA

Este documento describe los contratos de datos, serialización de mensajes y estructura de intercambio entre clientes, ESB y servicios en la arquitectura SOA de SIGETAD.

## 1. Protocolo de Comunicación General

### 1.1 Estructura del Mensaje en Tránsito

Todos los mensajes que pasan por el ESB (Bus TCP) siguen el formato:

```
[5 bytes LONGITUD][5 bytes SERVICIO][PAYLOAD JSON]
```

**Campos:**
- `LONGITUD`: Número decimal de 5 dígitos (rellenado a la izquierda con ceros) indicando el tamaño en bytes del resto del mensaje
- `SERVICIO`: Código exactamente de 5 caracteres que identifica el servicio destino
- `PAYLOAD`: Contenido JSON con la solicitud o respuesta

**Ejemplo (transmisión TCP):**
```
00045USUAR{"action":"login","data":{"correo":"admin@firmafast.cl","contrasena":"admin123"},"user":{}}
```

### 1.2 Estructura del Payload JSON

Tanto solicitudes como respuestas usan JSON. La estructura depende de si es cliente→ESB o servicio→ESB.

**Solicitud (Cliente → ESB):**
```json
{
  "action": "nombre_de_la_accion",
  "data": { /* parámetros específicos */ },
  "user": { /* información del usuario autenticado */ }
}
```

**Respuesta (Servicio → ESB → Cliente):**
```json
{
  "ok": boolean,
  "error": string | null,
  "data": any
}
```

---

## 2. Mapeo de Códigos de Servicio

| Código | Servicio | Descripción |
|--------|----------|-------------|
| USUAR | usuarios | Autenticación y gestión de usuarios |
| VACAN | vacantes | Gestión de vacantes de empleo |
| CANDI | candidatos | Perfiles y datos de candidatos |
| POSTU | postulaciones | Gestión de postulaciones |
| EVALU | evaluaciones | Evaluaciones de candidatos |
| HISTO | historial | Auditoría y registro de cambios |

---

## 3. Servicios y Contratos

### 3.1 USUAR - Servicio de Usuarios

#### 3.1.1 Acción: `login`

**Descripción:** Autenticar usuario con credenciales

**Solicitud:**
```json
{
  "action": "login",
  "data": {
    "correo": "string",           // Obligatorio
    "contrasena": "string"        // Obligatorio
  },
  "user": {}                      // Usuario no autenticado
}
```

**Respuesta (Éxito):**
```json
{
  "ok": true,
  "error": null,
  "data": {
    "id_usuario": 1,              // integer
    "nombre": "Admin",            // string
    "correo": "admin@firmafast.cl", // string
    "rol": "admin",               // enum: admin|analista|jefe_area|candidato
    "estado": "activo"            // enum: activo|inactivo
  }
}
```

**Respuesta (Error):**
```json
{
  "ok": false,
  "error": "Credenciales inválidas",
  "data": null
}
```

---

#### 3.1.2 Acción: `registrar_candidato_usuario`

**Descripción:** Registrar nuevo candidato (sin autenticación requerida)

**Solicitud:**
```json
{
  "action": "registrar_candidato_usuario",
  "data": {
    "nombre": "string",           // Obligatorio
    "nombre_completo": "string",  // Alternativa a nombre
    "correo": "string",           // Obligatorio
    "email": "string",            // Alternativa a correo
    "contrasena": "string",       // Opcional, default: "admin123"
    "telefono": "string",         // Opcional
    "profesion": "string",        // Opcional
    "experiencia_anios": "0|1|2|3|4|5+", // Opcional
    "cv": "string",               // URL o texto, opcional
    "foto_perfil": "string"       // URL o texto, opcional
  },
  "user": {}
}
```

**Respuesta (Éxito):**
```json
{
  "ok": true,
  "error": null,
  "data": {
    "usuario": {
      "id_usuario": 2,
      "nombre": "Juan Pérez",
      "correo": "juan@mail.com",
      "rol": "candidato",
      "estado": "activo"
    },
    "candidato": {
      "id_candidato": 1,
      "id_usuario": 2,
      "nombre_completo": "Juan Pérez",
      "email": "juan@mail.com",
      "telefono": "912345678",
      "profesion": "Ingeniero",
      "experiencia_anios": "2",
      "cv": "https://...",
      "foto_perfil": "https://..."
    }
  }
}
```

---

#### 3.1.3 Acción: `crear_usuario` (requiere rol `admin`)

**Descripción:** Crear nuevo usuario (solo administradores)

**Solicitud:**
```json
{
  "action": "crear_usuario",
  "data": {
    "nombre": "string",           // Obligatorio
    "correo": "string",           // Obligatorio
    "rol": "string",              // Obligatorio: admin|analista|jefe_area|candidato
    "contrasena": "string",       // Opcional, default: "admin123"
    "estado": "string"            // Opcional: activo|inactivo
  },
  "user": {
    "id_usuario": 1,
    "rol": "admin"
  }
}
```

**Respuesta (Éxito):** Usuario creado (mismo formato que login)

---

#### 3.1.4 Acción: `listar_usuarios` (requiere rol `admin`)

**Solicitud:**
```json
{
  "action": "listar_usuarios",
  "data": {},
  "user": { "id_usuario": 1, "rol": "admin" }
}
```

**Respuesta (Éxito):**
```json
{
  "ok": true,
  "error": null,
  "data": [
    { "id_usuario": 1, "nombre": "Admin", "correo": "admin@...", "rol": "admin", "estado": "activo" },
    { "id_usuario": 2, "nombre": "Juan", "correo": "juan@...", "rol": "candidato", "estado": "activo" }
  ]
}
```

---

### 3.2 VACAN - Servicio de Vacantes

#### 3.2.1 Acción: `listar_vacantes`

**Descripción:** Listar vacantes (por defecto solo abiertas)

**Solicitud:**
```json
{
  "action": "listar_vacantes",
  "data": {
    "solo_abiertas": true        // Opcional, default: true
  },
  "user": {}
}
```

**Respuesta (Éxito):**
```json
{
  "ok": true,
  "error": null,
  "data": [
    {
      "id_vacante": 1,           // integer
      "titulo": "Developer Senior",       // string
      "descripcion": "Buscamos...", // string
      "departamento": "TI",       // string
      "salario_minimo": 1500000,  // number
      "salario_maximo": 2500000,  // number
      "requisitos": "Python, Django",    // string
      "estado": "abierta",        // enum: abierta|cerrada
      "fecha_creacion": "2026-05-24",    // ISO date
      "creado_por": 1             // id del usuario
    }
  ]
}
```

---

#### 3.2.2 Acción: `crear_vacante` (requiere rol `admin|analista`)

**Solicitud:**
```json
{
  "action": "crear_vacante",
  "data": {
    "titulo": "string",           // Obligatorio
    "descripcion": "string",      // Obligatorio
    "departamento": "string",     // Obligatorio
    "salario_minimo": "number",   // Obligatorio
    "salario_maximo": "number",   // Obligatorio
    "requisitos": "string",       // Opcional
    "estado": "abierta"           // Opcional, default: abierta
  },
  "user": { "id_usuario": 1, "rol": "admin" }
}
```

**Respuesta (Éxito):** Vacante creada (mismo formato que listar)

---

#### 3.2.3 Acción: `cerrar_vacante` (requiere rol `admin|analista`)

**Solicitud:**
```json
{
  "action": "cerrar_vacante",
  "data": {
    "id_vacante": 1              // Obligatorio
  },
  "user": { "id_usuario": 1, "rol": "admin" }
}
```

**Respuesta (Éxito):** Vacante con estado `cerrada`

---

### 3.3 CANDI - Servicio de Candidatos

#### 3.3.1 Acción: `mi_perfil` (requiere rol `candidato`)

**Solicitud:**
```json
{
  "action": "mi_perfil",
  "data": {},
  "user": { "id_usuario": 2, "rol": "candidato" }
}
```

**Respuesta (Éxito):**
```json
{
  "ok": true,
  "error": null,
  "data": {
    "id_candidato": 1,
    "id_usuario": 2,
    "nombre_completo": "Juan Pérez",
    "email": "juan@mail.com",
    "telefono": "912345678",
    "profesion": "Ingeniero",
    "experiencia_anios": "2",
    "cv": "https://...",
    "foto_perfil": "https://...",
    "fecha_registro": "2026-05-20"
  }
}
```

---

#### 3.3.2 Acción: `guardar_perfil` (requiere rol `candidato`)

**Solicitud:**
```json
{
  "action": "guardar_perfil",
  "data": {
    "nombre_completo": "string",       // Opcional
    "email": "string",                 // Opcional
    "telefono": "string",              // Opcional
    "profesion": "string",             // Opcional
    "experiencia_anios": "0|1|2|3|4|5+",  // Opcional
    "cv": "string",                    // Opcional
    "foto_perfil": "string"            // Opcional
  },
  "user": { "id_usuario": 2, "rol": "candidato" }
}
```

**Respuesta (Éxito):** Perfil actualizado (mismo formato que mi_perfil)

---

#### 3.3.3 Acción: `listar_candidatos` (requiere rol `admin|analista|jefe_area`)

**Solicitud:**
```json
{
  "action": "listar_candidatos",
  "data": {
    "q": "string"                 // Opcional: busca en nombre, email o profesión
  },
  "user": { "id_usuario": 1, "rol": "admin" }
}
```

**Respuesta (Éxito):** Array de perfiles candidato (formato idéntico al de mi_perfil)

---

### 3.4 POSTU - Servicio de Postulaciones

#### 3.4.1 Acción: `postular` (requiere rol `candidato`)

**Solicitud:**
```json
{
  "action": "postular",
  "data": {
    "id_vacante": 1,              // Obligatorio
    "notas": "string"             // Opcional
  },
  "user": { "id_usuario": 2, "rol": "candidato" }
}
```

**Respuesta (Éxito):**
```json
{
  "ok": true,
  "error": null,
  "data": {
    "id_postulacion": 5,          // integer
    "id_candidato": 1,            // integer
    "id_vacante": 1,              // integer
    "candidato_nombre": "Juan Pérez",   // string
    "vacante_titulo": "Developer Senior", // string
    "estado": "postulado",        // enum: postulado|en_revision|entrevista|evaluacion|finalista|rechazado|contratado
    "notas": "",                  // string
    "fecha_postulacion": "2026-05-24"   // ISO date
  }
}
```

---

#### 3.4.2 Acción: `listar_postulaciones`

**Solicitud:**
```json
{
  "action": "listar_postulaciones",
  "data": {
    "id_vacante": 1,              // Opcional
    "estado": "postulado",        // Opcional
    "q": "string"                 // Opcional: búsqueda
  },
  "user": { "id_usuario": 2, "rol": "candidato" }
}
```

**Respuesta (Éxito):** Array de postulaciones (formato idéntico al de postular)

---

#### 3.4.3 Acción: `actualizar_estado` (requiere rol `admin|analista`)

**Solicitud:**
```json
{
  "action": "actualizar_estado",
  "data": {
    "id_postulacion": 5,          // Obligatorio
    "estado": "en_revision",      // Obligatorio
    "notas": "string"             // Opcional
  },
  "user": { "id_usuario": 1, "rol": "admin" }
}
```

**Respuesta (Éxito):** Postulación actualizada

---

### 3.5 EVALU - Servicio de Evaluaciones

#### 3.5.1 Acción: `registrar_evaluacion` (requiere rol `admin|jefe_area|analista`)

**Solicitud:**
```json
{
  "action": "registrar_evaluacion",
  "data": {
    "id_postulacion": 5,          // Obligatorio
    "calificacion": 4,            // Obligatorio: 1-5
    "comentarios": "string"       // Opcional
  },
  "user": { "id_usuario": 1, "rol": "admin" }
}
```

**Respuesta (Éxito):**
```json
{
  "ok": true,
  "error": null,
  "data": {
    "id_evaluacion": 1,
    "id_postulacion": 5,
    "id_usuario": 1,
    "calificacion": 4,
    "comentarios": "Entrevista exitosa",
    "fecha_evaluacion": "2026-05-24"
  }
}
```

---

### 3.6 HISTO - Servicio de Historial

#### 3.6.1 Acción: `listar_historial`

**Solicitud:**
```json
{
  "action": "listar_historial",
  "data": {
    "id_postulacion": 5           // Opcional: filtrar por postulación
  },
  "user": { "id_usuario": 1, "rol": "admin" }
}
```

**Respuesta (Éxito):**
```json
{
  "ok": true,
  "error": null,
  "data": [
    {
      "id_historial": 1,
      "id_postulacion": 5,      // integer | null
      "tipo": "postulacion",    // enum: postulacion|estado|evaluacion|evento
      "descripcion": "Candidato postuló a Developer Senior",
      "id_usuario": 2,
      "usuario_nombre": "Juan Pérez",
      "fecha_evento": "2026-05-24T10:30:00"
    }
  ]
}
```

---

## 4. Tipos de Datos y Validaciones

### Enumeraciones

**Roles de Usuario:**
- `admin`: Administrador del sistema
- `analista`: Analista de reclutamiento
- `jefe_area`: Jefe de área
- `candidato`: Candidato postulante

**Estados de Usuario:**
- `activo`: Usuario activo
- `inactivo`: Usuario inactivo

**Estados de Vacante:**
- `abierta`: Vacante abierta para postulaciones
- `cerrada`: Vacante cerrada

**Estados de Postulación:**
- `postulado`: Inicial
- `en_revision`: En revisión
- `entrevista`: Entrevista programada
- `evaluacion`: En evaluación
- `finalista`: Candidato finalista
- `rechazado`: Rechazado
- `contratado`: Contratado

**Años de Experiencia:**
- `0`: Sin experiencia
- `1`: 1 año
- `2`: 2 años
- `3`: 3 años
- `4`: 4 años
- `5+`: 5 o más años

**Tipos de Historial:**
- `postulacion`: Nueva postulación
- `estado`: Cambio de estado
- `evaluacion`: Nueva evaluación
- `evento`: Evento personalizado

---

## 5. Manejo de Errores

Cuando ocurre un error, la respuesta tiene:

```json
{
  "ok": false,
  "error": "Descripción del error",
  "data": null
}
```

**Errores Comunes:**

| Error | Causa |
|-------|-------|
| "Credenciales inválidas" | Correo o contraseña incorrectos en login |
| "Op no reconocida" | Action no existe para el servicio |
| "No tienes permisos" | Usuario sin rol requerido |
| "Recurso no encontrado" | ID no existe en la BD |
| "Campo obligatorio faltante" | Datos incompletos en la solicitud |

---

## 6. Flujo de Datos Completo - Ejemplo

### Ejemplo: Candidato postula a vacante

**1. Cliente obtiene lista de vacantes**

Cliente → ESB:
```
00096VACAN{"action":"listar_vacantes","data":{"solo_abiertas":true},"user":{}}
```

ESB → Servicio VACAN:
```json
{
  "action": "listar_vacantes",
  "data": {"solo_abiertas": true},
  "user": {}
}
```

Servicio VACAN → ESB:
```json
{
  "ok": true,
  "error": null,
  "data": [
    { "id_vacante": 1, "titulo": "Developer", ... }
  ]
}
```

ESB → Cliente:
```
00150VACAN{"ok":true,"error":null,"data":[{"id_vacante":1,"titulo":"Developer",...}]}
```

---

**2. Candidato se autentica**

Cliente → ESB:
```
00095USUAR{"action":"login","data":{"correo":"juan@mail.com","contrasena":"pass123"},"user":{}}
```

Servicio USUAR → ESB → Cliente:
```json
{
  "ok": true,
  "error": null,
  "data": { "id_usuario": 2, "rol": "candidato" }
}
```

---

**3. Candidato realiza postulación**

Cliente → ESB (con user autenticado):
```
00120POSTU{"action":"postular","data":{"id_vacante":1,"notas":"Interesado"},"user":{"id_usuario":2,"rol":"candidato"}}
```

Servicio POSTU → ESB → Cliente:
```json
{
  "ok": true,
  "error": null,
  "data": {
    "id_postulacion": 5,
    "estado": "postulado",
    "fecha_postulacion": "2026-05-24"
  }
}
```

---

## 7. Notas de Implementación

- **Serialización:** JSON UTF-8
- **Formato de fechas:** ISO 8601 (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
- **Números:** Sin miles separadores, punto decimal
- **Strings:** Sin límite especificado (validar en cliente si es necesario)
- **Null:** Representado como `null` en JSON
- **Arrays:** Siempre son arrays, incluso si están vacíos `[]`

