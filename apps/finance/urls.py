from rest_framework.routers import DefaultRouter
from .views import MovimentacaoViewSet

app_name = 'finance'

router = DefaultRouter()
router.register(r'movimentacoes', MovimentacaoViewSet, basename='movimentacao')

urlpatterns = router.urls
