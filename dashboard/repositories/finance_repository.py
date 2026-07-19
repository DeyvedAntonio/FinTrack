from .base_repository import BaseRepository


class FinanceRepository:
    @staticmethod
    def get_movimentacoes(params=None):
        return BaseRepository.request("GET", "finance/movimentacoes/", params=params)

    @staticmethod
    def create_movimentacao(payload):
        return BaseRepository.request("POST", "finance/movimentacoes/", payload)

    @staticmethod
    def update_movimentacao(mov_id, payload):
        return BaseRepository.request("PUT", f"finance/movimentacoes/{mov_id}/", payload)

    @staticmethod
    def delete_movimentacao(mov_id):
        return BaseRepository.request("DELETE", f"finance/movimentacoes/{mov_id}/")

    @staticmethod
    def export_csv(params=None):
        return BaseRepository.request("GET", "finance/movimentacoes/export-csv/", params=params)
