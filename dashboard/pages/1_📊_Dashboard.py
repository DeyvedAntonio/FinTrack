import pandas as pd
import streamlit as st
from core.theme import apply_theme
from core.session import check_authentication
from services.finance_service import FinanceService
from services.category_service import CategoryService
from components.kpi_cards import render_kpi_cards
from components.charts import render_analytics_charts

st.set_page_config(page_title="Dashboard | FinTrack", page_icon="📊", layout="wide")
apply_theme()
check_authentication()

user = st.session_state["user"]
moeda = user.get("moeda", "BRL")

st.title("📊 Painel de Indicadores (Dashboard)")
st.caption("Visão geral consolidada do seu desempenho financeiro.")

# 1. Obter Categorias
cat_options = CategoryService.get_category_dict()

# 2. Área de Filtros
with st.expander("🔍 Área de Filtros Avançados", expanded=True):
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        mes_selected = st.selectbox("Mês", options=["Todos", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], index=0)
    with col_f2:
        ano_selected = st.number_input("Ano", min_value=2000, max_value=2100, value=2026)
    with col_f3:
        cat_selected = st.selectbox("Categoria", options=["Todas"] + list(cat_options.values()))
    with col_f4:
        tipo_selected = st.selectbox("Tipo de Movimentação", options=["Todos", "RECEITA", "DESPESA"])

params = {}
if mes_selected != "Todos":
    params["mes"] = mes_selected
if ano_selected:
    params["ano"] = ano_selected
if cat_selected != "Todas":
    cat_id = [k for k, v in cat_options.items() if v == cat_selected]
    if cat_id:
        params["categoria"] = cat_id[0]
if tipo_selected != "Todos":
    params["tipo"] = tipo_selected

# 3. Consulta de Movimentações via FinanceService
movimentacoes = FinanceService.get_movimentacoes(params=params)

if not movimentacoes:
    st.info("Nenhum dado encontrado para os filtros selecionados. Cadastre movimentações para visualizar os gráficos e indicadores.")
else:
    # 4. KPI Cards
    saldo_atual, total_receitas, total_despesas = FinanceService.calculate_kpis(movimentacoes)
    render_kpi_cards(saldo_atual, total_receitas, total_despesas, moeda=moeda)

    st.divider()

    # 5. Gráficos Analíticos
    render_analytics_charts(movimentacoes)

    st.divider()

    # 6. Listagens (Maiores Despesas & Últimos Lançamentos)
    df = pd.DataFrame(movimentacoes)
    df["valor"] = df["valor"].astype(float)
    
    l1, l2 = st.columns(2)
    with l1:
        st.subheader("🔥 5 Maiores Despesas")
        df_desp_top = df[df["tipo"] == "DESPESA"].sort_values(by="valor", ascending=False).head(5)
        if not df_desp_top.empty:
            st.dataframe(
                df_desp_top[["descricao", "categoria_nome", "valor", "data"]].rename(columns={
                    "descricao": "Descrição",
                    "categoria_nome": "Categoria",
                    "valor": "Valor",
                    "data": "Data"
                }),
                use_container_width=True
            )
        else:
            st.caption("Nenhuma despesa registrada.")

    with l2:
        st.subheader("🕒 Últimos Lançamentos")
        df_recent = df.sort_values(by="created_at", ascending=False).head(5)
        st.dataframe(
            df_recent[["tipo_display", "descricao", "categoria_nome", "valor", "data"]].rename(columns={
                "tipo_display": "Tipo",
                "descricao": "Descrição",
                "categoria_nome": "Categoria",
                "valor": "Valor",
                "data": "Data"
            }),
            use_container_width=True
        )

    st.divider()

    # 7. Exportação CSV
    succ_csv, csv_content = FinanceService.export_csv(params=params)
    if succ_csv:
        st.download_button(
            label="📥 Exportar lançamentos filtrados em CSV",
            data=csv_content,
            file_name="movimentacoes_fintrack.csv",
            mime="text/csv",
            use_container_width=True
        )
