🏗️ NexusMold Cloud - B2B SaaS Control Horario y Obras

NexusMold Cloud es una plataforma integral (SaaS) diseñada para la gestión de operarios, control de presencia en taller e imputación automática de horas a proyectos y clientes.

El sistema cuenta con una arquitectura Full-Stack compuesta por una API robusta en Python y una interfaz frontend ágil, permitiendo fichajes en tiempo real desde cualquier dispositivo móvil a pie de obra.

✨ Características Principales

📱 Para los Operarios (App Web Móvil)

Control de Presencia: Fichaje rápido de Entrada/Salida del taller.

Seguridad Avanzada (JWT): Autenticación de un solo uso en la jornada. El servidor emite un "Pase VIP" (JSON Web Token) válido por 11 horas, permitiendo registrar tareas posteriores de forma ágil sin reintroducir contraseñas.

Cronómetro Automático: Sistema inteligente de inicio/fin de tareas que calcula los minutos exactos invertidos en cada obra (código de cliente) automáticamente.

📊 Para Gerencia (Panel de Administración)

Gestión de RRHH: Alta de nuevos operarios con generación de contraseñas de acceso.

Gestión administrativa completa: consulta, edición, restablecimiento de contraseña y eliminación de empleados.

Gestión de Proyectos: Creación de nuevas obras/clientes vinculadas a códigos rápidos de 4 cifras.

Las obras y tareas pueden consultarse, editarse y eliminarse desde el panel Admin; las operaciones requieren un token con rol `Admin`.

Informes y Nóminas: Exportación automática de datos a Excel (CSV), calculando el total de horas trabajadas por cada operario listadas para la gestoría.

🛠️ Stack Tecnológico

Backend: Python, FastAPI, SQLAlchemy, PyJWT.

Base de Datos: SQLite (Migración a PostgreSQL programada).

Frontend: HTML5, JavaScript (ES6+), Tailwind CSS.

Despliegue:

API alojada en Render (Cloud Platform).

Frontend alojado vía GitHub Pages.

🚀 Instalación y Uso Local

Si deseas correr este proyecto en tu entorno local:

Clona el repositorio:

git clone https://github.com/romeostefan56-spec/decomol_backend.git
cd decomol_backend


Instala las dependencias:

pip install -r requirements.txt


Configura antes de iniciar el servidor:

`NEXUS_JWT_SECRET` debe ser una cadena larga y privada. Para producción, define también `NEXUS_CORS_ORIGINS` con los dominios del frontend separados por comas.

Puedes crear automáticamente el primer administrador definiendo `NEXUS_ADMIN_CODE` y `NEXUS_ADMIN_PASSWORD` antes del arranque. Después inicia sesión desde `index.html`, en `Panel Gerencia`; solo ese token permite crear empleados/obras, consultar fichajes y descargar informes.

Inicia el servidor backend:

uvicorn app.main:app --reload
(Asegúrate de ajustar la variable API_BASE_URL en los archivos JS para apuntar a 127.0.0.1:8000 si pruebas en local).

☁️ Base de datos PostgreSQL en Render

1. En Render, crea un recurso `PostgreSQL` en el mismo equipo o cuenta que el servicio web.
2. Elige la región y el plan, y espera a que la base de datos quede disponible.
3. Abre el servicio Web del backend y entra en `Environment`.
4. Añade las variables `DATABASE_URL`, `NEXUS_JWT_SECRET`, `NEXUS_ADMIN_CODE`, `NEXUS_ADMIN_PASSWORD` y `NEXUS_CORS_ORIGINS`.
5. Copia en `DATABASE_URL` la `Internal Database URL` de PostgreSQL cuando el Web Service y la base estén en la misma región. Usa la `External Database URL` solo si conectas desde fuera de Render.
6. En `NEXUS_CORS_ORIGINS`, indica el dominio real del frontend, por ejemplo `https://tu-usuario.github.io`.
7. Guarda los cambios y ejecuta un nuevo deploy del servicio Web.

Cuando `DATABASE_URL` existe, el backend usa PostgreSQL automáticamente y crea las tablas al arrancar. Sin esa variable, conserva SQLite para desarrollo local. No subas estas variables ni sus contraseñas al repositorio.

La API estará disponible en http://127.0.0.1:8000/docs (Swagger UI).

Inicia la interfaz visual:
Abre los archivos index.html (Vista Trabajador) y admin.html (Panel Gerencia) en tu navegador web. (Asegúrate de ajustar la variable API_BASE_URL en los archivos JS para apuntar a 127.0.0.1:8000 si pruebas en local).

🔒 Arquitectura de Seguridad

Este proyecto implementa validación estricta de códigos (mínimo 4 cifras para obras), JWT con expiración para operarios y autorización por rol `Admin` para endpoints de administración. Las nuevas contraseñas se almacenan con hash bcrypt; las contraseñas antiguas en texto plano siguen siendo compatibles durante la migración.

Desarrollado como una solución operativa real para optimización de tiempos y costes en el sector de la construcción/manufactura.