# Instale no terminal antes: pip install sqlalchemy psycopg2-binary
import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import create_engine

st.set_page_config(page_title="Controle de Produtividade Técnica", layout="wide")

# Cole a sua URI completa com a SENHA aqui:
DATABASE_URL = "postgresql://postgres.nyxvvsrgddfwwwnvfecj:[Deusmaravilhoso]@aws-0-sa-east-1.pooler.supabase.com:5432/postgres

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
