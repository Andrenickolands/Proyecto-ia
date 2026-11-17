"""Demo en Gradio: foto de un bache -> severidad, riesgo y reporte.
Uso (despues de correr el notebook, que guarda el modelo en resultados/):
    pip install gradio
    python app.py
"""
import json
import numpy as np
import gradio as gr
from tensorflow import keras

CFG = json.load(open("resultados/config.json"))
CLASES, IMG = CFG["clases"], CFG["img"]
modelo = keras.models.load_model("resultados/modelo_severidad.keras")

REGLA = {("baja", "borde"): "Baja", ("baja", "carril"): "Media", ("media", "borde"): "Media",
         ("media", "carril"): "Alta", ("alta", "borde"): "Alta", ("alta", "carril"): "Crítico"}


def analizar(foto, posicion):
    if foto is None:
        return {}, "", "Sube una foto."
    x = np.array(foto.convert("RGB").resize((IMG, IMG)), dtype="float32")[None]
    p = modelo.predict(x, verbose=0)[0]
    sev = CLASES[int(p.argmax())]
    pos = "carril" if posicion.startswith("Carril") else "borde"
    riesgo = REGLA[(sev, pos)]
    reporte = (f"Reporte de daño vial. Tipo de daño: bache. Severidad visual estimada por el modelo: {sev} "
               f"(confianza {p.max():.0%}). Posición marcada por el ciudadano: {posicion.lower()}. "
               f"Riesgo sugerido: {riesgo}. La prioridad es una sugerencia automática y debe ser validada por una persona.")
    return {c: float(v) for c, v in zip(CLASES, p)}, riesgo, reporte


demo = gr.Interface(
    fn=analizar,
    inputs=[gr.Image(type="pil", label="Foto del daño"),
            gr.Radio(["Carril de circulación", "Borde o berma"], value="Carril de circulación", label="Posición en la vía")],
    outputs=[gr.Label(label="Severidad visual"), gr.Textbox(label="Riesgo sugerido"), gr.Textbox(label="Reporte", lines=4)],
    title="Priorización de baches · Arreglen las Calles",
    description="El modelo estima la severidad a partir de la foto. El riesgo combina esa severidad con la posición marcada.",
    allow_flagging="never",
)

if __name__ == "__main__":
    demo.launch(share=True)
