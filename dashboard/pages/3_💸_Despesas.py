import datetime
import pandas as pd
import streamlit as st
from core.theme import apply_theme, format_currency
from core.session import check_authentication
from services.finance_service import FinanceService
from services.category_service import CategoryService
from services.card_service import CardService

from components.kpi_cards import render_single_kpi_card

st.set_page_config(page_title="Despesas | FinTrack", page_icon="💸", layout="wide")
apply_theme()
check_authentication()

user = st.session_state["user"]
moeda = user.get("moeda", "BRL")

# Cabeçalho com Titulo e Card de Total de Despesas
col_header, col_kpi = st.columns([3, 1])
with col_header:
    st.title("💸 Gerenciamento de Despesas")
    st.caption("Cadastre e controle todos os seus gastos e custos.")
kpi_container = col_kpi.container()

# Obter Categorias e Cartões via Services
cat_dict = CategoryService.get_category_dict(tipo="DESPESA")
cartao_dict = CardService.get_cartao_dict()

# Estados para Formulário (Cadastro/Edição)
if "edit_despesa" not in st.session_state:
    st.session_state["edit_despesa"] = None
if "show_despesa_form" not in st.session_state:
    st.session_state["show_despesa_form"] = False

# Botão para Nova Despesa
with col_header:
    if st.button("➕ Nova Despesa", key="nova_despesa", help="Nova Despesa"):
        st.session_state["edit_despesa"] = None
        st.session_state["show_despesa_form"] = True

# Formulário de Cadastro / Edição
if st.session_state["show_despesa_form"]:
    is_editing = st.session_state["edit_despesa"] is not None
    desp_obj = st.session_state["edit_despesa"] or {}
    
    st.markdown(f"### {'Editar Despesa' if is_editing else 'Nova Despesa'}")
    with st.form("form_despesa"):
        descricao = st.text_input("Descrição", value=desp_obj.get("descricao", ""), placeholder="Ex: Mercado, Aluguel, Farmácia")
        valor = st.number_input("Valor", min_value=0.01, step=5.0, value=float(desp_obj.get("valor", 50.0)))
        
        data_val = datetime.date.today()
        if desp_obj.get("data"):
            try:
                data_val = datetime.datetime.strptime(desp_obj["data"], "%Y-%m-%d").date()
            except Exception:
                pass
        data_desp = st.date_input("Data", value=data_val)

        cat_options = list(cat_dict.values())
        curr_cat_name = desp_obj.get("categoria_nome")
        cat_index = cat_options.index(curr_cat_name) if curr_cat_name in cat_options else 0
        categoria_selected = st.selectbox("Categoria", options=cat_options if cat_options else ["Sem Categorias de Despesa"], index=cat_index if cat_options else 0)

        forma_options = {
            "CREDITO_1X": "Crédito À Vista",
            "DEBITO": "Débito",
            "PIX_TRANSFERENCIA": "PIX / Transferência",
            "DINHEIRO": "Dinheiro",
            "BOLETO": "Boleto"
        }
        curr_fp = desp_obj.get("forma_pagamento", "DEBITO")
        fp_keys = list(forma_options.keys())
        fp_idx = fp_keys.index(curr_fp) if curr_fp in fp_keys else 1
        
        forma_pagamento_key = st.selectbox("Forma de Pagamento", options=fp_keys, format_func=lambda x: forma_options.get(x, x), index=fp_idx)

        cartao_id_selected = None
        if cartao_dict:
            c_keys = [None] + list(cartao_dict.keys())
            curr_c_id = desp_obj.get("cartao")
            c_idx = c_keys.index(curr_c_id) if curr_c_id in c_keys else 0
            cartao_id_selected = st.selectbox("Cartão de Crédito (Opcional)", options=c_keys, format_func=lambda x: "Nenhum" if x is None else cartao_dict.get(x, ""), index=c_idx)

        observacoes = st.text_area("Observações", value=desp_obj.get("observacoes", "") or "")

        is_recorrente = st.checkbox("É uma despesa recorrente?", value=desp_obj.get("is_recorrente", False))
        data_fim_rec = None
        if is_recorrente:
            d_fim_val = None
            if desp_obj.get("data_fim_recorrencia"):
                try:
                    d_fim_val = datetime.datetime.strptime(desp_obj["data_fim_recorrencia"], "%Y-%m-%d").date()
                except Exception:
                    pass
            use_fim = st.checkbox("Definir Data Limite Final da Recorrência?", value=d_fim_val is not None)
            if use_fim:
                data_fim_rec = st.date_input("Data Final da Recorrência", value=d_fim_val or data_desp)

        col_save, col_cancel = st.columns(2)
        with col_save:
            btn_salvar = st.form_submit_button("Salvar Despesa", use_container_width=True)
        with col_cancel:
            btn_cancelar = st.form_submit_button("Cancelar", use_container_width=True)

        if btn_salvar:
            cat_id = [k for k, v in cat_dict.items() if v == categoria_selected]
            if not cat_id:
                st.error("Por favor, selecione uma categoria válida de despesa.")
            elif not descricao or valor <= 0:
                st.error("Valor deve ser maior que zero.")
            else:
                payload = {
                    "descricao": descricao,
                    "valor": str(valor),
                    "tipo": "DESPESA",
                    "data": str(data_desp),
                    "categoria": cat_id[0],
                    "forma_pagamento": forma_pagamento_key,
                    "cartao": cartao_id_selected,
                    "observacoes": observacoes,
                    "is_recorrente": is_recorrente,
                    "frequencia_recorrencia": "MENSAL",
                    "data_fim_recorrencia": str(data_fim_rec) if is_recorrente and data_fim_rec else None
                }
                success, res = FinanceService.save_movimentacao(desp_obj.get("id"), payload)
                if success:
                    st.success("Despesa salva com sucesso.")
                    st.session_state["show_despesa_form"] = False
                    st.session_state["edit_despesa"] = None
                    st.rerun()
                else:
                    st.error(res.get("detail") or str(res))

        if btn_cancelar:
            st.session_state["show_despesa_form"] = False
            st.session_state["edit_despesa"] = None
            st.rerun()

st.divider()

# Barra de Pesquisa e Filtros
col_search, col_f_cat, col_f_cart, col_f_mes, col_f_ano = st.columns([2, 1, 1, 1, 1])
with col_search:
    search_q = st.text_input("🔍 Buscar por descrição", placeholder="Ex: Mercado")
with col_f_cat:
    f_cat = st.selectbox("Categoria", options=["Todas"] + list(cat_dict.values()))
with col_f_cart:
    f_cartao_name = st.selectbox("Cartão", options=["Todos"] + list(cartao_dict.values()))
with col_f_mes:
    f_mes = st.selectbox("Mês", options=["Todos", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
with col_f_ano:
    f_ano = st.number_input("Ano", min_value=2000, max_value=2100, value=2026)

params = {"tipo": "DESPESA"}
if search_q:
    params["search"] = search_q
if f_cat != "Todas":
    cat_id_filt = [k for k, v in cat_dict.items() if v == f_cat]
    if cat_id_filt:
        params["categoria"] = cat_id_filt[0]
if f_cartao_name != "Todos":
    c_id_filt = [k for k, v in cartao_dict.items() if v == f_cartao_name]
    if c_id_filt:
        params["cartao"] = c_id_filt[0]
if f_mes != "Todos":
    params["mes"] = f_mes
if f_ano:
    params["ano"] = f_ano

data_despesas = FinanceService.get_movimentacoes(params=params)
total_despesas_valor = sum(float(item["valor"]) for item in data_despesas) if data_despesas else 0.0

# Renderizar KPI Card no canto superior direito
with kpi_container:
    render_single_kpi_card("Total de Despesas", total_despesas_valor, value_type="negative", moeda=moeda)

if data_despesas:
    st.subheader(f"Total de Registros ({len(data_despesas)})")
    
    for item in data_despesas:
        c_info, c_val, c_actions = st.columns([4, 2, 2])
        with c_info:
            cartao_str = f" | 💳 {item['cartao_nome']}" if item.get('cartao_nome') else ""
            obs_str = f" | 📝 {item['observacoes']}" if item.get('observacoes') else ""
            rec_tag = " | 🔁 Recorrente" if item.get('is_recorrente') else ""
            st.markdown(f"**{item['descricao']}**")
            st.caption(f"📅 {item['data']} | 🏷️ {item['categoria_nome']}{rec_tag} | 💵 {item.get('forma_pagamento_display') or 'Não informada'}{cartao_str}{obs_str}")
        with c_val:
            st.markdown(f"<span style='color: #EF4444; font-weight: bold; font-size: 1.2rem;'>- {format_currency(item['valor'], moeda)}</span>", unsafe_allow_html=True)
        with c_actions:
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button("✏️ Editar", key=f"edit_desp_{item['id']}"):
                    st.session_state["edit_despesa"] = item
                    st.session_state["show_despesa_form"] = True
                    st.rerun()
            with col_act2:
                if st.button("🗑️ Excluir", key=f"del_desp_{item['id']}", help="Excluir"):
                    succ_del, _ = FinanceService.delete_movimentacao(item["id"])
                    if succ_del:
                        st.success("Despesa excluída.")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir despesa.")
        st.divider()
else:
    st.info("Nenhum registro encontrado.")
