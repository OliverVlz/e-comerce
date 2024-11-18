# **Ecommerce Application**

¡Bienvenido al repositorio de **Ecommerce Application**! Este proyecto es una aplicación de comercio electrónico construida con Django y PostgreSQL. Está diseñado para ser ejecutado fácilmente en cualquier entorno utilizando Docker.

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

## **Configuración inicial**

### **Variables de entorno**
Edita el archivo `settings.py` o utiliza un archivo `.env` (si lo implementas) para definir las variables de configuración:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ecommerce1.0',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}
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

3. **Acceder a pgAdmin**
   Si necesitas acceder a la base de datos, puedes usar pgAdmin:
   ```
   http://localhost
   ```
   **Credenciales de acceso:**
   - Usuario: `admin@admin.com`
   - Contraseña: `admin`

4. **Cargar un backup de la base de datos (opcional)**
   Si tienes un backup existente, colócalo en el directorio raíz del proyecto y asegúrate de que esté referenciado en el `docker-compose.yml`:
   ```yml
   volumes:
     - ./backup.sql:/docker-entrypoint-initdb.d/backup.sql
   ```

   Luego, reconstruye los contenedores:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

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

