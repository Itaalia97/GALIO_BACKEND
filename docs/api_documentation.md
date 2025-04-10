### [Inicio de la API]

**URL:** `/`

**Método:** `GET`

**Autenticación requerida:** No

**Descripción:** Muestra una lista de los endpoints disponibles en la API.

---

### [Home de la API]

**URL:** `/home/`

**Método:** `GET`

**Autenticación requerida:** No

**Descripción:** Vista simple de prueba del backend.

---

### [Login de usuario]

**URL:** `/login/`

**Método:** `POST`

**Autenticación requerida:** No

**Descripción:** Autentica al usuario y devuelve datos del usuario y token JWT.

**Cuerpo:**
```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

**Respuesta exitosa (200):**
```json
{
  "refresh": "token_refresh",
  "access": "token_access",
  "username": "usuario",
  "imagen_enunciado_url": "http://..."
}
```

---

### [Obtener token JWT]

**URL:** `/api-token-auth/`

**Método:** `POST`

**Autenticación requerida:** No

**Descripción:** Obtiene los tokens de acceso y refresco mediante JWT.

**Cuerpo:**
```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

**Respuesta exitosa (200):**
```json
{
  "refresh": "token_refresh",
  "access": "token_access"
}
```

---

### [Refrescar token JWT]

**URL:** `/api/token/refresh/`

**Método:** `POST`

**Autenticación requerida:** No

**Descripción:** Renueva el token de acceso con un token de refresco válido.

**Cuerpo:**
```json
{
  "refresh": "token_refresh"
}
```

**Respuesta exitosa (200):**
```json
{
  "access": "nuevo_token_access"
}
```

---

### [Registro de usuario]

**URL:** `/registro/`

**Método:** `POST`

**Autenticación requerida:** No

**Descripción:** Registra un nuevo usuario en la plataforma.

**Cuerpo:**
```json
{
  "username": "nuevo_usuario",
  "email": "correo@quimica.unam.mx",
  "password": "contraseña"
}
```

**Respuesta exitosa (201):**
```json
{
  "message": "Usuario registrado exitosamente."
}
```

---

### [Lista o creación de ejercicios]

**URL:** `/ejercicios/`

**Método:** `GET`, `POST`

**Autenticación requerida:** Sí (JWT)

**Descripción:** Obtiene la lista o crea nuevos ejercicios.

---

### [Detalle de un ejercicio]

**URL:** `/ejercicios/<id>/`

**Método:** `GET`

**Autenticación requerida:** Sí (JWT)

**Descripción:** Devuelve el detalle del ejercicio según su ID.

**Respuesta exitosa (200):**
```json
{
  "id": 25,
  "dia": "2025-02-24",
  "enunciado": "¿Cuál es la concentración final del ion Na⁺?",
  "imagen_enunciado_url": "http://galio.proyectoplata.com/media/enunciados/ejercicio_25.png",
  "respuesta_corta": "0.0025 mol·L⁻¹"
}
```

---

### [Enviar respuesta del usuario]

**URL:** `/respuesta_usuario/`

**Método:** `POST`

**Autenticación requerida:** Sí (JWT)

**Descripción:** Envía la respuesta del usuario para el ejercicio del día.

**Body (form-data):**
- `ejercicio`: ID del ejercicio
- `respuesta_usuario`: Texto de la respuesta

**Respuesta exitosa (201):**
```json
{
  "respuesta_correcta_corta": "98.08 g/mol",
  "mensaje": "Respuesta enviada exitosamente."
}
```

---

### [Ver respuesta por fecha]

**URL:** `/respuestas_usuario_fecha/?fecha=AAAA-MM-DD`

**Método:** `GET`

**Autenticación requerida:** Sí (JWT)

**Descripción:** Devuelve el enunciado, la respuesta enviada por el usuario y la resolución correspondiente a una fecha dada.

**Respuesta exitosa (200):**
```json
{
  "dia": "2025-02-26",
  "enunciado": "Reacciona el NaOH con HCl...",
  "imagen_enunciado_url": "...",
  "respuesta_usuario": "NaCl + H2O",
  "resolucion": "La neutralización ácido-base genera una sal y agua.",
  "imagen_resolucion_url": "..."
}
```

---

### [Leaderboard - Tablero de posiciones]

**URL:** `/leaderboard/`

**Método:** `GET`

**Autenticación requerida:** Sí (JWT)

**Descripción:** Muestra las 20 mejores rachas de usuarios y las 20 mayores cantidades de ejercicios enviados.

**Respuesta exitosa (200):**
```json
{
  "top_20_racha": [
    { "posicion": 1, "usuario": "juanito", "racha": 6 },
    ...
  ],
  "usuario_logeado_racha": {
    "posicion": 3,
    "usuario": "maria",
    "racha": 4
  },
  "top_20_totales": [
    { "posicion": 1, "usuario": "lucas", "total_ejercicios": 28 },
    ...
  ],
  "usuario_logeado_totales": {
    "posicion": 5,
    "usuario": "maria",
    "total_ejercicios": 16
  }
}
```

---

### [Solicitar recuperación de contraseña]

**URL:** `/solicitar-recuperacion/`

**Método:** `GET`

**Autenticación requerida:** No

**Descripción:** Devuelve el formulario HTML de recuperación.

---

### [Enviar correo para recuperar contraseña]

**URL:** `/recuperar-contrasena-enviar/`

**Método:** `POST`

**Autenticación requerida:** No

**Descripción:** Envía un email con el enlace para restablecer contraseña.

**Body:**
```json
{
  "email": "usuario@quimica.unam.mx"
}
```

**Respuesta exitosa (200):**
```json
{
  "message": "Se ha enviado un correo electrónico para restablecer la contraseña."
}
```

---

### [Restablecer contraseña]

**URL:** `/restablecer-contrasena/<uidb64>/<token>/`

**Método:** `POST`

**Autenticación requerida:** No

**Descripción:** Permite establecer una nueva contraseña para el usuario.

**Body:**
```json
{
  "new_password": "nueva_contrasena"
}
```

**Respuesta exitosa (200):**
```json
{
  "message": "Contraseña restablecida exitosamente.",
  "note": "Tu nombre de usuario es: maria. Asegúrate de recordarlo junto con tu nueva contraseña."
}
```

---

### [Lista de usuarios]

**URL:** `/users/`

**Método:** `GET`

**Autenticación requerida:** Sí (JWT)

**Descripción:** Muestra una lista de todos los usuarios registrados.

---

### [Enviar correo de prueba]

**URL:** `/enviar-correo-prueba/`

**Método:** `GET`

**Autenticación requerida:** Sí (JWT)

**Descripción:** Envía un correo de prueba para verificar la configuración de correo.

