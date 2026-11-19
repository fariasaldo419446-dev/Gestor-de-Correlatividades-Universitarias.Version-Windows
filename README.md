# 🎓 Gestor de Correlatividades Universitarias (Escritorio)

Aplicación de escritorio para gestionar y visualizar el plan de estudios (UTN, UNC, etc.). Permite llevar el control del estado académico, visualizando materias por niveles y verificando automáticamente el estado de las correlatividades.

## 🚀 Características
* **Control de Estado:** Marca materias como *No Cursada, Regular, Cursando* o *Aprobada*.
* **Validación de Correlatividades:** El sistema habilita o bloquea materias automáticamente según si cumples con las correlativas (regulares o aprobadas) necesarias.
* **Progreso y disponibilidad:** Muestra cuántas materias aprobaste y cuáles ya se encuentran habilitadas para cursar.
* **Explicación de bloqueos:** Al abrir una materia, indica exactamente qué correlativas falta regularizar o aprobar.
* **Persistencia segura:** El progreso se guarda automáticamente en el perfil de Windows y no depende de la carpeta desde la que abras el `.exe`.
* **Interfaz Moderna:** Desarrollada con **CustomTkinter** para una apariencia limpia y amigable.
* **Portable:** Se puede compilar en un solo archivo `.exe` que no requiere instalación.

## 🛠 Tecnologías Utilizadas
* **Lenguaje:** Python 3.12+
* **Interfaz Gráfica (GUI):** CustomTkinter
* **Compilación:** PyInstaller (vía script automatizado)
* **Datos:** JSON (Almacenamiento local)

## 📂 Estructura del Proyecto
* `main.py`: Código fuente principal de la aplicación.
* `Crear app windows.bat`: Script automatizado para compilar el proyecto a `.exe` en un solo clic.
* `requirements.txt`: Dependencia de la interfaz.
* `estado_materias.json`: Archivo generado automáticamente con tu progreso dentro del perfil de usuario.

## 💿 Como generar el Ejecutable (.exe)

Si descargaste el código fuente y quieres crear tu propio ejecutable para Windows:

1. Asegúrate de tener **Python** instalado (marcando la casilla "Add to PATH").
2. Conservá todos los archivos del repositorio en la misma carpeta.
3. Haz doble clic en **`Crear app windows.bat`**.
4. ¡Listo! El script instalará las dependencias necesarias, compilará el programa y te dejará el archivo `.exe` listo para usar en esa misma carpeta.

<img width="1359" height="717" alt="App" src="https://github.com/user-attachments/assets/aac15f78-cd1c-460b-964c-af2c533969e6" />

## 📋 Requisitos para correr desde código (sin compilar)
Si prefieres ejecutar el script `main.py` directamente desde tu editor:
```bash
pip install -r requirements.txt
python main.py


