# Tamizaje de riesgo de anemia infantil

Aplicación web que estima el riesgo de anemia en niños de 6 a 35 meses en el Perú mediante una
red bayesiana entrenada con la ENDES 2024 del INEI (criterio de anemia OMS 2024).

Proyecto del curso Sistemas Basados en el Conocimiento, Escuela de Informática,
Universidad Nacional de Trujillo, 2026. Autores: Charcape Rodríguez Joaquín,
Díaz Zegarra Diego Jhonatan y Jara Solorzano Dylan Nikolas.

> La herramienta no diagnostica la anemia ni reemplaza la medición de hemoglobina.

## Contenido

| Archivo | Descripción |
|---|---|
| `app.py` | Interfaz de la aplicación (Streamlit) |
| `inferencia.py` | Carga de la red bayesiana y cálculo del riesgo |
| `modelo/red_experta.json` | Red bayesiana entrenada: estructura, tablas de probabilidad y umbral |
| `.streamlit/config.toml` | Colores y tipografía de la aplicación |
| `requirements.txt` | Librerías necesarias |

## 1. Probar la aplicación en tu computadora (VS Code)

1. Abre la carpeta en VS Code (**Archivo > Abrir carpeta**).
2. Abre una terminal (**Terminal > Nueva terminal**) y crea un entorno virtual:
   ```
   python -m venv .venv
   ```
   Actívalo: en Windows, `.venv\Scripts\activate`; en macOS o Linux, `source .venv/bin/activate`.
3. Instala las librerías:
   ```
   pip install -r requirements.txt
   ```
4. Ejecuta la aplicación:
   ```
   streamlit run app.py
   ```
   Se abrirá en el navegador, en `http://localhost:8501`. Para detenerla, presiona `Ctrl + C`
   en la terminal.

Se requiere Python 3.11 o superior.

## 2. Subir el proyecto a GitHub (desde VS Code)

1. En la barra lateral, abre **Control de código fuente** (ícono de ramas) y pulsa
   **Inicializar repositorio**.
2. Escribe un mensaje (por ejemplo, "Primera versión de la aplicación") y pulsa **Confirmar**
   (*Commit*). Si VS Code pregunta si deseas preparar todos los cambios, acepta.
3. Pulsa **Publicar rama** (*Publish Branch*), inicia sesión con tu cuenta de GitHub si te lo
   pide y elige **repositorio público**.

## 3. Publicar en Streamlit Community Cloud

1. Entra a <https://share.streamlit.io> e inicia sesión con tu cuenta de GitHub.
2. Pulsa **Create app** y elige desplegar desde un repositorio de GitHub.
3. Selecciona el repositorio, la rama `main` y el archivo `app.py`.
4. En **Advanced settings**, elige Python 3.12.
5. Pulsa **Deploy**. En unos minutos tendrás un enlace público.

Cada vez que confirmes y sincronices cambios desde VS Code, la aplicación se actualizará sola.
Si nadie la visita durante 12 horas entra en reposo; al abrirla, basta con pulsar el botón para
reactivarla. Conviene abrirla unos minutos antes de una presentación.

## 4. Personalizar el diseño

- **Textos, preguntas y distribución:** en `app.py`.
- **Colores y fuente:** en `.streamlit/config.toml`; cada línea está comentada.
- **Nombres de las preguntas y opciones:** en el diccionario `FACTORES` de `inferencia.py`.
  No cambies las claves internas (por ejemplo, `"Q1 Más pobre"`), porque son los estados del modelo;
  solo cambia el texto que ve el usuario.

## Actualizar el modelo

El archivo `modelo/red_experta.json` se genera con el proyecto de análisis
(`python src/exportar_modelo.py <carpeta_de_la_app>`) después de entrenar la red. No contiene
microdatos de la ENDES, solo las tablas de probabilidad estimadas.
