from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import Categoria
from .serializers import CategoriaSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Gerenciamento de Categorias de Receitas e Despesas.
    Permite Listar, Criar, Detalhar, Atualizar e Excluir categorias do usuário logado.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CategoriaSerializer

    def get_queryset(self):
        queryset = Categoria.objects.filter(usuario=self.request.user)
        tipo = self.request.query_params.get('tipo')
        if tipo in [Categoria.TipoCategoria.RECEITA, Categoria.TipoCategoria.DESPESA]:
            queryset = queryset.filter(tipo=tipo)
        return queryset

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Regra de negócio: Verificar se existem movimentações vinculadas a esta categoria
        # Suporta tanto o related_name 'movimentacoes' quanto verificação dinâmica
        tem_movimentacoes = False
        if hasattr(instance, 'movimentacoes') and instance.movimentacoes.exists():
            tem_movimentacoes = True
        elif hasattr(instance, 'movimentacao_set') and instance.movimentacao_set.exists():
            tem_movimentacoes = True

        if tem_movimentacoes:
            return Response(
                {"detail": "Categoria vinculada a movimentações. Não é possível excluí-la."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response({"message": "Categoria excluída com sucesso."}, status=status.HTTP_200_OK)
