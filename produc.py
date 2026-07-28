import plotly.express as px  # <--- ADICIONE ESTA IMPORTAÇÃO NO TOPO DO ARQUIVO

# ==========================================
# 2º QUANTIDADE POR GARANTIA
# ==========================================
st.subheader("📈 Quantidade de Ordens por Garantia")

if not df_filtrado.empty:
    contagem_garantia = df_filtrado["GARANTIA"].value_counts().reset_index()
    contagem_garantia.columns = ["Garantia", "Quantidade de OS"]

    col_met1, col_met2, col_met3 = st.columns([1, 1.2, 1.5])
    
    with col_met1:
        st.metric("Total de OS no Período", len(df_filtrado))
        st.dataframe(contagem_garantia, use_container_width=True, hide_index=True)
    
    with col_met2:
        # Criando gráfico de pizza compacto com valores absolutos e porcentagem
        fig = px.pie(
            contagem_garantia, 
            values="Quantidade de OS", 
            names="Garantia",
            hole=0.3 # Efeito rosquinha para visual mais limpo
        )
        
        # Define os rótulos internos com Quantidade (value) + Porcentagem (percent)
        fig.update_traces(
            textinfo="value+percent", 
            textposition="inside",
            hovertemplate="<b>%{label}</b><br>Quantidade: %{value}<br>Porcentagem: %{percent}"
        )
        
        # Ajusta o tamanho do gráfico e reduz margens para ficar menor
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum registro encontrado para o período/filtros selecionados.")
