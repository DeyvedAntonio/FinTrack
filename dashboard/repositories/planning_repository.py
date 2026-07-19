from .base_repository import BaseRepository


class PlanningRepository:
    @staticmethod
    def get_planejamentos():
        return BaseRepository.request("GET", "finance/planejamentos/")

    @staticmethod
    def get_resumo_planejamento(mes=None):
        endpoint = "finance/planejamentos/resumo/"
        if mes:
            endpoint += f"?mes={mes}"
        return BaseRepository.request("GET", endpoint)

    @staticmethod
    def create_planejamento(payload):
        return BaseRepository.request("POST", "finance/planejamentos/", payload)

    @staticmethod
    def update_planejamento(plan_id, payload):
        return BaseRepository.request("PUT", f"finance/planejamentos/{plan_id}/", payload)
