import streamlit as st


def render_lgpd_notice():
    """Exibe o alerta explicativo sobre o Art. 16, I da LGPD."""
    st.warning("""
**Direito de Eliminação de Dados e Retenção Legal (Art. 16, I da LGPD - Lei nº 13.709/2018):**  
Ao solicitar a exclusão da sua conta, seus dados pessoais identificáveis (nome, e-mail e foto) serão **permanentemente anonimizados** e seu acesso à plataforma será revogado imediatamente. 

Em estrito cumprimento à legislação fiscal e cível brasileira, seus registros de movimentações financeiras históricas serão mantidos de forma **anonimizada pelo prazo legal de 5 anos** para auditoria e prestação de contas, sem qualquer vinculação aos seus dados pessoais.
""")


def render_portability_notice():
    """Exibe o informativo sobre a portabilidade em CSV (Art. 18, V da LGPD)."""
    st.info("""
**Direito à Portabilidade dos Dados (Art. 18, V da LGPD):**  
Você pode realizar o download completo de todos os seus dados cadastrados no FinTrack (informações de perfil, categorias e o histórico completo de movimentações financeiras) em um arquivo no formato CSV.
""")
