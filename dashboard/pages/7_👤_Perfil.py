import streamlit as st
from core.theme import apply_theme
from core.session import check_authentication
from services.auth_service import AuthService
from components.alerts import render_lgpd_notice, render_portability_notice

st.set_page_config(page_title="Meu Perfil | FinTrack", page_icon="👤", layout="wide")
apply_theme()
check_authentication()

user = st.session_state["user"]

st.title("👤 Meu Perfil")
st.caption("Gerencie seus dados pessoais, preferências de exibição de moeda e credenciais de acesso.")

# 1. Foto e Informações de Cabeçalho do Perfil
col_photo, col_info = st.columns([2, 3])

with col_photo:
    if user.get("foto_perfil"):
        st.image(user["foto_perfil"], width=390)
    else:
        st.markdown("""
            <div style="width: 100px; height: 100px; border-radius: 50%; background-color: #2563EB; color: white; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; font-weight: bold; margin-bottom: 1rem;">
                👤
            </div>
        """, unsafe_allow_html=True)

with col_info:
    st.subheader(user.get("nome") or user.get("email"))
    st.write(f"E-mail: **{user.get('email')}**")
    st.write(f"Membro desde: **{user.get('date_joined', '')[:10]}**")

st.divider()

# 2. Formulários de Dados Pessoais e Alteração de Senha em 2 Colunas
col_dados, col_senha = st.columns(2)

with col_dados:
    st.subheader("Alterar Dados Pessoais")
    with st.form("form_perfil"):
        nome_input = st.text_input("Nome", value=user.get("nome", ""))
        email_input = st.text_input("E-mail", value=user.get("email", ""))
        
        moedas = ["BRL", "USD", "EUR"]
        curr_moeda = user.get("moeda", "BRL")
        moeda_idx = moedas.index(curr_moeda) if curr_moeda in moedas else 0
        moeda_input = st.selectbox("Moeda utilizada", options=moedas, index=moeda_idx, format_func=lambda x: "Real (R$)" if x == "BRL" else ("Dólar ($)" if x == "USD" else "Euro (€)"))
        
        foto_upload = st.file_uploader("Alterar foto de perfil (opcional)", type=["jpg", "png", "jpeg"])
        
        submit_perfil = st.form_submit_button("Salvar alterações", use_container_width=True)

        if submit_perfil:
            if not email_input:
                st.error("Dados inválidos. O e-mail não pode ficar em branco.")
            else:
                payload = {
                    "nome": nome_input,
                    "email": email_input,
                    "moeda": moeda_input
                }
                files = None
                if foto_upload:
                    files = {"foto_perfil": (foto_upload.name, foto_upload.getvalue(), foto_upload.type)}

                with st.spinner("Atualizando perfil..."):
                    success, data = AuthService.update_profile(payload=payload, files=files)
                    if success:
                        st.success("Perfil atualizado.")
                        st.rerun()
                    else:
                        st.error(data.get("email", [data.get("detail", "Dados inválidos.")])[0] if isinstance(data.get("email"), list) else data.get("detail", "Dados inválidos."))

with col_senha:
    st.subheader("Alterar Senha")
    with st.form("form_alterar_senha"):
        old_password = st.text_input("Senha Atual", type="password")
        new_password = st.text_input("Nova Senha", type="password")
        confirm_new_password = st.text_input("Confirmar Nova Senha", type="password")
        
        submit_senha = st.form_submit_button("Alterar senha", use_container_width=True)

        if submit_senha:
            if not old_password or not new_password or not confirm_new_password:
                st.error("Dados inválidos. Preencha todas as senhas.")
            elif new_password != confirm_new_password:
                st.error("A nova senha e a confirmação não coincidem.")
            else:
                with st.spinner("Alterando senha..."):
                    success_p, res_p = AuthService.change_password(old_password, new_password, confirm_new_password)
                    if success_p:
                        st.success("Senha alterada.")
                    else:
                        st.error(res_p.get("old_password", [res_p.get("detail", "Erro ao alterar senha.")])[0] if isinstance(res_p.get("old_password"), list) else res_p.get("detail", "Erro ao alterar senha."))

st.divider()

# 3. Exportação de Dados e Zona de Atenção (LGPD) em 2 Colunas
col_export, col_atencao = st.columns(2)

with col_export:
    st.subheader("📥 Exportação de Dados (LGPD)")
    render_portability_notice()

    if st.button("📦 Gerar Arquivo de Exportação CSV", use_container_width=True, key="btn_export_csv"):
        with st.spinner("Gerando arquivo consolidado de dados..."):
            success_exp, csv_data = AuthService.export_user_data_csv()
            if success_exp:
                st.download_button(
                    label="⬇️ Baixar meus_dados_fintrack.csv",
                    data=csv_data,
                    file_name="meus_dados_fintrack.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="btn_download_csv"
                )
            else:
                st.error("Erro ao gerar a exportação dos dados.")

with col_atencao:
    st.subheader("⚠️ Zona de Atenção (LGPD & Privacidade)")
    render_lgpd_notice()

    with st.expander("🚨 Solicitar Exclusão da Conta e Anonimização", expanded=False):
        st.write("Esta ação é **irreversível**. Para prosseguir, confirme sua senha atual abaixo:")
        
        with st.form("form_excluir_conta"):
            confirm_password = st.text_input("Confirme sua Senha Atual", type="password", placeholder="Digite sua senha para confirmar")
            confirm_checkbox = st.checkbox("Estou ciente de que meus dados pessoais serão anonimizados e o acesso encerrado.")
            
            submit_delete = st.form_submit_button("Excluir minha conta e anonimizar dados", use_container_width=True)

            if submit_delete:
                if not confirm_password:
                    st.error("Digite sua senha para confirmar a exclusão.")
                elif not confirm_checkbox:
                    st.error("Marque a caixa de seleção confirmando a ciência.")
                else:
                    with st.spinner("Processando anonimização e exclusão da conta..."):
                        success_d, res_d = AuthService.delete_account(confirm_password)
                        if success_d:
                            st.success("Sua conta foi inativada e seus dados anonimizados.")
                            st.rerun()
                        else:
                            err_msg = res_d.get("password", [res_d.get("detail", "Erro ao excluir conta.")])[0] if isinstance(res_d.get("password"), list) else res_d.get("detail", "Erro ao excluir conta.")
                            st.error(err_msg)

st.divider()

# 4. Botão de Encerramento de Sessão (Logout)
_, col_logout_center, _ = st.columns([3, 2, 3])
with col_logout_center:
    if st.button("🚪 Sair da Conta", use_container_width=True, key="btn_logout"):
        AuthService.logout()
        st.success("Sessão encerrada.")
        st.rerun()
