# Usa una imagen oficial de Python como base
FROM python:3.10-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requisitos e instala dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto en el contenedor
COPY . /app/

# Exponer el puerto 8000 para el servidor de desarrollo
EXPOSE 8000

# Comando por defecto para ejecutar el contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
