# Instale no terminal antes: pip install sqlalchemy psycopg2-binary
import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import create_engine

st.set_page_config(page_title="Controle de Produtividade Técnica", layout="wide")

# Cole a sua URI completa com a SENHA aqui:
DATABASE_URL = "postgresql://postgres.nyxvvsrgddfwwwnvfecj:Deusmaravilhoso@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)

engine = get_engine()

def carregar_dados():
    try:
        query = """
            SELECT 
                data_entrada AS "DATA DE ENTRADA", 
                numero_service AS "NUMERO DA SERVICE", 
                responsavel AS "RESPONSAVEL", 
                categoria_servico AS "CATEGORIA DE SERVIÇO", 
                garantia AS "GARANTIA", 
                care AS "CARE", 
                cameras_allied AS "CAMERAS ALLIED", 
                hhp_valid_check AS "HHP VALID CHECK" 
            FROM produtividade 
            ORDER BY id DESC
        """
        df = pd.read_sql(query, engine)
        if not df.empty:
            df["DATA DE ENTRADA"] = pd.to_datetime(df["DATA DE ENTRADA"]).dt.strftime("%d/%m/%Y")
        return df
    except Exception as e:
        return pd.DataFrame(columns=[
            "DATA DE ENTRADA", "NUMERO DA SERVICE", "RESPONSAVEL", 
            "CATEGORIA DE SERVIÇO", "GARANTIA", "CARE", 
            "CAMERAS ALLIED", "HHP VALID CHECK"
        ])

st.title("📋 Produtividade HHP")

# Listas do formulário
TECNICOS = ["Erison", "Bruno", "Felipe", "Gabriel", "Gabrielli", "João da Hora", "Leonardo", "Ludian", "Marcia", "Tomé"]
LISTA_CATEGORIA = ["Analise Técnica", "Troca de peças", "Orçamento recusado (X09)", "SAW", "IMEI", "Software Desbloqueio", "Parecer técnico - Laudo", "Suporte técnico - Q&A", "Reparo completo", "Solicitação peças", "OQC", "Orçamento anexado"]
LISTA_GARANTIA = ["OW", "LP", "CARE +", "STOCK REPAIR", "ALLIED", "CARREFOUR", "BÉLGICA", "SASCAR", "SDS", "SIS", "ASSURANT", "SAW"]
LISTA_CARE = ["FEITO", "NÃO FEITO", "ALLIED", "CARREFOUR", "SASCAR", "SDS", "SIS"]
LISTA_CAMERAS_ALLIED = ["NÃO APLICÁVEL", "NÃO FEITO", "FEITO"]
LISTA_HHP_CHECK = ["NÃO APLICÁVEL", "NÃO FEITO", "FEITO"]

df_dados = carregar_dados()

with st.sidebar:
    st.header("👤 Identificação")
    tecnico_logado = st.selectbox("Selecione seu nome (Login):", TECNICOS)

st.subheader("➕ Inserir Novo Serviço")
with st.form("form_servico", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        data_entrada = st.date_input("DATA DE ENTRADA", value=date.today())
        num_service = st.text_input("NUMERO DA SERVICE (OS)")
    with col2:
        categoria = st.selectbox("CATEGORIA DE SERVIÇO", LISTA_CATEGORIA)
        garantia = st.selectbox("GARANTIA", LISTA_GARANTIA)
    with col3:
        care = st.selectbox("CARE", LISTA_CARE)
        cameras = st.selectbox("CAMERAS ALLIED", LISTA_CAMERAS_ALLIED)
        hhp_check = st.selectbox("HHP VALID CHECK", LISTA_HHP_CHECK)
        
    btn_salvar = st.form_submit_button("💾 Salvar Registro")

if btn_salvar:
    if not num_service:
        st.error("Por favor, preencha o número da Service/OS!")
    else:
        novo_registro = pd.DataFrame([{
            "data_entrada": data_entrada,
            "numero_service": num_service,
            "responsavel": tecnico_logado,
            "categoria_servico": categoria,
            "garantia": garantia,
            "care": care,
            "cameras_allied": cameras,
            "hhp_valid_check": hhp_check
        }])
        novo_registro.to_sql("produtividade", engine, if_exists="append", index=False)
        st.success(f"OS {num_service} salva com sucesso!")
        st.rerun()

st.divider()
st.subheader("📊 Registros no Banco")
st.dataframe(df_dados, use_container_width=True, hide_index=True)


st.divider()

# ==========================================
# FILTROS
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("🔎 Filtros")

df_filtrado = df_dados.copy()

# Número da Service
filtro_service = st.sidebar.text_input("Número da Service")

# Responsável
filtro_responsavel = st.sidebar.multiselect(
    "Responsável",
    sorted(df_dados["RESPONSAVEL"].dropna().unique())
)

# Categoria
filtro_categoria = st.sidebar.multiselect(
    "Categoria",
    sorted(df_dados["CATEGORIA DE SERVIÇO"].dropna().unique())
)

# Garantia
filtro_garantia = st.sidebar.multiselect(
    "Garantia",
    sorted(df_dados["GARANTIA"].dropna().unique())
)

# CARE
filtro_care = st.sidebar.multiselect(
    "CARE",
    sorted(df_dados["CARE"].dropna().unique())
)

# Cameras Allied
filtro_camera = st.sidebar.multiselect(
    "Cameras Allied",
    sorted(df_dados["CAMERAS ALLIED"].dropna().unique())
)

# HHP Valid Check
filtro_hhp = st.sidebar.multiselect(
    "HHP Valid Check",
    sorted(df_dados["HHP VALID CHECK"].dropna().unique())
)

# ==========================================
# APLICA FILTROS
# ==========================================

if filtro_service:
    df_filtrado = df_filtrado[
        df_filtrado["NUMERO DA SERVICE"].astype(str).str.contains(
            filtro_service,
            case=False,
            na=False
        )
    ]

if filtro_responsavel:
    df_filtrado = df_filtrado[
        df_filtrado["RESPONSAVEL"].isin(filtro_responsavel)
    ]

if filtro_categoria:
    df_filtrado = df_filtrado[
        df_filtrado["CATEGORIA DE SERVIÇO"].isin(filtro_categoria)
    ]

if filtro_garantia:
    df_filtrado = df_filtrado[
        df_filtrado["GARANTIA"].isin(filtro_garantia)
    ]

if filtro_care:
    df_filtrado = df_filtrado[
        df_filtrado["CARE"].isin(filtro_care)
    ]

if filtro_camera:
    df_filtrado = df_filtrado[
        df_filtrado["CAMERAS ALLIED"].isin(filtro_camera)
    ]

if filtro_hhp:
    df_filtrado = df_filtrado[
        df_filtrado["HHP VALID CHECK"].isin(filtro_hhp)
    ]

# ==========================================
# RESULTADOS
# ==========================================

st.subheader("📊 Registros")

col1, col2 = st.columns([1,4])

with col1:
    st.metric("Total", len(df_filtrado))

with col2:
    st.write("")

st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True
)
