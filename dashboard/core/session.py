import streamlit as st


def init_session():
    """Garante que todas as chaves de sessão essenciais estejam inicializadas."""
    if "token" not in st.session_state:
        st.session_state["token"] = None
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"  # 'login', 'register', 'reset'


def get_token():
    return st.session_state.get("token")


def set_token(token):
    st.session_state["token"] = token


def get_user():
    return st.session_state.get("user")


def set_user(user):
    st.session_state["user"] = user


def clear_session():
    st.session_state["token"] = None
    st.session_state["user"] = None


def check_authentication():
    """Garante que a rota só seja acessada se o usuário estiver autenticado."""
    init_session()
    if not st.session_state["token"]:
        st.warning("Por favor, faça login para acessar esta página.")
        st.stop()
