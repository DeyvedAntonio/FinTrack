import pandas as pd
from repositories.finance_repository import FinanceRepository


class FinanceService:
    @staticmethod
    def get_movimentacoes(params=None):
        success, data = FinanceRepository.get_movimentacoes(params=params)
        if success and isinstance(data, list):
            return data
        return []

    @staticmethod
    def calculate_kpis(movimentacoes):
        if not movimentacoes:
            return 0.0, 0.0, 0.0

        df = pd.DataFrame(movimentacoes)
        df["valor"] = df["valor"].astype(float)

        total_receitas = df[df["tipo"] == "RECEITA"]["valor"].sum()
        total_despesas = df[df["tipo"] == "DESPESA"]["valor"].sum()
        saldo_atual = total_receitas - total_despesas

        return saldo_atual, total_receitas, total_despesas

    @staticmethod
    def save_movimentacao(mov_id, payload):
        if mov_id:
            return FinanceRepository.update_movimentacao(mov_id, payload)
        return FinanceRepository.create_movimentacao(payload)

    @staticmethod
    def delete_movimentacao(mov_id):
        return FinanceRepository.delete_movimentacao(mov_id)

    @staticmethod
    def export_csv(params=None):
        return FinanceRepository.export_csv(params=params)
