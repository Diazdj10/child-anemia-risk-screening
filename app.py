"""Aplicación web de tamizaje de riesgo de anemia infantil con una red bayesiana.

Proyecto del curso Sistemas Basados en el Conocimiento, Universidad Nacional de Trujillo.
Ejecutar localmente:  streamlit run app.py
"""
import streamlit as st

from inferencia import FACTORES, GRUPOS, NOMBRES, aportes, cargar_modelo, probabilidad

DESCONOCIDO = "No se conoce"
UMBRAL_APORTE = 0.015  # cambios menores a 1,5 puntos porcentuales se consideran mínimos
# Nivel alto: probabilidad desde la cual más de la mitad de los niños tenía anemia en la
# validación cruzada de 2024 (55,3 %). El umbral de tamizaje (moderado) viene del modelo.
UMBRAL_ALTO = 0.45
# Niños con anemia por cada 100 en cada nivel, en los datos de prueba (ENDES 2025)
ANEMIA_POR_NIVEL = {"Bajo": 25, "Moderado": 38, "Alto": 54}

st.set_page_config(page_title="Tamizaje de riesgo de anemia infantil", page_icon="🩺",
                   layout="wide")


@st.cache_resource
def modelo():
    return cargar_modelo()


red, inferencia, datos = modelo()
UMBRAL = datos["umbral"]
PREVALENCIA = probabilidad(inferencia, {})
metricas = datos["metricas_prueba_2025"]


def pct(x):
    return f"{100 * x:.1f} %".replace(".", ",")


# ----------------------------------------------------------------------------- encabezado
st.title("Tamizaje de riesgo de anemia infantil")
st.markdown("Estimación del riesgo de anemia en niños y niñas de **6 a 35 meses** en el Perú "
            "mediante una **red bayesiana** entrenada con la Encuesta Demográfica y de Salud "
            "Familiar (ENDES) 2024 del INEI, según el criterio de anemia de la OMS 2024.")
st.info("Esta herramienta **no diagnostica** la anemia ni reemplaza la medición de hemoglobina. "
        "Su propósito es ayudar a priorizar a los niños que requieren con mayor urgencia la "
        "prueba de hemoglobina y la atención.", icon="ℹ️")

pestana_eval, pestana_modelo = st.tabs(["Evaluar riesgo", "Acerca del modelo"])

# ----------------------------------------------------------------------------- evaluación
with pestana_eval:
    st.markdown("Complete los datos disponibles. Si no conoce alguno, deje la opción "
                f"**{DESCONOCIDO}**: la red estima el riesgo con la información que se tenga.")
    with st.form("formulario"):
        respuestas = {}
        columnas = st.columns(3, gap="large")
        for columna, (grupo, factores) in zip(columnas, GRUPOS.items()):
            with columna:
                st.subheader(grupo)
                for f in factores:
                    pregunta, opciones = FACTORES[f]
                    etiquetas = [DESCONOCIDO] + list(opciones.values())
                    elegido = st.selectbox(pregunta, etiquetas, key=f)
                    if elegido != DESCONOCIDO:
                        respuestas[f] = next(k for k, v in opciones.items() if v == elegido)
        enviado = st.form_submit_button("Calcular riesgo", type="primary",
                                        use_container_width=True)

    if enviado:
        p = probabilidad(inferencia, respuestas)
        nivel = "Alto" if p >= UMBRAL_ALTO else ("Moderado" if p >= UMBRAL else "Bajo")
        st.divider()
        st.subheader("Resultado")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Nivel de riesgo", nivel)
        c2.metric("Probabilidad estimada de anemia", pct(p),
                  delta=f"{100 * (p - PREVALENCIA):+.1f} pp frente al promedio".replace(".", ","),
                  delta_color="inverse")
        c3.metric("Promedio en niños de 6 a 35 meses", pct(PREVALENCIA))
        c4.metric("Datos ingresados", f"{len(respuestas)} de {len(FACTORES)}")

        referencia = (f"De cada 100 niños con un resultado similar en los datos de prueba, "
                      f"{ANEMIA_POR_NIVEL[nivel]} tenían anemia.")
        if nivel == "Alto":
            st.error(f"**Riesgo alto** (probabilidad de {pct(UMBRAL_ALTO)} o más). {referencia} "
                     "Se recomienda realizar la medición de hemoglobina con prioridad y asegurar "
                     "el seguimiento del niño o niña en su establecimiento de salud.", icon="🔴")
        elif nivel == "Moderado":
            st.warning(f"**Riesgo moderado** (probabilidad entre {pct(UMBRAL)} y "
                       f"{pct(UMBRAL_ALTO)}). {referencia} Se recomienda priorizar la medición "
                       "de hemoglobina en su próximo control.", icon="🟠")
        else:
            st.success(f"**Riesgo bajo** (probabilidad inferior a {pct(UMBRAL)}). {referencia} "
                       "Debe mantenerse el control de crecimiento y desarrollo y la medición de "
                       "hemoglobina según la norma técnica vigente.", icon="🟢")

        if respuestas:
            st.markdown("#### ¿Qué datos influyen en este resultado?")
            st.caption("Aporte adicional de cada dato una vez considerados los demás: cambio en la "
                       "probabilidad si ese dato no se conociera (en puntos porcentuales).")
            lista = aportes(inferencia, respuestas)
            suben = [(f, a) for f, a in lista if a >= UMBRAL_APORTE]
            bajan = [(f, a) for f, a in lista if a <= -UMBRAL_APORTE]
            minimos = [f for f, a in lista if abs(a) < UMBRAL_APORTE]
            i1, i2 = st.columns(2)
            with i1:
                st.markdown("**Elevan el riesgo**")
                if not suben:
                    st.markdown("Ninguno de los datos ingresados.")
                for f, a in suben:
                    st.markdown(f"▲ {NOMBRES[f]}: *{FACTORES[f][1][respuestas[f]].lower()}* "
                                f"(+{100 * a:.1f} pp)".replace(".", ","))
            with i2:
                st.markdown("**Reducen el riesgo**")
                if not bajan:
                    st.markdown("Ninguno de los datos ingresados.")
                for f, a in bajan:
                    st.markdown(f"▼ {NOMBRES[f]}: *{FACTORES[f][1][respuestas[f]].lower()}* "
                                f"({100 * a:.1f} pp)".replace(".", ","))
            if minimos:
                st.caption("Sin aporte adicional apreciable (su información ya está reflejada en "
                           "otros datos o su efecto es pequeño en este caso): "
                           + ", ".join(NOMBRES[f].lower() for f in minimos) + ".")
        else:
            st.caption("No se ingresó ningún dato: la probabilidad corresponde al promedio de "
                       "los niños de 6 a 35 meses.")

# ----------------------------------------------------------------------------- acerca de
with pestana_modelo:
    st.subheader("Cómo funciona")
    n_entrenamiento = f"{datos['n_entrenamiento']:,}".replace(",", " ")
    st.markdown(
        "La red bayesiana representa las relaciones entre la anemia y diez factores del niño, "
        "la madre y el hogar. Cada flecha indica una dependencia probabilística, y cada nodo "
        "tiene una tabla de probabilidad condicional estimada con los datos de "
        f"{n_entrenamiento} niños de la ENDES 2024. "
        "Con los datos ingresados, la red calcula la probabilidad de anemia mediante "
        "inferencia exacta (eliminación de variables).")

    etiquetas = {"anemia": "Anemia", "edad": "Edad", "sexo": "Sexo", "lactancia": "Lactancia",
                 "diarrea": "Diarrea", "desnutricion_cronica": "Desnutrición\\ncrónica",
                 "anemia_madre": "Anemia de\\nla madre", "educacion_madre": "Educación\\nde la madre",
                 "riqueza": "Nivel\\nsocioeconómico", "region_natural": "Región\\nnatural",
                 "desague_red_publica": "Desagüe de\\nred pública"}
    dot = ['digraph { rankdir=TB; bgcolor=transparent; nodesep=0.3; ranksep=0.35; size="7,5.5";',
           'node [shape=box, style="rounded", fontname="Helvetica", fontsize=11];',
           'anemia [label="Anemia", style="rounded,bold", penwidth=2];']
    dot += [f'{n} [label="{t}"];' for n, t in etiquetas.items() if n != "anemia"]
    dot += [f"{a} -> {b};" for a, b in datos["arcos"]]
    dot.append("}")
    _, centro, _ = st.columns([1, 3, 1])
    with centro:
        st.graphviz_chart("\n".join(dot))

    st.subheader("Desempeño en datos de prueba (ENDES 2025)")
    n_prueba = f"{datos['n_prueba']:,}".replace(",", " ")
    st.markdown(f"Evaluado con {n_prueba} niños de 2025, que no se usaron en el entrenamiento.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sensibilidad", pct(metricas["sensibilidad"]),
              help="Proporción de niños con anemia que la red clasifica en riesgo moderado o alto.")
    m2.metric("Especificidad", pct(metricas["especificidad"]),
              help="Proporción de niños sin anemia que la red clasifica en riesgo bajo.")
    m3.metric("Valor predictivo negativo", pct(metricas["VPN"]),
              help="Proporción de niños clasificados en riesgo bajo que no tenían anemia.")
    m4.metric("Área bajo la curva ROC", f"{metricas['AUC']:.3f}".replace(".", ","),
              help="Capacidad de distinguir entre niños con y sin anemia (0,5 = azar; 1 = perfecta).")
    st.markdown(
        f"El umbral de tamizaje ({pct(UMBRAL)}) se fijó para detectar al menos al 70 % de los "
        "niños con anemia, porque en el tamizaje es preferible una falsa alarma a dejar sin "
        "atención a un niño en riesgo. A partir de él se recomienda priorizar la prueba de "
        "hemoglobina. Los resultados se presentan en tres niveles:")
    st.table({
        "Nivel": ["Bajo", "Moderado", "Alto"],
        "Probabilidad estimada": [f"Menor a {pct(UMBRAL)}", f"{pct(UMBRAL)} a {pct(UMBRAL_ALTO)}",
                                  f"{pct(UMBRAL_ALTO)} o más"],
        "Niños con anemia por cada 100 (ENDES 2025)": [ANEMIA_POR_NIVEL[n] for n in
                                                      ("Bajo", "Moderado", "Alto")],
    })
    st.caption("El límite del nivel alto (45 %) se fijó con los datos de entrenamiento: por encima "
               "de él, más de la mitad de los niños tenía anemia en la validación cruzada de 2024.")

    st.subheader("Limitaciones")
    st.markdown(
        "- La red muestra asociaciones probabilísticas, no relaciones causales demostradas.\n"
        "- Su capacidad de clasificación es moderada, por lo que no sustituye la medición de "
        "hemoglobina.\n"
        "- Se entrenó con datos de una encuesta nacional; su desempeño puede variar en "
        "poblaciones específicas.")

    st.subheader("Créditos")
    st.markdown(
        "Charcape Rodríguez Joaquín, Díaz Zegarra Diego Jhonatan y Jara Solorzano Dylan Nikolas. "
        "Escuela de Informática, Universidad Nacional de Trujillo, 2026.  \n"
        "Datos: Instituto Nacional de Estadística e Informática (INEI), ENDES 2024 y 2025.")
