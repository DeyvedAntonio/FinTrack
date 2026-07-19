import datetime
import streamlit as st
import pandas as pd
import plotly.express as px

from core.theme import apply_theme, format_currency
from core.session import init_session
from services.planning_service import PlanningService

st.set_page_config(
    page_title="FinTrack - Planejamento Consciente",
    page_icon="🎯",
    layout="wide"
)

apply_theme()
init_session()

if not st.session_state["token"]:
    st.warning("Por favor, faça login na página inicial para acessar o Planejamento Financeiro.")
    st.stop()

user = st.session_state["user"]
moeda = user.get("moeda", "BRL")

st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 2.2rem; font-weight: 800; margin: 0; color: #F9FAFB;">
            🎯 Planejamento Financeiro Consciente
        </h1>
        <p style="color: #94A3B8; margin-top: 0.25rem;">
            Equilíbrio orçamentário (Regra 50/30/20), cálculo do Disponível Livre e simulador inteligente de novos parcelamentos.
        </p>
    </div>
""", unsafe_allow_html=True)

# Seletor de Mês
hoje = datetime.date.today()
meses_opts = [(hoje.replace(day=1) - datetime.timedelta(days=30*i)).strftime("%Y-%m") for i in range(6)]
mes_sel = st.selectbox("📅 Selecione o Mês de Referência para Análise", options=meses_opts, index=0)

resumo = PlanningService.get_resumo_planejamento(mes_sel) or {}

score = resumo.get("score_saude", 100)
score_color = "🟢" if score >= 70 else ("🟡" if score >= 50 else "🔴")

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Score de Saúde", f"{score_color} {score}%")
with k2:
    st.metric("Receita Esperada", format_currency(resumo.get("receita_esperada", 0.0), moeda))
with k3:
    st.metric("Faturas/Parcelas no Mês", format_currency(resumo.get("compromissos_parcelas", 0.0), moeda))
with k4:
    disp = resumo.get("disponivel_livre", 0.0)
    st.metric("Disponível Livre p/ Gastar", format_currency(disp, moeda))

st.divider()

# As abas são SEMPRE exibidas
tab_orcamento, tab_simulador, tab_guia = st.tabs([
    "📊 Orçamento Consciente (50/30/20)",
    "🛍️ Simulador de Novas Compras",
    "💡 Dicas de Saúde Financeira"
])

with tab_orcamento:
    st.subheader("Configuração do Planejamento Financeiro Base")
    st.caption("ℹ️ Defina abaixo sua Renda Esperada e alocação orçamentária. As configurações serão aplicadas automaticamente para todos os meses até que você decida modificá-las.")
    
    with st.form("form_planejamento"):
        c_rec, c_inv = st.columns(2)
        with c_rec:
            rec_esp = st.number_input("Receita Mensal Esperada (R$)", value=float(resumo.get("receita_esperada", 0.0)), min_value=0.0, step=100.0)
        with c_inv:
            meta_inv = st.number_input("Meta de Aporte em Investimentos (R$)", value=float(resumo.get("meta_investimento", 0.0)), min_value=0.0, step=50.0)

        st.write("**Metodologia de Alocação de Gastos (%)**")
        p1, p2, p3 = st.columns(3)
        with p1:
            pct_ess = st.number_input("Essenciais (Necessidades %)", value=int(resumo.get("pct_essenciais", 50)), min_value=0, max_value=100)
        with p2:
            pct_est = st.number_input("Estilo de Vida (Desejos %)", value=int(resumo.get("pct_estilo_vida", 30)), min_value=0, max_value=100)
        with p3:
            pct_inv = st.number_input("Investimentos / Futuro (%)", value=int(resumo.get("pct_investimentos", 20)), min_value=0, max_value=100)

        btn_save_plan = st.form_submit_button("Salvar Planejamento Base", use_container_width=True)

        if btn_save_plan:
            if (pct_ess + pct_est + pct_inv) != 100:
                st.error("A soma dos percentuais (Essenciais + Estilo de Vida + Investimentos) deve ser igual a 100%.")
            else:
                payload_plan = {
                    "mes_referencia": f"{mes_sel}-01",
                    "receita_esperada": rec_esp,
                    "meta_investimento_mensal": meta_inv,
                    "alocacao_essenciais_pct": pct_ess,
                    "alocacao_estilo_vida_pct": pct_est,
                    "alocacao_investimentos_pct": pct_inv
                }
                succ_plan, _ = PlanningService.save_planejamento(payload_plan)
                if succ_plan:
                    st.success("Planejamento base atualizado com sucesso! Ele agora é válido para seus próximos meses.")
                    st.rerun()
                else:
                    st.error("Erro ao salvar planejamento.")

    st.divider()
    st.subheader("Comparativo Orçamentário: Teto Ideal vs Realizado")

    data_chart = [
        {"Pilar": "Necessidades (50%)", "Tipo": "Gastos Reais", "Valor (R$)": resumo.get("despesa_realizada", 0.0)},
        {"Pilar": "Necessidades (50%)", "Tipo": "Teto Orçamentário", "Valor (R$)": resumo.get("teto_essenciais", 0.0)},
        {"Pilar": "Investimentos (20%)", "Tipo": "Meta de Aporte", "Valor (R$)": resumo.get("meta_investimento", 0.0)},
        {"Pilar": "Investimentos (20%)", "Tipo": "Teto Orçamentário", "Valor (R$)": resumo.get("teto_investimentos", 0.0)},
        {"Pilar": "Cartões & Parcelas", "Tipo": "Compromisso Mensal", "Valor (R$)": resumo.get("compromissos_parcelas", 0.0)},
    ]
    df_chart = pd.DataFrame(data_chart)
    
    fig_plan = px.bar(
        df_chart,
        x="Pilar",
        y="Valor (R$)",
        color="Tipo",
        barmode="group",
        text_auto=".2f",
        color_discrete_map={
            "Gastos Reais": "#EF4444",
            "Teto Orçamentário": "#3B82F6",
            "Meta de Aporte": "#10B981",
            "Compromisso Mensal": "#F59E0B"
        }
    )
    fig_plan.update_layout(
        xaxis_title="Pilar Orçamentário",
        yaxis_title="Valor (R$)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_plan, use_container_width=True)

with tab_simulador:
    st.subheader("Simulador Inteligente de Impacto de Compras")
    st.write("Antes de assumir um novo parcelamento no cartão de crédito, simule o impacto na sua renda disponível mensal dos próximos meses.")

    s_col1, s_col2 = st.columns(2)
    with s_col1:
        val_compra = st.number_input("Valor Total da Nova Compra (R$)", min_value=10.0, value=1200.0, step=100.0)
        n_parc = st.number_input("Número de Parcelas Desejado (x)", min_value=1, max_value=48, value=6)

    with s_col2:
        disp_atual = resumo.get("disponivel_livre", 0.0)
        st.markdown(f"**Disponível Livre Atual no Mês**: `{format_currency(disp_atual, moeda)}`")
        
        simulacao = PlanningService.simular_nova_compra(val_compra, n_parc, disp_atual)
        
        rec_badge = "🟢" if "Saudável" in simulacao["recomendacao"] else ("🟡" if "Moderado" in simulacao["recomendacao"] else "🔴")

        st.write(f"• Valor da Nova Parcela Mensal: **{format_currency(simulacao['valor_parcela'], moeda)}**")
        st.write(f"• Novo Disponível Livre Estimado: **{format_currency(simulacao['novo_disponivel'], moeda)}**")
        st.write(f"• Comprometimento da Renda Livre: **{simulacao['impacto_percentual']}%**")
        st.markdown(f"### Diagnóstico: {rec_badge} **{simulacao['recomendacao']}**")

with tab_guia:
    st.subheader("💡 Recomendações de Educação Financeira Consciente")
    
    if score >= 80:
        st.success("🎉 **Excelente gestão financeira!** Seu nível de parcelamento está sob controle e seu orçamento mantém margem de segurança saudável.")
    elif score >= 50:
        st.warning("⚠️ **Atenção moderada:** Fique atento ao acúmulo de parcelas futuras. Evite novos parcelamentos até reduzir a fatura atual.")
    else:
        st.error("🚨 **Alerta de Estresse Financeiro!** Suas despesas e compromissos com cartão superam o limite seguro da sua renda. Evite compras não essenciais.")

    st.markdown("""
    #### 📌 Regra de Ouro do Planejamento Consciente:
    1. **Pague a si mesmo primeiro**: Separe o valor da sua meta de investimento assim que a receita entrar.
    2. **Limite de Parcelados**: O valor total das faturas e parcelas acumuladas não deve ultrapassar **25%** da sua renda mensal.
    3. **Reserva para Imprevistos**: Mantenha pelo menos o equivalente a 3 a 6 meses de despesas essenciais em aplicações de liquidez diária.
    """)
