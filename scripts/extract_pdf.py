"""
Extracts content from Guía Atb.pdf and writes structured JSON files to data/.
Run once: python scripts/extract_pdf.py
"""

import json
import re
import sys
from pathlib import Path

try:
    from pdfminer.high_level import extract_text
except ImportError:
    print("Install pdfminer.six first: pip install pdfminer.six")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
PDF_PATH = ROOT / "input" / "Guía Atb.pdf"
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


def clean(t: str) -> str:
    t = re.sub(r"\s*pág\.\s*\d+\s*", "\n", t)
    t = re.sub(r"Abreviaturas\s*Volver al índice de contenido", "", t)
    t = re.sub(r"Para volver al punto previo pulsa[^\n]*\n", "", t)
    t = re.sub(r"Vuelve pulsando[^\n]*\n", "", t)
    t = re.sub(r"\n{4,}", "\n\n\n", t)
    t = re.sub(r" {3,}", "  ", t)
    return t.strip()


CHAPTERS = [
    {
        "id": "antimicrobianos-general",
        "number": 1,
        "title": "Antimicrobianos: aspectos generales",
        "system": "General",
        "keywords": ["dosificación", "ajuste renal", "ajuste hepático", "betalactámicos", "vancomicina", "insuficiencia renal", "terapia secuencial"],
        "search_anchor": "1.  Antimicrobianos: aspectos generales",
        "min_pos": 13000,
    },
    {
        "id": "artritis-infecciosa",
        "number": 2,
        "title": "Artritis infecciosa",
        "system": "Musculoesquelético",
        "keywords": ["artritis", "prótesis", "líquido sinovial", "artrocentesis", "gonorrea", "SARM", "Staphylococcus", "Streptococcus"],
        "search_anchor": "2.  Artritis infecciosa",
        "min_pos": 40000,
    },
    {
        "id": "endocarditis",
        "number": 3,
        "title": "Endocarditis infecciosa",
        "system": "Cardiovascular",
        "keywords": ["endocarditis", "válvula", "hemocultivos", "ETE", "ETT", "Staphylococcus aureus", "Streptococcus viridans", "enterococo"],
        "search_anchor": "3.  Endocarditis infecciosa",
        "min_pos": 40000,
    },
    {
        "id": "infecciones-abdominales",
        "number": 4,
        "title": "Infecciones abdominales (no biliares)",
        "system": "Abdominal",
        "keywords": ["peritonitis", "absceso", "apendicitis", "diverticulitis", "enterobacterias", "Bacteroides", "anaerobios"],
        "search_anchor": "Apendicitis Aguda  \n\nA. Etiología",
        "min_pos": 55000,
    },
    {
        "id": "peritonitis-bacteriana-espontanea",
        "number": 5,
        "title": "Peritonitis bacteriana espontánea",
        "system": "Abdominal",
        "keywords": ["PBE", "cirrosis", "líquido ascítico", "PMN", "polimorfonucleares", "cefotaxima", "norfloxacino"],
        "search_anchor": "5.  Peritonitis bacteriana espontánea",
        "min_pos": 40000,
    },
    {
        "id": "clostridioides-difficile",
        "number": 6,
        "title": "Infección por Clostridioides difficile",
        "system": "Abdominal",
        "keywords": ["C. difficile", "CD", "ICD", "diarrea", "colitis", "metronidazol", "vancomicina oral", "fidaxomicina", "ribotipo"],
        "search_anchor": "6. \n\nInfección por Clostridioides",
        "min_pos": 75000,
    },
    {
        "id": "via-biliar",
        "number": 7,
        "title": "Infecciones abdominales de vía biliar. Absceso hepático",
        "system": "Abdominal",
        "keywords": ["colecistitis", "colangitis", "absceso hepático", "biliar", "CPRE", "Klebsiella", "E. coli"],
        "search_anchor": "7. \n\nInfecciones abdominales de vía biliar",
        "min_pos": 80000,
    },
    {
        "id": "digestivas-altas",
        "number": 8,
        "title": "Infecciones digestivas altas",
        "system": "Abdominal",
        "keywords": ["H. pylori", "Helicobacter", "esofagitis", "gastroenteritis", "erradicación", "IBP"],
        "search_anchor": "8. \n\nInfecciones digestivas altas",
        "min_pos": 90000,
    },
    {
        "id": "cateter-venoso",
        "number": 9,
        "title": "Infecciones del catéter venoso",
        "system": "Dispositivos",
        "keywords": ["CVC", "CVP", "bacteriemia", "sellado", "catéter", "S. aureus", "coagulasa negativo", "candida"],
        "search_anchor": "9. \n\nInfecciones del catéter venoso",
        "min_pos": 98000,
    },
    {
        "id": "infecciones-orl",
        "number": 10,
        "title": "Infecciones ORL",
        "system": "ORL",
        "keywords": ["otitis", "sinusitis", "amigdalitis", "mastoiditis", "faringoamigdalitis", "S. pneumoniae", "H. influenzae"],
        "search_anchor": "10.  Infecciones ORL",
        "min_pos": 100000,
    },
    {
        "id": "piel-partes-blandas",
        "number": 11,
        "title": "Infecciones de piel y partes blandas",
        "system": "Piel",
        "keywords": ["celulitis", "erisipela", "fascitis necrotizante", "pie diabético", "absceso", "impétigo", "SARM", "Streptococcus pyogenes"],
        "search_anchor": "11.  Infecciones de piel y partes blandas",
        "min_pos": 110000,
    },
    {
        "id": "infecciones-respiratorias",
        "number": 12,
        "title": "Infecciones respiratorias y agudización EPOC",
        "system": "Respiratorio",
        "keywords": ["neumonía", "EPOC", "NAC", "gripe", "bronquitis", "S. pneumoniae", "atípicos", "CURB-65", "PORT"],
        "search_anchor": "12.  Infecciones respiratorias y agudización EPOC",
        "min_pos": 115000,
    },
    {
        "id": "nav",
        "number": 13,
        "title": "Neumonía asociada a ventilación mecánica",
        "system": "Respiratorio",
        "keywords": ["NAV", "UCI", "ventilación mecánica", "Pseudomonas", "SARM", "Acinetobacter", "broncoaspiración"],
        "search_anchor": "13.  Neumonía asociada a ventilación mecánica",
        "min_pos": 130000,
    },
    {
        "id": "snc",
        "number": 14,
        "title": "Infecciones del Sistema Nervioso Central",
        "system": "SNC",
        "keywords": ["meningitis", "encefalitis", "absceso cerebral", "punción lumbar", "LCR", "S. pneumoniae", "N. meningitidis", "Listeria", "herpes"],
        "search_anchor": "14.  Infecciones del Sistema Nervioso Central",
        "min_pos": 150000,
    },
    {
        "id": "its",
        "number": 15,
        "title": "Infecciones de transmisión sexual",
        "system": "ITS",
        "keywords": ["gonorrea", "sífilis", "clamidia", "VIH", "HSH", "ceftriaxona", "doxiciclina", "azitromicina", "ITS"],
        "search_anchor": "15.  Infecciones de transmisión sexual",
        "min_pos": 155000,
    },
    {
        "id": "infecciones-urinarias",
        "number": 16,
        "title": "Infecciones urinarias",
        "system": "Urinario",
        "keywords": ["cistitis", "pielonefritis", "prostatitis", "ITU", "urocultivo", "fosfomicina", "nitrofurantoína", "sonda vesical", "orquiepididimitis"],
        "search_anchor": "16.  Infecciones urinarias",
        "min_pos": 175000,
    },
    {
        "id": "neutropenia-febril",
        "number": 17,
        "title": "Neutropenia febril sin foco",
        "system": "General",
        "keywords": ["neutropenia", "fiebre", "quimioterapia", "MASCC", "piperacilina-tazobactam", "meropenem", "cefepima", "antifúngico"],
        "search_anchor": "17.  Neutropenia febril sin foco",
        "min_pos": 185000,
    },
    {
        "id": "osteomielitis",
        "number": 18,
        "title": "Osteomielitis",
        "system": "Musculoesquelético",
        "keywords": ["osteomielitis", "pie diabético", "infección ósea", "S. aureus", "rifampicina", "fluorquinolona", "crónica", "hematógena"],
        "search_anchor": "18.  Osteomielitis",
        "min_pos": 196000,
    },
    {
        "id": "sepsis",
        "number": 19,
        "title": "Sepsis",
        "system": "General",
        "keywords": ["sepsis", "shock séptico", "bacteriemia", "SARM", "foco desconocido", "empírico", "piperacilina-tazobactam", "meropenem"],
        "search_anchor": "19. Sepsis",
        "min_pos": 205000,
    },
    {
        "id": "fiebre-sin-foco",
        "number": 20,
        "title": "Síndrome febril sin focalidad",
        "system": "General",
        "keywords": ["FOD", "fiebre", "bacteriemia oculta", "fiebre importada", "paludismo", "viajero"],
        "search_anchor": "20. Síndrome febril sin focalidad",
        "min_pos": 213000,
    },
    {
        "id": "infecciones-oculares",
        "number": 21,
        "title": "Infecciones oculares",
        "system": "Ocular",
        "keywords": ["conjuntivitis", "queratitis", "endoftalmitis", "uveítis", "dacriocistitis", "colirio", "oftalmología"],
        "search_anchor": "21.  Infecciones oculares",
        "min_pos": 220000,
    },
    {
        "id": "candidiasis",
        "number": 22,
        "title": "Candidiasis invasiva",
        "system": "Fúngicas",
        "keywords": ["candida", "candidemia", "candidiasis", "equinocandina", "fluconazol", "anidulafungina", "caspofungina", "micafungina"],
        "search_anchor": "22. Candidiasis invasiva",
        "min_pos": 225000,
    },
    {
        "id": "covid19",
        "number": 23,
        "title": "Infección por SARS-CoV-2 (COVID-19)",
        "system": "Viral",
        "keywords": ["COVID", "SARS-CoV-2", "nirmatrelvir", "remdesivir", "dexametasona", "baricitinib", "tocilizumab"],
        "search_anchor": "23. Tratamiento Infección por SARS-CoV-2",
        "min_pos": 234000,
    },
]

ANNEXES = [
    {
        "id": "iras",
        "code": "A1",
        "title": "Criterios de Infección Relacionada con Asistencia Sanitaria",
        "search_anchor": "CRITERIOS DE INFECCIÓN RELACIONADA",
        "min_pos": 250000,
    },
    {
        "id": "resistencias",
        "code": "A2",
        "title": "Población en Riesgo de Infección por Bacterias Resistentes y Candida",
        "search_anchor": "POBLACIÓN EN RIESGO DE INFECCIÓN POR BACTERIAS",
        "min_pos": 250000,
    },
    {
        "id": "alergia-betalactamicos",
        "code": "A3",
        "title": "Evaluación Alergia a Betalactámicos",
        "search_anchor": "EVALUACIÓN ALERGIA A BETALACTÁMICOS",
        "min_pos": 255000,
    },
    {
        "id": "scores",
        "code": "A4",
        "title": "Índices y Scores de Riesgo",
        "search_anchor": "INDICES Y SCORES DE RIESGO",
        "min_pos": 262000,
    },
    {
        "id": "espectro-antibiotico",
        "code": "A5",
        "title": "Espectro Antibiótico",
        "search_anchor": "ESPECTRO ANTIBIÓTICO",
        "min_pos": 268000,
    },
    {
        "id": "nuevos-antibioticos",
        "code": "A6",
        "title": "Perfil Actividad de los Nuevos Antibióticos",
        "search_anchor": "PERFIL ACTIVIDAD DE LOS NUEVOS",
        "min_pos": 268000,
    },
    {
        "id": "muestras-microbiologia",
        "code": "A7",
        "title": "Contenedores Muestras Microbiología",
        "search_anchor": "CONTENEDORES MUESTRAS MICROBIOLOGIA",
        "min_pos": 269000,
    },
]


def extract_sections(text: str, items: list) -> list:
    """Find each item's text span using its search_anchor."""
    positions = []
    for item in items:
        anchor = item["search_anchor"]
        min_pos = item.get("min_pos", 15000)
        idx = text.find(anchor, min_pos)
        if idx >= 0:
            positions.append((idx, item))
        else:
            print(f"  WARNING: anchor not found for '{item['title']}' — '{anchor[:40]}'")
    positions.sort(key=lambda x: x[0])

    result = []
    for i, (start, item) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        chunk = clean(text[start:end])
        entry = dict(item)
        entry.pop("search_anchor", None)
        entry.pop("min_pos", None)
        entry["content"] = chunk
        result.append(entry)
    return result


def main():
    print(f"Extracting text from {PDF_PATH}...")
    text = extract_text(str(PDF_PATH))
    print(f"  Total characters: {len(text):,}")

    all_items = CHAPTERS + ANNEXES
    print("Locating all sections...")
    sections = extract_sections(text, all_items)
    print(f"  Found {len(sections)} sections")

    chapters_out = [s for s in sections if "number" in s]
    annexes_out = [s for s in sections if "code" in s]

    out = {"chapters": chapters_out, "annexes": annexes_out}
    out_path = DATA_DIR / "content.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  Saved → {out_path}")

    for ch in chapters_out:
        print(f"  Ch {ch.get('number', ch.get('code'))}: {len(ch['content']):,} chars — {ch['title']}")

    print("Done.")


if __name__ == "__main__":
    main()
