from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MovimentacaoViewSet, ParcelamentoViewSet, ConfigCartaoViewSet, PlanejamentoMensalViewSet, ResumoPlanejamentoAPIView

app_name = 'finance'

router = DefaultRouter()
router.register(r'movimentacoes', MovimentacaoViewSet, basename='movimentacao')
router.register(r'parcelamentos', ParcelamentoViewSet, basename='parcelamento')
router.register(r'cartoes', ConfigCartaoViewSet, basename='cartao')
router.register(r'planejamentos', PlanejamentoMensalViewSet, basename='planejamento')

urlpatterns = [
    path('planejamentos/resumo/', ResumoPlanejamentoAPIView.as_view(), name='planejamento-resumo'),
] + router.urls
