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

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Score de Saúde", f"{score_color} {score}%")
with k2:
    st.metric("Receita Esperada", format_currency(resumo.get("receita_esperada", 0.0), moeda))
with k3:
    st.metric("Total de Despesas", format_currency(resumo.get("despesa_realizada", 0.0), moeda))
with k4:
    st.metric("Faturas/Parcelas no Mês", format_currency(resumo.get("compromissos_parcelas", 0.0), moeda))
with k5:
    disp = resumo.get("disponivel_livre", 0.0)
    st.metric("Disponível Livre p/ Gastar", format_currency(disp, moeda))

st.divider()

# Obter os percentuais configurados atuais
curr_pct_ess = resumo.get("pct_essenciais", 50)
curr_pct_est = resumo.get("pct_estilo_vida", 30)
curr_pct_inv = resumo.get("pct_investimentos", 20)

# As abas são SEMPRE exibidas
tab_orcamento, tab_simulador, tab_guia = st.tabs([
    f"📊 Orçamento Consciente ({curr_pct_ess}/{curr_pct_est}/{curr_pct_inv})",
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
            pct_ess = st.number_input("Essenciais (Necessidades %)", value=int(curr_pct_ess), min_value=0, max_value=100)
        with p2:
            pct_est = st.number_input("Estilo de Vida (Desejos %)", value=int(curr_pct_est), min_value=0, max_value=100)
        with p3:
            pct_inv = st.number_input("Investimentos / Futuro (%)", value=int(curr_pct_inv), min_value=0, max_value=100)

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

    pilar_ess = f"Necessidades ({curr_pct_ess}%)"
    pilar_est = f"Estilo de Vida ({curr_pct_est}%)"
    pilar_inv = f"Investimentos ({curr_pct_inv}%)"

    data_chart = [
        {"Pilar": pilar_ess, "Tipo": "Gastos Reais", "Valor (R$)": resumo.get("gastos_essenciais_realizados", 0.0)},
        {"Pilar": pilar_ess, "Tipo": "Teto Orçamentário", "Valor (R$)": resumo.get("teto_essenciais", 0.0)},
        {"Pilar": pilar_est, "Tipo": "Gastos Reais", "Valor (R$)": resumo.get("gastos_estilo_vida_realizados", 0.0)},
        {"Pilar": pilar_est, "Tipo": "Teto Orçamentário", "Valor (R$)": resumo.get("teto_estilo_vida", 0.0)},
        {"Pilar": pilar_inv, "Tipo": "Aportes Realizados", "Valor (R$)": resumo.get("investimento_realizado", 0.0)},
        {"Pilar": pilar_inv, "Tipo": "Meta de Aporte", "Valor (R$)": resumo.get("meta_investimento", 0.0)},
        {"Pilar": pilar_inv, "Tipo": "Teto Orçamentário", "Valor (R$)": resumo.get("teto_investimentos", 0.0)},
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
            "Aportes Realizados": "#059669",
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

    modo_simulacao = st.radio(
        "Modo de Simulação",
        options=["Por Valor Total da Compra", "Por Valor Direto da Parcela"],
        horizontal=True,
        help="Escolha se deseja calcular a parcela dividindo o total ou informando o valor exato da parcela mensal (com juros/taxas embutidas)."
    )

    disp_atual = resumo.get("disponivel_livre", 0.0)
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        if modo_simulacao == "Por Valor Total da Compra":
            val_compra = st.number_input("Valor Total da Nova Compra (R$)", min_value=10.0, value=1200.0, step=100.0)
            n_parc = st.number_input("Número de Parcelas Desejado (x)", min_value=1, max_value=48, value=6)
            simulacao = PlanningService.simular_nova_compra(val_compra, n_parc, disp_atual)
        else:
            val_parc_direto = st.number_input("Valor Direto da Parcela Mensal (R$)", min_value=1.0, value=10.0, step=5.0, help="Informe o valor fixo da parcela já com taxas e juros inclusos.")
            n_parc = st.number_input("Número de Parcelas Desejado (x)", min_value=1, max_value=48, value=15)
            simulacao = PlanningService.simular_nova_compra(0.0, n_parc, disp_atual, valor_parcela_direto=val_parc_direto)

    with s_col2:
        st.markdown(f"**Disponível Livre Atual no Mês**: `{format_currency(disp_atual, moeda)}`")
        
        rec_badge = "🟢" if "Saudável" in simulacao["recomendacao"] else ("🟡" if "Moderado" in simulacao["recomendacao"] else "🔴")

        if modo_simulacao == "Por Valor Direto da Parcela":
            st.write(f"• Valor Total Estimado ({n_parc}x): **{format_currency(simulacao['valor_total_calculado'], moeda)}**")
        st.write(f"• Valor da Nova Parcela Mensal: **{format_currency(simulacao['valor_parcela'], moeda)}**")
        st.write(f"• Novo Disponível Livre Estimado: **{format_currency(simulacao['novo_disponivel'], moeda)}**")
        st.write(f"• Comprometimento da Renda Livre: **{simulacao['impacto_percentual']}%**")
        st.markdown(f"### Diagnóstico: {rec_badge} **{simulacao['recomendacao']}**")

with tab_guia:
    st.subheader("💡 Diagnóstico e Recomendações de Saúde Financeira")
    st.caption("Análise preditiva e personalizada baseada nos seus números reais do mês selecionado.")

    def fmt(val):
        return format_currency(val, moeda).replace("$", "\\$")

    rec_esp = resumo.get("receita_esperada", 0.0)
    desp_ess = resumo.get("gastos_essenciais_realizados", 0.0)
    teto_ess = resumo.get("teto_essenciais", 0.0)
    pct_ess = resumo.get("pct_essenciais", 50)

    desp_est = resumo.get("gastos_estilo_vida_realizados", 0.0)
    teto_est = resumo.get("teto_estilo_vida", 0.0)
    pct_est = resumo.get("pct_estilo_vida", 30)

    inv_real = resumo.get("investimento_realizado", 0.0)
    meta_inv = resumo.get("meta_investimento", 0.0)
    teto_inv = resumo.get("teto_investimentos", 0.0)
    pct_inv = resumo.get("pct_investimentos", 20)

    fat_parc = resumo.get("compromissos_parcelas", 0.0)
    disp_livre = resumo.get("disponivel_livre", 0.0)

    # Status Geral
    if disp_livre < 0:
        st.error(f"🚨 **Alerta de Déficit no Mês**: Suas despesas e investimentos superam sua renda em **{fmt(abs(disp_livre))}**. Você precisa reduzir gastos ou ajustar suas metas temporariamente.")
    elif score >= 80:
        st.success(f"🎉 **Excelente Saúde Financeira (Score: {score}%)**: Seu orçamento está equilibrado e você possui uma margem livre de **{fmt(disp_livre)}**.")
    elif score >= 50:
        st.warning(f"⚠️ **Atenção Moderada (Score: {score}%)**: Seu orçamento possui pouca margem de segurança. Evite novos parcelamentos e monitore seus custos fixos.")
    else:
        st.error(f"🚨 **Risco Orçamentário Elevado (Score: {score}%)**: Alto comprometimento da renda. Priorize a redução de faturas e controle os gastos de estilo de vida.")

    st.divider()
    st.markdown("### 📊 Análise por Pilar do Seu Planejamento")

    g1, g2 = st.columns(2)
    with g1:
        # Pilar 1: Necessidades
        pct_usado_ess = round((desp_ess / rec_esp) * 100, 1) if rec_esp > 0 else 0
        with st.container(border=True):
            st.markdown(f"#### 🏠 Necessidades / Essenciais (`{pct_usado_ess}%` da renda)")
            if desp_ess > teto_ess:
                dif = desp_ess - teto_ess
                st.markdown(f"• **Situação**: Custos essenciais ({fmt(desp_ess)}) excederam o teto ideal de {fmt(teto_ess)} por **{fmt(dif)}**.")
                st.caption("👉 *Ação Recomendada*: Renegocie contratos fixos (internet, energia, seguros) ou reavalie compras de supermercado.")
            else:
                sobra_ess = teto_ess - desp_ess
                st.markdown(f"• **Situação**: Custos essenciais dentro do limite ({fmt(desp_ess)} de {fmt(teto_ess)}).")
                st.caption(f"👉 *Excelente*: Sobraram **{fmt(sobra_ess)}** do limite reservado para necessidades básicas.")

        # Pilar 3: Investimentos
        with st.container(border=True):
            st.markdown("#### 📈 Investimentos / Futuro")
            if meta_inv > 0:
                pct_meta_inv = round((inv_real / meta_inv) * 100, 1)
                if inv_real >= meta_inv:
                    st.markdown(f"• **Situação**: Parabéns! Você cumpriu **{pct_meta_inv}%** da sua meta de aporte ({fmt(inv_real)} de {fmt(meta_inv)}).")
                    st.caption("👉 *Ação Recomendada*: O excedente pode ser direcionado para acelerar sua reserva de emergência ou metas de longo prazo.")
                else:
                    falta_inv = meta_inv - inv_real
                    st.markdown(f"• **Situação**: Você realizou **{fmt(inv_real)}** dos {fmt(meta_inv)} estipulados (**{pct_meta_inv}%** da meta).")
                    st.caption(f"👉 *Ação Recomendada*: Faltam **{fmt(falta_inv)}** para bater a meta de investimento. Garanta esse aporte assim que a renda entrar.")
            else:
                st.markdown("• **Situação**: Nenhuma meta mensal de investimento cadastrada no formulário base.")

    with g2:
        # Pilar 2: Estilo de Vida
        pct_usado_est = round((desp_est / rec_esp) * 100, 1) if rec_esp > 0 else 0
        with st.container(border=True):
            st.markdown(f"#### 🍷 Estilo de Vida / Desejos (`{pct_usado_est}%` da renda)")
            if desp_est > teto_est:
                dif_est = desp_est - teto_est
                st.markdown(f"• **Situação**: Gastos com estilo de vida ({fmt(desp_est)}) ultrapassaram o teto ideal de {fmt(teto_est)} por **{fmt(dif_est)}**.")
                st.caption("👉 *Ação Recomendada*: Reduza idas a restaurantes, compras impulsivas ou assinaturas de streaming desnecessárias este mês.")
            elif desp_est == 0:
                st.markdown("• **Situação**: Nenhum gasto categorizado como 'Estilo de Vida' registrado ainda neste mês.")
                st.caption("👉 *Dica*: Lembre-se de atribuir o pilar 'Estilo de Vida (Desejos)' nas suas categorias na página de Categorias para acompanhar seu lazer.")
            else:
                sobra_est = teto_est - desp_est
                st.markdown(f"• **Situação**: Gastos de estilo de vida controlados ({fmt(desp_est)} de {fmt(teto_est)}).")
                st.caption(f"👉 *Margem*: Você ainda possui **{fmt(sobra_est)}** de limite para gastos com desejos e lazer neste mês.")

        # Pilar 4: Cartão & Parcelas
        pct_cartao = round((fat_parc / rec_esp) * 100, 1) if rec_esp > 0 else 0
        with st.container(border=True):
            st.markdown(f"#### 💳 Cartão de Crédito e Parcelas (`{pct_cartao}%` da renda)")
            if pct_cartao > 30:
                st.markdown(f"• **Situação**: Comprometimento alto! {fmt(fat_parc)} em cartão/parcelas consome **{pct_cartao}%** da sua renda (limite recomendado: 25%).")
                st.caption("👉 *Ação Crítica*: Não assuma novas compras parceladas. Quite antecipadamente parcelas menores para liberar margem no cartão.")
            elif pct_cartao > 0:
                st.markdown(f"• **Situação**: Comprometimento moderado ({fmt(fat_parc)} ou **{pct_cartao}%** da renda).")
                st.caption("👉 *Monitoramento*: Mantenha os parcelamentos sob controle até a liquidação completa das faturas atuais.")
            else:
                st.markdown("• **Situação**: Nenhuma parcela ou fatura pendente registrada no mês.")
                st.caption("👉 *Excelente*: Excelente controle de crédito e parcelamentos no período.")

    st.divider()
    st.markdown("### 📋 Plano de Ação Personalizado")
    
    acoes = []
    if disp_livre < 0:
        acoes.append(f"🔴 **Eliminar o Déficit**: Reavalie o teto de gastos de estilo de vida para cobrir o saldo negativo de {fmt(abs(disp_livre))}.")
    if desp_ess > teto_ess:
        acoes.append(f"🏠 **Adequar Essenciais**: Reduzir {fmt(desp_ess - teto_ess)} nas despesas fixas para voltar ao percentual de {pct_ess}%.")
    if inv_real < meta_inv and meta_inv > 0:
        acoes.append(f"📈 **Completar Aporte**: Efetuar o aporte restante de {fmt(meta_inv - inv_real)} em sua carteira de investimentos.")
    if pct_cartao > 25:
        acoes.append(f"💳 **Congelar Parcelamentos**: Evitar novas compras no cartão até que a fatura fique abaixo de 25% da renda ({fmt(rec_esp * 0.25)}).")
    if disp_livre > 0 and inv_real >= meta_inv:
        acoes.append(f"🟢 **Otimizar Excedente**: Alocar os {fmt(disp_livre)} de saldo livre em ativos de renda fixa de alta liquidez (Reserva de Emergência).")

    if acoes:
        for ac in acoes:
            st.markdown(f"- {ac}")
    else:
        st.write("✨ Seu planejamento mensal está 100% alinhado com suas metas. Continue assim!")
