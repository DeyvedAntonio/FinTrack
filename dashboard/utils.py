import os
import requests
import streamlit as st

# URL Base da API REST Django
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")


def get_headers():
    """Retorna os cabeçalhos das requisições incluindo o Token de Autenticação se logado."""
    headers = {"Content-Type": "application/json"}
    if "token" in st.session_state and st.session_state["token"]:
        headers["Authorization"] = f"Token {st.session_state['token']}"
    return headers


def api_request(method, endpoint, payload=None, params=None, files=None):
    """
    Realiza requisições HTTP para a API Django Backend com tratamento centralizado de erros e autenticação.
    """
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    headers = get_headers()
    
    if files:
        # Se houver upload de arquivos, remover Content-Type para o requests gerenciar o boundary multipart
        headers.pop("Content-Type", None)

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method.upper() == "POST":
            if files:
                response = requests.post(url, headers=headers, data=payload, files=files, timeout=15)
            else:
                response = requests.post(url, headers=headers, json=payload, params=params, timeout=10)
        elif method.upper() == "PUT":
            if files:
                response = requests.put(url, headers=headers, data=payload, files=files, timeout=15)
            else:
                response = requests.put(url, headers=headers, json=payload, params=params, timeout=10)
        elif method.upper() == "PATCH":
            if files:
                response = requests.patch(url, headers=headers, data=payload, files=files, timeout=15)
            else:
                response = requests.patch(url, headers=headers, json=payload, params=params, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, params=params, timeout=10)
        else:
            return False, {"detail": "Método HTTP não suportado."}

        # Resposta JSON
        if response.status_code in [200, 201]:
            if response.headers.get("Content-Type") == "text/csv; charset=utf-8":
                return True, response.content
            return True, response.json()
        elif response.status_code == 204:
            return True, {"message": "Operação realizada com sucesso."}
        else:
            try:
                err_data = response.json()
            except Exception:
                err_data = {"detail": response.text or f"Erro {response.status_code}"}
            return False, err_data

    except requests.exceptions.ConnectionError:
        return False, {"detail": "Não foi possível conectar ao servidor Backend (Django). Verifique se a API está rodando."}
    except Exception as e:
        return False, {"detail": str(e)}


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


def check_authentication():
    """Garante que a rota só seja acessada se o usuário estiver autenticado."""
    if "token" not in st.session_state or not st.session_state["token"]:
        st.warning("Por favor, faça login para acessar esta página.")
        st.stop()
