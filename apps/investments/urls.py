from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AtivoViewSet, OperacaoInvestimentoViewSet, CarteiraAPIView

app_name = 'investments'

router = DefaultRouter()
router.register(r'ativos', AtivoViewSet, basename='ativo')
router.register(r'operacoes', OperacaoInvestimentoViewSet, basename='operacao')

urlpatterns = router.urls + [
    path('carteira/', CarteiraAPIView.as_view(), name='carteira'),
]
