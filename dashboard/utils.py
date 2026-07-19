from core.theme import apply_theme, format_currency
from core.session import check_authentication, init_session
from repositories.base_repository import BaseRepository

# Retrocompatibilidade
api_request = BaseRepository.request
