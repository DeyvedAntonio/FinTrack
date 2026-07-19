import streamlit as st
# pyrefly: ignore [missing-import]
from utils import apply_theme, check_authentication, api_request

st.set_page_config(page_title="Meu Perfil | FinTrack", page_icon="👤", layout="wide")
apply_theme()
check_authentication()

user = st.session_state["user"]

st.title("👤 Meu Perfil")
st.caption("Gerencie seus dados pessoais, preferências de exibição de moeda e credenciais de acesso.")

# 1. Foto e Informações de Cabeçalho do Perfil
col_photo, col_info = st.columns([1, 4])

with col_photo:
    if user.get("foto_perfil"):
        st.image(user["foto_perfil"], width=120)
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

# 2. Formulário de Atualização do Perfil
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
                success, data = api_request("PATCH", "auth/profile/", payload=payload, files=files)
                if success:
                    st.session_state["user"] = data["user"]
                    st.success("Perfil atualizado.")
                    st.rerun()
                else:
                    st.error(data.get("email", [data.get("detail", "Dados inválidos.")])[0] if isinstance(data.get("email"), list) else data.get("detail", "Dados inválidos."))

st.divider()

# 3. Formulário de Alteração de Senha
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
            payload_pwd = {
                "old_password": old_password,
                "new_password": new_password,
                "confirm_new_password": confirm_new_password
            }
            with st.spinner("Alterando senha..."):
                success_p, res_p = api_request("POST", "auth/change-password/", payload_pwd)
                if success_p:
                    st.session_state["token"] = res_p["token"]
                    st.success("Senha alterada.")
                else:
                    st.error(res_p.get("old_password", [res_p.get("detail", "Erro ao alterar senha.")])[0] if isinstance(res_p.get("old_password"), list) else res_p.get("detail", "Erro ao alterar senha."))

st.divider()

# 4. Exportação de Dados e Portabilidade (LGPD Art. 18, V)
st.subheader("📥 Exportação de Dados e Portabilidade (LGPD)")
st.info("""
**Direito à Portabilidade dos Dados (Art. 18, V da LGPD):**  
Você pode realizar o download completo de todos os seus dados cadastrados no FinTrack (informações de perfil, categorias e o histórico completo de movimentações financeiras) em um arquivo no formato CSV.
""")

if st.button("📦 Gerar Arquivo de Exportação CSV", use_container_width=True):
    with st.spinner("Gerando arquivo consolidado de dados..."):
        success_exp, csv_data = api_request("GET", "auth/export-csv/")
        if success_exp:
            st.download_button(
                label="⬇️ Clique aqui para baixar meus_dados_fintrack.csv",
                data=csv_data,
                file_name="meus_dados_fintrack.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.error("Erro ao gerar a exportação dos dados.")

st.divider()

# 5. Botão de Encerramento de Sessão (Logout)
if st.button("🚪 Sair da Conta", use_container_width=True):
    api_request("POST", "auth/logout/")
    st.session_state["token"] = None
    st.session_state["user"] = None
    st.success("Sessão encerrada.")
    st.rerun()

st.divider()

# 5. Zona de Atenção - LGPD e Exclusão de Perfil
st.subheader("⚠️ Zona de Atenção (LGPD & Privacidade)")

st.warning("""
**Direito de Eliminação de Dados e Retenção Legal (Art. 16, I da LGPD - Lei nº 13.709/2018):**  
Ao solicitar a exclusão da sua conta, seus dados pessoais identificáveis (nome, e-mail e foto) serão **permanentemente anonimizados** e seu acesso à plataforma será revogado imediatamente. 

Em estrito cumprimento à legislação fiscal e cível brasileira, seus registros de movimentações financeiras históricas serão mantidos de forma **anonimizada pelo prazo legal de 5 anos** para auditoria e prestação de contas, sem qualquer vinculação aos seus dados pessoais.
""")

with st.expander("🚨 Solicitar Exclusão da Conta e Anonimização de Dados", expanded=False):
    st.write("Esta ação é **irreversível**. Para prosseguir, confirme sua senha atual abaixo:")
    
    with st.form("form_excluir_conta"):
        confirm_password = st.text_input("Confirme sua Senha Atual", type="password", placeholder="Digite sua senha para confirmar")
        confirm_checkbox = st.checkbox("Estou ciente de que meus dados pessoais serão anonimizados e o acesso será encerrado permanentemente.")
        
        submit_delete = st.form_submit_button("Excluir minha conta e anonimizar dados", use_container_width=True)

        if submit_delete:
            if not confirm_password:
                st.error("Digite sua senha para confirmar a exclusão.")
            elif not confirm_checkbox:
                st.error("Marque a caixa de seleção confirmando que está ciente da irreversibilidade da ação.")
            else:
                with st.spinner("Processando anonimização e exclusão da conta..."):
                    success_d, res_d = api_request("POST", "auth/delete-account/", {"password": confirm_password})
                    if success_d:
                        st.session_state["token"] = None
                        st.session_state["user"] = None
                        st.success("Sua conta foi inativada e seus dados pessoais foram permanentemente anonimizados conforme a LGPD.")
                        st.rerun()
                    else:
                        err_msg = res_d.get("password", [res_d.get("detail", "Erro ao excluir conta.")])[0] if isinstance(res_d.get("password"), list) else res_d.get("detail", "Erro ao excluir conta.")
                        st.error(err_msg)

