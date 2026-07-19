import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")


class BaseRepository:
    @staticmethod
    def get_headers():
        headers = {"Content-Type": "application/json"}
        if "token" in st.session_state and st.session_state["token"]:
            headers["Authorization"] = f"Token {st.session_state['token']}"
        return headers

    @classmethod
    def request(cls, method, endpoint, payload=None, params=None, files=None):
        url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
        headers = cls.get_headers()

        if files:
            headers.pop("Content-Type", None)

        try:
            m = method.upper()
            if m == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif m == "POST":
                if files:
                    response = requests.post(url, headers=headers, data=payload, files=files, timeout=15)
                else:
                    response = requests.post(url, headers=headers, json=payload, params=params, timeout=10)
            elif m == "PUT":
                if files:
                    response = requests.put(url, headers=headers, data=payload, files=files, timeout=15)
                else:
                    response = requests.put(url, headers=headers, json=payload, params=params, timeout=10)
            elif m == "PATCH":
                if files:
                    response = requests.patch(url, headers=headers, data=payload, files=files, timeout=15)
                else:
                    response = requests.patch(url, headers=headers, json=payload, params=params, timeout=10)
            elif m == "DELETE":
                response = requests.delete(url, headers=headers, params=params, timeout=10)
            else:
                return False, {"detail": "Método HTTP não suportado."}

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
