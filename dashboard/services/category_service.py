from repositories.category_repository import CategoryRepository


class CategoryService:
    @staticmethod
    def get_categories(tipo=None):
        params = {"tipo": tipo} if tipo else None
        success, data = CategoryRepository.get_all(params=params)
        if success and isinstance(data, list):
            return data
        return []

    @staticmethod
    def get_category_dict(tipo=None):
        cats = CategoryService.get_categories(tipo=tipo)
        return {c["id"]: c["nome"] for c in cats}

    @staticmethod
    def save_category(cat_id, nome, tipo, limite_mensal=0.0):
        if cat_id:
            return CategoryRepository.update(cat_id, nome, tipo, limite_mensal)
        return CategoryRepository.create(nome, tipo, limite_mensal)

    @staticmethod
    def delete_category(cat_id):
        return CategoryRepository.delete(cat_id)
