# **Ecommerce Application**

¡Bienvenido al repositorio de **Ecommerce Application**! Este proyecto es una aplicación de comercio electrónico construida con Django, Bootstrap y PostgreSQL. Está diseñado para ser ejecutado fácilmente en cualquier entorno utilizando Docker.

## **Características**
- Gestión de usuarios (Clientes, Distribuidores y Administradores).
- Carrito de compras con sistema de órdenes.
- Gestión de productos y categorías.
- Compatible con PostgreSQL como base de datos.
- Implementación lista para despliegue con Docker.

---

## **Requisitos**
Antes de comenzar, asegúrate de tener las siguientes herramientas instaladas en tu máquina:
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## **Clonar el proyecto**
Clona este repositorio en tu máquina local utilizando:
```bash
https://github.com/OliverVlz/e-comerce.git
cd ecommerce
```

---



## **Ejecución del proyecto con Docker**

1. **Construir y levantar los servicios**
   Utiliza Docker Compose para construir y ejecutar el proyecto:
   ```bash
   docker-compose up --build
   ```

2. **Acceder a la aplicación**
   Una vez que Docker haya levantado todos los servicios, accede a la aplicación desde tu navegador en:
   ```
   http://localhost:8000
   ```

3. ### Miniguía para ingresar a **pgAdmin** con las configuraciones actuales:

    #### **Paso 1: Acceder a pgAdmin**
    1. Abre tu navegador y dirígete a `http://localhost`.
    2. Inicia sesión utilizando las credenciales configuradas en tu archivo `docker-compose.yml`:
       - **Correo**: `admin@admin.com`
       - **Contraseña**: `admin`
    
    ---
    
    #### **Paso 2: Configurar un nuevo servidor en pgAdmin**
    1. Haz clic en **"Agregar un Nuevo Servidor"**.
    2. En la pestaña **General**:
       - Asigna un nombre al servidor, como: `PostgreSQL Local`.
    
    3. Cambia a la pestaña **Conexión** y completa los campos:
       - **Nombre/Dirección del servidor**: `db` (es el nombre del servicio configurado en Docker).
       - **Puerto**: `5432` (puerto estándar para PostgreSQL).
       - **Base de datos de mantenimiento**: `postgres` (base de datos inicial).
       - **Nombre de usuario**: `postgres`.
       - **Contraseña**: `postgres`.
    
    4. Haz clic en **Salvar**.

---

#### **Paso 3: Ver la base de datos y tablas**
1. En el panel izquierdo, selecciona el servidor recién configurado (`PostgreSQL Local`).
2. Navega a:
   - **Bases de Datos → ecommerce1.0 → Schemas → public → Tables**.
3. Aquí puedes explorar y administrar las tablas, datos y relaciones.

---

## **Comandos útiles**

### **Crear un superusuario**
Para crear un superusuario, ejecuta este comando dentro del contenedor:
```bash
docker exec -it ecommerce_web python manage.py createsuperuser
```

### **Aplicar migraciones**
Si realizas cambios en los modelos de Django, aplica las migraciones con:
```bash
docker exec -it ecommerce_web python manage.py makemigrations
docker exec -it ecommerce_web python manage.py migrate
```

### **Acceder a la base de datos**
Para interactuar directamente con la base de datos:
```bash
docker exec -it ecommerce_db psql -U postgres -d ecommerce1.0
```

---

