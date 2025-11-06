import datetime
import random
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import os

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Rastreo de Proyectos - CONALEP Hidalgo", page_icon="📊")

st.title("📊 Rastreo de Proyectos - Dirección General CONALEP Hidalgo")

st.write("""
Esta aplicación permite registrar, consultar y actualizar el estado de los **proyectos y actividades**
de la Dirección General del CONALEP Hidalgo.
""")

# --- ARCHIVO CSV PARA GUARDAR DATOS ---
csv_file = "proyectos.csv"

# --- CARGAR O CREAR DATAFRAME ---
if "df" not in st.session_state:
    if os.path.exists(csv_file):
        st.session_state.df = pd.read_csv(csv_file)
    else:
        np.random.seed(42)
        areas = [
            "Planeación y Evaluación",
            "Infraestructura",
            "Recursos Humanos",
            "Informática",
            "Vinculación",
            "Dirección General"
        ]

        data = {
            "ID": [f"PROY-{i}" for i in range(1050, 1000, -1)],
            "Proyecto": np.random.choice([
                "Implementación de fibra óptica",
                "Mantenimiento de red en planteles",
                "Actualización de sistemas internos",
                "Revisión de cámaras IP",
                "Capacitación de personal",
                "Auditoría de infraestructura tecnológica",
                "Desarrollo de software educativo"
            ], size=50),
            "Área": np.random.choice(areas, size=50),
            "Responsable": np.random.choice(["Juan Pérez", "Ana López", "Carlos Torres", "María García", "Luis Hernández"], size=50),
            "Estatus": np.random.choice(["Pendiente", "En progreso", "Completado"], size=50),
            "Avance (%)": np.random.randint(0, 100, size=50),
            "Fecha de inicio": [
                datetime.date(2024, 1, 1) + datetime.timedelta(days=random.randint(0, 200))
                for _ in range(50)
            ],
            "Fecha estimada de término": [
                datetime.date(2024, 7, 1) + datetime.timedelta(days=random.randint(0, 90))
                for _ in range(50)
            ],
            "Comentarios": np.random.choice([
                "En espera de aprobación",
                "En ejecución",
                "Completado con éxito",
                "Requiere recursos adicionales",
                "En revisión por la Dirección"
            ], size=50)
        }

        st.session_state.df = pd.DataFrame(data)
        st.session_state.df.to_csv(csv_file, index=False)

# --- FUNCIÓN PARA GUARDAR CAMBIOS ---
def guardar_datos():
    st.session_state.df.to_csv(csv_file, index=False)

# --- SECCIÓN: AGREGAR NUEVO PROYECTO ---
st.header("➕ Agregar nuevo proyecto o actividad")

with st.form("add_project_form"):
    proyecto = st.text_input("Nombre del proyecto o actividad")
    area = st.selectbox("Área responsable", [
        "Planeación y Evaluación", "Infraestructura", "Recursos Humanos",
        "Informática","Vinculación","Dirección General"
    ])
    responsable = st.text_input("Responsable o encargado")
    fecha_inicio = st.date_input("Fecha de inicio", datetime.date.today())
    fecha_fin = st.date_input("Fecha estimada de término", datetime.date.today() + datetime.timedelta(days=30))
    avance = st.slider("Porcentaje de avance", 0, 100, 0)
    comentarios = st.text_area("Comentarios u observaciones")
    submitted = st.form_submit_button("Agregar proyecto")

if submitted:
    if len(st.session_state.df) > 0:
        last_id = max(int(x.split('-')[1]) for x in st.session_state.df["ID"])
    else:
        last_id = 1000
    new_id = f"PROY-{last_id + 1}"

    df_new = pd.DataFrame([{
        "ID": new_id,
        "Proyecto": proyecto,
        "Área": area,
        "Responsable": responsable,
        "Estatus": "Pendiente" if avance < 100 else "Completado",
        "Avance (%)": avance,
        "Fecha de inicio": fecha_inicio,
        "Fecha estimada de término": fecha_fin,
        "Comentarios": comentarios
    }])

    st.session_state.df = pd.concat([df_new, st.session_state.df], ignore_index=True)
    guardar_datos()
    st.success(f"✅ Proyecto '{proyecto}' agregado exitosamente.")

# --- SECCIÓN: BUSCAR Y EDITAR PROYECTO EXISTENTE ---
st.header("🔍 Buscar y actualizar proyecto existente")

busqueda = st.text_input("Buscar por nombre del proyecto o ID")

if busqueda:
    resultados = st.session_state.df[
        st.session_state.df["Proyecto"].str.contains(busqueda, case=False, na=False) |
        st.session_state.df["ID"].str.contains(busqueda, case=False, na=False)
    ]

    if resultados.empty:
        st.warning("⚠️ No se encontraron proyectos con ese nombre o ID.")
    else:
        st.write("Resultados encontrados:")
        st.dataframe(resultados, use_container_width=True, hide_index=True)

        seleccion = st.selectbox("Selecciona un proyecto para editar o eliminar:", resultados["ID"])

        if seleccion:
            proyecto_editar = st.session_state.df[st.session_state.df["ID"] == seleccion].iloc[0]

            st.subheader(f"✏️ Editar proyecto: {proyecto_editar['Proyecto']}")
            nuevo_estatus = st.selectbox(
                "Estatus",
                ["Pendiente", "En progreso", "Completado"],
                index=["Pendiente", "En progreso", "Completado"].index(proyecto_editar["Estatus"])
            )
            nuevo_avance = st.slider("Avance (%)", 0, 100, int(proyecto_editar["Avance (%)"]))
            nuevo_comentario = st.text_area("Comentarios", proyecto_editar["Comentarios"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Guardar cambios"):
                    idx = st.session_state.df.index[st.session_state.df["ID"] == seleccion][0]
                    st.session_state.df.at[idx, "Estatus"] = nuevo_estatus
                    st.session_state.df.at[idx, "Avance (%)"] = nuevo_avance
                    st.session_state.df.at[idx, "Comentarios"] = nuevo_comentario
                    guardar_datos()
                    st.success(f"✅ Proyecto '{proyecto_editar['Proyecto']}' actualizado correctamente.")
            with col2:
                if st.button("🗑️ Eliminar proyecto"):
                    st.session_state.df = st.session_state.df[st.session_state.df["ID"] != seleccion]
                    guardar_datos()
                    st.warning(f"🗑️ Proyecto '{proyecto_editar['Proyecto']}' eliminado correctamente.")

# --- SECCIÓN: TABLA DE PROYECTOS ---
st.header("📋 Proyectos registrados")
st.write(f"Total de proyectos: **{len(st.session_state.df)}**")

st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)

# --- ESTADÍSTICAS ---
st.header("📈 Estadísticas generales")

col1, col2, col3 = st.columns(3)
total = len(st.session_state.df)
completados = len(st.session_state.df[st.session_state.df["Estatus"] == "Completado"])
en_progreso = len(st.session_state.df[st.session_state.df["Estatus"] == "En progreso"])
avance_promedio = int(st.session_state.df["Avance (%)"].mean())

col1.metric("Proyectos completados", completados)
col2.metric("En progreso", en_progreso)
col3.metric("Avance promedio (%)", avance_promedio)

# --- GRÁFICAS ---
st.subheader("Distribución de proyectos por área")
chart_area = (
    alt.Chart(st.session_state.df)
    .mark_bar()
    .encode(
        x="Área:N",
        y="count():Q",
        color="Estatus:N"
    )
)
st.altair_chart(chart_area, use_container_width=True)

st.subheader("Proyectos por estatus")
chart_status = (
    alt.Chart(st.session_state.df)
    .mark_arc()
    .encode(
        theta="count():Q",
        color="Estatus:N"
    )
)
st.altair_chart(chart_status, use_container_width=True)

