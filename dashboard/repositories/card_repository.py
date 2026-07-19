from .base_repository import BaseRepository


class CardRepository:
    # Cartões de Crédito
    @staticmethod
    def get_cartoes():
        return BaseRepository.request("GET", "finance/cartoes/")

    @staticmethod
    def create_cartao(payload):
        return BaseRepository.request("POST", "finance/cartoes/", payload)

    @staticmethod
    def update_cartao(cartao_id, payload):
        return BaseRepository.request("PATCH", f"finance/cartoes/{cartao_id}/", payload)

    @staticmethod
    def delete_cartao(cartao_id):
        return BaseRepository.request("DELETE", f"finance/cartoes/{cartao_id}/")

    # Compras Parceladas
    @staticmethod
    def get_parcelamentos():
        return BaseRepository.request("GET", "finance/parcelamentos/")

    @staticmethod
    def create_parcelamento(payload):
        return BaseRepository.request("POST", "finance/parcelamentos/", payload)

    @staticmethod
    def delete_parcelamento(parcelamento_id):
        return BaseRepository.request("DELETE", f"finance/parcelamentos/{parcelamento_id}/")
