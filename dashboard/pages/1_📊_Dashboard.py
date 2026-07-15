import pandas as pd
import streamlit as st
# pyrefly: ignore [missing-import]
from utils import apply_theme, check_authentication, api_request, format_currency

st.set_page_config(page_title="Dashboard | FinTrack", page_icon="📊", layout="wide")
apply_theme()
check_authentication()

user = st.session_state["user"]
moeda = user.get("moeda", "BRL")

st.title("📊 Painel de Indicadores (Dashboard)")
st.caption("Visão geral consolidada do seu desempenho financeiro.")

# 1. Obter Categorias para os Filtros
success_cat, data_cat = api_request("GET", "categories/")
categorias_list = data_cat if success_cat else []
cat_options = {c["id"]: c["nome"] for c in categorias_list}

# 2. Área de Filtros Persistentes
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

    col_btn_f1, col_btn_f2 = st.columns([1, 5])
    with col_btn_f1:
        aplicar_filtros = st.button("Aplicar filtros", use_container_width=True)

# Montar Parâmetros da Requisição da API
params = {}
if mes_selected != "Todos":
    params["mes"] = mes_selected
if ano_selected:
    params["ano"] = ano_selected
if cat_selected != "Todas":
    # encontrar id da categoria
    cat_id = [k for k, v in cat_options.items() if v == cat_selected]
    if cat_id:
        params["categoria"] = cat_id[0]
if tipo_selected != "Todos":
    params["tipo"] = tipo_selected

# 3. Requisição de Dados das Movimentações
success_mov, data_mov = api_request("GET", "finance/movimentacoes/", params=params)

if not success_mov:
    st.error("Erro ao carregar os dados financeiros.")
    st.stop()

movimentacoes = data_mov if isinstance(data_mov, list) else []

if not movimentacoes:
    st.info("Nenhum dado encontrado para os filtros selecionados. Cadastre movimentações para visualizar os gráficos e indicadores.")
else:
    df = pd.DataFrame(movimentacoes)
    df["valor"] = df["valor"].astype(float)
    df["data"] = pd.to_datetime(df["data"])

    # 4. Cálculo dos Cards de KPIs
    total_receitas = df[df["tipo"] == "RECEITA"]["valor"].sum()
    total_despesas = df[df["tipo"] == "DESPESA"]["valor"].sum()
    saldo_atual = total_receitas - total_despesas

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Saldo Atual</div>
                <div class="kpi-value {'positive' if saldo_atual >= 0 else 'negative'}">{format_currency(saldo_atual, moeda)}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total de Receitas</div>
                <div class="kpi-value positive">{format_currency(total_receitas, moeda)}</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total de Despesas</div>
                <div class="kpi-value negative">{format_currency(total_despesas, moeda)}</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 5. Gráficos Analíticos do PRD
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

    st.divider()

    # 6. Listas Recomendadas do PRD
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

    # 7. Botão Exportar CSV do Dashboard
    if st.button("📥 Exportar todos os lançamentos filtrados em CSV"):
        success_csv, csv_content = api_request("GET", "finance/movimentacoes/export-csv/", params=params)
        if success_csv:
            st.download_button(
                label="Clique para baixar movimentacoes.csv",
                data=csv_content,
                file_name="movimentacoes_fintrack.csv",
                mime="text/csv"
            )
        else:
            st.error("Erro ao gerar arquivo CSV.")
