# Política Antimicrobiana — Hospital Universitario de Valme

Aplicación web interactiva para consulta de la **Guía de Tratamiento Antimicrobiano en Adultos (v1.1, 2023)** del Grupo PROA del Hospital Universitario de Valme (Sevilla).

## Funcionalidades

- **Explorador de síndromes**: Navegación por 23 síndromes infecciosos organizados por sistema orgánico
- **Búsqueda**: Búsqueda libre por síndrome, patógeno o fármaco
- **Calculadora de ajuste renal**: Dosis recomendada según filtrado glomerular estimado para >30 antibióticos
- **Nomograma de vancomicina**: Cálculo de dosis de carga y mantenimiento por peso y FGe
- **Terapia secuencial IV→VO**: Guía de conversión a vía oral
- **Referencia de fármacos**: Dosis estándar e incrementadas por clase antimicrobiana
- **Anexos clínicos**: Criterios IRAS, resistencias, alergia betalactámicos, scores de riesgo

## Estructura del proyecto

```
politica_antimicrobiana/
├── app.py                    # Aplicación Streamlit principal
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml           # Tema y configuración
├── data/
│   ├── content.json          # Contenido de 23 capítulos + anexos (generado del PDF)
│   ├── dosing.json           # Dosis estándar/incrementadas por clase
│   ├── renal_dosing.json     # Ajuste de dosis en insuficiencia renal
│   └── vancomycin_nomogram.json  # Nomograma de vancomicina
├── scripts/
│   └── extract_pdf.py        # Script de extracción del PDF (ejecutar una vez)
└── input/
    └── Guía Atb.pdf          # PDF fuente (no incluido en el repositorio público)
```

## Instalación local

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd politica_antimicrobiana
```

### 2. Crear entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Regenerar datos desde el PDF (opcional)

> Solo necesario si actualizas el PDF fuente.

Coloca el PDF en `input/Guía Atb.pdf` y ejecuta:

```bash
python scripts/extract_pdf.py
```

Esto regenera los archivos en `data/`.

### 5. Ejecutar la app

```bash
streamlit run app.py
```

La app se abre en `http://localhost:8501`.

## Publicar en Streamlit Community Cloud

1. Sube el repositorio a GitHub (asegúrate de incluir la carpeta `data/` con los JSON pero **NO** el PDF si tiene derechos de copia)
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta con tu cuenta GitHub
4. Selecciona el repositorio y `app.py` como punto de entrada
5. Despliega

> El PDF fuente (`input/Guía Atb.pdf`) contiene derechos de copia del Grupo PROA del Hospital Universitario de Valme. Solicita autorización antes de incluirlo en un repositorio público.

## Actualizar el contenido

Cuando se publique una nueva versión de la guía:

1. Reemplaza `input/Guía Atb.pdf` con el nuevo PDF
2. Ejecuta `python scripts/extract_pdf.py`
3. Revisa los archivos generados en `data/`
4. Actualiza manualmente `data/dosing.json`, `data/renal_dosing.json` y `data/vancomycin_nomogram.json` si cambian las tablas de dosificación
5. Commit y push

## Fuente

> Guía de Tratamiento Antimicrobiano en Adultos, v1.1 (marzo 2023).  
> © Grupo PROA, Hospital Universitario de Valme, Sevilla.  
> Editores: Marta Trigo Rodríguez, Juan E. Corzo Delgado, Nicolás Merchante Gutiérrez.

---

⚠️ **Aviso**: Esta aplicación es una herramienta de apoyo a la toma de decisiones. Las recomendaciones son orientativas y deben adaptarse a cada situación clínica individual. Consulte con la Unidad de Enfermedades Infecciosas ante casos complejos o dudas terapéuticas.
