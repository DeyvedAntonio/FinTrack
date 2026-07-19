import pandas as pd
import streamlit as st


def render_analytics_charts(movimentacoes):
    """Renderiza os gráficos analíticos do Dashboard de Despesas e Evolução Mensal."""
    if not movimentacoes:
        st.info("Sem dados suficientes para gerar os gráficos analíticos.")
        return

    df = pd.DataFrame(movimentacoes)
    df["valor"] = df["valor"].astype(float)
    df["data"] = pd.to_datetime(df["data"])

    g1, g2 = st.columns(2)

    with g1:
        st.subheader("Despesas por Categoria")
        df_desp = df[df["tipo"] == "DESPESA"]
        if not df_desp.empty:
            desp_by_cat = df_desp.groupby("categoria_nome")["valor"].sum().reset_index()
            st.bar_chart(desp_by_cat, x="categoria_nome", y="valor", color="#EF4444")
        else:
            st.caption("Sem despesas no período selecionado.")

    with g2:
        st.subheader("Evolução das Movimentações por Mês")
        df["mes_ano"] = df["data"].dt.strftime("%Y-%m")
        mov_by_month = df.groupby(["mes_ano", "tipo_display"])["valor"].sum().unstack(fill_value=0)
        st.line_chart(mov_by_month)
