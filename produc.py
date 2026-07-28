# Instale no terminal antes: pip install streamlit pandas sqlalchemy psycopg2-binary
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Controle de Produtividade Técnica", layout="wide")

# ==========================================
# SEGURANÇA E CONEXÃO
# ==========================================
DATABASE_URL = "postgresql://postgres.nyxvvsrgddfwwwnvfecj:Deusmaravilhoso@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
ADMIN_PASSWORD = "123"  # <--- DEFINA A SUA SENHA DE ADMINISTRADOR AQUI

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)

engine = get_engine()

def carregar_dados():
    try:
        query = """
            SELECT 
                id,
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
            df["DATA_DT"] = pd.to_datetime(df["DATA DE ENTRADA"])
            df["DATA DE ENTRADA"] = df["DATA_DT"].dt.strftime("%d/%m/%Y")
        return df
    except Exception as e:
        return pd.DataFrame(columns=[
            "id", "DATA DE ENTRADA", "NUMERO DA SERVICE", "RESPONSAVEL", 
            "CATEGORIA DE SERVIÇO", "GARANTIA", "CARE", 
            "CAMERAS ALLIED", "HHP VALID CHECK", "DATA_DT"
        ])

# Listas do formulário
TECNICOS = ["Erison", "Bruno", "Felipe", "Gabriel", "Gabrielli", "João da Hora", "Leonardo", "Ludian", "Marcia", "Tomé"]
LISTA_CATEGORIA = ["Analise Técnica", "Troca de peças", "Orçamento recusado (X09)", "SAW", "IMEI", "Software Desbloqueio", "Parecer técnico - Laudo", "Suporte técnico - Q&A", "Reparo completo", "Solicitação peças", "OQC", "Orçamento anexado"]
LISTA_GARANTIA = ["OW", "LP", "CARE +", "STOCK REPAIR", "ALLIED", "CARREFOUR", "BÉLGICA", "SASCAR", "SDS", "SIS", "ASSURANT", "SAW"]
LISTA_CARE = ["FEITO", "NÃO FEITO", "ALLIED", "CARREFOUR", "SASCAR", "SDS", "SIS"]
LISTA_CAMERAS_ALLIED = ["NÃO APLICÁVEL", "NÃO FEITO", "FEITO"]
LISTA_HHP_CHECK = ["NÃO APLICÁVEL", "NÃO FEITO", "FEITO"]

df_dados = carregar_dados()

# ==========================================
# SIDEBAR - IDENTIFICAÇÃO E OUTROS FILTROS
# ==========================================
with st.sidebar:
    st.header("👤 Identificação")
    tecnico_logado = st.selectbox("Selecione seu nome (Login):", TECNICOS)

    st.markdown("---")
    st.header("🔎 Filtros Específicos")

    filtro_service = st.text_input("Número da Service")
    filtro_responsavel = st.multiselect("Responsável", sorted(df_dados["RESPONSAVEL"].dropna().unique()))
    filtro_categoria = st.multiselect("Categoria", sorted(df_dados["CATEGORIA DE SERVIÇO"].dropna().unique()))
    filtro_garantia = st.multiselect("Garantia", sorted(df_dados["GARANTIA"].dropna().unique()))
    filtro_care = st.multiselect("CARE", sorted(df_dados["CARE"].dropna().unique()))
    filtro_camera = st.multiselect("Cameras Allied", sorted(df_dados["CAMERAS ALLIED"].dropna().unique()))
    filtro_hhp = st.multiselect("HHP Valid Check", sorted(df_dados["HHP VALID CHECK"].dropna().unique()))

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
st.title("📋 Produtividade HHP")

st.info(f"👤 **Técnico Ativo:** {tecnico_logado}")

st.subheader("➕ Inserir Novo Serviço")
with st.form("form_servico", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        data_entrada = st.date_input("DATA DE ENTRADA", value=date.today())
        num_service = st.text_input("NUMERO DA SERVICE (OS)")
        st.text_input("TÉCNICO RESPONSÁVEL", value=tecnico_logado, disabled=True)
        
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
        st.success(f"OS {num_service} salva por {tecnico_logado} com sucesso!")
        st.rerun()

st.divider()

# ==========================================
# FILTRO DE PERÍODO (FORA DA BARRA LATERAL)
# ==========================================
st.subheader("📅 Selecionar Período de Movimentação")

col_data1, col_data2 = st.columns([2, 2])
with col_data1:
    # Filtro de intervalo (Ex: de 27/07/2026 a 28/07/2026)
    periodo_selecionado = st.date_input("Filtrar do dia inicial até o dia final:",
        value=(date.today() - timedelta(days=7), date.today()),
        format="DD/MM/YYYY"
    )

# ==========================================
# APLICAÇÃO DOS FILTROS
# ==========================================
df_filtrado = df_dados.copy()

# Aplica Período
if isinstance(periodo_selecionado, (tuple, list)):
    if len(periodo_selecionado) == 2:
        d_inicio, d_fim = periodo_selecionado
        df_filtrado = df_filtrado[
            (df_filtrado["DATA_DT"].dt.date >= d_inicio) & 
            (df_filtrado["DATA_DT"].dt.date <= d_fim)
        ]
    elif len(periodo_selecionado) == 1:
        d_inicio = periodo_selecionado[0]
        df_filtrado = df_filtrado[df_filtrado["DATA_DT"].dt.date == d_inicio]

if filtro_service:
    df_filtrado = df_filtrado[
        df_filtrado["NUMERO DA SERVICE"].astype(str).str.contains(filtro_service, case=False, na=False)
    ]
if filtro_responsavel:
    df_filtrado = df_filtrado[df_filtrado["RESPONSAVEL"].isin(filtro_responsavel)]
if filtro_categoria:
    df_filtrado = df_filtrado[df_filtrado["CATEGORIA DE SERVIÇO"].isin(filtro_categoria)]
if filtro_garantia:
    df_filtrado = df_filtrado[df_filtrado["GARANTIA"].isin(filtro_garantia)]
if filtro_care:
    df_filtrado = df_filtrado[df_filtrado["CARE"].isin(filtro_care)]
if filtro_camera:
    df_filtrado = df_filtrado[df_filtrado["CAMERAS ALLIED"].isin(filtro_camera)]
if filtro_hhp:
    df_filtrado = df_filtrado[df_filtrado["HHP VALID CHECK"].isin(filtro_hhp)]

# ==========================================
# 1º REGISTROS NO BANCO (MUDADO DE LUGAR)
# ==========================================
st.subheader("📊 Registros no Banco (Filtrados)")
df_exibir = df_filtrado.drop(columns=["id", "DATA_DT"], errors="ignore")
st.dataframe(df_exibir, use_container_width=True, hide_index=True)

st.divider()

# ==========================================
# 2º QUANTIDADE POR GARANTIA
# ==========================================
st.subheader("📈 Quantidade de Ordens por Garantia")

if not df_filtrado.empty:
    contagem_garantia = df_filtrado["GARANTIA"].value_counts().reset_index()
    contagem_garantia.columns = ["Garantia", "Quantidade de OS"]

    col_met1, col_met2 = st.columns([1, 2])
    
    with col_met1:
        st.metric("Total de OS no Período/Filtro", len(df_filtrado))
        st.dataframe(contagem_garantia, use_container_width=True, hide_index=True)
    
    with col_met2:
        st.bar_chart(contagem_garantia.set_index("Garantia"))
else:
    st.warning("Nenhum registro encontrado para o período/filtros selecionados.")

# ==========================================
# PAINEL ADMINISTRATIVO (EDIÇÃO E EXCLUSÃO)
# ==========================================
st.divider()
with st.expander("🔒 Área Restrita - Gerenciamento e Edição (Requer Senha)"):
    senha_digitada = st.text_input("Digite a senha de administrador:", type="password")

    if senha_digitada == ADMIN_PASSWORD:
        st.success("Acesso autorizado!")
        tab_editar, tab_excluir = st.tabs(["✏️ Editar Registro", "❌ Excluir Registro"])

        with tab_editar:
            st.markdown("### Alterar informações diretamente na tabela")
            
            df_edited = st.data_editor(
                df_filtrado.drop(columns=["DATA_DT"], errors="ignore"),
                key="editor_dados",
                disabled=["id"],
                hide_index=True,
                use_container_width=True
            )

            if st.button("💾 Salvar Alterações"):
                try:
                    with engine.begin() as conn:
                        for row in df_edited.to_dict(orient="records"):
                            data_formatada = pd.to_datetime(row["DATA DE ENTRADA"], format="%d/%m/%Y").strftime("%Y-%m-%d")
                            
                            sql = text("""
                                UPDATE produtividade SET
                                    data_entrada = :data_entrada,
                                    numero_service = :numero_service,
                                    responsavel = :responsavel,
                                    categoria_servico = :categoria,
                                    garantia = :garantia,
                                    care = :care,
                                    cameras_allied = :cameras,
                                    hhp_valid_check = :hhp
                                WHERE id = :id
                            """)
                            conn.execute(sql, {
                                "data_entrada": data_formatada,
                                "numero_service": row["NUMERO DA SERVICE"],
                                "responsavel": row["RESPONSAVEL"],
                                "categoria": row["CATEGORIA DE SERVIÇO"],
                                "garantia": row["GARANTIA"],
                                "care": row["CARE"],
                                "cameras": row["CAMERAS ALLIED"],
                                "hhp": row["HHP VALID CHECK"],
                                "id": row["id"]
                            })
                    st.success("Registros atualizados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao atualizar: {e}")

        with tab_excluir:
            st.markdown("### Excluir Registro")
            if not df_dados.empty:
                opcoes = df_dados.apply(lambda r: f"ID: {r['id']} | OS: {r['NUMERO DA SERVICE']} | Técnico: {r['RESPONSAVEL']}", axis=1)
                registro_selecionado = st.selectbox("Selecione o registro para apagar:", opcoes)
                
                id_para_deletar = int(registro_selecionado.split("|")[0].replace("ID:", "").strip())

                if st.button("🚨 Confirmar Exclusão", type="primary"):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("DELETE FROM produtividade WHERE id = :id"), {"id": id_para_deletar})
                        st.success(f"Registro ID {id_para_deletar} removido com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao deletar registro: {e}")

    elif senha_digitada != "":
        st.error("Senha incorreta!")
