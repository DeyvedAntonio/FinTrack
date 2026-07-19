import streamlit as st
import streamlit.components.v1 as components


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

        /* Botões de Adição / Novo (Verde) */
        div.stButton > button[aria-label*="Nova"],
        div.stButton > button[aria-label*="Novo"],
        div.stButton > button[aria-label*="Adicionar"] {
            background-color: #10B981 !important;
            color: #FFFFFF !important;
            border: none !important;
        }
        div.stButton > button[aria-label*="Nova"]:hover,
        div.stButton > button[aria-label*="Novo"]:hover,
        div.stButton > button[aria-label*="Adicionar"]:hover {
            background-color: #059669 !important;
            color: #FFFFFF !important;
        }

        /* Botões de Excluir / Deletar (Vermelho Opaco) */
        div.stButton > button[aria-label*="Excluir"],
        div.stButton > button[aria-label*="Deletar"] {
            background-color: #DC2626 !important;
            color: #FFFFFF !important;
            border: 1px solid #B91C1C !important;
        }
        div.stButton > button[aria-label*="Excluir"]:hover,
        div.stButton > button[aria-label*="Deletar"]:hover {
            background-color: #B91C1C !important;
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

    components.html("""
        <script>
        const parentDoc = window.parent.document;
        function styleButtons() {
            const buttons = parentDoc.querySelectorAll('button');
            buttons.forEach(btn => {
                const text = (btn.innerText || btn.textContent || '').trim();
                const label = btn.getAttribute('aria-label') || '';
                const combined = (text + ' ' + label).toLowerCase();
                
                if (combined.includes('nova') || combined.includes('novo') || combined.includes('adicionar')) {
                    btn.style.setProperty('background-color', '#10B981', 'important');
                    btn.style.setProperty('color', '#FFFFFF', 'important');
                    btn.style.setProperty('border', 'none', 'important');
                } else if (combined.includes('excluir') || combined.includes('deletar')) {
                    btn.style.setProperty('background-color', '#DC2626', 'important');
                    btn.style.setProperty('color', '#FFFFFF', 'important');
                    btn.style.setProperty('border', '1px solid #B91C1C', 'important');
                }
            });
        }
        styleButtons();
        if (!window.parent._fintrackButtonObserver) {
            window.parent._fintrackButtonObserver = true;
            const observer = new MutationObserver(styleButtons);
            observer.observe(parentDoc.body, { childList: true, subtree: true });
        }
        </script>
    """, height=0, width=0)


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
