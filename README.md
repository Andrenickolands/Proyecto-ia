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
  

## Prueba de campo con fotos de Bogotá

RDD2022 no tiene fotos de Colombia, así que la sección 11 del notebook evalúa el modelo con fotos propias.

1. Generar las fotos: con `herramientas/descargar_huecos.py` y `herramientas/Inventario_Huecos_Bogota.xlsx` en la misma carpeta, ejecutar `pip install requests openpyxl pillow` y `python descargar_huecos.py`. Sale `100_Huecos_Bogota.zip`. También sirven fotos tomadas con el celular (JPG, PNG, WEBP o BMP).
2. En Colab, ejecutar la sección 11 y subir el ZIP o las fotos. La primera vez crea `etiquetas_bogota.csv` y una hoja con las fotos numeradas, sin mostrar predicciones.
3. Llenar `severidad` (baja, media o alta) y, si se sabe, `posicion` (carril o borde). Volver a ejecutar la celda.
4. Sale `resultados/predicciones_bogota.csv`, la matriz de confusión, Grad-CAM sobre las fotos y las métricas en `resultados.json`.

Las fotos de prensa tienen derechos de autor: se usan solo para evaluar y no se suben a este repositorio (están en `.gitignore`).
