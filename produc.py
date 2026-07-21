import streamlit as st
import pandas as pd
from datetime import date

# Configuração da página
st.set_page_config(page_title="Controle de Produtividade Técnica", layout="wide")

st.title("📋 Lançamento de Produtividade Técnica")

# --- LISTAS OFICIAIS EXTRAÍDAS DAS SUAS IMAGENS ---
TECNICOS = ["Ludian", "João da Hora", "Erison", "Leonardo"]

LISTA_CATEGORIA = [
    "Analise Técnica",
    "Troca de peças",
    "Orçamento recusado (X09)",
    "SAW",
    "IMEI",
    "Software Desbloqueio",
    "Parecer técnico - Laudo",
    "Suporte técnico - Q&A",
    "Reparo completo",
    "Solicitação peças",
    "OQC",
    "Orçamento anexado"
]

LISTA_GARANTIA = [
    "OW",
    "LP",
    "CARE +",
    "STOCK REPAIR",
    "ALLIED",
    "CARREFOUR",
    "BÉLGICA",
    "SASCAR",
    "SDS",
    "SIS",
    "ASSURANT",
    "SAW"
]

LISTA_CARE = [
    "FEITO",
    "NÃO FEITO",
    "ALLIED",
    "CARREFOUR",
    "SASCAR",
    "SDS",
    "SIS"
]

LISTA_CAMERAS_ALLIED = [
    "NÃO APLICÁVEL",
    "NÃO FEITO",
    "FEITO"
]

LISTA_HHP_CHECK = [
    "NÃO APLICÁVEL",
    "NÃO FEITO",
    "FEITO"
]

# Armazenamento temporário no app
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "DATA DE ENTRADA", "NUMERO DA SERVICE", "RESPONSAVEL", 
        "CATEGORIA DE SERVIÇO", "GARANTIA", "CARE", 
        "CAMERAS ALLIED", "HHP VALID CHECK"
    ])

# --- BARRA LATERAL: SELEÇÃO DO TÉCNICO ---
with st.sidebar:
    st.header("👤 Identificação do Técnico")
    tecnico_logado = st.selectbox("Selecione seu nome (Login):", TECNICOS)
    st.divider()

# --- FORMULÁRIO DE INSERÇÃO ---
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

# --- LÓGICA DE SALVAMENTO ---
if btn_salvar:
    if not num_service:
        st.error("Por favor, preencha o número da Service/OS!")
    else:
        novo_registro = {
            "DATA DE ENTRADA": data_entrada.strftime("%d/%m/%Y"),
            "NUMERO DA SERVICE": num_service,
            "RESPONSAVEL": tecnico_logado,
            "CATEGORIA DE SERVIÇO": categoria,
            "GARANTIA": garantia,
            "CARE": care,
            "CAMERAS ALLIED": cameras,
            "HHP VALID CHECK": hhp_check
        }
        st.session_state.dados = pd.concat([
            st.session_state.dados, 
            pd.DataFrame([novo_registro])
        ], ignore_index=True)
        
        st.success(f"OS {num_service} registrada com sucesso para {tecnico_logado}!")

# --- TABELA DE REGISTROS ---
st.divider()
st.subheader("📊 Registros Inseridos")

if not st.session_state.dados.empty:
    st.dataframe(
        st.session_state.dados, 
        use_container_width=True, 
        hide_index=True
    )
else:
    st.info("Nenhum registro lançado ainda hoje.")
