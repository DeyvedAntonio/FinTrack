from .base_repository import BaseRepository


class CategoryRepository:
    @staticmethod
    def get_all(params=None):
        return BaseRepository.request("GET", "categories/", params=params)

    @staticmethod
    def create(nome, tipo, limite_mensal=0.0, pilar='ESSENCIAL'):
        payload = {"nome": nome, "tipo": tipo, "limite_mensal": limite_mensal, "pilar": pilar}
        return BaseRepository.request("POST", "categories/", payload)

    @staticmethod
    def update(cat_id, nome, tipo, limite_mensal=0.0, pilar='ESSENCIAL'):
        payload = {"nome": nome, "tipo": tipo, "limite_mensal": limite_mensal, "pilar": pilar}
        return BaseRepository.request("PUT", f"categories/{cat_id}/", payload)

    @staticmethod
    def delete(cat_id):
        return BaseRepository.request("DELETE", f"categories/{cat_id}/")
