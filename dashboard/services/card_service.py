from repositories.card_repository import CardRepository


class CardService:
    @staticmethod
    def get_cartoes():
        success, data = CardRepository.get_cartoes()
        if success and isinstance(data, list):
            return data
        return []

    @staticmethod
    def get_cartao_dict():
        cartoes = CardService.get_cartoes()
        return {c["id"]: c["nome_exibicao"] for c in cartoes}

    @staticmethod
    def save_cartao(cartao_id, payload):
        if cartao_id:
            return CardRepository.update_cartao(cartao_id, payload)
        return CardRepository.create_cartao(payload)

    @staticmethod
    def delete_cartao(cartao_id):
        return CardRepository.delete_cartao(cartao_id)

    @staticmethod
    def get_parcelamentos():
        success, data = CardRepository.get_parcelamentos()
        if success and isinstance(data, list):
            return data
        return []

    @staticmethod
    def save_parcelamento(payload):
        return CardRepository.create_parcelamento(payload)

    @staticmethod
    def delete_parcelamento(parcelamento_id):
        return CardRepository.delete_parcelamento(parcelamento_id)
