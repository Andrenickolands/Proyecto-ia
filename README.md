# Priorización automática de baches a partir de fotos ciudadanas

Proyecto integrador de **Inteligencia Artificial Avanzada** (Momento 3, Ruta A, tema libre).
Andrés Nicolás Sepúlveda Amaya · Ingeniería de Software · Fundación Universitaria Compensar.

## El problema

La Unidad de Mantenimiento Vial de Bogotá recibió cerca de 13.000 peticiones ciudadanas sobre la malla vial entre 2025 y 2026. Cada reporte lo revisa una persona para decidir qué se atiende primero. En [Arreglen las Calles](https://arreglenlascalles.com) pasa lo mismo en pequeño: el riesgo lo escoge el ciudadano a ojo y con eso no se puede ordenar la lista.

Este proyecto entrena un modelo que mira la foto del daño y estima su severidad. Esa severidad se combina con la posición que el ciudadano marca en la vía para sugerir el riesgo (Baja, Media, Alta, Crítico), y un modelo de lenguaje redacta el reporte para la entidad.

## Qué hay en el repositorio

| Archivo | Para qué sirve |
| --- | --- |
| `notebooks/priorizacion_baches.ipynb` | Todo el proyecto: datos, EDA, división, línea base, redes profundas, evaluación, Grad-CAM, errores y reportes |
| `app.py` | Demo en Gradio |
| `requirements.txt` | Librerías |

## Cómo reproducirlo

1. Abrir el notebook en Google Colab.
2. Entorno de ejecución → Cambiar tipo de entorno de ejecución → GPU T4.
3. Entorno de ejecución → Ejecutar todo. Tarda entre 15 y 20 minutos.
4. Al final quedan en `resultados/` las figuras, el modelo y `resultados.json` con todas las métricas.
5. Para la demo: `pip install gradio` y `python app.py`.

Las semillas están fijas (42) y la división train/val/test se hace antes de cualquier transformación.

## Datos

- **RDD2022** (Arya et al.), subconjunto de India, descargado del enlace oficial del repositorio [sekilab/RoadDamageDetector](https://github.com/sekilab/RoadDamageDetector). También está en [figshare](https://figshare.com/articles/dataset/RDD2022_-_The_multi-national_Road_Damage_Dataset_released_through_CRDDC_2022/21431547).
- La fecha de descarga queda registrada en `resultados/resultados.json`.
- Se usan solo las imágenes con al menos un bache (clase D40).

## Método

| Paso | Qué se hace |
| --- | --- |
| Etiqueta de severidad | Regla sobre el área del bache más grande y la cantidad de baches; los cortes son terciles calculados solo con train |
| Línea base | HOG + histograma de color + regresión logística |
| Red profunda 1 | CNN propia entrenada desde cero |
| Red profunda 2 | MobileNetV2 con transfer learning y ajuste fino |
| Métrica | Recall de la clase alta y F1-macro en test |
| Explicabilidad | Grad-CAM |
| NLP | Reporte en lenguaje natural con plantilla + modelo de lenguaje, evaluado con lista de chequeo |

## Límites

- La severidad es una etiqueta débil: depende de qué tan cerca se tomó la foto.
- La prioridad es una sugerencia.
  
