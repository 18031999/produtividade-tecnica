import streamlit as st
import pandas as pd
from datetime import date

# Configuração da página
st.set_page_config(page_title="Controle de Produtividade Técnica", layout="wide")

st.title("📋Produtividade HHP")

# Senha do Supervisor (Altere aqui se desejar)
SENHA_SUPERVISOR = "admin123"

# --- LISTAS OFICIAIS ---
TECNICOS = ["Ludian", "João da Hora", "Erison", "Leonardo", "Tomé","Gabrielli", "Gabriel", "Vagner"]

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

# Armazenamento temporário dos dados
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "DATA DE ENTRADA", "NUMERO DA SERVICE", "RESPONSAVEL", 
        "CATEGORIA DE SERVIÇO", "GARANTIA", "CARE", 
        "CAMERAS ALLIED", "HHP VALID CHECK"
    ])

# --- BARRA LATERAL (APENAS LOGIN E SUPERVISOR) ---
with st.sidebar:
    st.header("👤 Identificação")
    tecnico_logado = st.selectbox("Selecione seu nome (Login):", TECNICOS)
    
    st.divider()
    st.header("🔒 Acesso Supervisor")
    senha_digitada = st.text_input("Senha do Supervisor:", type="password")
    is_admin = (senha_digitada == SENHA_SUPERVISOR)
    
    if is_admin:
        st.success("Modo Supervisor Ativo 🔓")

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
        st.rerun()

# --- TABELA DE REGISTROS ---
st.divider()
st.subheader("📊 Tabela de Registros Inseridos")

if not st.session_state.dados.empty:
    
    # --- MODO SUPERVISOR: EDITA E EXCLUI COM CHECKBOX ---
    if is_admin:
        st.info("💡 **Modo Supervisor:** Altere textos direto nas células. Para excluir, marque a caixa 'Excluir' na linha desejada e clique em 'Excluir Selecionados'.")
        
        df_admin = st.session_state.dados.copy()
        df_admin.insert(0, "Excluir", False)
        
        df_editado = st.data_editor(
            df_admin,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Excluir": st.column_config.CheckboxColumn("Excluir?", help="Marque para apagar esta linha")
            },
            key="tabela_admin"
        )
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("💾 Salvar Edições"):
                st.session_state.dados = df_editado.drop(columns=["Excluir"]).copy()
                st.success("Alterações salvas!")
                st.rerun()
                
        with col_btn2:
            if st.button("🗑️ Excluir Selecionados", type="primary"):
                df_filtrado = df_editado[df_editado["Excluir"] == False].drop(columns=["Excluir"])
                st.session_state.dados = df_filtrado.copy()
                st.success("Registros excluídos com sucesso!")
                st.rerun()

    # --- MODO TÉCNICO NORMAL ---
    else:
        st.info("💡 Clique nas colunas para ordenar ou pesquise/filtre dados na própria tabela estilo Excel.")
        st.data_editor(
            st.session_state.dados,
            use_container_width=True,
            hide_index=True,
            disabled=True,  # Impede técnicos de editarem os dados
            key="tabela_tecnico"
        )
        
        # Permitir que o técnico apague lançamento DELE feito HOJE
        hoje_str = date.today().strftime("%d/%m/%Y")
        meus_lancamentos_hoje = st.session_state.dados[
            (st.session_state.dados["RESPONSAVEL"] == tecnico_logado) & 
            (st.session_state.dados["DATA DE ENTRADA"] == hoje_str)
        ]
        
        if not meus_lancamentos_hoje.empty:
            st.markdown("##### 🗑️ Corrigir/Excluir meu lançamento de hoje:")
            col_sel, col_del = st.columns([3, 1])
            with col_sel:
                os_para_excluir = st.selectbox(
                    "Selecione a OS que deseja apagar:", 
                    meus_lancamentos_hoje["NUMERO DA SERVICE"].unique(),
                    label_visibility="collapsed"
                )
            with col_del:
                if st.button("❌ Apagar OS"):
                    st.session_state.dados = st.session_state.dados[
                        st.session_state.dados["NUMERO DA SERVICE"] != os_para_excluir
                    ]
                    st.success(f"OS {os_para_excluir} excluída!")
                    st.rerun()

else:
    st.info("Nenhum registro encontrado.")

# --- HISTÓRICO / RESUMO DE GARANTIA NO FINAL ---
st.divider()
st.subheader("📜 Histórico")

if not st.session_state.dados.empty:
    col_h1, col_h2 = st.columns([1, 2])
    
    with col_h1:
        st.metric("Total de OS Cadastradas", len(st.session_state.dados))
        
    with col_h2:
        st.markdown("**Quantidade Total por Garantia:**")
        contagem_garantia = st.session_state.dados["GARANTIA"].value_counts().reset_index()
        contagem_garantia.columns = ["Tipo de Garantia", "Total de OS"]
        
        st.dataframe(
            contagem_garantia, 
            use_container_width=True, 
            hide_index=True
        )
else:
    st.caption("O Histórico será exibido aqui assim que os primeiros registros forem adicionados.")
