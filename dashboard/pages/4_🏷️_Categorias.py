import streamlit as st
# pyrefly: ignore [missing-import]
from utils import apply_theme, check_authentication, api_request

st.set_page_config(page_title="Categorias | FinTrack", page_icon="🏷️", layout="wide")
apply_theme()
check_authentication()

st.title("🏷️ Gerenciamento de Categorias")
st.caption("Administre suas categorias personalizadas de Receita e Despesa.")

# Estados para Formulário
if "edit_cat" not in st.session_state:
    st.session_state["edit_cat"] = None
if "show_cat_form" not in st.session_state:
    st.session_state["show_cat_form"] = False

# Botão para Nova Categoria
if st.button("➕ Nova Categoria"):
    st.session_state["edit_cat"] = None
    st.session_state["show_cat_form"] = True

# Formulário de Cadastro / Edição
if st.session_state["show_cat_form"]:
    is_editing = st.session_state["edit_cat"] is not None
    cat_obj = st.session_state["edit_cat"] or {}

    st.markdown(f"### {'Editar Categoria' if is_editing else 'Nova Categoria'}")
    with st.form("form_categoria"):
        nome_cat = st.text_input("Nome da Categoria", value=cat_obj.get("nome", ""), placeholder="Ex: Investimentos, Lazer, Educação")
        
        tipo_index = 0
        if cat_obj.get("tipo") == "DESPESA":
            tipo_index = 1
        tipo_cat = st.radio("Tipo da Categoria", options=["RECEITA", "DESPESA"], format_func=lambda x: "Receita" if x == "RECEITA" else "Despesa", index=tipo_index)
        
        curr_limite = float(cat_obj.get("limite_mensal", 0.0))
        limite_cat = st.number_input("Limite Mensal de Orçamento (R$)", min_value=0.0, value=curr_limite, step=50.0, help="Defina um teto mensal de orçamento para acompanhar no Dashboard.")

        col_save, col_cancel = st.columns(2)
        with col_save:
            btn_salvar = st.form_submit_button("Salvar Categoria", use_container_width=True)
        with col_cancel:
            btn_cancelar = st.form_submit_button("Cancelar", use_container_width=True)

        if btn_salvar:
            if not nome_cat.strip():
                st.error("O nome da categoria é obrigatório.")
            else:
                payload = {"nome": nome_cat.strip(), "tipo": tipo_cat, "limite_mensal": limite_cat}
                if is_editing:
                    success, res = api_request("PUT", f"categories/{cat_obj['id']}/", payload)
                    msg_sucesso = "Categoria atualizada."
                else:
                    success, res = api_request("POST", "categories/", payload)
                    msg_sucesso = "Categoria criada."

                if success:
                    st.success(msg_sucesso)
                    st.session_state["show_cat_form"] = False
                    st.session_state["edit_cat"] = None
                    st.rerun()
                else:
                    st.error(res.get("nome", [res.get("detail", "Erro ao salvar categoria.")])[0] if isinstance(res.get("nome"), list) else res.get("detail", "Erro ao salvar."))

        if btn_cancelar:
            st.session_state["show_cat_form"] = False
            st.session_state["edit_cat"] = None
            st.rerun()

st.divider()

# Listagem de Categorias
success, categorias = api_request("GET", "categories/")

if success and categorias:
    col_rec, col_desp = st.columns(2)

    with col_rec:
        st.subheader("🟢 Categorias de Receita")
        rec_list = [c for c in categorias if c["tipo"] == "RECEITA"]
        if rec_list:
            for item in rec_list:
                c1, c2, c3 = st.columns([4, 2, 2])
                with c1:
                    st.write(f"🏷️ **{item['nome']}**")
                    if float(item.get("limite_mensal", 0)) > 0:
                        st.caption(f"Meta/Limite: R$ {float(item['limite_mensal']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                with c2:
                    if st.button("✏️ Editar", key=f"edit_c_{item['id']}"):
                        st.session_state["edit_cat"] = item
                        st.session_state["show_cat_form"] = True
                        st.rerun()
                with c3:
                    if st.button("🗑️ Excluir", key=f"del_c_{item['id']}"):
                        succ_del, res_del = api_request("DELETE", f"categories/{item['id']}/")
                        if succ_del:
                            st.success("Categoria excluída.")
                            st.rerun()
                        else:
                            st.error(res_del.get("detail", "Erro ao excluir categoria."))
                st.divider()
        else:
            st.caption("Nenhuma categoria de receita cadastrada.")

    with col_desp:
        st.subheader("🔴 Categorias de Despesa")
        desp_list = [c for c in categorias if c["tipo"] == "DESPESA"]
        if desp_list:
            for item in desp_list:
                c1, c2, c3 = st.columns([4, 2, 2])
                with c1:
                    st.write(f"🏷️ **{item['nome']}**")
                    if float(item.get("limite_mensal", 0)) > 0:
                        st.caption(f"Orçamento Limite: R$ {float(item['limite_mensal']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                with c2:
                    if st.button("✏️ Editar", key=f"edit_c_{item['id']}"):
                        st.session_state["edit_cat"] = item
                        st.session_state["show_cat_form"] = True
                        st.rerun()
                with c3:
                    if st.button("🗑️ Excluir", key=f"del_c_{item['id']}"):
                        succ_del, res_del = api_request("DELETE", f"categories/{item['id']}/")
                        if succ_del:
                            st.success("Categoria excluída.")
                            st.rerun()
                        else:
                            st.error(res_del.get("detail", "Erro ao excluir categoria."))
                st.divider()
        else:
            st.caption("Nenhuma categoria de despesa cadastrada.")
else:
    st.info("Nenhuma categoria cadastrada.")
