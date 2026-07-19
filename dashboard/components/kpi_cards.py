import streamlit as st
from core.theme import format_currency


def render_kpi_cards(saldo_atual, total_receitas, total_despesas, moeda="BRL"):
    """Renderiza a grade de KPI Cards padronizada no Dashboard."""
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


def render_single_kpi_card(title, value, value_type="negative", moeda="BRL"):
    """Renderiza um único KPI Card (ex: no topo superior direito de telas de gerenciamento)."""
    val_str = format_currency(value, moeda) if isinstance(value, (int, float)) else str(value)
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value {value_type}">{val_str}</div>
        </div>
    """, unsafe_allow_html=True)
