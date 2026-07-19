from .base_repository import BaseRepository


class AuthRepository:
    @staticmethod
    def login(email, password):
        return BaseRepository.request("POST", "auth/login/", {"email": email, "password": password})

    @staticmethod
    def register(nome, email, password, confirm_password):
        payload = {
            "nome": nome,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        }
        return BaseRepository.request("POST", "auth/register/", payload)

    @staticmethod
    def logout():
        return BaseRepository.request("POST", "auth/logout/")

    @staticmethod
    def update_profile(payload, files=None):
        return BaseRepository.request("PATCH", "auth/profile/", payload=payload, files=files)

    @staticmethod
    def change_password(old_password, new_password, confirm_new_password):
        payload = {
            "old_password": old_password,
            "new_password": new_password,
            "confirm_new_password": confirm_new_password
        }
        return BaseRepository.request("POST", "auth/change-password/", payload)

    @staticmethod
    def request_password_reset(email):
        return BaseRepository.request("POST", "auth/password-reset/", {"email": email})

    @staticmethod
    def delete_account(password):
        return BaseRepository.request("POST", "auth/delete-account/", {"password": password})

    @staticmethod
    def export_user_csv():
        return BaseRepository.request("GET", "auth/export-csv/")
