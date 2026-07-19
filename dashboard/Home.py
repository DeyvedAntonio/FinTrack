import os
import streamlit as st
from core.theme import apply_theme
from core.session import init_session
from services.auth_service import AuthService
from repositories.auth_repository import AuthRepository

st.set_page_config(
    page_title="FinTrack - Gestão Financeira Pessoal",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
init_session()

# Caminho das imagens do sistema
img_dir = os.path.join(os.path.dirname(__file__), "..", "img")
img_dark = os.path.join(img_dir, "fintrack_dark2.png")

# Se não estiver autenticado
if not st.session_state["token"]:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 2rem 2.5rem; border-radius: 16px; border: 1px solid #334155; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4); margin-bottom: 2rem;">
            <span style="background-color: rgba(37, 99, 235, 0.2); color: #60A5FA; font-size: 0.85rem; font-weight: 600; padding: 0.35rem 0.75rem; border-radius: 20px; border: 1px solid rgba(96, 165, 250, 0.3);">✨ Gestão Financeira Inteligente</span>
            <h1 style="font-size: 2.8rem; font-weight: 900; color: #F9FAFB; margin: 0.75rem 0 0.25rem 0; letter-spacing: -1px;">
                <span style="color: #3B82F6;">Fin</span>Track
            </h1>
            <p style="font-size: 1.1rem; color: #94A3B8; font-weight: 400; margin: 0;">
                Sistema Inteligente de Gestão Financeira Pessoal & Controle de Investimentos
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 🚀 O que é o FinTrack?")
        st.write("Uma plataforma completa e moderna para gerenciamento financeiro pessoal, integrando controle de receitas, despesas, cartões de crédito parcelados e gestão de carteira de investimentos com preço médio automático.")
        
        st.markdown("#### ✨ Funcionalidades Principais:")
        st.markdown("• **📊 Dashboard & Indicadores**: Visão geral de saldo consolidado e gráficos de evolução.")
        st.markdown("• **💰 Fluxo de Caixa**: Entradas e saídas operacionais com busca e exportação CSV.")
        st.markdown("• **💳 Cartões de Crédito**: Apelidos, últimos 4 dígitos, datas de vencimento e compras parceladas.")
        st.markdown("• **📈 Carteira de Investimentos**: Ativos, cálculo automático de Preço Médio e distribuição por classe.")
        st.markdown("• **🏷️ Orçamentos por Categoria**: Teto mensal de despesas.")
        st.markdown("• **🔒 Privacidade & LGPD**: Portabilidade de dados (Art. 18, V) e exclusão anonimizada (Art. 16, I).")

    with col_right:
        if st.session_state["auth_mode"] == "login":
            st.subheader("🔑 Entrar")
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
                            success, data = AuthService.login(email, password)
                            if success:
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

        elif st.session_state["auth_mode"] == "register":
            st.subheader("📝 Criar Conta")
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
                            success, data = AuthService.register(nome, email, password, confirm_password)
                            if success:
                                st.success("Cadastro realizado com sucesso!")
                                st.rerun()
                            else:
                                err = data.get("email", [data.get("detail", "Erro ao cadastrar.")])[0]
                                st.error(err)

            if st.button("Já possui conta? Entrar", use_container_width=True):
                st.session_state["auth_mode"] = "login"
                st.rerun()

        elif st.session_state["auth_mode"] == "reset":
            st.subheader("🔒 Recuperar Senha")
            st.caption("Informe seu e-mail para receber as instruções.")

            with st.form("form_reset"):
                email = st.text_input("E-mail Cadastrado", placeholder="seuemail@exemplo.com")
                submit_reset = st.form_submit_button("Enviar link", use_container_width=True)

                if submit_reset:
                    if not email:
                        st.error("Informe seu e-mail.")
                    else:
                        with st.spinner("Enviando solicitação..."):
                            success, _ = AuthRepository.request_password_reset(email)
                            if success:
                                st.info("Link enviado. Se o e-mail estiver cadastrado, você receberá o link em breve.")
                            else:
                                st.error("Erro ao solicitar redefinição de senha.")

            if st.button("Voltar para o Login", use_container_width=True):
                st.session_state["auth_mode"] = "login"
                st.rerun()

else:
    user = st.session_state["user"]
    nome_usuario = user.get("nome") or user.get("email")
    moeda = user.get("moeda", "BRL")

    with st.sidebar:
        st.markdown(f"### Olá, **{nome_usuario}**! 👋")
        st.caption(f"Moeda Padrão: **{moeda}**")
        st.divider()
        st.info("Navegue pelas páginas do menu lateral para visualizar seu Dashboard, Lançamentos, Cartões, Investimentos ou Perfil.")
        
        st.divider()
        if st.button("🚪 Sair da Conta", use_container_width=True):
            AuthService.logout()
            st.rerun()

    # Hero Banner SaaS para Usuário Autenticado
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 2.2rem 2.5rem; border-radius: 16px; border: 1px solid #334155; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4); margin-bottom: 2rem;">
            <span style="background-color: rgba(16, 185, 129, 0.15); color: #34D399; font-size: 0.85rem; font-weight: 600; padding: 0.35rem 0.75rem; border-radius: 20px; border: 1px solid rgba(52, 211, 153, 0.3);">✨ Painel de Controle Principal</span>
            <h1 style="font-size: 2.4rem; font-weight: 800; color: #F9FAFB; margin: 0.8rem 0 0.4rem 0;">Bem-vindo(a) de volta ao FinTrack, {nome_usuario}! 👋</h1>
            <p style="font-size: 1.1rem; color: #94A3B8; margin: 0; font-weight: 400;">
                Sistema Inteligente de Gestão Financeira Pessoal & Controle de Investimentos
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🗺️ O que você pode fazer no FinTrack hoje?")
    
    col_feat1, col_feat2 = st.columns(2)
    with col_feat1:
        st.info("📊 **1. Painel Geral (Dashboard)**\n\nVisualize indicadores de saúde financeira, saldo atual e gráficos de evolução de gastos.")
        st.success("💰 **2. Fluxo de Caixa (Receitas & Despesas)**\n\nLance movimentações informando categoria, observações e forma de pagamento com exportação CSV.")
        st.warning("💳 **3. Cartões & Parcelas**\n\nGerencie cartões de crédito (apelidos e 4 dígitos), datas de vencimento e compras parceladas.")

    with col_feat2:
        st.info("📈 **4. Carteira de Investimentos**\n\nMonitore o preço médio ponderado e a distribuição patrimonial por tipo de ativo.")
        st.success("🏷️ **5. Categorias & Orçamentos**\n\nDefina orçamentos mensais para cada centro de custo.")
        st.warning("👤 **6. Perfil & LGPD**\n\nExporte seus dados em CSV (Art. 18, V) ou solicite a exclusão anonimizada (Art. 16, I).")
