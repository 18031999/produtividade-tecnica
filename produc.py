import streamlit as st
import pandas as pd
from datetime import date

# Configuração da página
st.set_page_config(page_title="Controle de Produtividade Técnica", layout="wide")

st.title("📋 Lançamento de Produtividade Técnica")

# Senha do Supervisor (Você pode alterar aqui)
SENHA_SUPERVISOR = "admin123"

# --- LISTAS OFICIAIS ---
TECNICOS = ["Ludian", "João da Hora", "Erison", "Leonardo"]

LISTA_CATEGORIA = [
    "Analise Técnica", "Troca de peças", "Orçamento recusado (X09)",
    "SAW", "IMEI", "Software Desbloqueio", "Parecer técnico - Laudo",
    "Suporte técnico - Q&A", "Reparo completo", "Solicitação peças",
    "OQC", "Orçamento anexado"
]

LISTA_GARANTIA = [
    "OW", "LP", "CARE +", "STOCK REPAIR", "ALLIED", "CARREFOUR",
    "BÉLGICA", "SASCAR", "SDS", "SIS", "ASSURANT", "SAW"
]

LISTA_CARE = ["FEITO", "NÃO FEITO", "ALLIED", "CARREFOUR", "SASCAR", "SDS", "SIS"]
LISTA_CAMERAS_ALLIED = ["NÃO APLICÁVEL", "NÃO FEITO", "FEITO"]
LISTA_HHP_CHECK = ["NÃO APLICÁVEL", "NÃO FEITO", "FEITO"]

# Armazenamento temporário no app
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "DATA DE ENTRADA", "NUMERO DA SERVICE", "RESPONSAVEL", 
        "CATEGORIA DE SERVIÇO", "GARANTIA", "CARE", 
        "CAMERAS ALLIED", "HHP VALID CHECK"
    ])

# --- BARRA LATERAL: LOGIN, FILTROS E MODO SUPERVISOR ---
with st.sidebar:
    st.header("👤 Identificação do Técnico")
    tecnico_logado = st.selectbox("Selecione seu nome (Login):", TECNICOS)
    
    st.divider()
    st.header("🔒 Acesso Supervisor")
    senha_digitada = st.text_input("Senha do Supervisor:", type="password")
    is_admin = (senha_digitada == SENHA_SUPERVISOR)
    
    if is_admin:
        st.success("Modo Supervisor Ativo! 🔓")
    
    st.divider()
    st.header("🔍 Filtros de Visualização")
    filtro_tecnico = st.multiselect("Filtrar por Técnico:", TECNICOS)
    filtro_categoria = st.multiselect("Filtrar por Categoria:", LISTA_CATEGORIA)
    filtro_garantia = st.multiselect("Filtrar por Garantia:", LISTA_GARANTIA)

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

# --- APLICAÇÃO DOS FILTROS ---
df_exibicao = st.session_state.dados.copy()

if filtro_tecnico:
    df_exibicao = df_exibicao[df_exibicao["RESPONSAVEL"].isin(filtro_tecnico)]
if filtro_categoria:
    df_exibicao = df_exibicao[df_exibicao["CATEGORIA DE SERVIÇO"].isin(filtro_categoria)]
if filtro_garantia:
    df_exibicao = df_exibicao[df_exibicao["GARANTIA"].isin(filtro_garantia)]

# --- PAINEIS DE PRODUTIVIDADE ---
st.divider()
st.subheader("📈 Resumo da Produtividade")

if not st.session_state.dados.empty:
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Total de OS Registradas", len(st.session_state.dados))
    with col_m2:
        st.metric("OS na Exibição Atual", len(df_exibicao))
    with col_m3:
        tecnico_mais_produtivo = st.session_state.dados["RESPONSAVEL"].mode()
        if not tecnico_mais_produtivo.empty:
            st.metric("Técnico Lider do Dia", tecnico_mais_produtivo[0])

    aba_tec, aba_cat, aba_gar = st.tabs(["👤 Por Técnico", "🏷️ Por Categoria", "🛡️ Por Garantia"])
    with aba_tec:
        st.dataframe(st.session_state.dados["RESPONSAVEL"].value_counts().reset_index(), use_container_width=True, hide_index=True)
    with aba_cat:
        st.dataframe(st.session_state.dados["CATEGORIA DE SERVIÇO"].value_counts().reset_index(), use_container_width=True, hide_index=True)
    with aba_gar:
        st.dataframe(st.session_state.dados["GARANTIA"].value_counts().reset_index(), use_container_width=True, hide_index=True)

# --- TABELA E GERENCIAMENTO DE EXCLUSÃO/EDIÇÃO ---
st.divider()

if is_admin:
    st.subheader("🛠️ Gerenciamento do Supervisor (Edição Liberada)")
    st.info("💡 Você está no modo Supervisor! Altere os dados direto na tabela abaixo ou marque a caixinha de seleção para excluir linhas.")
    
    # Tabela 100% editável para o supervisor
    dados_editados = st.data_editor(
        df_exibicao,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_supervisor"
    )
    if st.button("💾 Salvar Alterações do Supervisor"):
        st.session_state.dados = dados_editados.copy()
        st.success("Alterações salvas com sucesso!")
        st.rerun()

else:
    st.subheader("📊 Tabela de Registros Inseridos")
    if not df_exibicao.empty:
        hoje_str = date.today().strftime("%d/%m/%Y")
        
        # Exibe a tabela normal
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
        
        # Permite ao técnico excluir apenas os lançamentos DELE feitos HOJE
        st.markdown("##### 🗑️ Cancelar/Excluir lançamento recente (Apenas seus lançamentos de hoje):")
        
        meus_lancamentos_hoje = st.session_state.dados[
            (st.session_state.dados["RESPONSAVEL"] == tecnico_logado) & 
            (st.session_state.dados["DATA DE ENTRADA"] == hoje_str)
        ]
        
        if not meus_lancamentos_hoje.empty:
            os_para_excluir = st.selectbox(
                "Selecione a OS que deseja apagar:", 
                meus_lancamentos_hoje["NUMERO DA SERVICE"].unique()
            )
            if st.button("❌ Confirmar Exclusão"):
                st.session_state.dados = st.session_state.dados[
                    st.session_state.dados["NUMERO DA SERVICE"] != os_para_excluir
                ]
                st.success(f"OS {os_para_excluir} excluída com sucesso!")
                st.rerun()
        else:
            st.caption("Você não tem lançamentos realizados hoje para cancelar.")
    else:
        st.info("Nenhum registro encontrado.")
