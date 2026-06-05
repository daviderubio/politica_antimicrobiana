"""
Política Antimicrobiana — Hospital Universitario de Valme
Guía de Tratamiento Antimicrobiano en Adultos (v1.1 - marzo 2023)
"""

import json
import re
from pathlib import Path

import streamlit as st

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Política Antimicrobiana · Valme",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"

# ── Data loading (cached) ────────────────────────────────────────────────────
@st.cache_data
def load_content():
    with open(DATA_DIR / "content.json", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_dosing():
    with open(DATA_DIR / "dosing.json", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_renal():
    with open(DATA_DIR / "renal_dosing.json", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_vancomycin():
    with open(DATA_DIR / "vancomycin_nomogram.json", encoding="utf-8") as f:
        return json.load(f)

# ── Session state ────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_chapter" not in st.session_state:
    st.session_state.selected_chapter = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# ── Helpers ──────────────────────────────────────────────────────────────────
SYSTEM_ICONS = {
    "General": "🏥",
    "Musculoesquelético": "🦴",
    "Cardiovascular": "❤️",
    "Abdominal": "🫁",
    "Respiratorio": "🌬️",
    "SNC": "🧠",
    "ITS": "🔬",
    "Urinario": "💧",
    "ORL": "👂",
    "Piel": "🩹",
    "Dispositivos": "🔗",
    "Ocular": "👁️",
    "Fúngicas": "🍄",
    "Viral": "🦠",
}


def highlight_text(text: str, query: str) -> str:
    """Wrap query matches in markdown bold."""
    if not query or len(query) < 2:
        return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group()}**", text)


def search_chapters(chapters: list, query: str) -> list:
    """Return chapters that match query in title, keywords, or content."""
    q = query.lower().strip()
    if not q:
        return []
    results = []
    for ch in chapters:
        score = 0
        if q in ch["title"].lower():
            score += 10
        for kw in ch.get("keywords", []):
            if q in kw.lower():
                score += 5
        if q in ch.get("content", "").lower():
            score += 1
        if score > 0:
            results.append((score, ch))
    results.sort(key=lambda x: x[0], reverse=True)
    return [ch for _, ch in results]


def format_content(text: str) -> str:
    """Basic cleanup of PDF-extracted text for display."""
    lines = text.split("\n")
    out = []
    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            out.append("")
            continue
        # Detect section headers (short, all-caps or ends with colon)
        if len(stripped) < 80 and stripped.isupper() and len(stripped) > 3:
            out.append(f"\n### {stripped.title()}")
        elif re.match(r"^\d+\.\d+", stripped):
            out.append(f"\n#### {stripped}")
        elif re.match(r"^[A-Z]\.", stripped) and len(stripped) < 60:
            out.append(f"\n**{stripped}**")
        else:
            out.append(stripped)
    return "\n".join(out)


# ── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🧬 Política Antimicrobiana")
        st.caption("Hospital Universitario de Valme · v1.1 (2023)")
        st.divider()

        # Search
        query = st.text_input(
            "🔍 Buscar síndrome, patógeno o fármaco",
            value=st.session_state.search_query,
            placeholder="ej. cistitis, SARM, meropenem…",
            key="search_input",
        )
        if query != st.session_state.search_query:
            st.session_state.search_query = query
            st.session_state.page = "search"
            st.rerun()

        st.divider()

        # Navigation
        nav_items = [
            ("🏠 Inicio", "home"),
            ("💊 Calculadoras", "calculadoras"),
            ("📋 Referencia de Fármacos", "farmacos"),
            ("📎 Anexos", "anexos"),
        ]
        for label, page_id in nav_items:
            if st.button(label, use_container_width=True, key=f"nav_{page_id}"):
                st.session_state.page = page_id
                st.session_state.selected_chapter = None
                st.session_state.search_query = ""
                st.rerun()

        st.divider()
        st.markdown("**📚 Guía por Síndrome**")

        content = load_content()
        chapters = sorted(content["chapters"], key=lambda c: c["number"])

        # Group by system
        systems: dict[str, list] = {}
        for ch in chapters:
            sys_name = ch.get("system", "General")
            systems.setdefault(sys_name, []).append(ch)

        system_order = [
            "General", "Respiratorio", "Abdominal", "Urinario",
            "Cardiovascular", "SNC", "Musculoesquelético", "Piel",
            "ORL", "Ocular", "ITS", "Dispositivos", "Fúngicas", "Viral",
        ]
        for sys_name in system_order:
            if sys_name not in systems:
                continue
            icon = SYSTEM_ICONS.get(sys_name, "📌")
            with st.expander(f"{icon} {sys_name}", expanded=False):
                for ch in systems[sys_name]:
                    label = f"{ch['number']}. {ch['title']}"
                    if st.button(label, key=f"ch_{ch['id']}", use_container_width=True):
                        st.session_state.page = "chapter"
                        st.session_state.selected_chapter = ch["id"]
                        st.session_state.search_query = ""
                        st.rerun()

        st.divider()
        st.caption("Grupo PROA · Hospital Valme")
        st.caption("Para consultas: proa.valme@gmail.com")


# ── Pages ────────────────────────────────────────────────────────────────────
def page_home():
    st.title("Guía de Tratamiento Antimicrobiano en Adultos")
    st.markdown(
        """
        **Hospital Universitario de Valme · Grupo PROA · v1.1 (2023)**

        Guía de referencia rápida para la toma de decisiones sobre antibioterapia en distintos escenarios clínicos,
        adaptada a la ecología local y al mapa de resistencias del área sanitaria de Valme.
        """
    )

    content = load_content()
    chapters = sorted(content["chapters"], key=lambda c: c["number"])

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Síndromes infecciosos", len(chapters))
    with col2:
        st.metric("Anexos clínicos", len(content["annexes"]))

    st.divider()

    # Quick access grid
    st.subheader("Acceso rápido por sistema")

    systems: dict[str, list] = {}
    for ch in chapters:
        sys_name = ch.get("system", "General")
        systems.setdefault(sys_name, []).append(ch)

    system_order = [
        "General", "Respiratorio", "Abdominal", "Urinario",
        "Cardiovascular", "SNC", "Musculoesquelético", "Piel",
        "ORL", "Ocular", "ITS", "Dispositivos", "Fúngicas", "Viral",
    ]

    cols = st.columns(3)
    col_idx = 0
    for sys_name in system_order:
        if sys_name not in systems:
            continue
        icon = SYSTEM_ICONS.get(sys_name, "📌")
        with cols[col_idx % 3]:
            st.markdown(f"**{icon} {sys_name}**")
            for ch in systems[sys_name]:
                if st.button(
                    f"{ch['number']}. {ch['title']}",
                    key=f"home_ch_{ch['id']}",
                    use_container_width=True,
                ):
                    st.session_state.page = "chapter"
                    st.session_state.selected_chapter = ch["id"]
                    st.rerun()
            st.markdown("")
        col_idx += 1

    st.divider()
    st.info(
        "⚠️ Las pautas indicadas son recomendaciones generales. Cada escenario clínico es único "
        "y debe individualizarse siempre que proceda. Consulte con la Unidad de Enfermedades "
        "Infecciosas si lo necesita."
    )


def page_chapter():
    content = load_content()
    chapters = {ch["id"]: ch for ch in content["chapters"]}
    ch_id = st.session_state.selected_chapter

    if ch_id not in chapters:
        st.error("Capítulo no encontrado.")
        return

    ch = chapters[ch_id]
    icon = SYSTEM_ICONS.get(ch.get("system", ""), "📌")

    st.markdown(f"### {icon} {ch['number']}. {ch['title']}")
    sys_name = ch.get("system", "")
    if sys_name:
        st.caption(f"Sistema: {sys_name}")

    # Keywords as tags
    if ch.get("keywords"):
        tags = " · ".join(f"`{kw}`" for kw in ch["keywords"])
        st.markdown(tags)

    st.divider()

    # Chapter navigation (prev / next)
    all_chapters = sorted(content["chapters"], key=lambda c: c["number"])
    ids = [c["id"] for c in all_chapters]
    idx = ids.index(ch_id) if ch_id in ids else -1

    nav_col1, nav_col2, nav_col3 = st.columns([1, 8, 1])
    with nav_col1:
        if idx > 0:
            prev_ch = all_chapters[idx - 1]
            if st.button("← Anterior", use_container_width=True):
                st.session_state.selected_chapter = prev_ch["id"]
                st.rerun()
    with nav_col3:
        if idx < len(all_chapters) - 1:
            next_ch = all_chapters[idx + 1]
            if st.button("Siguiente →", use_container_width=True):
                st.session_state.selected_chapter = next_ch["id"]
                st.rerun()

    st.divider()

    # Content display
    content_text = ch.get("content", "")
    if st.session_state.search_query:
        content_text = highlight_text(content_text, st.session_state.search_query)

    st.markdown(content_text, unsafe_allow_html=False)

    st.divider()
    st.caption(
        "Contenido extraído de: Guía de Tratamiento Antimicrobiano en Adultos, "
        "Hospital Universitario de Valme (2023). Grupo PROA."
    )


def page_search():
    query = st.session_state.search_query
    st.title(f"🔍 Resultados para: \"{query}\"")

    content = load_content()
    all_items = content["chapters"] + content["annexes"]
    results = search_chapters(all_items, query)

    if not results:
        st.warning("No se encontraron resultados. Intenta con otra búsqueda.")
        return

    st.success(f"{len(results)} resultado(s) encontrado(s)")

    for item in results:
        icon = SYSTEM_ICONS.get(item.get("system", ""), "📌")
        is_annex = "code" in item
        prefix = item.get("code", str(item.get("number", "")))
        label = f"{icon} {prefix}. {item['title']}" if not is_annex else f"📎 {prefix}. {item['title']}"

        with st.expander(label):
            # Show snippet with match
            text = item.get("content", "")
            q_lower = query.lower()
            idx = text.lower().find(q_lower)
            if idx >= 0:
                start = max(0, idx - 200)
                end = min(len(text), idx + 500)
                snippet = "…" + text[start:end] + "…"
                snippet = highlight_text(snippet, query)
                st.markdown(snippet)

            if not is_annex:
                if st.button(f"Ver capítulo completo →", key=f"result_{item['id']}"):
                    st.session_state.page = "chapter"
                    st.session_state.selected_chapter = item["id"]
                    st.rerun()
            else:
                if st.button(f"Ver anexo completo →", key=f"result_{item['id']}"):
                    st.session_state.page = "anexo_detail"
                    st.session_state.selected_chapter = item["id"]
                    st.rerun()


def page_calculadoras():
    st.title("💊 Calculadoras Clínicas")

    renal_data = load_renal()
    vanco_data = load_vancomycin()
    dosing_data = load_dosing()

    tab1, tab2, tab3 = st.tabs([
        "🧮 Ajuste Dosis Renal",
        "📊 Vancomicina (Nomograma)",
        "🔄 Terapia Secuencial IV→VO",
    ])

    # ── Tab 1: Renal dosing ──────────────────────────────────────────────────
    with tab1:
        st.subheader("Ajuste de dosis en insuficiencia renal")
        st.markdown(
            "Introduce el filtrado glomerular estimado (FGe) y selecciona el antibiótico para obtener "
            "la dosis recomendada."
        )

        col1, col2 = st.columns([1, 2])
        with col1:
            fg = st.number_input(
                "FGe (ml/min)",
                min_value=0,
                max_value=200,
                value=60,
                step=5,
                help="Filtrado Glomerular estimado por CKD-EPI o Cockcroft-Gault",
            )
            # CKD classification
            if fg >= 90:
                ckd_stage = "G1 — Normal/Alto (≥90)"
                ckd_color = "normal"
            elif fg >= 60:
                ckd_stage = "G2 — Leve reducción (60-89)"
                ckd_color = "normal"
            elif fg >= 45:
                ckd_stage = "G3a — Moderada reducción (45-59)"
                ckd_color = "warning"
            elif fg >= 30:
                ckd_stage = "G3b — Moderada-severa (30-44)"
                ckd_color = "warning"
            elif fg >= 15:
                ckd_stage = "G4 — Severa reducción (15-29)"
                ckd_color = "error"
            else:
                ckd_stage = "G5 — Fallo renal (<15)"
                ckd_color = "error"

            st.info(f"**ERC estadio:** {ckd_stage}")

        with col2:
            drug_names = [d["name"] for d in renal_data["drugs"]]
            selected_drug = st.selectbox("Seleccionar antibiótico", drug_names)

        # Find drug and compute dose
        drug_info = next((d for d in renal_data["drugs"] if d["name"] == selected_drug), None)
        if drug_info:
            if drug_info.get("alert"):
                st.warning(f"⚠️ {drug_info['alert']}")
            if drug_info.get("notes"):
                st.info(f"ℹ️ {drug_info['notes']}")

            for route_entry in drug_info["routes"]:
                route = route_entry["route"]
                st.markdown(f"**Vía: {route}**")
                dose_found = "No se encontró dosis para este FGe"
                for tier in route_entry["tiers"]:
                    min_fg = tier.get("min_fg", 0)
                    max_fg = tier.get("max_fg", 999)
                    if max_fg is None:
                        max_fg = 999
                    if min_fg <= fg <= max_fg:
                        dose_found = tier["dose"]
                        break
                    elif min_fg <= fg and max_fg == 999:
                        dose_found = tier["dose"]
                        break

                # Color-code by FG severity
                if fg < 15:
                    st.error(f"🔴 Dosis recomendada: **{dose_found}**")
                elif fg < 30:
                    st.error(f"🔴 Dosis recomendada: **{dose_found}**")
                elif fg < 60:
                    st.warning(f"🟡 Dosis recomendada: **{dose_found}**")
                else:
                    st.success(f"🟢 Dosis recomendada: **{dose_found}**")

                # Show full tier table
                with st.expander("Ver tabla completa de ajuste"):
                    tier_data = []
                    for tier in route_entry["tiers"]:
                        min_fg = tier.get("min_fg", 0)
                        max_fg = tier.get("max_fg")
                        if max_fg is None:
                            rango = f"≥{min_fg} ml/min"
                        else:
                            rango = f"{min_fg}–{max_fg} ml/min"
                        tier_data.append({"FGe": rango, "Dosis": tier["dose"]})
                    import pandas as pd
                    st.dataframe(pd.DataFrame(tier_data), hide_index=True, use_container_width=True)

        st.divider()
        st.caption(renal_data["notes"])

    # ── Tab 2: Vancomycin nomogram ───────────────────────────────────────────
    with tab2:
        st.subheader("Dosificación de Vancomicina")
        st.markdown(
            "Nomograma para el cálculo de dosis de carga y mantenimiento basado en peso real y función renal."
        )

        for note in vanco_data["notes"]:
            st.info(f"ℹ️ {note}")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Peso real (kg)", min_value=20, max_value=200, value=70, step=5)
            fg_vanco = st.number_input(
                "FGe (ml/min)", min_value=0, max_value=200, value=60, step=5, key="fg_vanco"
            )

        with col2:
            # Loading dose
            ld_info = vanco_data["loading_dose"]
            ld_min = round(weight * 25)
            ld_max = round(weight * 30)
            ld_min = min(ld_min, ld_info["max_dose_mg"])
            ld_max = min(ld_max, ld_info["max_dose_mg"])
            st.metric("Dosis de carga recomendada", f"{ld_min}–{ld_max} mg")
            st.caption(f"(25-30 mg/kg · máx {ld_info['max_dose_mg']} mg · infundir en {ld_info['infusion_time_min']} min)")

        # Maintenance from nomogram
        nom = vanco_data["maintenance_nomogram"]
        weight_ranges = nom["weight_ranges"]
        fg_ranges = nom["fg_ranges"]

        # Determine weight category
        if weight < 60:
            w_cat = "<60 kg"
        elif weight <= 70:
            w_cat = "60-70 kg"
        elif weight <= 80:
            w_cat = "71-80 kg"
        elif weight <= 90:
            w_cat = "81-90 kg"
        elif weight <= 100:
            w_cat = "91-100 kg"
        else:
            w_cat = ">100 kg"

        # Determine FG category
        if fg_vanco >= 70:
            fg_cat = ">70"
        elif fg_vanco >= 50:
            fg_cat = "50-70"
        elif fg_vanco >= 30:
            fg_cat = "30-49"
        elif fg_vanco >= 10:
            fg_cat = "10-29"
        else:
            fg_cat = "<10"

        maintenance_dose = nom["doses"][w_cat][fg_cat]
        st.markdown("---")
        st.subheader("Resultado")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Categoría de peso", w_cat)
            st.metric("Categoría FGe", fg_cat)
        with col_b:
            st.success(f"**Dosis de mantenimiento: {maintenance_dose}**")

        # Show monitoring info
        st.markdown("---")
        st.subheader("Monitorización")
        mon = vanco_data["monitoring"]
        st.markdown(f"- **Objetivo PK/PD:** {mon['auc_target']}")
        st.markdown(f"- **Nivel valle:** {mon['trough_target']}")
        st.markdown(f"- **Momento extracción:** {mon['timing']}")
        st.markdown(f"- **Frecuencia:** {mon['frequency']}")

        # Full nomogram table
        with st.expander("📊 Ver nomograma completo"):
            import pandas as pd
            table_data = []
            for w_range in weight_ranges:
                row = {"Peso": w_range}
                for fg_r in fg_ranges:
                    row[f"FGe {fg_r}"] = nom["doses"][w_range][fg_r]
                table_data.append(row)
            df = pd.DataFrame(table_data).set_index("Peso")
            st.dataframe(df, use_container_width=True)

        st.divider()
        st.warning(
            "⚠️ Este nomograma es orientativo. Se recomienda monitorización de niveles y ajuste "
            "individualizado. Contactar con Enfermedades Infecciosas para casos complejos."
        )

    # ── Tab 3: Sequential therapy ────────────────────────────────────────────
    with tab3:
        st.subheader("Terapia Secuencial IV → VO")
        st.markdown(
            """
            El paso de vía IV a vía oral debe considerarse cuando se cumplen **todos** los criterios:
            - ✅ Mejoría clínica objetiva
            - ✅ Afebril >24 horas
            - ✅ Tolerancia oral adecuada
            - ✅ Tracto gastrointestinal funcionante
            - ✅ No contraindicación para la absorción oral
            """
        )

        st.markdown("---")
        st.subheader("Antibióticos con alta biodisponibilidad oral (>70%)")
        st.markdown("*En estos fármacos el cambio IV→VO no supone pérdida significativa de eficacia.*")

        seq = dosing_data["sequential_therapy"]
        import pandas as pd
        rows = []
        for ab in seq["antibiotics_with_excellent_oral_bioavailability"]:
            rows.append({
                "Fármaco": ab["name"],
                "Dosis IV": ab["iv"],
                "Dosis VO equivalente": ab["vo"],
                "Nota": ab["note"],
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, hide_index=True, use_container_width=True)


def page_farmacos():
    st.title("📋 Referencia de Fármacos Antimicrobianos")
    st.markdown(
        "Dosis estándar e incrementadas según la Guía de Tratamiento Antimicrobiano, "
        "Hospital Universitario de Valme (2023)."
    )

    dosing_data = load_dosing()

    # Filter by class
    classes = [cls["class"] for cls in dosing_data["antibiotic_classes"]]
    selected_class = st.selectbox("Filtrar por clase", ["Todas"] + classes)

    # Filter by search
    drug_search = st.text_input("🔍 Buscar fármaco", placeholder="ej. vancomicina, meropenem…")

    st.divider()

    import pandas as pd

    for ab_class in dosing_data["antibiotic_classes"]:
        if selected_class != "Todas" and ab_class["class"] != selected_class:
            continue

        # Filter drugs by search
        drugs = ab_class["antibiotics"]
        if drug_search:
            drugs = [d for d in drugs if drug_search.lower() in d["name"].lower()]
        if not drugs:
            continue

        st.subheader(f"💊 {ab_class['class']}")
        rows = []
        for d in drugs:
            rows.append({
                "Fármaco": d["name"],
                "Vía": ", ".join(d["routes"]),
                "Dosis estándar": d["standard_dose"],
                "Dosis incrementada (I)": d["increased_dose"],
                "Notas": d["notes"],
            })
        df = pd.DataFrame(rows)
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Notas": st.column_config.TextColumn(width="large"),
                "Dosis estándar": st.column_config.TextColumn(width="medium"),
                "Dosis incrementada (I)": st.column_config.TextColumn(width="medium"),
            },
        )
        st.markdown("")

    st.divider()
    st.markdown(
        """
        **Nota:** Dosis incrementadas corresponden a la categoría **I** del antibiograma
        (*Sensible cuando se Incrementa la exposición*). El resto de antimicrobianos de la guía
        sin dosis incrementada deben usarse solo en dosis estándar.
        """
    )
    st.caption(
        "Fuente: Guía de Tratamiento Antimicrobiano en Adultos, Hospital Universitario de Valme (2023). "
        "Ref: The Sandford Guide to Antimicrobial Therapy 2019."
    )


def page_anexos():
    st.title("📎 Anexos Clínicos")

    content = load_content()
    annexes = content.get("annexes", [])

    if not annexes:
        st.warning("No se encontraron anexos.")
        return

    for annex in annexes:
        with st.expander(f"**{annex['code']}. {annex['title']}**"):
            st.markdown(annex.get("content", "Sin contenido disponible."))

    st.divider()
    st.caption(
        "Fuente: Guía de Tratamiento Antimicrobiano en Adultos, "
        "Hospital Universitario de Valme (2023). Grupo PROA."
    )


def page_anexo_detail():
    """Show single annex full content."""
    content = load_content()
    annexes = {a["id"]: a for a in content.get("annexes", [])}
    annex_id = st.session_state.selected_chapter

    if annex_id not in annexes:
        st.error("Anexo no encontrado.")
        return

    ann = annexes[annex_id]
    st.markdown(f"### 📎 {ann['code']}. {ann['title']}")
    st.divider()
    st.markdown(ann.get("content", ""))
    st.divider()
    if st.button("← Volver a Anexos"):
        st.session_state.page = "anexos"
        st.rerun()


# ── Main routing ─────────────────────────────────────────────────────────────
render_sidebar()

page = st.session_state.page

if page == "home":
    page_home()
elif page == "chapter":
    page_chapter()
elif page == "search":
    page_search()
elif page == "calculadoras":
    page_calculadoras()
elif page == "farmacos":
    page_farmacos()
elif page == "anexos":
    page_anexos()
elif page == "anexo_detail":
    page_anexo_detail()
else:
    page_home()
