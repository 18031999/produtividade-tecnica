import streamlit as st
import pandas as pd
from datetime import date, timedelta

# Configuração da página
st.set_page_config(page_title="Controle de Produtividade Técnica", layout="wide")

st.title("📋 Produtividade HHP")

# Senha do Supervisor
SENHA_SUPERVISOR = "admin123"

# --- LISTAS OFICIAIS ---
TECNICOS = ["Erison", "Bruno", "Felipe", "Gabriel", "Gabrielli", "João da Hora", "Leonardo", "Ludian", "Marcia", "Tomé"]

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
        
        st.success(f"OS {num_service} registrada com sucesso!")
        st.rerun()

# --- TABELA DE REGISTROS ---
st.divider()
st.subheader("📊 Registros")

if not st.session_state.dados.empty:
    
    # --- FILTROS EM CIMA DA TABELA ---
    st.markdown("🔍 **Filtros Rápidos da Tabela:**")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    
    with f_col1:
        filtro_resp = st.multiselect(
            "Responsável:", 
            options=sorted(st.session_state.dados["RESPONSAVEL"].unique().tolist())
        )
    with f_col2:
        filtro_cat = st.multiselect(
            "Categoria:", 
            options=sorted(st.session_state.dados["CATEGORIA DE SERVIÇO"].unique().tolist())
        )
    with f_col3:
        filtro_gar = st.multiselect(
            "Garantia:", 
            options=sorted(st.session_state.dados["GARANTIA"].unique().tolist())
        )
    with f_col4:
        busca_os = st.text_input("Buscar por Nº OS:")

    # Aplicação dos filtros na tabela
    df_exibir = st.session_state.dados.copy()
    
    if filtro_resp:
        df_exibir = df_exibir[df_exibir["RESPONSAVEL"].isin(filtro_resp)]
    if filtro_cat:
        df_exibir = df_exibir[df_exibir["CATEGORIA DE SERVIÇO"].isin(filtro_cat)]
    if filtro_gar:
        df_exibir = df_exibir[df_exibir["GARANTIA"].isin(filtro_gar)]
    if busca_os:
        df_exibir = df_exibir[df_exibir["NUMERO DA SERVICE"].str.contains(busca_os, case=False, na=False)]

    # --- MODO SUPERVISOR: EDITA E EXCLUI COM CHECKBOX ---
    if is_admin:
        st.info("💡 **Modo Supervisor:** Altere dados direto nas células. Marque 'Excluir' nas linhas desejadas e clique em 'Excluir Selecionados'.")
        
        df_admin = df_exibir.copy()
        df_admin.insert(0, "Excluir", False)
        
        df_editado = st.data_editor(
            df_admin,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Excluir": st.column_config.CheckboxColumn("Excluir?", help="Marque para apagar")
            },
            key="tabela_admin"
        )
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("💾 Salvar Edições"):
                novos_dados = df_editado.drop(columns=["Excluir"]).copy()
                st.session_state.dados.update(novos_dados)
                st.success("Alterações salvas!")
                st.rerun()
                
        with col_btn2:
            if st.button("🗑️ Excluir Selecionados", type="primary"):
                os_para_remover = df_editado[df_editado["Excluir"] == True]["NUMERO DA SERVICE"].tolist()
                st.session_state.dados = st.session_state.dados[
                    ~st.session_state.dados["NUMERO DA SERVICE"].isin(os_para_remover)
                ]
                st.success("Registros excluídos!")
                st.rerun()

    # --- MODO TÉCNICO NORMAL ---
    else:
        st.dataframe(df_exibir, use_container_width=True, hide_index=True)
        
        # Permitir que o técnico apague lançamento dele feito hoje
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

    # --- SEÇÃO DE HISTÓRICO COM FILTRO DE PERÍODO EM PORTUGUÊS ---
    st.divider()
    st.subheader("📜 Histórico")

    col_p1, col_p2 = st.columns([2, 2])
    
    # Mapeamento do filtro de períodos rápidos para o Português
    opcoes_periodo = {
        "Nenhum (Personalizado)": None,
        "Última Semana": 7,
        "Último Mês": 30,
        "Últimos 3 Meses": 90,
        "Últimos 6 Meses": 180,
        "Último Ano": 365,
        "Últimos 2 Anos": 730
    }

    with col_p1:
        filtro_rapido = st.selectbox("Filtrar por Período:", list(opcoes_periodo.keys()))

    hoje = date.today()

    # Se um período rápido for selecionado, ajusta as datas
    if opcoes_periodo[filtro_rapido] is not None:
        dias_subtrair = opcoes_periodo[filtro_rapido]
        data_inicio_padrao = hoje - timedelta(days=dias_subtrair)
        val_inicial = (data_inicio_padrao, hoje)
    else:
        val_inicial = (hoje, hoje)

    with col_p2:
        periodo_selecionado = st.date_input(
            "Selecione o Intervalo de Datas:",
            value=val_inicial,
            format="DD/MM/YYYY"
        )

    # Preparar filtro de data
    df_historico = df_exibir.copy()
    df_historico["DATA_DT"] = pd.to_datetime(df_historico["DATA DE ENTRADA"], format="%d/%m/%Y").dt.date

    # Aplicar o filtro do calendário
    if isinstance(periodo_selecionado, tuple) and len(periodo_selecionado) == 2:
        d_inicio, d_fim = periodo_selecionado
        df_historico = df_historico[
            (df_historico["DATA_DT"] >= d_inicio) & (df_historico["DATA_DT"] <= d_fim)
        ]
    elif isinstance(periodo_selecionado, tuple) and len(periodo_selecionado) == 1:
        d_inicio = periodo_selecionado[0]
        df_historico = df_historico[df_historico["DATA_DT"] == d_inicio]

    # Exibir resumo filtrado
    if not df_historico.empty:
        col_h1, col_h2 = st.columns([1, 2])
        
        with col_h1:
            st.metric("Total de OS no Período", len(df_historico))
            
        with col_h2:
            st.markdown("**Quantidade por Garantia no Período:**")
            contagem_garantia = df_historico["GARANTIA"].value_counts().reset_index()
            contagem_garantia.columns = ["Tipo de Garantia", "Total de OS"]
            
            st.dataframe(contagem_garantia, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum registro encontrado para o período/dia selecionado.")

else:
    st.info("Nenhum registro encontrado.")
