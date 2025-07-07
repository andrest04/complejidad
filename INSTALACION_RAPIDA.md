# Guía de Instalación Rápida

## Instalación Simple (Todas las plataformas)

### Requisitos previos

- Python 3.10 o superior
- Conexión a internet para descargar dependencias

### Pasos

1. Abre una terminal/cmd en la carpeta del proyecto
2. Ejecuta los siguientes comandos uno por uno:

   ```bash
   python -m venv venv
   ```

   **Activar entorno virtual:**
   ```bash
   # En Windows:
   venv\Scripts\activate
   
   # En macOS/Linux:
   source venv/bin/activate
   ```

   **Instalar dependencias y ejecutar:**
   ```bash
   pip install -r requirements.txt
   python run.py
   ```

3. Ve a <http://localhost:5000> en tu navegador

## Solución de problemas comunes

**Error: "Python no está instalado"**
- Descarga Python desde python.org
- Asegúrate de marcar "Add Python to PATH" durante la instalación

**Error: "pip no reconocido"**
- Reinstala Python marcando "Add Python to PATH"
- O usa: `python -m pip install -r requirements.txt`

**Error de dependencias**
- Asegúrate de tener conexión a internet
- Actualiza pip: `python -m pip install --upgrade pip`

**Puerto 5000 ocupado**
- La aplicación se ejecutará en otro puerto automáticamente
- Revisa la terminal para ver el puerto correcto
