from repositories.investment_repository import InvestmentRepository


class InvestmentService:
    @staticmethod
    def get_ativos():
        success, data = InvestmentRepository.get_ativos()
        if success and isinstance(data, list):
            return data
        return []

    @staticmethod
    def get_ativo_dict():
        ativos = InvestmentService.get_ativos()
        return {a["id"]: f"{a['codigo']} - {a['nome']}" for a in ativos}

    @staticmethod
    def save_ativo(payload):
        return InvestmentRepository.create_ativo(payload)

    @staticmethod
    def delete_ativo(ativo_id):
        return InvestmentRepository.delete_ativo(ativo_id)

    @staticmethod
    def get_operacoes():
        success, data = InvestmentRepository.get_operacoes()
        if success and isinstance(data, list):
            return data
        return []

    @staticmethod
    def save_operacao(payload):
        return InvestmentRepository.create_operacao(payload)

    @staticmethod
    def delete_operacao(operacao_id):
        return InvestmentRepository.delete_operacao(operacao_id)

    @staticmethod
    def get_carteira_summary():
        success, data = InvestmentRepository.get_carteira()
        if success and isinstance(data, dict):
            return data
        return {"total_investido": 0.0, "posicao_ativos": [], "alocacao_por_tipo": {}}
