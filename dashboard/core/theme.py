import streamlit as st


def apply_theme():
    """Injeta os estilos CSS globais alinhados à Paleta de Cores e Tipografia Inter do PRD FinTrack."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
        
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
            color: #1F2937;
        }

        /* Cores Principais do PRD FinTrack */
        :root {
            --primary: #2563EB;
            --secondary: #10B981;
            --background: #F8FAFC;
            --highlight: #F59E0B;
            --text: #1F2937;
        }

        /* Botão Primário Padrão */
        .stButton>button {
            background-color: #2563EB;
            color: white;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #1d4ed8;
            color: white;
            transform: translateY(-1px);
        }

        /* Estilização nativa de botões por prefixo de Key (.st-key-...) */
        div[class*="st-key-nova"] button,
        div[class*="st-key-novo"] button,
        div[class*="st-key-btn_new"] button,
        div[class*="st-key-add_"] button {
            background-color: #10B981 !important;
            color: #FFFFFF !important;
            border: none !important;
        }

        div[class*="st-key-nova"] button:hover,
        div[class*="st-key-novo"] button:hover,
        div[class*="st-key-btn_new"] button:hover,
        div[class*="st-key-add_"] button:hover {
            background-color: #059669 !important;
            color: #FFFFFF !important;
        }

        /* Botões de Exclusão / Deletar (Vermelho Opaco) */
        div[class*="st-key-del_"] button,
        div[class*="st-key-del-"] button,
        div[class*="st-key-delete"] button {
            background-color: #DC2626 !important;
            color: #FFFFFF !important;
            border: 1px solid #B91C1C !important;
        }

        div[class*="st-key-del_"] button:hover,
        div[class*="st-key-del-"] button:hover,
        div[class*="st-key-delete"] button:hover {
            background-color: #B91C1C !important;
            color: #FFFFFF !important;
        }

        /* Botões Neutros / Cinza (Sair da Conta / Logout) */
        div[class*="st-key-btn_logout"] button,
        div[class*="st-key-logout"] button,
        div[class*="st-key-gray"] button {
            background-color: #4B5563 !important;
            color: #FFFFFF !important;
            border: 1px solid #374151 !important;
        }

        div[class*="st-key-btn_logout"] button:hover,
        div[class*="st-key-logout"] button:hover,
        div[class*="st-key-gray"] button:hover {
            background-color: #374151 !important;
            color: #FFFFFF !important;
        }

        /* KPI Cards */
        .kpi-card {
            background-color: #1F2937;
            padding: 1rem 1.25rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px 0 rgba(0,0,0,0.2);
            border: 1px solid #374151;
        }
        .kpi-title {
            font-size: 0.85rem;
            color: #9CA3AF;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .kpi-value {
            font-size: 1.65rem;
            font-weight: 700;
            margin-top: 0.25rem;
        }
        .kpi-value.positive { color: #10B981; }
        .kpi-value.negative { color: #EF4444; }
        .kpi-value.neutral { color: #2563EB; }

        /* Ocultar navegação padrão rústica se quisermos sidebar limpa */
        div[data-testid="stSidebarNav"] {
            padding-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)


def format_currency(val, currency_code="BRL"):
    """Formata valor numérico para a moeda selecionada no perfil do usuário."""
    symbols = {
        "BRL": "R$",
        "USD": "$",
        "EUR": "€"
    }
    symbol = symbols.get(currency_code, "R$")
    try:
        val_float = float(val)
        return f"{symbol} {val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return f"{symbol} 0,00"
