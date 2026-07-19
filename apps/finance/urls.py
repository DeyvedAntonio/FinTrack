from rest_framework.routers import DefaultRouter
from .views import MovimentacaoViewSet, ParcelamentoViewSet, ConfigCartaoViewSet

app_name = 'finance'

router = DefaultRouter()
router.register(r'movimentacoes', MovimentacaoViewSet, basename='movimentacao')
router.register(r'parcelamentos', ParcelamentoViewSet, basename='parcelamento')
router.register(r'cartoes', ConfigCartaoViewSet, basename='cartao')

urlpatterns = router.urls
