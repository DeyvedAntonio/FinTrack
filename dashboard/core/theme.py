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

        /* Botão Primário */
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

        /* KPI Cards */
        .kpi-card {
            background-color: white;
            padding: 1.25rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1);
            border: 1px solid #E2E8F0;
        }
        .kpi-title {
            font-size: 0.875rem;
            color: #64748B;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .kpi-value {
            font-size: 1.75rem;
            font-weight: 700;
            margin-top: 0.5rem;
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
