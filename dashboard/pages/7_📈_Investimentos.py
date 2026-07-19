import datetime
import pandas as pd
import streamlit as st
from core.theme import apply_theme, format_currency
from core.session import check_authentication
from services.investment_service import InvestmentService

st.set_page_config(page_title="Investimentos | FinTrack", page_icon="📈", layout="wide")
apply_theme()
check_authentication()

user = st.session_state["user"]
moeda = user.get("moeda", "BRL")

st.title("📈 Carteira de Investimentos")
st.caption("Acompanhe o valor investido, preço médio ponderado, composição por classe de ativos e transações.")

# Obter resumo da carteira e ativos via Service
summary = InvestmentService.get_carteira_summary()
total_investido = summary.get("total_investido", 0.0)
posicao_ativos = summary.get("posicao_ativos", [])
alocacao_tipo = summary.get("alocacao_por_tipo", {})

ativo_dict = InvestmentService.get_ativo_dict()

tab_resumo, tab_operacao, tab_ativos_hist = st.tabs(["📊 Resumo da Carteira", "➕ Registrar Operação", "🏦 Ativos & Histórico"])

with tab_resumo:
    st.subheader("Visão Geral do Patrimônio Investido")
    
    col_k1, col_k2, col_k3 = st.columns(3)
    with col_k1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Patrimônio Investido</div>
                <div class="kpi-value neutral">{format_currency(total_investido, moeda)}</div>
            </div>
        """, unsafe_allow_html=True)
    with col_k2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Ativos em Carteira</div>
                <div class="kpi-value positive">{len(posicao_ativos)}</div>
            </div>
        """, unsafe_allow_html=True)
    with col_k3:
        top_tipo = max(alocacao_tipo, key=alocacao_tipo.get) if alocacao_tipo else "Nenhum"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Classe Dominante</div>
                <div class="kpi-value positive" style="font-size: 1.3rem;">{top_tipo}</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    if posicao_ativos:
        c_chart, c_table = st.columns([1, 2])
        
        with c_chart:
            st.subheader("Alocação por Tipo de Ativo")
            df_aloc = pd.DataFrame(list(alocacao_tipo.items()), columns=["Classe", "Total (R$)"])
            st.bar_chart(df_aloc, x="Classe", y="Total (R$)", color="#2563EB")

        with c_table:
            st.subheader("Detalhamento dos Ativos")
            df_pos = pd.DataFrame(posicao_ativos)
            df_display = df_pos[["codigo", "nome", "tipo_ativo_display", "quantidade", "preco_medio", "total_investido", "percentual_carteira"]].rename(columns={
                "codigo": "Código",
                "nome": "Ativo",
                "tipo_ativo_display": "Classe",
                "quantidade": "Qtd",
                "preco_medio": "Preço Médio",
                "total_investido": "Total (R$)",
                "percentual_carteira": "% Carteira"
            })
            st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Sua carteira de investimentos ainda está vazia. Registre ordens de compra na aba 'Registrar Operação'.")

with tab_operacao:
    st.subheader("Registrar Nova Operação (Aporte / Venda)")

    if not ativo_dict:
        st.warning("Cadastre primeiro um Ativo na aba 'Ativos & Histórico' antes de registrar uma operação.")
    else:
        with st.form("form_nova_operacao"):
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                tipo_op = st.selectbox("Tipo de Operação", options=["COMPRA", "VENDA"], format_func=lambda x: "🟢 Compra / Aporte" if x == "COMPRA" else "🔴 Venda / Resgate")
                ativo_id = st.selectbox("Selecione o Ativo", options=list(ativo_dict.keys()), format_func=lambda x: ativo_dict.get(x, ""))
                quantidade_op = st.number_input("Quantidade Negociada", min_value=0.000001, step=1.0, value=10.0, format="%.6f")
            with col_o2:
                preco_op = st.number_input("Preço Unitário (R$)", min_value=0.01, step=1.0, value=50.0)
                taxas_op = st.number_input("Taxas / Corretagem (R$)", min_value=0.0, step=0.5, value=0.0)
                data_op = st.date_input("Data da Operação", value=datetime.date.today())

            obs_op = st.text_area("Observações", placeholder="Ex: Aporte mensal, Rebalanceamento")

            submit_op = st.form_submit_button("Salvar Operação", use_container_width=True)

            if submit_op:
                if quantidade_op <= 0 or preco_op <= 0:
                    st.error("Quantidade e preço unitário devem ser maiores que zero.")
                else:
                    payload_op = {
                        "ativo": ativo_id,
                        "tipo_operacao": tipo_op,
                        "quantidade": str(quantidade_op),
                        "preco_unitario": str(preco_op),
                        "taxas": str(taxas_op),
                        "data_operacao": data_op.strftime("%Y-%m-%d"),
                        "observacoes": obs_op.strip()
                    }
                    with st.spinner("Registrando operação..."):
                        succ_op, res_op = InvestmentService.save_operacao(payload_op)
                        if succ_op:
                            st.success("Operação cadastrada com sucesso!")
                            st.rerun()
                        else:
                            st.error(res_op.get("detail", "Erro ao cadastrar operação."))

with tab_ativos_hist:
    st.subheader("Gerenciador de Ativos & Extrato de Ordens")

    with st.expander("➕ Cadastrar Novo Ativo", expanded=False):
        with st.form("form_novo_ativo"):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                codigo_at = st.text_input("Código / Ticker do Ativo", placeholder="Ex: PETR4, HGLG11, IVVB11, CDB Inter")
                nome_at = st.text_input("Nome do Ativo / Empresa", placeholder="Ex: Petrobras PN, CSHG Logística")
            with col_a2:
                tipos_map = {
                    "ACOES": "Ações (B3)",
                    "FII": "Fundos Imobiliários (FIIs)",
                    "RENDA_FIXA": "Renda Fixa (CDB, LCI, Tesouro)",
                    "ETFS": "ETFs",
                    "CRIPTO": "Criptomoedas",
                    "INTERNACIONAL": "Investimentos no Exterior"
                }
                tipo_at_key = st.selectbox("Classe do Ativo", options=list(tipos_map.keys()), format_func=lambda x: tipos_map.get(x, x))
                setor_at = st.text_input("Setor / Segmento (Opcional)", placeholder="Ex: Logística, Energia, Bancos")

            submit_at = st.form_submit_button("Cadastrar Ativo", use_container_width=True)

            if submit_at:
                if not codigo_at.strip() or not nome_at.strip():
                    st.error("Preencha o código e o nome do ativo.")
                else:
                    payload_at = {
                        "codigo": codigo_at.strip().upper(),
                        "nome": nome_at.strip(),
                        "tipo_ativo": tipo_at_key,
                        "setor": setor_at.strip()
                    }
                    with st.spinner("Cadastrando ativo..."):
                        succ_at, res_at = InvestmentService.save_ativo(payload_at)
                        if succ_at:
                            st.success("Ativo cadastrado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Erro ao cadastrar ativo.")

    st.divider()

    st.subheader("Histórico de Operações")
    operacoes = InvestmentService.get_operacoes()

    if operacoes:
        for op in operacoes:
            c_op1, c_op2, c_op3 = st.columns([4, 3, 2])
            with c_op1:
                badge_color = "🟢" if op["tipo_operacao"] == "COMPRA" else "🔴"
                st.write(f"{badge_color} **{op['tipo_operacao_display']}** - **{op['ativo_codigo']}** ({op['ativo_nome']})")
                st.caption(f"Data: {op['data_operacao']} | Classe: {op['tipo_ativo_display']} {f'| 📝 {op[\"observacoes\"]}' if op.get('observacoes') else ''}")
            with c_op2:
                st.write(f"**{op['quantidade']} x {format_currency(op['preco_unitario'], moeda)}**")
                st.caption(f"Total: {format_currency(op['valor_total_operacao'], moeda)} | Taxas: {format_currency(op['taxas'], moeda)}")
            with c_op3:
                if st.button("🗑️ Excluir", key=f"del_op_{op['id']}"):
                    succ_del_op, _ = InvestmentService.delete_operacao(op["id"])
                    if succ_del_op:
                        st.success("Operação excluída.")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir operação.")
            st.divider()
    else:
        st.info("Nenhuma operação registrada até o momento.")
