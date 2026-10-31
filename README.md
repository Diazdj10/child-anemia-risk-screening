# Tamizaje de riesgo de anemia infantil

Aplicación web que estima el riesgo de anemia en niños y niñas de 6 a 35 meses en el Perú
mediante una **red bayesiana** construida con datos de la Encuesta Demográfica y de Salud
Familiar (ENDES) 2024 y 2025 del INEI (entrenamiento con 2024 y validación con 2025), según el
criterio de anemia de la OMS 2024.

> La herramienta **no diagnostica** la anemia ni reemplaza la medición de hemoglobina. Su
> propósito es ayudar a priorizar a los niños que requieren con mayor urgencia la prueba de
> hemoglobina y la atención.

Proyecto del curso **Sistemas Basados en el Conocimiento**, Escuela de Informática,
Universidad Nacional de Trujillo, 2026.

**Autores:** Charcape Rodríguez Joaquín, Díaz Zegarra Diego Jhonatan y Jara Solorzano Dylan Nikolas.

## Problema

La anemia infantil es un problema de salud pública en el Perú. Detectarla exige medir la
hemoglobina, y no siempre es posible hacerlo a todos los niños con la misma urgencia. Este
proyecto propone un sistema de tamizaje que, con datos sencillos de preguntar, estima la
probabilidad de anemia y señala a quiénes conviene priorizar.

## Cómo funciona

1. La persona usuaria responde hasta 10 preguntas sobre el niño, la madre y el hogar. Cualquier
   dato puede quedar como *No se conoce*: la red estima el riesgo con la información disponible.
2. La red bayesiana calcula la probabilidad de anemia mediante inferencia exacta
   (eliminación de variables).
3. La aplicación compara esa probabilidad con un umbral y clasifica el caso como **riesgo
   elevado** o **riesgo menor**.
4. Se muestra qué datos elevan o reducen el riesgo, para que el resultado sea explicable.

### Factores considerados

| Grupo | Variables |
|---|---|
| Niño o niña | edad, sexo, lactancia materna, diarrea reciente, desnutrición crónica |
| Madre | anemia de la madre, nivel educativo |
| Hogar | nivel socioeconómico (quintil de riqueza), región natural, desagüe de red pública |

## Modelo y resultados

- **Datos de entrenamiento:** 9 706 niños de la ENDES 2024.
- **Datos de prueba:** 9 061 niños de la ENDES 2025, no usados en el entrenamiento.
- **Umbral de decisión:** 33,2 %, fijado para detectar al menos al 70 % de los niños con anemia,
  porque en un tamizaje es preferible una falsa alarma a dejar sin atención a un niño en riesgo.

| Métrica | Valor |
|---|---|
| Sensibilidad | 70,1 % |
| Especificidad | 51,1 % |
| Valor predictivo negativo | 75,1 % |
| Área bajo la curva ROC | 0,653 |

### Limitaciones

- La red muestra asociaciones probabilísticas, no relaciones causales demostradas.
- Su capacidad de clasificación es moderada, por lo que no sustituye la medición de hemoglobina.
- Parte de los niños clasificados en riesgo elevado no tendrá anemia (consecuencia del umbral
  elegido).
- Se entrenó con una encuesta nacional; su desempeño puede variar en poblaciones específicas.

## Estructura del proyecto

| Archivo | Descripción |
|---|---|
| `app.py` | Interfaz de la aplicación (Streamlit) |
| `inferencia.py` | Carga de la red bayesiana y cálculo del riesgo |
| `modelo/red_experta.json` | Red bayesiana entrenada: estructura, tablas de probabilidad y umbral |
| `.streamlit/config.toml` | Colores y tipografía |
| `requirements.txt` | Librerías necesarias |

El modelo no contiene microdatos de la ENDES, solo las tablas de probabilidad estimadas.

## Ejecución local

Requiere Python 3.11 o superior.

```
python -m venv .venv
.venv\Scripts\activate        # macOS o Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

La aplicación se abre en `http://localhost:8501`.

## Tecnologías

Python, [pgmpy](https://pgmpy.org/) (redes bayesianas) y [Streamlit](https://streamlit.io/)
(interfaz web).

## Fuente de datos

Instituto Nacional de Estadística e Informática (INEI), Encuesta Demográfica y de Salud
Familiar (ENDES) 2024 y 2025.
