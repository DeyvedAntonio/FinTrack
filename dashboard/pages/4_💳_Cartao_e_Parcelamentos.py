import streamlit as st
# pyrefly: ignore [missing-import]
from core.theme import apply_theme, format_currency
# pyrefly: ignore [missing-import]
from core.session import check_authentication
# pyrefly: ignore [missing-import]
from services.card_service import CardService
# pyrefly: ignore [missing-import]
from services.category_service import CategoryService

st.set_page_config(page_title="Cartões & Parcelamentos | FinTrack", page_icon="💳", layout="wide")
apply_theme()
check_authentication()

user = st.session_state["user"]
moeda = user.get("moeda", "BRL")

st.title("💳 Cartões de Crédito e Parcelamentos")
st.caption("Cadastre múltiplos cartões de crédito com apelidos, limite e datas de vencimento, e gerencie compras parceladas.")

# Obter Categorias e Cartões via Services
cat_options = CategoryService.get_category_dict(tipo="DESPESA")
cartoes = CardService.get_cartoes()
cartao_options = {c["id"]: c["nome_exibicao"] for c in cartoes}

tab_cartoes, tab_parcelas = st.tabs(["💳 Meus Cartões de Crédito", "📦 Compras Parceladas"])

with tab_cartoes:
    st.subheader("Gerenciador de Cartões de Crédito")
    
    with st.expander("➕ Cadastrar Novo Cartão de Crédito", expanded=False):
        with st.form("form_novo_cartao"):
            col_nc1, col_nc2 = st.columns(2)
            with col_nc1:
                apelido_nc = st.text_input("Apelido do Cartão", placeholder="Ex: Nubank, XP Infinite, Itaú Personnalité")
                ultimos_digitos_nc = st.text_input("Últimos 4 Dígitos do Cartão (Opcional)", max_chars=4, placeholder="1234")
                limite_nc = st.number_input("Limite Disponível no Cartão (R$)", min_value=0.0, step=100.0, value=5000.0)
            with col_nc2:
                fechamento_nc = st.number_input("Dia do Fechamento da Fatura (1-31)", min_value=1, max_value=31, value=5)
                vencimento_nc = st.number_input("Dia do Vencimento da Fatura (1-31)", min_value=1, max_value=31, value=12)
                meta_fatura_nc = st.number_input("Meta Mensal de Teto de Fatura (R$)", min_value=0.0, step=100.0, value=2000.0)
                reducao_nc = st.number_input("Redução Mensal Desejada (R$)", min_value=0.0, step=50.0, value=0.0)

            submit_nc = st.form_submit_button("Cadastrar Cartão", use_container_width=True)

            if submit_nc:
                if not apelido_nc.strip():
                    st.error("Por favor, informe um apelido para o cartão.")
                else:
                    payload_nc = {
                        "apelido": apelido_nc.strip(),
                        "ultimos_digitos": ultimos_digitos_nc.strip(),
                        "limite_cartao": limite_nc,
                        "dia_fechamento": fechamento_nc,
                        "dia_vencimento": vencimento_nc,
                        "meta_fatura_mensal": meta_fatura_nc,
                        "reducao_mensal_desejada": reducao_nc
                    }
                    with st.spinner("Cadastrando cartão..."):
                        succ_c, _ = CardService.save_cartao(None, payload_nc)
                        if succ_c:
                            st.success("Cartão cadastrado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Erro ao cadastrar cartão.")

    st.divider()

    if cartoes:
        for c in cartoes:
            with st.container():
                col_info1, col_info2, col_act = st.columns([4, 4, 2])
                with col_info1:
                    st.markdown(f"#### 💳 {c['nome_exibicao']}")
                    st.write(f"Limite: **{format_currency(c['limite_cartao'], moeda)}**")
                    st.write(f"Meta de Fatura: **{format_currency(c['meta_fatura_mensal'], moeda)}**")
                with col_info2:
                    st.write(f"Fechamento: **Dia {c['dia_fechamento']}**")
                    st.write(f"Vencimento: **Dia {c['dia_vencimento']}**")
                    if float(c.get('reducao_mensal_desejada', 0)) > 0:
                        st.caption(f"Meta de redução passiva: {format_currency(c['reducao_mensal_desejada'], moeda)}/mês")
                with col_act:
                    if st.button("🗑️ Excluir Cartão", key=f"del_card_{c['id']}", help="Excluir"):
                        succ_del_c, _ = CardService.delete_cartao(c["id"])
                        if succ_del_c:
                            st.success("Cartão removido.")
                            st.rerun()
                        else:
                            st.error("Erro ao remover cartão.")
            st.divider()
    else:
        st.info("Você ainda não cadastrou nenhum cartão de crédito.")

with tab_parcelas:
    st.subheader("Gerenciador de Parcelamentos Recorrentes")
    
    if not cartoes:
        st.warning("⚠️ Para cadastrar compras parceladas, você precisa ter ao menos 1 cartão de crédito cadastrado na aba 'Meus Cartões de Crédito'.")
    else:
        with st.expander("➕ Cadastrar Novo Parcelamento", expanded=False):
            with st.form("form_novo_parcelamento"):
                desc_parc = st.text_input("Descrição da Compra Parcelada", placeholder="Ex: Notebook, Celular, Viagem")
                valor_total_parc = st.number_input("Valor Total Global (R$)", min_value=0.01, step=50.0)
                num_parc = st.number_input("Número Total de Parcelas", min_value=1, max_value=72, value=12)
                data_1a = st.date_input("Data da 1ª Parcela")
                
                cat_id_parc = st.selectbox("Categoria de Despesa", options=list(cat_options.keys()), format_func=lambda x: cat_options.get(x, ""))
                cartao_id_parc = st.selectbox("Cartão de Crédito Utilizado *", options=list(cartao_options.keys()), format_func=lambda x: cartao_options.get(x, ""))

                submit_parc = st.form_submit_button("Cadastrar Parcelamento", use_container_width=True)

                if submit_parc:
                    if not desc_parc.strip():
                        st.error("Preencha a descrição do parcelamento.")
                    elif not cat_id_parc:
                        st.error("Selecione uma categoria válida.")
                    elif not cartao_id_parc:
                        st.error("Selecione um cartão de crédito obrigatório.")
                    else:
                        payload_parc = {
                            "descricao": desc_parc.strip(),
                            "valor_total": valor_total_parc,
                            "num_parcelas": num_parc,
                            "data_primeira_parcela": data_1a.strftime("%Y-%m-%d"),
                            "categoria": cat_id_parc,
                            "cartao": cartao_id_parc
                        }
                        with st.spinner("Cadastrando parcelamento..."):
                            succ_p, res_p = CardService.save_parcelamento(payload_parc)
                            if succ_p:
                                st.success("Parcelamento cadastrado com sucesso!")
                                st.rerun()
                            else:
                                err_det = res_p.get("cartao", [res_p.get("detail", "Erro ao cadastrar parcelamento.")])
                                st.error(err_det if isinstance(err_det, str) else err_det[0])

    st.divider()

    list_parcelamentos = CardService.get_parcelamentos()
    
    if list_parcelamentos:
        for p in list_parcelamentos:
            col_p1, col_p2, col_p3 = st.columns([4, 3, 2])
            with col_p1:
                st.write(f"📦 **{p['descricao']}**")
                st.caption(f"Categoria: **{p.get('categoria_nome', 'Sem categoria')}**")
                if p.get('cartao_nome'):
                    st.caption(f"Cartão: **💳 {p['cartao_nome']}**")
            with col_p2:
                st.write(f"**{p['num_parcelas']}x** de **{format_currency(p['valor_parcela'], moeda)}**")
                st.caption(f"Total: {format_currency(p['valor_total'], moeda)} | 1ª Parcela: {p['data_primeira_parcela']}")
            with col_p3:
                if st.button("🗑️ Excluir", key=f"del_parc_{p['id']}", help="Excluir"):
                    succ_del_p, _ = CardService.delete_parcelamento(p["id"])
                    if succ_del_p:
                        st.success("Parcelamento excluído.")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir parcelamento.")
            st.divider()
    else:
        st.info("Nenhum parcelamento cadastrado no momento.")
