"""Carga de la red bayesiana y cálculo del riesgo de anemia (sin interfaz)."""
import json
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
from pgmpy.factors.discrete import TabularCPD  # noqa: E402
from pgmpy.inference import VariableElimination  # noqa: E402
from pgmpy.models import DiscreteBayesianNetwork  # noqa: E402

RUTA_MODELO = Path(__file__).parent / "modelo" / "red_experta.json"

# Preguntas del formulario: nodo -> (pregunta, {estado del modelo: texto para el usuario})
FACTORES = {
    "edad": ("Edad del niño o niña", {"6-11": "6 a 11 meses", "12-23": "12 a 23 meses",
                                       "24-35": "24 a 35 meses"}),
    "sexo": ("Sexo", {"Hombre": "Masculino", "Mujer": "Femenino"}),
    "lactancia": ("¿Aún recibe lactancia materna?", {"Sí": "Sí", "No": "No"}),
    "diarrea": ("¿Tuvo diarrea en las últimas dos semanas?", {"Sí": "Sí", "No": "No"}),
    "desnutricion_cronica": ("¿Tiene talla baja para su edad (desnutrición crónica)?",
                             {"Sí": "Sí", "No": "No"}),
    "anemia_madre": ("¿La madre tiene anemia?", {"Sí": "Sí", "No": "No"}),
    "educacion_madre": ("Nivel educativo de la madre", {
        "Sin educación/Primaria": "Sin educación o primaria", "Secundaria": "Secundaria",
        "Superior": "Superior"}),
    "riqueza": ("Nivel socioeconómico del hogar (quintil de riqueza)", {
        "Q1 Más pobre": "Muy bajo (quintil 1)", "Q2 Pobre": "Bajo (quintil 2)",
        "Q3 Medio": "Medio (quintil 3)", "Q4 Rico": "Alto (quintil 4)",
        "Q5 Más rico": "Muy alto (quintil 5)"}),
    "region_natural": ("Región natural de residencia", {
        "Lima Metropolitana": "Lima Metropolitana", "Resto Costa": "Resto de la costa",
        "Sierra": "Sierra", "Selva": "Selva"}),
    "desague_red_publica": ("¿El hogar tiene desagüe conectado a la red pública?",
                            {"Sí": "Sí", "No": "No"}),
}

# Nombre breve de cada factor, para las explicaciones del resultado
NOMBRES = {"edad": "Edad", "sexo": "Sexo", "lactancia": "Lactancia materna",
           "diarrea": "Diarrea reciente", "desnutricion_cronica": "Desnutrición crónica",
           "anemia_madre": "Anemia de la madre", "educacion_madre": "Educación de la madre",
           "riqueza": "Nivel socioeconómico", "region_natural": "Región natural",
           "desague_red_publica": "Desagüe de red pública"}

GRUPOS = {
    "Datos del niño o niña": ["edad", "sexo", "lactancia", "diarrea", "desnutricion_cronica"],
    "Datos de la madre": ["anemia_madre", "educacion_madre"],
    "Datos del hogar": ["riqueza", "region_natural", "desague_red_publica"],
}


def cargar_modelo(ruta=RUTA_MODELO):
    datos = json.load(open(ruta, encoding="utf-8"))
    red = DiscreteBayesianNetwork([tuple(a) for a in datos["arcos"]])
    for c in datos["cpds"]:
        red.add_node(c["variable"])
        estados = {c["variable"]: c["estados"], **c["estados_padres"]}
        cpd = TabularCPD(c["variable"], len(c["estados"]), c["valores"],
                         evidence=c["padres"] or None,
                         evidence_card=[len(c["estados_padres"][p]) for p in c["padres"]] or None,
                         state_names=estados)
        red.add_cpds(cpd)
    assert red.check_model()
    return red, VariableElimination(red), datos


def probabilidad(inferencia, evidencia):
    """P(anemia = Sí | evidencia); la evidencia omite los factores desconocidos."""
    q = inferencia.query(["anemia"], evidence=evidencia or None, show_progress=False)
    return float(q.get_value(anemia="Sí"))


def aportes(inferencia, evidencia):
    """Cambio en la probabilidad atribuible a cada factor conocido: diferencia entre la
    probabilidad con toda la evidencia y la probabilidad si ese factor no se conociera."""
    p_total = probabilidad(inferencia, evidencia)
    resultado = []
    for factor in evidencia:
        sin_factor = {k: v for k, v in evidencia.items() if k != factor}
        resultado.append((factor, p_total - probabilidad(inferencia, sin_factor)))
    return sorted(resultado, key=lambda t: abs(t[1]), reverse=True)
