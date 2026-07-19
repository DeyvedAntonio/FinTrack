import pandas as pd
import streamlit as st
import plotly.express as px
# pyrefly: ignore [missing-import]
from core.theme import format_currency


def render_analytics_charts(movimentacoes, moeda="BRL"):
    """Renderiza os gráficos analíticos interativos do Dashboard usando Plotly."""
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
            # Ordenar valores em ordem ascendente para que a maior barra fique no topo do gráfico horizontal
            desp_by_cat = desp_by_cat.sort_values(by="valor", ascending=True)
            desp_by_cat["valor_str"] = desp_by_cat["valor"].apply(lambda v: format_currency(v, moeda))

            max_val = float(desp_by_cat["valor"].max()) if not desp_by_cat.empty else 100.0

            fig_cat = px.bar(
                desp_by_cat,
                x="valor",
                y="categoria_nome",
                orientation="h",
                text="valor_str",
                labels={"valor": "Valor Total", "categoria_nome": "Categoria"}
            )

            fig_cat.update_traces(
                marker_color="#EF4444",
                textposition="outside",
                cliponaxis=False,
                textfont=dict(color="#E5E7EB", size=12),
                hovertemplate="<b>%{y}</b>: %{text}<extra></extra>"
            )

            # Estilização limpa dos eixos e transparência para dark mode
            fig_cat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E5E7EB", family="Inter, sans-serif"),
                xaxis=dict(
                    showgrid=True,
                    gridcolor="#374151",
                    title=None,
                    range=[0, max_val * 1.25],
                    tickfont=dict(color="#9CA3AF")
                ),
                yaxis=dict(
                    showgrid=False,
                    title=None,
                    tickfont=dict(color="#E5E7EB", size=12)
                ),
                margin=dict(l=10, r=110, t=20, b=20),
                height=380
            )

            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.caption("Sem despesas no período selecionado.")

    with g2:
        st.subheader("Evolução das Movimentações por Mês")
        df["mes_ano"] = df["data"].dt.strftime("%Y-%m")
        mov_by_month = df.groupby(["mes_ano", "tipo_display"])["valor"].sum().reset_index()
        mov_by_month = mov_by_month.sort_values(by="mes_ano")
        mov_by_month["valor_str"] = mov_by_month["valor"].apply(lambda v: format_currency(v, moeda))

        color_map = {
            "Receita": "#10B981",
            "Despesa": "#EF4444",
            "RECEITA": "#10B981",
            "DESPESA": "#EF4444"
        }

        fig_evol = px.line(
            mov_by_month,
            x="mes_ano",
            y="valor",
            color="tipo_display",
            markers=True,
            color_discrete_map=color_map,
            labels={"mes_ano": "Mês", "valor": "Valor", "tipo_display": "Tipo"}
        )

        fig_evol.update_traces(
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate="<b>%{x}</b> (%{fullData.name}): %{y}<extra></extra>"
        )

        fig_evol.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E5E7EB", family="Inter, sans-serif"),
            xaxis=dict(
                type="category",
                showgrid=True,
                gridcolor="#374151",
                title=None,
                tickfont=dict(color="#E5E7EB", size=12)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#374151",
                title=None,
                tickfont=dict(color="#9CA3AF")
            ),
            legend=dict(
                title=None,
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(color="#E5E7EB")
            ),
            margin=dict(l=10, r=20, t=20, b=50),
            height=380
        )

        st.plotly_chart(fig_evol, use_container_width=True)
