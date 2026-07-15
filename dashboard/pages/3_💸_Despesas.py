import datetime
import pandas as pd
import streamlit as st
# pyrefly: ignore [missing-import]
from utils import apply_theme, check_authentication, api_request, format_currency

st.set_page_config(page_title="Despesas | FinTrack", page_icon="💸", layout="wide")
apply_theme()
check_authentication()

user = st.session_state["user"]
moeda = user.get("moeda", "BRL")

st.title("💸 Gerenciamento de Despesas")
st.caption("Cadastre e controle todos os seus gastos e custos.")

# Obter Categorias do Tipo DESPESA
success_cat, data_cat = api_request("GET", "categories/", params={"tipo": "DESPESA"})
categorias_despesa = data_cat if success_cat else []
cat_dict = {c["id"]: c["nome"] for c in categorias_despesa}

# Estados para Formulário (Cadastro/Edição)
if "edit_despesa" not in st.session_state:
    st.session_state["edit_despesa"] = None
if "show_despesa_form" not in st.session_state:
    st.session_state["show_despesa_form"] = False

# Botão para Nova Despesa
if st.button("➕ Nova Despesa"):
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

        # Seleção da Categoria
        cat_options = list(cat_dict.values())
        curr_cat_name = desp_obj.get("categoria_nome")
        cat_index = cat_options.index(curr_cat_name) if curr_cat_name in cat_options else 0
        categoria_selected = st.selectbox("Categoria", options=cat_options if cat_options else ["Sem Categorias de Despesa"], index=cat_index if cat_options else 0)

        forma_pagamento = st.selectbox("Forma de Pagamento", options=["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Boleto", "Outro"], index=0)
        observacoes = st.text_area("Observações", value=desp_obj.get("observacoes", "") or "")

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
                    "forma_pagamento": forma_pagamento,
                    "observacoes": observacoes
                }
                if is_editing:
                    success, res = api_request("PUT", f"finance/movimentacoes/{desp_obj['id']}/", payload)
                    msg_sucesso = "Despesa atualizada."
                else:
                    success, res = api_request("POST", "finance/movimentacoes/", payload)
                    msg_sucesso = "Despesa salva."

                if success:
                    st.success(msg_sucesso)
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
col_search, col_f_cat, col_f_mes, col_f_ano = st.columns([2, 1, 1, 1])
with col_search:
    search_q = st.text_input("🔍 Buscar por descrição", placeholder="Ex: Mercado")
with col_f_cat:
    f_cat = st.selectbox("Categoria", options=["Todas"] + list(cat_dict.values()))
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
if f_mes != "Todos":
    params["mes"] = f_mes
if f_ano:
    params["ano"] = f_ano

# Listagem de Despesas
success_list, data_despesas = api_request("GET", "finance/movimentacoes/", params=params)

if success_list and data_despesas:
    st.subheader(f"Total de Registros ({len(data_despesas)})")
    
    for item in data_despesas:
        c_info, c_val, c_actions = st.columns([4, 2, 2])
        with c_info:
            st.markdown(f"**{item['descricao']}**")
            st.caption(f"📅 {item['data']} | 🏷️ {item['categoria_nome']} | 💳 {item.get('forma_pagamento') or 'Não informada'} {f'| 📝 {item['observacoes']}' if item.get('observacoes') else ''}")
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
                if st.button("🗑️ Excluir", key=f"del_desp_{item['id']}"):
                    succ_del, _ = api_request("DELETE", f"finance/movimentacoes/{item['id']}/")
                    if succ_del:
                        st.success("Despesa excluída.")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir despesa.")
        st.divider()
else:
    st.info("Nenhum registro encontrado.")
