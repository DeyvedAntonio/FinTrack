from .models import Categoria


CATEGORIAS_PADRAO = [
    ('Alimentação', Categoria.TipoCategoria.DESPESA),
    ('Transporte', Categoria.TipoCategoria.DESPESA),
    ('Moradia', Categoria.TipoCategoria.DESPESA),
    ('Saúde', Categoria.TipoCategoria.DESPESA),
    ('Educação', Categoria.TipoCategoria.DESPESA),
    ('Lazer', Categoria.TipoCategoria.DESPESA),
    ('Salário', Categoria.TipoCategoria.RECEITA),
    ('Investimentos', Categoria.TipoCategoria.RECEITA),
    ('Outros', Categoria.TipoCategoria.RECEITA),
    ('Outros', Categoria.TipoCategoria.DESPESA),
]


def criar_categorias_padrao_para_usuario(usuario):
    """
    Cria as categorias padrão iniciais para um usuário recém-criado.
    """
    categorias = [
        Categoria(nome=nome, tipo=tipo, usuario=usuario)
        for nome, tipo in CATEGORIAS_PADRAO
    ]
    Categoria.objects.bulk_create(categorias, ignore_conflicts=True)
