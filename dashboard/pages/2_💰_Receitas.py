import datetime
import pandas as pd
import streamlit as st
from core.theme import apply_theme, format_currency
from core.session import check_authentication
from services.finance_service import FinanceService
from services.category_service import CategoryService

st.set_page_config(page_title="Receitas | FinTrack", page_icon="💰", layout="wide")
apply_theme()
check_authentication()

user = st.session_state["user"]
moeda = user.get("moeda", "BRL")

st.title("💰 Gerenciamento de Receitas")
st.caption("Cadastre e acompanhe todas as suas entradas financeiras.")

# Obter Categorias do Tipo RECEITA
cat_dict = CategoryService.get_category_dict(tipo="RECEITA")

# Estados para Formulário (Cadastro/Edição)
if "edit_receita" not in st.session_state:
    st.session_state["edit_receita"] = None
if "show_receita_form" not in st.session_state:
    st.session_state["show_receita_form"] = False

# Botão para Nova Receita
if st.button("➕ Nova Receita"):
    st.session_state["edit_receita"] = None
    st.session_state["show_receita_form"] = True

# Formulário de Cadastro / Edição
if st.session_state["show_receita_form"]:
    is_editing = st.session_state["edit_receita"] is not None
    rec_obj = st.session_state["edit_receita"] or {}
    
    st.markdown(f"### {'Editar Receita' if is_editing else 'Nova Receita'}")
    with st.form("form_receita"):
        descricao = st.text_input("Descrição", value=rec_obj.get("descricao", ""), placeholder="Ex: Salário, Freelance")
        valor = st.number_input("Valor", min_value=0.01, step=10.0, value=float(rec_obj.get("valor", 100.0)))
        
        data_val = datetime.date.today()
        if rec_obj.get("data"):
            try:
                data_val = datetime.datetime.strptime(rec_obj["data"], "%Y-%m-%d").date()
            except Exception:
                pass
        data_rec = st.date_input("Data", value=data_val)

        cat_options = list(cat_dict.values())
        curr_cat_name = rec_obj.get("categoria_nome")
        cat_index = cat_options.index(curr_cat_name) if curr_cat_name in cat_options else 0
        categoria_selected = st.selectbox("Categoria", options=cat_options if cat_options else ["Sem Categorias de Receita"], index=cat_index if cat_options else 0)

        observacoes = st.text_area("Observações", value=rec_obj.get("observacoes", "") or "")

        col_save, col_cancel = st.columns(2)
        with col_save:
            btn_salvar = st.form_submit_button("Salvar Receita", use_container_width=True)
        with col_cancel:
            btn_cancelar = st.form_submit_button("Cancelar", use_container_width=True)

        if btn_salvar:
            cat_id = [k for k, v in cat_dict.items() if v == categoria_selected]
            if not cat_id:
                st.error("Por favor, selecione uma categoria válida de receita.")
            elif not descricao or valor <= 0:
                st.error("Valor inválido. A descrição é obrigatória e o valor deve ser maior que zero.")
            else:
                payload = {
                    "descricao": descricao,
                    "valor": str(valor),
                    "tipo": "RECEITA",
                    "data": str(data_rec),
                    "categoria": cat_id[0],
                    "observacoes": observacoes
                }
                success, res = FinanceService.save_movimentacao(rec_obj.get("id"), payload)
                if success:
                    st.success("Receita salva com sucesso.")
                    st.session_state["show_receita_form"] = False
                    st.session_state["edit_receita"] = None
                    st.rerun()
                else:
                    st.error(res.get("detail") or str(res))

        if btn_cancelar:
            st.session_state["show_receita_form"] = False
            st.session_state["edit_receita"] = None
            st.rerun()

st.divider()

# Barra de Pesquisa e Filtros
col_search, col_f_cat, col_f_mes, col_f_ano = st.columns([2, 1, 1, 1])
with col_search:
    search_q = st.text_input("🔍 Buscar por descrição", placeholder="Ex: Salário")
with col_f_cat:
    f_cat = st.selectbox("Categoria", options=["Todas"] + list(cat_dict.values()))
with col_f_mes:
    f_mes = st.selectbox("Mês", options=["Todos", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
with col_f_ano:
    f_ano = st.number_input("Ano", min_value=2000, max_value=2100, value=2026)

params = {"tipo": "RECEITA"}
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

data_receitas = FinanceService.get_movimentacoes(params=params)

if data_receitas:
    st.subheader(f"Total de Registros ({len(data_receitas)})")
    
    for item in data_receitas:
        c_info, c_val, c_actions = st.columns([4, 2, 2])
        with c_info:
            st.markdown(f"**{item['descricao']}**")
            st.caption(f"📅 {item['data']} | 🏷️ {item['categoria_nome']} {f'| 📝 {item[\"observacoes\"]}' if item.get('observacoes') else ''}")
        with c_val:
            st.markdown(f"<span style='color: #10B981; font-weight: bold; font-size: 1.2rem;'>+ {format_currency(item['valor'], moeda)}</span>", unsafe_allow_html=True)
        with c_actions:
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button("✏️ Editar", key=f"edit_rec_{item['id']}"):
                    st.session_state["edit_receita"] = item
                    st.session_state["show_receita_form"] = True
                    st.rerun()
            with col_act2:
                if st.button("🗑️ Excluir", key=f"del_rec_{item['id']}"):
                    succ_del, _ = FinanceService.delete_movimentacao(item["id"])
                    if succ_del:
                        st.success("Receita excluída.")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir receita.")
        st.divider()
else:
    st.info("Nenhum registro encontrado.")
