from repositories.planning_repository import PlanningRepository


class PlanningService:
    @staticmethod
    def get_resumo_planejamento(mes=None):
        success, data = PlanningRepository.get_resumo_planejamento(mes)
        if success and isinstance(data, dict):
            return data
        return None

    @staticmethod
    def save_planejamento(payload, plan_id=None):
        if plan_id:
            return PlanningRepository.update_planejamento(plan_id, payload)
        return PlanningRepository.create_planejamento(payload)

    @staticmethod
    def simular_nova_compra(valor_total, num_parcelas, disponivel_atual, valor_parcela_direto=None):
        if valor_parcela_direto is not None and valor_parcela_direto > 0:
            parcela_mensal = round(valor_parcela_direto, 2)
            valor_total_calculado = round(parcela_mensal * num_parcelas, 2) if num_parcelas > 0 else parcela_mensal
        else:
            parcela_mensal = round(valor_total / num_parcelas, 2) if num_parcelas > 0 else valor_total
            valor_total_calculado = valor_total

        novo_disponivel = disponivel_atual - parcela_mensal
        impacto_percentual = round((parcela_mensal / disponivel_atual) * 100, 1) if disponivel_atual > 0 else 100.0
        
        recomendacao = "Saudável"
        if novo_disponivel < 0:
            recomendacao = "Crítico (Orçamento Estourado)"
        elif impacto_percentual > 40:
            recomendacao = "Atenção (Alto Comprometimento da Renda)"
        elif impacto_percentual > 20:
            recomendacao = "Moderado"

        return {
            'valor_parcela': parcela_mensal,
            'valor_total_calculado': valor_total_calculado,
            'novo_disponivel': novo_disponivel,
            'impacto_percentual': impacto_percentual,
            'recomendacao': recomendacao
        }
