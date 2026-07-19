import streamlit as st
from repositories.auth_repository import AuthRepository
from core.session import set_token, set_user, clear_session


class AuthService:
    @staticmethod
    def login(email, password):
        success, data = AuthRepository.login(email, password)
        if success:
            set_token(data["token"])
            set_user(data["user"])
        return success, data

    @staticmethod
    def register(nome, email, password, confirm_password):
        success, data = AuthRepository.register(nome, email, password, confirm_password)
        if success:
            set_token(data["token"])
            set_user(data["user"])
        return success, data

    @staticmethod
    def logout():
        AuthRepository.logout()
        clear_session()

    @staticmethod
    def update_profile(payload, files=None):
        success, data = AuthRepository.update_profile(payload, files)
        if success:
            set_user(data["user"])
        return success, data

    @staticmethod
    def change_password(old_password, new_password, confirm_new_password):
        success, data = AuthRepository.change_password(old_password, new_password, confirm_new_password)
        if success:
            set_token(data["token"])
        return success, data

    @staticmethod
    def delete_account(password):
        success, data = AuthRepository.delete_account(password)
        if success:
            clear_session()
        return success, data

    @staticmethod
    def export_user_data_csv():
        return AuthRepository.export_user_csv()
