import streamlit as st
# pyrefly: ignore [missing-import]
from utils import apply_theme, api_request

# Configuração da Página
st.set_page_config(
    page_title="FinTrack - Gestão Financeira Pessoal",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar Tema Visual e Paleta de Cores do FinTrack
apply_theme()

# Inicialização de estados da sessão
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"  # 'login', 'register', 'reset'

# Cabeçalho do App com Logo e Tipografia do PRD
st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0 2rem 0;">
        <h1 style="font-size: 3rem; font-weight: 900; margin: 0; color: #1F2937; letter-spacing: -1px;">
            <span style="color: #2563EB;">Fin</span>Track
        </h1>
        <p style="font-size: 1.1rem; color: #64748B; margin-top: 0.25rem;">
            Sistema Inteligente de Gestão Financeira Pessoal
        </p>
    </div>
""", unsafe_allow_html=True)

# Se não estiver autenticado, exibe o painel de Autenticação (Login / Cadastro)
if not st.session_state["token"]:
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        # Modo: LOGIN
        if st.session_state["auth_mode"] == "login":
            st.subheader("Entrar")
            st.caption("Acesse sua conta para gerenciar suas finanças.")

            with st.form("form_login"):
                email = st.text_input("E-mail", placeholder="seuemail@exemplo.com")
                password = st.text_input("Senha", type="password", placeholder="Sua senha")
                submit_login = st.form_submit_button("Entrar", use_container_width=True)

                if submit_login:
                    if not email or not password:
                        st.error("Por favor, preencha todos os campos.")
                    else:
                        with st.spinner("Entrando..."):
                            success, data = api_request("POST", "auth/login/", {"email": email, "password": password})
                            if success:
                                st.session_state["token"] = data["token"]
                                st.session_state["user"] = data["user"]
                                st.success("Login realizado com sucesso!")
                                st.rerun()
                            else:
                                err_msg = data.get("non_field_errors", [data.get("detail", "E-mail ou senha inválidos.")])[0]
                                st.error(err_msg)

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Criar conta", use_container_width=True):
                    st.session_state["auth_mode"] = "register"
                    st.rerun()
            with col_btn2:
                if st.button("Esqueci minha senha", use_container_width=True):
                    st.session_state["auth_mode"] = "reset"
                    st.rerun()

        # Modo: CADASTRO
        elif st.session_state["auth_mode"] == "register":
            st.subheader("Criar Conta")
            st.caption("Cadastre-se gratuitamente no FinTrack.")

            with st.form("form_register"):
                nome = st.text_input("Nome Completo", placeholder="Seu nome completo")
                email = st.text_input("E-mail", placeholder="seuemail@exemplo.com")
                password = st.text_input("Senha", type="password", placeholder="Sua senha segura")
                confirm_password = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha")
                submit_reg = st.form_submit_button("Cadastrar", use_container_width=True)

                if submit_reg:
                    if not nome or not email or not password or not confirm_password:
                        st.error("Preencha todos os campos do formulário.")
                    elif password != confirm_password:
                        st.error("Senhas diferentes. Verifique a senha digitada.")
                    else:
                        with st.spinner("Cadastrando sua conta..."):
                            payload = {
                                "nome": nome,
                                "email": email,
                                "password": password,
                                "confirm_password": confirm_password
                            }
                            success, data = api_request("POST", "auth/register/", payload)
                            if success:
                                st.session_state["token"] = data["token"]
                                st.session_state["user"] = data["user"]
                                st.success("Cadastro realizado com sucesso!")
                                st.rerun()
                            else:
                                err = data.get("email", [data.get("detail", "Erro ao cadastrar.")])[0]
                                st.error(err)

            if st.button("Já possui conta? Entrar", use_container_width=True):
                st.session_state["auth_mode"] = "login"
                st.rerun()

        # Modo: RECUPERAÇÃO DE SENHA
        elif st.session_state["auth_mode"] == "reset":
            st.subheader("Recuperar Senha")
            st.caption("Informe seu e-mail para receber as instruções.")

            with st.form("form_reset"):
                email = st.text_input("E-mail Cadastrado", placeholder="seuemail@exemplo.com")
                submit_reset = st.form_submit_button("Enviar link", use_container_width=True)

                if submit_reset:
                    if not email:
                        st.error("Informe seu e-mail.")
                    else:
                        with st.spinner("Enviando solicitação..."):
                            success, data = api_request("POST", "auth/password-reset/", {"email": email})
                            if success:
                                st.info("Link enviado. Se o e-mail estiver cadastrado, você receberá o link em breve.")
                            else:
                                st.error("Erro ao solicitar redefinição de senha.")

            if st.button("Voltar para o Login", use_container_width=True):
                st.session_state["auth_mode"] = "login"
                st.rerun()

# Se estiver AUTENTICADO
else:
    user = st.session_state["user"]
    nome_usuario = user.get("nome") or user.get("email")
    moeda = user.get("moeda", "BRL")

    # Renderizar Menu Lateral Persistente
    with st.sidebar:
        st.markdown(f"### Olá, **{nome_usuario}**!")
        st.caption(f"Moeda Padrão: **{moeda}**")
        st.divider()
        st.info("Navegue pelas páginas do menu acima para visualizar o Dashboard, Gerenciar Receitas, Despesas, Categorias ou seu Perfil.")
        
        st.divider()
        if st.button("Sair da Conta", use_container_width=True):
            api_request("POST", "auth/logout/")
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.rerun()

    # Conteúdo Principal de Boas-Vindas
    st.markdown(f"## Bem-vindo(a) ao seu painel, **{nome_usuario}**! 👋")
    st.write("Selecione uma opção na barra lateral para começar a explorar seus indicadores ou registrar lançamentos.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Dashboard**: Visualize gráficos dinâmicos, saldo atual, despesas por categoria e evolução mensal.")
    with col2:
        st.success("💰 **Receitas e Despesas**: Cadastre, pesquise, filtre e exporte seus lançamentos em formato CSV.")
    with col3:
        st.warning("🏷️ **Categorias**: Organize suas entradas e saídas por categorias personalizadas.")
