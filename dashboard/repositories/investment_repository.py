from .base_repository import BaseRepository


class InvestmentRepository:
    @staticmethod
    def get_ativos():
        return BaseRepository.request("GET", "investments/ativos/")

    @staticmethod
    def create_ativo(payload):
        return BaseRepository.request("POST", "investments/ativos/", payload)

    @staticmethod
    def delete_ativo(ativo_id):
        return BaseRepository.request("DELETE", f"investments/ativos/{ativo_id}/")

    @staticmethod
    def get_operacoes():
        return BaseRepository.request("GET", "investments/operacoes/")

    @staticmethod
    def create_operacao(payload):
        return BaseRepository.request("POST", "investments/operacoes/", payload)

    @staticmethod
    def delete_operacao(operacao_id):
        return BaseRepository.request("DELETE", f"investments/operacoes/{operacao_id}/")

    @staticmethod
    def get_carteira():
        return BaseRepository.request("GET", "investments/carteira/")
